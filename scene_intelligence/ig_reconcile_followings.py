"""
ig_reconcile_followings.py
---------------------------
Reconcile ig_follow_tracker.json against @inch_of_shadow's ACTUAL
Instagram followings list.

Why this exists:
  The follow tracker drifts from IG reality. Accounts get unfollowed
  outside the protocol, follows silently drop (account went private,
  blocked us, etc.), or tracker entries were wrong from creation. The
  2026-05-15 session exposed this: 7 of 7 unfollow targets showed a
  "Follow" button -- IG said we never followed them. CC flagged that
  all ~51 overdue entries might be inaccurate.

  This script fetches the real followings list once, compares it to
  the tracker's active_follows, and marks every drifted entry as
  status tracker_drift_not_following (moved to unfollowed_history).
  It then prints a CLEAN overdue list -- accounts we genuinely follow
  and that are past their 7-day window -- safe to actually unfollow.

Run on a day with no IG engagement scheduled (Tue/Sat, or any open
slot). One IG action for the day.

  python3 scene_intelligence/ig_reconcile_followings.py
  python3 scene_intelligence/ig_reconcile_followings.py --dry-run

Credentials: IG_SESSION_ID, IG_CSRF_TOKEN, IG_USER_ID from .env
(same as ig_followback_checker.py / ig_live_driver.py).
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from datetime import date
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env"
SI_DIR = BASE_DIR / "scene_intelligence"
TRACKER_FILE = SI_DIR / "ig_follow_tracker.json"

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
    "Origin": IG_WEB,
}


def _build_session(session_id: str, csrf_token: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({**_BASE_HEADERS, "X-CSRFToken": csrf_token})
    s.cookies.set("sessionid", session_id, domain=".instagram.com")
    s.cookies.set("csrftoken", csrf_token, domain=".instagram.com")
    return s


def _load_credentials() -> tuple[str, str, str]:
    load_dotenv(ENV_FILE)
    sid = os.getenv("IG_SESSION_ID", "").strip()
    csrf = os.getenv("IG_CSRF_TOKEN", "").strip()
    uid = os.getenv("IG_USER_ID", "").strip()
    missing = [n for n, v in [("IG_SESSION_ID", sid), ("IG_CSRF_TOKEN", csrf),
                              ("IG_USER_ID", uid)] if not v]
    if missing:
        raise SystemExit(
            f"\n[RECONCILE] Missing .env variables: {', '.join(missing)}\n"
            f"Refresh with: python3 scene_intelligence/ig_live_driver.py --extract-cookies\n"
        )
    return sid, csrf, uid


def fetch_all_followings(session: requests.Session, user_id: str) -> Optional[set[str]]:
    """
    Fetch the complete set of usernames @inch_of_shadow currently follows.
    Paginates via next_max_id. Returns a lowercased username set, or None
    on a hard failure (caller should abort without touching the tracker).

    Hard cap: 60 pages (each page ~50-200 users) -- far more than needed
    for a ~900-following account, but a guard against infinite loops.
    """
    usernames: set[str] = set()
    max_id: Optional[str] = None
    page = 0
    MAX_PAGES = 60

    while page < MAX_PAGES:
        page += 1
        params = {"count": 200}
        if max_id:
            params["max_id"] = max_id
        url = f"{IG_API_BASE}/friendships/{user_id}/following/"
        try:
            r = session.get(url, params=params,
                            headers={"Referer": f"{IG_WEB}/"}, timeout=20)
        except requests.RequestException as exc:
            print(f"  [NET ERROR] page {page}: {exc}", file=sys.stderr)
            return None

        if r.status_code == 401:
            print("[RECONCILE] Session expired (HTTP 401). Re-extract cookies.",
                  file=sys.stderr)
            return None
        if r.status_code == 429:
            print("[RECONCILE] Rate-limited (HTTP 429). Stop, wait several hours.",
                  file=sys.stderr)
            return None
        if r.status_code != 200:
            print(f"  [HTTP {r.status_code}] page {page}", file=sys.stderr)
            return None

        try:
            body = r.json()
        except ValueError:
            print(f"  [JSON ERROR] page {page}", file=sys.stderr)
            return None

        users = body.get("users", [])
        for u in users:
            uname = (u.get("username") or "").strip().lower()
            if uname:
                usernames.add(uname)

        print(f"  page {page}: +{len(users)} users (running total {len(usernames)})")

        max_id = body.get("next_max_id")
        if not max_id:
            break  # last page
        time.sleep(random.uniform(2, 5))  # human-like pacing

    return usernames


def reconcile(dry_run: bool) -> int:
    if not TRACKER_FILE.exists():
        print(f"[RECONCILE] Tracker not found: {TRACKER_FILE}", file=sys.stderr)
        return 1

    tracker = json.loads(TRACKER_FILE.read_text(encoding="utf-8"))
    active = tracker.get("active_follows", [])
    if not active:
        print("[RECONCILE] No active_follows entries -- nothing to reconcile.")
        return 0

    print(f"=== IG Followings Reconciliation  [{date.today()}] ===")
    print(f"Tracker active_follows: {len(active)}")
    print(f"Dry run: {dry_run}\n")

    sid, csrf, uid = _load_credentials()
    session = _build_session(sid, csrf)

    print("Fetching actual IG followings list...")
    real_following = fetch_all_followings(session, uid)
    if real_following is None:
        print("\n[RECONCILE] ABORTED -- could not fetch followings. "
              "Tracker NOT modified.", file=sys.stderr)
        return 1

    print(f"\nActual accounts @inch_of_shadow follows: {len(real_following)}\n")

    today = date.today().isoformat()
    drifted = []
    confirmed = []
    for entry in active:
        uname = (entry.get("username") or "").strip().lower()
        if not uname:
            continue
        if uname in real_following:
            confirmed.append(entry)
        else:
            drifted.append(entry)

    print("=== Reconciliation Result ===")
    print(f"  Confirmed still-following:  {len(confirmed)}")
    print(f"  DRIFTED (not actually following): {len(drifted)}")

    if drifted:
        print(f"\n  Drifted entries (tracker said active, IG says not following):")
        for e in drifted:
            print(f"    - @{e.get('username')}  (tracker followed_at: {e.get('followed_at','?')})")

    # Clean overdue list (genuinely-followed + past window + not reciprocated)
    overdue = []
    for e in confirmed:
        if e.get("followed_back") or e.get("keep_following"):
            continue
        ua = e.get("unfollow_after", "")
        if ua and ua <= today:
            overdue.append(e)
    overdue.sort(key=lambda x: x.get("unfollow_after", ""))

    print(f"\n=== CLEAN overdue-for-unfollow list ({len(overdue)}) ===")
    print("(genuinely followed, past 7-day window, not reciprocated -- "
          "safe to actually unfollow)")
    for e in overdue:
        print(f"  @{e.get('username'):<32} unfollow_after: {e.get('unfollow_after')}")

    if dry_run:
        print(f"\n[DRY-RUN] No tracker writes. {len(drifted)} would be moved to "
              f"unfollowed_history.")
        return 0

    if drifted:
        drift_names = {(e.get("username") or "").lower() for e in drifted}
        tracker["active_follows"] = [
            e for e in active
            if (e.get("username") or "").lower() not in drift_names
        ]
        for e in drifted:
            tracker.setdefault("unfollowed_history", []).append({
                "username": e.get("username"),
                "followed_at": e.get("followed_at"),
                "unfollowed_at": today,
                "reason": "tracker_drift_not_following",
                "note": f"Reconciliation {today}: IG followings list does not "
                        f"contain this account. Follow dropped / never landed / "
                        f"unfollowed outside protocol.",
            })
        stats = tracker.setdefault("stats", {})
        stats["total_followed"] = max(0, stats.get("total_followed", 0) - len(drifted))
        stats["last_reconciled"] = today

        tmp = TRACKER_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(tracker, indent=2, ensure_ascii=False),
                       encoding="utf-8")
        tmp.replace(TRACKER_FILE)
        print(f"\n[OK] Tracker reconciled. {len(drifted)} drift entries moved to "
              f"unfollowed_history.")
        print(f"     active_follows now: {len(tracker['active_follows'])}")
    else:
        print(f"\n[OK] No drift found -- tracker is accurate. Nothing to change.")

    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true",
                   help="Preview reconciliation without modifying the tracker")
    try:
        from scene_intelligence.ig_daily_ledger import add_ledger_argument, check_and_claim
    except ImportError:
        from ig_daily_ledger import add_ledger_argument, check_and_claim
    add_ledger_argument(p)
    args = p.parse_args()
    # 2.0 law (T-003): reconcile paginates the OWN-followings roster — the
    # enumeration class that got a token invalidated on 2026-08-29. Its
    # endpoint budget is 0 (banned), so this claim now always refuses with
    # the pointer to the replacement: Amir's IG data export contains the
    # complete following list (data/instagram-*/connections/...). Reconcile
    # from the export is the 2.0 path; the API path stays only as history.
    try:
        from scene_intelligence.ig_ops_guards import standard_gates
    except ImportError:
        from ig_ops_guards import standard_gates
    standard_gates("ig")
    check_and_claim("ig_reconcile_followings", override=args.override_ledger,
                    reason=getattr(args, 'override_reason', None),
                    est_calls=19, endpoint="roster_walk")
    return reconcile(args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
