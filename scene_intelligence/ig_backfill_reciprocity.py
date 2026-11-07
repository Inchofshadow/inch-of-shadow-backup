"""
scene_intelligence/ig_backfill_reciprocity.py
---------------------------------------------
Repair reciprocity measurement from the FOLLOWERS ROSTER, in one pass.

Why this exists (2026-08-28)
----------------------------
ig_followback_checker asks about one account at a time via
/friendships/show/{user_id}/, which needs a numeric user_id. 26 of 28
active_follows entries have user_id=null, and resolving them goes through
web_profile_info -- the endpoint that was throttling. Every resolution failed,
the checker left those entries untouched, and `followed_back: false` (meaning
"never measured") was read by the unfollow sweep as "does not follow back".
@_.miser._ and @infoluences were churned that way.

The roster approach fixes the measurement instead of retrying the broken path:
one paginated walk of /friendships/{me}/followers/ returns every follower's
username AND numeric pk. Reciprocity then becomes set membership -- no
per-account calls, no user_id needed up front, and a different endpoint from
the throttled one.

Trust rules (this is the important part)
----------------------------------------
  PRESENCE in the roster proves a follow-back. Always safe to write, even if
  pagination stopped early.
  ABSENCE only proves a non-follow-back if the roster is COMPLETE. A truncated
  fetch would otherwise mark real reciprocators as verified non-followers --
  the exact failure this script exists to prevent (cf. the reconcile
  partial-fetch hazard, audit L5). So negatives are written ONLY when the
  fetched count reconciles with the account's reported follower count within
  ROSTER_COMPLETENESS_TOLERANCE.

Usage:
    python3 scene_intelligence/ig_backfill_reciprocity.py --dry-run
    python3 scene_intelligence/ig_backfill_reciprocity.py
    python3 scene_intelligence/ig_backfill_reciprocity.py --override-ledger

Claims the daily IG ledger slot. ~5-20 API calls for a ~930-follower account.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import tempfile
import time
from datetime import date
from pathlib import Path
from typing import Optional

import requests

SI_DIR = Path(__file__).resolve().parent
REPO = SI_DIR.parent
sys.path.insert(0, str(SI_DIR))

TRACKER_FILE = SI_DIR / "ig_follow_tracker.json"
IG_API_BASE = "https://www.instagram.com/api/v1"
IG_WEB = "https://www.instagram.com"

MAX_PAGES = 60
ROSTER_COMPLETENESS_TOLERANCE = 0.02  # fetched must be within 2% of reported

_BASE_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36"),
    "X-IG-App-ID": "936619743392459",
    "Accept": "*/*",
}


def _load_credentials() -> tuple[str, str, str]:
    try:
        from dotenv import load_dotenv
        load_dotenv(REPO / ".env")
    except ImportError:
        pass
    sid = os.getenv("IG_SESSION_ID", "").strip()
    csrf = os.getenv("IG_CSRF_TOKEN", "").strip()
    uid = os.getenv("IG_USER_ID", "").strip()
    if not sid or not csrf:
        raise SystemExit("[BACKFILL] IG_SESSION_ID / IG_CSRF_TOKEN missing from .env")
    if not uid:
        raise SystemExit(
            "[BACKFILL] IG_USER_ID missing from .env — needed to address the "
            "followers roster. Get it with:\n"
            "  python3 scene_intelligence/ig_live_driver.py --whoami"
        )
    return sid, csrf, uid


def _build_session(sid: str, csrf: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({**_BASE_HEADERS, "X-CSRFToken": csrf})
    s.cookies.set("sessionid", sid, domain=".instagram.com")
    s.cookies.set("csrftoken", csrf, domain=".instagram.com")
    return s


def fetch_followers_roster(session: requests.Session,
                           me_id: str) -> tuple[Optional[dict], bool]:
    """Walk /friendships/{me}/followers/.

    Returns (mapping {username_lower: pk}, complete_flag). complete_flag is
    True only when pagination ended naturally (no next_max_id) -- a page cap
    or an error yields False, which downgrades the run to positives-only.
    """
    roster: dict[str, str] = {}
    max_id: Optional[str] = None
    page = 0
    complete = False

    while page < MAX_PAGES:
        page += 1
        params = {"count": 200}
        if max_id:
            params["max_id"] = max_id
        try:
            r = session.get(f"{IG_API_BASE}/friendships/{me_id}/followers/",
                            params=params,
                            headers={"Referer": f"{IG_WEB}/"}, timeout=20)
        except requests.RequestException as exc:
            print(f"  [NET ERROR] page {page}: {exc}", file=sys.stderr)
            return (roster or None), False

        if r.status_code == 401:
            raise SystemExit("[BACKFILL] Session expired (HTTP 401). Refresh cookies in .env.")
        if r.status_code == 429:
            raise SystemExit("[BACKFILL] Rate-limited (HTTP 429). Stop; do not retry today.")
        if r.status_code != 200:
            print(f"  [HTTP {r.status_code}] page {page} — stopping", file=sys.stderr)
            return (roster or None), False

        try:
            body = r.json()
        except ValueError:
            print(f"  [JSON ERROR] page {page}", file=sys.stderr)
            return (roster or None), False

        users = body.get("users", [])
        for u in users:
            uname = (u.get("username") or "").strip().lower()
            pk = str(u.get("pk") or u.get("id") or "").strip()
            if uname:
                roster[uname] = pk
        print(f"  page {page}: +{len(users)} (total {len(roster)})")

        max_id = body.get("next_max_id")
        if not max_id:
            complete = True
            break
        time.sleep(random.uniform(2, 5))

    return roster, complete


def _reported_follower_count(session: requests.Session) -> Optional[int]:
    """Own follower count, for the completeness check. Best-effort: this uses
    web_profile_info, which may be throttled -- a None just means we cannot
    certify completeness, so negatives are withheld."""
    try:
        r = session.get(f"{IG_API_BASE}/users/web_profile_info/",
                        params={"username": "inch_of_shadow"},
                        headers={"Referer": f"{IG_WEB}/inch_of_shadow/"}, timeout=15)
        if r.status_code != 200:
            return None
        u = r.json().get("data", {}).get("user", {})
        return int((u.get("edge_followed_by") or {}).get("count"))
    except Exception:
        return None


def _atomic_write(path: Path, data: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix="." + path.stem)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Backfill reciprocity from the followers roster")
    ap.add_argument("--dry-run", action="store_true",
                    help=("report only, write nothing. WARNING (2026-08-29): do NOT run this "
                          "and then immediately re-run for real -- that walks the roster twice "
                          "(~80 pages in minutes) and Instagram invalidated the session for it. "
                          "Walk once: run for real, or dry-run and wait for the next quiet day."))
    ap.add_argument("--override-ledger", action="store_true")
    ap.add_argument("--override-reason", default=None, metavar="TEXT",
                    help="required with --override-ledger (logged)")
    args = ap.parse_args()

    # BANNED under the 2.0 law (Amir, 2026-08-30; TICKETS.md T-003): the full
    # followers-roster walk is exactly what invalidated the session token on
    # 2026-08-29, and reciprocity now comes from Amir's official IG data
    # export (data/instagram-*/connections/followers_and_following/) with
    # ZERO API calls — see docs/ig-engagement-sop.md. No flag re-enables this;
    # git history keeps the code if the law ever changes.
    print("[BANNED] ig_backfill_reciprocity walks the followers roster — "
          "banned by the 2.0 law (2026-08-30). Reciprocity comes from the "
          "IG data export now (see the SOP). Nothing was run.")
    return 4

    if not args.dry_run:
        import ig_daily_ledger as ledger
        ledger.check_and_claim("ig_backfill_reciprocity", **ledger.override_kwargs(args))

    sid, csrf, me_id = _load_credentials()
    session = _build_session(sid, csrf)
    today = date.today().isoformat()

    print("=== Reciprocity backfill from followers roster ===")
    reported = _reported_follower_count(session)
    print(f"Reported follower count: {reported if reported is not None else 'unavailable'}")

    roster, complete = fetch_followers_roster(session, me_id)
    if not roster:
        raise SystemExit("[BACKFILL] Roster fetch returned nothing — aborting, tracker untouched.")

    trust_negatives = False
    if complete and reported:
        drift = abs(len(roster) - reported) / max(reported, 1)
        trust_negatives = drift <= ROSTER_COMPLETENESS_TOLERANCE
        print(f"Roster complete: {len(roster)} fetched vs {reported} reported "
              f"({drift:.1%} drift) -> negatives {'TRUSTED' if trust_negatives else 'WITHHELD'}")
    else:
        print("Roster completeness NOT certified -> writing positives only "
              "(absence proves nothing on a partial fetch)")

    tracker = json.loads(TRACKER_FILE.read_text(encoding="utf-8"))
    active = tracker.get("active_follows", [])

    ids_filled = pos = neg = 0
    for e in active:
        uname = (e.get("username") or "").strip().lower()
        if not uname:
            continue
        in_roster = uname in roster

        if in_roster and not e.get("user_id"):
            if roster[uname]:
                e["user_id"] = roster[uname]
                ids_filled += 1

        if in_roster:
            if not e.get("followed_back"):
                e["followed_back"] = True
                e.setdefault("followed_back_at", today)
                e["followback_discovered_via"] = "followers_roster_backfill"
                pos += 1
            e["followback_verified_at"] = today
            e.pop("followback_resolve_failed_at", None)
            e.pop("overdue_unfollow", None)
        elif trust_negatives:
            # Certified complete roster: absence is a real measurement.
            e["followback_verified_at"] = today
            e.pop("followback_resolve_failed_at", None)
            neg += 1

    print(f"\nuser_ids filled:        {ids_filled}")
    print(f"NEW follow-backs found: {pos}")
    print(f"verified non-followers: {neg}")
    unverified = sum(1 for e in active if not e.get("followback_verified_at"))
    print(f"still unverified:       {unverified} (these stay protected from the sweep)")

    if args.dry_run:
        print("\n[DRY-RUN] Nothing written.")
        return 0

    try:
        from ig_tracker_stats import recompute_follow_backs
        recompute_follow_backs(tracker)
    except Exception:
        pass
    stats = tracker.setdefault("stats", {})
    stats["active_follows"] = len(active)
    stats["total_unfollowed"] = len(tracker.get("unfollowed_history", []))
    stats["total_followed"] = stats["active_follows"] + stats["total_unfollowed"]
    if trust_negatives:
        stats["last_checked"] = today

    backup = TRACKER_FILE.with_suffix(f".json.bak.{today.replace('-','')}_pre_backfill")
    backup.write_text(TRACKER_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    _atomic_write(TRACKER_FILE, tracker)
    print(f"\n[OK] Tracker updated (backup: {backup.name})")
    print(f"[OK] follow_backs now: {stats.get('follow_backs')} of {stats.get('active_follows')} active")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
