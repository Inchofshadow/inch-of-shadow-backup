"""
scene_intelligence/extract_contacts.py
---------------------------------------
Tool 1 — Scene Intelligence Engine: Contact Extractor

Reads four data sources and extracts music industry contacts into a
single structured JSON file ready for Google Sheets ingestion.

Sources:
  1. YouTube subscriptions CSV   → labels, DJs, venues, artists, media
  2. Instagram following JSON    → all accounts you follow
  3. ChatGPT label PDF           → distributors and platforms mentioned
  4. SoundCloud screenshots      → manually curated from following screenshots

Enrichment (applied to all contacts):
  - genre_main / genre_sub  — inferred from name keywords + known overrides
  - location                — city inferred from name keywords + known overrides
  - match_score             — 1–5 genre fit vs. Inch of Shadow's sound

Output:
  scene_intelligence/raw_contacts.json

Usage:
  python3 scene_intelligence/extract_contacts.py
"""

from __future__ import annotations

import csv
import difflib
import json
import re
import sys
from pathlib import Path

from pdfminer.high_level import extract_text

sys.path.insert(0, str(Path(__file__).parent))
from utils import dedup_key

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR       = Path(__file__).parent.parent   # project root
DATA_DIR       = BASE_DIR / "data"
OUTPUT_DIR     = Path(__file__).parent          # scene_intelligence/
OUTPUT_FILE    = OUTPUT_DIR / "raw_contacts.json"
RA_JSON        = OUTPUT_DIR / "ra_contacts.json"

YOUTUBE_CSV    = DATA_DIR / "YouTube and YouTube Music" / "subscriptions" / "subscriptions.csv"
INSTAGRAM_JSON = (
    DATA_DIR
    / "instagram-inch_of_shadow-2026-02-19-wdv7RP05"
    / "connections"
    / "followers_and_following"
    / "following.json"
)
CHATGPT_PDF    = DATA_DIR / "chatgpt label conv.pdf"
SC_FOLDER      = DATA_DIR / "soundcloud"

FUZZY_THRESHOLD = 0.95

# ---------------------------------------------------------------------------
# Category classifier
# ---------------------------------------------------------------------------

def _tokenize(name: str) -> set[str]:
    """Split on separators and return lowercase token set."""
    parts = re.split(r'[_.\-\s]+', name.lower())
    return {p for p in parts if len(p) > 1}


# Hard-coded known accounts — exact lowercase match on name/username
KNOWN_ACCOUNTS: dict[str, str] = {
    # ── DJs / Producers (Instagram) ────────────────────────────────────────
    "ninakraviz":               "dj",
    "vladimir_ivkovic":         "dj",
    "legowelt_official":        "dj",
    "cybotronlive":             "dj",
    "lcdsoundsystem":           "dj",
    "misskittinofficial":       "dj",
    "djhellofficial":           "dj",
    "ladystarlightnyc":         "dj",
    "redaxesofficial":          "dj",
    "the_hacker_amato":         "dj",
    "kalbata":                  "dj",
    "nastiaydj":                "dj",
    "juniorfairplay":           "dj",
    "maxim_turbo":              "dj",
    "danorbach808":             "dj",
    "annahaletadj":             "dj",
    "marsmandj":                "dj",
    "cursesforever":            "dj",
    "dollkraut":                "dj",
    "puscifer":                 "dj",
    "diiv":                     "dj",
    "suuns_mtl":                "dj",
    "thetwilightsad":           "dj",
    "thewarrenellis":           "dj",
    "dannycarey_tool":          "dj",
    "toolmusic":                "dj",
    "young marco":              "dj",
    "richie hawtin":            "dj",
    "legowelt":                 "dj",
    "etienne de crécy":         "dj",
    "persephone":               "dj",
    "jana fitz":                "dj",
    "maayan nidam":             "dj",
    "francisco farfa":          "dj",
    "crystal castles":          "dj",
    "nick cave":                "dj",
    "nina kraviz":              "dj",
    # ── Labels (Instagram usernames) ───────────────────────────────────────
    "4ad":                      "label",
    "sacredbones":              "label",
    "clone.nl":                 "label",
    "clonerecords":             "label",
    "dfarecs":                  "label",
    "minimalwave":              "label",
    "minitel_ofc":              "label",
    "analog africa":            "label",
    "international feel":       "label",
    "melopee records":          "label",
    "roam recordings":          "label",
    "slow motion records":      "label",
    "radiant records":          "label",
    "disco suicide":            "label",
    "lunar disko records":      "label",
    "other people":             "label",
    "constellation":            "label",
    "minimal wave":             "label",
    "dekmantel":                "label",
    "eta records":              "label",
    "la groovie machine":       "label",
    # ── Labels (YouTube display names → lowercase) ──────────────────────────
    "viewlexx":                 "label",
    "multi culti":              "label",
    "pinkman":                  "label",
    "bambatta music":           "label",
    "in between music":         "label",
    "terminal passage":         "label",
    "deep obelisk":             "label",
    "germsgems":                "label",
    "tubedigga":                "label",
    "silent chaos music":       "label",
    "silentchaos music":        "label",
    "future funk":              "label",
    "electronic love collective": "label",
    "imaginary ambition":       "label",
    "subaqueousmusic":          "label",
    "deeptek":                  "label",
    "deeptekk":                 "label",
    "303lush":                  "label",
    "meta moto":                "label",
    "tonepusher":               "label",
    "les yeux orange":          "label",
    "rogalist records":         "label",
    # ── Media (Instagram) ──────────────────────────────────────────────────
    "synth_history":            "media",
    "glue.berlin":              "media",
    "postpunkonline":           "media",
    "brooklynvegan":            "media",
    "pitchfork":                "media",
    "resident_advisor":         "media",
    "nts_radio":                "media",
    "redlightradio":            "media",
    "intergalacticfm":          "media",
    "operator.radio":           "media",
    "teder.fm":                 "media",
    "inn7.fm":                  "media",
    "mutantradiotbilisi":       "media",
    "backsideradio_official":   "media",
    "antenna.radio":            "media",
    "hopestradio":              "media",
    "samplesfrommars":          "media",
    "productionmusiclive":      "media",
    "underscopefeed":           "media",
    "stream_informer":          "media",
    "resident advisor":         "media",
    "boiler room":              "media",
    "ra exchange":              "media",
    "phonica records":          "media",
    "themes for great cities":  "media",
    "disco pastors":            "media",
    "thf radio":                "media",
    # ── Media (YouTube display names → lowercase) ───────────────────────────
    "inverted audio":           "media",
    "180 fact":                 "media",
    "pensado's place":          "media",
    "pro audio files":          "media",
    "production expert":        "media",
    "reverb":                   "media",
    "gearspace forum":          "media",
    "sonic academy":            "media",
    "point blank music school": "media",
    "production music live":    "media",
    "sage audio":               "media",
    "waves audio":              "media",
    "music theory":             "media",
    "whypeopledance":           "media",
    # ── Venues (Instagram) ─────────────────────────────────────────────────
    "berghain_panoramabar":     "venue",
    "hoppetosse.berlin":        "venue",
    "renate.berlin":            "venue",
    "prachtwerkberlin":         "venue",
    "rso.berlin":               "venue",
    "ohmberlin":                "venue",
    "omenberlin":               "venue",
    "lunacy_berlin":            "venue",
    "sameheads":                "venue",
    "arkaodaberlin":            "venue",
    "in.between.berlin":        "venue",
    "dreambabydreambar":        "venue",
    "torturegardenberlin":      "venue",
    "the_lodge_berlin":         "venue",
    "microverse__berlin":       "venue",
    "studio25.berlin":          "venue",
    "revier_suedost":           "venue",
    "loophole.berlin":          "venue",
    "sofarsoundsberlin":        "venue",
    "feinstoffberlin":          "venue",
    "kwia.berlin":              "venue",
    "sonicboomstudios_berlin":  "venue",
    "kicha.studios":            "venue",
    "bulbulberlin":             "venue",
    "salo.community":           "venue",
    "dgtl":                     "venue",
    "the black club":           "venue",
    "kes berlin":               "venue",
}

LABEL_SUBS   = ["records", "recordings", "label", "trax", "discos", "disques",
                 "editions", "imprint", "recs", "schallplatten"]
LABEL_TOKENS = {"rec", "wax", "tapes", "vinyl"}

VENUE_SUBS   = ["club", "festival", "kantine", "boilerroom"]
VENUE_TOKENS = {"bar", "venue", "lounge", "club", "fest", "klub", "stage"}

MEDIA_SUBS   = ["radio", "magazine", "podcast", "pitchfork", "xlr8r", "mixmag",
                 "djmag", "zine"]
MEDIA_TOKENS = {"fm", "media", "press", "news", "mag", "blog"}

DJ_SUBS      = ["deejay", "musik", "muzik", "muze", "musica", "musique",
                 "techno", "disco", "acid", "electro", "minimal", "synth",
                 "produced", "producer", "modular", "darkwave", "coldwave",
                 "postpunk", "italo", "ambient", "industrial", "ebm",
                 "rave", "dnb", "downtempo"]
DJ_TOKENS    = {"dj", "beats", "wave", "bass", "funk", "soul", "jazz"}


def classify(name: str) -> str:
    n      = name.lower().strip()
    tokens = _tokenize(name)
    if n in KNOWN_ACCOUNTS:
        return KNOWN_ACCOUNTS[n]
    if any(s in n for s in LABEL_SUBS):
        return "label"
    if tokens & LABEL_TOKENS:
        return "label"
    if any(s in n for s in VENUE_SUBS):
        return "venue"
    if tokens & VENUE_TOKENS:
        return "venue"
    if any(s in n for s in MEDIA_SUBS):
        return "media"
    if tokens & MEDIA_TOKENS:
        return "media"
    if any(s in n for s in DJ_SUBS):
        return "dj"
    if tokens & DJ_TOKENS:
        return "dj"
    return "other"


# ---------------------------------------------------------------------------
# Genre inference
# ---------------------------------------------------------------------------

GENRE_KEYWORD_MAP: list[tuple[str, str, str]] = [
    ("dark disco",    "Electronic", "Dark Disco"),
    ("darkwave",      "Electronic", "Darkwave"),
    ("coldwave",      "Electronic", "Coldwave"),
    ("minimal synth", "Electronic", "Minimal Synth"),
    ("post-punk",     "Alternative","Post-Punk"),
    ("postpunk",      "Alternative","Post-Punk"),
    ("post punk",     "Alternative","Post-Punk"),
    ("italo",         "Electronic", "Italo Disco"),
    ("disko",         "Electronic", "Disco"),
    ("disco",         "Electronic", "Disco"),
    ("discos",        "Electronic", "Disco"),
    ("acid",          "Electronic", "Acid"),
    ("techno",        "Electronic", "Techno"),
    ("electro",       "Electronic", "Electro"),
    ("ebm",           "Electronic", "EBM"),
    ("industrial",    "Electronic", "Industrial"),
    ("minimal",       "Electronic", "Minimal"),
    ("ambient",       "Electronic", "Ambient"),
    ("downtempo",     "Electronic", "Downtempo"),
    ("slowmo",        "Electronic", "Slowmo"),
    ("synth",         "Electronic", "Synth"),
    ("wave",          "Electronic", "Wave"),
    ("house",         "Electronic", "House"),
    ("rave",          "Electronic", "Rave"),
    ("dnb",           "Electronic", "Drum & Bass"),
    ("dub",           "Electronic", "Dub"),
    ("funk",          "Soul",       "Funk"),
    ("soul",          "Soul",       "Soul"),
    ("jazz",          "Jazz",       "Jazz"),
    ("africa",        "World",      "African"),
    ("world",         "World",      "World"),
    ("groov",         "Electronic", "Groove"),
    ("experimental",  "Electronic", "Experimental"),
    ("digital",       "Electronic", "Electronic"),
    ("hertz",         "Electronic", "Electronic"),
]

KNOWN_GENRE_MAP: dict[str, tuple[str, str]] = {
    "analog africa":             ("World",       "African / Global Bass"),
    "international feel":        ("Electronic",  "Disco / Balearic"),
    "other people":              ("Electronic",  "Experimental / Electronic"),
    "constellation":             ("Alternative", "Post-Rock / Experimental"),
    "minimal wave":              ("Electronic",  "Minimal Synth / Wave"),
    "minimalwave":               ("Electronic",  "Minimal Synth / Wave"),
    "dekmantel":                 ("Electronic",  "Techno / Experimental"),
    "phonica records":           ("Electronic",  "Various"),
    "resident advisor":          ("Electronic",  "Various"),
    "boiler room":               ("Electronic",  "Various"),
    "themes for great cities":   ("Electronic",  "Electronic"),
    "radiant records":           ("Electronic",  "Disco / Electronic"),
    "melopee records":           ("Electronic",  "Disco / Electronic"),
    "dada collective":           ("Electronic",  "Techno / Experimental"),
    "in between":                ("Electronic",  "Electronic"),
    "in between music":          ("Electronic",  "Electronic"),
    "roam recordings":           ("Electronic",  "Ambient / Electronic"),
    "the code":                  ("Electronic",  "Techno"),
    "slow motion records":       ("Electronic",  "Slowmo / Disco"),
    "mm discos":                 ("Electronic",  "Disco / Italo"),
    "off the grid records":      ("Electronic",  "Techno / Minimal"),
    "axylone recordings":        ("Electronic",  "Techno"),
    "eta records":               ("Electronic",  "Electro / Techno"),
    "thf radio":                 ("Electronic",  "Various"),
    "dgtl":                      ("Electronic",  "Techno / Electronic"),
    "young marco":               ("Electronic",  "Disco / Italo"),
    "richie hawtin":             ("Electronic",  "Techno / Minimal"),
    "legowelt":                  ("Electronic",  "Electro / Techno"),
    "legowelt_official":         ("Electronic",  "Electro / Techno"),
    "etienne de crécy":          ("Electronic",  "Electro / House"),
    "persephone":                ("Electronic",  "Techno"),
    "jana fitz":                 ("Electronic",  "Techno"),
    "maayan nidam":              ("Electronic",  "Techno / Electro"),
    "crystal castles":           ("Electronic",  "Darkwave / Synth"),
    "nick cave":                 ("Alternative", "Post-Punk / Dark"),
    "4ad":                       ("Alternative", "Post-Punk / Indie"),
    "sacredbones":               ("Alternative", "Post-Punk / Dark"),
    "sacred bones":              ("Alternative", "Post-Punk / Dark"),
    "clone.nl":                  ("Electronic",  "Electro / Techno"),
    "clonerecords":              ("Electronic",  "Electro / Techno"),
    "dfarecs":                   ("Electronic",  "Post-Punk / Dance"),
    "cybotronlive":              ("Electronic",  "Electro / Techno"),
    "viewlexx":                  ("Electronic",  "Electro"),
    "pinkman":                   ("Electronic",  "Techno / Electro"),
    "life in patterns":          ("Electronic",  "Electronic"),
    "sound metaphors":           ("Electronic",  "Electronic"),
    "la groovie machine":        ("Electronic",  "Disco / Groove"),
    "funnuoyere":                ("Electronic",  "Techno"),
    "status zero":               ("Electronic",  "Techno / EBM"),
    "gauss":                     ("Electronic",  "Techno / Experimental"),
    "demi digital":              ("Electronic",  "Electro / Electronic"),
    "multi culti":               ("World",       "Global / Electronic"),
    "nina kraviz":               ("Electronic",  "Techno / Acid"),
    "ninakraviz":                ("Electronic",  "Techno / Acid"),
    "francisco farfa":           ("Electronic",  "Techno"),
    "kalbata":                   ("World",       "Global Bass / Reggae"),
    "reluctant celebrity":       ("Electronic",  "EBM / Coldwave"),
    "antonio crippa":            ("Electronic",  "Techno"),
    "double figure":             ("Electronic",  "Electro / Synth"),
    "alan myra":                 ("Electronic",  "Techno / EBM"),
    "mechantronica":             ("Electronic",  "Electro / Techno"),
    "lunar disko records":       ("Electronic",  "Disco / Italo"),
    "disco suicide":             ("Electronic",  "Disco / Dark Disco"),
    "sandlett studio":           ("Electronic",  "Electronic"),
    "fanée":                     ("Electronic",  "Electronic"),
    "the black club":            ("Electronic",  "Techno"),
    "bambatta music":            ("Electronic",  "Electro / Disco"),
    "bambatta":                  ("Electronic",  "Electro / Disco"),
    "viewlexx":                  ("Electronic",  "Electro"),
}


def infer_genre(name: str) -> tuple[str, str]:
    """Return (genre_main, genre_sub) for a contact name."""
    n = name.lower().strip()
    if n in KNOWN_GENRE_MAP:
        return KNOWN_GENRE_MAP[n]
    for keyword, main, sub in GENRE_KEYWORD_MAP:
        if keyword in n:
            return main, sub
    return "", ""


# ---------------------------------------------------------------------------
# Location inference
# ---------------------------------------------------------------------------

LOCATION_KEYWORDS: list[tuple[str, str]] = [
    (".berlin",    "Berlin"),
    ("_berlin",    "Berlin"),
    ("berlin",     "Berlin"),
    ("london",     "London"),
    ("brooklyn",   "New York"),
    ("newyork",    "New York"),
    ("nyc",        "New York"),
    ("paris",      "Paris"),
    ("amsterdam",  "Amsterdam"),
    ("chicago",    "Chicago"),
    ("detroit",    "Detroit"),
    ("tokyo",      "Tokyo"),
    ("telaviv",    "Tel Aviv"),
    ("milan",      "Milan"),
    ("milano",     "Milan"),
    ("barcelona",  "Barcelona"),
    ("ibiza",      "Ibiza"),
    ("montreal",   "Montreal"),
    ("glasgow",    "Glasgow"),
    ("brussels",   "Brussels"),
    ("toronto",    "Toronto"),
    ("rotterdam",  "Rotterdam"),
    ("hague",      "The Hague"),
    ("cologne",    "Cologne"),
]

KNOWN_LOCATION_MAP: dict[str, str] = {
    "dekmantel":              "Amsterdam",
    "international feel":     "Ibiza",
    "phonica records":        "London",
    "resident advisor":       "London",
    "ra exchange":            "London",
    "boiler room":            "London",
    "constellation":          "Montreal",
    "young marco":            "Amsterdam",
    "legowelt":               "The Hague",
    "legowelt_official":      "The Hague",
    "richie hawtin":          "Berlin",
    "maayan nidam":           "Berlin",
    "jana fitz":              "Berlin",
    "analog africa":          "Berlin",
    "thf radio":              "Berlin",
    "kes berlin":             "Berlin",
    "dgtl":                   "Amsterdam",
    "minimal wave":           "New York",
    "minimalwave":            "New York",
    "other people":           "New York",
    "sacredbones":            "New York",
    "sacred bones":           "New York",
    "4ad":                    "London",
    "clone.nl":               "Rotterdam",
    "clonerecords":           "Rotterdam",
    "dfarecs":                "New York",
    "viewlexx":               "The Hague",
    "pinkman":                "Rotterdam",
    "berghain_panoramabar":   "Berlin",
    "in.between.berlin":      "Berlin",
    "ninakraviz":             "Moscow / Berlin",
    "nina kraviz":            "Moscow / Berlin",
    "etienne de crécy":       "Paris",
    "la groovie machine":     "Paris",
    "francisco farfa":        "Milan",
    "salo centanaro":         "Rome",
    "antonio crippa":         "Milan",
    "mechantronica":          "Italy",
    "alan myra":              "Berlin",
    "persephone":             "London",
    "crystal castles":        "Toronto",
    "the black club":         "London",
    "cybotronlive":           "Detroit",
}


def infer_location(name: str) -> str:
    """Return city/location string for a contact name."""
    n = name.lower().strip()
    if n in KNOWN_LOCATION_MAP:
        return KNOWN_LOCATION_MAP[n]
    for keyword, city in LOCATION_KEYWORDS:
        if keyword in n:
            return city
    return ""


# ---------------------------------------------------------------------------
# Genre match score (1–5 vs. Inch of Shadow's sound)
# ---------------------------------------------------------------------------

_SCORE5 = {"dark disco", "darkwave", "coldwave", "electro", "acid", "ebm",
            "minimal synth", "synth wave", "ebm / coldwave"}
_SCORE4 = {"techno", "downtempo", "slowmo", "industrial", "italo disco",
            "disco", "minimal", "synth", "electro / techno", "techno / acid",
            "techno / electro", "techno / ebm", "techno / minimal",
            "disco / dark disco", "disco / balearic", "disco / italo"}
_SCORE3 = {"house", "experimental", "post-punk", "rave", "wave",
            "electronic", "groove", "ambient", "post-rock"}
_SCORE2 = {"world", "global", "alternative", "various", "funk", "soul"}


def genre_match_score(genre_main: str, genre_sub: str) -> str:
    """Return '1'–'5' match score, or '' if genre unknown."""
    if not genre_main and not genre_sub:
        return ""
    text = (genre_main + " " + genre_sub).lower()
    for kw in _SCORE5:
        if kw in text:
            return "5"
    for kw in _SCORE4:
        if kw in text:
            return "4"
    for kw in _SCORE3:
        if kw in text:
            return "3"
    for kw in _SCORE2:
        if kw in text:
            return "2"
    return "1"


def _enrich(contact: dict) -> dict:
    """Add genre_main, genre_sub, location, match_score to a contact dict."""
    gm, gs = infer_genre(contact["name"])
    contact["genre_main"]  = gm
    contact["genre_sub"]   = gs
    contact["location"]    = infer_location(contact["name"])
    contact["match_score"] = genre_match_score(gm, gs)
    return contact


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


def deduplicate(contacts: list[dict]) -> list[dict]:
    """
    Merge contacts with the same normalized name across sources.
    First occurrence wins for category/genre/location; sources are combined.
    """
    seen: dict[str, dict] = {}
    result: list[dict] = []
    for c in contacts:
        key = dedup_key(c.get("name", ""))
        if not key:
            result.append(c)
            continue
        if key in seen:
            existing = seen[key]
            srcs = set(existing["source"].split("+"))
            srcs.add(c["source"])
            existing["source"] = "+".join(sorted(srcs))
            if not existing.get("url") and c.get("url"):
                existing["url"] = c["url"]
        else:
            seen[key] = c
            result.append(c)
    return result


def fuzzy_deduplicate(contacts: list[dict]) -> list[dict]:
    """Second-pass fuzzy dedup using SequenceMatcher at 95% threshold.
    Only merges contacts with the same category."""
    keys = [dedup_key(c.get("name", "")) for c in contacts]
    merged = [False] * len(contacts)
    result = []
    for i, contact in enumerate(contacts):
        if merged[i]:
            continue
        for j in range(i + 1, len(contacts)):
            if merged[j]:
                continue
            if contacts[i].get("category") != contacts[j].get("category"):
                continue
            if not keys[i] or not keys[j]:
                continue
            ratio = difflib.SequenceMatcher(None, keys[i], keys[j]).ratio()
            if ratio >= FUZZY_THRESHOLD:
                srcs = set(contact["source"].split("+"))
                srcs.add(contacts[j]["source"])
                contact["source"] = "+".join(sorted(srcs))
                if not contact.get("url") and contacts[j].get("url"):
                    contact["url"] = contacts[j]["url"]
                merged[j] = True
        result.append(contact)
    return result


# ---------------------------------------------------------------------------
# Source 1 — YouTube subscriptions
# ---------------------------------------------------------------------------

def extract_youtube(path: Path) -> list[dict]:
    contacts = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["Channel Title"].strip()
            url  = row["Channel Url"].strip()
            if not name:
                continue
            contacts.append({
                "name":     name,
                "url":      url,
                "category": classify(name),
                "source":   "youtube",
            })
    return contacts


# ---------------------------------------------------------------------------
# Source 2 — Instagram following
# ---------------------------------------------------------------------------

def extract_instagram(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    contacts = []
    for entry in data.get("relationships_following", []):
        username = entry.get("title", "").strip()
        href = ""
        sl = entry.get("string_list_data", [])
        if sl:
            href = sl[0].get("href", "")
        if not username:
            continue
        contacts.append({
            "name":     username,
            "url":      href,
            "category": classify(username),
            "source":   "instagram",
        })
    return contacts


# ---------------------------------------------------------------------------
# Source 3 — ChatGPT PDF
# ---------------------------------------------------------------------------

PDF_ENTITIES = [
    ("Symphonic Distribution",  "distributor", "symphonic"),
    ("DistroKid",               "distributor", "distrokid"),
    ("TuneCore",                "distributor", "tunecore"),
    ("Label-Worx",              "distributor", "label-worx"),
    ("FUGA",                    "distributor", "fuga"),
    ("AWAL",                    "distributor", "awal"),
    ("Ditto Music",             "distributor", "ditto music"),
    ("ONErpm",                  "distributor", "onerpm"),
    ("Amuse",                   "distributor", "amuse"),
    ("Sound.xyz",               "platform",    "sound.xyz"),
    ("Catalog",                 "platform",    "catalog"),
    ("Zora",                    "platform",    "zora"),
    ("Audius",                  "platform",    "audius"),
    ("Royal",                   "platform",    "royal"),
    ("Arpeggi Labs",            "platform",    "arpeggi"),
    ("Revelator",               "platform",    "revelator"),
    ("Beatport",                "platform",    "beatport"),
    ("Traxsource",              "platform",    "traxsource"),
    ("Juno",                    "platform",    "juno"),
]


def extract_pdf(path: Path) -> list[dict]:
    text = extract_text(str(path)).lower()
    contacts = []
    for display_name, entity_type, pattern in PDF_ENTITIES:
        if pattern in text:
            contacts.append({
                "name":     display_name,
                "category": entity_type,
                "source":   "chatgpt_pdf",
            })
    return contacts


# ---------------------------------------------------------------------------
# Source 4 — SoundCloud (visually extracted from 20 screenshots)
# ---------------------------------------------------------------------------

# Manually curated — personal / unidentifiable accounts excluded.
SOUNDCLOUD_ACCOUNTS: list[tuple[str, str]] = [
    # ── Labels ──────────────────────────────────────────────────────────────
    ("Analog Africa",            "label"),
    ("Melopee Records",          "label"),
    ("DADA COLLECTIVE",          "label"),
    ("Axylone Recordings",       "label"),
    ("Roam Recordings",          "label"),
    ("Off The Grid Records",     "label"),
    ("MM DISCOS",                "label"),
    ("Slow Motion Records",      "label"),
    ("Radiant Records",          "label"),
    ("International Feel",       "label"),
    ("Disco Suicide",            "label"),
    ("Lunar Disko Records",      "label"),
    ("Other People",             "label"),
    ("Constellation",            "label"),
    ("Minimal Wave",             "label"),
    ("Sound Metaphors",          "label"),
    ("Life in Patterns",         "label"),
    ("IN BETWEEN",               "label"),
    ("Dekmantel",                "label"),
    ("ETA Records",              "label"),
    ("La Groovie Machine",       "label"),
    ("Sandlett Studio",          "label"),
    ("Fanée",                    "label"),
    ("THE CODE",                 "label"),
    ("La Forme Lente Beaux Arts","label"),
    ("Overground",               "label"),
    # ── DJs / Artists ───────────────────────────────────────────────────────
    ("Camid",                    "dj"),
    ("Tarantella",               "dj"),
    ("Marc Six",                 "dj"),
    ("Nora Makaretsik",          "dj"),
    ("Mr AA",                    "dj"),
    ("MEANT",                    "dj"),
    ("La Dame Noir",             "dj"),
    ("TRASHWEE",                 "dj"),
    ("Francisco Farfa",          "dj"),
    ("Jason Peters",             "dj"),
    ("Raffeeous",                "dj"),
    ("Mosnik",                   "dj"),
    ("Kurt Kjergaard",           "dj"),
    ("Calma Tesla",              "dj"),
    ("Tanir Bayoumi",            "dj"),
    ("GAUSS",                    "dj"),
    ("Demi Digital",             "dj"),
    ("Persephone",               "dj"),
    ("DISCOBASE",                "dj"),
    ("STATUS ZERO",              "dj"),
    ("Salo Centanaro",           "dj"),
    ("Funnuoyere",               "dj"),
    ("Jana Fitz",                "dj"),
    ("DOR",                      "dj"),
    ("Kykid",                    "dj"),
    ("Reluctant Celebrity",      "dj"),
    ("Antonio Crippa",           "dj"),
    ("Kataryna Sano",            "dj"),
    ("Adi Shipsel",              "dj"),
    ("Shai Lasham",              "dj"),
    ("Double Figure",            "dj"),
    ("Orpheu The Wizard",        "dj"),
    ("KDL",                      "dj"),
    ("Mechantronica",            "dj"),
    ("Alan Myra",                "dj"),
    ("Orris",                    "dj"),
    ("Adi Shahal",               "dj"),
    ("aurora",                   "dj"),
    ("Etienne de Crécy",         "dj"),
    ("Young Marco",              "dj"),
    ("Chad Arvel",               "dj"),
    ("Richie Hawtin",            "dj"),
    ("Maayan Nidam",             "dj"),
    ("Legowelt",                 "dj"),
    ("Atlantis",                 "dj"),
    ("One-Eye Witness",          "dj"),
    ("Crystal Castles",          "dj"),
    ("Trip",                     "dj"),
    ("Adam Came",                "dj"),
    ("Paul Coster",              "dj"),
    ("PEZ",                      "dj"),
    ("Nina Kraviz",              "dj"),
    ("BRUBY",                    "dj"),
    ("Rapha",                    "dj"),
    ("chi.lls",                  "dj"),
    ("Nick Cave",                "dj"),
    ("Aatronaut",                "dj"),
    # ── Media ───────────────────────────────────────────────────────────────
    ("THF Radio",                "media"),
    ("Resident Advisor",         "media"),
    ("Boiler Room",              "media"),
    ("RA Exchange",              "media"),
    ("Phonica Records",          "media"),
    ("themes for great cities",  "media"),
    ("disco pastors",            "media"),
    ("Stereo Society",           "media"),
    ("positivesource",           "media"),
    ("WhiteLight/WhiteHeat",     "media"),
    ("Sinachi",                  "media"),
    # ── Venues ──────────────────────────────────────────────────────────────
    ("DGTL",                     "venue"),
    ("The Black Club",           "venue"),
    ("KES Berlin",               "venue"),
]


def extract_soundcloud(_folder: Path) -> list[dict]:
    """Return manually curated SoundCloud following list (from screenshot reading)."""
    return [
        {"name": name, "url": "", "category": category, "source": "soundcloud"}
        for name, category in SOUNDCLOUD_ACCOUNTS
    ]


# ---------------------------------------------------------------------------
# Source 5 — Resident Advisor (pre-fetched JSON)
# ---------------------------------------------------------------------------

def extract_ra_contacts(path: Path) -> list[dict]:
    """Read ra_contacts.json produced by extract_ra.py."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        print("  WARNING: ra_contacts.json is not a list — skipping.")
        return []
    return [c for c in data if c.get("name")]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _print_cats(contacts: list[dict], header: str) -> None:
    cats: dict[str, int] = {}
    for c in contacts:
        cat = c.get("category", "other")
        cats[cat] = cats.get(cat, 0) + 1
    print(f"  {header}")
    for cat, count in sorted(cats.items()):
        print(f"    {cat:<12} {count}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\nScene Intelligence — Contact Extractor")
    print("=" * 42)

    # --- YouTube ---
    print(f"\n[1/4] Reading YouTube subscriptions...")
    if not YOUTUBE_CSV.exists():
        print(f"  ERROR: File not found — {YOUTUBE_CSV}")
        sys.exit(1)
    youtube_contacts = extract_youtube(YOUTUBE_CSV)
    _print_cats(youtube_contacts, f"{len(youtube_contacts)} channels extracted")

    # --- Instagram ---
    print(f"\n[2/4] Reading Instagram following list...")
    if not INSTAGRAM_JSON.exists():
        print(f"  ERROR: File not found — {INSTAGRAM_JSON}")
        sys.exit(1)
    instagram_contacts = extract_instagram(INSTAGRAM_JSON)
    _print_cats(instagram_contacts, f"{len(instagram_contacts)} accounts extracted")

    # --- ChatGPT PDF ---
    print(f"\n[3/4] Reading ChatGPT label conversation PDF...")
    if not CHATGPT_PDF.exists():
        print(f"  ERROR: File not found — {CHATGPT_PDF}")
        sys.exit(1)
    pdf_contacts = extract_pdf(CHATGPT_PDF)
    pdf_cats: dict[str, int] = {}
    for c in pdf_contacts:
        pdf_cats[c["category"]] = pdf_cats.get(c["category"], 0) + 1
    print(f"  {len(pdf_contacts)} entities extracted")
    for cat, count in sorted(pdf_cats.items()):
        print(f"    {cat:<12} {count}")

    # --- SoundCloud ---
    print(f"\n[4/4] Reading SoundCloud following (from screenshots)...")
    sc_contacts = extract_soundcloud(SC_FOLDER)
    _print_cats(sc_contacts, f"{len(sc_contacts)} accounts loaded")

    # --- Resident Advisor (optional) ---
    ra_contacts = []
    if RA_JSON.exists():
        print(f"\n[5/5] Reading Resident Advisor contacts...")
        ra_contacts = extract_ra_contacts(RA_JSON)
        _print_cats(ra_contacts, f"{len(ra_contacts)} contacts loaded")
    else:
        print(f"\n[5/5] Resident Advisor: ra_contacts.json not found — skipping.")
        print(f"      Run: python3 scene_intelligence/extract_ra.py")

    # --- Combine, deduplicate, enrich (music contacts only) ---
    music_contacts = youtube_contacts + instagram_contacts + sc_contacts + ra_contacts
    before = len(music_contacts)
    music_contacts = deduplicate(music_contacts)
    music_contacts = fuzzy_deduplicate(music_contacts)
    dupes = before - len(music_contacts)

    for c in music_contacts:
        _enrich(c)
    for c in pdf_contacts:
        c.update({"genre_main": "", "genre_sub": "", "location": "", "match_score": ""})

    # --- Show enrichment summary ---
    enriched = sum(1 for c in music_contacts if c.get("genre_main"))
    located  = sum(1 for c in music_contacts if c.get("location"))
    print(f"\n  Deduplication:  {dupes} duplicates merged across sources")
    print(f"  Genre inferred: {enriched} contacts")
    print(f"  Location found: {located} contacts")

    # --- Save ---
    # Keep nested structure per source for clarity (multi-source contacts appear in all matching buckets)
    output = {
        "youtube":           [c for c in music_contacts if "youtube"           in c.get("source", "")],
        "instagram":         [c for c in music_contacts if "instagram"         in c.get("source", "")],
        "soundcloud":        [c for c in music_contacts if "soundcloud"        in c.get("source", "")],
        "resident_advisor":  [c for c in music_contacts if "resident_advisor"  in c.get("source", "")],
        "multi_source":      [c for c in music_contacts if "+"                 in c.get("source", "")],
        "chatgpt_labels":    pdf_contacts,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    total = len(music_contacts) + len(pdf_contacts)
    print(f"\n{'=' * 42}")
    print(f"  Total unique contacts: {total}")
    print(f"  Saved to: {OUTPUT_FILE.relative_to(BASE_DIR)}")
    print()


if __name__ == "__main__":
    main()
