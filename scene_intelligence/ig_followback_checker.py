"""
scene_intelligence/ig_followback_checker.py
---------------------------------------------
Daily follow-back checker for the Inch of Shadow IG automation stack.

What it does:
    1. Reads ig_follow_tracker.json active_follows list.
    2. For each followed account, calls GET /api/v1/friendships/show/{their_user_id}/
       and checks the `followed_by` field (True = they follow back).
    3. Updates entries:
          followed_back: true
          followed_back_at: "YYYY-MM-DD"
    4. Saves updated ig_follow_tracker.json; stats.follow_backs is recomputed
       as a snapshot of active reciprocators (see ig_tracker_stats.py).
    5. Prints a clean daily summary report.

Also enforces unfollow schedule:
    - Marks accounts that are past unfollow_after date as 'due_for_unfollow'
      (does NOT unfollow — that is the engine's job on next session run).

Run:
    python3 scene_intelligence/ig_followback_checker.py

Or with verbose output:
    python3 scene_intelligence/ig_followback_checker.py --verbose

Or just print the report without making any API calls:
    python3 scene_intelligence/ig_followback_checker.py --report-only

Credentials:
    Reads IG_SESSION_ID, IG_CSRF_TOKEN from .env (same as ig_live_driver.py).
    No IG_USER_ID needed for friendships/show calls.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import random
from datetime import datetime, date
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env"
SI_DIR = BASE_DIR / "scene_intelligence"

try:
    from scene_intelligence import ig_engagement_config as cfg  # type: ignore
    TRACKER_FILE = BASE_DIR / cfg.FOLLOW_TRACKER_FILE
    PAID_FILE = BASE_DIR / cfg.PAID_AUDIENCE_FILE
except (ImportError, AttributeError):
    TRACKER_FILE = SI_DIR / "ig_follow_tracker.json"
    PAID_FILE = SI_DIR / "ig_paid_audience_seed.json"

# ---------------------------------------------------------------------------
# Instagram API constants — mirrors ig_live_driver.py
# ---------------------------------------------------------------------------

IG_APP_ID = "936619743392459"
IG_API_BASE = "https://www.instagram.com/api/v1"
IG_WEB = "https://www.instagram.com"

_BASE_HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "X-IG-App-ID": IG_APP_ID,
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "*/*",
    "Origin": "https://www.instagram.com",
}

# ---------------------------------------------------------------------------
# Session builder
# ---------------------------------------------------------------------------

def _build_requests_session(session_id: str, csrf_token: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({**_BASE_HEADERS, "X-CSRFToken": csrf_token})
    s.cookies.set("sessionid", session_id, domain=".instagram.com")
    s.cookies.set("csrftoken", csrf_token, domain=".instagram.com")
    return s


def _load_credentials() -> tuple[str, str]:
    """Load IG_SESSION_ID and IG_CSRF_TOKEN from .env. Exits on failure."""
    load_dotenv(ENV_FILE)
    sid = os.getenv("IG_SESSION_ID", "").strip()
    csrf = os.getenv("IG_CSRF_TOKEN", "").strip()

    missing = []
    if not sid:
        missing.append("IG_SESSION_ID")
    if not csrf:
        missing.append("IG_CSRF_TOKEN")

    if missing:
        raise SystemExit(
            f"\n[FOLLOWBACK CHECKER] Missing .env variables: {', '.join(missing)}\n"
            f"Run:  python3 scene_intelligence/ig_live_driver.py --extract-cookies\n"
            f"Then: python3 scene_intelligence/ig_live_driver.py --whoami\n"
        )
    return sid, csrf


# ---------------------------------------------------------------------------
# Tracker I/O
# ---------------------------------------------------------------------------

def _load_tracker() -> dict:
    """Load ig_follow_tracker.json, return parsed dict."""
    if not TRACKER_FILE.exists():
        raise SystemExit(f"[ERROR] Tracker file not found: {TRACKER_FILE}")
    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_tracker(data: dict) -> None:
    """Write tracker back to disk atomically (write to .tmp, then rename)."""
    tmp = TRACKER_FILE.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(TRACKER_FILE)


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------

def _friendships_show(
    session: requests.Session,
    their_user_id: str,
    handle: str,
    verbose: bool = False,
) -> Optional[dict]:
    """
    GET /api/v1/friendships/show/{their_user_id}/

    Returns the friendship dict on success, None on failure.
    The `followed_by` key is True if they follow us back.

    Rate limit: safe at ~40/hr. We add a human-like pause between calls.
    """
    url = f"{IG_API_BASE}/friendships/show/{their_user_id}/"
    try:
        r = session.get(
            url,
            headers={"Referer": f"{IG_WEB}/{handle}/"},
            timeout=15,
        )
    except requests.RequestException as exc:
        if verbose:
            print(f"  [NET ERROR] @{handle}: {exc}")
        return None

    if r.status_code == 401:
        raise SystemExit(
            "[FOLLOWBACK CHECKER] Session expired (HTTP 401). Re-extract cookies.\n"
            "Run: python3 scene_intelligence/ig_live_driver.py --extract-cookies"
        )

    if r.status_code == 429:
        raise SystemExit(
            "[FOLLOWBACK CHECKER] Rate limited (HTTP 429). Wait a few hours before retrying."
        )

    if r.status_code == 404:
        if verbose:
            print(f"  [404] @{handle} — account deleted or user_id stale")
        return None

    if r.status_code != 200:
        if verbose:
            print(f"  [HTTP {r.status_code}] @{handle} — unexpected status")
        return None

    try:
        return r.json()
    except ValueError:
        if verbose:
            print(f"  [PARSE ERROR] @{handle} — non-JSON response")
        return None


def _resolve_user_id(
    session: requests.Session,
    handle: str,
    verbose: bool = False,
) -> Optional[str]:
    """
    Fetch user_id for a handle via web_profile_info.
    Used only when user_id is missing from the tracker entry.
    """
    url = f"{IG_API_BASE}/users/web_profile_info/"
    try:
        r = session.get(
            url,
            params={"username": handle},
            headers={"Referer": f"{IG_WEB}/{handle}/"},
            timeout=15,
        )
    except requests.RequestException as exc:
        if verbose:
            print(f"  [NET ERROR] resolving @{handle}: {exc}")
        return None

    if r.status_code != 200:
        return None

    try:
        user = r.json().get("data", {}).get("user", {})
        uid = str(user.get("id", ""))
        return uid if uid else None
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Per-entry check
# ---------------------------------------------------------------------------

def _check_entry(
    entry: dict,
    session: requests.Session,
    today: str,
    verbose: bool,
) -> dict:
    """
    Check a single active_follows entry for follow-back status.

    Returns the (possibly updated) entry dict.
    Never modifies entries where followed_back is already True.
    """
    handle = entry.get("username", "?")

    # Already confirmed follow-back — no need to re-check
    if entry.get("followed_back"):
        if verbose:
            print(f"  [SKIP] @{handle} — already follows back")
        return entry

    # Resolve user_id — required for friendships/show
    user_id = str(entry.get("user_id", "")).strip()
    if not user_id:
        if verbose:
            print(f"  [RESOLVE] @{handle} — user_id missing, fetching...")
        user_id = _resolve_user_id(session, handle, verbose=verbose) or ""
        if user_id:
            entry["user_id"] = user_id
            if verbose:
                print(f"  [RESOLVE] @{handle} — user_id={user_id}")
        else:
            # NOT a measurement. followed_back stays untouched and
            # followback_verified_at is deliberately NOT written, so the
            # engine's fail-closed gate keeps this entry OUT of the sweep
            # (2026-08-28: 26 such failures were read as "doesn't follow back").
            print(f"  [SKIP] @{handle} — could not resolve user_id (UNVERIFIED, protected from sweep)")
            entry["followback_resolve_failed_at"] = today
            return entry

    friendship = _friendships_show(session, user_id, handle, verbose=verbose)
    if friendship is None:
        return entry

    # Real measurement happened — stamp it. This, not stats.last_checked, is
    # what makes an entry sweep-eligible.
    entry["followback_verified_at"] = today
    entry.pop("followback_resolve_failed_at", None)

    follows_back = bool(friendship.get("followed_by"))
    if follows_back and not entry.get("followed_back"):
        entry["followed_back"] = True
        entry["followed_back_at"] = today
        print(f"  [FOLLOW-BACK] @{handle} now follows back!")

    elif verbose:
        following_me = bool(friendship.get("followed_by"))
        i_follow = bool(friendship.get("following"))
        print(f"  [CHECK] @{handle} — followed_by={following_me}, i_follow={i_follow}")

    return entry


# ---------------------------------------------------------------------------
# Unfollow due-date logic
# ---------------------------------------------------------------------------

def _mark_overdue(entry: dict, today_date: date, verbose: bool) -> dict:
    """
    If an account has not followed back and is past its unfollow_after date,
    mark it as 'overdue_unfollow' so the next engine session can act on it.

    Does NOT unfollow. The engine (ig_engagement.py) handles actual unfollows.
    """
    # Skip if already follows back — never auto-unfollow
    if entry.get("followed_back"):
        return entry

    # Skip if protected — keep_following accounts are never queued for unfollow.
    # Also clear any stale overdue_unfollow flag that was set before keep_following
    # was applied (e.g. @nocturnazine, @wrong_era_berlin flagged 2026-06-29).
    if entry.get("keep_following"):
        if entry.get("overdue_unfollow"):
            entry["overdue_unfollow"] = False
            handle = entry.get("username", "?")
            if verbose:
                print(f"  [KEEP] @{handle} — cleared stale overdue_unfollow (keep_following=true)")
        return entry

    # Skip if already marked
    if entry.get("overdue_unfollow"):
        return entry

    unfollow_after_str = entry.get("unfollow_after") or entry.get("unfollow_after_date", "")
    if not unfollow_after_str:
        return entry

    try:
        due_date = date.fromisoformat(unfollow_after_str)
    except ValueError:
        return entry

    if today_date >= due_date:
        entry["overdue_unfollow"] = True
        handle = entry.get("username", "?")
        if verbose:
            print(f"  [OVERDUE] @{handle} — unfollow due since {unfollow_after_str}")

    return entry


# ---------------------------------------------------------------------------
# Main checker
# ---------------------------------------------------------------------------

def run_checker(verbose: bool = False, report_only: bool = False) -> dict:
    """
    Core checker logic.

    Returns a summary dict with counts.
    """
    tracker = _load_tracker()
    active_follows: list[dict] = tracker.get("active_follows", [])
    today_str = date.today().isoformat()
    today_date = date.today()

    print(f"\n=== IG Follow-Back Checker  [{today_str}] ===")
    print(f"Active follows: {len(active_follows)}")

    if not active_follows:
        print("Nothing to check. Run the engagement engine first to start following accounts.")
        return {"total": 0, "new_followbacks": 0, "overdue": 0, "errors": 0}

    if report_only:
        # Just print the current state without any API calls
        return _print_report(tracker, active_follows, verbose)

    # Load credentials and build session
    sid, csrf = _load_credentials()
    session = _build_requests_session(sid, csrf)

    print(f"Checking {len(active_follows)} account(s)...\n")

    new_followbacks = 0
    overdue_count = 0
    error_count = 0
    consecutive_resolve_failures = 0
    resolve_failure_total = 0
    try:
        import ig_engagement_config as _cfg  # type: ignore
        max_consec = int(getattr(_cfg, "FOLLOWBACK_MAX_CONSECUTIVE_RESOLVE_FAILURES", 3))
    except Exception:
        max_consec = 3

    for i, entry in enumerate(active_follows):
        handle = entry.get("username", "?")

        # Mark overdue regardless of API call
        before_overdue = bool(entry.get("overdue_unfollow"))
        entry = _mark_overdue(entry, today_date, verbose)
        if entry.get("overdue_unfollow") and not before_overdue:
            overdue_count += 1

        was_followed_back = bool(entry.get("followed_back"))

        try:
            entry = _check_entry(entry, session, today_str, verbose)
        except SystemExit:
            raise  # Let rate-limit / auth errors propagate
        except Exception as exc:
            error_count += 1
            if verbose:
                print(f"  [ERROR] @{handle}: {exc}")
            active_follows[i] = entry
            continue

        # CLASS A BREAKER (2026-08-28): repeated id-resolution failures are an
        # IG-signal event per SOP 4.3 ("could not resolve user ID" -> stop, do
        # not retry today), not a data quirk. Without this, the 2026-08-28 run
        # logged 26 of them, stamped stats.last_checked as if all was well, and
        # handed the session an unfollow plan built on nothing.
        if entry.get("followback_resolve_failed_at") == today_str:
            consecutive_resolve_failures += 1
            resolve_failure_total += 1
            if consecutive_resolve_failures >= max_consec:
                active_follows[i] = entry
                tracker["active_follows"] = active_follows
                # Deliberately NOT stamping stats.last_checked: nothing was
                # measured, and a stamp here is exactly what made the broken
                # staleness gate pass on 2026-08-28.
                _save_tracker(tracker)
                raise SystemExit(
                    f"\n[CHECKER STOPPED] {consecutive_resolve_failures} consecutive "
                    f"user_id resolution failures (Class A signal, SOP 4.3).\n"
                    f"  Partial progress saved; stats.last_checked NOT stamped.\n"
                    f"  Do NOT retry today. Unverified entries stay protected from "
                    f"the unfollow sweep.\n"
                    f"  Likely causes: web_profile_info throttled, or session cookies "
                    f"degraded. Backfill ids from the followers roster instead."
                )
        else:
            consecutive_resolve_failures = 0

        if entry.get("followed_back") and not was_followed_back:
            new_followbacks += 1

        active_follows[i] = entry

        # Human-like pause between API calls — 2-5 seconds
        if i < len(active_follows) - 1:
            time.sleep(random.uniform(2.0, 5.0))

    # Rebuild tracker with updated entries
    tracker["active_follows"] = active_follows

    # Update stats — single snapshot definition, see ig_tracker_stats.py
    try:
        from scene_intelligence.ig_tracker_stats import recompute_follow_backs
    except ImportError:
        from ig_tracker_stats import recompute_follow_backs
    stats = tracker.setdefault("stats", {})
    recompute_follow_backs(tracker)
    stats["last_checked"] = today_str

    # Save
    _save_tracker(tracker)
    print(f"\nTracker saved. ({TRACKER_FILE.name})")

    # Sync followback flags into paid_audience_seed.json so downstream
    # analytics see the same state. Match by username (lowercased).
    try:
        if PAID_FILE.exists():
            paid = json.loads(PAID_FILE.read_text())
            tracker_lookup = {
                str(e.get("username", "")).lower(): e
                for e in active_follows
            }
            paid_synced = 0
            for entry in paid:
                u = str(entry.get("username", "")).lower()
                t = tracker_lookup.get(u)
                if not t:
                    continue
                if t.get("followed_back") and not entry.get("followed_back"):
                    entry["followed_back"] = True
                    if t.get("followed_back_at"):
                        entry["followed_back_at"] = t["followed_back_at"]
                    paid_synced += 1
            PAID_FILE.write_text(json.dumps(paid, indent=2, ensure_ascii=False))
            if paid_synced:
                print(f"Paid audience seed synced: {paid_synced} new follow-backs marked. ({PAID_FILE.name})")
    except Exception as exc:
        print(f"  [WARN] Failed to sync paid_audience_seed: {exc}")

    # Summary report
    summary = _print_report(tracker, active_follows, verbose)
    summary["new_followbacks"] = new_followbacks
    summary["overdue"] = overdue_count
    summary["errors"] = error_count

    return summary


def _print_report(tracker: dict, active_follows: list[dict], verbose: bool) -> dict:
    """Print and return a summary of current follow state."""
    today = date.today().isoformat()

    total = len(active_follows)
    followed_back = [e for e in active_follows if e.get("followed_back")]
    protected = [e for e in active_follows if e.get("keep_following") and not e.get("followed_back")]
    protected_handles = {e.get("username") for e in protected}
    pending = [e for e in active_follows if not e.get("followed_back") and not e.get("overdue_unfollow") and not e.get("keep_following")]
    overdue = [e for e in active_follows if e.get("overdue_unfollow") and not e.get("followed_back") and e.get("username") not in protected_handles]
    unfollowed = tracker.get("unfollowed_history", [])
    total_unfollowed = len(unfollowed)
    stats = tracker.get("stats", {})

    print(f"\n--- Follow-Back Report [{today}] ---")
    print(f"Active follows:    {total}")
    print(f"  Follow-backs:    {len(followed_back)}  ({_pct(len(followed_back), total)})")
    print(f"  Pending:         {len(pending)}")
    print(f"  Protected (keep):{len(protected)}")
    print(f"  Overdue unfollow:{len(overdue)}")
    print(f"Total unfollowed:  {total_unfollowed}")
    print(f"Total ever followed: {stats.get('total_followed', 0)}")
    # Rate = reciprocators / total ever followed. len(followed_back) IS
    # stats.follow_backs (same snapshot); adding them, as this line did until
    # 2026-07-19, printed ~2x the real rate (audit P3-19).
    print(f"Follow-back rate:  {_pct(len(followed_back), max(1, stats.get('total_followed', total)))}")

    if followed_back:
        print(f"\nFollow-backs ({len(followed_back)}):")
        for e in followed_back:
            date_str = e.get("followed_back_at", "?")
            print(f"  @{e['username']}  (followed back: {date_str})")

    if overdue:
        print(f"\nOverdue for unfollow ({len(overdue)}) — will be unfollowed next session:")
        for e in overdue:
            due = e.get("unfollow_after") or e.get("unfollow_after_date", "?")
            print(f"  @{e['username']}  (due: {due})")

    if protected:
        print(f"\nProtected / keep_following ({len(protected)}) — excluded from unfollow sweep:")
        for e in protected:
            reason = e.get("keep_reason", "no reason recorded")
            print(f"  @{e['username']}  ({reason})")

    if verbose and pending:
        print(f"\nStill waiting ({len(pending)}):")
        for e in pending:
            followed_at = e.get("followed_at", "?")
            due = e.get("unfollow_after") or e.get("unfollow_after_date", "?")
            print(f"  @{e['username']}  (followed: {followed_at}, unfollow_after: {due})")

    return {
        "total": total,
        "followed_back": len(followed_back),
        "pending": len(pending),
        "protected": len(protected),
        "overdue": len(overdue),
        "total_unfollowed": total_unfollowed,
    }


def _pct(part: int, total: int) -> str:
    if total == 0:
        return "0%"
    return f"{round(100 * part / total)}%"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Check which followed accounts have followed back."
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print per-account check details",
    )
    parser.add_argument(
        "--report-only", "-r",
        action="store_true",
        help="Print current report from tracker file without making API calls",
    )
    try:
        from scene_intelligence.ig_daily_ledger import add_ledger_argument, check_and_claim
    except ImportError:
        from ig_daily_ledger import add_ledger_argument, check_and_claim
    add_ledger_argument(parser)
    args = parser.parse_args()

    # 2.0 law (T-003): hard gates first, then the budgeted claim. The checker
    # is EXCEPTIONAL-ONLY since 2026-08-30 — routine reciprocity comes from
    # Amir's 30-day IG data export, not from friendships/show calls.
    # --report-only reads the tracker locally and never claims.
    if not args.report_only:
        try:
            from scene_intelligence.ig_ops_guards import standard_gates
        except ImportError:
            from ig_ops_guards import standard_gates
        standard_gates("ig")
        check_and_claim("ig_followback_checker", override=args.override_ledger,
                    reason=getattr(args, 'override_reason', None),
                        est_calls=20, endpoint="friendship_checks")

    try:
        summary = run_checker(verbose=args.verbose, report_only=args.report_only)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Partial results may have been saved.")
        sys.exit(1)
    except Exception as exc:
        print(f"\n[FATAL ERROR] {exc}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    if summary.get("new_followbacks", 0) > 0:
        print(f"\n{summary['new_followbacks']} new follow-back(s) recorded today.")


if __name__ == "__main__":
    main()
