"""Extract a free/paid contact route for discovery-sourced curators.

discover_curators.py adds curators with playlist URLs but no contact route.
This pass re-fetches each curator's top playlist description from Spotify
(read-only) and runs extract_contact() to pull an IG handle / email, then
attaches a `contact` dict + `route` onto the contact (enrichment only, never
deletes). Backs up first.

Usage:
  python3 scene_intelligence/curator_extract_routes.py --names-file <json list of top_playlist_url>
  python3 scene_intelligence/curator_extract_routes.py --all-discovery   # every curator_discovery contact missing a route
  python3 scene_intelligence/curator_extract_routes.py --all-discovery --dry-run
"""
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import discover_curators as eng
from curator_enrich import extract_contact, playlist_id_from_url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--urls-file", help="JSON file: list of top_playlist_url to limit to")
    ap.add_argument("--all-discovery", action="store_true",
                    help="Process every curator_discovery contact that lacks a contact route")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    limit_urls = None
    if args.urls_file:
        limit_urls = set(json.load(open(args.urls_file, encoding="utf-8")))

    contacts = eng._load_contacts()
    targets = []
    for c in contacts:
        if c.get("source") != "curator_discovery":
            continue
        if c.get("contact"):  # already has a route
            continue
        url = c.get("top_playlist_url", "")
        if limit_urls is not None and url not in limit_urls:
            continue
        if playlist_id_from_url(url):
            targets.append(c)

    print(f"{len(targets)} curator(s) to route-extract (= {len(targets)} Spotify API calls).")

    free = paid = 0
    for c in targets:
        pid = playlist_id_from_url(c["top_playlist_url"])
        detail = eng.fetch_spotify_playlist_detail(pid)
        if not detail:
            print(f"  [skip] no detail for {c.get('top_playlist_name')!r}")
            continue
        desc = detail.get("description", "") or ""
        route = extract_contact(desc)
        c["contact"] = route
        c["top_playlist_description"] = desc
        free += route["route"] == "free"
        paid += route["route"] == "paid"
        tag = route["ig"] or route["email"] or route["submission"]
        print(f"  [{route['route']:<4}] {c.get('top_playlist_name','')[:46]:<46} -> {tag}")

    print(f"\nFree-route: {free} | Paid-route: {paid}")
    if args.dry_run:
        print("DRY RUN - no contacts written.")
        return
    eng._backup_contacts()
    eng._save_contacts(contacts)
    print(f"Updated {len(targets)} curator contacts with a route (backup made).")


if __name__ == "__main__":
    main()
