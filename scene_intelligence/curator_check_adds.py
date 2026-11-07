"""Auto-detect playlist adds: for each pitched curator, check via the Spotify API
whether the release's track is now on their playlist, and mark them 'added'.

Pure helpers are unit-tested; the API + I/O run in main(), reusing discover_curators'
Spotify auth. Read-only.
"""
import re
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def track_id_from_url(url):
    """Extract the Spotify track id from a URL, or '' if none."""
    m = re.search(r"track/([A-Za-z0-9]+)", url or "")
    return m.group(1) if m else ""


def track_in_playlist(track_id, playlist_track_ids):
    """True if the track id is present among a playlist's track ids."""
    return bool(track_id) and track_id in set(playlist_track_ids)


def fetch_playlist_track_ids(playlist_id, eng, max_pages=4):
    """Return the track ids on a playlist (paginated, capped). Reuses engine auth."""
    ids = []
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    params = {"fields": "items(track(id)),next", "limit": 100}
    calls = 0
    while url and calls < max_pages:
        data = eng._spotify_get(url, params=params)
        calls += 1
        if not data:
            break
        for it in data.get("items", []):
            t = (it or {}).get("track") or {}
            if t.get("id"):
                ids.append(t["id"])
        url = data.get("next")
        params = None  # next is a full URL
    return ids, calls


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description="Mark curators who added the release track")
    ap.add_argument("slug", help="Release slug (matches releases/<slug>.json)")
    ap.add_argument("--base-dir", default=".")
    ap.add_argument("--dry-run", action="store_true", help="Report would-be adds, do not write")
    args = ap.parse_args()

    import discover_curators as eng  # scene_intelligence/ is on sys.path

    release = _load(f"{args.base_dir}/releases/{args.slug}.json")
    track_id = track_id_from_url((release.get("platform_links") or {}).get("spotify", ""))
    if not track_id:
        raise SystemExit("No Spotify track URL in the release JSON - cannot check adds.")

    contacts_path = f"{args.base_dir}/scene_intelligence/enriched_contacts.json"
    contacts = _load(contacts_path)
    pitched = [c for c in contacts if isinstance(c, dict) and c.get("category") == "curator"
               and c.get("promo_latest_status") in ("sent", "pitched")]
    n_pl = sum(len(c.get("curator_playlists", [])) for c in pitched)
    print(f"{len(pitched)} pitched curator(s), {n_pl} playlist(s) to check "
          f"(about {n_pl} to {n_pl * 4} Spotify API calls).")

    total_calls = 0
    added = []
    for c in pitched:
        hit = False
        for p in c.get("curator_playlists", []):
            if not p.get("id"):
                continue
            ids, calls = fetch_playlist_track_ids(p["id"], eng)
            total_calls += calls
            if track_in_playlist(track_id, ids):
                hit = True
                break
        if hit:
            added.append(c.get("name"))
            if not args.dry_run:
                c["promo_latest_status"] = "added"

    print(f"Made {total_calls} API calls. Added: {added or 'none'}")
    if added and not args.dry_run:
        with open(contacts_path, "w", encoding="utf-8") as f:
            json.dump(contacts, f, ensure_ascii=False, indent=2)
        print("Marked the above curators as 'added' in enriched_contacts.json.")


if __name__ == "__main__":
    main()
