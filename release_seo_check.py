#!/usr/bin/env python3
"""release_seo_check.py - the guard script behind the release-prep skill
(strategy, draft and audit modes, System ticket 102).

Pure local text checks. It reads releases/<slug>.json, artist_profile.json (the
artist's own links and credit lines, the same source youtube/tools/yt_release.py
uses) and release_manager/seo_platform_specs.json. It never writes a release
file, never opens a network connection and never touches a platform. Pasting
anything live stays with Amir or the uploads chat.

What it checks, per field (worst first):
  PRIVATE LINK a SoundCloud secret link (/s-...) or an edit/admin URL in copy
  FACTS        ISRC, UPC, catalog number, dates (11 December, Dec 11, 2026-12-11,
               11.12.2026, December 2026), URLs and BPM numbers must match the
               release JSON (public URLs may also come from artist_profile.json)
  PLACEHOLDER  no [TODO ...], <link>, TBD, [CHECK], draft marks left in the text
  NEVER TAG    no tag from platform_tags.tag_rules.never (also inside a longer tag:
               "acid techno"), no text-only word (description_words_only) as a tag,
               and no such hashtag inside a description
  KEY          the musical key goes nowhere: not in copy, not in tags
  DASHES       no em dash, no horizontal bar, no "--", no en dash between words
  BPM          no tempo in copy unless Amir asked ("bpm_in_copy_ok": true); tags fine
  SC TITLE     SoundCloud titles stay plain ("Half the Night", not "Inch of Shadow - ...")
  NAME         "Inch of Shadow" in full, never IoS (warn on other casing)
  LENGTH       character limits from seo_platform_specs.json
  INPUT        a field with no text or tags, or a mistyped key, never passes silently
  APPROVED TEXT  a field marked approved that lacks metadata.description word for word (warn)
  LABEL        another label of his named in this release's copy (warn)
  RELEASE TYPE copy says EP while the release JSON says otherwise (warn); passes when
               metadata.copy_release_type is "EP" (Amir's call for our copy)
  YEAR         a year that is not the release or copyright year (warn)
  HASHTAGS     YouTube description: 3 to 5 hashtags (warn, PLAYBOOK 5.4)
  DUPLICATE    the same tag twice (warn)
Fields marked "voice": true and not "approved" are listed as drafts that need
Amir's OK in the main chat before use.

What it can NOT see (stays a manual check): whether a sentence is true, names of
people, studios or gear, whether a tag page exists, form-only fields (Bandcamp top
genre, profile location), and whether Amir really approved a text. Never-list
words in running text are allowed on purpose (the rule is about tags).

Usage
  python3 release_seo_check.py facts <slug>          the only facts copy may use
  python3 release_seo_check.py facts <slug> --json
  python3 release_seo_check.py check fields.json     pass/fail per field, top 3 fixes first
  python3 release_seo_check.py check fields.json --json
  python3 release_seo_check.py check fields.json --out plans/<file>.md

Fields file (JSON):
  {"release": "<slug>", "mode": "audit", "as_of": "2026-11-16", "source": "...",
   "bpm_in_copy_ok": false,
   "fields": [
     {"platform": "soundcloud", "field": "title", "item": "Half the Night", "text": "Half the Night"},
     {"platform": "soundcloud", "field": "tags", "item": "Half the Night", "tags": ["electro", "acid"]},
     {"platform": "bandcamp", "field": "about", "text": "...", "voice": true, "approved": "2026-11-10 Amir"}
   ]}
Field keys: platform, field, item, text or tags, voice, approved, note. Nothing else.
Exit code 1 when any field fails, 0 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parent
RELEASES = ROOT / "releases"
PROFILE = ROOT / "artist_profile.json"
SPECS = ROOT / "release_manager" / "seo_platform_specs.json"

# Order = severity, used for the top 3 fixes.
SEVERITY = ["PRIVATE LINK", "FACTS", "PLACEHOLDER", "NEVER TAG", "KEY", "DASHES", "BPM", "SC TITLE",
            "NAME", "LENGTH", "INPUT", "APPROVED TEXT", "LABEL", "RELEASE TYPE", "YEAR", "HASHTAGS",
            "DUPLICATE", "RULES"]

HINTS = {
    "PRIVATE LINK": "remove it; secret and edit links never go into public copy",
    "FACTS": "use only the values in the release JSON (python3 release_seo_check.py facts <slug>)",
    "PLACEHOLDER": "fill it from the release JSON or drop the line",
    "NEVER TAG": "remove the tag (locked in platform_tags.tag_rules)",
    "KEY": "remove it; the key never goes in copy or tags (Amir 11-11)",
    "DASHES": "commas and full stops instead (python3 copy_clean.py)",
    "BPM": "drop the tempo from the text; BPM belongs in tags only, unless Amir asks",
    "SC TITLE": "plain title on SoundCloud; SC already adds the artist name (11-11 pass)",
    "NAME": "write Inch of Shadow in full",
    "LENGTH": "shorten to the platform limit",
    "INPUT": "fix the fields file (keys: platform, field, item, text or tags, voice, approved, note)",
    "APPROVED TEXT": "check which exact text Amir approved",
    "LABEL": "check the label: this release is on another one",
    "RELEASE TYPE": "align the copy and the release JSON release_type",
    "YEAR": "check the year against the release JSON",
    "HASHTAGS": "3 to 5 hashtags, last in the description (youtube/PLAYBOOK.md 5.4)",
    "DUPLICATE": "drop the repeated tag",
    "RULES": "lock tag_rules in the release JSON first",
}

TAG_FIELDS = {"tags", "tag_keywords", "hashtags"}
TAGLIKE_TEXT_FIELDS = {"genre"}          # a single value that works as a tag (SC genre = first tag)
FIELD_KEYS = {"platform", "field", "item", "text", "tags", "voice", "approved", "note"}
APPROVED_TEXT_FIELDS = {("soundcloud", "description"), ("soundcloud", "playlist_description"),
                        ("bandcamp", "about")}
# URLs under these key words in the release JSON / artist profile are not public facts.
PRIVATE_KEY_WORDS = {"secret", "edit"}

# (platform, field) -> path in seo_platform_specs.json
LIMIT_PATHS = {
    ("soundcloud", "title"): ("soundcloud", "text_fields", "track_title"),
    ("soundcloud", "description"): ("soundcloud", "text_fields", "track_description"),
    ("soundcloud", "caption"): ("soundcloud", "text_fields", "track_caption"),
    ("soundcloud", "playlist_title"): ("soundcloud", "text_fields", "playlist_title"),
    ("soundcloud", "playlist_description"): ("soundcloud", "text_fields", "playlist_description"),
    ("bandcamp", "album_title"): ("bandcamp", "text_fields", "album_title"),
    ("bandcamp", "track_title"): ("bandcamp", "text_fields", "track_title"),
    ("bandcamp", "bio"): ("bandcamp", "text_fields", "artist_bio"),
    ("youtube", "title"): ("youtube", "video_fields", "title"),
    ("youtube", "description"): ("youtube", "video_fields", "description"),
}

# ---------------------------------------------------------------- patterns
EM_DASH_RE = re.compile("[\u2014\u2015]|-{2,}")
EN_DASH_WORDS_RE = re.compile("(?<=[A-Za-z\\s])\u2013(?=[A-Za-z\\s])")
ISRC_RE = re.compile(r"(?<![A-Za-z0-9])([A-Z]{2})-?([A-Z0-9]{3})-?(\d{2})-?(\d{5})(?![A-Za-z0-9])")
UPC_RE = re.compile(r"(?<!\d)\d{12,13}(?!\d)")
URL_RE = re.compile(r"https?://[^\s<>\"']+|\bwww\.[^\s<>\"']+", re.I)
SC_SECRET_RE = re.compile(r"soundcloud\.com/\S*/s-[A-Za-z0-9]{5,}", re.I)
ADMIN_URL_RE = re.compile(r"edit_album|edit_track|/edit(?:[/?#]|$)|/settings(?:[/?#]|$)|studio\.youtube\.com"
                          r"|artists\.spotify\.com|artists\.apple\.com", re.I)
BPM_NUM_RE = re.compile(r"\b(\d{2,3}(?:[.,]\d+)?)\s?(?:bpm|beats per minute)\b", re.I)
BPM_AFTER_RE = re.compile(r"\b(?:bpm|tempo)[:\s]+(\d{2,3})(?:[.,]\d+)?\b", re.I)
BPM_WORD_RE = re.compile(r"\bbpm\b|\bbeats per minute\b", re.I)
PLACEHOLDER_RE = re.compile(
    r"\[TODO[^\]]*\]?|<[^<>\n]{0,40}(?:link|url|tbd)[^<>\n]{0,40}>|\bTBD\b|\bXXX\b|\[link[^\]]*\]"
    r"|\[(?:CHECK|ASK|HYPOTHESIS|OWN DATA|OFFICIAL|NOT VERIFIED)[^\]]*\]|[\u270d\u2753]", re.I)
NAME_RE = re.compile(r"\bI[oO]S\b")
NAME_CASE_RE = re.compile(r"\binch\s+of\s+shadow\b", re.I)
HASHTAG_RE = re.compile(r"(?:(?<=\s)|^)#[A-Za-z0-9_]+")
EP_RE = re.compile(r"\bEP\b")
YEAR_RE = re.compile(r"(?<![\d-])((?:19|20)\d\d)(?![\d-])")
# Keys in copy: note letter upper case. "Fm", "C#m", "Ebm" (EBM and DM stay clear).
KEY_SHORT_RE = re.compile("(?<![A-Za-z0-9])[A-G][#b\u266f\u266d]?m(?![A-Za-z0-9'])")
KEY_LONG_RE = re.compile("(?<![A-Za-z0-9])([A-G])([#b\u266f\u266d]?)[ -]?(minor|major|min|maj)\\b", re.I)
KEY_SPELLED_RE = re.compile(r"(?<![A-Za-z0-9])[A-G][ -]?(?:sharp|flat)[ -]?(?:minor|major|min|maj)\b", re.I)
KEY_OF_RE = re.compile(r"\bin the key of\b|\bkey of [A-G]\b|\bkey: ?[A-G]", re.I)
CAMELOT_RE = re.compile(r"(?<![A-Za-z0-9])(?:1[0-2]|[1-9])[AB](?![A-Za-z0-9])")
# Keys as a whole tag (tags are often lower case): "f minor", "fm", "c#m", "8a".
# A "b" flat only together with the word ("eb minor"): "ebm" as a tag is the genre EBM.
KEY_TAG_RE = re.compile("^(?:[a-g][#\u266f\u266d]?m|[a-g][#b\u266f\u266d]?\\s?(?:minor|major|min|maj)"
                        "|[a-g][ -]?(?:sharp|flat)[ -]?(?:minor|major|min|maj)"
                        "|(?:1[0-2]|[1-9])[ab]|key\\b.*)$", re.I)

MONTHS = {m: i for i, names in enumerate([
    ("jan", "january"), ("feb", "february"), ("mar", "march"), ("apr", "april"), ("may",),
    ("jun", "june"), ("jul", "july"), ("aug", "august"), ("sep", "sept", "september"),
    ("oct", "october"), ("nov", "november"), ("dec", "december")], start=1) for m in names}
_MON = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sept?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
ISO_DATE_RE = re.compile(r"\b(20\d\d)-(\d\d)-(\d\d)\b")
NUM_DATE_RE = re.compile(r"(?<![\d./])(\d{1,2})[./](\d{1,2})[./](20\d\d|\d\d)(?![\d./])")
DMY_RE = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?" + _MON + r"\b\.?(?:,?\s+(20\d\d))?", re.I)
MDY_RE = re.compile(r"\b" + _MON + r"\.?\s+(\d{1,2})(?:st|nd|rd|th)?\b(?:,?\s+(20\d\d))?", re.I)
MY_RE = re.compile(r"\b" + _MON + r"\.?,?\s+(20\d\d)\b", re.I)


# ---------------------------------------------------------------- loading
def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_release(slug: str, releases_dir: Path = RELEASES) -> dict:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug or ""):
        raise SystemExit("Bad release slug: %r" % slug)
    path = releases_dir / (slug + ".json")
    if not path.is_file():
        raise SystemExit("No release file: %s" % path)
    return load_json(path)


def _walk_urls(obj, path: Tuple[str, ...] = ()) -> Iterable[str]:
    """Public URLs only: anything under a key named secret_* or edit_* is left out."""
    if isinstance(obj, str):
        words = {w for seg in path for w in re.split(r"[\W_]+", seg.lower())}
        if not words & PRIVATE_KEY_WORDS:
            for u in URL_RE.findall(obj):
                if not SC_SECRET_RE.search(u) and not ADMIN_URL_RE.search(u):
                    yield u
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk_urls(v, path + (str(k),))
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_urls(v, path)


def norm_url(url: str) -> str:
    url = url.strip().rstrip(".,;:)]}!?'\"")
    url = re.sub(r"^https?://", "", url, flags=re.I)
    host, _, rest = url.partition("/")
    host = host.lower()
    if host.startswith("www."):
        host = host[4:]
    out = host + ("/" + rest if rest else "")
    return out.rstrip("/")


def norm_tag(tag: str) -> str:
    return re.sub(r"\s+", " ", str(tag).strip().lstrip("#").lower())


def _norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _catalog_patterns(cats: Iterable[str]) -> List[Tuple["re.Pattern", int]]:
    """ICR-003 -> a pattern for any ICR number; only the release's own prefix is checked,
    so gear names (TB-303, TR-808) are left alone."""
    out = []
    for c in cats:
        m = re.fullmatch(r"\s*([A-Za-z]{2,6})[- ]?(\d{1,5})\s*", c)
        if m:
            out.append((re.compile(r"(?<![A-Za-z0-9])" + re.escape(m.group(1)) + r"[- ]?(\d{1,5})(?!\d)", re.I),
                        int(m.group(2))))
    return out


def _own_key_patterns(keys: Iterable[str]) -> List[Tuple[str, "re.Pattern"]]:
    """The release's own key, any case: 'Fm' on file also catches 'f minor' in copy."""
    out = []
    for k in keys:
        m = re.fullmatch("\\s*([A-Ga-g])\\s*([#b\u266f\u266d]|sharp|flat)?\\s*(m|min|minor|maj|major)?\\s*", k)
        if not m:
            continue
        note, acc, q = m.group(1).lower(), (m.group(2) or "").lower(), (m.group(3) or "maj").lower()
        accp = {"": "", "#": "(?:#|\u266f|[ -]?sharp)", "\u266f": "(?:#|\u266f|[ -]?sharp)", "sharp": "(?:#|\u266f|[ -]?sharp)",
                "b": "(?:b|\u266d|[ -]?flat)", "\u266d": "(?:b|\u266d|[ -]?flat)", "flat": "(?:b|\u266d|[ -]?flat)"}[acc]
        qual = "(?:minor|min)" if q in ("m", "min", "minor") else "(?:major|maj)"
        out.append((note + ("x" if acc else ""),
                    re.compile(r"(?<![A-Za-z0-9])" + note + accp + r"[ -]?" + qual + r"\b", re.I)))
    return out


def build_facts(release: dict, profile: Optional[dict] = None) -> dict:
    """Everything copy may state, from the structured release fields (+ the artist profile links)."""
    md = release.get("metadata", {}) or {}
    tracks = release.get("tracks", []) or []
    dist = release.get("distribution", {}) or {}
    rules = (release.get("platform_tags", {}) or {}).get("tag_rules", {}) or {}
    urls: Set[str] = {norm_url(u) for u in _walk_urls(release)}
    if profile:
        urls |= {norm_url(u) for u in _walk_urls(profile)}
    dates = {d for d in (release.get("release_date"), dist.get("live_date")) if d}
    labels_all = [l for l in (profile or {}).get("labels", [])]
    label_text = " ".join(str(md.get(k, "")) for k in ("copyright", "copyright_p", "label"))
    labels_release = [l for l in labels_all if l.lower() in label_text.lower()]
    years = {int(d[:4]) for d in dates if d[:4].isdigit()} | {int(y) for y in YEAR_RE.findall(label_text)}
    cats = {c for c in [md.get("catalog_number")] if c}
    keys = {t.get("key") for t in tracks if t.get("key")}
    return {
        "slug": release.get("slug", ""),
        "artist": md.get("artist", ""),
        "title": md.get("title", ""),
        "release_type": md.get("release_type", ""),
        "copy_release_type": md.get("copy_release_type", "") or "",
        "release_date": release.get("release_date", ""),
        "approved_description": md.get("description", "") or "",
        "catalog_numbers": cats,
        "catalog_patterns": _catalog_patterns(cats),
        "upcs": {u for u in [dist.get("upc")] if u},
        "isrcs": {t.get("isrc").replace("-", "") for t in tracks if t.get("isrc")},
        "bpms": {int(round(float(t["bpm"]))) for t in tracks if t.get("bpm")},
        "keys": keys,
        "own_key_patterns": _own_key_patterns(keys),
        "dates": dates,
        "years": years,
        "urls": urls,
        "labels_all": labels_all,
        "labels_release": labels_release,
        "never": {norm_tag(t) for t in rules.get("never", [])},
        "text_only": {norm_tag(t) for t in rules.get("description_words_only", [])},
        "has_rules": bool(rules.get("never")),
    }


def spec_limit(specs: dict, platform: str, field: str) -> Optional[int]:
    path = LIMIT_PATHS.get((platform, field))
    if not path:
        return None
    node = specs.get("platforms", {})
    for key in path:
        node = (node or {}).get(key)
    return (node or {}).get("max_chars") if isinstance(node, dict) else None


# ---------------------------------------------------------------- checks
def _quote(text: str, start: int, end: int, pad: int = 18) -> str:
    a, b = max(0, start - pad), min(len(text), end + pad)
    snippet = text[a:b].replace("\n", " ")
    return ("..." if a > 0 else "") + snippet + ("..." if b < len(text) else "")


def _date_known(year, month, day, known: Set[str]) -> bool:
    for d in known:
        try:
            ky, km, kd = (int(x) for x in d[:10].split("-"))
        except ValueError:
            continue
        if km == month and (day is None or kd == day) and (year is None or year == ky):
            return True
    return False


def _dates_in(text: str):
    """Yields (match, ok(known_dates) -> bool). Earlier patterns win an overlap."""
    for m in ISO_DATE_RE.finditer(text):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        yield m, (lambda k, y=y, mo=mo, d=d: _date_known(y, mo, d, k))
    for m in NUM_DATE_RE.finditer(text):
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y = y + 2000 if y < 100 else y
        # 11.12.2026 (day first) or 12/11/2026 (month first): either reading may match
        yield m, (lambda k, a=a, b=b, y=y: _date_known(y, b, a, k) or _date_known(y, a, b, k))
    for m in DMY_RE.finditer(text):
        y, mo, d = (int(m.group(3)) if m.group(3) else None), MONTHS[m.group(2).lower()], int(m.group(1))
        yield m, (lambda k, y=y, mo=mo, d=d: _date_known(y, mo, d, k))
    for m in MDY_RE.finditer(text):
        y, mo, d = (int(m.group(3)) if m.group(3) else None), MONTHS[m.group(1).lower()], int(m.group(2))
        yield m, (lambda k, y=y, mo=mo, d=d: _date_known(y, mo, d, k))
    for m in MY_RE.finditer(text):
        y, mo = int(m.group(2)), MONTHS[m.group(1).lower()]
        yield m, (lambda k, y=y, mo=mo: _date_known(y, mo, None, k))


def _list_hit(tag: str, words: Set[str]) -> Optional[Tuple[str, str]]:
    """('exact' | 'word' | 'part', the listed word) when a tag is, contains as a whole word,
    or contains glued together (#acidtechno) a word from the list."""
    squashed = tag.replace(" ", "")
    for n in sorted(words):
        if tag == n or squashed == n.replace(" ", ""):
            return "exact", n
    for n in sorted(words):
        if re.search(r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])", tag):
            return "word", n
    for n in sorted(words):
        nsq = n.replace(" ", "")
        if len(nsq) >= 5 and nsq in squashed:
            return "part", n
    return None


def check_text(text: str, facts: dict, platform: str, field: str, bpm_ok: bool) -> List[dict]:
    issues = []

    def add(check, level, quote, note=""):
        issues.append({"check": check, "level": level, "quote": quote, "note": note})

    # URLs first; every other check runs on the text with the URLs blanked out
    for u in URL_RE.findall(text):
        shown = u.rstrip(".,;:)")
        if SC_SECRET_RE.search(u):
            add("PRIVATE LINK", "FAIL", shown, "SoundCloud secret link")
        elif ADMIN_URL_RE.search(u):
            add("PRIVATE LINK", "FAIL", shown, "edit or admin URL")
        elif norm_url(u) not in facts["urls"]:
            add("FACTS", "FAIL", shown, "URL not in the release JSON or artist_profile.json")
    body = URL_RE.sub(lambda m: " " * len(m.group(0)), text)

    # FACTS
    for m in ISRC_RE.finditer(body):
        if "".join(m.groups()) not in facts["isrcs"]:
            add("FACTS", "FAIL", m.group(0), "ISRC not in the release JSON")
    for m in UPC_RE.finditer(body):
        if m.group(0) not in facts["upcs"]:
            add("FACTS", "FAIL", m.group(0), "UPC not in the release JSON")
    for rx, number in facts["catalog_patterns"]:
        for m in rx.finditer(body):
            if int(m.group(1)) != number:
                add("FACTS", "FAIL", m.group(0), "catalog number not in the release JSON (%s)"
                    % ", ".join(sorted(facts["catalog_numbers"])))
    spans: List[Tuple[int, int]] = []
    for m, ok in _dates_in(body):
        if any(m.start() < e and s < m.end() for s, e in spans):
            continue
        spans.append((m.start(), m.end()))
        if not ok(facts["dates"]):
            add("FACTS", "FAIL", m.group(0).strip(),
                "date is not the release date in the release JSON (%s)" % (facts["release_date"] or "none set"))
    bpm_hits = list(BPM_NUM_RE.finditer(body))
    bpm_hits += [m for m in BPM_AFTER_RE.finditer(body)          # "tempo 127 BPM" is one hit, not two
                 if not any(m.start() < h.end() and h.start() < m.end() for h in bpm_hits)]
    for m in bpm_hits:
        if int(round(float(m.group(1).replace(",", ".")))) not in facts["bpms"]:
            add("FACTS", "FAIL", m.group(0), "BPM not in the release JSON")

    # PLACEHOLDER
    for m in PLACEHOLDER_RE.finditer(text):
        add("PLACEHOLDER", "FAIL", _quote(text, m.start(), m.end(), 0))

    # hashtags inside the text count as tags for the never list and the key
    for h in HASHTAG_RE.findall(body):
        issues.extend(i for i in check_tags([h], facts) if i["check"] in ("NEVER TAG", "KEY"))

    # KEY
    key_spans: List[Tuple[int, int]] = []

    def key(m, level="FAIL", note=""):
        if any(m.start() < e and s < m.end() for s, e in key_spans):
            return
        key_spans.append((m.start(), m.end()))
        add("KEY", level, _quote(body, m.start(), m.end()), note)

    for rx in (KEY_SPELLED_RE, KEY_OF_RE, CAMELOT_RE):
        for m in rx.finditer(body):
            key(m)
    for m in KEY_LONG_RE.finditer(body):
        if m.group(1).islower():
            continue  # only an upper-case note letter counts here ("a minor detail" is English)
        # "A minor ..." / "A major label" can be the article at a sentence start: warn
        if m.group(1) == "A" and not m.group(2):
            key(m, "WARN", "maybe the article, check")
        else:
            key(m)
    for m in KEY_SHORT_RE.finditer(body):
        if m.group(0) == "Am":
            key(m, "WARN", "maybe the word Am, check")   # "I Am the Night"
        else:
            key(m)
    for note, rx in facts["own_key_patterns"]:
        for m in rx.finditer(body):
            if note == "a":
                key(m, "WARN", "the key on file for this release, or the article: check")
            else:
                key(m, "FAIL", "the key on file for this release")

    # DASHES
    for rx in (EM_DASH_RE, EN_DASH_WORDS_RE):
        for m in rx.finditer(body):
            add("DASHES", "FAIL", _quote(body, m.start(), m.end()))

    # BPM in copy
    if not bpm_ok:
        found = bpm_hits or list(BPM_WORD_RE.finditer(body))
        for m in found:
            add("BPM", "FAIL", _quote(body, m.start(), m.end()))

    # SC TITLE
    if platform == "soundcloud" and field in ("title", "playlist_title") and facts["artist"]:
        if re.match(re.escape(facts["artist"]) + "\\s*[-\u2013\u2014:|]", text.strip(), re.I):
            add("SC TITLE", "FAIL", text.strip())

    # NAME
    for m in NAME_RE.finditer(body):
        add("NAME", "FAIL", _quote(body, m.start(), m.end()))
    for m in NAME_CASE_RE.finditer(body):
        if _norm_ws(m.group(0)) != "Inch of Shadow":
            add("NAME", "WARN", _quote(body, m.start(), m.end()), "casing: Inch of Shadow")

    # LABEL
    low = body.lower()
    for lab in facts["labels_all"]:
        if lab not in facts["labels_release"] and lab.lower() in low:
            i = low.index(lab.lower())
            add("LABEL", "WARN", _quote(body, i, i + len(lab)), "not this release's label")

    # RELEASE TYPE
    rtype = (facts["release_type"] or "").strip().lower()
    copy_type = (facts.get("copy_release_type") or "").strip().lower()
    if rtype and rtype != "ep" and copy_type != "ep":   # copy_release_type "EP" = Amir's call for our copy
        m = EP_RE.search(body)
        if m:
            add("RELEASE TYPE", "WARN", _quote(body, m.start(), m.end()),
                "the release JSON says release_type %r" % facts["release_type"])

    # YEAR (a year standing alone, outside a full date)
    if facts["years"]:
        for m in YEAR_RE.finditer(body):
            if any(m.start() < e and s < m.end() for s, e in spans):
                continue
            if int(m.group(1)) not in facts["years"]:
                add("YEAR", "WARN", _quote(body, m.start(), m.end()),
                    "not the release or copyright year (%s)" % ", ".join(str(y) for y in sorted(facts["years"])))

    # HASHTAGS on YouTube
    if platform == "youtube" and field == "description":
        n = len(HASHTAG_RE.findall(body))
        if not 3 <= n <= 5:
            add("HASHTAGS", "WARN", "%d hashtag%s" % (n, "" if n == 1 else "s"), "PLAYBOOK 5.4 wants 3 to 5")
    return issues


def check_tags(tags: List[str], facts: dict) -> List[dict]:
    issues = []

    def add(check, level, quote, note=""):
        issues.append({"check": check, "level": level, "quote": quote, "note": note})

    seen = {}
    for raw in tags:
        raw = str(raw)
        t = norm_tag(raw)
        squashed = t.replace(" ", "")
        hit = _list_hit(t, facts["never"])
        if hit:
            kind, word = hit
            if kind == "exact":
                add("NEVER TAG", "FAIL", raw, "on the never list (tag_rules.never)")
            elif kind == "word":
                add("NEVER TAG", "FAIL", raw, "contains the never-list word %r" % word)
            else:
                add("NEVER TAG", "WARN", raw, "may contain the never-list word %r, check" % word)
        else:
            hit = _list_hit(t, facts["text_only"])
            if hit and hit[0] in ("exact", "word"):
                add("NEVER TAG", "FAIL", raw, "text-only word %r (tag_rules.description_words_only)" % hit[1])
        if KEY_TAG_RE.match(t) or any(rx.fullmatch(t) for _, rx in facts["own_key_patterns"]):
            add("KEY", "FAIL", raw)
        if EM_DASH_RE.search(raw) or EN_DASH_WORDS_RE.search(raw):
            add("DASHES", "FAIL", raw)
        if NAME_RE.search(raw):
            add("NAME", "FAIL", raw)
        m = BPM_NUM_RE.search(raw) or BPM_AFTER_RE.search(raw)
        if m and int(round(float(m.group(1).replace(",", ".")))) not in facts["bpms"]:
            add("FACTS", "FAIL", raw, "BPM not in the release JSON")
        if PLACEHOLDER_RE.search(raw):
            add("PLACEHOLDER", "FAIL", raw)
        if squashed in seen:
            add("DUPLICATE", "WARN", raw, "same as %r" % seen[squashed])
        else:
            seen[squashed] = raw
    return issues


def _split_tags(text: str) -> List[str]:
    return [t.strip() for t in re.split(r"[,\n]+|\s+(?=#)", text) if t.strip()]


def check_field(f: dict, facts: dict, specs: dict, bpm_ok: bool) -> dict:
    issues: List[dict] = []

    def bad(level, quote, note):
        issues.append({"check": "INPUT", "level": level, "quote": quote, "note": note})

    if not isinstance(f, dict):
        f = {"_": f}
    platform = str(f.get("platform", "")).strip().lower()
    field = str(f.get("field", "")).strip().lower()
    if not platform or not field:
        bad("FAIL", "platform / field", "both are required")
    for k in sorted(set(f) - FIELD_KEYS):
        bad("WARN", str(k), "unknown key, ignored")

    if "tags" in f or field in TAG_FIELDS:
        tags = f["tags"] if "tags" in f else f.get("text")
        if isinstance(tags, str):
            tags = _split_tags(tags)
        if not isinstance(tags, list):
            bad("FAIL", field or "tags", "no tags given (a list under \"tags\")")
            tags = []
        tags = [str(t).strip() for t in tags if str(t).strip()]
        if not tags and not any(i["level"] == "FAIL" for i in issues):
            bad("WARN", field, "empty tag list, nothing checked")
        issues += check_tags(tags, facts)
        if platform == "youtube":
            total = len(", ".join(tags))
            lim = (specs.get("platforms", {}).get("youtube", {}).get("video_fields", {})
                   .get("tags", {}).get("max_total_chars"))
            if lim and total > lim:
                issues.append({"check": "LENGTH", "level": "FAIL", "quote": "%d / %d characters" % (total, lim),
                               "note": ""})
    elif isinstance(f.get("text"), str):
        text = f["text"]
        if not text.strip():
            bad("WARN", field, "empty text, nothing checked")
        issues += check_text(text, facts, platform, field, bpm_ok)
        if field in TAGLIKE_TEXT_FIELDS and text.strip():
            issues += [i for i in check_tags([text], facts) if i["check"] in ("NEVER TAG", "KEY")]
        lim = spec_limit(specs, platform, field)
        if lim and len(text) > lim:
            issues.append({"check": "LENGTH", "level": "FAIL", "quote": "%d / %d characters" % (len(text), lim),
                           "note": ""})
        approved_text = _norm_ws(facts["approved_description"])
        if (f.get("approved") and (platform, field) in APPROVED_TEXT_FIELDS and approved_text
                and approved_text not in _norm_ws(text)):
            issues.append({"check": "APPROVED TEXT", "level": "WARN", "quote": _quote(text, 0, 40, 0),
                           "note": "marked approved, but metadata.description is not in it word for word"})
    else:
        bad("FAIL", field or "field", "no \"text\" and no \"tags\": nothing was checked")

    status = "FAIL" if any(i["level"] == "FAIL" for i in issues) else (
        "WARN" if issues else "PASS")
    draft = bool(f.get("voice")) and not f.get("approved")
    return {"platform": platform, "field": field, "item": str(f.get("item", "") or ""), "status": status,
            "draft": draft, "approved": str(f.get("approved", "") or ""), "issues": issues}


def run_check(doc: dict, releases_dir: Path = RELEASES, profile_path: Path = PROFILE,
              specs_path: Path = SPECS) -> dict:
    if not isinstance(doc, dict):
        raise SystemExit("The fields file must be a JSON object with \"release\" and \"fields\"")
    fields = doc.get("fields")
    if not isinstance(fields, list) or not fields:
        raise SystemExit("No fields to check: \"fields\" must be a list with at least one field")
    release = load_release(str(doc.get("release", "")), releases_dir)
    profile = load_json(profile_path) if profile_path.is_file() else {}
    specs = load_json(specs_path) if specs_path.is_file() else {}
    facts = build_facts(release, profile)
    bpm_ok = doc.get("bpm_in_copy_ok") is True
    results = [check_field(f, facts, specs, bpm_ok) for f in fields]
    release_issues = []
    if not facts["has_rules"]:
        release_issues.append({"check": "RULES", "level": "WARN", "quote": "platform_tags.tag_rules.never is empty",
                               "note": "the never-tag check had nothing to check against"})
    fixes = []
    for r in results:
        for i in r["issues"]:
            if i["level"] == "FAIL":
                fixes.append((SEVERITY.index(i["check"]), r, i))
    fixes.sort(key=lambda x: x[0])
    # one fix per problem (check), listing every field it hits, worst problems first
    top: List[dict] = []
    for _, r, i in fixes:
        line = next((t for t in top if t["check"] == i["check"]), None)
        if line is None:
            if len(top) == 3:
                continue
            line = {"where": [], "check": i["check"], "quote": i["quote"], "fix": HINTS[i["check"]]}
            top.append(line)
        if _where(r) not in line["where"]:
            line["where"].append(_where(r))
    verdict = "FAIL" if any(r["status"] == "FAIL" for r in results) else (
        "WARN" if any(r["status"] == "WARN" for r in results) or release_issues else "PASS")
    return {"release": facts["slug"], "mode": doc.get("mode", "audit"), "as_of": doc.get("as_of", ""),
            "source": doc.get("source", ""), "verdict": verdict, "top_fixes": top,
            "release_issues": release_issues, "fields": results,
            "drafts": [_where(r) for r in results if r["draft"]]}


def _where(r: dict) -> str:
    return "%s %s%s" % (r["platform"], r["field"], " (%s)" % r["item"] if r["item"] else "")


# ---------------------------------------------------------------- output
def render_report(rep: dict) -> str:
    n = len(rep["fields"])
    nf = sum(1 for r in rep["fields"] if r["status"] == "FAIL")
    nw = sum(1 for r in rep["fields"] if r["status"] == "WARN")
    out = ["RELEASE SEO CHECK  %s  (%s%s)" % (rep["release"], rep["mode"],
                                             ", as of " + rep["as_of"] if rep["as_of"] else "")]
    if rep["source"]:
        out.append("Source: " + rep["source"])
    out.append("Verdict: %s  (%d fields: %d fail, %d warn, %d pass; %d draft%s need Amir's OK)" % (
        rep["verdict"], n, nf, nw, n - nf - nw, len(rep["drafts"]), "" if len(rep["drafts"]) == 1 else "s"))
    out += ["", "TOP 3 FIXES"]
    if not rep["top_fixes"]:
        out.append("  none, nothing fails")
    for k, t in enumerate(rep["top_fixes"], 1):
        out.append('  %d. %s "%s" -> %s' % (k, t["check"], t["quote"], t["fix"]))
        out.append("     in: " + "; ".join(t["where"]))
    for i in rep["release_issues"]:
        out.append("  release: %s %s, %s" % (i["check"], i["quote"], i["note"]))
    out += ["", "PER FIELD"]
    for r in rep["fields"]:
        tag = "  DRAFT (his voice, needs Amir's OK)" if r["draft"] else (
            "  approved: " + r["approved"] if r["approved"] else "")
        out.append("%-5s %s%s" % (r["status"], _where(r), tag))
        for i in r["issues"]:
            out.append('      %-4s %-13s "%s"%s' % (i["level"], i["check"], i["quote"],
                                                  "  (" + i["note"] + ")" if i["note"] else ""))
    if rep["drafts"]:
        out += ["", "DRAFTS FOR AMIR'S OK (main chat, before any use)"] + ["  " + d for d in rep["drafts"]]
    out.append("")
    out.append("Nothing was written live. This report is local text only.")
    return "\n".join(out) + "\n"


def facts_sheet(slug: str, releases_dir: Path = RELEASES, profile_path: Path = PROFILE) -> dict:
    release = load_release(slug, releases_dir)
    md = release.get("metadata", {}) or {}
    pt = release.get("platform_tags", {}) or {}
    rules = pt.get("tag_rules", {}) or {}
    dist = release.get("distribution", {}) or {}
    return {
        "slug": release.get("slug", slug), "artist": md.get("artist", ""), "title": md.get("title", ""),
        "release_type": md.get("release_type", ""), "copy_release_type": md.get("copy_release_type", "") or "",
        "release_date": release.get("release_date", ""),
        "label_line": md.get("copyright", ""), "catalog_number": md.get("catalog_number", ""),
        "upc": dist.get("upc", ""), "lane": release.get("lane", ""),
        "approved_description": md.get("description", ""),
        "tracks": [{"number": t.get("number"), "title": t.get("title"), "isrc": t.get("isrc"),
                    "bpm_tags_only": t.get("bpm"), "duration": t.get("duration"),
                    "key": "on file, never in copy or tags" if t.get("key") else ""}
                   for t in release.get("tracks", [])],
        "soundcloud": {"genre": (pt.get("soundcloud") or {}).get("genre", ""),
                       "tags": (pt.get("soundcloud") or {}).get("tags", [])},
        "bandcamp_tags": (pt.get("bandcamp") or {}).get("tags", []),
        "hashtags": pt.get("hashtags", []),
        "tag_rules": {"locked": rules.get("locked", ""), "never": rules.get("never", []),
                      "text_only": rules.get("description_words_only", [])},
        "links": {k: v for k, v in (release.get("platform_links") or {}).items() if v},
        "campaign_links": release.get("bandcamp_campaign_links", {}),
    }


def render_facts(f: dict) -> str:
    out = ["FACT SHEET  %s  (the only facts copy may use)" % f["slug"],
           "%s - %s  |  %s  |  release %s  |  %s  |  %s  |  UPC %s" % (
               f["artist"], f["title"],
               f["release_type"] + ("  (store)  copy says: %s" % f["copy_release_type"]
                                    if f["copy_release_type"] and f["copy_release_type"] != f["release_type"] else ""),
               f["release_date"], f["label_line"],
               f["catalog_number"], f["upc"]),
           "Approved description: " + (f["approved_description"] or "(none)"), "", "Tracks"]
    for t in f["tracks"]:
        out.append("  %s. %s  ISRC %s  %s  BPM %s (tags only)%s" % (
            t["number"], t["title"], t["isrc"], t["duration"], t["bpm_tags_only"],
            "  key: " + t["key"] if t["key"] else ""))
    out += ["", "SoundCloud genre: %s  tags: %s" % (f["soundcloud"]["genre"], ", ".join(f["soundcloud"]["tags"])),
            "Bandcamp tags: " + ", ".join(f["bandcamp_tags"]),
            "Hashtags: " + ", ".join(f["hashtags"]),
            "Tag rules (locked %s)" % (f["tag_rules"]["locked"] or "NOT LOCKED"),
            "  never as tags: " + (", ".join(f["tag_rules"]["never"]) or "(empty, lock it first)"),
            "  text only: " + (", ".join(f["tag_rules"]["text_only"]) or "(none)"), "", "Links"]
    for k, v in list(f["links"].items()) + list(f["campaign_links"].items()):
        out.append("  %s: %s" % (k, v))
    return "\n".join(out) + "\n"


def _safe_out(path: Path, input_path: Optional[Path]) -> Path:
    p = path.resolve()
    if RELEASES.resolve() in p.parents or p.parent == RELEASES.resolve():
        raise SystemExit("Refused: the report never goes into releases/ (release files are not written here)")
    if input_path is not None and p == input_path.resolve():
        raise SystemExit("Refused: --out would overwrite the input file")
    if p.suffix.lower() not in (".md", ".txt", ".json"):
        raise SystemExit("Refused: --out must be .md, .txt or .json")
    if p.exists():
        head = p.read_text(encoding="utf-8", errors="replace")[:400]
        if not (head.startswith("RELEASE SEO CHECK") or '"top_fixes"' in head or '"verdict"' in head):
            raise SystemExit("Refused: %s exists and is not an earlier report of this script" % p.name)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Release SEO guard: facts sheet and field checks (local only).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("facts", help="print the fact sheet for a release")
    a.add_argument("slug")
    a.add_argument("--json", action="store_true")
    b = sub.add_parser("check", help="check a fields file (strategy, draft or audit)")
    b.add_argument("fields")
    b.add_argument("--json", action="store_true")
    b.add_argument("--out", help="also save the report (.md/.txt/.json, never into releases/)")
    args = ap.parse_args(argv)

    if args.cmd == "facts":
        f = facts_sheet(args.slug)
        sys.stdout.write(json.dumps(f, indent=2, ensure_ascii=False) + "\n" if args.json else render_facts(f))
        return 0

    src = Path(args.fields)
    doc = load_json(src)
    rep = run_check(doc)
    text = json.dumps(rep, indent=2, ensure_ascii=False) + "\n" if args.json else render_report(rep)
    sys.stdout.write(text)
    if args.out:
        out = _safe_out(Path(args.out), src)
        out.write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n" if out.suffix == ".json"
                       else render_report(rep), encoding="utf-8")
    return 1 if rep["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
