"""
scene_intelligence/sc_weekly_health.py
---------------------------------------
Weekly read-only SC health pass for Inch of Shadow.

Runs every Wednesday from a Claude Code session in VS Code (NOT from
Claude-in-Chrome). The Wednesday /schedule task is a reminder-only —
the artist comes to Claude Code and asks for this run.

What it does:
  1. Verifies SC_BROWSER_TOKEN against /me.
  2. Fetches /users/16014870/followings (paginated).
  3. Fetches /users/16014870/followers (paginated).
  4. Updates sc_follow_tracker.json:
       - marks followed_back=True for any entry whose user_id is
         now in /me/followers
       - marks no_longer_following=True for any entry whose user_id
         is no longer in /me/followings
       - resolves user_id holes by slug match against live followings
  5. Runs discovery refresh via sc_engagement.discover_related_artists.
  6. Saves discovery_candidates_<YYYYMMDD>.json.
  7. Generates docs/reports/sc-weekly-<YYYYMMDD>.md.

Hard rules:
  - READ-ONLY. Never writes to SC's API.
  - API budget:
    - Direct calls (token verify + /me/followings + /me/followers pagination):
      ~3-5 calls. Tracked by API_BUDGET_HARD_CAP (=30); aborts if exceeded.
    - Discovery calls (~15 seed crawls + ~50 per-candidate last-upload fetches
      since 2026-05-27): goes through sc_engagement.sc_client_get and is NOT
      tracked against API_BUDGET_HARD_CAP. Total real calls per run: ~70.
  - Aborts on: 401, 403, CAPTCHA-shaped responses, network errors,
    unexpected response shapes.

Usage:
    python3 scene_intelligence/sc_weekly_health.py [--dry-run] [--no-discovery]

Reference: docs/sc-engagement-sop.md §6.1
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

try:
    from scene_intelligence.json_io import atomic_write_json
    from scene_intelligence.ig_ops_guards import standard_gates as _standard_gates
except ImportError:
    from json_io import atomic_write_json  # script-dir invocation
    from ig_ops_guards import standard_gates as _standard_gates

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

BASE = Path(__file__).parent.parent
load_dotenv(BASE / ".env")

USER_ID = "16014870"
TOKEN = os.getenv("SC_BROWSER_TOKEN", "").strip()

API_BASE = "https://api-v2.soundcloud.com"
HEADERS = {
    "Authorization": f"OAuth {TOKEN}",
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    ),
    "Origin": "https://soundcloud.com",
    "Referer": "https://soundcloud.com/",
}

TRACKER_FILE = BASE / "scene_intelligence" / "sc_follow_tracker.json"
ENG_LOG_FILE = BASE / "scene_intelligence" / "engagement_log.json"
AUDIT_FILE   = BASE / "scene_intelligence" / "sc_following_audit.json"
REPORTS_DIR  = BASE / "docs" / "reports"

API_BUDGET_HARD_CAP = 30

# Counter
_api_calls = 0


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class HealthCheckError(Exception):
    """Base error: any of these halt the run cleanly."""

class TokenExpired(HealthCheckError):
    pass

class APIBudgetExceeded(HealthCheckError):
    pass

class CaptchaTriggered(HealthCheckError):
    pass


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def _api_get(url: str, params: dict | None = None) -> dict | list:
    """Single GET. Increments budget. Raises on non-200 or budget overflow."""
    global _api_calls
    if _api_calls >= API_BUDGET_HARD_CAP:
        raise APIBudgetExceeded(
            f"API budget hard cap of {API_BUDGET_HARD_CAP} reached"
        )
    _api_calls += 1
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    except requests.RequestException as exc:
        raise HealthCheckError(f"Network error on {url}: {exc}") from exc

    body_lower = (r.text or "").lower()
    if r.status_code == 401:
        raise TokenExpired(
            "SC_BROWSER_TOKEN rejected (HTTP 401). "
            "Refresh per docs/sc-engagement-sop.md §8.2."
        )
    if "captcha-delivery.com" in body_lower or "captcha" in body_lower[:300]:
        raise CaptchaTriggered(
            f"CAPTCHA in response from {url}. "
            "48-72h cooldown applies per SOP §4.1.4."
        )
    if r.status_code == 403:
        raise HealthCheckError(f"HTTP 403 on {url}: {r.text[:200]}")
    if r.status_code == 429:
        retry_after = int(r.headers.get("Retry-After", "0") or "0")
        if retry_after > 60:
            raise HealthCheckError(
                f"Rate-limit block on {url} (Retry-After={retry_after}s). "
                "Treating as bot signal — aborting."
            )
        raise HealthCheckError(
            f"Rate-limited on {url} (Retry-After={retry_after}s). Try later."
        )
    if r.status_code != 200:
        raise HealthCheckError(f"HTTP {r.status_code} on {url}: {r.text[:200]}")

    try:
        return r.json()
    except ValueError as exc:
        raise HealthCheckError(f"Non-JSON response from {url}: {exc}") from exc


def _paginate(url: str) -> list:
    """Walk a SC v2 collection endpoint to completion."""
    out: list = []
    next_url = url
    while next_url:
        data = _api_get(next_url, params={"limit": 200})
        if not isinstance(data, dict):
            raise HealthCheckError(f"Unexpected paginated shape: {type(data).__name__}")
        out.extend(data.get("collection", []))
        next_url = data.get("next_href")
    return out


# ---------------------------------------------------------------------------
# Workflow steps
# ---------------------------------------------------------------------------

def verify_token() -> dict:
    """Confirm SC_BROWSER_TOKEN works and authenticates as the right user."""
    if not TOKEN:
        raise TokenExpired(
            "SC_BROWSER_TOKEN not set in .env. "
            "Add it per docs/sc-engagement-sop.md §8.2."
        )
    me = _api_get(f"{API_BASE}/me")
    if not isinstance(me, dict):
        raise HealthCheckError(f"Unexpected /me response: {type(me).__name__}")
    if str(me.get("id")) != USER_ID:
        raise HealthCheckError(
            f"Token authenticates as user_id={me.get('id')}, "
            f"expected {USER_ID}. Wrong account?"
        )
    return me


def fetch_lists() -> tuple[list, list]:
    """Fetch full following + follower lists. ~2 calls each at our scale."""
    followings = _paginate(f"{API_BASE}/users/{USER_ID}/followings")
    followers  = _paginate(f"{API_BASE}/users/{USER_ID}/followers")
    return followings, followers


# G-03: more than this share of current reciprocators "lost" in one run is
# treated as a bad follower fetch, not real churn, and nothing is stamped.
FOLLOWBACK_LOST_MAX_SHARE = 0.2


def update_tracker(
    tracker: dict,
    followings: list,
    followers: list,
    dry_run: bool,
) -> dict:
    """Mutate tracker in-memory; return per-update counts."""
    today = date.today().isoformat()

    # Backup the PRE-mutation state (SC-05, 2026-09-01). The old code wrote
    # the backup after mutating, so every "_health" bak preserved the run's
    # own changes instead of a restore point (audit F4).
    if not dry_run:
        bak_path = TRACKER_FILE.parent / (
            f"sc_follow_tracker.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}_health.json"
        )
        bak_path.write_text(json.dumps(tracker, indent=2, ensure_ascii=False))

    following_ids = {str(u["id"]) for u in followings if u.get("id")}
    follower_ids  = {str(u["id"]) for u in followers  if u.get("id")}
    by_permalink  = {(u.get("permalink") or "").lower(): u for u in followings}

    new_followbacks: list[str] = []
    followback_lost: list[str] = []
    followback_regained: list[str] = []
    drift_detected:  list[str] = []
    reciprocator_churn: list[str] = []
    user_ids_resolved = 0
    lost_candidates: list[dict] = []

    for entry in tracker.get("follows", []):
        # Resolve missing user_id by permalink/slug
        if not entry.get("user_id"):
            slug = (entry.get("log_slug") or "").lower()
            if not slug:
                url = (entry.get("url") or "").rstrip("/").lower()
                slug = url.split("/")[-1].split("?")[0] if url else ""
            if slug and slug in by_permalink:
                u = by_permalink[slug]
                entry["user_id"]      = str(u["id"])
                entry["followers"]    = u.get("followers_count", 0)
                entry["resolved_via"] = "live_followings"
                user_ids_resolved += 1

        uid = str(entry.get("user_id") or "")

        # Detect new follow-back
        if uid and uid in follower_ids and not entry.get("followed_back"):
            entry["followed_back"] = True
            entry["followback_detected_at"] = today
            new_followbacks.append(entry.get("name", uid))

        # G-03 (2026-10-21): a reciprocator who no longer follows us. The
        # flag used to be one-way, so they kept seed status and unfollow
        # protection forever. History is kept: followed_back stays True and
        # followback_lost_at records when they dropped us.
        if uid and entry.get("followed_back") and follower_ids:
            if uid not in follower_ids and not entry.get("followback_lost_at"):
                lost_candidates.append(entry)
            elif uid in follower_ids and entry.get("followback_lost_at"):
                entry.pop("followback_lost_at", None)
                entry["followback_regained_at"] = today
                followback_regained.append(entry.get("name", uid))

        # Detect drift (was followed, no longer in our followings)
        if uid and uid not in following_ids and not entry.get("no_longer_following"):
            entry["no_longer_following"] = True
            drift_detected.append(entry.get("name", uid))
            # RECIPROCATOR CHURN ALARM (SC-05, 2026-09-01). A drifted entry
            # that had followed_back means WE unfollowed a reciprocator —
            # the la-ramazotti case sat unnamed in a 32-name drift list for
            # 7 weeks because nothing cross-checked this.
            if entry.get("followed_back") and not entry.get("followback_lost_at"):
                reciprocator_churn.append(entry.get("name", uid))   # G-03: lost ones left first

    # Sanity gate: a partial follower fetch would mark half the reciprocators
    # as lost in one go. Above the threshold nothing is stamped this run.
    n_recip = sum(1 for e in tracker.get("follows", []) if e.get("followed_back")
                  and not e.get("followback_lost_at"))
    lost_suspect = bool(lost_candidates) and (
        len(lost_candidates) > max(FOLLOWBACK_LOST_MAX_SHARE * n_recip, 5))
    if not lost_suspect:
        for entry in lost_candidates:
            entry["followback_lost_at"] = today
            followback_lost.append(entry.get("name", entry.get("user_id", "")))

    tracker.setdefault("stats", {})["follow_backs"] = sum(
        1 for e in tracker.get("follows", []) if e.get("followed_back")
    )

    return {
        "new_followbacks":    new_followbacks,
        "drift_detected":     drift_detected,
        "reciprocator_churn": reciprocator_churn,
        "followback_lost":    followback_lost,
        "followback_regained": followback_regained,
        "followback_lost_suspect": len(lost_candidates) if lost_suspect else 0,
        "user_ids_resolved":  user_ids_resolved,
        "following_ids":      following_ids,
        "follower_ids":       follower_ids,
    }


def run_discovery(tracker: dict) -> list:
    """Call into sc_engagement to refresh discovery candidates."""
    sys.path.insert(0, str(BASE))
    from scene_intelligence import sc_engagement as sce
    eng_log = sce.load_eng_log()
    si_queue = sce.build_si_queue(eng_log)
    raw = sce.discover_related_artists(si_queue, tracker, eng_log)

    # Strip utm tracking from sc_url, return clean records
    clean = []
    for c in raw:
        url = (c.get("sc_url", "") or "").split("?")[0]
        permalink = url.rstrip("/").split("/")[-1] if url else ""
        clean.append({
            "name":        c.get("name", ""),
            "user_id":     c.get("user_id", ""),
            "sc_url":      url,
            "permalink":   permalink,
            "followers":   c.get("followers", 0),
            # Carried through so a candidate reused from an older file can be
            # re-validated against the track/recency filters without an API
            # call (added 2026-07-10).
            "track_count": c.get("track_count"),
            "last_upload_age_days": c.get("last_upload_age_days"),
            "tier":        c.get("tier", ""),
            "priority":    c.get("priority", 0),
            "source":      c.get("source", "discovery"),
        })
    clean.sort(key=lambda x: -x.get("priority", 0))
    return clean


def merge_candidates(existing: list, new: list) -> list:
    """Same-day runs append (2026-10-25, three hourly refreshes): keep every
    earlier candidate, add new user_ids, newest first within priority order."""
    seen = {str(c.get("user_id")) for c in new}
    merged = list(new) + [c for c in existing if str(c.get("user_id")) not in seen]
    merged.sort(key=lambda x: -x.get("priority", 0))
    return merged


def save_candidates(candidates: list) -> Path:
    """Save the candidate list to a date-stamped JSON file, merging with an
    earlier run of the same day."""
    today = date.today().strftime("%Y%m%d")
    path = BASE / "scene_intelligence" / f"discovery_candidates_{today}.json"
    runs = 1
    if path.exists():
        try:
            prev = json.loads(path.read_text(encoding="utf-8"))
            before = len(candidates)
            candidates = merge_candidates(prev.get("candidates", []), candidates)
            runs = int(prev.get("runs", 1)) + 1
            _log(f"  Same-day merge: {before} new + earlier runs = {len(candidates)} in today's file (run {runs})")
        except (OSError, ValueError):
            pass
    atomic_write_json(path, {
        "runs":             runs,
        "fetched_at":       date.today().isoformat(),
        "count":            len(candidates),
        "candidates":       candidates,
        "next_action_hint": (
            "Review names. Mark unwanted ones to skip. "
            "Then route follows through "
            "sc_engagement.py --log-action --action-type sc_follow ..."
        ),
    })
    return path


def save_audit(followings: list, followers: list) -> None:
    """Save a snapshot of the live following/follower state for offline use."""
    following_ids = {str(u["id"]) for u in followings if u.get("id")}
    follower_ids  = {str(u["id"]) for u in followers  if u.get("id")}
    atomic_write_json(AUDIT_FILE, {
        "fetched_at":      date.today().isoformat(),
        "total_following": len(following_ids),
        "total_followers": len(follower_ids),
        "mutual_count":    len(following_ids & follower_ids),
    })


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

FOLLOWER_BANDS = [(0, 100), (100, 300), (300, 600), (600, 1000),
                  (1000, 2000), (2000, 10**9)]
BAND_EXPERIMENT_START = "2026-07-03"   # 600-1000 experiment cohort start
BAND_MATURITY_DAYS = 14                # cohort entries younger than this are unripe


def _safe_followers(entry: dict) -> int:
    try:
        return int(entry.get("followers") or 0)
    except (TypeError, ValueError):
        return 0


def band_conversion_lines(follows: list[dict]) -> list[str]:
    """Follow-back-by-band markdown lines (SC-05, 2026-09-01).

    The 600-1000 experiment's own decision rule demanded this measurement
    'each health pass' (sc_engagement_config) but no report ever computed it —
    the 07-17 evaluation date passed unmeasured (audit F7). Two views: all
    time, and the experiment cohort (since 2026-07-03, mature >= 14 days).
    """
    mature_cut = (date.today() - timedelta(days=BAND_MATURITY_DAYS)).isoformat()
    cohort = [e for e in follows
              if BAND_EXPERIMENT_START <= (e.get("followed_at") or "") <= mature_cut]
    lines: list[str] = []
    for label, pool in (("all time", follows),
                        (f"since {BAND_EXPERIMENT_START}, mature ≥{BAND_MATURITY_DAYS}d", cohort)):
        lines.append(f"- _{label}:_")
        for lo, hi in FOLLOWER_BANDS:
            xs = [e for e in pool if lo <= _safe_followers(e) < hi]
            if not xs:
                continue
            b = sum(1 for e in xs if e.get("followed_back"))
            hi_label = f"{hi}" if hi < 10**9 else "+"
            lines.append(f"  - {lo}-{hi_label}: {b}/{len(xs)} ({100*b/len(xs):.0f}%)")
    return lines

def generate_report(
    tracker: dict,
    followings: list,
    followers: list,
    update_summary: dict,
    candidates: list,
) -> str:
    follows = tracker.get("follows", [])
    total = len(follows)
    fb_total = sum(1 for e in follows if e.get("followed_back"))
    today_iso = date.today().isoformat()
    active_unresolved = [
        e for e in follows
        if not e.get("followed_back") and not e.get("no_longer_following")
        and not e.get("keep_following")
    ]
    # Split honestly (SC-05): the old single "Pending (within 14-day window)"
    # counter never checked the window — 128 of its 157 were past it.
    pending_in_window = sum(1 for e in active_unresolved
                            if (e.get("unfollow_after") or "") > today_iso)
    overdue = len(active_unresolved) - pending_in_window
    keeps = sum(1 for e in follows if e.get("keep_following"))
    no_longer = sum(1 for e in follows if e.get("no_longer_following"))
    no_user_id = sum(1 for e in follows if not e.get("user_id"))

    by_month  = Counter()
    fb_month  = Counter()
    src_total = Counter()
    src_back  = Counter()
    for e in follows:
        d = e.get("followed_at", "")
        if d:
            month = d[:7]  # YYYY-MM
            by_month[month] += 1
            if e.get("followed_back"):
                fb_month[month] += 1
        s = e.get("source", "?")
        src_total[s] += 1
        if e.get("followed_back"):
            src_back[s] += 1

    following_ids = update_summary["following_ids"]
    follower_ids  = update_summary["follower_ids"]
    mutual = following_ids & follower_ids

    md: list[str] = []
    md.append(f"# SC Weekly Health Report -- {date.today().isoformat()}")
    md.append("")
    md.append("## Account")
    md.append(f"- Following: **{len(following_ids)}**")
    md.append(f"- Followers: **{len(follower_ids)}**")
    md.append(f"- Mutual: **{len(mutual)}**")
    try:
        from scene_intelligence.sc_engagement_config import GOAL_FOLLOWERS, GOAL_RATIO_FLOOR
    except ImportError:
        from sc_engagement_config import GOAL_FOLLOWERS, GOAL_RATIO_FLOOR
    ratio = len(follower_ids) / len(following_ids) if following_ids else 0
    nxt = next(((d, n) for d, n in sorted(GOAL_FOLLOWERS.items())
                if d >= date.today().isoformat()), None)
    if nxt:
        d, n = nxt
        md.append(f"- **Camp check:** {len(follower_ids)}/{n} followers toward {d} "
                  f"(gap {n - len(follower_ids)}) · ratio {ratio:.2f} vs floor {GOAL_RATIO_FLOOR}")
    md.append("")
    md.append("## Tracker")
    md.append(f"- Total entries: {total}")
    md.append(f"- Followed back: {fb_total} ({100 * fb_total / total:.0f}% of tracker)" if total else "- Followed back: 0")
    md.append(f"- Pending, still inside the 14-day window: {pending_in_window}")
    md.append(f"- Overdue for the U2 unfollow lane: {overdue}")
    md.append(f"- Explicit keeps (keep_following): {keeps}")
    md.append(f"- No longer following: {no_longer}")
    md.append(f"- Missing user_id: {no_user_id}  (resolved this run: {update_summary['user_ids_resolved']})")
    md.append("")
    md.append("## New follow-backs this week")
    if update_summary["new_followbacks"]:
        for n in update_summary["new_followbacks"]:
            md.append(f"- {n}")
    else:
        md.append("_None_")
    md.append("")
    churned = update_summary.get("reciprocator_churn", [])
    if churned:
        md.append("## ⚠ RECIPROCATOR CHURN DETECTED — tell Amir")
        md.append("Accounts that FOLLOWED US BACK are no longer in our followings "
                  "(we unfollowed a reciprocator, or a protected account was swept):")
        for n in churned:
            md.append(f"- **{n}**")
        md.append("")
    lost = update_summary.get("followback_lost", [])
    md.append("## Stopped following us back (G-03)")
    if update_summary.get("followback_lost_suspect"):
        md.append(f"_Skipped: {update_summary['followback_lost_suspect']} reciprocators looked lost "
                  "at once, more than the sanity share. Likely a partial follower fetch; nothing stamped._")
    elif lost:
        md.append("Followed us back before, not in our followers now (followback_lost_at stamped; "
                  "no longer used as seeds):")
        for n in lost:
            md.append(f"- {n}")
    else:
        md.append("_None_")
    regained = update_summary.get("followback_regained", [])
    if regained:
        md.append("Following us again: " + ", ".join(regained))
    md.append("")
    md.append("## Drift detected this run")
    if update_summary["drift_detected"]:
        md.append("Entries that are no longer in your followings list (you/SC unfollowed them):")
        for n in update_summary["drift_detected"]:
            md.append(f"- {n}")
    else:
        md.append("_None_")
    md.append("")
    md.append("## Follow-back rate by follower band")
    md.extend(band_conversion_lines(follows))
    md.append("")
    md.append("## Follow-back rate by source")
    for s in sorted(src_total):
        n = src_total[s]
        b = src_back[s]
        pct = 100 * b / n if n else 0
        md.append(f"- `{s}`: {b}/{n} ({pct:.0f}%)")
    md.append("")
    md.append("## Follow-back rate by month")
    for m in sorted(by_month):
        n = by_month[m]
        b = fb_month[m]
        pct = 100 * b / n if n else 0
        md.append(f"- {m}: {b}/{n} ({pct:.0f}%)")
    md.append("")
    md.append("## Discovery output this run")
    if candidates:
        md.append(f"- {len(candidates)} candidates")
        md.append("- Top 10 by priority:")
        for c in candidates[:10]:
            md.append(
                f"  - **{c.get('name','')}** "
                f"({c.get('followers',0)} followers) -- "
                f"{c.get('sc_url','')}"
            )
    else:
        md.append("_Discovery skipped or returned no candidates_")
    md.append("")
    md.append("## API budget")
    md.append(f"- Calls used: {_api_calls} / {API_BUDGET_HARD_CAP}")
    md.append("")
    md.append("---")
    md.append("Generated by `scene_intelligence/sc_weekly_health.py`. See [SOP](../sc-engagement-sop.md).")
    return "\n".join(md)


def save_report(report: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"sc-weekly-{date.today().strftime('%Y%m%d')}.md"
    path.write_text(report)
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    print(msg, flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute but don't write tracker/audit/report files.")
    parser.add_argument("--no-discovery", action="store_true",
                        help="Skip the discovery refresh step.")
    args = parser.parse_args()

    # SC-01 (2026-09-01): pauses.sc + SC detection cooldowns gate this run —
    # the whole script is API work.
    _standard_gates("sc")

    _log("=" * 60)
    _log(f"SC Weekly Health Check -- {date.today().isoformat()}")
    _log(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}"
         f"{' (no-discovery)' if args.no_discovery else ''}")
    _log("=" * 60)

    try:
        # Step 1: token + identity check
        _log("\n[1/5] Verifying SC_BROWSER_TOKEN...")
        me = verify_token()
        _log(f"  OK -- authenticated as {me.get('username')} (id={me.get('id')})")
        _log(f"  Followers: {me.get('followers_count')}, Following: {me.get('followings_count')}")

        # Step 2: fetch live lists
        _log("\n[2/5] Fetching live followings + followers...")
        followings, followers = fetch_lists()
        _log(f"  Followings: {len(followings)}")
        _log(f"  Followers:  {len(followers)}")

        # Step 3: update tracker
        _log("\n[3/5] Updating tracker (follow-backs, drift, user_id resolution)...")
        tracker = json.loads(TRACKER_FILE.read_text())
        update_summary = update_tracker(tracker, followings, followers, args.dry_run)
        _log(f"  New follow-backs:     {len(update_summary['new_followbacks'])}")
        _log(f"  Drift detected:       {len(update_summary['drift_detected'])}")
        _log(f"  user_ids resolved:    {update_summary['user_ids_resolved']}")
        _log(f"  Stopped following back: {len(update_summary['followback_lost'])}"
             + (f" (SKIPPED, {update_summary['followback_lost_suspect']} looked lost: partial fetch?)"
                if update_summary.get('followback_lost_suspect') else ""))
        if update_summary.get("reciprocator_churn"):
            _log("  " + "!" * 56)
            _log(f"  RECIPROCATOR CHURN: {update_summary['reciprocator_churn']}")
            _log("  A followed-back account left our followings. Tell Amir NOW.")
            _log("  " + "!" * 56)

        if not args.dry_run:
            atomic_write_json(TRACKER_FILE, tracker)   # tmp+rename (SC-05)
            save_audit(followings, followers)

        # Step 4: discovery refresh
        candidates: list = []
        if not args.no_discovery:
            _log("\n[4/5] Running discovery refresh...")
            candidates = run_discovery(tracker)
            _log(f"  Discovered: {len(candidates)} candidates")
            if candidates and not args.dry_run:
                path = save_candidates(candidates)
                _log(f"  Saved -> {path.relative_to(BASE)}")
        else:
            _log("\n[4/5] Discovery skipped (--no-discovery)")

        # Step 5: report
        _log("\n[5/5] Generating report...")
        report = generate_report(tracker, followings, followers, update_summary, candidates)
        if not args.dry_run:
            report_path = save_report(report)
            _log(f"  Saved -> {report_path.relative_to(BASE)}")

        _log("\n" + "=" * 60)
        _log(f"SUCCESS. API calls used: {_api_calls} / {API_BUDGET_HARD_CAP}")
        _log("=" * 60)
        return 0

    except TokenExpired as e:
        _log("\nSTOP: token expired or invalid.")
        _log(f"  {e}")
        return 1
    except CaptchaTriggered as e:
        _log("\nSTOP: CAPTCHA detected.")
        _log(f"  {e}")
        return 2
    except APIBudgetExceeded as e:
        _log("\nSTOP: API budget exceeded.")
        _log(f"  {e}")
        return 3
    except HealthCheckError as e:
        _log("\nSTOP: health check error.")
        _log(f"  {e}")
        return 4


if __name__ == "__main__":
    sys.exit(main())
