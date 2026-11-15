"""Live follow-back check of today's engine unfollow candidates (2026-11-15).

Why: the follow-back check combines several HikerAPI follower lists
(ig_reciprocity_from_lists.py). A follow-back from the last few days can only
be in the newest list, and single lists are partial, so a fresh reciprocator
can be marked "not following". The Fable gate (2026-11-15) asked for a fix;
Amir picked "check each one live".

What: on session days, before the 15:00 session, take the unfollow candidates
the engine would pick today (plus a few spares) and search Amir's follower
list for each name (HikerAPI /v1/user/search/followers, 1 call per name,
Instagram never contacted as Amir).
  - found  -> followed_back = True (kept for good, same as a list hit)
  - absent -> precheck_not_follower_at = today
  - error  -> nothing written for that name; it is not cleared today
The engine (cfg.UNFOLLOW_PRECHECK_REQUIRED) only unfollows entries whose
precheck_not_follower_at is today, so a skipped or failed check means no
unfollow, never a wrong one.

  python3 scene_intelligence/ig_unfollow_precheck.py            # dry run, no calls
  python3 scene_intelligence/ig_unfollow_precheck.py --apply
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

SI_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SI_DIR))
TRACKER_FILE = SI_DIR / "ig_follow_tracker.json"
SPARES = 4
OWN = "inch_of_shadow"


def candidates(cfg, tracker: dict, today: date, extra: int = SPARES) -> list[str]:
    """Handles the engine would unfollow today, ignoring the precheck gate,
    with `extra` spares so a found reciprocator does not leave a slot empty."""
    import ig_engagement as E
    personal, keep = E.load_personal_network(cfg)
    promo = E.active_promo_handles(cfg, E.load_release_context(cfg), E.load_promotion_log(cfg),
                                   E.load_enriched_contacts(cfg))
    limits = dict(cfg.PHASE_LIMITS[cfg.CURRENT_PHASE])
    limits["unfollows_per_session"] = int(limits["unfollows_per_session"]) + extra
    old = getattr(cfg, "UNFOLLOW_PRECHECK_REQUIRED", False)
    cfg.UNFOLLOW_PRECHECK_REQUIRED = False  # list what the gate would allow once checked
    try:
        eligible, _rej = E.plan_unfollow_sweep(cfg, tracker, keep, promo, limits, today)
    finally:
        cfg.UNFOLLOW_PRECHECK_REQUIRED = old
    return [e.handle for e in eligible]


def search_result(users, handle: str):
    """True = exact match found, False = a real list without it, None = no
    usable answer (None / not a list): an error, never a clear (Fable 11-15)."""
    if not isinstance(users, list):
        return None
    return any(str(u.get("username", "")).lower() == handle for u in users if isinstance(u, dict))


def pick_control(tracker: dict) -> str | None:
    """A known follower to test the search with, dotted or underscored
    handle first (the likely tokenising miss)."""
    fb = [str(e.get("username", "")).lower() for e in tracker.get("active_follows", [])
          if e.get("followed_back") is True and e.get("username")]
    fb.sort(key=lambda h: (not ("." in h or "_" in h), h))
    return fb[0] if fb else None


def apply_results(tracker: dict, results: dict, today: str) -> dict:
    """results: handle -> True (follows Amir) / False (does not) / None (error)."""
    n = {"follows_back": 0, "not_follower": 0, "error": 0}
    by = {str(e.get("username", "")).lower(): e for e in tracker.get("active_follows", [])}
    for h, res in results.items():
        e = by.get(h)
        if e is None or res is None:
            n["error"] += res is None
            continue
        if res:
            e["followed_back"] = True
            e.setdefault("followed_back_at", today)
            e["followback_verified_at"] = today
            e["followback_discovered_via"] = "provider_follower_search"
            e.pop("precheck_not_follower_at", None)
            n["follows_back"] += 1
        else:
            e["precheck_not_follower_at"] = today
            n["not_follower"] += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description="Live follow-back check of today's unfollow candidates")
    ap.add_argument("--apply", action="store_true", help="make the calls and write (default: dry run)")
    a = ap.parse_args()
    import ig_engagement_config as cfg
    today = date.today()
    tracker = json.loads(TRACKER_FILE.read_text(encoding="utf-8"))
    names = candidates(cfg, tracker, today)
    print(f"[PRECHECK] {len(names)} candidates: {', '.join(names) or '-'}")
    if not names or not a.apply:
        if not a.apply:
            print("[DRY-RUN] no calls, nothing written. Add --apply.")
        return 0
    import ig_daily_ledger as L
    from ig_data_provider import Provider, ProviderError
    control = pick_control(tracker)
    if not control:
        raise SystemExit("[PRECHECK] no known follower to use as control; nothing written (no unfollows today)")
    L.check_and_claim("ig_unfollow_precheck", kind="provider", est_calls=len(names) + 2,
                      endpoint="provider_search_followers")
    p = Provider(sleep=0.3)
    me = p.profile(OWN)
    if not me or not me.get("id"):
        raise SystemExit("[PRECHECK] own profile not returned; nothing written (no unfollows today)")

    def search(h):
        try:
            return search_result(p._get("/v1/user/search/followers", user_id=me["id"], query=h), h)
        except ProviderError as exc:
            print(f"  @{h}: provider error ({str(exc)[:60]})")
            return None

    # Control (Fable 11-15): a known follower must be found, else today's
    # search is not trustworthy and nobody is cleared.
    if search(control) is not True:
        raise SystemExit(f"[PRECHECK] control @{control} (a known follower) not found; "
                         "search not trusted today, nothing written (no unfollows today)")
    print(f"  control @{control}: found, search trusted")
    results: dict = {}
    for h in names:
        res = search(h)
        results[h] = res
        print(f"  @{h}: " + {True: "FOLLOWS YOU (kept)", False: "not a follower",
                              None: "no usable answer, not cleared today"}[res])
    res = apply_results(tracker, results, today.isoformat())
    backup = TRACKER_FILE.with_suffix(f".json.bak.{today:%Y%m%d}_pre_precheck")
    shutil.copy2(TRACKER_FILE, backup)
    fd, tmp = tempfile.mkstemp(dir=str(SI_DIR), prefix=".trk_tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(tracker, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, TRACKER_FILE)
    print(f"[PRECHECK] {res} ({p.calls} calls), backup {backup.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
