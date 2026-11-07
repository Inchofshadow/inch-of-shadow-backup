"""
scene_intelligence/classify_subtypes.py
-----------------------------------------
Tool 1 -- Scene Intelligence Engine: Sub-Type Classification

Enriches contacts with:
  sub_type           -- classification within each category (radio, premiere, press, etc.)
  label_connections  -- for DJs: which labels in our database they release on
  relevance_score    -- 0-100 computed ranking for sort order

Also fixes known category miscategorizations and deletes irrelevant contacts.

Usage:
  python3 scene_intelligence/classify_subtypes.py           # Run classification
  python3 scene_intelligence/classify_subtypes.py --dry-run # Preview changes
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR      = Path(__file__).parent.parent
ENRICHED_FILE = BASE_DIR / "scene_intelligence" / "enriched_contacts.json"

sys.path.insert(0, str(Path(__file__).parent))
from utils import dedup_key


# ---------------------------------------------------------------------------
# Media sub-type detection
# ---------------------------------------------------------------------------

# Radio stations (performance opportunities -- live sets, mixes)
_MEDIA_RADIO_NAMES = {
    "hoer.berlin", "thfradio", "nts_radio", "redlightradio",
    "operator.radio", "backsideradio_official", "hopestradio",
    "mutantradiotbilisi", "radio.d59b", "ibizasonica", "teder.fm",
    "intergalacticfm",
}
_MEDIA_RADIO_KEYWORDS = {"radio", ".fm"}

# Premiere channels (paid promotion for singles)
_MEDIA_PREMIERE_NAMES = {
    "sinachi", "one-eye witness", "themes for great cities",
    "whitelight/whiteheat", "positivesource", "disco pastors",
    "stereo society", "mintel",
}

# Press / blogs (editorial coverage)
_MEDIA_PRESS_NAMES = {
    "pitchfork", "brooklynvegan", "inverted audio", "ra exchange",
    "underscopefeed", "whypeopledance", "postpunkonline",
    "synth_history", "180 fact", "resident advisor", "resident_advisor",
    "hypecaptureuk", "themuddshow",
}

# Production / education channels (not useful for outreach)
_MEDIA_PRODUCTION_NAMES = {
    "loopop", "alex ball", "production expert", "pensado's place",
    "sound station strategy", "musician paradise", "trackreverse",
    "droid-life interface", "minosaur", "samplesfrommars",
    "productionmusiclive", "sonic academy", "point blank music school",
    "pro audio files", "gearspace forum", "waves audio", "sage audio",
    "music theory", "reverb", "stream_informer", "production music live",
}

# Music curator channels
_MEDIA_CHANNEL_NAMES = {
    "turtle trance", "utopiaspb", "jarre98",
}

# Record shops
_MEDIA_SHOP_NAMES = {
    "phonica records",
}


def _classify_media(name: str, contact: dict) -> str:
    """Detect sub_type for a media contact."""
    nl = name.lower()

    if nl in _MEDIA_RADIO_NAMES:
        return "radio"
    if any(kw in nl for kw in _MEDIA_RADIO_KEYWORDS):
        return "radio"
    if nl in _MEDIA_PREMIERE_NAMES:
        return "premiere"
    if nl in _MEDIA_PRESS_NAMES:
        return "press"
    if nl in _MEDIA_PRODUCTION_NAMES:
        return "production"
    if nl in _MEDIA_SHOP_NAMES:
        return "shop"
    if nl in _MEDIA_CHANNEL_NAMES:
        return "channel"

    # Heuristic: SoundCloud-sourced media are often premiere channels
    src = contact.get("source", "")
    if "soundcloud" in src and "radio" not in nl:
        return "premiere"

    return ""


# ---------------------------------------------------------------------------
# Promoter sub-type detection
# ---------------------------------------------------------------------------

_PROMOTER_EVENT_NAMES = {
    "tortured garden berlin", "shape of us", "the code",
    "anima_berlin", "lunacy_berlin", "dreambabydreambar",
    "blank_with_benefits",
}

_PROMOTER_BOOKING_KEYWORDS = {"booking", "agency"}
_PROMOTER_MGMT_KEYWORDS = {"management", "mgmt"}


def _classify_promoter(name: str, contact: dict) -> str:
    """Detect sub_type for a promoter contact."""
    nl = name.lower()

    if any(kw in nl for kw in _PROMOTER_BOOKING_KEYWORDS):
        return "booking"
    if any(kw in nl for kw in _PROMOTER_MGMT_KEYWORDS):
        return "management"
    if nl in _PROMOTER_EVENT_NAMES:
        return "event"

    return "party"


# ---------------------------------------------------------------------------
# Category fixes
# ---------------------------------------------------------------------------

# name_lower -> new category
_CATEGORY_FIXES = {
    "heartfeltmanagement": "promoter",
    "roof.booking": "promoter",
}

# name_lower -> sub_type override (applied after category fix)
_SUB_TYPE_OVERRIDES = {
    "heartfeltmanagement": "management",
    "roof.booking": "booking",
}

# Contacts to delete
_DELETE_NAMES = {
    "feinstoffberlin",
}


# ---------------------------------------------------------------------------
# Label connections (cross-reference)
# ---------------------------------------------------------------------------

def _compute_label_connections(contacts: list[dict]) -> None:
    """For each DJ, find which labels in our database they release on."""
    # Build index: lowercase label name -> display name
    label_index: dict[str, str] = {}
    for c in contacts:
        if c.get("category") != "label":
            continue
        display = c.get("name", "")
        label_index[display.lower()] = display

    # Match each contact's discogs_labels against our label database
    # Skip labels matching themselves (self-reference)
    for c in contacts:
        dl = c.get("discogs_labels", "")
        if not dl:
            c["label_connections"] = ""
            continue

        own_name = c.get("name", "").lower()
        matched = []
        for part in dl.split(", "):
            key = part.strip().lower()
            if key in label_index and key != own_name:
                display = label_index[key]
                if display not in matched:
                    matched.append(display)

        c["label_connections"] = ", ".join(matched)


# ---------------------------------------------------------------------------
# Relevance score
# ---------------------------------------------------------------------------

def _compute_relevance(contact: dict) -> int:
    """Compute 0-100 relevance score from available signals."""
    score = 0

    # Match score / genre fit (0-30)
    ms = 0
    try:
        ms = int(contact.get("match_score") or 0)
    except (ValueError, TypeError):
        pass
    score += ms * 6

    # Discogs verified (0-10)
    if contact.get("discogs_found"):
        score += 5
        conf = contact.get("discogs_match_confidence", 0)
        try:
            if int(conf) >= 90:
                score += 5
        except (ValueError, TypeError):
            pass

    # Release recency (0-10)
    last_year = contact.get("discogs_last_year", "")
    if last_year:
        try:
            yr = int(last_year)
            if yr >= 2024:
                score += 10
            elif yr >= 2022:
                score += 7
            elif yr >= 2020:
                score += 4
        except ValueError:
            pass

    # Label connections (0-10)
    lc = contact.get("label_connections", "")
    if lc:
        conn_count = len(lc.split(", "))
        score += min(conn_count * 5, 10)

    # Discovery frequency (0-10)
    try:
        df = int(contact.get("discovery_frequency") or 0)
    except (ValueError, TypeError):
        df = 0
    if df >= 5:
        score += 10
    elif df >= 3:
        score += 7
    elif df >= 2:
        score += 4

    # Location bonus (0-5)
    loc = (contact.get("location") or "").lower()
    if "berlin" in loc:
        score += 5
    elif loc:
        score += 2

    # Email available (0-5)
    if contact.get("discogs_email"):
        score += 5

    # YouTube subscribers (0-10)
    try:
        yt_subs = int(contact.get("youtube_subscribers") or 0)
    except (ValueError, TypeError):
        yt_subs = 0
    if yt_subs >= 100000:
        score += 10
    elif yt_subs >= 10000:
        score += 7
    elif yt_subs >= 1000:
        score += 4

    # SoundCloud presence (0-10)
    try:
        sc_followers = int(contact.get("soundcloud_followers") or 0)
    except (ValueError, TypeError):
        sc_followers = 0
    if sc_followers >= 10000:
        score += 10
    elif sc_followers >= 1000:
        score += 7
    elif sc_followers >= 100:
        score += 4
    elif contact.get("soundcloud_user_id"):
        score += 2

    # SoundCloud location match (0-5) -- skip if already in Europe
    sc_city = (contact.get("soundcloud_city") or "").lower()
    loc = (contact.get("location") or "").lower()
    sc_country = (contact.get("soundcloud_country") or "").lower()
    _europe = ("germany", "netherlands", "france", "uk", "spain", "italy",
               "belgium", "austria", "sweden", "denmark", "norway", "finland",
               "portugal", "poland", "czech", "ireland", "switzerland",
               "greece", "hungary", "romania", "croatia", "serbia",
               "de", "nl", "fr", "gb", "es", "it", "be", "at", "se", "dk",
               "no", "fi", "pt", "pl", "cz", "ie", "ch", "gr", "hu", "ro",
               "hr", "rs")
    in_europe = any(e in loc or e in sc_country for e in _europe)
    if in_europe:
        if sc_city and "berlin" in sc_city:
            score += 5
        elif sc_city and any(c in sc_city for c in ("amsterdam", "london", "paris", "hamburg")):
            score += 3

    return min(score, 100)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("\nScene Intelligence -- Sub-Type Classification")
    print("=" * 48)

    if not ENRICHED_FILE.exists():
        print(f"ERROR: {ENRICHED_FILE} not found.")
        sys.exit(1)

    dry_run = "--dry-run" in sys.argv
    reclassify = "--reclassify" in sys.argv

    with open(ENRICHED_FILE, encoding="utf-8") as f:
        contacts = json.load(f)

    print(f"  Loaded {len(contacts)} contacts")
    if dry_run:
        print("  MODE: dry-run (no changes saved)")
    if reclassify:
        print("  MODE: --reclassify (existing sub_types WILL be overwritten)")
    print()

    # --- Step 1: Delete irrelevant contacts ---
    deleted = []
    remaining = []
    for c in contacts:
        if c.get("name", "").lower() in _DELETE_NAMES:
            deleted.append(c.get("name", ""))
        else:
            remaining.append(c)
    contacts = remaining

    if deleted:
        print(f"  Deleted {len(deleted)} contacts: {', '.join(deleted)}")

    # --- Step 2: Category fixes ---
    cat_fixes = 0
    for c in contacts:
        nl = c.get("name", "").lower()
        if nl in _CATEGORY_FIXES:
            old_cat = c.get("category", "")
            new_cat = _CATEGORY_FIXES[nl]
            if old_cat != new_cat:
                print(f"  Category fix: {c['name']} -- {old_cat} -> {new_cat}")
                c["category"] = new_cat
                cat_fixes += 1

    print(f"  Category fixes: {cat_fixes}")

    # --- Step 3: Classify sub_types ---
    sub_counts: dict[str, dict[str, int]] = {}
    classified = 0

    preserved = 0
    for c in contacts:
        cat = c.get("category", "")
        name = c.get("name", "")
        nl = name.lower()

        # GUARD (2026-07-05, audit P2-11): never blank or overwrite an
        # existing sub_type - the unconditional assignment used to wipe
        # all 210 curator sub_types and every manual Type edit on each
        # re-run. Pass --reclassify to overwrite deliberately.
        existing = (c.get("sub_type") or "").strip()
        if existing and not reclassify:
            preserved += 1
            sub = existing
        elif nl in _SUB_TYPE_OVERRIDES:
            sub = _SUB_TYPE_OVERRIDES[nl]
        elif cat == "media":
            sub = _classify_media(name, c)
        elif cat == "promoter":
            sub = _classify_promoter(name, c)
        else:
            sub = ""

        if sub:
            c["sub_type"] = sub

        if sub:
            classified += 1
            key = f"{cat}/{sub}"
            sub_counts.setdefault(key, {"count": 0, "names": []})
            sub_counts[key]["count"] += 1
            sub_counts[key]["names"].append(name)

    print(f"\n  Sub-types classified: {classified} (existing preserved: {preserved})")
    for key in sorted(sub_counts.keys()):
        info = sub_counts[key]
        names_preview = ", ".join(info["names"][:5])
        if len(info["names"]) > 5:
            names_preview += f" +{len(info['names']) - 5} more"
        print(f"    {key:<25} {info['count']:>3}  ({names_preview})")

    # --- Step 4: Label connections ---
    _compute_label_connections(contacts)
    connected = [c for c in contacts if c.get("label_connections")]
    print(f"\n  Label connections: {len(connected)} DJs release on our labels")
    for c in connected[:10]:
        print(f"    {c['name']:<35} -> {c['label_connections'][:50]}")
    if len(connected) > 10:
        print(f"    ... and {len(connected) - 10} more")

    # --- Step 5: Relevance scores ---
    for c in contacts:
        c["relevance_score"] = _compute_relevance(c)

    # Show top 15 by relevance
    by_rel = sorted(contacts, key=lambda c: -c.get("relevance_score", 0))
    print(f"\n  Top 15 by relevance score:")
    for c in by_rel[:15]:
        rs = c.get("relevance_score", 0)
        cat = c.get("category", "")
        sub = c.get("sub_type", "")
        label = f"{cat}/{sub}" if sub else cat
        print(f"    [{rs:>3}] {c['name']:<35} ({label})")

    # --- Save ---
    if dry_run:
        print(f"\n  DRY RUN -- {len(contacts)} contacts, no changes saved.")
        return

    with open(ENRICHED_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

    print(f"\n  Saved {len(contacts)} contacts to enriched_contacts.json")
    print("  Next: python3 scene_intelligence/push_to_sheets.py")
    print()


if __name__ == "__main__":
    main()
