"""
ig_audit_queue_freshness.py
----------------------------
Pre-engagement queue audit. Verifies that pending Reach candidates in
ig_target_list.json have posted recently enough to pass the 21-day Reach
filter at runtime.

Why this exists:
  The queue builder (ig_queue_builder.py) crawls follower lists but doesn't
  capture last_post_date per candidate. Candidates can be active when
  crawled and dormant by the time CC tries to engage. Sessions hit
  filter_failed_at_runtime skips → eventually trip the circuit breaker.

  This script pre-filters the queue: pulls profile metadata for the next
  N pending entries, checks each one's most recent post timestamp, and
  marks stale candidates as status="skipped_stale" so CC's next session
  walks past them.

Run BEFORE the next engagement session, ideally one day in advance so the
script + engagement don't burn the same daily IG slot:

  python3 scene_intelligence/ig_audit_queue_freshness.py             # audit next 25
  python3 scene_intelligence/ig_audit_queue_freshness.py --count 50  # audit next 50
  python3 scene_intelligence/ig_audit_queue_freshness.py --dry-run   # preview, no writes

Each profile fetch is one IG API call (web_profile_info endpoint). Default
audit of 25 entries = 25 calls, well under the 150-per-session safety cap.

Credentials: reads IG_SESSION_ID, IG_CSRF_TOKEN from .env (same as
ig_followback_checker.py and ig_live_driver.py).
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env"
SI_DIR = BASE_DIR / "scene_intelligence"
QUEUE_FILE = SI_DIR / "ig_target_list.json"

IG_APP_ID = "936619743392459"
IG_API_BASE = "https://www.instagram.com/api/v1"
IG_WEB = "https://www.instagram.com"

def _recency_from_config(default: int = 30) -> int:
    """One law: the engine's REACH["max_post_recency_days"] (60 since 2026-09-11).
    A hardcoded 30 here would mark 31-60-day candidates stale that the engine accepts."""
    try:
        try:
            from scene_intelligence import ig_engagement_config as cfg
        except ImportError:
            import ig_engagement_config as cfg
        return int((getattr(cfg, "REACH", {}) or {}).get("max_post_recency_days", default))
    except Exception:
        return default


REACH_MAX_POST_AGE_DAYS = _recency_from_config()

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


def _load_credentials() -> tuple[str, str]:
    load_dotenv(ENV_FILE)
    sid = os.getenv("IG_SESSION_ID", "").strip()
    csrf = os.getenv("IG_CSRF_TOKEN", "").strip()
    if not sid or not csrf:
        raise SystemExit(
            "\n[AUDIT] Missing IG_SESSION_ID or IG_CSRF_TOKEN in .env.\n"
            "Refresh with: python3 scene_intelligence/ig_live_driver.py --extract-cookies\n"
        )
    return sid, csrf


_PROVIDER = None  # set in audit() when the provider is available


def _provider_fetch_profile(username: str) -> Optional[dict]:
    """Provider path (2026-09-14): returns the legacy data.user body shape."""
    try:
        from scene_intelligence.ig_data_provider import legacy_user_body, ProviderError
    except ImportError:
        from ig_data_provider import legacy_user_body, ProviderError
    try:
        prof = _PROVIDER.profile(username)
    except ProviderError as exc:
        print(f"  [PROVIDER ERROR] @{username}: {exc}", file=sys.stderr)
        return None
    return legacy_user_body(prof) if prof else None


def _provider_fetch_feed(user_id: str, count: int = 3) -> Optional[list]:
    try:
        from scene_intelligence.ig_data_provider import ProviderError
    except ImportError:
        from ig_data_provider import ProviderError
    try:
        ep = _PROVIDER.newest_post_epoch(user_id, amount=count)
    except ProviderError as exc:
        print(f"  [PROVIDER ERROR] feed {user_id}: {exc}", file=sys.stderr)
        return None
    return [{"taken_at": ep}] if ep else []


def _fetch_profile(session: requests.Session, username: str) -> Optional[dict]:
    if _PROVIDER is not None:
        return _provider_fetch_profile(username)
    """
    GET /api/v1/users/web_profile_info/?username={username}
    Returns the parsed JSON body on success, None on failure.
    """
    url = f"{IG_API_BASE}/users/web_profile_info/"
    try:
        r = session.get(
            url,
            params={"username": username},
            headers={"Referer": f"{IG_WEB}/{username}/"},
            timeout=15,
        )
    except requests.RequestException as exc:
        print(f"  [NET ERROR] @{username}: {exc}", file=sys.stderr)
        return None

    if r.status_code == 401:
        raise SystemExit("[AUDIT] Session expired (HTTP 401). Re-extract cookies.")
    if r.status_code == 429:
        _rate_limited("profile read")
    if r.status_code != 200:
        print(f"  [HTTP {r.status_code}] @{username}", file=sys.stderr)
        return None

    try:
        return r.json()
    except ValueError:
        print(f"  [JSON ERROR] @{username}", file=sys.stderr)
        return None


def _fetch_user_feed(session: requests.Session, user_id: str, count: int = 3) -> Optional[list]:
    if _PROVIDER is not None:
        return _provider_fetch_feed(user_id, count)
    """
    GET /api/v1/feed/user/<user_id>/?count=<n>
    Returns the list of recent posts (each with taken_at epoch seconds).
    Discovered 2026-06-08: this private API still returns taken_at after
    IG stripped timestamps from web_profile_info on 2026-06-03. One extra
    call per audit candidate but restores real recency filtering.
    """
    url = f"{IG_API_BASE}/feed/user/{user_id}/"
    try:
        r = session.get(
            url,
            params={"count": str(count)},
            headers={"Referer": f"{IG_WEB}/"},
            timeout=15,
        )
    except requests.RequestException as exc:
        print(f"  [FEED NET ERROR] user_id={user_id}: {exc}", file=sys.stderr)
        return None
    if r.status_code == 401:
        raise SystemExit("[AUDIT] Session expired (HTTP 401). Re-extract cookies.")
    if r.status_code == 429:
        _rate_limited("profile read")
    if r.status_code != 200:
        return None
    try:
        body = r.json()
    except ValueError:
        return None
    items = body.get("items") or []
    return items if isinstance(items, list) else None


# Scene-relevance keyword lists (designed 2026-06-09 from observed bios).
# Strong positives capture explicit scene markers. Strong negatives kill
# accounts the queue builder shouldn't have surfaced (pizza shops, gaming,
# real estate). The classifier scores the bio + username + full_name and
# returns a numeric relevance score plus the matched signals for logging.

_REL_STRONG_POS = (
    # Roles
    "dj ", "/dj", "dj/", " dj ", "producer", "label", "records", "recordings",
    "vinyl", "selector", "selecta", "remix", "remixer", "punk",
    # Genres the artist cares about
    "techno", "house ", "electro", "ebm", "industrial", "darkwave",
    "coldwave", "post-punk", "postpunk", "post punk", "minimal wave",
    "minimalwave", "disco", "dark disco", "italo", "synthwave", "synth",
    "ambient", "acid", "trance", "psytrance", "downtempo", "dub techno",
    "deep house", "rave", "electroclash", "new beat", "breakbeat",
    "drum and bass", "drum & bass", "dnb", "body music", "ebmusic",
    # Music infrastructure / clout
    "soundcloud.com", "bandcamp.com", "beatport.com", "spotify.com/artist",
    "boilerroom", "boiler room", "residency", "resident @", "resident at",
    "booking:", "bookings:", "bookings@", "booking @", "demo:", "demos:",
    "release", "released", "ep out", "lp out", "out now",
    "radio show", "@radio", ".radio", "_radio", "radio ",
    "club ", "@club", "festival", "promoter",
    # Sound-design / music-adjacent
    "sound design", "sounddesign", "composing", "composer",
    "track ", "tracks", "mixtape", "mixtapes",
)
# Israeli/Hebrew signals -- SOP excludes these per artist preference.
# Strong signal: any of these → fail outright.
_REL_ISRAEL_NEG = (
    "🇮🇱",
    "tel aviv", "telaviv", "haifa", " idf", "israel", "israeli",
    # Common Hebrew name endings + handle patterns
    "shir.", "shir_", "_shir", "_yael", "_yaeli", "ofir",
)
_REL_WEAK_POS = (
    "music", "sound", "mix ", "beats", "track", "electronic",
    "audio", "synth", "groovebox", "drum machine", "modular",
    "composer", "performer", "live act",
)
# Visual/creative roles that orbit the scene but aren't peer artists to
# follow (added 2026-06-17 after @verridavide, a music-event photographer,
# passed Reach screening on the weak "music" signal alone). Moderate negative:
# a real music-MAKER signal (+2 strong-pos) still outweighs it, but a
# photographer/videographer with only incidental music words now fails.
_REL_SOFT_NEG = (
    "photographer", "photography", "videographer", "visual artist",
    "graphic designer", "illustrator", "tattoo artist", "model ",
)
_REL_STRONG_NEG = (
    # Food/delivery
    "pizza", "delivery", "menu", "garlic", "DM to order", "dm to order",
    "restaurant", "cafe", "kitchen", "chef",
    # Adult/modeling
    "fetish", "nsfw", "onlyfans", "nude", "naughty",
    # Gaming
    "video game", "gaming", "gamer", "twitch.tv", "esports",
    # Random business
    "real estate", "realtor", "agent.com", "marketing agency",
    "social media manager", "personal trainer", "fitness coach",
    "weight loss", "crypto", "nft", "trading", "forex",
    # Personal lifestyle (not scene)
    "yoga teacher", "wellness coach",
)

def _score_scene_relevance(user: dict) -> tuple[int, str, list[str]]:
    """Return (score, verdict, matched_signals) for a profile's scene-relevance.
    verdict: 'pass' | 'fail' | 'unknown'.
    Threshold: score >= 1 = pass (any positive, no strong negative).
    Empty/no-signal bios → 'unknown' so audit doesn't auto-fail them."""
    bio = (user.get("biography") or "").lower()
    username = (user.get("username") or "").lower()
    full_name = (user.get("full_name") or "").lower()
    haystack = " ".join([bio, username, full_name])

    score = 0
    hits = []

    # Hebrew character check (any char in Hebrew Unicode block) → strong neg
    if any("֐" <= ch <= "׿" for ch in (bio + full_name)):
        score -= 20
        hits.append("-hebrew_chars")

    for kw in _REL_ISRAEL_NEG:
        if kw in haystack:
            score -= 20
            hits.append(f"-{kw}")

    for kw in _REL_STRONG_NEG:
        if kw in haystack:
            score -= 5
            hits.append(f"-{kw}")

    for kw in _REL_SOFT_NEG:
        if kw in haystack:
            score -= 3
            hits.append(f"-{kw.strip()}")

    for kw in _REL_STRONG_POS:
        if kw in haystack:
            score += 2
            hits.append(f"+{kw.strip()}")

    for kw in _REL_WEAK_POS:
        if kw in haystack:
            score += 1
            hits.append(f"~{kw.strip()}")

    # Empty bio is unknown -- don't reject
    if not bio.strip() and not full_name:
        return 0, "unknown", []
    if score >= 1:
        return score, "pass", hits
    if score < 0:
        return score, "fail", hits
    # Score = 0 with bio content but no signal: unknown (e.g. tact0001 art bio)
    return score, "unknown", hits


def _walk_for_user(profile_body: dict) -> Optional[dict]:
    """Find the 'user' dict in the response. IG has used multiple wrappers
    over the years: data.user, user, graphql.user, etc."""
    if not isinstance(profile_body, dict):
        return None
    for path in (
        ("data", "user"),
        ("user",),
        ("graphql", "user"),
        ("data", "graphql", "user"),
    ):
        node = profile_body
        ok = True
        for k in path:
            if isinstance(node, dict) and k in node:
                node = node[k]
            else:
                ok = False
                break
        if ok and isinstance(node, dict):
            return node
    return None


def _walk_for_timestamps(user: dict) -> list[float]:
    """Pull all taken_at timestamps from any media-list shape IG might return.
    Tries the legacy edge_owner_to_timeline_media first, then several known
    fallback shapes (recent_media, feed, items[], etc.)."""
    timestamps: list[float] = []

    # Legacy path: edge_owner_to_timeline_media.edges[].node.taken_at_timestamp
    edges = user.get("edge_owner_to_timeline_media", {}).get("edges", []) if isinstance(user.get("edge_owner_to_timeline_media"), dict) else []
    for e in edges:
        ts = e.get("node", {}).get("taken_at_timestamp") if isinstance(e, dict) else None
        if isinstance(ts, (int, float)):
            timestamps.append(float(ts))

    # Newer shape: timeline_media.edges
    if not timestamps:
        edges = user.get("timeline_media", {}).get("edges", []) if isinstance(user.get("timeline_media"), dict) else []
        for e in edges:
            ts = e.get("node", {}).get("taken_at_timestamp") if isinstance(e, dict) else None
            if isinstance(ts, (int, float)):
                timestamps.append(float(ts))

    # API v1 private shape: items[] directly with taken_at (epoch seconds)
    if not timestamps:
        items = user.get("items", []) or user.get("feed", {}).get("items", []) if isinstance(user.get("feed"), dict) else user.get("items", [])
        if isinstance(items, list):
            for it in items:
                if not isinstance(it, dict):
                    continue
                ts = it.get("taken_at") or it.get("taken_at_timestamp")
                if isinstance(ts, (int, float)):
                    timestamps.append(float(ts))

    # latest_reel_media at user level (single int)
    if not timestamps:
        ts = user.get("latest_reel_media")
        if isinstance(ts, (int, float)) and ts > 0:
            timestamps.append(float(ts))

    return timestamps


def _extract_last_post_age_days(profile_body: dict, debug: bool = False) -> Optional[int]:
    """
    Walk the JSON to find the most-recent post's taken_at_timestamp,
    return age in days. Returns None if profile is private (no media
    visible), has no posts, or structure is unexpected. Returns -1 if
    the profile is private (sentinel).
    """
    user = _walk_for_user(profile_body)
    if user is None:
        if debug:
            top_keys = list(profile_body.keys()) if isinstance(profile_body, dict) else type(profile_body).__name__
            print(f"    [DEBUG] no user found; top-level keys: {top_keys}", file=sys.stderr)
        return None

    if user.get("is_private") is True:
        return -1

    timestamps = _walk_for_timestamps(user)
    if not timestamps:
        if debug:
            print(f"    [DEBUG] user found but no timestamps; user keys: {list(user.keys())[:20]}", file=sys.stderr)
        return None

    newest_ts = max(timestamps)
    now_ts = datetime.now(timezone.utc).timestamp()
    return int((now_ts - newest_ts) / 86400)


def audit(count: int, dry_run: bool, max_age: int, debug: bool = False) -> int:
    if not QUEUE_FILE.exists():
        print(f"[AUDIT] Queue file not found: {QUEUE_FILE}", file=sys.stderr)
        return 1

    queue_data = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    queue = queue_data.get("queue", [])
    pending = [q for q in queue if q.get("status") == "pending"]
    if not pending:
        print("[AUDIT] No pending entries to audit.")
        return 0

    # VALUE-FIRST SELECTION (2026-09-01): plain file order audited the OLDEST
    # entries first, and the builder appends new candidates at the END — so
    # the 23 fresh multi-seed candidates from the 09-01 seed refresh sat
    # behind 745 stale unaudited entries (~12 weeks of runs away) while
    # REACH_VETTED_ONLY kept them out of every session. Audit the likeliest
    # converters first instead: highest seed overlap, then newest position.
    order = {id(e): i for i, e in enumerate(pending)}
    targets = sorted(
        pending,
        key=lambda e: (-int(e.get("seed_count") or 1), -order[id(e)]),
    )[:count]
    print(f"=== Queue Freshness Audit  [{date.today()}] ===")
    print(f"Pending entries to audit: {len(targets)} (of {len(pending)} total pending)")
    print(f"Reach freshness threshold: ≤{max_age} days since last post")
    print(f"Dry run: {dry_run}\n")

    if _PROVIDER is not None:
        session = None  # every read goes through the provider
    else:
        sid, csrf = _load_credentials()
        session = _build_session(sid, csrf)
    today = date.today().isoformat()

    fresh = []
    stale = []
    private = []
    no_data = []
    errors = []
    retired = []

    # 2.0 law (T-003): consecutive-error breaker. On 2026-08-27 a 16-long
    # 400/404 streak burned calls into a suspected endpoint throttle because
    # nothing stopped the loop. Five consecutive failed fetches now abort the
    # run (partial results still persist below). Entries that fail across
    # THREE separate audits are retired from re-fetching for good (the six
    # documented perma-400 accounts kept getting re-spent).
    CONSECUTIVE_FAIL_BREAKER = 5
    PERMA_FAIL_RETIRE_AT = 3
    consec_fail = 0
    breaker_tripped = False

    # 2026-06-08 RECENCY RESTORED: web_profile_info no longer returns timestamps
    # (IG change on 2026-06-03), but /api/v1/feed/user/<id>/?count=3 still does.
    # Two calls per candidate (~2x cost) but restores real recency filtering.
    # This closed the gap that caused 0/8 follows on the Monday 2026-06-08
    # session: audit said candidates were healthy, runtime failed them on
    # last-post-recency.
    min_f = 200
    max_f = 2500
    min_posts = 12
    import time as _t  # local; ensures availability in datetime conversion below
    from datetime import datetime as _dt

    for i, entry in enumerate(targets, 1):
        h = entry.get("username", "")
        if not h:
            errors.append((h, "empty_username"))
            continue

        print(f"  [{i:2d}/{len(targets)}] checking @{h}...", end=" ", flush=True)
        body = _fetch_profile(session, h)
        if not body:
            errors.append((h, "fetch_failed"))
            consec_fail += 1
            if not dry_run:
                entry["fetch_fail_count"] = int(entry.get("fetch_fail_count", 0)) + 1
                if entry["fetch_fail_count"] >= PERMA_FAIL_RETIRE_AT:
                    entry["status"] = "retired_fetch_error"
                    entry["skipped_reason"] = (
                        f"fetch_failed_{entry['fetch_fail_count']}_audits")
                    entry["skipped_date"] = today
                    retired.append(h)
                    print(f"ERROR -> retired ({entry['fetch_fail_count']} audits)")
                else:
                    print("ERROR")
            else:
                print("ERROR")
            if consec_fail >= CONSECUTIVE_FAIL_BREAKER:
                breaker_tripped = True
                print(f"\n[BREAKER] {consec_fail} consecutive failed fetches — "
                      f"aborting the run (possible endpoint throttle, "
                      f"2026-08-27 class). Partial results are persisted; "
                      f"no further API calls today.")
                break
            time.sleep(0.2 if _PROVIDER is not None else random.uniform(3, 6))
            continue
        consec_fail = 0
        if entry.get("fetch_fail_count"):
            entry.pop("fetch_fail_count", None)  # recovered

        # Debug: save raw response from the FIRST candidate
        if debug and i == 1:
            raw_dump = SI_DIR / f"audit_raw_first_response_{date.today()}.json"
            raw_dump.write_text(json.dumps(body, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"\n    [DEBUG] raw response saved to {raw_dump.name}", file=sys.stderr)

        user = _walk_for_user(body)
        if not user:
            no_data.append(h)
            print("no user data")
            time.sleep(0.2 if _PROVIDER is not None else random.uniform(3, 7))
            continue

        followers = (user.get("edge_followed_by") or {}).get("count")
        following = (user.get("edge_follow") or {}).get("count")
        posts_count = (user.get("edge_owner_to_timeline_media") or {}).get("count")
        is_private = bool(user.get("is_private"))
        is_verified = bool(user.get("is_verified"))
        bio = user.get("biography") or ""

        # Enrich queue entry with profile data (engine's has_ig_data filter
        # will then apply at plan time)
        if not dry_run:
            if followers is not None:
                entry["ig_followers"] = int(followers)
            if following is not None:
                entry["ig_following"] = int(following)
            if posts_count is not None:
                entry["ig_posts"] = int(posts_count)
            entry["ig_is_private"] = is_private
            entry["ig_is_verified"] = is_verified
            if bio:
                entry["ig_bio"] = bio
            entry["audit_date"] = today

        # Classify by what the engine would reject this entry as
        if is_private:
            private.append(h)
            print(f"PRIVATE -> mark stale")
            if not dry_run:
                entry["status"] = "skipped_stale"
                entry["skipped_reason"] = "private_account"
                entry["skipped_date"] = today
        elif followers is None or posts_count is None:
            no_data.append(h)
            print("missing counts")
        elif followers < min_f:
            stale.append((h, f"followers={followers}<{min_f}"))
            print(f"stale (followers={followers}<{min_f})")
            if not dry_run:
                entry["status"] = "skipped_stale"
                entry["skipped_reason"] = f"followers_too_low:{followers}"
                entry["skipped_date"] = today
        elif followers > max_f:
            stale.append((h, f"followers={followers}>{max_f}"))
            print(f"stale (followers={followers}>{max_f})")
            if not dry_run:
                entry["status"] = "skipped_stale"
                entry["skipped_reason"] = f"followers_too_high:{followers}"
                entry["skipped_date"] = today
        elif posts_count < min_posts:
            stale.append((h, f"posts={posts_count}<{min_posts}"))
            print(f"stale (posts={posts_count}<{min_posts})")
            if not dry_run:
                entry["status"] = "skipped_stale"
                entry["skipped_reason"] = f"posts_too_few:{posts_count}"
                entry["skipped_date"] = today
        elif is_verified:
            stale.append((h, "verified"))
            print(f"stale (verified)")
            if not dry_run:
                entry["status"] = "skipped_stale"
                entry["skipped_reason"] = "verified"
                entry["skipped_date"] = today
        else:
            # All static-metric filters passed; now check scene-relevance via
            # bio/name/username keyword scoring (NO extra IG call -- uses data
            # we already have). Reject obvious negatives (pizza shops, gaming,
            # fetish, etc.) before spending a recency call on them.
            rel_score, rel_verdict, rel_hits = _score_scene_relevance(user)
            if not dry_run:
                entry["ig_scene_relevance_score"] = rel_score
                entry["ig_scene_relevance_verdict"] = rel_verdict
                if rel_hits:
                    entry["ig_scene_relevance_signals"] = rel_hits[:8]
            if rel_verdict == "fail":
                stale.append((h, f"not_scene_relevant({rel_score})"))
                print(f"stale (not_scene_relevant: {', '.join(rel_hits[:3])})")
                if not dry_run:
                    entry["status"] = "skipped_stale"
                    entry["skipped_reason"] = f"not_scene_relevant:{rel_score}"
                    entry["skipped_date"] = today
                time.sleep(0.2 if _PROVIDER is not None else random.uniform(3, 7))
                continue

            # Relevance pass or unknown; proceed to recency via feed endpoint.
            user_id = user.get("id") or user.get("pk")
            last_post_age_days = None
            if user_id:
                # Brief pause before the second call to look human
                time.sleep(0.2 if _PROVIDER is not None else random.uniform(2, 4))
                items = _fetch_user_feed(session, str(user_id), count=3)
                if items:
                    taken_ats = [it.get("taken_at") for it in items if isinstance(it, dict) and isinstance(it.get("taken_at"), (int, float))]
                    if taken_ats:
                        newest = max(taken_ats)
                        last_post_age_days = int((_t.time() - newest) / 86400)

            if not dry_run and last_post_age_days is not None:
                entry["ig_last_post_age_days"] = last_post_age_days
                entry["ig_last_post_checked_at"] = today

            if last_post_age_days is None:
                # Feed lookup failed -- keep pending but mark unknown so the
                # engine can choose to skip these as a fallback.
                fresh.append((h, f"{followers}f/{posts_count}p / recency=?"))
                print(f"fresh ({followers}f/{posts_count}p) -- recency unknown, kept pending")
            elif last_post_age_days > max_age:
                stale.append((h, f"last_post={last_post_age_days}d>{max_age}"))
                print(f"stale (last_post={last_post_age_days}d > {max_age}d)")
                if not dry_run:
                    entry["status"] = "skipped_stale"
                    entry["skipped_reason"] = f"last_post_too_old:{last_post_age_days}d"
                    entry["skipped_date"] = today
            else:
                fresh.append((h, f"{followers}f/{posts_count}p/{last_post_age_days}d"))
                print(f"fresh ({followers}f/{posts_count}p, last post {last_post_age_days}d ago) -- kept pending")

        # Pause between requests
        time.sleep(0.2 if _PROVIDER is not None else random.uniform(3, 7))

    print()
    print("=== Audit Summary ===")
    print(f"  Fresh (kept pending):     {len(fresh)}")
    print(f"  Stale (marked skipped):   {len(stale)}")
    print(f"  Private accounts:         {len(private)}")
    print(f"  No post data:             {len(no_data)}")
    print(f"  Fetch errors:             {len(errors)}")
    print(f"  Retired (perma-error):    {len(retired)}")
    if breaker_tripped:
        print(f"  BREAKER: run aborted on consecutive failures")

    if stale:
        print(f"\n  Stale handles flagged as skipped_stale:")
        for h, age in stale:
            print(f"    - @{h} ({age}d since last post)")

    if not dry_run:
        # 2.0 fix: ALWAYS persist (atomically). The old `and stale` condition
        # threw away every enrichment field + fail counts on a zero-stale run
        # (review second-tier finding).
        queue_data["_meta"]["last_freshness_audit"] = today
        try:
            from scene_intelligence.json_io import atomic_write_json
        except ImportError:
            from json_io import atomic_write_json
        atomic_write_json(QUEUE_FILE, queue_data)
        print(f"\n[OK] Queue updated. {len(stale)} stale, {len(retired)} "
              f"retired, {len(fresh)} fresh enriched.")
    else:
        print(f"\n[DRY-RUN] No queue writes. {len(stale)} entries would be marked stale.")

    return 0



def _rate_limited(where: str):
    """2026-09-11: record the 429 so tomorrow's dispatcher is gated, then stop."""
    try:
        try:
            from scene_intelligence.ig_ops_guards import record_detection
        except ImportError:
            from ig_ops_guards import record_detection
        record_detection("instagram", "rate_limited_429_profile_reads",
                         f"HTTP 429 during the audit ({where}); recorded automatically")
    except Exception as exc:  # never let bookkeeping hide the stop
        print(f"[AUDIT] could not record the detection event: {exc}")
    raise SystemExit(f"[AUDIT] Rate-limited (HTTP 429). Recorded; cooldown gate now blocks the next run.")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--count", type=int, default=25,
                   help="How many pending entries to audit (default: 25)")
    p.add_argument("--dry-run", action="store_true",
                   help="Preview audit results without modifying the queue")
    p.add_argument("--max-age", type=int, default=REACH_MAX_POST_AGE_DAYS,
                   help=f"Max post age in days (default: {REACH_MAX_POST_AGE_DAYS})")
    p.add_argument("--debug", action="store_true",
                   help="Save raw response from first profile to disk + print "
                        "diagnostic info when parser can't find media (use this "
                        "if all candidates return 'no posts / no data')")
    try:
        from scene_intelligence.ig_daily_ledger import add_ledger_argument, check_and_claim
    except ImportError:
        from ig_daily_ledger import add_ledger_argument, check_and_claim
    add_ledger_argument(p)
    args = p.parse_args()
    # 2.0 law (T-003): hard gates first; claim carries the run's call budget
    # (~1 call per audited entry, profile_reads capped at 30/day — the
    # 2026-08-27 streak showed ~50 consecutive reads is throttle territory).
    global _PROVIDER
    try:
        from scene_intelligence import ig_engagement_config as _cfg
        from scene_intelligence.ig_data_provider import available as _prov_available, Provider
        from scene_intelligence.ig_ops_guards import standard_gates, get_pause, blocks_api_jobs
    except ImportError:
        import ig_engagement_config as _cfg
        from ig_data_provider import available as _prov_available, Provider
        from ig_ops_guards import standard_gates, get_pause, blocks_api_jobs
    if _prov_available():
        # Provider path (2026-09-14): pause still respected; IG cooldown and
        # timing law do not apply (nothing here touches Instagram as Amir).
        pause = get_pause("ig")
        if pause and blocks_api_jobs(pause):
            raise SystemExit("[AUDIT] IG automation is paused (scope: all). Nothing runs.")
        check_and_claim("ig_audit_queue_freshness", kind="provider",
                        est_calls=2 * int(args.count), endpoint="provider_profile+media")
        _PROVIDER = Provider(sleep=0.3)
        print("[AUDIT] provider mode: reads via HikerAPI, Instagram never contacted as Amir")
    else:
        if not getattr(_cfg, "IG_DIRECT_API_ENABLED", True):
            raise SystemExit("[AUDIT] Direct Instagram reads are OFF (config "
                             "IG_DIRECT_API_ENABLED=False) and no HIKERAPI_KEY in .env. "
                             "Nothing runs.")
        standard_gates("ig")
        check_and_claim("ig_audit_queue_freshness", override=args.override_ledger,
                        reason=getattr(args, 'override_reason', None),
                        est_calls=int(args.count), endpoint="profile_reads")
    return audit(args.count, args.dry_run, args.max_age, debug=args.debug)


if __name__ == "__main__":
    sys.exit(main())
