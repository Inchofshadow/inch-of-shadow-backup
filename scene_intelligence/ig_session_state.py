"""Pre-flight state summary for the IG session (added 2026-09-18).

Read-only. Exists for the same reason as ig_log_action.py: the session used
to improvise a `cd ... && python3 -c "<inline script>"` one-liner to read
the tracker and queue, which is a different command string every run and so
raised a fresh permission prompt every time. On 2026-09-18 that single call
sat unapproved for 210 minutes and cost the session its afternoon.

One stable command, one allow rule, no prompts:

    python3 scene_intelligence/ig_session_state.py

Prints only what the playbook's STATE READ step needs. Touches no state.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

SI_DIR = Path(__file__).parent


def _load(name: str):
    try:
        return json.loads((SI_DIR / name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _age_days(stamp) -> str:
    if not isinstance(stamp, str):
        return "unknown"
    try:
        d = datetime.fromisoformat(stamp.replace("Z", "+00:00")).date()
    except ValueError:
        return "unknown"
    return f"{(date.today() - d).days}d ago ({d.isoformat()})"


ACTION_DAYS = {0, 2, 4, 5}  # Mon Wed Fri Sat
NIGHT_CUTOFF_HOUR = 22


def gates(now: datetime | None = None) -> int:
    """All HARD STATE GATES in one stable command (added 2026-09-21).

    The playbook's gate 1 (pauses.ig) never had a command, so every run
    improvised a compound `python3 -c ...; python3 -c ...; ...` line, which
    is a new string each time and raised a permission prompt (09-21, before
    the first gate). Exit 0 = gates clear, 3 = a gate blocks (STOP).
    The pre-confirm flag is reported too, but it is not a hard gate.
    """
    from zoneinfo import ZoneInfo
    berlin = ZoneInfo("Europe/Berlin")
    now = now or datetime.now(berlin)
    day = now.date().isoformat()
    blocks: list[str] = []

    print(f"== NOW == {now:%A %Y-%m-%d %H:%M} Berlin")
    if now.weekday() not in ACTION_DAYS:
        blocks.append(f"{now:%A} is not an action day (Mon/Wed/Fri/Sat)")
    if now.hour >= NIGHT_CUTOFF_HOUR:
        blocks.append("past the 22:00 night-clicking cutoff")

    state = _load("autonomy_state.json")
    if state is None:
        blocks.append("autonomy_state.json unreadable (fail closed)")
        pause = "unreadable"
    else:
        pause = (state.get("pauses") or {}).get("ig")
        if pause is not None:
            blocks.append(f"pauses.ig is set: {pause} -- only Amir resumes")
    print(f"== GATE 1 pauses.ig == {pause}")

    try:
        sys.path.insert(0, str(SI_DIR.parent))
        from scene_intelligence.ig_ops_guards import active_detection_cooldown
        cd = active_detection_cooldown(platform="ig", kind="session")
    except Exception as exc:  # fail closed
        cd = f"cooldown check failed: {exc}"
    print(f"== GATE 2 detection cooldown (session) == {cd}")
    if cd is not None:
        blocks.append(f"detection cooldown active: {cd}")

    try:
        from scene_intelligence.ig_daily_ledger import runs_on
        runs = runs_on(day)
    except Exception as exc:
        runs = None
        blocks.append(f"ledger unreadable: {exc} (fail closed)")
    if runs is not None:
        sessions = [r for r in runs if r.get("script") == "ig_session"]
        # 2026-09-26: a claim alone is not a session. The 09-26 run claimed
        # the ledger, then halted at the confirm gate with zero clicks, and
        # this gate refused the real session all afternoon. "Ran" means the
        # day is marked processed, or today's live log holds a click.
        processed = day in ((state or {}).get("processed") or {}).get("ig", [])
        clicks = 0
        live = SI_DIR / f"ig_session_{day}.jsonl"
        if live.exists():
            for ln in live.read_text(encoding="utf-8").splitlines():
                try:
                    a = json.loads(ln).get("action")
                except ValueError:
                    continue
                if a in ("ig_like", "ig_follow", "ig_unfollow"):
                    clicks += 1
        print(f"== GATE 3 ledger == {len(runs)} entries today; "
              f"ig_session claimed: {'yes' if sessions else 'no'}; "
              f"processed: {processed}; clicks in live log: {clicks}")
        if processed or clicks:
            blocks.append("an ig_session already ran today (never two a day)")
        elif sessions:
            print("   note: claim with zero clicks (halted run); a real session may still run")

    try:
        from scene_intelligence.ig_session_confirm import read_flag
        flag = read_flag()
    except Exception:
        flag = None
    try:
        from scene_intelligence.ig_session_confirm import standing as _standing
        st = _standing()
    except Exception:
        st = None
    print(f"== PRE-CONFIRM == "
          + (f"STANDING since {st['since'][:10]}" if st else
             ('confirmed ' + flag['confirmed_at'] if flag else 'none')))

    if blocks:
        print("== VERDICT == STOP")
        for b in blocks:
            print(f"  - {b}")
        return 3
    print("== VERDICT == gates clear")
    return 0


def main() -> int:
    if "--gates" in sys.argv[1:]:
        return gates()
    tracker = _load("ig_follow_tracker.json")
    if tracker is None:
        print("[FAILED] ig_follow_tracker.json unreadable", file=sys.stderr)
        return 1
    stats = tracker.get("stats", {})
    print("== TRACKER ==")
    print(f"  last_session:   {tracker.get('last_session')}")
    print(f"  active_follows: {stats.get('active_follows')}")
    print(f"  total_followed: {stats.get('total_followed')}")
    print(f"  follow_backs:   {stats.get('follow_backs')}")

    targets = _load("ig_target_list.json") or {}
    queue = targets.get("queue") or []
    vetted = sum(1 for c in queue if isinstance(c, dict)
                 and c.get("status") == "pending" and c.get("audit_date"))
    unvetted = sum(1 for c in queue if isinstance(c, dict)
                   and c.get("status") == "pending" and not c.get("audit_date"))
    meta = targets.get("_meta") or {}
    print("== QUEUE ==")
    # 2026-09-28: the raw count (pending + audited) overstated supply and
    # disagreed with the loop-closer in the 09-28 report (16 vs 0). Lead with
    # what the engine can actually follow.
    try:
        sys.path.insert(0, str(SI_DIR.parent))
        from scene_intelligence.ig_engagement import followable_pool_size
        followable = followable_pool_size()
    except Exception:
        followable = None
    if followable is not None:
        print(f"  followable pool:  {followable}   (what the plan can follow; warn at <= 30)")
        print(f"  audited pending:  {vetted}   (raw; includes names the engine rejects)")
        vetted = followable
    else:
        print(f"  vetted pending:   {vetted}   (raw count; followable check unavailable)")
    print(f"  unvetted pending: {unvetted}")
    print(f"  last builder run: {_age_days(meta.get('last_builder_run'))}")
    if vetted <= 30:
        print("  [!] POOL LOW -- a queue refresh is due")

    promo = _load("promotion_log.json") or {}
    campaigns = promo.get("campaigns") if isinstance(promo, dict) else None
    if isinstance(campaigns, list):
        live = [c.get("slug") or c.get("name") for c in campaigns
                if isinstance(c, dict) and c.get("status") == "active"]
        print("== PROMO ==")
        print(f"  active campaigns: {', '.join(str(x) for x in live) or 'none'}")

    release = _load("release_context.json") or {}
    if release:
        print("== RELEASE ==")
        print(f"  active: {release.get('active_release') or release.get('slug') or 'none'}")

    print("== NOTE ==")
    print("  volumes come from the plan file, never from this summary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
