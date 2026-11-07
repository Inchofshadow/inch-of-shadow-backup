"""
sc_buy_links.py
---------------
Ticket BC-02. Point the SoundCloud "buy" link of each of Amir's own tracks
and sets at the matching Bandcamp page, with a ?campaign=sc-buy link
(bandcamp_links.py, BC-07).

Steps (each one separate, nothing is changed before Amir's go):
  record  read the current buy links of his own tracks/sets and save a
          snapshot (record-before-changing rule).
  plan    build the change list old -> new from the latest snapshot.
          Tracks without a Bandcamp page on HIS account go on a REVIEW
          list and keep their current link.

Usage:
  python3 scene_intelligence/sc_buy_links.py record   # ~3 read-only SC calls
  python3 scene_intelligence/sc_buy_links.py plan     # local only
  python3 scene_intelligence/sc_buy_links.py apply --plan-file data/soundcloud/<plan>.json  # after his go

Reads use SC_BROWSER_TOKEN through sc_weekly_health's guarded GET
(budget cap, captcha/429 abort). It never touches .sc_user_token.json,
which the SC engagement sessions own.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scene_intelligence"))

import bandcamp_links as bl  # noqa: E402

OUT_DIR = BASE_DIR / "data" / "soundcloud"
CHANNEL = "sc-buy"
MIX_CHANNEL = "sc-mix"  # DJ sets/mixes whose tracklist holds one of our releases
OWN_CREDIT = re.compile(r"inch of shadow", re.I)

# SC title words -> Bandcamp catalog key (bandcamp_links.CATALOG). Album
# tracks point at the album page: their own track pages were not checked.
TITLE_RULES: list[tuple[str, str]] = [
    (r"\bdeceiver\b", "the-deceiver"),
    (r"\bfarewell\b", "farewell"),
    (r"\btour\b.*\bremix\b|\bremix\b.*\btour\b", "the-tour-remix"),
    (r"\bmeltscape\b", "meltscape"),
    (r"\bthe cure\b", "meltscape"),
    (r"\beastern stars\b", "eastern-stars"),
]


def bandcamp_key_for(title: str) -> str:
    low = (title or "").lower()
    for pattern, key in TITLE_RULES:
        if re.search(pattern, low):
            return key
    return ""


def slim(item: dict, kind: str) -> dict:
    return {
        "kind": kind,
        "id": item.get("id"),
        "title": item.get("title", ""),
        "permalink_url": item.get("permalink_url", ""),
        "sharing": item.get("sharing", ""),
        "purchase_url": item.get("purchase_url") or "",
        "purchase_title": item.get("purchase_title") or "",
        "downloadable": item.get("downloadable"),
        "description": item.get("description") or "",
    }


def record() -> Path:
    import sc_weekly_health as h  # guarded GET with budget cap
    if not h.TOKEN:
        raise SystemExit("SC_BROWSER_TOKEN missing in .env")
    tracks = h._paginate(f"{h.API_BASE}/users/{h.USER_ID}/tracks")
    sets = h._paginate(f"{h.API_BASE}/users/{h.USER_ID}/playlists_without_albums") + \
        h._paginate(f"{h.API_BASE}/users/{h.USER_ID}/albums")
    snap = {
        "recorded_at": datetime.now().isoformat(timespec="seconds"),
        "ticket": "BC-02",
        "api_calls": h._api_calls,
        "items": [slim(t, "track") for t in tracks] + [slim(s, "set") for s in sets],
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"buy-links-before-{datetime.now():%Y%m%d_%H%M%S}.json"
    path.write_text(json.dumps(snap, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def latest_snapshot() -> Path | None:
    snaps = sorted(OUT_DIR.glob("buy-links-before-*.json"))
    return snaps[-1] if snaps else None


def tracklist_key(description: str) -> tuple[str, str]:
    """Newest own release named in a mix tracklist -> (catalog key, matched line).

    Only lines that also carry our own credit count, so a tracklist line like
    'The Cure - A Forest' never maps to the Meltscape track 'The Cure'.
    """
    found: dict[str, str] = {}
    for line in (description or "").splitlines():
        if not OWN_CREDIT.search(line):
            continue
        key = bandcamp_key_for(line)
        if key and key not in found:
            found[key] = line.strip()
    for key in bl.CATALOG:  # CATALOG is newest first
        if key in found:
            return key, found[key]
    return "", ""


def build_plan(items: list[dict]) -> dict:
    change, same, review = [], [], []
    for it in items:
        key, channel, via = bandcamp_key_for(it["title"]), CHANNEL, "title"
        if not key:
            key, line = tracklist_key(it.get("description", ""))
            channel, via = MIX_CHANNEL, f"tracklist: {line}"
        if not key:
            review.append({**it, "reason": "no own Bandcamp release in title or tracklist"})
            continue
        new = bl.campaign_url(bl.CATALOG[key], channel)
        row = {**it, "bandcamp_key": key, "matched_by": via, "new_purchase_url": new,
               "new_purchase_title": it["purchase_title"] or ""}
        (same if it["purchase_url"] == new else change).append(row)
    return {"change": change, "unchanged": same, "review": review}


def plan() -> Path:
    snap_path = latest_snapshot()
    if not snap_path:
        raise SystemExit("No snapshot yet: run 'record' first.")
    snap = json.loads(snap_path.read_text(encoding="utf-8"))
    result = build_plan(snap["items"])
    result.update({"snapshot": snap_path.name, "planned_at": datetime.now().isoformat(timespec="seconds"),
                   "status": "waiting for Amir's go"})
    out = OUT_DIR / f"buy-links-plan-{datetime.now():%Y%m%d_%H%M%S}.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    for name in ("change", "unchanged", "review"):
        print(f"\n{name.upper()} ({len(result[name])})")
        for r in result[name]:
            old = r["purchase_url"] or "(none)"
            new = r.get("new_purchase_url", "keep")
            print(f"  [{r['kind']}] {r['title'][:50]:<50} {old}  ->  {new}")
    return out


BUTTON_TEXT = "Buy on Bandcamp"
# Counters and caches that move on their own between two reads.
VOLATILE = {"last_modified", "playback_count", "likes_count", "reposts_count", "comment_count",
            "download_count", "media", "station_urn", "station_permalink", "tracks", "track_count",
            "track_authorization"}


def changed_fields(before: dict, after: dict) -> dict:
    return {k: (before.get(k), after.get(k)) for k in set(before) | set(after)
            if k not in VOLATILE and before.get(k) != after.get(k)}


def apply(plan_path: Path) -> list[dict]:
    """Write buy link + button text for every 'change' row, one by one.

    Each item is read in full before and after; anything other than
    purchase_url / purchase_title changing stops the run.
    """
    import requests
    import sc_weekly_health as h
    plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
    results = []
    for row in plan_data["change"]:
        kind = "tracks" if row["kind"] == "track" else "playlists"
        field = "track" if row["kind"] == "track" else "playlist"
        url_v2 = f"{h.API_BASE}/{kind}/{row['id']}"
        before = h._api_get(url_v2)
        want = {"purchase_url": row["new_purchase_url"], "purchase_title": BUTTON_TEXT}
        if all(before.get(k) == v for k, v in want.items()):
            results.append({"title": row["title"], "status": "already set"})
            continue
        resp = requests.put(f"https://api.soundcloud.com/{kind}/{row['id']}",
                            headers={"Authorization": f"OAuth {h.TOKEN}", "Accept": "application/json"},
                            data={f"{field}[{k}]": v for k, v in want.items()}, timeout=20)
        h._api_calls += 1
        if resp.status_code != 200:
            raise SystemExit(f"PUT {row['title']!r} failed: HTTP {resp.status_code}. Stopped.")
        after = h._api_get(url_v2)
        diff = changed_fields(before, after)
        extra = set(diff) - set(want)
        ok = all(after.get(k) == v for k, v in want.items())
        results.append({"title": row["title"], "status": "ok" if ok and not extra else "CHECK",
                        "changed": sorted(diff), "unexpected": sorted(extra)})
        if extra or not ok:
            raise SystemExit(f"Unexpected result on {row['title']!r}: {diff}. Stopped.")
    log = OUT_DIR / f"buy-links-applied-{datetime.now():%Y%m%d_%H%M%S}.json"
    log.write_text(json.dumps({"plan": plan_path.name, "api_calls": h._api_calls, "results": results},
                              indent=2, ensure_ascii=False), encoding="utf-8")
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="SC buy links to Bandcamp (BC-02).")
    ap.add_argument("step", choices=["record", "plan", "apply"])
    ap.add_argument("--plan-file", type=Path, help="apply: plan JSON (Amir-approved)")
    args = ap.parse_args(argv)
    if args.step == "record":
        print(f"Saved {record().relative_to(BASE_DIR)}")
    elif args.step == "plan":
        print(f"\nSaved {plan().relative_to(BASE_DIR)}")
    else:
        if not args.plan_file:
            raise SystemExit("apply needs --plan-file <the plan Amir approved>")
        for r in apply(args.plan_file):
            print(f"  {r['status']:<11} {r['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
