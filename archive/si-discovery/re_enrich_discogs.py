"""
scene_intelligence/re_enrich_discogs.py
-----------------------------------------
Re-run Discogs enrichment for contacts that weren't found on the first pass.

Improvements over the initial enrichment:
  - Name cleanup (strip underscores, dots, common suffixes)
  - Known name mappings (Instagram handle -> real artist/label name)
  - Tries both cleaned name and original name
  - Only processes unfound contacts (skips already-enriched ones)

Usage:
  python3 scene_intelligence/re_enrich_discogs.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from utils import CATEGORY_DEFAULT_SCORE

# ---------------------------------------------------------------------------
# Paths and config
# ---------------------------------------------------------------------------
BASE_DIR    = Path(__file__).parent.parent
DATA_FILE   = BASE_DIR / "scene_intelligence" / "enriched_contacts.json"

load_dotenv(BASE_DIR / ".env")
DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN", "")

DISCOGS_SEARCH = "https://api.discogs.com/database/search"
DISCOGS_ARTIST = "https://api.discogs.com/artists/{id}"
DISCOGS_LABEL  = "https://api.discogs.com/labels/{id}"

REQUEST_DELAY = 1.0
TIMEOUT       = 10

# ---------------------------------------------------------------------------
# Known name mappings: Instagram handle -> Discogs search name
# ---------------------------------------------------------------------------
KNOWN_NAMES: dict[str, str] = {
    # DJs / Artists
    "ninakraviz":              "Nina Kraviz",
    "positivesource":          "Positive Source",
    "discopastors":            "Disco Pastors",
    "orpheuthewizard":         "Orpheu The Wizard",
    "bonnie_spacey":           "Bonnie Spacey",
    "monsieur_sukram":         "Monsieur Sukram",
    "freudenthal_of_pardonmoi": "Freudenthal",
    "cbas_lab":                "CBAS",
    "sano_musik":              "Sano",
    "mehrismehr_music":        "Mehr Ist Mehr",
    "zantaella.music":         "Zantaella",
    "acid.tears.303":          "Acid Tears",
    "tigerweeds_ath":          "Tigerweeds",
    "matthias.superluminal":   "Superluminal",
    "s.loth030":               "S.Loth",
    "spasm.music":             "Spasm",
    "r.missing":               "R.Missing",
    "discoverberlin_":         "Discover Berlin",
    "fliko":                   "Fliko",
    "Coldwaveyears":           "Cold Wave Years",
    "Andrei Martinez Agras":   "Andrei Martinez Agras",
    "fabriziomammarella":      "Fabrizio Mammarella",
    "franzscala":              "Franz Scala",
    "krisbaha":                "Kris Baha",
    "identified_patient":      "Identified Patient",
    "adriani.alessandro":      "Alessandro Adriani",
    "tunik303":                "Tunik",
    "_alice_glass":            "Alice Glass",
    "djkatah":                 "DJ Katah",
    "thisisdjkitty":           "DJ Kitty",
    "foggggggy_":              "Foggy",
    "t___o___r___a___i":       "Torai",
    "unikat0.2":               "Unikat",
    # Labels
    "melopeerecords":          "Melopee Records",
    "slowmotion_records":      "Slow Motion Records",
    "subaqueousmusic":         "Subaqueous",
    "deepteKk":                "DeepTekk",
    "303lush":                 "303 Lush",
    "epicurerecords":          "Epicure Records",
    "king80industries":        "King 80 Industries",
    "_aterral":                "Aterral",
    "stereosocietyofficial":   "Stereo Society",
}


# ---------------------------------------------------------------------------
# HTTP helpers (same as enrich_contacts.py)
# ---------------------------------------------------------------------------

def _headers() -> dict:
    h = {"User-Agent": "InchOfShadowSceneIntelligence/1.0"}
    if DISCOGS_TOKEN:
        h["Authorization"] = f"Discogs token={DISCOGS_TOKEN}"
    return h


def _get(url: str, params: dict | None = None) -> dict | None:
    try:
        r = requests.get(url, params=params, headers=_headers(), timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            print("  [rate limit] waiting 15s...", flush=True)
            time.sleep(15)
        return None
    except requests.RequestException:
        return None


def _extract_email(text: str) -> str:
    matches = re.findall(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}', text or "")
    return matches[0] if matches else ""


# ---------------------------------------------------------------------------
# Name cleanup
# ---------------------------------------------------------------------------

def clean_name(name: str) -> str:
    """Clean Instagram-style name for Discogs search."""
    n = name.strip("_. ")
    for suffix in ("_official", "_music", "_records", "_dj", "_berlin", "_sf"):
        if n.lower().endswith(suffix):
            n = n[:len(n) - len(suffix)]
    n = re.sub(r"[_\.]+", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


# ---------------------------------------------------------------------------
# Discogs lookups (from enrich_contacts.py)
# ---------------------------------------------------------------------------

import difflib

def search_and_enrich(name: str, search_name: str, category: str) -> dict | None:
    """Search Discogs and return enrichment data if found with decent confidence."""
    search_type = "label" if category == "label" else "artist"

    data = _get(DISCOGS_SEARCH, params={"q": search_name, "type": search_type, "per_page": 3})
    time.sleep(REQUEST_DELAY)
    if not data or not data.get("results"):
        return None

    result = data["results"][0]
    entity_id = result.get("id")
    if not entity_id:
        return None

    # Match confidence
    matched_name = result.get("title", "")
    name_norm = re.sub(r'[^a-z0-9]', '', name.lower())
    matched_norm = re.sub(r'[^a-z0-9]', '', matched_name.lower())
    search_norm = re.sub(r'[^a-z0-9]', '', search_name.lower())

    # Check confidence against both original and search name
    conf_orig = round(difflib.SequenceMatcher(None, name_norm, matched_norm).ratio() * 100)
    conf_search = round(difflib.SequenceMatcher(None, search_norm, matched_norm).ratio() * 100)
    confidence = max(conf_orig, conf_search)

    # Skip low confidence matches
    if confidence < 50:
        return None

    # Get detail
    if category == "label":
        detail = _get(DISCOGS_LABEL.format(id=entity_id))
    else:
        detail = _get(DISCOGS_ARTIST.format(id=entity_id))
    time.sleep(REQUEST_DELAY)

    if not detail:
        return None

    genres = ", ".join(result.get("genre", []) or [])
    url = detail.get("uri", "")
    urls = detail.get("urls", [])
    website = urls[0] if urls else ""

    enrichment = {
        "discogs_url":       url,
        "discogs_genres":    genres,
        "discogs_found":     True,
        "discogs_match_confidence": confidence,
        "discogs_website":   website,
    }

    # Label-specific fields
    if category == "label":
        enrichment["discogs_country"] = detail.get("country", "")
        contact_info = detail.get("contact_info", "")
        profile = detail.get("profile", "")
        enrichment["discogs_email"] = _extract_email(contact_info) or _extract_email(profile)

        releases_url = detail.get("releases_url", "")
        if releases_url:
            rel_data = _get(releases_url, params={"per_page": 1, "sort": "year", "sort_order": "desc"})
            time.sleep(REQUEST_DELAY)
            if rel_data:
                enrichment["discogs_releases"] = str(rel_data.get("pagination", {}).get("items", ""))
                releases = rel_data.get("releases", [])
                if releases:
                    enrichment["discogs_last_year"] = str(releases[0].get("year", ""))

    # DJ-specific fields
    else:
        releases_url = detail.get("releases_url", "")
        labels_found: list[str] = []
        if releases_url:
            rel_data = _get(releases_url, params={"per_page": 5, "sort": "year", "sort_order": "desc"})
            time.sleep(REQUEST_DELAY)
            if rel_data:
                enrichment["discogs_releases"] = str(rel_data.get("pagination", {}).get("items", ""))
                for rel in rel_data.get("releases", [])[:5]:
                    lbl = rel.get("label", "")
                    if lbl and lbl not in labels_found:
                        labels_found.append(lbl)
                    if "discogs_last_year" not in enrichment:
                        yr = rel.get("year", "")
                        if yr:
                            enrichment["discogs_last_year"] = str(yr)
        enrichment["discogs_labels"] = ", ".join(labels_found)

    return enrichment


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("\nScene Intelligence — Discogs Re-Enrichment")
    print("=" * 46)

    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found.")
        sys.exit(1)

    with open(DATA_FILE, encoding="utf-8") as f:
        contacts = json.load(f)

    # Find unfound contacts in enrichable categories
    targets = [
        c for c in contacts
        if c.get("category") in ("label", "dj")
        and not c.get("discogs_found")
    ]

    if DISCOGS_TOKEN:
        print(f"  Discogs token: set  (60 req/min)")
    else:
        print(f"  Discogs token: not set  (25 req/min)")

    print(f"  Contacts to retry: {len(targets)}")
    est_min = (len(targets) * 4 * REQUEST_DELAY) / 60
    print(f"  Estimated time:    ~{est_min:.0f} minutes")
    print()

    found = 0
    skipped = 0

    for i, contact in enumerate(targets):
        name = contact["name"]
        cat = contact["category"]

        # Determine search name
        known = KNOWN_NAMES.get(name)
        cleaned = clean_name(name)
        search_names = []
        if known:
            search_names.append(known)
        if cleaned.lower() != name.lower():
            search_names.append(cleaned)
        if not search_names:
            search_names.append(name)

        print(f"  [{i+1:>4}/{len(targets)}] {cat:<6}  {name[:30]:<30}", end="  ", flush=True)

        result = None
        used_name = ""
        for sn in search_names:
            result = search_and_enrich(name, sn, cat)
            if result:
                used_name = sn
                break

        if not result and name not in [sn for sn in search_names]:
            # Try original name as last resort
            result = search_and_enrich(name, name, cat)
            if result:
                used_name = name

        if result:
            found += 1
            contact.update(result)

            # Verification status
            pct = result.get("discogs_match_confidence", "")
            contact["verification_status"] = f"V {pct}%" if pct != "" else "V"

            # Update genre from Discogs if we had none
            if result.get("discogs_genres") and not contact.get("genre_main"):
                genres = result["discogs_genres"].split(", ")
                contact["genre_main"] = genres[0] if genres else ""
                if len(genres) > 1:
                    contact["genre_sub"] = ", ".join(genres[1:])

            # Update location from Discogs country
            if result.get("discogs_country") and not contact.get("location"):
                contact["location"] = result["discogs_country"]

            parts = []
            if used_name != name:
                parts.append(f"as '{used_name}'")
            conf = result.get("discogs_match_confidence", "")
            parts.append(f"{conf}%")
            if result.get("discogs_genres"):
                parts.append(result["discogs_genres"][:25])
            if result.get("discogs_email"):
                parts.append("EMAIL")
            print("FOUND  " + "  |  ".join(parts))
        else:
            skipped += 1
            print("--")

    # Save
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 46)
    print(f"  New matches: {found}")
    print(f"  Still unfound: {skipped}")
    print(f"  Saved to: {DATA_FILE.name}")
    print()


if __name__ == "__main__":
    main()
