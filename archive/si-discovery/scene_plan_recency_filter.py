"""
Scene plan recency filter
--------------------------
Recency-checks the Scene candidates in a session_plan_<date>.json and DROPS the
stale ones (most-recent post older than the like window) so the Cowork session
does not circuit-break on year-old accounts.

Why this exists (2026-06-26): the engine plan draws Scene targets from
enriched_contacts.json, which has NO live last-post data -- so it serves
dormant accounts. On 2026-06-26 five stale candidates in a row tripped the
Class B circuit breaker and the Scene track halted at 2/20 likes. This tool
checks each planned Scene candidate's real recency (via the same IG endpoints
the queue audit uses) and rewrites the plan to fresh-only.

Cost: ~2 IG calls per Scene candidate (web_profile_info -> user_id, then
feed/user -> post dates; IG stripped timestamps from web_profile_info on
2026-06-03). A 19-candidate plan = ~38 calls. Pre-announce + run on the
session-prep step, ideally the night before (pre-stage), to avoid stacking
heavy reads on the action-session day.

Usage:
  python3 scene_intelligence/scene_plan_recency_filter.py 2026-06-27
  python3 scene_intelligence/scene_plan_recency_filter.py 2026-06-27 --dry-run
  python3 scene_intelligence/scene_plan_recency_filter.py 2026-06-27 --max-age 90
"""
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import date, datetime, timezone

SI_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SI_DIR))
import ig_audit_queue_freshness as A  # reuse the proven session + fetch path


def _newest_post_age_days(session, username: str, session_date: date):
    """Return (age_days, verdict). verdict in fresh/stale/private/no_recency/fetch_fail."""
    prof = A._fetch_profile(session, username)
    if not prof:
        return None, "fetch_fail"
    user = A._walk_for_user(prof) or {}
    if user.get("is_private"):
        return None, "private"
    uid = user.get("id") or user.get("pk")
    if not uid:
        return None, "no_recency"
    feed = A._fetch_user_feed(session, str(uid), count=3)
    if not feed:
        return None, "no_recency"
    taken = [it.get("taken_at") or it.get("taken_at_timestamp")
             for it in feed if isinstance(it, dict)]
    taken = [t for t in taken if isinstance(t, (int, float))]
    if not taken:
        return None, "no_recency"
    newest = datetime.fromtimestamp(max(taken), tz=timezone.utc).date()
    return (session_date - newest).days, "ok"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("plan_date", help="session_plan_<DATE>.json to filter (YYYY-MM-DD)")
    p.add_argument("--max-age", type=int, default=90, help="Scene like window in days (default 90)")
    p.add_argument("--dry-run", action="store_true", help="report only, do not rewrite the plan")
    args = p.parse_args()

    plan_path = SI_DIR / f"session_plan_{args.plan_date}.json"
    if not plan_path.exists():
        print(f"[ERROR] {plan_path.name} not found. Run --plan-only first.", file=sys.stderr)
        return 1
    d = json.loads(plan_path.read_text(encoding="utf-8"))
    handles = [x["handle"] for x in d.get("scene_likes", [])]
    if not handles:
        print("[INFO] No scene_likes in plan; nothing to check.")
        return 0

    session_date = date.fromisoformat(args.plan_date)
    sid, csrf = A._load_credentials()
    session = A._build_session(sid, csrf)

    print(f"Recency-checking {len(handles)} Scene candidates "
          f"(~{len(handles) * 2} IG calls max), window <= {args.max_age}d ...")
    keep, results, calls = [], [], 0
    for h in handles:
        age, verdict = _newest_post_age_days(session, h, session_date)
        calls += 1 if verdict in ("fetch_fail", "private") else 2
        if verdict == "ok":
            fresh = age <= args.max_age
            results.append((h, "fresh" if fresh else "stale", age))
            if fresh:
                keep.append(h)
        else:
            # unknown recency: keep (not proven stale), but flag
            results.append((h, verdict, None))
            if verdict == "no_recency":
                keep.append(h)
        time.sleep(1.5)

    for h, v, a in results:
        print(f"  {v:11} age={a} @{h}")
    dropped = [h for h, v, a in results if h not in keep]
    print(f"\nIG calls used: ~{calls}")
    print(f"FRESH/kept: {len(keep)} / {len(handles)} | dropped: {dropped or 'none'}")

    if args.dry_run:
        print("[DRY-RUN] plan not modified.")
        return 0
    d["scene_likes"] = [x for x in d["scene_likes"] if x["handle"] in keep]
    note = d.setdefault("_meta", {}).get("note", "")
    d["_meta"]["note"] = (note + f" | scene recency-filtered: kept <= {args.max_age}d").strip(" |")
    plan_path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[OK] Rewrote {plan_path.name}: {len(d['scene_likes'])} fresh Scene targets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
