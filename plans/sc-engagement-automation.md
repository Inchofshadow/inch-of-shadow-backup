# SoundCloud Engagement Automation — Inch of Shadow

> ⚠️ **DEPRECATED 2026-05-04.** This document predates the May 3 DataDome incident. Some claims here are no longer accurate (the OAuth user-token write path no longer works; the engine's `run_engagement` is now disabled by default). The current operational protocol is **[docs/sc-engagement-sop.md](../docs/sc-engagement-sop.md)** — read that first. This file is kept as historical context (architecture rationale, tier rules, layer model, repost economics) but should not be used as a running guide.

**Last updated:** 2026-04-25 (superseded 2026-05-04)
**Status:** Active — two scheduled tasks running, moderate mode enabled
**Goal:** Grow SC follower count so bookers see a credible profile and book gigs. Raw follower count + follow ratio are the primary signals bookers look at.

---

## Architecture Overview

Two complementary systems working in parallel:

| System | Type | Runs | Targets |
|--------|------|------|---------|
| `sc_engagement.py` | Automated | Tue / Thu / Sat ~11 AM | Scene artists from SI |
| Webapp `/engagement` | Manual | On demand | Fans of scene artists |

The hybrid model is intentional: the API handles the heavy lifting for scene artists automatically, while Chrome browser cookies allow likes/reposts that the API alone can't do (SC restricts write actions on standard API tokens). Fan follows are manual because SC doesn't expose the followers list of other users in a way that's safe to automate at scale.

---

## Scheduled Task 1 — `sc-weekly-engagement`

**Cron:** `0 11 * * 2,4,6` (Tue, Thu, Sat — display label in scheduler may show "Tuesday only" which is a UI bug, not a real bug)
**Mode:** Moderate (switched 2026-04-25 after 2+ clean weeks)
**Script:** `scene_intelligence/sc_engagement.py`

### Action Budgets

| Action | Conservative | Moderate (current) | Aggressive (boost only) |
|--------|-------------|-------------------|------------------------|
| Likes | 15 / run | 30 / run | 50 / run |
| Follows | 8 / run | 15 / run | 20 / run |
| Reposts | 2 / week | 4 / week | 6 / week |
| Weekly total (3x) | 45L / 24F | 90L / 45F | 150L / 60F |

Safe SC ceiling for an account at this stage: ~50 likes/day, ~25 follows/day. All three modes stay under that.

**When to switch modes:**
- conservative → moderate: after 2 clean weeks (done)
- moderate → aggressive: release boost window only (e.g. May 10–12 for Farewell)
- aggressive → moderate: reverts automatically after boost ends

### Three Engagement Layers

**Layer A — SI contacts (primary)**
Direct engagement with scene artists, labels, and venues in `enriched_contacts.json`. Requires `soundcloud_user_id` and match score ≥ 2.

**Layer B — 2nd-degree artists (discovery)**
Finds new artists by inspecting who SI contacts *follow*. Uses top 15 SI seeds, inspects 100 followings each, caps at 50 new candidates per run. Filtered by genre keywords (dark disco, acid, EBM, techno, electro, etc.) against artist bio/city/name. Triggered with `--discover` flag — not on by default.

### Artist Tiering (applies to both layers)

| Followers | Tier | Likes | Follow | Repost |
|-----------|------|-------|--------|--------|
| ≤ 2,000 | Peer | ✓ | ✓ | ✓ (if score ≥4, ≥500 followers) |
| 2,001 – 50,000 | Prominent | ✓ | ✗ | ✓ (if score ≥4) |
| 50,001+ | Famous | ✓ | ✗ | ✗ |

Rationale: artists with 2K+ followers almost never follow back a small account — following them bloats your Following count with zero return. Likes still give visibility via the "liked by" feed (Discorank 3x multiplier). Famous accounts get likes only for algorithmic presence.

### Like Rules
- Max 2 likes per artist per run
- Must have ≥ 3 tracks on SC (ghost/empty accounts skipped)
- Prefers tracks uploaded within last 21 days (+15 priority)
- Active uploaders within 90 days get +5 priority bonus
- Stale accounts (no upload in 90+ days) get -10 priority penalty — still eligible, just deprioritised
- Like cooldown: 30 days per artist, 60 days per track
- Checks recent tracks first (up to 3 fetched per artist)

### Follow Rules
- Peer tier only (≤ 2,000 followers)
- **Must have uploaded within last 90 days** — hard cutoff, no exceptions
- Must have ≥ 3 tracks on SC
- Not already in follow tracker
- Not in permanently_unfollowed list
- Unfollow after **7 days** if no follow-back
- Artists who follow back are **never** auto-unfollowed

### Repost Rules
- Match score ≥ 4 (strong or perfect genre fit)
- Artist has ≥ 500 SC followers (must have real reach)
- Not famous tier
- Repost cooldown: 60 days per track
- Budget: 2/week (conservative), 4/week (moderate)
- Reposts show in followers' feeds — high value, used sparingly

### Unfollow Sweep
Runs every session before likes/follows. Checks follow-back status first (fetches `/me/followers`), marks follow-backs, then unfollows anyone past 7 days with no follow-back. Artists who followed back are kept permanently.

### Tech Stack
- **Likes/Reposts:** SC API v2 via OAuth (`sc_v2_post`) — DataDome blocks the requests-based browser path (`sc_browser_likes.py` is all stubs). The OAuth path is working and confirmed on Apr 25 (11 likes, 1 repost). Fragile long-term — if SC tightens OAuth restrictions, these move to Claude-in-Chrome manual browser clicks.
- **Follow/Unfollow:** SC API v1 (`/me/followings/`) — stable, no browser needed.
- **Fan follows:** Claude-in-Chrome browser automation — screens follower profiles from peer seed pages, follows quality candidates.
- **Cookie session:** Chrome cookies extracted from Inch of Shadow's Chrome profile (`sc_extract_chrome_cookies.py`). Refreshed as needed.
- Auth: OAuth user token in `.sc_user_token.json` (mode 600). Auto-refreshes on expiry. Re-authenticate via `sc_auth_callback.py` if refresh token expires.

### Track Play Behavior — Procedural Rule (no code)
`sc_browser_likes.py` is fully stubbed (PLAYWRIGHT_AVAILABLE=False). Likes and reposts are executed by Claude-in-Chrome clicking in real Chrome, not by Python. So the play-before-like behavior lives here as a hard rule, not in code.

**When executing likes or reposts via Chrome MCP, follow this 5-step procedure for every track:**
1. Open the track URL in Chrome
2. **Mute the tab BEFORE clicking play** (always — no exceptions)
3. Click play
4. Wait 15–20 seconds
5. Then like or repost

Applies only to tracks queued for action — not general browsing. Adds human behavioral signal. SC filters automated plays so this does not affect play counts.

If Playwright is ever rebuilt in `sc_browser_likes.py` (Option B — real build, ~200 lines), this rule would move into code. Not planned currently.

### Key Files
```
scene_intelligence/sc_engagement.py          # Main engine
scene_intelligence/sc_engagement_config.py  # All tunable values
scene_intelligence/sc_follow_tracker.json   # Active follows + unfollow schedule
scene_intelligence/engagement_log.json      # Full action history (all platforms)
.sc_user_token.json                          # OAuth token (gitignored)
.sc_browser_state.json                      # Chrome cookie session (gitignored)
```

---

## Scheduled Task 2 — `sc-release-boost`

**Type:** Manual trigger only — run after uploading a new track or DJ set
**Mode:** Aggressive for 5 consecutive days from trigger date (reverts to moderate after)
**Script:** `scene_intelligence/sc_engagement.py` with aggressive mode

### When to Trigger
- Trigger **3–5 days before release date** for maximum algorithm impact
- For **Farewell** (releases May 15): trigger around **May 10–12**
- Do NOT trigger casually between releases — save the boost window for real drops

### What Changes vs Weekly Task
- Mode switches to aggressive (50 likes/run, 20 follows/run, 6 reposts/week)
- Active release context (`release_context.json`) is used to boost contacts matching the release genre (EBM, Acid for Farewell)
- Runs daily for 5 days instead of 3x/week cadence
- Reverts to moderate automatically after 5 days

---

## Scheduled Task (manual webapp) — Fan Follow

**Location:** Flask webapp `/engagement` page
**Type:** Manual — you open the page and follow fans from seed profiles

### How It Works
The sc-weekly-engagement scheduled task handles fan follows automatically via Claude-in-Chrome (no manual web app needed). On each Tue/Thu/Sat run it screens 30–40 candidate profiles from peer seed pages and follows up to 10 quality fans.

1. Screens follower profiles from 4 peer seed pages (see below)
2. Each candidate must pass quality gates before being followed
3. Logs each follow to `sc_follow_tracker.json` with 7-day unfollow timer
4. If no follow-back after 7 days, they appear in the unfollow sweep

### Peer Seed Pages (4 sources)
- Slow Motion Records followers (21K — primary pool, added 2026-04-25)
- Plus 3 other peer label/artist pages from SI (rotated)

### Fan Quality Gates
A candidate must pass ALL of these to be followed:
- Real profile photo (not default avatar)
- `last_modified` within last 2 months (active user signal)
- Likes ≥ 50 **OR** Following count ≥ 50 (engaged listener signal — either works)
- Not already following Inch of Shadow
- Not in permanently_unfollowed list

### Seed Selection Rules
- Match score ≥ 3 minimum
- Labels prioritised (+15 priority bonus) — their followers are DJs/producers, highest quality audience
- DJs +5, Venues +3
- Contacts with Instagram link +10 (IG fans tend to follow back more)
- Random jitter (0–15) added to rotate seeds
- 30-day seed history — same contact won't be picked as seed within 30 days

### Fan Follow Rules (vs Artist Follow)
| | Artist Follow (automated) | Fan Follow (manual) |
|--|--------------------------|---------------------|
| Who | SI contacts (DJs, labels) | Fans of SI seed profiles |
| Likes | ✓ (their tracks) | ✗ (they're not scene artists) |
| Follows | ✓ | ✓ |
| Reposts | ✓ (if score ≥4) | ✗ (no tracks to repost) |
| Unfollow window | 7 days | 7 days |
| Tracked in | `sc_follow_tracker.json` | `engagement_log["follows"]` |

Fans don't get likes or reposts — they're not producing scene-relevant music. The only goal is follow-back to increase raw follower count.

---

## Promotion Log Sync (added 2026-04-25)

The engine reads `promotion_log.json` on every run and bumps contacts in active campaigns to the front of the engagement queue.

**Active campaign** = has at least one target with status `not_sent` or `pre_warming`. When all targets are marked `sent`/`replied`/`rejected`/`skipped`, the campaign auto-drops.

**Current active campaign:** farewell-single (release May 15)
Active targets being pre-warmed: Cultivated Electronics, lies_records, 030303records, holywanderer

**How it works:**
- Promo contacts matched to SI by name first, then SC slug fallback
- Priority boost of +1,000 so they always sort above SI queue items
- Per-contact pre-warm cooldown: 14 days (no spam)
- On successful action: logs `sc_pre_warm` to engagement_log with campaign id + release title
- Cross-ref write-back: fills missing `soundcloud_url` and `demo_email` in SI if target has them; bumps `last_engaged` to today

**Config values:** `PROMO_TRIGGER_STATUSES`, `PROMO_REPWARM_COOLDOWN_DAYS = 14`, `PROMO_PRIORITY_BOOST = 1000`

---

## Circuit Breakers (added 2026-04-23)

The engine now has session-level safety stops. All configured in `sc_engagement_config.py`.

| Trigger | Behaviour | Config value |
|---------|-----------|-------------|
| 3 consecutive like failures | Halts likes for rest of session, follows continue | `MAX_CONSECUTIVE_LIKE_FAILURES = 3` |
| 2 consecutive follow failures | Halts follows for rest of session | `MAX_CONSECUTIVE_FOLLOW_FAILURES = 2` |
| HTTP 403 on any API call | Full session halt — account restriction signal | — |
| HTTP 429 with Retry-After > 60s | Full session halt — block signal, not standard rate limit | `RATE_LIMIT_BLOCK_THRESHOLD_SECONDS = 60` |
| Like/follow success | Resets the consecutive failure counter for that action | — |

On success, failure counters reset. Circuit breaker state is reset fresh at the start of every `run_engagement()` call — it does not persist between sessions.

Normal 429s (Retry-After ≤ 60s) still sleep and retry as before. Only abnormally long Retry-After is treated as a block.

These are grounded in SC API behaviour — 403 on `/me/followings/` or `/me/track_likes/` means the OAuth account is restricted, not a transient error. The circuit breaker logic is API-specific, not borrowed from browser automation patterns.

---

## Hard Rules (non-negotiable, all sessions)

- Never re-follow a previously unfollowed account — enforced via `permanently_unfollowed` list in `sc_follow_tracker.json`. Written on every unfollow, checked before every follow.
- Hidden contacts (from `engagement_log["hidden"]`) are skipped by the SC engine — same list the IG engine uses. Currently 21 contacts hidden.
- Never run the release boost outside the 3–5 day pre-release window.
- Moderate is now the standard mode. Use aggressive only during the release boost window (5 days max). Never run aggressive as a default.
- **Track play-before-action (browser likes/reposts only).** Before clicking like or repost on any track in Chrome (Chrome MCP / Claude-in-Chrome):
  1. Open the track URL in a Chrome tab.
  2. **Mute the tab BEFORE pressing play** — always, every track, every time. No exceptions.
  3. Click play.
  4. Wait **15–20 seconds**.
  5. Then click like / repost.

  Only applies to tracks the engine has queued for action (e.g. items from `--dump-queue`). Does NOT apply to general browsing, research, or discovery — only to tracks about to receive a like or repost. Rationale: a real play signal alongside the like reads as human behaviour to SC's anti-bot, and may register a play count for the artist (extra value for the contact we're warming).
- Auth token must verify clean before any session starts — the engine enforces this via `verify_auth()` before touching anything.
- Log all manual SC actions (follows, unfollows, likes) via `sc_log_manual.py` so cooldowns and permanently_unfollowed stay accurate.
- **Browser scope is strictly limited.** Only click what is required for the current task (like, repost, follow, play). Never click anything else on the page.
- **Never touch SC settings.** No account settings, notification settings, privacy settings — nothing. If a settings prompt appears, stop and report it.
- **Never click or agree to any notification or privacy popup.** Do not dismiss, accept, or decline. Stop immediately and notify the user — they decide.
- **DMs are off-limits entirely.** Never open the DM inbox. Never open an individual DM. Never send a DM. Never click anything that would navigate to a DM thread.
- **Never click any link.** Not from DMs, track descriptions, profile bios, comments, or anywhere else on the page. If a link needs to be opened for a task, get explicit user confirmation first and use Claude-in-Chrome navigate tool directly — never click it.

---

## Known Issues & Watch Points

| Issue | Status | Notes |
|-------|--------|-------|
| mm.discos followed despite 3,602 followers | Resolves Apr 28 | Violated 2K rule — auto-unfollows Apr 28, no action needed |
| franzscala + cultivated_electronics followed but not in tracker | Deferred | API follow may have succeeded without tracker write — no auto-unfollow scheduled |
| ninakraviz SC match wrong | Fixed 2026-04-22 | Was matching parody account (37 followers, "Famous Russian Dentist"). SC fields cleared. |
| Webapp unfollow timer was 10 days | Fixed 2026-04-22 | Changed to 7 days in `webapp.py` to match automated task |
| Hidden list not respected by SC engine | Fixed 2026-04-23 | `build_si_queue()` now filters hidden contacts. 2 immediately filtered: Synthet, acid__memories |
| No circuit breakers in engine | Fixed 2026-04-23 | Consecutive failure halts + 403/429 escalation added. See Circuit Breakers section above. |
| No never-re-follow protection | Fixed 2026-04-23 | `permanently_unfollowed` list added to tracker. Written on unfollow, checked before follow. |
| Scheduler display shows "only Tuesday" | Cosmetic | Cron `0 11 * * 2,4,6` is correct, `nextRunAt` confirms Thu/Sat runs work |
| ferawell-single + single stub campaigns | Fixed 2026-04-25 | Empty campaigns deleted from promotion_log.json |
| Promotion log sync missing | Fixed 2026-04-25 | Built in VS Code — promo contacts now bump to front of queue, sc_pre_warm logged |
| promotion_log.json typo the-deciver-single | Fixed 2026-04-25 | Corrected to the-deceiver-single |
| Mode was conservative after 2+ clean weeks | Fixed 2026-04-25 | Switched to moderate in sc_engagement_config.py |

---

## Improvement Ideas (log as they come up)

- **Track play behavior** (planned, build in VS Code) — mute tab → play track 15–20s → like/repost. Adds human browsing signal. See "Planned" section in Tech Stack above.
- Re-enrich SC follower counts periodically — stale counts cause tier mismatches (contacts enriched at 800 followers might now have 3K)
- SC playlist curator discovery — find who runs dark disco / EBM / acid playlists and add to SI for outreach
- Community outreach tracker — Reddit/Discord (r/TechnoProduction, r/EBM, r/darkwave) alongside SC growth
- AI-generated contextual comments (post-Farewell) — use ANTHROPIC_API_KEY to generate short genuine comments per track. Too complex now, good future signal layer.
