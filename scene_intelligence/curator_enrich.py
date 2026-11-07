"""Enrich manual playlist-curator targets via the Spotify API and upsert them as
category='curator' contacts in enriched_contacts.json.

Pure helpers (extract_contact, playlist_id_from_url, build_curator_contact) are unit
tested. The API calls + file I/O happen in main(), reusing discover_curators.
"""
import re
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
IG_RE = re.compile(r"(?:instagram\.com/|@)([A-Za-z0-9._]{2,30})")


def extract_contact(description, default_paid="groover"):
    """Free contact (IG/email) from a playlist description; else route paid (Groover)."""
    desc = description or ""
    email_m = EMAIL_RE.search(desc)
    email = email_m.group(0) if email_m else ""
    # strip emails first so an email domain is not misread as an IG handle
    ig_m = IG_RE.search(EMAIL_RE.sub(" ", desc))
    # handles may end in '_' (e.g. zaatar___) but never in '.', so strip trailing dots only
    ig = (ig_m.group(1) if ig_m else "").rstrip(".")
    if email or ig:
        return {"ig": ig, "email": email, "route": "free", "submission": ""}
    return {"ig": "", "email": "", "route": "paid", "submission": default_paid}


def playlist_id_from_url(url):
    """Extract the Spotify playlist id from a URL, or '' if none."""
    m = re.search(r"playlist/([A-Za-z0-9]+)", url or "")
    return m.group(1) if m else ""


def build_curator_contact(target, detail, contact, reference_artists):
    """Build a category='curator' contact dict from a staging target + API detail."""
    detail = detail or {}
    owner = detail.get("owner") or {}
    saves = (detail.get("followers") or {}).get("total", 0)
    ref = sorted({a for a in (reference_artists or []) if a})
    return {
        "name": owner.get("display_name") or target.get("curator") or target.get("name", ""),
        "category": "curator",
        "sub_type": "spotify",
        "spotify_id": owner.get("id", ""),
        "spotify_url": (owner.get("external_urls") or {}).get("spotify", ""),
        "curator_playlists": [{
            "name": detail.get("name") or target.get("name", ""),
            "url": target.get("url", ""),
            "id": detail.get("id", ""),
            "saves": saves,
            "fit": target.get("fit", ""),
            "description": detail.get("description", ""),
        }],
        "saves": saves,
        "fit": target.get("fit", ""),
        "contact": contact,
        "source": "manual",
        "confidence": "high",
        "reference_artists": ref,
        "cross_list_count": len(ref),
        "promo_latest_status": "",
        "last_engaged": "",
    }


def _upsert(contacts, row):
    """Add row, or merge its playlist into an existing curator with the same spotify_id."""
    for c in contacts:
        if c.get("category") == "curator" and row.get("spotify_id") and c.get("spotify_id") == row["spotify_id"]:
            urls = {p.get("url") for p in c.get("curator_playlists", [])}
            for p in row["curator_playlists"]:
                if p.get("url") not in urls:
                    c.setdefault("curator_playlists", []).append(p)
            merged = sorted(set(c.get("reference_artists", [])) | set(row["reference_artists"]))
            c["reference_artists"] = merged
            c["cross_list_count"] = len(merged)
            return
    contacts.append(row)


def main():
    ap = argparse.ArgumentParser(description="Enrich manual playlist targets into curator-contacts")
    ap.add_argument("--staging", default="scene_intelligence/playlist_curator_targets.json")
    ap.add_argument("--dry-run", action="store_true", help="Enrich + print, do not write contacts")
    args = ap.parse_args()

    import discover_curators as eng  # scene_intelligence/ is on sys.path (inserted above)

    staging = json.load(open(args.staging, encoding="utf-8"))
    targets = [t for t in staging.get("targets", []) if playlist_id_from_url(t.get("url", ""))]
    print(f"{len(targets)} target(s) with a Spotify URL to enrich "
          f"(this makes {len(targets)} Spotify API calls).")

    contacts = eng._load_contacts()
    free = paid = 0
    rows = []
    for t in targets:
        pid = playlist_id_from_url(t["url"])
        detail = eng.fetch_spotify_playlist_detail(pid)
        if not detail:
            print(f"  [skip] no detail for {t.get('name')!r}")
            continue
        contact = extract_contact(detail.get("description", ""))
        free += contact["route"] == "free"
        paid += contact["route"] == "paid"
        ref = t.get("reference_artists") or staging.get("_meta", {}).get("reference_artists") or []
        rows.append(build_curator_contact(t, detail, contact, ref))
        print(f"  {detail.get('name')!r} | saves {(detail.get('followers') or {}).get('total')} | route {contact['route']}")

    print(f"Free-route: {free} | Paid-route: {paid}")
    if args.dry_run:
        print("DRY RUN - no contacts written.")
        return
    eng._backup_contacts()
    for r in rows:
        _upsert(contacts, r)
    eng._save_contacts(contacts)
    print(f"Wrote {len(rows)} curator-contacts into enriched_contacts.json (backup made).")


if __name__ == "__main__":
    main()
