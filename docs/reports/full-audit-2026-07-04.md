# Full Repository Audit - 2026-07-04

**Scope:** entire working tree (91 Python files, ~33k lines, 16 templates, 2 JS bundles, 9 skills, 3 agent definitions, all SOP docs, data files, git hygiene).
**Method:** 12 parallel domain auditors (risk-weighted: IG/SC live automation and webapp security got the deepest pass), followed by adversarial verification of every critical/high finding by an independent agent instructed to refute it, and a completeness critic hunting for gaps. All auditors were read-only; no live API, browser, or engagement script was executed.
**Results:** 185 findings. 21 critical/high adversarially verified: all 21 confirmed, 0 refuted. 112 medium/low findings are single-auditor (code evidence required but not independently verified). 52 are improvement/doc-drift items. Fixes are NOT applied; this is a findings report.

## Executive Summary

The webapp, secrets hygiene, and release tooling came out in decent shape: no hardcoded credentials anywhere, `.gitignore` covers every secret-bearing file on disk, Flask binds to 127.0.0.1 with CSRF enabled, subprocess calls use list args, and the tests pass. The serious problems cluster in exactly one place: **the live IG/SC engagement automation, where most of the documented hard rules exist only as prose and were never implemented in code.** The fixes deferred from the 2026-06-12 automation review never landed.

The five themes:

1. **Hard rules without machine enforcement.** "Never 2 IG scripts same day" - not enforced anywhere (the engine writes `last_session` but nothing ever reads it, and five support scripts hit the IG API with no shared ledger). The 48-72h post-detection cooldown - `PAUSE_AFTER_*` config values are dead, referenced by zero code. Blocked-accounts and personal-network lists - never consulted by the SC engine at all. `no_longer_engage` - the flag exists in data but no Python file reads it.

2. **The own-label rule is already being violated.** The SC engine liked mm.discos twice (2026-05-09 and 2026-05-23, in the engagement log), both released-on labels remain eligible like/repost targets on every run, and mm.discos currently qualifies for the Sunday unfollow sweep because the candidate filter (in code AND in both SOP docs) never checks `no_longer_engage`. On the IG side, none of the own-label handles are in `ig_blocked_accounts.json`, so they can enter the follow queue via seed overlap.

3. **Unbounded/unconfirmed actions.** The one CRITICAL: the SC unfollow sweep has no session cap, no circuit-breaker check, and no delay between failed calls - 271 candidates qualify today, so one default live run would attempt 271 authenticated writes (the May-03 incident triggered CAPTCHA after 3). IG follows and unfollows are logged as successful without checking Instagram's response, corrupting the tracker with phantom entries and ghost follows.

4. **Data-integrity landmines.** Every shared JSON (follow trackers, engagement log, the 938-contact SI database, releases) is written non-atomically, and the trackers fall back to silently EMPTY state on a corrupt file - one interrupted write erases all follow history, the re-follow banlist, and today's cap counters. `enrich_contacts.py` and `classify_subtypes.py` will each destroy hours of curation if run once (both are listed as routine commands). Sheets sync-back reverts local edits to stale Sheet values for four fields (only score is protected).

5. **The scheduling layer was the audit's biggest blind spot (caught by the critic).** `scene_intelligence/run_ig_session.sh` (tracked in git, one `launchctl load` from active) runs the IG engine `--live --no-preflight`, bypassing every gate. An installed launchd agent runs `sc_weekly_health.py` unattended twice a week (currently failing, exit 2), making un-preannounced SC API calls. And `.claude/settings.local.json` auto-approves arbitrary `python3 -c` execution.

## Recommended Fix Order

**P0 - before the next automation session (the Sunday sweep is the nearest hazard):**
1. Unfollow sweep: skip `no_longer_engage`/`no_longer_following` entries, cap at 15/session, check the circuit breaker inside the loop, delay on failures (findings 1, 10, 14 - code + both SOP docs + CC task body).
2. Data fix, 5 minutes: add own-label IG handles to `ig_blocked_accounts.json`; set `no_longer_engage` on mm.discos and Stereo Society SI records and make `build_si_queue`/`build_promo_queue` honor it (findings 7, 9).
3. Decide the fate of `run_ig_session.sh` + its plist: delete from the repo or strip `--no-preflight` (critic gap).

**P1 - account safety (IG side):**
4. Same-day guard + PAUSE_AFTER cooldown enforcement in `preflight()`, honored even with `--no-preflight` on live runs (findings 2, 3).
5. Confirm follows/unfollows from the API response before mutating the tracker, mirroring the fixed likes path (findings 4, 5).
6. Session-identity verification: `build_live_driver()` must verify the session belongs to inch_of_shadow before acting; SC cookie extractor must abort instead of falling back to the most-cookies profile (findings 19, 13).
7. Shared IG daily ledger consulted by all five API-calling support scripts (finding 8); circuit-breaker check in the SC reposts pass (finding 11).

**P2 - data integrity:**
8. Atomic writes (temp file + os.replace) for all shared JSON; abort loudly on corrupt files instead of returning empty state (finding 12 + mediums in webapp/storage/push_to_sheets/stats).
9. Guards on `enrich_contacts.py` (refuse if output exists, require --force-rebuild, backup first) and `classify_subtypes.py` (never blank an existing sub_type) (findings 15, 16).
10. Sync-back: per-field locks or last-pushed snapshot comparison (finding 17).

**P3 - effectiveness bugs (automation quietly underperforming):**
11. Queue stale-sync prefix matching so dead accounts stop re-entering CC sessions (finding 6).
12. `discovery` vs `discovery_v2` source mismatch: engine-driven discovery follows have silently never executed (finding 21).
13. Genre filter: match on genre_main + genre_sub and handle "Electronic"; affects all three promo shortlist lanes (finding 18).

**P4 - review the 58 unverified mediums** (top candidates: follow-back pagination at 200 followers, fabrication guard failing open, email header injection + attachment path in outreach, Sheets formula injection, `python3 -c` auto-approval) and the improvement/doc-drift lists below.


## Confirmed Findings (adversarially verified)

Every finding below was checked by an independent verifier agent instructed to refute it. All 21 survived.

### 1. [CRITICAL] Unfollow sweep is unbounded: no per-session cap, no circuit-breaker check, no delay after failed unfollows (271 candidates today)

**File:** [scene_intelligence/sc_engagement.py:1832-1875](../../scene_intelligence/sc_engagement.py#L1832-L1875) | **Unit:** sc-core | **Category:** safety-cap | **Verdict:** confirmed

run_unfollow_sweep iterates every tracker entry whose window expired, with no session cap of any kind (SOP 4.1 caps unfollows at 15/session, Sunday only). It never checks _cb_session_halted, so even after a 403/DataDome halt the loop keeps firing DELETE calls. _action_delay() is only called in the success branch, so consecutive failures fire back-to-back with zero delay. Verified against the live tracker: 271 entries qualify as sweep candidates today (386 follows, most past unfollow_after), so a single default `python3 scene_intelligence/sc_engagement.py` live run (the sweep runs unless --likes-only/--follows-only) would attempt 271 authenticated writes in one session. The May-03 incident documented a CAPTCHA after only 3 scripted writes.

```
for entry in list(tracker.get("follows", [])):
        ...
        if not dry_run:
            ok = sc_delete(f"/me/followings/{uid}")
            result["success"] = ok
            if ok:
                ...
                _action_delay()
            else:
                _log(f"    UNFOLLOW FAILED: {name}")
```

**Impact:** One full live run can fire hundreds of write API calls (many failing rapid-fire with no inter-call delay and no halt on block signal) — realistic account-flag/ban risk, plus mass tracker mutation in one shot.

**Suggested fix:** Add an unfollows-per-session cap (e.g. 15, config value), check _cb_session_halted (and a consecutive-unfollow-failure breaker) inside the loop, and call _action_delay() on failures too.

### 2. [HIGH] No same-day double-run guard: HARD RULE 'never 2 IG scripts same day' is not enforced

**File:** [scene_intelligence/ig_engagement.py:1448-1476](../../scene_intelligence/ig_engagement.py#L1448-L1476) | **Unit:** ig-core | **Category:** safety-cap | **Verdict:** confirmed

preflight() checks only weekday and the 10-11 hour window. tracker['stats']['last_session'] is written at line 1790 after every live run but is never read anywhere, so a second --live run in the same window (or any run with --no-preflight, which bypasses ALL gates including the followback circuit breaker) executes a full second session the same day, doubling cumulative daily actions (up to ~2x(25 likes + 10 follows + 8 unfollows + ~10 like-before-follow likes)). The 2026-06-12 automation review explicitly flagged the missing same-day guard; the fix never landed. session_reports.json contains started_at timestamps that could trivially back this guard.

```
weekday_name = now.strftime("%A")
    if weekday_name not in cfg.SESSION_DAYS:
        return False, f"today_is_{weekday_name}_not_in_session_days"

    if not (cfg.SESSION_HOUR_START <= now.hour < cfg.SESSION_HOUR_END):
        return False, f"outside_session_window_hour_{now.hour}"
```

**Impact:** A duplicate run (Cowork double-trigger is a documented incident class) silently doubles daily action volume on the account that already had a bot-detection near-miss on 2026-05-03.

**Suggested fix:** In preflight(), read tracker['stats']['last_session'] (and/or the latest non-dry-run entry in session_reports.json) and hard-refuse if its date == today, including when --no-preflight is passed for live runs (only allow the bypass for stub/dry-run drivers).

### 3. [HIGH] Post-detection 48-72h cooldown is dead config: PAUSE_AFTER_* values are never read by any code

**File:** [scene_intelligence/ig_engagement_config.py:258-261](../../scene_intelligence/ig_engagement_config.py#L258-L261) | **Unit:** ig-core | **Category:** safety-cap | **Verdict:** confirmed

PAUSE_AFTER_SOFT_BLOCK=48, PAUSE_AFTER_HARD_BLOCK=72, PAUSE_AFTER_CAPTCHA=72, PAUSE_AFTER_VERIFICATION=0 appear only in the config; repo-wide grep finds zero references in any .py file. When a CircuitBreakerTripped halts a session, the signal is recorded in session_reports.json (ig_engagement.py:2158) but preflight() never inspects prior circuit_breaker events, so the very next scheduled run (or an immediate manual re-run) starts a fresh live session with zero cooldown after an Action Block / challenge.

```
PAUSE_AFTER_SOFT_BLOCK = 48    # action blocked on one type, account still works
PAUSE_AFTER_HARD_BLOCK = 72    # account restricted
PAUSE_AFTER_CAPTCHA = 72
PAUSE_AFTER_VERIFICATION = 0   # 0 = stop all automation, manual review required
```

**Impact:** Directly violates the owner's HARD RULE of a 48-72h zero-scripts cooldown after any detection event; continuing to hit the API right after a block is the highest-probability path to a permanent action block or account loss.

**Suggested fix:** In preflight(), scan session_reports.json for the most recent entry with circuit_breaker != null and refuse to run until now - ended_at exceeds the matching PAUSE_AFTER_* duration (and require manual state reset for verification-class signals).

### 4. [HIGH] Follows are logged as successful without any confirmation from Instagram

**File:** [scene_intelligence/ig_engagement.py:2053-2069](../../scene_intelligence/ig_engagement.py#L2053-L2069) | **Unit:** ig-core | **Category:** data-integrity | **Verdict:** confirmed

_execute_follow calls driver.follow_current_profile() and then unconditionally appends to tracker['active_follows'], increments total_followed, removes the entry from the queue, writes the engagement log and paid seed. RequestsBrowserDriver.follow_current_profile (ig_live_driver.py:283-296) returns None in three silent-failure cases: uid unresolvable, network error (_post returns None), and any non-2xx response that doesn't match a circuit-breaker signal (e.g. generic 400). It never checks friendship_status in the response. This is exactly the 'follows counted as successful without confirmation' item from the 2026-06-12 review; the likes path was fixed (like_post returns a confirmation bool checked at line 1899-1911) but the follow path was not.

```
driver.follow_current_profile()
    driver.check_for_circuit_breaker()

    today = today_iso()
    unfollow_after = (date.today() + timedelta(days=cfg.REACH["unfollow_after_days"])).isoformat()
    tracker["active_follows"].append({
```

**Impact:** Phantom follows corrupt the tracker and the follow-back rate metric (phantom entries can never be followed back, dragging the FOLLOWBACK circuit breaker toward false halts), trigger pointless unfollow actions 7 days later against accounts never followed, and pollute the paid-audience seed dataset.

**Suggested fix:** Make follow_current_profile() return bool (r.status_code == 200 and json status == 'ok' / friendship_status.following == true); in _execute_follow, only persist tracker/log/queue-consumption state when it returns True, mirroring the like_post pattern.

### 5. [HIGH] Unfollows are recorded as done without confirmation, permanently corrupting the tracker on failure

**File:** [scene_intelligence/ig_engagement.py:1838-1851](../../scene_intelligence/ig_engagement.py#L1838-L1851) | **Unit:** ig-core | **Category:** data-integrity | **Verdict:** confirmed

_execute_unfollow calls driver.unfollow_current_profile() and then unconditionally moves the entry from active_follows to unfollowed_history. RequestsBrowserDriver.unfollow_current_profile (ig_live_driver.py:323-336) silently returns None when uid resolution fails or the POST hits a network error, and does not check the response for success. Because REACH['never_retry_unfollowed']=True, a failed unfollow leaves the account actually followed forever while the tracker says it was unfollowed and blocks any retry.

```
driver.unfollow_current_profile()

    # Move from active_follows -> unfollowed_history
    tracker["active_follows"] = [
        e for e in tracker["active_follows"]
        if normalise_handle(e.get("username", "")) != u.handle
    ]
    tracker["unfollowed_history"].append({
```

**Impact:** Ghost follows accumulate on the real account (following count bloats, a bot-pattern signal IG scores), the tracker's total_unfollowed stat inflates, and the reconciliation between tracker and reality drifts silently.

**Suggested fix:** Have unfollow_current_profile() return a bool based on the friendships/destroy response (status ok / following == false) and only mutate the tracker when it returns True; on False, leave the entry in active_follows for the next sweep.

### 6. [HIGH] Queue stale-sync misses most real runtime skip reasons (exact-match list), dead accounts stay pending

**File:** [scene_intelligence/ig_merge_session_log.py (52-59, 367-377)](../../scene_intelligence/ig_merge_session_log.py) | **Unit:** ig-support | **Category:** bug | **Verdict:** confirmed

_QUEUE_STALE_SKIP_REASONS is matched with exact string equality against the free-text 'reason' Cowork writes. Real sessions write suffixed/variant reasons that never match. Verified against archived sessions: 'page_unavailable_deleted' (4x), 'account_not_found' (7x), 'account_dead' (4x), 'filter_failed_private_account' (4x), 'filter_failed_at_runtime_0posts_49followers', 'filter_failed_followers_too_high_6028', 'posts_older_than_90_days'/'all_posts_over_90_days' (17x), 'private_account' all fail the match. Verified live consequence: the 2026-07-01 session skipped @darktrackid, @ytprsy, @syber.shark.creations (page_unavailable_deleted) and @andreapoeppelbaum (filter_failed_at_runtime_0posts_49followers), and all four are still status='pending' in ig_target_list.json today.

```
_QUEUE_STALE_SKIP_REASONS = (
    "filter_failed_at_runtime",
    "posts_older_than_window",
    "ig_handle_dead",
    "account_unavailable",
    "in_blocked_list",
    "in_personal_network",
)
...
if track == "reach" and reason in _QUEUE_STALE_SKIP_REASONS:
```

**Impact:** Dead/private/off-filter accounts are re-served to CC session after session, wasting the 8 follow slots and producing skip streaks that trip the Class B circuit breaker - the exact 2026-06-08 0/8 failure mode this sync function was written to prevent.

**Suggested fix:** Match by prefix/family instead of equality: treat any reach-track ig_skip whose reason startswith one of ('filter_failed', 'posts_older', 'account_', 'page_unavailable', 'ig_handle_dead', 'private_account', 'no_recent_post') as stale; log unrecognized reasons loudly so new vocabulary gets added.

### 7. [HIGH] Own-release labels (no_longer_engage) are not in any exclusion file the queue builder consults - they can enter the follow queue

**File:** [scene_intelligence/ig_queue_builder.py (281-296, 483-486)](../../scene_intelligence/ig_queue_builder.py) | **Unit:** ig-support | **Category:** safety-cap | **Verdict:** confirmed

The builder's only exclusions are ig_blocked_accounts.json (7 entries), ig_personal_network.json (37 entries), active_follows and unfollowed_history. Verified: none of @mmdiscos/@mm.discos, @stereo.society, @nanadisc, or Indigo Children Records handles appear in either file, and no ig_*.py script reads enriched_contacts.json no_longer_engage flags (grep for no_longer_engage in scene_intelligence/ig_*.py returns nothing). Follower counts are unknown at build time (endpoint returns none), so the max_followers gate cannot reject these labels either; if any follows 2+ seeds it lands in ig_target_list.json as a pending follow target. The standing rule (and docs/cowork-ig-engagement-body.md: 'NEVER engage own-release labels via automation: @mmdiscos, @stereo.society, @nanadisc') is enforced only by CC eyeballing - which already failed on 2026-06-17 (@mm.discos engaged).

```
if handle in blocked:
        return False, "blocked"
    if handle in personal:
        return False, "personal_network"
```

**Impact:** A hard never-engage rule (own-release labels) has no machine enforcement in the Reach selection path; one seed-overlap coincidence puts a forbidden label into the vetted follow queue that CC is instructed to treat as 'the contract'.

**Suggested fix:** Add the own-release label IG handles (and any other no_longer_engage contacts with known IG handles) to ig_blocked_accounts.json, and/or have _passes_static_filters also reject handles matching enriched_contacts entries with no_longer_engage=true.

### 8. [HIGH] No same-day IG-script guard in any of the five API-calling support scripts

**File:** [scene_intelligence/ig_audit_queue_freshness.py:389-390](../../scene_intelligence/ig_audit_queue_freshness.py#L389-L390) | **Unit:** ig-support | **Category:** safety-cap | **Verdict:** confirmed

HARD RULE: never two IG automation scripts on the same day, plus 48-72h cooldown after a detection event. None of ig_audit_queue_freshness.py, ig_queue_builder.py, ig_followback_checker.py, ig_reconcile_followings.py, or ig_follower_audit.py checks any shared state before hitting the IG private API - not engagement_log.json, not tracker stats.last_session (which exists and reads '2026-07-01'), not each other's _meta dates - and none records its own run in a place the others check. The engine's only guard (ig_engagement.py validate_config) is a static day-of-week overlap check between IG and SC config, not a runtime 'did anything IG run today' check. Enforcement is purely the docstrings ('Run BEFORE the next engagement session, ideally one day in advance'; reconcile: 'Run on a day with no IG engagement scheduled') plus human discipline.

```
sid, csrf = _load_credentials()
    session = _build_session(sid, csrf)
```

**Impact:** One absent-minded invocation stacks a 50-165-call API script on top of an engagement session on the same cookie session - the pattern behind the 2026-05-03 near-miss bot warning; account-loss class risk.

**Suggested fix:** Add a tiny shared ledger (e.g. scene_intelligence/ig_daily_ledger.json) that every IG-API script writes on start and checks first; refuse to run if any IG script (or a session JSONL for today) is recorded for the current Berlin date, with an explicit --override flag.

### 9. [HIGH] no_longer_engage is never honored: released-on labels MM Discos and Stereo Society are live like/repost targets, and MM Discos was actually liked by the automation

**File:** [scene_intelligence/sc_engagement.py:1190-1228](../../scene_intelligence/sc_engagement.py#L1190-L1228) | **Unit:** sc-core | **Category:** safety-cap | **Verdict:** confirmed

The standing HARD RULE says labels the artist released on (MM Discos, Stereo Society, NaNa Disc, Indigo Children) must never be engaged. grep shows zero references to `no_longer_engage` in any scene_intelligence/*.py; build_si_queue filters only on user_id, match_score, tracks, hidden list, like-cooldown and icon tier. Verified in data: enriched_contacts.json has 'mm.discos' (label, score 5, 3,625 followers, 149 tracks, uid 2159984) and 'Stereo Society' (score 2, 12,756 followers, uid set), neither flagged nor in engagement_log['hidden']. Both pass every build_si_queue gate; mm.discos (tier 'prominent', score 5, followers>=500) also qualifies for the reposts queue. engagement_log.json shows the engine actually liked mm.discos on 2026-05-09 and 2026-05-23 — the violation already occurred twice, and the 30-day cooldown has again expired.

```
category = (contact.get("category") or "").strip().lower()
        if followers > LIKE_MAX_ARTIST_FOLLOWERS and category not in LIKE_LABEL_CATEGORIES:
            continue
```

**Impact:** Direct violation of the owner's never-engage rule for released-on labels; automation has already liked MM Discos twice and both labels remain eligible like (and MM Discos repost) targets on every run.

**Suggested fix:** In build_si_queue and build_promo_queue, skip any contact with no_longer_engage truthy (and add an explicit blocklist for the four released-on labels); set the flag on the mm.discos / Stereo Society SI records.

### 10. [HIGH] Unfollow sweep ignores no_longer_following / no_longer_engage tracker flags: 246 of today's 271 candidates are flagged, including released-on label mm.discos

**File:** [scene_intelligence/sc_engagement.py:1837-1852](../../scene_intelligence/sc_engagement.py#L1837-L1852) | **Unit:** sc-core | **Category:** bug | **Verdict:** confirmed

run_unfollow_sweep only checks followed_back and unfollow_after. The live tracker carries 298 entries flagged no_longer_following=true (documented tracker-drift: 'button read Follow on live SC, so tracker drift — we are not actually following') and 9 flagged no_longer_engage=true. Verified: 246 of the 271 current sweep candidates carry one of these flags, including the mm.discos entry (no_longer_engage=true) — the HARD RULE says released-on labels must never appear in unfollow-sweep candidates. For the no_longer_following entries the engine would issue DELETE /me/followings/{uid} for follows that do not exist on live SC (guaranteed failures, retried every sweep since remove_follow_record only runs on success).

```
# Keep if followed back (never auto-unfollow these)
        if entry.get("followed_back"):
            kept.append({"name": name, "reason": "followed_back"})
            continue

        # Keep if window hasn't expired yet
        if not unfollow_after or today_str < unfollow_after:
```

**Impact:** Hard-rule violation (mm.discos in sweep candidates) plus ~246 pointless/failing write calls per sweep that never clear, permanently re-attempted on every run.

**Suggested fix:** Skip entries where entry.get('no_longer_following') or entry.get('no_longer_engage') is truthy (and consider pruning no_longer_following entries into permanently_unfollowed instead of leaving them in follows).

### 11. [HIGH] Reposts pass ignores all circuit breakers and iterates the entire repost queue on persistent failure

**File:** [scene_intelligence/sc_engagement.py:2073-2088](../../scene_intelligence/sc_engagement.py#L2073-L2088) | **Unit:** sc-core | **Category:** safety-cap | **Verdict:** confirmed

The likes pass (line 2016) and follows pass (line 2049) both check _cb_session_halted before and during execution, but the reposts pass has no circuit-breaker check at all, and repost_track_for_artist has none either. If a 403 (account-restriction signal) halts the session during likes or follows, the reposts pass still runs and fires write attempts. Worse, reposts_done only increments on success and there is no failure counter or artist-check cap, so under persistent failure the loop walks EVERY item in queue['reposts'], each iteration making a track fetch plus a write attempt.

```
if not likes_only and not follows_only and reposts_budget > 0:
            _log(f"\n--- Reposts (budget: {reposts_budget} this week) ---")
            reposts_done = 0
            ...
            for item in queue["reposts"]:
                if reposts_done >= reposts_budget:
                    break
                r = repost_track_for_artist(item, eng_log, dry_run)
```

**Impact:** Continued write traffic after a block signal (the exact scenario circuit breakers exist to stop) and an unbounded quota-burning loop when reposts fail systemically.

**Suggested fix:** Check _cb_session_halted in the reposts loop, add a consecutive-repost-failure breaker, and cap artists checked (like the likes pass does with budget*4).

### 12. [HIGH] Non-atomic JSON writes plus silent empty-state fallback can wipe the follow tracker, the permanently_unfollowed banlist, and today's cap counters

**File:** [scene_intelligence/sc_engagement.py (652-654, 647-649, 715-721)](../../scene_intelligence/sc_engagement.py) | **Unit:** sc-core | **Category:** data-integrity | **Verdict:** confirmed

_save_follow_tracker and save_eng_log write directly over the target file with open(..., 'w') + json.dump — a crash/kill mid-write leaves a truncated file. load_follow_tracker then catches JSONDecodeError and silently returns an EMPTY tracker, and load_eng_log returns {'log': {}}. The next run would therefore see 0 follows (386 records + the permanently_unfollowed re-follow banlist gone) and today's action counts as 0 (daily like/follow caps reset mid-day). _save_si_contacts_if_dirty (line 932) has the same non-atomic write over the 938-contact SI database.

```
def _save_follow_tracker(data: dict) -> None:
    with open(FOLLOW_TRACKER, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
...
    except (json.JSONDecodeError, OSError):
        return {"follows": [], "permanently_unfollowed": [],
                "stats": {"total_followed": 0, "total_unfollowed": 0, "follow_backs": 0}}
```

**Impact:** One interrupted write can silently destroy all follow history and the never-re-follow banlist, bypass daily caps for the rest of the day, and cause mass re-follows of previously unfollowed accounts.

**Suggested fix:** Write to a temp file in the same directory and os.replace() into place; on JSONDecodeError of an EXISTING file, abort loudly instead of returning empty state.

### 13. [HIGH] Strategy 2 saves an UNVERIFIED profile's cookies (most-cookies heuristic) when the API check is inconclusive

**File:** [scene_intelligence/sc_extract_chrome_cookies.py:267-280](../../scene_intelligence/sc_extract_chrome_cookies.py#L267-L280) | **Unit:** sc-support | **Category:** safety-cap | **Verdict:** confirmed

If the /me verification fails for all candidates (network error, SC 4xx, DataDome block - all swallowed into (False, "")), the script falls back to "most-cookies profile with oauth_token" and writes that session to .sc_browser_state.json with no identity check at all. On a Mac with 5 Chrome profiles, whichever profile happens to have the most soundcloud.com cookies wins, regardless of which SC account it is logged into.

```
print("\nAPI verification inconclusive. Trying most-cookies profile with oauth_token...")
        best = None
        best_count = 0
        for profile_path, cookies in candidates:
            oauth_val = _get_oauth_token_value(cookies)
            if oauth_val and len(cookies) > best_count:
```

**Impact:** Session file for the wrong SC account gets persisted and silently used as auth fallback (sc_browser_likes priority 2, and sc_engagement.py points here on token failure). Engagement actions on the wrong account is precisely the class of incident (2026-06-10 wrong-profile session) the project's hard rules exist to prevent.

**Suggested fix:** When API verification is inconclusive, ABORT and tell the user to retry when the API is reachable; never persist a session whose account identity was not confirmed. At minimum require Strategy 3's email match as a gate rather than a later fallback.

### 14. [HIGH] Sunday unfollow-sweep candidate filter omits no_longer_engage - own label mm.discos currently qualifies for unfollow

**File:** [docs/cowork-task-bodies.md:304-309](../../docs/cowork-task-bodies.md#L304-L309) | **Unit:** safety-caps | **Category:** safety-cap | **Verdict:** confirmed

The autonomous Sunday sweep (Task 2, step C.2) builds candidates from only three conditions: followed_back==false, no_longer_following!=true, unfollow_after<=today. It never excludes no_longer_engage=true entries, and neither does the identical filter in docs/sc-engagement-sop.md 437-441, nor the sc_unfollow --log-action handler in sc_engagement.py (it unconditionally removes the entry and adds it to permanently_unfollowed, with no followed_back or no_longer_engage guard). Live data confirms exposure: sc_follow_tracker.json contains mm.discos (Amir's own-release label, marked_no_engage_reason 'Own-label exclusion - user instruction 2026-05-23') with followed_back=false, no no_longer_following flag, and unfollow_after=2026-05-05 (long expired) - it matches C.2 exactly. The standing rule says own-release labels must never appear in unfollow-sweep candidates. sc-agent-context.md line 362 states the rule ('never engage/sweep no_longer_engage entries') but the operational filter the agent executes does not implement it.

```
C.2 Build the candidate set -- entries where ALL true:
       - followed_back == false
       - no_longer_following != true
       - unfollow_after <= today (window expired)
```

**Impact:** Next Sunday sweep can unfollow mm.discos (and any other no_longer_engage entry with an expired window), publicly unfollowing a label Amir released on and permanently banning re-follow via permanently_unfollowed - a relationship-damaging, hard-rule violation executed autonomously.

**Suggested fix:** Add '- no_longer_engage != true' to C.2 in both docs/cowork-task-bodies.md and docs/sc-engagement-sop.md 6.3 step 2, and add a code guard in sc_engagement.py's sc_unfollow handler that refuses (or requires --force) when the tracker entry has no_longer_engage=true or followed_back=true.

### 15. [HIGH] enrich_contacts.py silently rebuilds enriched_contacts.json from raw_contacts.json — no guard on the mature DB (known landmine, still unguarded)

**File:** [scene_intelligence/enrich_contacts.py (254-257, 325-327)](../../scene_intelligence/enrich_contacts.py) | **Unit:** si-enrich | **Category:** data-integrity | **Verdict:** confirmed

main() loads raw_contacts.json, normalizes it, and writes the result over enriched_contacts.json unconditionally. There is no check that OUTPUT_FILE already exists, no confirmation prompt, no merge with existing data, and no backup. Running the documented command once replaces the 1200-contact enriched DB (curator DB, IG handles, score locks, SC/Spotify/YT enrichment, promo flags) with a bare re-normalization of the raw extract. The only 'guard' is a note in Claude's memory file — nothing in code.

```
with open(INPUT_FILE, encoding="utf-8") as f:
        raw = json.load(f)

    all_contacts = normalize_raw_contacts(raw)
...
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_contacts, f, indent=2, ensure_ascii=False)
```

**Impact:** One accidental run destroys the crown-jewel dataset. Recovery depends entirely on scene_intelligence/backups/ (only written by push_to_sheets, max 25 kept) being fresh.

**Suggested fix:** At startup, if OUTPUT_FILE exists: refuse unless a --force-rebuild flag is passed, print a loud warning with contact counts (existing vs. new), and write a timestamped backup of the existing file before overwriting. Better: merge by dedup_key instead of replacing.

### 16. [HIGH] classify_subtypes.py unconditionally overwrites sub_type for every contact — wipes 210 curator sub_types and all manual Type edits

**File:** [scene_intelligence/classify_subtypes.py:363-378](../../scene_intelligence/classify_subtypes.py#L363-L378) | **Unit:** si-enrich | **Category:** data-integrity | **Verdict:** confirmed

Step 3 assigns c["sub_type"] = sub for ALL contacts. For any category other than media/promoter (and not in the 2-name override map), sub is "", so the field is blanked. Verified against the live DB: 214 non-media/promoter contacts currently have sub_type set, including all 210 category="curator" contacts (Curator DB Slice 1) plus labels/DJs whose Type was manually edited in Sheets and synced back via push_to_sheets sync (lines 979-985). MEMORY.md lists this script as a routine re-run command, so this is one command away from firing.

```
if nl in _SUB_TYPE_OVERRIDES:
            sub = _SUB_TYPE_OVERRIDES[nl]
        elif cat == "media":
            sub = _classify_media(name, c)
        elif cat == "promoter":
            sub = _classify_promoter(name, c)
        else:
            sub = ""

        c["sub_type"] = sub
```

**Impact:** Re-running the documented command 'python3 scene_intelligence/classify_subtypes.py' erases every curator sub_type and every manual sub_type edit for non-media/promoter contacts; media/promoter manual edits are also replaced by heuristics (e.g. SoundCloud-sourced media forced back to 'premiere').

**Suggested fix:** Only assign when the classifier produced a value: 'if sub: c["sub_type"] = sub', or skip contacts that already have a non-empty sub_type unless a --reclassify flag is passed.

### 17. [HIGH] Sync-back applies stale Sheet values over newer local edits for category, sub_type, genre, and promo_list — only score has a lock

**File:** [scene_intelligence/push_to_sheets.py:969-1023](../../scene_intelligence/push_to_sheets.py#L969-L1023) | **Unit:** si-enrich | **Category:** data-integrity | **Verdict:** confirmed

sync_from_sheet treats any non-empty Sheet cell that differs from local data as a manual edit and overwrites the local field. But the Sheet is a snapshot from the previous push: if category/sub_type/genre_sub/promo_list was changed locally since then (RM writes genre tags directly to enriched_contacts.json; curator/enrichment scripts set sub_type and genre), the next sync reverts it to the stale Sheet value. This exact failure class already happened for match_score and was patched with score_locked (comment at lines 998-1001) — the other four synced fields have no equivalent protection.

```
# Category change
            if cat_idx >= 0 and len(row) > cat_idx:
                sheet_cat = row[cat_idx].strip().lower()
                if sheet_cat and sheet_cat != contact.get("category", ""):
                    print(f"    {name}: category {contact.get('category')} -> {sheet_cat} ({tab_name})")
                    contact["category"] = sheet_cat
```

**Impact:** Any local change to category, sub_type, genre, or promo flag made between two pushes is silently reverted on the next /sync, exactly like the pre-2026-05-06 score bug.

**Suggested fix:** Track a last_pushed snapshot per contact (or per-field hash) and only apply a Sheet value when it differs from what was last pushed (true three-way merge); or extend the *_locked mechanism to the other synced fields.

### 18. [HIGH] Genre filter checks genre_main only and 'electronic' is not in the family set, excluding ~40% of eligible DJs

**File:** [scene_intelligence/promo_dj_shortlist.py (15-18, 53)](../../scene_intelligence/promo_dj_shortlist.py) | **Unit:** si-discover | **Category:** bug | **Verdict:** confirmed

shortlist() filters via genre_match(release_genre, c.get("genre_main", "")). The DARK_ELECTRONIC token set contains "electronica" but not "electronic", and genre_sub is never consulted. Verified against the live DB: of 566 DJ contacts, 167 have genre_main exactly "Electronic" (plus 82 blank) - all excluded even when genre_sub is "Dark Disco"/"EBM" etc. Only 196 DJs pass on genre_main vs 336 if genre_sub were included. extract_contacts.py and extract_ra.py both set genre_main="Electronic" with the specific genre in genre_sub, so those sources are systematically filtered out. The same genre_match is imported by promo_label_shortlist.py (line 61) and promo_press_shortlist.py (line 98), so all three promo lanes shortlist the wrong (narrower) target set.

```
if not genre_match(release_genre, c.get("genre_main", "")):
```

**Impact:** DJ, label, and press shortlists silently omit a large share of in-scene contacts; promotion campaigns target a skewed subset (Rekordbox-sourced contacts dominate because they store the specific genre in genre_main).

**Suggested fix:** Match on genre_main + genre_sub combined (e.g. genre_match(release_genre, f"{c.get('genre_main','')} {c.get('genre_sub','')}")) and add "electronic" to DARK_ELECTRONIC or strip it as a neutral token.

### 19. [MEDIUM] Live driver never verifies which account the session cookie belongs to (wrong-profile incident class)

**File:** [scene_intelligence/ig_live_driver.py:520-554](../../scene_intelligence/ig_live_driver.py#L520-L554) | **Unit:** ig-core | **Category:** safety-cap | **Verdict:** confirmed

build_live_driver() loads IG_SESSION_ID/IG_CSRF_TOKEN/IG_USER_ID from .env and starts acting immediately. verify_session() exists but is only invoked by the --whoami and --test CLI paths, never on a live engine run. Authentication is carried by sessionid; if the cookies were extracted from the wrong Chrome profile (a real incident on 2026-06-10 -- 4 of 5 profiles on this Mac start with 'Amir', only 'Amir (Inch of Shadow)' is correct), every follow/like/unfollow executes on the wrong Instagram account with no warning. Setting the ds_user_id cookie from IG_USER_ID does not detect the mismatch.

```
print(f"[LIVE DRIVER] Loaded credentials from .env (user_id={own_user_id})")
    return RequestsBrowserDriver(
        session_id=session_id,
        csrf_token=csrf_token,
        own_user_id=own_user_id,
    )
```

**Impact:** An entire automated engagement session could run against a personal or unrelated IG account, burning that account's action budget and creating bot-pattern activity on it; this is the requests-driver equivalent of the mandatory Chrome-profile verbatim check.

**Suggested fix:** In build_live_driver(), call verify_session() and hard-fail unless the resolved pk equals IG_USER_ID and the username equals 'inch_of_shadow' (exact match), printing the verified identity before any action.

### 20. [MEDIUM] Blocked-accounts and personal-network lists are never consulted in any engine selection path (2026-06-12 deferred fix has not landed here)

**File:** [scene_intelligence/sc_engagement.py:1329-1337](../../scene_intelligence/sc_engagement.py#L1329-L1337) | **Unit:** sc-core | **Category:** safety-cap | **Verdict:** confirmed

docs/sc-engagement-sop.md §4.3 rules 13-14 require reading scene_intelligence/ig_blocked_accounts.json and ig_personal_network.json and skipping any user_id/slug/name in them ('Cross-check before any follow/like'). grep confirms sc_engagement.py contains zero references to either file. The only related control is DISCOVERY_COUNTRY_EXCLUDE, which the code itself documents as best-effort with CC's click-time visit as the backstop — but run_engagement's autonomous API-write mode (likes/follows/reposts fired directly by the script) has no click-time backstop at all, so a blocked account reachable via the SI queue, promo queue, or a discovery candidate with null country_code gets engaged with no check anywhere.

```
# Country exclusion (added 2026-06-16, Amir): skip excluded country
            # codes (best-effort; SC's country_code is sometimes null, in which
            # case CC's click-time profile visit is the backstop).
            if (user.get("country_code") or "").upper() in DISCOVERY_COUNTRY_EXCLUDE:
                continue
```

**Impact:** Blocked accounts and personal-network friends can be liked/followed by autonomous engine runs — exactly the blocked-list bypass class flagged in the 2026-06-12 automation review.

**Suggested fix:** Load ig_blocked_accounts.json and ig_personal_network.json at queue-build time and exclude matches (by user_id, slug, and normalized name) in build_si_queue, build_promo_queue, and discover_related_artists.

### 21. [LOW] Source-string mismatch ('discovery' vs 'discovery_v2') silently excludes ALL discovery candidates from the follows queue

**File:** [scene_intelligence/sc_engagement.py (1501 (vs 1421))](../../scene_intelligence/sc_engagement.py) | **Unit:** sc-core | **Category:** bug | **Verdict:** confirmed

build_full_queue bypasses the upload-age follow gate only when item['source'] == 'discovery', but discover_related_artists emits source 'discovery_v2' (line 1421, tag added 2026-05-21). Discovery items therefore hit the else branch, where item['contact'] is the empty dict {}, last_upload_str is '', and follow_upload_ok stays False — so no discovery candidate can ever enter follows_queue. This breaks both `run_engagement(--discover)` follows and the `--dump-queue --discover` follows output. The live CC workflow only survives because sc_weekly_health.py calls discover_related_artists directly and writes its own candidate files.

```
if item.get("source") == "discovery":
            follow_upload_ok = True
        else:
            last_upload_str = item["contact"].get("soundcloud_last_upload", "")
            follow_upload_ok = False
```

**Impact:** Engine-driven discovery follows (the core reciprocity strategy) silently never execute; --dump-queue hands CC a follows list with zero discovery targets.

**Suggested fix:** Change the check to item.get('source', '').startswith('discovery') or compare against both 'discovery' and 'discovery_v2'.


## Unverified Findings - Medium Severity

58 findings. Not adversarially verified (skipped to save tokens); reviewed by a single auditor that was required to cite code evidence. Review before acting.


### ig-core

- **[scene_intelligence/ig_engagement.py:2013-2036](../../scene_intelligence/ig_engagement.py#L2013-L2036)** (bug): Transient profile-fetch failure permanently deletes Reach queue entries via the genre filter. When get_profile_state() fails (network error, non-200, unparseable JSON), it returns the `empty` dict (ig_live_driver.py:165, 175-187) with is_private=False/not_found=False and no follower_count, so _execute_follow proceeds: the live-metrics overwrite is skip... *Fix:* In _execute_follow, treat a state dict lacking follower_count (fetch failure) as 'skip without queue mutation': return early and leave the entry pending. Only run live gates (range...
- **[scene_intelligence/ig_engagement_config.py:104-119](../../scene_intelligence/ig_engagement_config.py#L104-L119)** (bug): Dead-account targeting rules (post recency, min posts, engagement rate, profile photo, ghost posts) are never enforced. REACH promises 'max_post_recency_days': 30 ('must have posted within 30 days'), 'min_engagement_rate': 0.005, 'require_profile_photo': True, 'skip_zero_engagement_posts': True, 'skip_all_repost_accounts': True -- repo-wide grep shows none of these keys is read... *Fix:* In _execute_follow, after the live fetch: skip (without permanent queue deletion) when post_count < min_posts, when the newest recent_posts posted_at is older than max_post_recency...
- **[scene_intelligence/ig_engagement.py:614-632](../../scene_intelligence/ig_engagement.py#L614-L632)** (safety-cap): no_longer_engage flag is not honored by the engine; own-label protection rests on a single ig_blocked field. contact_is_always_skip checks ig_username_cleared, ig_handle_dead, ig_blocked, the blocked-accounts file, personal network, and the hidden log -- but never contact.get('no_longer_engage'), the flag the owner's standing rule designates for released-on labels. V... *Fix:* Add `if contact.get("no_longer_engage") is True: return True, "no_longer_engage"` to contact_is_always_skip, and add the own-label handles (mm.discos, stereosocietyofficial, plus N...
- **[scene_intelligence/ig_engagement.py:1084-1090](../../scene_intelligence/ig_engagement.py#L1084-L1090)** (bug): Blocked-country (Hebrew bio) hard rule not re-checked against the live bio at follow time. build_reach_pool runs contains_hebrew()/is_israeli_location() only on the statically stored queue bio/location -- which are empty for 1063 of 1068 pending entries -- so the config's 'hard rule, both Reach and Scene' is effectively unenforced for Reach. _execut... *Fix:* In _execute_follow, after the live bio is captured, run is_blocked_country({'ig_bio': live_bio}, cfg) / contains_hebrew(live_bio, cfg) and skip (removing from queue) on a hit.

### ig-support

- **[scene_intelligence/ig_merge_session_log.py:475-483](../../scene_intelligence/ig_merge_session_log.py#L475-L483)** (safety-cap): Vetted-pool depth warning (<=30) is not implemented anywhere. Owner rule (2026-06-14, feedback_ig_queue_depth_warning): after every session merge, check vetted-pool depth and warn unprompted in bold if <=30. merge() syncs the queue and archives the JSONL but never counts remaining pending entries or prints any depth warn... *Fix:* At the end of merge(), count queue entries with status=='pending' (optionally only those with audit_date/fresh relevance verdict = the actually-vetted pool) and print a loud 'WARNI...
- **[scene_intelligence/ig_audit_queue_freshness.py:569-575](../../scene_intelligence/ig_audit_queue_freshness.py#L569-L575)** (bug): Queue only saved when metric-stale entries exist; private markings and all enrichment silently discarded otherwise. The save condition is 'if not dry_run and stale:'. But entries are mutated in several paths that do not append to the 'stale' list: private accounts get status='skipped_stale' (lines 464-467) yet go into the 'private' list, and every audited entry gets enrichm... *Fix:* Track a 'touched' boolean (as update_queue_from_events in the merge script does) set on any entry mutation, and save when touched, not when stale is non-empty. Also use a tmp+renam...
- **[scene_intelligence/ig_followback_checker.py:459](../../scene_intelligence/ig_followback_checker.py#L459)** (bug): Follow-back rate double-counts reciprocators (reports ~2x the real rate). run_checker sets stats['follow_backs'] = count of active entries with followed_back (lines 397-398) immediately before calling _print_report, which then computes the rate numerator as len(followed_back) + stats.get('follow_backs', 0) - the same entries counted... *Fix:* Numerator should be a single deduplicated count: active reciprocators plus unfollowed_history entries with follow_back=true; drop the stats addition.
- **[scene_intelligence/ig_followback_checker.py:396-399](../../scene_intelligence/ig_followback_checker.py#L396-L399)** (data-integrity): stats.follow_backs written with conflicting semantics by checker (snapshot) vs merge script (cumulative counter). ig_merge_session_log.py line 288 increments stats['follow_backs'] cumulatively on each visual-guard reciprocator catch ('stats["follow_backs"] = int(stats.get("follow_backs", 0) or 0) + 1'), treating it as an ever-increasing counter. The checker overwrites the... *Fix:* Pick one semantic (cumulative counter owned by merge; snapshot derived at print time and never persisted), and remove/rename the redundant total_follows counter.
- **[scene_intelligence/ig_reconcile_followings.py:228-237](../../scene_intelligence/ig_reconcile_followings.py#L228-L237)** (data-integrity): unfollowed_history schema drift across writers; automation unfollows display '?' in the viewer. The merge script writes history entries with keys followed_date/unfollowed_date/follow_back/source (ig_merge_session_log.py:298-306); reconcile writes followed_at/unfollowed_at/reason. ig_show_automation_follows.py:117 reads only 'unfollowed_at' or 'date', so ... *Fix:* Standardize on one schema (e.g. followed_at/unfollowed_at/follow_back/reason), migrate existing entries once, and update ig_show_automation_follows.py to read the canonical key.
- **[scene_intelligence/ig_queue_builder.py (38-40, 89-145)](../../scene_intelligence/ig_queue_builder.py)** (safety-cap): Default run uses 33 seeds against the script's own '~15 seeds per run' safety guidance (~165 API calls). The module docstring states 'Safe at ~15 seed accounts per run', but DEFAULT_SEEDS has grown to 33 entries (matches _meta.seeds_used in the live queue file, so full-list runs happen in practice, last on 2026-07-03). Each seed costs 1 resolve call + up to 4 pag... *Fix:* Either update the safety guidance with a verified bound, or (better) warn and require confirmation when len(seeds) > 15, and support chunked runs (e.g. --seed-offset) so a rebuild ...
- **[scene_intelligence/ig_merge_session_log.py:90-92](../../scene_intelligence/ig_merge_session_log.py#L90-L92)** (safety-cap): Fabrication guard fails open when no event timestamps parse. check_not_fabricated returns ok=True with 'guard skipped' when zero events have a parseable ts. Cowork has already slipped field names four times (seq/post 06-20, target 06-24, username/timestamp 06-27, type 07-01); only 'ts' and 'timestamp' are aliased in _no... *Fix:* Fail closed: if no timestamps parse, abort with the same --force escape hatch instead of proceeding; optionally also warn when fewer than N% of events carry parseable timestamps.

### sc-core

- **[scene_intelligence/sc_engagement.py:1803-1809](../../scene_intelligence/sc_engagement.py#L1803-L1809)** (bug): Follow-back detection reads only the first 200 followers (no pagination) — reciprocators beyond page 1 will be wrongfully auto-unfollowed. update_follow_back_status fetches /me/followers with limit=200 and no linked_partitioning/next_href pagination despite the docstring saying 'paginated'. Any follower beyond the first 200 returned is invisible, so their tracker entry keeps followed_back=false a... *Fix:* Paginate with linked_partitioning=1 / next_href until exhausted (bounded by a sane page cap), and treat a failed/partial fetch as 'skip sweep' rather than 'no follow-backs'.
- **[scene_intelligence/sc_engagement.py:2418-2421](../../scene_intelligence/sc_engagement.py#L2418-L2421)** (bug): --log-action sc_follow does not check permanently_unfollowed, contradicting SOP §4.3 rule 16. The SOP states: '`permanently_unfollowed`: never re-followed... The --log-action sc_follow handler checks it and refuses re-follows (idempotent).' The handler only calls is_already_following(), which checks tracker['follows'] — it never looks at tracker['perma... *Fix:* In the sc_follow handler, refuse (print a loud warning, non-zero exit) when str(args.user_id) is in tracker.get('permanently_unfollowed', []).
- **[scene_intelligence/sc_engagement.py (455, 528)](../../scene_intelligence/sc_engagement.py)** (bug): Retry-After parsed with int() — an HTTP-date value raises uncaught ValueError and crashes the run mid-session. Both _user_request and sc_v2_post do `int(r.headers.get("Retry-After", 15))`. RFC 9110 allows Retry-After to be an HTTP-date string; int() then raises ValueError, which is not caught (the except clauses only catch requests.RequestException), aborting run_engag... *Fix:* Wrap the parse: try int(...) except ValueError: retry_after = RATE_LIMIT_BLOCK_THRESHOLD_SECONDS + 1 (treat unparseable as block signal).
- **[scene_intelligence/sc_engagement.py:2014-2099](../../scene_intelligence/sc_engagement.py#L2014-L2099)** (data-integrity): No try/finally or incremental persistence around the action loops — any exception after actions loses all performed-action records. run_engagement mutates eng_log and tracker in memory during the likes/follows/reposts passes and only persists at the very end (lines 2096-2099; the earlier save at 1977-1979 covers only the unfollow sweep). Any unhandled exception in between (e.g. the Retry-A... *Fix:* Wrap the action phases in try/finally with the saves in finally, or save eng_log + tracker after each successful action (writes are small and local).
- **[scene_intelligence/sc_engagement.py (1925-1926, 2096-2098)](../../scene_intelligence/sc_engagement.py)** (data-integrity): No file locking: concurrent run_engagement and --log-action (or a second engine run) silently lose each other's writes. run_engagement loads engagement_log.json and sc_follow_tracker.json once at start and overwrites both files wholesale at the end. The --log-action CLI path does its own load/modify/save of the same files. There is no lockfile or freshness check, so if --log-ac... *Fix:* Take an exclusive lockfile (fcntl.flock on a .lock next to the JSONs) around load-modify-save in both run_engagement and the --log-action handlers.

### sc-support

- **[scene_intelligence/check_sc_follows.py:100-105](../../scene_intelligence/check_sc_follows.py#L100-L105)** (bug): SI ID lookup built from a field that does not exist (soundcloud_id vs soundcloud_user_id). build_si_lookup reads c.get("soundcloud_id") but enriched_contacts.json uses the field soundcloud_user_id. Verified against the live file: 0 of 1200 contacts have soundcloud_id, 815 have soundcloud_user_id. So by_sc_id is always empty and matching silently deg... *Fix:* Use c.get("soundcloud_user_id") when building by_sc_id.
- **[scene_intelligence/sc_weekly_health.py:244-248](../../scene_intelligence/sc_weekly_health.py#L244-L248)** (data-integrity): Tracker "backup" is written AFTER mutation, so it backs up the new state, not the pre-run state. update_tracker mutates tracker entries in the loop (lines 213-241: followed_back, no_longer_following, user_id resolution, stats), then writes the bak file from the same already-mutated dict. The backup is byte-equivalent to what will be written to sc_follow_t... *Fix:* Snapshot the raw tracker file (or a deep copy of the loaded dict) to the .bak path BEFORE calling update_tracker / before any mutation.
- **[scene_intelligence/sc_weekly_health.py (27-31, 82, 259-265)](../../scene_intelligence/sc_weekly_health.py)** (safety-cap): API_BUDGET_HARD_CAP does not cover discovery, the largest API consumer (~50-70 calls vs cap of 30). _api_get enforces API_BUDGET_HARD_CAP=30, but run_discovery calls sc_engagement.discover_related_artists, whose HTTP calls go through sce.sc_client_get and are never counted. The docstring itself admits ~70 real calls per run. The "hard cap" therefore bounds o... *Fix:* Pass a call-counter/budget hook into sc_engagement.sc_client_get (or count calls it makes) so the hard cap covers the whole run, and report both numbers.
- **[scene_intelligence/sc_extract_chrome_cookies.py:71-73](../../scene_intelligence/sc_extract_chrome_cookies.py#L71-L73)** (security): Insecure tempfile.mktemp used for a copy of the Chrome cookie database. tempfile.mktemp is deprecated precisely because it is race-prone: it returns a predictable path without creating the file, so another local process can pre-create/symlink it before shutil.copy2 writes the full Chrome Cookies DB (session credential material) th... *Fix:* Use tempfile.NamedTemporaryFile(delete=False, suffix=".db") or tempfile.mkstemp, then copy into the already-created 0600 file descriptor/path.
- **[scene_intelligence/sc_extract_chrome_cookies.py:177-183](../../scene_intelligence/sc_extract_chrome_cookies.py#L177-L183)** (bug): Loose account-identity match: any SC account with "inch" or "shadow" in its permalink passes as Inch of Shadow. _verify_oauth_token_api accepts a token as the correct account if the user_id matches OR the permalink merely contains the substring "inch" or "shadow". A profile logged into any unrelated account like "shadow-child" or "nightshadow-berlin" would be accepted a... *Fix:* Match strictly on user_id == SC_USER_ID (the exact-ID check already exists; delete the three substring fallbacks).
- **[scene_intelligence/sc_log_manual.py:138-146](../../scene_intelligence/sc_log_manual.py#L138-L146)** (bug): _lookup_in_si uses substring match on the whole SC URL; short slugs can hit the wrong contact. The match is `slug_lower in sc_url` against the full soundcloud_url string. A slug like "nina" matches "soundcloud.com/nina-kraviz"; "dark" matches any URL containing it. The first contact in iteration order wins. The resolved contact supplies name, soundcloud... *Fix:* Compare the extracted URL slug exactly: `sc_url.rstrip('/').split('/')[-1] == slug_lower`.
- **[scene_intelligence/sc_log_manual.py:306-324](../../scene_intelligence/sc_log_manual.py#L306-L324)** (bug): Manual follow with unresolved user ID is silently dropped from the tracker (no pending mechanism for follows). log_manual_follow only appends a tracker entry when sc_id is truthy (`if not already and sc_id`). If SI lookup misses and API resolution fails or --no-resolve is used, the follow lands in engagement_log with the note "7-day unfollow timer started" but no track... *Fix:* Add a manually_followed_slugs_pending list mirroring the unfollow path, and print an explicit WARNING that the follow is not tracked when sc_id is empty.

### safety-caps

- **[scene_intelligence/ig_engagement_config.py (11-14, 362-363)](../../scene_intelligence/ig_engagement_config.py)** (safety-cap): SESSION_DAYS/SESSION_HOURS/SC_SESSION_DAYS all stale - coded IG/SC overlap guard validates fiction while real schedules collide Mon and Fri. Config still has SESSION_DAYS = ['Monday','Wednesday','Friday'] (no Saturday, added to the cadence 2026-06-01), SESSION_HOUR_START=10 / SESSION_HOUR_END=11 (the unified slot is 11:00 Berlin, which fails 'SESSION_HOUR_START <= now.hour < SESSION_HOUR_END'), and... *Fix:* Update SESSION_DAYS to include Saturday, widen SESSION_HOUR_END to cover the 11:00 slot, set SC_SESSION_DAYS to ['Monday','Tuesday','Thursday','Friday'] - then either accept the co...
- **[docs/sc-engagement-sop.md:103-108](../../docs/sc-engagement-sop.md#L103-L108)** (safety-cap): SC per-session caps (24 likes / 12 follows / 1 repost / 15 unfollows) have zero code enforcement - --log-action accepts unlimited actions. 4.1.2 declares caps 'per session, never exceeded'. In the autonomous CC path (Chrome clicks + --log-action), nothing enforces them: sc_engagement.py has get_today_action_counts() but it is only consulted by the run_engagement() budget path (which CC never runs... *Fix:* Add a cheap guard to the --log-action handlers: compute get_today_action_counts() and refuse (or print a loud CAP EXCEEDED error requiring --force) once the day's count reaches the...
- **[docs/ig-engagement-sop.md:109-134](../../docs/ig-engagement-sop.md#L109-L134)** (safety-cap): IG daily-load rules (150-call cap, one action session/day, 48-72h detection cooldown) are prose-only; engine preflight never checks whether IG already ran today. 4.1's hard cap ('Hard cap: 150 IG API calls per calendar day'), the action-sessions-one-per-day rule, and 4.2's 48-72h post-detection cooldown are enforced only by CC reciting the pre-flight checklist. In code: ig_engagement.py preflight() checks weekday, hour... *Fix:* Add a tiny shared daily-ledger (e.g. scene_intelligence/ig_daily_calls.json) that every IG-API script increments and checks at startup, refuse to start when a session/JSONL for tod...
- **[docs/sc-engagement-sop.md:120-126](../../docs/sc-engagement-sop.md#L120-L126)** (safety-cap): SC docs require Chrome profile named exactly 'Inch of Shadow' - IG docs say the only correct profile on this machine is 'Amir (Inch of Shadow)'. SOP 4.2 rule 7a and docs/cowork-task-bodies.md (hard rule 3, line 65; PASS 0 B.1, line 101) instruct CC to verify the macOS Chrome profile 'NAMED "Inch of Shadow"' and STOP if it reads anything else. docs/cowork-ig-engagement-body.md line 38 - written after th... *Fix:* Confirm the real Chrome profile name and use the identical exact string ('Amir (Inch of Shadow)' if that is it) in sc-engagement-sop.md 4.2, cowork-task-bodies.md Tasks 1 and 2, an...
- **[docs/sc-engagement-sop.md:137-139](../../docs/sc-engagement-sop.md#L137-L139)** (safety-cap): Blocked-list and personal-network exclusions are not implemented anywhere in the SC engine (2026-06-12 review fix never landed). 4.3 rules 13-14 direct that ig_blocked_accounts.json and ig_personal_network.json be checked 'before any follow/like', and PASS B / task-body C.3 repeat it. Grep of scene_intelligence/sc_engagement.py finds zero references to either file: build_si_queue exclud... *Fix:* Filter discovery output and build_si_queue against both JSONs in sc_engagement.py (match user_id, slug, and normalized name), and add the same check to the sc_follow --log-action h...
- **[docs/cowork-ig-engagement-body.md:308-309](../../docs/cowork-ig-engagement-body.md#L308-L309)** (safety-cap): Own-release-label exclusion lists omit Indigo Children Records; NaNa Disc has no machine-readable flag anywhere. The never-engage list in the live IG body (and ig-engagement-sop.md ~889 and 1134) names only '@mmdiscos, @stereo.society, @nanadisc'. The owner's standing rule covers four labels including Indigo Children Records (Amir's own label). Data check: enriched_conta... *Fix:* Add Indigo Children Records' handles to the never-engage lists in both SOPs/bodies, add all four labels' IG handles to ig_blocked_accounts.json and SC user_ids/slugs to a blocked s...
- **[docs/cowork-ig-engagement-body.md:195-216](../../docs/cowork-ig-engagement-body.md#L195-L216)** (safety-cap): Owner's 'warn when vetted Reach pool <= 30' rule is encoded nowhere - STATE READ only checks queue age. The standing instruction (2026-06-14, after pool exhaustion produced three 0/8-follow sessions and bled active_follows 37->23) requires an unprompted BOLD warning whenever the vetted pending-queue depth is <= 30, checked after every session merge. Neither the ... *Fix:* Add a depth check to ig_merge_session_log.py (count status=='pending' after queue sync; print a loud WARNING at <= 30) and add a matching STATE READ bullet to the Cowork body and S...

### webapp-sec

- **[release_manager/webapp.py:3326-3332](../../release_manager/webapp.py#L3326-L3332)** (security): send-email endpoint accepts arbitrary attachment path with no directory restriction. /api/promotion/check-file carefully restricts paths to the project root (resolve + relative_to(project_root)), but /api/promotion/send-email takes 'attachment' from the JSON body and passes it straight to send_email(), which attaches any readable file on disk ... *Fix:* In api_send_email, run the attachment through the same resolve()+relative_to(PROJECT_ROOT) check as api_check_file (extract a shared helper), and additionally deny dotfiles (.env, ...
- **[release_manager/webapp.py:2296-2297](../../release_manager/webapp.py#L2296-L2297)** (data-integrity): Non-atomic JSON writes to shared data files (enriched_contacts.json, engagement_log.json, promotion_log.json, releases/*.json). All persistence is open(path, 'w') + json.dump with no tmp-file/os.replace, no backup, and no locking: enriched_contacts.json (lines 2296, 2401, 2436, 2487), engagement_log.json (_save_engagement_log 1629-1633), promotion_log.json (_save_promo_log 2526-2530), ... *Fix:* Write to a sibling temp file and os.replace() into place (atomic on APFS), in one shared helper used by all save functions; for enriched_contacts.json also keep a rolling .bak and ...

### rm-rest

- **[release_manager/email_outreach.py:603-605](../../release_manager/email_outreach.py#L603-L605)** (security): SMTP STARTTLS without certificate verification exposes Gmail app password. send_email() calls smtplib.SMTP(...).starttls() with no ssl context. Verified on this machine (system Python 3.9.6): smtplib.SMTP.starttls with context=None uses ssl._create_stdlib_context(), which does NOT verify the server certificate or hostname. login() th... *Fix:* Pass a verifying context: `server.starttls(context=ssl.create_default_context())`, or use smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()).
- **[release_manager/email_outreach.py:600](../../release_manager/email_outreach.py#L600)** (security): Email header injection via unvalidated Subject. send_email() sets msg["Subject"] = subject with no CR/LF sanitization. to_addr is regex-validated (blocks newlines) but subject is not. The webapp passes a client-supplied subject straight through (webapp.py:3307/3332 `subject = data.get("subject", "").strip()... *Fix:* Reject or strip CR/LF from subject (and body headers) in send_email: `if "\n" in subject or "\r" in subject: return {"ok": False, ...}`, or use email.message.EmailMessage with a st...
- **[release_manager/email_outreach.py (567-568, 578, 589-594)](../../release_manager/email_outreach.py)** (security): send_email attaches any caller-supplied filesystem path (local file exfil primitive). attachment_path is read and attached with no allowlist or directory restriction. The only caller (webapp.py:3326 `attachment = data.get("attachment", "").strip()` -> 3332 `send_email(to, subject, body, attachment_path=attachment)`) passes a free-text path from... *Fix:* In send_email (or the webapp route), resolve the path and require it to live under an approved directory (e.g. an epk/ or press_kit/ folder inside the repo): `p = Path(attachment_p...
- **[release_manager/email_outreach.py (53-56, 553-554, 608)](../../release_manager/email_outreach.py)** (safety-cap): Rate limit is in-memory only: resets on every restart and is per-process. The 20/hour and 3s-interval caps are enforced against module-global `_send_log: list[float]`, which is lost whenever the Flask server restarts (RM is routinely relaunched, per the run-detached workflow) and is not shared across processes (a CLI/script importin... *Fix:* Persist send timestamps to a small JSON file (e.g. release_manager/.email_send_log.json) next to the promo log; load it in can_send() and append+write in send_email().
- **[release_manager/email_outreach.py:602-611](../../release_manager/email_outreach.py#L602-L611)** (bug): Send-state gaps allow double-sends and unhandled crashes. Three related issues. (1) The module keeps no per-recipient send record and the sole caller (webapp.py api_send_email, 3300-3350) never checks target["status"] == "sent" before sending, so re-clicking Send re-emails the same label. (2) sendmail() and quit() ar... *Fix:* Wrap quit() separately (or use `with smtplib.SMTP(...)` and treat sendmail success as success), broaden except to (smtplib.SMTPException, OSError), and have the API refuse to send ...
- **[release_manager/cli.py (32-40 (with storage.py:14))](../../release_manager/cli.py)** (bug): CLI is unrunnable: bare sibling imports collide with storage.py's package import. cli.py uses bare top-level imports (`from models import ...`, `from storage import ...`), which only resolve when release_manager/ is sys.path[0], i.e. the documented invocation `python3 release_manager/cli.py`. But storage.py (imported by cli) now does `from ... *Fix:* Convert cli.py to package-relative imports (`from release_manager.models import ...`, same for storage/timeline/checklist/display and the inline `from checklist import _CHECKLIST_T...
- **[release_manager/storage.py:76-81](../../release_manager/storage.py#L76-L81)** (data-integrity): save_release writes release JSON non-atomically. save_release() opens the target file with mode "w" (truncating it) and json.dump()s directly. A crash, SIGTERM (the webapp is known to get SIGTERM'd when run as a background task), or full disk mid-write leaves a truncated/corrupt releases/<slug>.json. load_re... *Fix:* Write to a temp file in the same directory then os.replace(): `tmp = path.with_suffix(".json.tmp"); tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")...

### si-enrich

- **[scene_intelligence/push_to_sheets.py (921, 1062-1064)](../../scene_intelligence/push_to_sheets.py)** (data-integrity): Sync matches contacts by exact display name — duplicate names collide, and Delete flag removes ALL contacts sharing the name. by_name = {c.get("name", ""): c for c in contacts} collapses duplicates (last one wins), so Sheet edits for a duplicated name are applied to an arbitrary one of the records. Worse, the delete pass filters by name: contacts[:] = [c for c in contacts if c.get("n... *Fix:* Give each contact a stable id and write it to a hidden Sheet column; match sync rows by id. Short term: warn on duplicate names at load, and delete at most the single matching reco...
- **[scene_intelligence/push_to_sheets.py (928-932, 1072-1089)](../../scene_intelligence/push_to_sheets.py)** (data-integrity): --prune-deleted can mass-delete contacts when a tab fails to load or a contact was renamed in the Sheet. The prune pass removes every scored contact whose name was not seen in any tab. But (a) a tab that raises WorksheetNotFound (renamed/removed tab) is silently skipped with 'continue', so all its contacts look absent and get pruned; (b) MEMORY.md documents that ... *Fix:* Abort the prune pass if any expected tab failed to load; cap prune count (e.g. refuse if >5% of contacts would be pruned) and require interactive confirmation listing the names fir...
- **[scene_intelligence/push_to_sheets.py (1091-1093, 1138-1139)](../../scene_intelligence/push_to_sheets.py)** (data-integrity): enriched_contacts.json written non-atomically by every SI script. All writers open the live DB with open(path, 'w') and json.dump directly: push_to_sheets.py (2 sites), enrich_soundcloud.py:_save (233-234), enrich_spotify.py:_save (174-175), enrich_youtube.py:_save (249-250), enrich_urls.py (605-606), enrich_contacts.py (326... *Fix:* Add a shared atomic save in utils.py: dump to a temp file in the same directory (explicit encoding='utf-8'), fsync, then os.replace() over the target; use it from all 10 writers.
- **[scene_intelligence/push_to_sheets.py:844](../../scene_intelligence/push_to_sheets.py#L844)** (security): Rows written with USER_ENTERED — formula injection from third-party enrichment data. ws.update(matrix, "A1", value_input_option="USER_ENTERED") lets Sheets interpret cell values. Many cell values originate from third parties (Discogs profile URLs/emails, SoundCloud usernames/descriptions via _parse_user_data, scraped label websites via scrape_... *Fix:* Use value_input_option="RAW" (hyperlinks are already applied separately via updateCells textFormat.link, so USER_ENTERED is not needed), or prefix cells starting with =,+,@ with an...

### si-discover

- **[scene_intelligence/promo_dj_shortlist.py (15-18, 29-31)](../../scene_intelligence/promo_dj_shortlist.py)** (bug): DARK_ELECTRONIC omits downtempo/slowmo/ambient, so a Downtempo release yields zero candidates. genre_match requires _in_scene(release_genre) to be true. DARK_ELECTRONIC has no "downtempo", "slowmo", or "ambient" tokens. The artist's 2026 plan includes a Downtempo/Exotic EP; for such a release _in_scene(release_genre) is False for every contact, so all t... *Fix:* Add downtempo/slowmo/ambient (and other planned release genres) to the family set, or warn loudly when _in_scene(release_genre) is False so the empty result is explained.
- **[scene_intelligence/extract_contacts.py (525-532, 883-884)](../../scene_intelligence/extract_contacts.py)** (bug): _enrich() unconditionally overwrites RA-provided genre, location, and match_score. extract_ra.py writes contacts with populated genre_main/genre_sub (e.g. "Dark Disco"), country in location, and match_score "5"/"4". extract_contacts.py main() then runs `for c in music_contacts: _enrich(c)` over the combined list including RA contacts, and _e... *Fix:* In _enrich, only fill fields that are empty: `if not contact.get("genre_main"): ...` for each of the four fields.
- **[scene_intelligence/discover_curators.py (118-137, 515)](../../scene_intelligence/discover_curators.py)** (data-integrity): filter_existing() does not dedup within the candidate batch - same curator can be inserted twice in one run. main() concatenates Spotify and SoundCloud candidates and passes them through filter_existing(), which only checks each candidate against the pre-run `existing` sets and never adds accepted candidates' keys to those sets. A curator present on both platforms un... *Fix:* Inside the loop, after accepting a candidate, add dedup_key(c["name"]) (and its platform ids) to the existing sets so subsequent batch members dedup against it.
- **[scene_intelligence/ig_enrich_instagram.py (420-425, 443)](../../scene_intelligence/ig_enrich_instagram.py)** (bug): rate_limited results are appended to the progress file twice. In the rate_limited branch the result is appended to `results` and save_progress() is called; the code then falls through to the unconditional `results.append(result)` at line 443 and saves again, so every rate-limited handle is recorded twice in ig_enriched_c... *Fix:* Remove the append/save inside the rate_limited branch (the fallthrough already does it), or `continue` semantics via a flag.
- **[scene_intelligence/ig_enrich_instagram.py (386-388, 447)](../../scene_intelligence/ig_enrich_instagram.py)** (bug): --resume never retries failed/rate-limited handles, contradicting the on-screen instruction. done_handles is built from ALL progress entries regardless of status (`{r["handle"].lower() for r in results}`), and targets are filtered against it. Handles that previously returned status error, rate_limited, or auth_error are therefore skipped forever on ev... *Fix:* Build done_handles only from entries with status == "ok" (matching load_targets), e.g. `{r["handle"].lower() for r in results if r.get("status") == "ok"}`.
- **[scene_intelligence/ig_enrich_instagram.py (174-177, 374-384)](../../scene_intelligence/ig_enrich_instagram.py)** (safety-cap): Chrome profile chosen by cookie count with no check that the session is @inch_of_shadow. extract_ig_cookies() picks whichever Chrome profile has the most instagram.com cookies with a sessionid. The machine has 5 Chrome profiles (4 named "Amir..."; a wrong-profile IG session incident occurred 2026-06-10 per project SOP). The session verification st... *Fix:* After the current_user check, hard-fail unless me['username'] == 'inch_of_shadow' (or a configured expected handle); optionally restrict cookie extraction to the "Amir (Inch of Sha...
- **[scene_intelligence/scene_plan_recency_filter.py:93-97](../../scene_intelligence/scene_plan_recency_filter.py#L93-L97)** (bug): fetch_fail candidates are dropped from the plan, contradicting the in-code 'keep unknown recency' comment. The comment says unknown-recency candidates are kept ("not proven stale"), but the code appends to `keep` only for verdict == "no_recency". Verdicts "fetch_fail" (transient network/HTTP failure) and "private" are excluded from keep, so at line 109 they are rem... *Fix:* Also keep verdict == "fetch_fail" (matching the comment), or retry once before dropping; keep dropping only proven-stale and private.

### root-tools

- **[sc_auth_callback.py (24-30, 75)](../../sc_auth_callback.py)** (security): OAuth flow has no state parameter (login CSRF). The authorization URL printed at line 75 contains no `state` value, and the /callback handler accepts any `code` without validating a state parameter. While the one-shot server is listening on localhost:8080, any webpage the user visits can redirect the browse... *Fix:* Generate a random state with secrets.token_urlsafe(), append &state=... to the auth URL, and reject callbacks whose state param does not match.
- **[stats/collectors.py:197-201](../../stats/collectors.py#L197-L201)** (data-integrity): SC token refresh overwrites token file and drops obtained_at used by other scripts. _sc_refresh_token writes the raw refresh response verbatim: `json.dump(new_data, f)`. Unlike scene_intelligence/sc_engagement.py (line 332: `new_data["obtained_at"] = time.time()`), it does not preserve/set obtained_at. scene_intelligence/sc_build_browser_sess... *Fix:* Set new_data['obtained_at'] = time.time() before dumping (matching sc_engagement.py), and merge into the existing file's dict instead of replacing it wholesale.
- **[stats/storage.py:100-103](../../stats/storage.py#L100-L103)** (data-integrity): manual_entries.json rewritten non-atomically; crash mid-write loses all manual history. save_manual_entry loads the whole entries list and rewrites MANUAL_FILE in place with open('w') + json.dump. If the process dies mid-write (or two webapp requests race, since /api routes call this concurrently via webapp.py line 3436), the single file holding ... *Fix:* Write to a temp file in the same directory and os.replace() onto MANUAL_FILE; optionally keep a .bak of the previous version.

### agents-skills

- **[.claude/agents/ig-expert.md:81-82](../../.claude/agents/ig-expert.md#L81-L82)** (safety-cap): Indigo Children Records missing from every never-engage label list (all three agents). The standing hard rule covers four labels: MM Discos, Stereo Society, NaNa Disc, and Indigo Children Records (Amir's own label, aka ICR). ig-expert line 81-82, sc-expert line 47 ('own-release labels (MM Discos / Stereo Society / NaNa Disc)'), and promotion-exp... *Fix:* Add 'Indigo Children Records (ICR, Amir's own label)' to the exclusion lists in .claude/agents/ig-expert.md, sc-expert.md, and promotion-expert.md (and the engagement SOPs).
- **[.claude/skills/enrich/SKILL.md (18-19,30)](../../.claude/skills/enrich/SKILL.md)** (safety-cap): /enrich fires SoundCloud API calls without the mandatory pre-announce-and-wait step. Amir's standing HARD RULE: pre-announce every SC API call with an estimated call count and wait for confirmation. The enrich skill runs enrich_soundcloud.py (SC resolve + search over hundreds of contacts) directly, including as part of --all, with no pre-annou... *Fix:* Add to Step 2: 'Before running enrich_soundcloud.py, estimate the SC API call count (roughly 1-2 calls per un-enriched contact in the selected categories), announce it, and wait fo...
- **[.claude/skills/release/SKILL.md:32-34](../../.claude/skills/release/SKILL.md#L32-L34)** (safety-cap): ig_fetch_insights.py runs (release capture stage and ig-expert) without the never-2-IG-scripts-same-day check. The IG risk hard rules say NEVER two IG automation scripts on the same day, with a pre-run checklist. The release skill's capture stage runs ig_fetch_insights.py after pre-announcing the call count, but never checks whether a CC engagement session ran (or is s... *Fix:* In both files, before running ig_fetch_insights.py: check the day against the Mon/Wed/Fri/Sat cadence and the tracker's last_session / today's session JSONL; if an engagement sessi...
- **[docs/ig-session-scorecard.md:26-38](../../docs/ig-session-scorecard.md#L26-L38)** (data-integrity): Scorecard stopped at 06-24; sessions on 06-26, 07-01, and 07-04 unscored and 06-22 still 'TBD'. The standing rule (2026-06-21) is to rate EVERY IG engagement session after its integrity check. The last scored row is 2026-06-24, and 2026-06-22 is still '_TBD_'. Evidence of later sessions: git commit 37c7377 'merge 06-26', tracker stats last_session=2026-0... *Fix:* Backfill rows for 06-26 and 07-01 from their merged JSONLs/reports, resolve the 06-22 TBD, score 07-04 after its integrity check, and update the trend line. Consider making the sco...

### cross-cutting

- **[runsync:1-3](../../runsync#L1-L3)** (bug): runsync and sync.sh cd to the wrong directory - scripts cannot work as written. Both tracked helper scripts `runsync` and `sync.sh` cd to `/Users/amir/Desktop/Inch of Shadow` (the parent folder) and then run `python3 scene_intelligence/push_to_sheets.py --prune-deleted`. Verified there is no `scene_intelligence/` directory in the parent f... *Fix:* Change both scripts to `cd "/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode"` (or `cd "$(dirname "$0")"`), and consider dropping the hardcoded --prune-deleted flag given the 'n...


## Unverified Findings - Low Severity


### ig-core

- **[scene_intelligence/ig_engagement.py:993-1001](../../scene_intelligence/ig_engagement.py#L993-L1001)** (bug): Hidden list (engagement_log 'hidden', 95 entries) is not applied to the Reach follow path. build_scene_pool receives and honors the hidden set (via contact_is_always_skip), but build_reach_pool's signature takes only blocked and personal -- the 95-entry eng_log['hidden'] list is never consulted for follow targets. A handle deliberately hidden from e... *Fix:* Pass the hidden set into build_reach_pool and reject queue entries whose normalised handle is in it.
- **[scene_intelligence/ig_live_driver.py:278-281](../../scene_intelligence/ig_live_driver.py#L278-L281)** (bug): like_post counts an unconfirmed like when the 200 response body is not JSON. The confirmation contract is 'True only if Instagram confirmed the like (status=ok)', but the fallback returns True for any HTTP 200 whose body fails to parse as JSON (e.g. an HTML interstitial served with 200). The engine then logs the like as done and burns ... *Fix:* Return False in the except branch -- non-JSON responses are unconfirmed by definition; the engine's backfill logic already handles False correctly.
- **[scene_intelligence/ig_engagement.py:2132-2138](../../scene_intelligence/ig_engagement.py#L2132-L2138)** (data-integrity): save_session_report silently wipes all session history if the file is unreadable. If session_reports.json exists but fails to parse (partial write by another tool, encoding issue), the bare `except Exception: existing = {}` resets the store and the subsequent _atomic_write_json overwrites the file with only the current session, destroying t... *Fix:* On parse failure, rename the corrupt file to session_reports.json.corrupt-<ts> before writing fresh, and print a loud warning instead of silently discarding history.
- **[scene_intelligence/ig_engagement.py:1382-1400](../../scene_intelligence/ig_engagement.py#L1382-L1400)** (bug): SessionResult.errors is never populated and unexpected exceptions skip the session report entirely. result.errors is declared, printed in main (line 2324-2327), and persisted in save_session_report, but no code path ever appends to it. run_session catches only CircuitBreakerTripped; any other exception propagates out of run_session (state files are saved in ... *Fix:* Wrap the run_session body's per-action calls in a broad except that appends str(exc) to result.errors and halts gracefully, so the finally-persist and the post-run report always ex...

### ig-support

- **[scene_intelligence/ig_merge_session_log.py:104-107](../../scene_intelligence/ig_merge_session_log.py#L104-L107)** (bug): _date_from_ts falls back to merge-day date, not the session's target_date. For events lacking a parseable ts (a demonstrated Cowork field-slip class), _date_from_ts returns str(date.today()) - the day the merge is run, not the session date being merged. Merging a past session (a documented usage: 'ig_merge_session_log.py 2026-05-08',... *Fix:* Thread target_date into _date_from_ts callers and use it as the fallback instead of date.today().
- **[scene_intelligence/ig_merge_session_log.py:79-80](../../scene_intelligence/ig_merge_session_log.py#L79-L80)** (bug): Naive event timestamps are assumed UTC; a Berlin-local naive ts would falsely trip the fabrication guard by up to 2h. _parse_ts does dt.replace(tzinfo=timezone.utc) for offset-less timestamps. All 1142 archived events so far carry +02:00 offsets, but if Cowork ever writes naive Berlin local time (CEST=UTC+2), the parsed value sits up to 2h in the future of the file's true UTC... *Fix:* Assume Europe/Berlin (or the local timezone) for naive timestamps, or widen tolerance only for naive-ts events while flagging the format problem.
- **[scene_intelligence/ig_merge_session_log.py:444-483](../../scene_intelligence/ig_merge_session_log.py#L444-L483)** (data-integrity): Merge is not idempotent: failure after the engagement-log write but before archive leads to double-appended events on re-run. Write order is engagement_log (465) -> tracker (469) -> queue (475) -> archive JSONL (482). update_queue_from_events line 381 does queue_data["_meta"][...] without setdefault (KeyError if a queue file ever lacks _meta), and shutil.move can fail; any exception ... *Fix:* Use setdefault for _meta, archive the JSONL only after all writes succeed (already the case) but also record merged source_file names and refuse to re-merge a date already present ...
- **[scene_intelligence/ig_merge_session_log.py (235, 313)](../../scene_intelligence/ig_merge_session_log.py)** (data-integrity): Tracker rewrite via username-keyed dict silently collapses duplicate/empty-username active_follows entries. update_tracker_from_events builds active_by_name keyed on lowercased username and then unconditionally replaces tracker['active_follows'] with list(active_by_name.values()) whenever any count changed. Any pre-existing duplicate usernames (or multiple entries w... *Fix:* Detect and warn when len(active_by_name) != len(active) before rewriting.
- **[scene_intelligence/ig_reconcile_followings.py:238-239](../../scene_intelligence/ig_reconcile_followings.py#L238-L239)** (data-integrity): Decrementing stats.total_followed for drifted entries corrupts the follow-back-rate denominator. Reconcile does stats['total_followed'] = max(0, total_followed - len(drifted)). Drift covers both 'follow never landed' AND 'unfollowed outside protocol / account blocked us' - for the latter cases the follow genuinely happened and should stay in the ever-foll... *Fix:* Do not decrement total_followed for drift (or split drift into 'never_landed' vs 'dropped' and only decrement the former, if distinguishable).
- **[scene_intelligence/ig_audit_queue_freshness.py:571-574](../../scene_intelligence/ig_audit_queue_freshness.py#L571-L574)** (data-integrity): Non-atomic direct writes to shared JSON state (queue, paid seed, roster) unlike sibling scripts. ig_audit_queue_freshness.py writes QUEUE_FILE with a direct write_text (no tmp+rename), and likewise ig_followback_checker.py:425 (PAID_FILE.write_text) and ig_follower_audit.py:156/163 (roster/shortlist). The merge script and tracker saver use atomic tmp+os.r... *Fix:* Reuse the merge script's _atomic_write helper (tmp + os.replace) in all three scripts; optionally add an fcntl lock around tracker read-modify-write.
- **[scene_intelligence/ig_show_automation_follows.py:117](../../scene_intelligence/ig_show_automation_follows.py#L117)** (bug): History viewer reads 'unfollowed_at'/'date' keys, blind to the merge script's 'unfollowed_date' (124 of 157 entries). Companion symptom of the history-schema drift: the viewer's fallback chain omits 'unfollowed_date', the key used by the majority writer (ig_merge_session_log.py). Verified in the live tracker: 124 entries carry unfollowed_date and would print '?', vs 30 with u... *Fix:* Add 'unfollowed_date' to the fallback chain (u.get('unfollowed_at') or u.get('unfollowed_date') or u.get('date','?')) until the schema is unified.

### sc-core

- **[scene_intelligence/sc_engagement.py:454-464](../../scene_intelligence/sc_engagement.py#L454-L464)** (bug): 429 handling sleeps the Retry-After, then still returns failure without retrying — the wait is wasted and counts toward the failure breaker. On a soft 429, _user_request sleeps retry_after seconds and then returns None. The caller (sc_put/sc_delete) treats None as failure, incrementing the consecutive-failure counters. Two soft 429s in a row therefore halt follows for the session (MAX_CONSECUTIVE_F... *Fix:* After sleeping a sub-threshold Retry-After, retry the request once; only return None if the retry also fails.
- **[scene_intelligence/sc_engagement.py:1860-1861](../../scene_intelligence/sc_engagement.py#L1860-L1861)** (data-integrity): Unfollow log-key derivation checks source == 'discovery' but 239 tracker entries are 'discovery_v2' — unfollow logged under a different key than the follow. At follow time, discovery items are logged under contact_key 'discovery_{uid}' (set in discover_related_artists). At unfollow time, run_unfollow_sweep rebuilds the key and only uses the 'discovery_{uid}' form when entry.source == 'discovery'; the tracker curre... *Fix:* Use entry.get('source', '').startswith('discovery') for the key choice (mirroring the fix in build_full_queue).

### sc-support

- **[scene_intelligence/sc_weekly_health.py:154-164](../../scene_intelligence/sc_weekly_health.py#L154-L164)** (bug): _paginate re-sends params={"limit": 200} on next_href URLs that already carry query params. The first request builds ?limit=200 correctly, but next_href already contains the full query string (cursor/offset/limit). requests appends the extra limit=200, producing duplicate query parameters on every follow-up page. check_sc_follows.py:64-79 has the sam... *Fix:* Only pass params on the first request; follow next_href verbatim with params=None.
- **[scene_intelligence/sc_log_manual.py (166-168, 190-192)](../../scene_intelligence/sc_log_manual.py)** (data-integrity): Non-atomic writes to shared engagement_log.json and sc_follow_tracker.json, no backup. _save_eng_log and _save_tracker json.dump directly onto the live files that the engagement engine and weekly health pass read. A crash/Ctrl-C mid-dump truncates the file; the loaders in this same script then silently fall back to an EMPTY default dict (lines 1... *Fix:* Write to <file>.tmp then os.replace(); and make the loaders raise (or refuse to save) on JSONDecodeError instead of returning an empty default.
- **[scene_intelligence/sc_weekly_health.py (79, 303-312)](../../scene_intelligence/sc_weekly_health.py)** (data-integrity): sc_following_audit.json is written by two scripts with incompatible schemas, clobbering each other. save_audit here writes {fetched_at, total_following, total_followers, mutual_count}; check_sc_follows.py:227-234 writes {not_in_si, in_si_no_data, matched_count, total_following} to the SAME path (scene_intelligence/sc_following_audit.json, git-tracked). Which... *Fix:* Give the weekly-health snapshot its own filename (e.g. sc_follow_snapshot.json) or nest both payloads under distinct keys.
- **[scene_intelligence/release_weekly_health.py:95-97](../../scene_intelligence/release_weekly_health.py#L95-L97)** (bug): Checklist rendering uses item["label"] (KeyError) while everything else uses .get. overdue/upcoming tuples index item["label"] directly. Every other field access in this function is defensive (.get). Verified current releases/*.json all have label on all 55 checklist items, so this is latent, but one hand-edited or programmatically-added ite... *Fix:* Use item.get("label", "(unnamed item)").

### webapp-sec

- **[release_manager/webapp.py:1601-1626](../../release_manager/webapp.py#L1601-L1626)** (bug): _load_engagement_log has no corruption handling, unlike _load_promo_log. _load_engagement_log calls json.load with no try/except (lines 1603-1605). _load_promo_log (2509-2523) and _load_contacts (1640-1645) both handle JSONDecodeError/OSError, but the engagement log does not. Combined with the non-atomic write finding, a truncated ... *Fix:* Mirror _load_promo_log: wrap in try/except (json.JSONDecodeError, OSError), back the corrupt file up to .bak, and return the empty default structure.
- **[release_manager/webapp.py:136](../../release_manager/webapp.py#L136)** (security): Open redirect via Referer header in CSRF error handler. The CSRF error handler for non-API paths redirects to request.referrer, an attacker-controlled request header, with no same-origin check. A cross-site form POST to a page route (which by definition fails CSRF) bounces the browser to the attacker's Referer URL. *Fix:* Only redirect to request.referrer if urlparse(request.referrer).netloc in ('', request.host); otherwise fall back to url_for('dashboard').
- **[release_manager/templates/engagement.html:92](../../release_manager/templates/engagement.html#L92)** (security): Contact URLs from scraped SI data rendered as hrefs with no scheme validation (javascript: possible). Server-rendered templates emit contact-controlled URLs directly into href attributes: engagement.html lines 92, 147, 190-191, 223, 283; promotion_target_row.html line 6; release_detail.html line 394 (premiere contacts); sc_automation.html line 145. Jinja autoe... *Fix:* Add a Jinja filter mirroring app.js safeUrl (allow only http(s)/mailto) and apply it to every contact/seed/target URL in templates; also tighten _extract_social_links to require th...
- **[release_manager/templates/sc_automation.html:381-389](../../release_manager/templates/sc_automation.html#L381-L389)** (security): Server error strings and profile fields injected via innerHTML without escaping. testAuth() and the runEngine/runUnfollowOnly error paths interpolate data.error, data.username, follower counts, etc. into innerHTML template literals without the escapeHtml() helper that is defined at line 522 and used for action labels. data.error can contai... *Fix:* Wrap all interpolated values in the existing escapeHtml() (lines 382, 385, 389, 430, 440, 466, 472), or set textContent on a child span instead of innerHTML.
- **[release_manager/templates/stats.html:236-237](../../release_manager/templates/stats.html#L236-L237)** (security): Chart.js loaded from third-party CDN without SRI, contrary to local-first/privacy project rules. The stats page pulls chart.js@4 and chartjs-adapter-date-fns@3 from cdn.jsdelivr.net with floating major-version tags and no integrity/crossorigin attributes. Project rules (CLAUDE.md) require preferring local/self-controlled solutions and no third-party servi... *Fix:* Vendor both bundles into release_manager/static/ (matching how fonts were handled), or at minimum pin exact versions and add integrity= SRI hashes.
- **[release_manager/webapp.py:2218-2228](../../release_manager/webapp.py#L2218-L2228)** (safety-cap): log-follow endpoint silently resets the 7-day unfollow timer and enforces no daily follow cap. POST /api/engagement/log-follow unconditionally overwrites log['follows'][key] with today's date, so re-logging a handle already in the tracker resets its 7-day unfollow countdown with no warning, and the duplicate follow event is prepended to the log. There i... *Fix:* If key already exists in log['follows'], keep the original date (or return {'ok': True, 'duplicate': True}); include follows_today in the response and return a warning flag when it...
- **[release_manager/webapp.py:685-686](../../release_manager/webapp.py#L685-L686)** (bug): Unhandled ValueError on numeric form fields (track BPM, video trim) returns 500. track_new (line 686) and track_edit (line 732) do float(bpm_str) and video_resizer_page does float(trim_start_str)/float(trim_end_str) (lines 1156-1157) with no try/except. Non-numeric input (possible via non-HTML5 clients, pasted text with units, or locale co... *Fix:* Wrap conversions in try/except ValueError, flash a validation error and re-render the form (use validate_bpm for range checking).
- **[release_manager/webapp.py:1170-1175](../../release_manager/webapp.py#L1170-L1175)** (bug): Video resizer error re-renders omit release_options, emptying the metadata release dropdown. The two early-return error paths in video_resizer_page ('Not a video file' at 1170-1175 and 'No video selected' at 1195-1200) call render_template without release_options and preselected_release, although video_resizer.html iterates release_options at line 107... *Fix:* Pass release_options=release_options and preselected_release=preselected_release in both error-path render_template calls (or build a shared kwargs dict).
- **[release_manager/webapp.py:1719-1720](../../release_manager/webapp.py#L1719-L1720)** (bug): Non-numeric match_score crashes engagement queue build with ValueError. _build_platform_queue does int(raw_score) whenever the value is non-empty, so a contact whose match_score is e.g. 'n/a', '3.5', or a stray word (the field syncs back from hand-edited Google Sheets) raises ValueError and 500s the /engagement page and /api/engag... *Fix:* Use the same try/except int() fallback as promotion_page (default 2), ideally via a shared _score(contact) helper used in all four places.
- **[release_manager/webapp.py:304-313](../../release_manager/webapp.py#L304-L313)** (bug): Artwork upload with a new extension leaves the old file in place; find_artwork may keep serving the stale image. release_artwork saves to artwork/{slug}{ext} but never removes an existing artwork with a different extension, and find_artwork iterates ARTWORK_EXTENSIONS — a set with arbitrary iteration order — returning the first slug.{ext} that exists. If slug.jpg exists ... *Fix:* In release_artwork, delete (or rename to .bak) any existing artwork/{slug}.* with a different extension before saving; and make find_artwork check a deterministic, preference-order...
- **[release_manager/webapp.py:127-138](../../release_manager/webapp.py#L127-L138)** (security): Silent no-CSRF fallback when Flask-WTF is missing, and broken template rendering in that mode. If flask_wtf fails to import, the app starts with csrf=None: every state-changing endpoint (delete release, remove SI contact, send email, SC automation run) loses CSRF protection with only this silent degradation. Worse, that fallback is not actually usable: ... *Fix:* Fail hard at startup if Flask-WTF is missing (raise SystemExit with an install hint), or register a csrf_token() stub returning '' AND refuse non-GET requests in the fallback.
- **[release_manager/webapp.py:2929-2935](../../release_manager/webapp.py#L2929-L2935)** (security): State-changing GET requests: /promotion?release= writes release context, press-kit GET mutates promo log. promotion_page (a GET route) calls set_active_release_context, persisting state to disk and re-steering the Engagement queue; /api/promotion/press-kit/<slug> (GET, lines 3148-3151) sets press_kit_generated=True and saves the promo log. GET requests are not cov... *Fix:* Move the context write to the existing POST /api/context/release (have the page JS call it on selector change) and make press-kit generation a POST, or at minimum gate the writes o...

### rm-rest

- **[release_manager/storage.py:115-121](../../release_manager/storage.py#L115-L121)** (bug): find_release partial-match path skips schema migration and load guards. The partial-match branch json.load()s candidate files raw: it neither calls _migrate_distribution() (unlike load_release and list_releases) nor wraps json.load in the try/except that the exact-match path has. An old-schema release found via partial slug is ret... *Fix:* Reuse load_release for candidates: `rel = load_release(path.stem); if rel: candidates.append(rel)` — that gets both the migration and the corrupt-file guard for free.
- **[release_manager/contact_bridge.py (213-221 vs 236-239)](../../release_manager/contact_bridge.py)** (bug): Score bonus 'Email available' contradicts has_email and boosts NO DEMOS labels. The +1 scoring bonus uses `(demo_email not in ("DM ONLY", "NO DEMOS")) or discogs_email` — so a label whose demo_email is explicitly "NO DEMOS" still gets +1 'Email available' if any discogs_email exists. The has_email flag computed a few lines later uses diff... *Fix:* Make the bonus use the same rule as has_email: `has_real_email = demo_email not in ("DM ONLY", "NO DEMOS") and bool(demo_email or discogs_email)` (and skip the bonus entirely when ...
- **[release_manager/models.py:47-54](../../release_manager/models.py#L47-L54)** (bug): make_slug can return an empty slug for non-ASCII/symbol-only titles. make_slug strips everything outside [a-z0-9]; a title made only of symbols or non-Latin characters (e.g. umlauts-only or Cyrillic) yields "" (release_type choices always contribute letters via cli, but webapp callers passing type differently could hit it; a ti... *Fix:* Transliterate (unicodedata.normalize('NFKD').encode('ascii','ignore')) before the regex and fall back to a timestamp-based slug when the result is empty or equals just the type.

### si-enrich

- **[scene_intelligence/classify_subtypes.py (154-157, 332-340)](../../scene_intelligence/classify_subtypes.py)** (data-integrity): Hardcoded _DELETE_NAMES silently deletes contacts on every run. Every run removes any contact whose lowercase name is in _DELETE_NAMES ('feinstoffberlin'). If that contact is ever re-added (e.g. re-discovered by a discovery script or restored from the Sheet), it is silently deleted again with only a one-line log. This runs... *Fix:* Remove the delete step (the one-shot cleanup already happened) or move it behind an explicit --apply-deletions flag; better, use a no_longer_engage/blocked flag instead of deletion...
- **[scene_intelligence/enrich_contacts.py (77-81, 95-101)](../../scene_intelligence/enrich_contacts.py)** (bug): Discogs 429 handling sleeps but never retries — rate-limited lookups recorded as 'not found'. _get sleeps 15s on HTTP 429 and then returns None without retrying the request. search_discogs treats None as no result, so enrich_label/enrich_dj return _EMPTY and the contact is stamped discogs_found=False / verification_status '✗' even though the lookup was... *Fix:* After the sleep, retry the request once (as enrich_soundcloud.py and enrich_spotify.py already do).
- **[scene_intelligence/enrich_urls.py:465-479](../../scene_intelligence/enrich_urls.py#L465-L479)** (bug): Contact name interpolated into SPARQL via str.format — braces crash the run, quotes break the query. wikidata_pass builds the query with _WD_VENUE_QUERY.format(name_lower=search_name) where search_name derives from the contact name. A name containing '{' or '}' raises KeyError/ValueError from str.format and crashes the whole pass (before the end-of-run save, ... *Fix:* Escape or strip '{', '}', '"' and '\\' from search_name before formatting (search_name is already lowercased/cleaned; add re.sub(r'[{}"\\\\]', '', ...)), and save after each pass r...
- **[scene_intelligence/update_scores.py:40-43](../../scene_intelligence/update_scores.py#L40-L43)** (bug): Contacts missing the match_score key entirely are skipped by the score patcher. The check 'if contact.get("match_score") != ""' returns None for contacts that lack the key (e.g. records added by discovery/curator scripts that never went through normalize_raw_contacts), and None != "" is True, so they are counted as 'already scored' and ne... *Fix:* Use 'if contact.get("match_score"):' (or str(...).strip()) so both missing and empty values are patched.
- **[scene_intelligence/push_to_sheets.py:1152-1154](../../scene_intelligence/push_to_sheets.py#L1152-L1154)** (bug): Sync summary miscounts: prunes reported as edits, duplicate delete flags double-counted. changes accumulates field edits + len(deleted) + len(pruned), and deleted can contain the same name multiple times (once per tab/duplicated email row where the Delete flag appears). main() then prints 'Synced: {edits - deletes} edits, {deletes} deletions', whi... *Fix:* Deduplicate the deleted list (use a set) and return edits, deletions, and prunes as separate counters.

### si-discover

- **[scene_intelligence/fetch_youtube_subs.py (151-153, 219-220)](../../scene_intelligence/fetch_youtube_subs.py)** (data-integrity): Partial fetch after mid-pagination error overwrites the previous complete subscriptions.csv. fetch_subscriptions() `break`s out of the pagination loop on any HTTP error or request exception, returning whatever pages were fetched so far. main() writes that partial list over the existing subscriptions.csv as long as it is non-empty (only the fully-empty... *Fix:* Track whether pagination completed; on partial failure either refuse to overwrite the CSV or write to a temp file and warn.
- **[scene_intelligence/curator_enrich.py:71-83](../../scene_intelligence/curator_enrich.py#L71-L83)** (data-integrity): _upsert only merges on non-empty spotify_id; rows without owner id duplicate on every run, and saves never refresh. _upsert matches only `row.get("spotify_id") and c.get("spotify_id") == row["spotify_id"]`. If Spotify returns a playlist whose owner block lacks an id (or the owner field is missing), the built row has spotify_id "" and is appended as a new contact on every en... *Fix:* Fall back to dedup_key(name) matching when spotify_id is empty, and refresh `saves` on merge.
- **[scene_intelligence/extract_contacts.py (360, 386)](../../scene_intelligence/extract_contacts.py)** (bug): Duplicate dict key "viewlexx" in KNOWN_GENRE_MAP. KNOWN_GENRE_MAP literally contains "viewlexx": ("Electronic", "Electro") twice (lines 360 and 386). The second silently wins (values happen to be identical today), but the duplication signals unreviewed map growth and would silently mask a divergent edit. *Fix:* Remove the duplicate entry (line 386).
- **[scene_intelligence/ig_enrich_instagram.py:97](../../scene_intelligence/ig_enrich_instagram.py#L97)** (security): tempfile.mktemp used for the copied Chrome cookie DB. The decrypted-cookie workflow copies the Chrome Cookies sqlite DB to a path from tempfile.mktemp(), which is deprecated and race-prone (predictable name, created non-atomically). On a single-user Mac the practical risk is low, but the file transiently holds se... *Fix:* Use tempfile.NamedTemporaryFile(delete=False) or tempfile.mkstemp() and keep the existing unlink in finally.
- **[scene_intelligence/ig_fetch_insights.py:52-56](../../scene_intelligence/ig_fetch_insights.py#L52-L56)** (bug): Non-JSON HTTP error body crashes _get with an unhandled JSONDecodeError; URLError not handled. _get catches only urllib.error.HTTPError and immediately json.loads the error body; Meta occasionally returns HTML error pages (5xx), which raises json.JSONDecodeError and aborts the run with a traceback. Plain network failures (urllib.error.URLError, timeout)... *Fix:* Wrap json.loads in try/except returning ({"error": {"message": body[:200]}}), and catch URLError with a clear message.

### root-tools

- **[sc_auth_callback.py:59-63](../../sc_auth_callback.py#L59-L63)** (security): Reflected XSS: query 'error' param echoed unescaped into HTML. The `error` query parameter (fully attacker-controlled if a malicious page redirects the browser to localhost:8080/callback) is interpolated directly into an HTML response without escaping. Line 56 similarly reflects r.text from the token endpoint. Contained b... *Fix:* Wrap interpolated values in html.escape(), or return Content-type: text/plain.
- **[sc_auth_callback.py:43-44](../../sc_auth_callback.py#L43-L44)** (security): OAuth token file written with default (world-readable) permissions. The SoundCloud user token (write access to tracks/profile) is saved via plain open(TOKEN_FILE, 'w'), producing mode 0644 under the default umask. stats/collectors.py _sc_refresh_token (lines 199-200) rewrites the same file the same way. The file is correctly i... *Fix:* os.chmod(TOKEN_FILE, 0o600) after writing (or open with os.open(..., 0o600)) in both writers.
- **[artwork_resizer.py (251-255, 1046-1048)](../../artwork_resizer.py)** (bug): --open flag is a no-op: Finder is always opened. An --open flag is defined ("Open the resized/ folder in Finder automatically when done") but args.open is never read. main() unconditionally runs `subprocess.run(["open", str(output_dir)])` for every non-dry-run invocation, including --delete-adjacent or scrip... *Fix:* Change the guard to `if args.open and not args.dry_run:`.
- **[stats/storage.py:33-35](../../stats/storage.py#L33-L35)** (data-integrity): Snapshot writes are non-atomic (contained: corrupt snapshots are skipped). save_snapshot writes each snapshot with a plain open('w'); an interrupted daily_sync leaves a truncated snapshot_*.json. list_snapshots (lines 44-50) silently skips unreadable files, so that day's data point is lost without any warning, and get_growth quietly ... *Fix:* Temp-file + os.replace() pattern; have list_snapshots log skipped/corrupt files instead of `except Exception: continue`.
- **[stats/collectors.py:241-242](../../stats/collectors.py#L241-L242)** (bug): SoundCloud tracks response not handled if API returns paginated dict (followers path handles it, tracks path does not). collect_soundcloud handles both list and {"collection": [...]} shapes for /me/followers (lines 272-274) but iterates /me/tracks JSON directly. If SoundCloud returns the paginated dict shape for tracks (it does when linked_partitioning is on, and the API has sh... *Fix:* Mirror the followers handling: `data = r2.json(); if isinstance(data, dict): data = data.get("collection", [])`.
- **[stats/bandcamp_import.py:63](../../stats/bandcamp_import.py#L63)** (bug): Unhandled ValueError on malformed 'paid to you' field crashes the webapp route. The try/except only wraps reading the CSV (lines 44-49). Inside the row loop, `float(r.get("paid to you", 0) or 0)` raises ValueError on any non-numeric value (currency symbol, thousands separator, localized decimal comma, or a stray summary row). parse_bandca... *Fix:* Wrap the conversion (strip currency symbols/commas, fall back to 0.0 on ValueError) or extend the try block around the whole parse.
- **[description_scorer.py:94-104](../../description_scorer.py#L94-L104)** (bug): load_limits parses non-limit quick-reference entries into bogus char limits. load_limits takes the FIRST integer in every value of character_limits_quick_reference. The specs file (verified) contains non-limit entries, so limits gains e.g. spotify_pitch_optimal_timing=31, soundcloud_tags_max=5, youtube_hashtags=3, instagram_hashtags=3,... *Fix:* Only accept keys already in FALLBACK_LIMITS (or whitelist *_bio/*_description/*_caption/*_pitch fields), or require the value to be a bare int / start with the digits.
- **[image_generator.py:146-148](../../image_generator.py#L146-L148)** (bug): URL image download lacks status check; error page saved as .png. If the API returns a url instead of b64_json, the bytes are taken from requests.get(...).content without raise_for_status(). A 403/expired-URL HTML body would be written to generated_images/ as a corrupt PNG and reported as "Saved:". *Fix:* r = requests.get(url, timeout=60); r.raise_for_status(); return r.content.

### agents-skills

- **[.claude/agents/sc-expert.md:45-48](../../.claude/agents/sc-expert.md#L45-L48)** (safety-cap): Own-label protection claimed 'automatic' but rests solely on a flag only mm.discos actually carries. The unfollow-sweep spec says the no_longer_engage exclusion 'automatically protects own-release labels (MM Discos / Stereo Society / NaNa Disc)'. In the live tracker (scene_intelligence/sc_follow_tracker.json, 386 follows) the only own-release label carrying n... *Fix:* Add an explicit name deny-list to the agent ('regardless of flags, never propose engaging or sweeping MM Discos, Stereo Society, NaNa Disc, Indigo Children Records, or known person...
- **[.claude/skills/bio/SKILL.md:114](../../.claude/skills/bio/SKILL.md#L114)** (bug): Duplicated filename in the fallback warning ('artist_profile.json or artist_profile.json'). The final note names the same file twice; the second reference was presumably meant to be a different file (e.g. release_manager/seo_platform_specs.json or the bios key inside the profile). Everything else in the skill checks out against the code: bio_manager.... *Fix:* Change the second reference to the intended file, likely `release_manager/seo_platform_specs.json`, or to 'the `bios` key inside artist_profile.json'.
- **[.claude/agents/ig-expert.md:9-38](../../.claude/agents/ig-expert.md#L9-L38)** (safety-cap): ig-expert's mandatory reading list omits docs/ig-status.md, the merge-first check, and the pool<=30 warning duty. ig-expert reads CC's state files 'every run' for analysis and writes ig_next_session_brief.md, but its read-first list omits docs/ig-status.md (which declares itself 'read this first in any new IG conversation') and docs/ig-session-scorecard.md. It also encode... *Fix:* Add to the read-first list: docs/ig-status.md + latest session report; add two duties: 'if the newest ig_session_*.jsonl is not yet merged, tell Amir to run ig_merge_session_log.py...

### cross-cutting

- **[credentials.json:1](../../credentials.json#L1)** (security): Google service-account private key file is world-readable (mode 0644). credentials.json (the GOOGLE_CREDENTIALS_FILE service-account key used by gspread) sits in the repo root with permissions -rw-r--r--, readable by any local user/process. By contrast .env is correctly 0600 (-rw-------). The file is properly gitignored and never... *Fix:* chmod 600 credentials.json (and youtube_oauth.json / youtube_token.json / .sc_user_token.json / .sc_browser_state.json / .flask_secret if they are also group/world-readable).


## Documentation Drift (docs/skills/SOPs vs code)


### safety-caps

- **[docs/sc-engagement-sop.md:140](../../docs/sc-engagement-sop.md#L140)** (doc-drift): SOP claims --log-action sc_follow refuses permanently_unfollowed re-follows - the code has no such check. SOP 4.3.16 (line 140) and 7.4 item 2 (line 634: 'Refuses if the user_id is already in the tracker (idempotent) or in permanently_unfollowed') claim the sc_follow log handler enforces never-re-follow. docs/cowork-task-bodies.md line 339 repeats it ('the engine'... *Fix:* Add a permanently_unfollowed check to the sc_follow --log-action handler (refuse with a clear error), or correct the claim in SOP 4.3.16 / 7.4 and cowork-task-bodies.md line 339 un...
- **[docs/cowork-ig-engagement-body.md (228, 344, 399, 537)](../../docs/cowork-ig-engagement-body.md)** (doc-drift): Live IG Cowork body still runs Phase 1b (8/20/7) while config advanced to Phase 2 (10/25/8) on 2026-07-02. ig_engagement_config.py line 21 sets CURRENT_PHASE = 2 ('Phase 2 -- scaling (10 follows / 8 unfollows / 25 likes). Advanced from 1b on 2026-07-02 (Amir approved)'). The Cowork task body CC executes was last updated 2026-06-26 and still hard-codes Phase 1b ever... *Fix:* Update the body's session section, interleave cycle, unfollow count, and report template to Phase 2 numbers (10 follows / 25 likes / 8 unfollows), or better, make the body referenc...
- **[docs/ig-engagement-sop.md (573 vs 1152-1189)](../../docs/ig-engagement-sop.md)** (doc-drift): Followback reminder day contradicts itself: 5 table says Thursday, 6.2 task body routes Sunday. The protocol table (line 573) says the followback reminder moved to 'Thu 11:00 Berlin ... (moved from Sun after 2026-06-01 cadence change so it lands on a silent-skip day, never stacked with an action session)'. But 6.2 - the section containing the actual Cowo... *Fix:* Rewrite 6.2's heading and body for Thursday routing to match the 5 table (and update the in-body 'Sunday 11:00' strings and 6.3's rationale which still says 'Sunday already has the...
- **[docs/sc-agent-context.md (51-57, 317)](../../docs/sc-agent-context.md)** (doc-drift): SC agent-context schedule is stale: says Monday quiet / Saturday engagement, opposite of the live Mon/Tue/Thu/Fri cadence. CC is told to read this briefing first, every session, before the SOP. Its 3 daily-workflow table says 'Mon: Quiet day. No engagement.' and lists 'Sat 11:30 Sc weekly engagement'; the 13 card says 'Tue/Thu/Fri/Sat 11:30 -> engagement'. The live cadence (docs/c... *Fix:* Update 3 and 13 to Mon/Tue/Thu/Fri 11:30 engagement, Wed health, Sun sweep, Sat off; refresh the 1 follower snapshot and active-release line or mark them 'as of' with a pointer to ...
- **[docs/ig-agent-context.md (347-357, 592, 734-738, 999-1005)](../../docs/ig-agent-context.md)** (doc-drift): IG agent-context (required session reading, authority #3) predates every cadence/phase change: Mon 11:59/Wed 12:23/Fri 13:15, Sun followback, Tue/Thu/Sat SC days, Phase 1 current. The Cowork body orders CC to read this file fully before every session, and its authority order ranks it above config comments. It is frozen at 2026-05-05: 7 cadence table has per-day times Mon 11:59 / Wed 12:23 / Fri 13:15 with no Saturday session and Sunday ... *Fix:* Do a dated refresh pass of 3, 5, 7, 13, 14, 20, 22, 26 against the current SOP/config, or demote the file with a banner ('schedule/phase values here are historical - SOP and ig_eng...

### agents-skills

- **[.claude/agents/sc-expert.md:75-79](../../.claude/agents/sc-expert.md#L75-L79)** (doc-drift): Session-rating rubric contradicts the agent's own 2026-07-03 targeting update (100-600 vs 100-1000). The 'Targeting' section (lines 28-36) was updated 2026-07-03: ceiling 1000, spread ~4/4/4 across 100-300 / 300-600 / 600-1000, and docs/sc-engagement-sop.md line 341-348 matches ('SPREAD THE BAND (updated 2026-07-03 for the 600-1000 EXPERIMENT)'). But the clos... *Fix:* Update line 76-77 to '100-300 / 300-600 / 600-1000 band spread ~4/4/4 (per the 2026-07-03 experiment; revert to 100-600 if the experiment is rolled back)'.
- **[docs/ig-status.md (1-14,42-47)](../../docs/ig-status.md)** (doc-drift): ig-status.md ('single source of truth, read this first') is ~3 weeks stale and self-inconsistent. Header says 'Last updated: 2026-06-15' yet the body contains rules dated 2026-06-26 (recency filter, reciprocator recovery). The 'Current state (verified 2026-06-15)' block claims total_followed=103 / total_unfollowed=91 / last_session 06-15, but the live trac... *Fix:* Refresh the doc after each merged session (or per week): update the header date, current-state counters from the tracker, blocked list (add 80mgddevon), pool depth, and prune the c...

### ig-core

- **[scene_intelligence/ig_engagement_config.py:27-31](../../scene_intelligence/ig_engagement_config.py#L27-L31)** (doc-drift): Stale SESSION_JITTER rationale contradicts Phase 2 limits. The jitter comment still says 'Never exceeds the strategy doc's "safe" 20 likes/session by more than 2' and '8 possible values (15-22)', written when likes_per_session was 20. CURRENT_PHASE=2 sets likes_per_session=25 (since 2026-07-02), so actual per-session ... *Fix:* Update the comment to reflect Phase 2 numbers and state the true worst-case daily like count including prominent and like-before-follow likes.

### ig-support

- **[scene_intelligence/ig_audit_queue_freshness.py:26-27](../../scene_intelligence/ig_audit_queue_freshness.py#L26-L27)** (doc-drift): Docstring undercounts API cost: 'audit of 25 entries = 25 calls' is now up to ~50. Since the 2026-06-08 recency restoration (acknowledged in the comment at lines 399-404: 'Two calls per candidate (~2x cost)'), each candidate that reaches the recency stage costs a web_profile_info call plus a feed/user call, so --count 25 can spend ~50 calls ... *Fix:* Update the docstring to 'up to 2 calls per candidate (~50 for the default 25)' and print the actual call count at the end of a run.

### sc-core

- **[scene_intelligence/sc_engagement_config.py (19-26, 40, 243-248)](../../scene_intelligence/sc_engagement_config.py)** (doc-drift): Config comments drift from behavior: 'auto-reverts after boost window', 'well under' the 50/day ceiling at exactly 50, and stale 600-ceiling prose. Three documented claims don't match reality: (1) line 26 says aggressive 'auto-reverts after boost window ends' but mode is a per-invocation CLI arg with no revert mechanism anywhere in sc_engagement.py; (2) lines 19-21 claim 'Likes: ~50/day hard ceiling... Al... *Fix:* Reword the comments: state that mode must be manually passed/reverted, drop 'well under' for aggressive likes (or lower to 45), and update the 600 references to 'DISCOVERY_FOLLOW_C...

### sc-support

- **[scene_intelligence/check_sc_follows.py (12-13, 135-140, 165)](../../scene_intelligence/check_sc_follows.py)** (doc-drift): Promised report C (tracker entries no longer followed) never produced; tracked_ids and following_ids dead code. The module docstring promises "C) SC follow tracker entries that are no longer in your following list". tracked_ids (lines 135-140) and following_ids (line 165, populated at 165/155) are computed but never compared or printed; the printed section labeled C is ... *Fix:* Either implement the tracker-vs-following diff using tracked_ids & following_ids, or update the docstring and delete the dead variables.
- **[scene_intelligence/sc_weekly_health.py (329-333, 367)](../../scene_intelligence/sc_weekly_health.py)** (doc-drift): Report label "Pending (within 14-day window)" is wrong: no window is applied. pending counts every tracker entry that is neither followed_back nor no_longer_following, with no date filtering at all. Entries followed months ago and never cleaned count as "within 14-day window". Note also sc_log_manual.py starts a 7-day timer (unfollow_af... *Fix:* Either filter by followed_at >= today-14d (or unfollow_after) or relabel the line "Pending (never followed back, still following)".
- **[scene_intelligence/sc_build_browser_session.py:76-77](../../scene_intelligence/sc_build_browser_session.py#L76-L77)** (doc-drift): Both session-builder scripts tell the user to test with a --test flag that no longer exists. sc_build_browser_session.py:77 and sc_extract_chrome_cookies.py:305 print "Test with: python3 scene_intelligence/sc_browser_likes.py --test <track_url>", but sc_browser_likes.py's argparse only defines --verify (lines 259-262); --test produces "unrecognized ar... *Fix:* Change both hints to `python3 scene_intelligence/sc_browser_likes.py --verify`.

### safety-caps

- **[docs/ig-engagement-sop.md (17, 589, 902, 1361-1364, 1434, 1471)](../../docs/ig-engagement-sop.md)** (doc-drift): IG SOP describes Phase 1/1b as current and 'Mon/Wed/Fri only' - both stale vs config Phase 2 and the Mon/Wed/Fri/Sat cadence. The SOP that CC must 'read completely at the start of every IG session' still says: 1 'currently Phase 1 (10 follows / 20 likes / 0 unfollows per session)' (line 17); protocol table 'Phase 1b session: 8 follows + 20 likes + N unfollows' (589); '== PHASE 1B SES... *Fix:* Sweep the SOP for phase references: mark the phase tables as reference-only, state 'current phase lives in ig_engagement_config.py CURRENT_PHASE', and fix the 15 quick-ref day list...
- **[docs/ig-engagement-sop.md:259](../../docs/ig-engagement-sop.md#L259)** (doc-drift): Session hard cap documented as 50 minutes while SESSION_MAX_MINUTES was raised to 60 on 2026-07-02. 4.7 says 'Hard session cap | 50 minutes (was 35; bumped 2026-05-11)', and both the SOP body (1080-1083) and cowork-ig-engagement-body.md 532-533 say 'target <= 50 minutes (SESSION_MAX_MINUTES in ig_engagement_config.py)' - citing the config symbol with a stale... *Fix:* Update the three doc references to 60 minutes, or phrase them as 'the value of SESSION_MAX_MINUTES (currently 60)' so a config change does not silently invalidate the docs.
- **[docs/cowork-ig-engagement-body.md:283](../../docs/cowork-ig-engagement-body.md#L283)** (doc-drift): Scene exclusion 'match_score < 3' contradicts config tiers lowered to min_score=2 on 2026-06-15. The body's Scene EXCLUDE list (line 283) and ig-engagement-sop.md 869 say to exclude 'match_score < 3 (below engagement-tier minimum)', and the 10 tier table (1380-1381) still labels Tiers 3/4 as 'score 3'. Config ENGAGEMENT_TIERS lines 159 and 171 set min_sco... *Fix:* Change the exclusion to 'match_score < 2' in the body and SOP 869, and update the 10 tier table rows to 'score 2-3' for Tiers 3/4.
- **[docs/sc-engagement-sop.md:491-494](../../docs/sc-engagement-sop.md#L491-L494)** (doc-drift): Release-boost follow cap says 18/day; config aggressive mode says 20/day. 6.4 hard rules cap boost follows at 'Follows: 18 per day', while sc_engagement_config.py MODES['aggressive'] (the release-boost mode per the config comment 'Aggressive: release windows only (sc-release-boost)') sets follows_per_day = 20, and the SOP's own 10 t... *Fix:* Pick one number (18 or 20) and align 6.4, 10, and MODES['aggressive'] in sc_engagement_config.py.
- **[docs/ig-engagement-sop.md:1198](../../docs/ig-engagement-sop.md#L1198)** (doc-drift): SOP claims followback checker has a 'hard cap' of 60 API calls per run - no cap exists in the script. 6.2 states 'Hard caps: 60 API calls per run (today's tracker has 47 pending follows, well under).' ig_followback_checker.py contains no per-run call limit at all - it iterates every active follow with 2-5s pauses and only aborts on an actual HTTP 429. The 'cap... *Fix:* Add a MAX_CALLS_PER_RUN=60 guard to ig_followback_checker.py (process oldest entries first, defer the rest to the next run), or correct the SOP to say the volume is bounded only by...

### webapp-sec

- **[release_manager/templates/seo_copy.html:7](../../release_manager/templates/seo_copy.html#L7)** (doc-drift): Page claims generated copy is 'never stored' but the API persists it into the release JSON. The SEO Copy page subtitle says copy 'is generated from your release metadata and never stored', but api_seo_copy_generate (webapp.py:1412-1433) writes the generated copy into rel['seo_copy'] and calls save_release, and release_detail.html renders that stored ... *Fix:* Change the subtitle to say the copy is saved to the release and viewable on the release detail page.
- **[release_manager/templates/engagement.html:277](../../release_manager/templates/engagement.html#L277)** (doc-drift): Unfollow section says 'followed 10+ days ago' but the code threshold is 7 days. The Unfollow Ready hint text states 10+ days, while _get_unfollow_queue uses days_since >= 7 (webapp.py:1909-1915) and the follows list countdown uses days_left = max(0, 7 - days_since) (webapp.py:2117), so accounts appear as 'ready' 3 days earlier than the co... *Fix:* Update the hint to 7+ days, or centralize the threshold in one constant referenced by both the code and the template.

### rm-rest

- **[release_manager/contact_bridge.py (14, 30)](../../release_manager/contact_bridge.py)** (doc-drift): Docstring claims module reads enriched_contacts.json; the path constant is never used. _ENRICHED_CONTACTS_FILE is defined but never opened anywhere in the module; contacts are passed in by callers (webapp). The module header says 'Reads enriched_contacts.json locally.' Verified positive for the owner rule: contact_bridge performs zero writes to ... *Fix:* Delete the unused constant or update the docstring to say contacts are supplied by the caller.
- **[release_manager/email_outreach.py:48-49](../../release_manager/email_outreach.py#L48-L49)** (doc-drift): GMAIL_ADDRESS / GMAIL_APP_PASSWORD env vars not documented in CLAUDE.md API keys list. email_outreach.py requires GMAIL_ADDRESS and GMAIL_APP_PASSWORD from .env, but CLAUDE.md's 'API Keys (in .env)' section lists only SPOTIFY/DISCOGS/GOOGLE/ANTHROPIC/YOUTUBE/SOUNDCLOUD keys. CLAUDE.md's tool table also still says Tool 4 (Email Outreach) is 'Not ... *Fix:* Add GMAIL_ADDRESS, GMAIL_APP_PASSWORD to the CLAUDE.md API keys list and update the tool status table.
- **[release_manager/cli.py:4](../../release_manager/cli.py#L4)** (doc-drift): cli.py header calls Release Manager 'Tool 3'; CLAUDE.md says Tool 2. The module docstring labels this 'Tool 3 — Release Manager'. Per CLAUDE.md the Release Manager is Tool 2 and Tool 3 is the Promotion Engine. *Fix:* Change the docstring to 'Tool 2 — Release Manager'.

### si-discover

- **[scene_intelligence/curator_extract_routes.py (10, 26)](../../scene_intelligence/curator_extract_routes.py)** (doc-drift): Docstring advertises --names-file but the actual flag is --urls-file. The module usage block says `--names-file <json list of top_playlist_url>` while argparse defines `--urls-file`. Anyone (including an agent) copying the documented command gets an argparse error. *Fix:* Change the docstring to --urls-file.
- **[scene_intelligence/ig_enrich_instagram.py:23-25](../../scene_intelligence/ig_enrich_instagram.py#L23-L25)** (doc-drift): Header documents a stale project path (~/Documents/Claude/Inchofshadowcode). The run instructions in the module docstring say `cd ~/Documents/Claude/Inchofshadowcode`; the project lives at ~/Desktop/Inch of Shadow/Inchofshadowcode. The script itself uses Path(__file__)-relative paths so it works from anywhere, but the doc misleads. *Fix:* Update or remove the cd line.

### root-tools

- **[artwork_resizer.py:48-51](../../artwork_resizer.py#L48-L51)** (doc-drift): Comment claims decompression-bomb guard but the limit is raised above Pillow's default. Pillow's built-in decompression-bomb threshold is ~178,956,970 pixels. Setting Image.MAX_IMAGE_PIXELS = 250_000_000 loosens the guard rather than adding one, while the comment presents it as protection. *Fix:* Reword the comment to say the default limit is deliberately raised to accommodate large masters, or keep Pillow's default if no legitimate master exceeds it.
- **[sc_auth_callback.py:1-6](../../sc_auth_callback.py#L1-L6)** (doc-drift): Doc says 'Delete this file after use' but file is kept and depended on. The module docstring instructs deleting the script after use, yet it remains checked in and is the canonical way to (re)mint .sc_user_token.json, which stats/collectors.py and the SC engagement stack depend on. The instruction no longer reflects reality. *Fix:* Update the docstring to describe it as the permanent SC re-auth helper (and add the missing state-param handling while touching it).

### agents-skills

- **[.claude/skills/promo/SKILL.md:4](../../.claude/skills/promo/SKILL.md#L4)** (doc-drift): Example slug 'the-deciver-single' in argument-hints does not match any release file. Both promo (line 4) and release (line 4) skills use 'the-deciver-single' as the example slug. The releases/ directory contains only farewell-single.json and the-deceiver-single.json. Step 1 of both skills resolves the slug by matching a file in releases/, so a... *Fix:* Correct to 'the-deceiver-single' in .claude/skills/promo/SKILL.md line 4 and .claude/skills/release/SKILL.md line 4.

### cross-cutting

- **[CLAUDE.md:58-59](../../CLAUDE.md#L58-L59)** (doc-drift): CLAUDE.md dependency list is stale vs requirements.txt. CLAUDE.md 'Dependencies (requirements.txt)' lists 10 packages, but requirements.txt on disk has 16: it additionally pins google-auth-oauthlib, openai, rembg, onnxruntime, Flask-WTF, and defusedxml. The doc also omits the runtime-but-unpinned playwright/browser... *Fix:* Update the CLAUDE.md dependency line to match requirements.txt (add google-auth-oauthlib, openai, rembg, onnxruntime, Flask-WTF, defusedxml).


## Improvement Suggestions


### ig-core

- **[scene_intelligence/ig_engagement.py:2294-2299](../../scene_intelligence/ig_engagement.py#L2294-L2299)** (improvement): No vetted-pool depth warning (<=30 must warn loudly) anywhere in the plan/session flow. The owner's standing rule requires a bold, unprompted warning whenever the vetted Reach pool depth is <=30. build_reach_pool already computes the full eligible set before truncating to the session cap (line 1113-1114), and neither print_plan, write_session_pla... *Fix:* Have build_reach_pool return the pre-cap eligible count, and in print_plan/main print a bold '[WARNING] Vetted Reach pool depth N <= 30 -- rebuild queue' banner when it is at or be...

### sc-core

- **[scene_intelligence/sc_engagement.py:1383-1394](../../scene_intelligence/sc_engagement.py#L1383-L1394)** (improvement): Discovery re-fetches tracks for rejected candidates once per seed encounter — seen_ids only records accepted candidates. In discover_related_artists, seen_ids.add(uid) happens only after a candidate passes every filter. A candidate rejected by the recency or genre check (the common case — recent refreshes yield ~16/50) is re-processed, including a fresh fetch_recent_tracks() API... *Fix:* Add uid to seen_ids (or a separate rejected_ids set) immediately after it passes the cheap in-band checks, before the track fetch, so each uid is evaluated at most once per run.

### rm-rest

- **[release_manager/seo_copy_generator.py:269-286](../../release_manager/seo_copy_generator.py#L269-L286)** (improvement): No validation of generated copy against platform character limits or expected schema. generate_copy() trusts the model to 'Always respect character limits exactly' (system prompt, line 124) but never checks the returned fields: no length check against the per-field limits stated in the prompts (spotify_pitch 490, artist_pick 135, youtube titles... *Fix:* After json.loads, validate each expected key: type-check, enforce max lengths from a limits table (source them from seo_platform_specs.json), and either flag violations in the retu...

### cross-cutting

- **[requirements.txt:1-16](../../requirements.txt#L1-L16)** (improvement): playwright and browser_cookie3 used at runtime but missing from requirements.txt. Three modules import playwright (scene_intelligence/sc_engagement.py:151) and browser_cookie3 (scene_intelligence/ig_enrich_instagram.py:114, scene_intelligence/sc_extract_chrome_cookies.py:90), but neither package is pinned in requirements.txt. All three impo... *Fix:* Add `playwright>=1.40.0` and `browser-cookie3>=0.19.0` to requirements.txt (or a requirements-automation.txt if they should stay optional), and have the except branches print an ex...

### ig-core

- **[scene_intelligence/ig_engagement.py:1184-1192](../../scene_intelligence/ig_engagement.py#L1184-L1192)** (improvement): Unfollow sweep shields only keep_following personal accounts, not the full personal network. plan_unfollow_sweep checks `handle in keep_following` (only entries with keep_following=true in ig_personal_network.json), not the full personal set. A friend present in the personal file without the keep_following flag who somehow entered active_follows would... *Fix:* Pass the full personal set into plan_unfollow_sweep and skip any handle in it, with reason 'personal_network_never_touch'.

### ig-support

- **[scene_intelligence/ig_queue_builder.py (510-511, 593-612)](../../scene_intelligence/ig_queue_builder.py)** (improvement): 'Update existing queue entries' branch is dead code - existing entries' seed_count/metadata never refresh. The filter loop skips any handle already in the queue ('if handle in existing_handles: continue' at 511), so 'passed' can never contain an existing handle, making the 'if h in existing_by_handle' update branch (599-612) unreachable. The comment 'Update existin... *Fix:* Move the existing-handle check after the overlap map is built: update existing entries' seed_count/seeds from the fresh overlap data, and only skip them for the add-new path.
- **[scene_intelligence/ig_follower_audit.py:159-162](../../scene_intelligence/ig_follower_audit.py#L159-L162)** (improvement): Dead reach() helper; shortlist sort duplicates its logic inconsistently. The reach(f) function (verified accounts weighted 10,000,000) is defined but never used; the actual sort uses a different lambda (verified first, then known followers). Harmless today but a trap: someone editing the ranking will change reach() and see no effec... *Fix:* Delete reach() or use it as the sort key; guard main() with 'if not uid: raise SystemExit' after _resolve_uid.

### sc-support

- **[scene_intelligence/sc_unfollow_cleanup.py:1](../../scene_intelligence/sc_unfollow_cleanup.py#L1)** (improvement): Deprecated one-line stub with zero callers - safe, can be deleted. File content is a single comment: deprecated marker. Repo-wide grep (py/md/json) finds no imports, subprocess calls, or doc references to sc_unfollow_cleanup anywhere, so nothing breaks by its emptiness. Importing/compiling it is a no-op. *Fix:* Delete the file, or keep it only if the comment is intentionally the tombstone of record.

### webapp-sec

- **[release_manager/webapp.py:108](../../release_manager/webapp.py#L108)** (improvement): No MAX_CONTENT_LENGTH on file uploads and no content sniffing on artwork upload. The Flask app never sets MAX_CONTENT_LENGTH, so upload endpoints (release_artwork line 841, artwork resizer line 994, video resizer line 1186) accept unbounded request bodies. release_artwork additionally validates only the filename extension (line 834-835), n... *Fix:* Set app.config['MAX_CONTENT_LENGTH'] (e.g. 2 GB for video, or per-route checks), and verify artwork uploads open with PIL (Image.open + verify) before accepting.

### rm-rest

- **[release_manager/bio_manager.py (54-58, 188-206)](../../release_manager/bio_manager.py)** (improvement): save_profile non-atomic; generated bios not length-validated. save_profile() truncate-writes artist_profile.json directly (same corruption window as storage.save_release; this file holds all 7 canonical bios). generate_bios() validates only that at least one platform key exists — it never checks the char limits it demand... *Fix:* Use write-temp-then-os.replace for save_profile; add a per-platform max-length check in generate_bios mirroring the prompt limits; guard load_profile with try/except returning {}.

### si-enrich

- **[scene_intelligence/scrape_label_emails.py (70-81, 98-103, 31-36)](../../scene_intelligence/scrape_label_emails.py)** (improvement): Scraper: no delay between labels or on Bandcamp, spoofed browser UA, no robots.txt handling, nondeterministic email pick. Rate limiting is only the 0.3s sleep between subpages of one website; scrape_bandcamp has no sleep at all and there is no delay between labels, so consecutive Bandcamp-hosted labels hammer bandcamp.com back-to-back (7 pages per site x N labels). The UA is a sp... *Fix:* Add a per-domain delay (e.g. 1-2s) including between labels and inside scrape_bandcamp; use the project's honest User-Agent; sort emails before picking the fallback.
- **[scene_intelligence/enrich_youtube.py (244-250, 337)](../../scene_intelligence/enrich_youtube.py)** (improvement): _save strips _uploads_playlist after every batch, so Phase 3 re-fetches playlists Phase 1 just retrieved. phase_direct stores contact["_uploads_playlist"] from the channels.list response, but _save (called after every 50-contact batch and at the end of Phase 1) pops the field from ALL contacts before writing. When phase_activity runs in the same invocation (--all)... *Fix:* Strip the transient key only from a copy used for serialization (or keep a separate cid->playlist dict in memory instead of storing it on contacts).
- **[scene_intelligence/push_to_sheets.py (561-568, 928-935)](../../scene_intelligence/push_to_sheets.py)** (improvement): worksheet() metadata fetches bypass the rate limiter. _rate_limit() wraps most calls, but spreadsheet.worksheet(title) in _get_or_create_ws and in sync_from_sheet each perform an API metadata fetch that is not counted in _api_calls. main() additionally calls _get_or_create_ws twice more per Labels/DJs tab for row... *Fix:* Call _rate_limit() before every spreadsheet.worksheet()/fetch_sheet_metadata() call, and cache worksheet handles in main() instead of re-fetching for the colouring passes.

### si-discover

- **[scene_intelligence/extract_rekordbox.py:430-433](../../scene_intelligence/extract_rekordbox.py#L430-L433)** (improvement): Writes enriched_contacts.json with no --dry-run flag and no backup. Unlike discover_curators.py (timestamped backup) and discover_contacts.py (--dry-run), extract_rekordbox.py always appends and rewrites the mature enriched_contacts.json on every invocation. It is append-only and dedups by name, so risk is contained, but it is... *Fix:* Add --dry-run and reuse the timestamped-backup helper pattern from discover_curators.py before writing.
- **[scene_intelligence/curator_check_adds.py:27](../../scene_intelligence/curator_check_adds.py#L27)** (improvement): Playlist scan capped at 400 tracks; adds to longer playlists are silently missed. fetch_playlist_track_ids caps pagination at max_pages=4 (4 x 100 tracks). Genre mega-playlists commonly exceed 400 tracks; if the release track was added near the end, track_in_playlist returns False and the curator is never marked 'added'. *Fix:* Use the playlist's tracks.total to page fully (with a sane hard cap), or check the most-recent pages first since adds land at the end.
- **[scene_intelligence/ig_enrich_helper.py:54-78](../../scene_intelligence/ig_enrich_helper.py#L54-L78)** (improvement): Orphaned helper patches contacts by positional _index - fragile if ever reused. save_results() writes ig_* fields into enriched_contacts.json by raw list index (`contacts[idx][k] = v`) captured at some earlier load. No file in the repo imports ig_enrich_helper (verified by grep), so it is dead code today - but if any future caller compute... *Fix:* Delete the module, or rekey the patch by IG handle/name like patch_enriched_contacts() in ig_enrich_instagram.py does.

### root-tools

- **[stats/daily_sync.py:30-41](../../stats/daily_sync.py#L30-L41)** (improvement): daily_sync exits 0 and saves a snapshot even when every collector fails. collect_all never raises; if all four platforms error (expired IG token, dead SC token, etc.) daily_sync still writes a snapshot with an empty platforms dict and exits 0, so cron/launchd sees success. get_overview will then show the empty snapshot as "latest" ... *Fix:* sys.exit(1) (or at least skip save_snapshot) when result['platforms'] is empty; consider exiting non-zero whenever errors is non-empty so cron mail/monitoring fires.
- **[image_generator.py:186-199](../../image_generator.py#L186-L199)** (improvement): art/card --reference uploads local images to OpenAI without the privacy notice other modes print. restyle prints "Note: restyle uploads your source photo to OpenAI's servers." (line 529) and composite prints an equivalent note (line 539), but generate_art with --reference opens the reference files and sends them to client.images.edit with no notice. Given ... *Fix:* Print the same style of note when references are passed in art/card modes.

### agents-skills

- **[.claude/agents/ig-expert.md:43-53](../../.claude/agents/ig-expert.md#L43-L53)** (improvement): Canva master (1080x1350) is center-cropped to 1080x1080 by the prescribed resizer step. The Canva flow generates instagram_post at 1080x1350 (4:5), then routes the export through 'artwork_resizer.py <master-path> --release <slug> --only instagram'. Verified in artwork_resizer.py lines 88-89: the instagram group exports exactly social_instagram_po... *Fix:* Either add a 1080x1350 instagram feed export to artwork_resizer.py's EXPORTS, or instruct the agent to design safe-area-aware (keep key elements in the central square) and to use -...
- **[.claude/skills/discover/SKILL.md (26,52-54)](../../.claude/skills/discover/SKILL.md)** (improvement): Default '/discover' with no flags runs three API crawls and offers a Sheets push with no confirmation gates. With no arguments the skill runs Spotify + YouTube + Discogs crawls and appends up to 100 contacts to the shared enriched_contacts.json, then offers classify + push_to_sheets. There is no step to show the user the candidate list before it is appended (only --d... *Fix:* Make the no-flag default a --dry-run preview, show the top candidates, and only append after the user confirms; keep the Sheets push behind a second explicit confirm (it already as...
- **[.claude/agents/promotion-expert.md:39-43](../../.claude/agents/promotion-expert.md#L39-L43)** (improvement): Promotion-expert exclusions could be made checkable: no instruction to verify against SI no_longer_engage flags or the blocked list. The exclusion section says 'Never pitch anyone flagged no-engage anywhere you can see it' but names no concrete files/fields to check besides ig_personal_network.json. The concrete flags exist: no_longer_engage in sc_follow_tracker.json and enriched_contacts.j... *Fix:* List the exact files/fields to cross-check for every shortlist: scene_intelligence/ig_blocked_accounts.json, ig_personal_network.json accounts, and any contact/tracker entry with n...

### cross-cutting

- **[requirements.txt:1-16](../../requirements.txt#L1-L16)** (improvement): pytest used by the 14-file test suite but not pinned anywhere. tests/ contains 14 test files (71 tests, all passing) that require pytest to run, but pytest appears in no requirements file. It currently works only because pytest happens to be installed in the user's Python 3.9 site-packages. *Fix:* Add `pytest>=7.0.0` to requirements.txt or a requirements-dev.txt.
- **[=1.1.3:1](../../=1.1.3#L1)** (improvement): Stray shell-redirect artifact file '=1.1.3' in repo root. The repo root contains a file literally named `=1.1.3` whose entire content is `(eval):1: command not found: pip` - the artifact of a shell command like `pip install piexif >=1.1.3` where the version spec was parsed as an output redirect. It is already listed ... *Fix:* Delete the file and remove the `=1.1.3` line from .gitignore.


## Audit Gaps (completeness critic)

- FILE COVERAGE (.py): complete. All 91 .py files outside .git map to a unit: 6 root + 5 stats (root-tools), 14 release_manager (webapp-sec + rm-rest), 52 scene_intelligence (sc-core/sc-support/ig-core/ig-support/si-enrich/si-discover), 14 tests (cross-cutting read all fully). No orphan .py files.
- MISSED FILES - deployment/scheduling layer (no unit had these in scope): /Users/amir/Desktop/Inch of Shadow/Inchofshadowcode/scene_intelligence/run_ig_session.sh, scene_intelligence/com.inchofshadow.ig-engagement.plist, deploy/com.inchofshadow.sc-health-refresh.plist, run_sc_enrich.command (all four are git-tracked). cross-cutting audited only runsync and sync.sh.
- HIGH-RISK MISS inside that gap: run_ig_session.sh line 27 runs '"$PYTHON" scene_intelligence/ig_engagement.py --live --no-preflight' - a headless LIVE IG session with preflight explicitly disabled, scheduled Mon/Wed/Fri 10:00 by com.inchofshadow.ig-engagement.plist. The plist is NOT currently installed in ~/Library/LaunchAgents (verified), but it sits tracked in the repo one 'launchctl load' away from colliding with the Cowork Mon/Wed/Fri sessions that safety-caps analyzed. Nobody audited this file or reconciled it with the never-2-IG-scripts-same-day rule.
- MISSED RUNTIME STATE: two launch agents ARE installed and loaded (~/Library/LaunchAgents/com.inchofshadow.sc-health-refresh.plist runs sc_weekly_health.py Sun+Wed 08:00; com.inchofshadow.stats-sync.plist, which exists ONLY outside the repo, runs stats/daily_sync.py). launchctl list shows both with last exit status 2 (currently failing). sc-support flagged sc_weekly_health's un-budgeted discovery calls but nobody connected it to the fact it runs UNATTENDED twice weekly, bypassing the SC-API pre-announce hard rule; root-tools' daily_sync 'exits 0 even when all collectors fail' finding also never met the evidence that the agent is exiting 2.
- MISSED FILE: run_sc_enrich.command (repo root, tracked) chains 'enrich_soundcloud.py --force' then '--all' - a full re-enrichment of ~750+ SC profiles in one double-click with no confirmation, directly relevant to the SC-API pre-announce rule. si-enrich audited enrich_soundcloud.py itself but not this wrapper.
- LENS NEVER RUN - live state tracked in git: sc_follow_tracker.json, ig_follow_tracker.json, engagement_log.json, ig_target_list.json, enriched_contacts.json (with ~120 contact emails / PII) plus 25 discovery_candidates_*.json are git-TRACKED and sit modified in the working tree. Any git checkout/restore/stash/merge rolls live trackers back to stale state - the exact 'stale tracker' failure class from the 2026-06-10 incident. No remote is configured (verified git remote -v empty) so no exfil angle, but nobody assessed rollback risk or PII-in-history.
- LENS NEVER RUN - test adequacy: tests/ covers only curator/promo/merge-guard helpers (14 files, 71 tests). Zero tests exist for sc_engagement.py (2496 lines), ig_engagement.py (2332 lines), ig_live_driver.py, webapp.py, email_outreach.py - precisely the code where the critical/high findings cluster. cross-cutting ran the suite but no unit flagged the coverage hole.
- LENS NEVER RUN - Claude harness permissions: .claude/settings.local.json allow-list contains "Bash(python3 -c \":*)" which auto-approves python3 -c one-liners, i.e. arbitrary Python execution without a prompt, and "Bash(python3 scene_intelligence/enrich_youtube.py)" which auto-approves a live YouTube-API script. No unit examined harness permission config.
- MISSED FILES - operational instruction docs that steer live CC sessions: scene_intelligence/ig_next_session_brief.md (untracked, feeds the next session), scene_intelligence/sc_session_report_*.md / ig_session_report_*.md / session briefs, docs/ig-clip-glue-template.md (new, untracked), docs/brand/*, docs/boost_reports/*. safety-caps explicitly declared 'session brief files - outside scope'; no other unit picked them up, so a stale/wrong brief steering a real session is unchecked.
- SKIMMING ADMISSIONS worth a follow-up pass: webapp-sec read only ~50% of release_manager/static/app.js (2665 lines) closely and 'representative' functions of stats.js (sink greps mitigate but do not equal line-by-line); cross-cutting grepped docs/ and plans/ for secret patterns only; agents-skills verified cross-references by grep only in docs/ig-agent-context.md etc. (acceptable - safety-caps read those fully); sc-core skipped sc_weekly_health.py internals (acceptable - sc-support read it fully).
- LENS NEVER RUN - data-as-config validation: release_manager/seo_platform_specs.json character limits/fields were never checked against the platforms' actual current limits (rm-rest audited the generator, root-tools audited the parser; nobody audited the spec values that all copy-length decisions depend on). Same for scene_intelligence/label_tiers.json thresholds. Low priority but genuinely uncovered.
- SANITY CHECK on findings distribution: no suspicious absences found. sc-core (1 critical + 4 high), ig-core (4 high), si-enrich (3 high confirmed) are proportionate to risk; webapp-sec's lack of high findings is backed by explicitly verified positives (CSRF wrapper, 127.0.0.1 binding, path-traversal guards, list-args subprocess); cross-cutting's clean secrets result was methodologically strong (diffed actual .env values against the tree). The only distribution anomaly is the one above: everything that runs on a TIMER (launchd) produced zero findings because it was in nobody's scope.
- MINOR uncovered content: untracked 'Music Theory Reference/' directory and docs/reports/* weekly reports were never opened by any unit (cross-cutting pattern-grepped them for secrets only). Content-only, low risk.


## Coverage Statements

- **sc-core**: Fully read (line-by-line): scene_intelligence/sc_engagement.py (all 2496 lines) and scene_intelligence/sc_engagement_config.py (all 422 lines); both pass python3 -m py_compile.
- **sc-support**: Fully read (every line): scene_intelligence/sc_browser_likes.py, sc_build_browser_session.py, sc_extract_chrome_cookies.py, check_sc_follows.py, sc_log_manual.py, sc_unfollow_cleanup.py, sc_weekly_health.py, release_weekly_health.py.
- **ig-core**: Fully read (every line): scene_intelligence/ig_engagement.py (2332 lines), scene_intelligence/ig_engagement_config.py (449 lines), scene_intelligence/ig_live_driver.py (745 lines).
- **ig-support**: Fully read (every line): all 7 in-scope files - scene_intelligence/ig_queue_builder.py, ig_merge_session_log.py, ig_followback_checker.py, ig_audit_queue_freshness.py, ig_reconcile_followings.py, ig_follower_audit.py, ig_show_automation_follows.py.
- **safety-caps**: Fully read (every line): docs/ig-engagement-sop.md (1526 lines, in two passes), docs/sc-engagement-sop.md, docs/cowork-ig-engagement-body.md, docs/cowork-task-bodies.md, docs/ig-agent-context.md (1047 lines, two passes), docs/sc-agent-context.md, scene_intelligence/ig_engagement_config.py, scene_intelligence/sc_engagement_config.py.
- **webapp-sec**: Fully read: release_manager/webapp.py (all 3620 lines), all 16 templates in release_manager/templates/ (base, dashboard, release_detail, release_form, track_form, artwork_resizer, video_resizer, seo_copy, bios, engagement, promotion, promotion_target_row, sc_automation, stats, autopilot, palette).
- **rm-rest**: Fully read (every line): all 12 in-scope files — email_outreach.py, seo_copy_generator.py, cli.py, storage.py, models.py, contact_bridge.py, bio_manager.py, checklist.py, timeline.py, reconcile.py, display.py, paths.py.
- **si-enrich**: Fully read (every line): all 11 in-scope files — push_to_sheets.py, utils.py, enrich_soundcloud.py, enrich_spotify.py, enrich_youtube.py, enrich_urls.py, enrich_contacts.py, re_enrich_discogs.py, classify_subtypes.py, update_scores.py, scrape_label_emails.py.
- **si-discover**: Fully read all 21 in-scope files: extract_contacts.py, discover_contacts.py, discover_curators.py, extract_rekordbox.py, extract_ra.py, fetch_youtube_subs.py, curator_enrich.py, curator_check_adds.py, curator_pitch_sheet.py, curator_config.py, curator_extract_routes.py, promo_dj_shortlist.py, promo_label_shortlist.py, promo_press_shortlist.py, ig_enrich_instagram.py, ig_enrich_helper.py, ig_fetch_.
- **root-tools**: Fully read (every line): artwork_resizer.py, video_resizer.py, metadata_utils.py, image_generator.py, description_scorer.py, sc_auth_callback.py, stats/collectors.py, stats/storage.py, stats/daily_sync.py, stats/bandcamp_import.py, stats/__init__.py.
- **agents-skills**: Fully read (line by line): all 9 skills (.claude/skills/{bio,discover,enrich,ig,promo,release,release-prep,sc,sync}/SKILL.md), all 3 agents (.claude/agents/{ig-expert,sc-expert,promotion-expert}.md), docs/ig-status.md, docs/ig-session-scorecard.md.
- **cross-cutting**: FULLY DONE: (1) Secrets - grepped all 323 tracked files and all untracked non-ignored files for sk-/sk-ant/AIza/ya29/EAA/IGQ/Bearer/client_secret/api_key/password/BEGIN PRIVATE KEY patterns AND cross-checked every actual .env value (18 keys, >=12 chars) against tracked and untracked files programmatically without printing values; verified git check-ignore for .env, credentials.json, .sc_user_token.