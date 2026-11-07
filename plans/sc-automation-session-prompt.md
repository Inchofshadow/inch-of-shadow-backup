# SoundCloud Automation — Deep Review and Improvement Session

> **DEPRECATED 2026-06-12. Do not use as a session prompt.** All file paths below reference the old `/Users/amir/Documents/Claude/Inchofshadowcode/` location (now `/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode/`), and entry counts / Nina references are stale (Nina Protocol shut down July 2026). Kept for historical reference only.

You are continuing work on the SoundCloud engagement automation for Inch of Shadow
(@inch_of_shadow / soundcloud.com/inch-of-shadow), a Berlin-based dark disco / acid /
electro / EBM / techno artist.

---

## CRITICAL: Read these files before doing anything

Read them in this order, fully. Do not skip any.

1. `/Users/amir/Documents/Claude/Inchofshadowcode/plans/master-plan.md`
   — the full project vision (5 tools, 7 career goals). SC automation sits inside
   Goal 0 (grow audience and revenue). Read to understand the bigger picture.

2. `/Users/amir/Documents/Claude/Inchofshadowcode/plans/sc-engagement-automation.md`
   — the full SC strategy doc (architecture, rules, known issues, improvement ideas)

3. `/Users/amir/Documents/Claude/Inchofshadowcode/scene_intelligence/sc_engagement_config.py`
   — all current tunable values (modes, limits, tiering, timing, genre keywords)

4. `/Users/amir/Documents/Claude/Inchofshadowcode/scene_intelligence/sc_engagement.py`
   — the main engine (1,738 lines — skim the structure, read key functions carefully,
   especially: build_si_queue, build_full_queue, run_engagement, run_unfollow_sweep,
   discover_related_artists, like_tracks_for_artist, follow_artist)

5. `/Users/amir/Documents/Claude/Inchofshadowcode/scene_intelligence/sc_browser_likes.py`
   — 270 lines. This is the primary mechanism for likes and reposts (requests-based
   Chrome cookies). Read carefully. The key risk: cookie staleness. If `.sc_browser_state.json`
   is stale, likes fail silently without raising an exception. Understand how freshness
   is checked (or not checked).

6. `/Users/amir/Documents/Claude/Inchofshadowcode/scene_intelligence/sc_follow_tracker.json`
   — live follow state (8 active follows, all from April 21, all due April 28)

7. `/Users/amir/Documents/Claude/Inchofshadowcode/scene_intelligence/engagement_log.json`
   — shared action log for IG + SC (60 SC actions, 70 IG actions, 21 hidden contacts,
   5 contacts in SC queue). Check: is the hidden list being respected by the SC engine?

8. `/Users/amir/Documents/Claude/Inchofshadowcode/scene_intelligence/promotion_log.json`
   — active campaign data. Read the farewell-single campaign (56 targets, 45 sent,
   3 replied, 1 played). The SC engine is not currently reading this file at all.

9. `/Users/amir/Documents/Claude/Inchofshadowcode/scene_intelligence/release_context.json`
   — active release context (Farewell, EBM/Acid, set April 15). The SC engine should
   be reading this. Check if it is.

10. `/Users/amir/Documents/Claude/Inchofshadowcode/scene_intelligence/ig_blocked_accounts.json`
    — NEW file from the IG session. 12 Israeli accounts pre-populated. SC engine must
    read and respect this list.

11. `/Users/amir/Documents/Claude/Inchofshadowcode/scene_intelligence/ig_personal_network.json`
    — NEW file from the IG session. 25 personal contacts. SC engine must never engage
    with these accounts.

12. `/Users/amir/Documents/Claude/Inchofshadowcode/plans/ig-engagement-strategy.md`
    — the IG strategy doc. Read ALL parts. Most decisions made there have SC equivalents.
    Pay special attention to: Part 3 (bot detection and timing), Part 4 (engagement tiers
    and the tier table architecture), Part 5 (session rules and circuit breakers),
    Part 8 (data collection for paid campaigns and the 7-step intelligence vision).

**Also be aware of (do not need to read in full, just know they exist):**
- `scene_intelligence/nina_follow_log.json` — tracks follows on Nina Protocol (a web3
  music platform), NOT SoundCloud. 23 entries, all status unknown. This is a separate
  platform entirely. Do not confuse it with SC follows. The IG and SC sessions do not
  touch Nina Protocol.
- `release_manager/templates/sc_automation.html` — the webapp template for the fan
  follow `/engagement` page. Only read if you need to modify the webapp quality filters.
- `plans/soundcloud-seo-audit.txt` — a previous SEO audit of the SC profile. Useful
  context if working on the intelligence / competitive intel system.

---

## Current status — what's already built and running

The SC automation is NOT starting from scratch. It is live:

**Two scheduled tasks running:**
- `sc-weekly-engagement` — Tue / Thu / Sat ~11 AM, conservative mode
  (15 likes/day, 8 follows/day, 2 reposts/week)
- `sc-release-boost` — manual trigger only, runs around release date in moderate mode

**What the engine does:**
- Pulls SI contacts from `enriched_contacts.json` (972 contacts, 537 with SC data)
- Builds an engagement queue by tier (peer ≤2K followers, prominent 2K–50K, famous 50K+)
- Likes recent tracks (≤21 days old preferred, max 2 likes per artist, 30-day cooldown)
- Follows peer-tier artists (≤2K followers), unfollows after 7 days if no follow-back
- Reposts (score ≥4 contacts, ≥500 SC followers, 60-day cooldown, 2/week budget)
- Discovers 2nd-degree artists via SI contacts' following lists (--discover flag)
- Fan follow queue via webapp `/engagement` page (manual: you browse, webapp logs)

**Tech stack:**
- Primary: requests-based using Chrome cookies (`sc_extract_chrome_cookies.py`) — no browser launch
- Fallback: Playwright headless Chromium (`sc_build_browser_session.py`)
- Last resort: SC API v2 direct
- Follow/Unfollow: SC API v1 (`/me/followings/`) — stable
- Auth: OAuth user token in `.sc_user_token.json`. Refresh token auto-renews.
  Re-authenticate via `sc_auth_callback.py` if refresh token expires.

---

## Known issues — fix these

From the strategy doc and live data:

1. **mm.discos was followed despite having 3,602 followers** — violates the 2K follow rule.
   Auto-unfollows April 28. But the bug that allowed it needs to be found and fixed.

2. **franzscala + cultivated_electronics were followed but are NOT in the follow tracker.**
   The API follow may have succeeded without a tracker write. These accounts have no
   auto-unfollow scheduled. Need to investigate: did the follow actually happen? If yes,
   manually add them to the tracker or unfollow them.

3. **ninakraviz matched a parody SC account** (37 followers, "Famous Russian Dentist").
   Fixed April 22 — SC fields cleared. But this reveals a confidence threshold issue:
   the enrichment matched at some confidence level that was too low. Review the matching
   logic in `enrich_soundcloud.py` to make sure this can't happen again.

4. **No Israeli account blocking** — the SC engine has no equivalent of the IG blocked
   countries rule. Israeli accounts found in SI should be skipped for follows. Check
   the SI data: Acidalia (followed April 21) has location "milan" but the name pattern
   should be reviewed. The full Israeli account list from the IG session is in
   `ig_blocked_accounts.json`. Add the same logic to SC.

5. **No personal network / blocked accounts concept** — the SC engine will engage with
   anyone in SI who passes tier rules. It has no equivalent of `ig_personal_network.json`
   or `ig_blocked_accounts.json`. Add both. The same files used by the IG engine should
   be respected here: if someone is in the personal network or blocked list, SC skips them.

6. **No promotion log sync** — the SC engine does not read `promotion_log.json` to prioritise
   contacts in active promo campaigns. If Mannequin Records is being pitched for Farewell,
   the SC engine should prioritise liking their recent tracks right now. This bridge
   exists in the IG strategy but not in SC. Build it.

7. **The fan follow webapp is entirely manual and has no quality filters** — the webapp
   picks seed profiles and you browse their followers manually. There is no genre check,
   no minimum follower count, no recency filter, nothing. This means you could accidentally
   follow totally irrelevant accounts with no mechanism to catch it.

8. **Repost quality bar may be too loose** — the current rule is score ≥4, ≥500 SC followers.
   A repost is the highest-value action SC offers (shows in all your followers' feeds).
   Review whether this bar should be higher. What does a repost actually do for your
   algorithm? What's the risk if you repost something that doesn't fit your sound?

9. **No data collection for paid marketing** — the IG session built a full paid audience
   seed architecture. SC needs the same: every follow, follow-back, and repost interaction
   should be tracked with enough metadata to build an audience seed file later.

10. **Comment strategy not addressed** — unlike IG, comments on SC are genuinely common
    and don't look robotic if done well. The strategy doc mentions community outreach but
    there is no comment system. What would a SC comment strategy look like? Is it worth
    automating any part of it, or should it be manual like the IG comment queue?

---

## Things from the IG strategy that directly apply to SC — review each

The IG strategy session produced a set of decisions that have SC equivalents. Go through
each of these and confirm whether the SC engine already handles it, needs updating, or
needs a new feature:

**Security and detection:**
- Timing rules — SC config has `ACTION_DELAY_MIN: 4, ACTION_DELAY_MAX: 12` seconds.
  The IG session determined that non-uniform weighted distributions (peaking around
  15-18 seconds) with occasional longer pauses (30-60s every 4-6 actions) are necessary
  for human-like behaviour. Are SC's current timing values appropriate for the API-based
  approach? Or too fast?

- Circuit breakers — IG has an exhaustive list of hard stops. SC has... what exactly?
  Read the engine and find out. Add any missing ones. For SC specifically: 429 rate limit
  responses, 401/403 auth failures, any "account restricted" API responses, OAuth token
  expiry mid-session.

- The SC engine uses Chrome cookies for likes/reposts. How fresh are those cookies?
  When was `.sc_browser_state.json` last updated? Is there a staleness check?

**Targeting and quality:**
- The IG session set strict Layer 4 quality rules: minimum 12 posts, minimum 200
  followers, max 8:1 following/followers ratio, bio required, profile photo required,
  post recency 21 days. What are the equivalent rules for SC? SC doesn't have "posts"
  but has tracks. Review what the minimum track count, minimum follower count, and
  maximum following/followers ratio should be for SC targets.

- The IG session confirmed that follows should never be attempted on accounts that show
  bot signals (random usernames, zero engagement, all-repost content). Does the SC
  engine have equivalent checks?

- Follow-back likelihood scoring — the IG session identified a "sweet spot" for
  high follow-back probability: accounts that follow significantly more than follow
  them. Does the SC engine prioritise these? Should it?

**Blocked accounts and personal network:**
- `ig_blocked_accounts.json` — SC engine should read and respect this
- `ig_personal_network.json` — SC engine should read and respect this
- Israeli accounts — same block rule applies to SC

**Engagement cooldown:**
- SC has 30-day like cooldown per artist, 60-day per track. Are these the right values?
  The IG session confirmed 30 days with 25-38 day jitter is correct. Jitter should be
  added to SC cooldowns too.

**Engagement tier table:**
- The IG session built a live-editable tier table in `ig_engagement_config.py` with
  configurable `budget_pct` values per tier, cooldown ranges (not exact values), and
  per-category skip rules. SC currently has a flat three-tier system (peer / prominent /
  famous) with no budget allocation or live control. Build the same tier table architecture
  for SC. Adapt it for SC-specific categories: DJs, labels, venues, media, promoters.
  The table should be editable live without touching engine code — same philosophy as IG.

**Like-before-follow sequence:**
- The IG session established that every follow must be preceded by a like (like a post,
  wait 15-25 seconds, then follow). On SC, does the engine currently like a track before
  following an artist? Or does it run likes and follows as separate independent queues?
  If separate, should they be linked? Assess and decide.

**Data and intelligence:**
- Every SC action should contribute to the paid marketing seed data.
  Track: discovery source, follower count at interaction time, genre signals, follow-back result.
  Output file: `scene_intelligence/sc_paid_audience_seed.json`

- SC is actually richer than IG for competitive intelligence because more content is public:
  - Track descriptions (longer and more detailed than IG captions)
  - Explicit genre tags per track (not hashtags — actual SC tag fields)
  - Play counts (real performance data — no IG equivalent)
  - Repost chains (traceable influence network — who reposts whom)
  - Comment text on tracks (verbatim fan language — raw copy material)
  These feed into `data_intelligence/competitive_intel.json` (the same file IG writes to).
  Design how the SC engine contributes to this file during its runs.

- The full 7-step intelligence vision from the IG session applies here too:
  Step 1: Collect copy/tag/description data from 20-30 reference SC artists.
  Step 2: Every profile visited logs bio, tags, engagement rate.
  Step 3: Monthly manual performance input from SC stats.
  Step 4: Copy generator reads SC data alongside IG data.
  Step 5: SC follow-back dataset feeds paid campaign custom audiences.
  Step 6: Paid campaign results feed back into SC targeting rules.
  Step 7: SC + IG data together = full proprietary scene intelligence asset.
  Plan how each step is implemented on SC specifically.

---

## Questions to answer before changing anything

Before making any changes to the engine, answer these honestly:

1. What is the current follow-back rate from the 8 active SC follows?
   All were followed April 21, all expire April 28. Check now — have any followed back?

2. The conservative mode runs 8 follows/day × 3 sessions/week. That is 24 follows/week.
   At the SC follower tier (≤2K), what follow-back rate are we realistically expecting?
   Is 24/week fast enough for meaningful growth? What does the SC algorithm actually
   reward — raw follower count, or engagement rate?

3. SC runs Tue/Thu/Sat. IG runs Mon/Wed/Fri. This was intentional. Confirm there is no
   conflict in the shared `engagement_log.json` when both engines write on different days.
   Is there a race condition risk if both somehow run on the same day?

4. The release boost task runs in moderate mode for 5 days around a release.
   Farewell drops May 15. When exactly should this be triggered? The strategy says
   3-5 days before — so around May 10-12. Confirm and pre-plan this.

5. The webapp fan follow feature — how many fan follows have been done? Are they logged
   anywhere? Is the 7-day unfollow timer firing correctly for webapp-logged follows?

---

## Specific things to build or improve this session

After reading everything and answering the questions above, work through these in priority
order. Confirm with the user before touching the engine code.

**Priority 1 — Fixes (bugs, safety gaps):**
- Add Israeli account blocking to SC engine (read from `ig_blocked_accounts.json`)
- Add personal network / blocked accounts check (read from `ig_personal_network.json`)
- Fix the mm.discos bug — find why the follower check passed for a 3,602-follower account
- Investigate franzscala + cultivated_electronics tracker gap
- Add jitter to all cooldown windows (currently exact values, not ranges)

**Priority 2 — Promotion log sync:**
- SC engine reads `promotion_log.json` and `release_context.json`
- Contacts in active campaigns get priority in the like queue
- Log `sc_pre_warm: true` in the promotion log when SC engages with a promo contact

**Priority 3 — Data collection:**
- Add paid marketing seed tracking to every SC follow and follow-back
- Store: discovery source, follower count at time, genre signals, follow-back result
- Output file: `scene_intelligence/sc_paid_audience_seed.json`

**Priority 4 — Config improvements:**
- Review and confirm all timing values (are they human-like enough for SC?)
- Add follow-back likelihood scoring to the queue builder (prioritise high-ratio accounts)
- Add minimum track count as a quality filter for follow targets
- Add genre keyword check for fan follow targets in the webapp

**Priority 5 — Comment strategy (SC-specific opportunity):**
- SC comments are fundamentally different from IG. On SC, genuine comments on tracks
  are extremely common and valued by artists. A comment like "love the acid line on this"
  or "the atmosphere on this one is exactly my sound" is completely normal SC behaviour —
  not robotic, not spammy. This is a significantly bigger opportunity than IG.
- Design a SC comment queue system:
  - Engine flags tracks worth a genuine comment (criteria: score ≥4, track uploaded
    within 14 days, artist in active promo campaign or Tier 1)
  - Flags are appended to `scene_intelligence/sc_comment_queue.json` with: artist name,
    track URL, track title, track tags, reason flagged, date added
  - You review the queue, listen to the track if you want, write a genuine comment,
    post it manually, mark it done
  - Engine logs the comment action in `engagement_log.json`
- Question to answer: should any part of the comment itself ever be automated (e.g.,
  engine drafts a suggested comment based on track tags)? Or always fully manual?
  Give an honest recommendation with pros and cons.

**Priority 6 — Phase system:**
- SC currently has conservative vs moderate modes but no phase system.
  Should SC have a Phase 1 / Phase 2 / Phase 3 structure like IG?
  SC is more mature (already running), so the phasing might be different.
  Review and propose the right structure.

---

## Key file paths

```
/Users/amir/Documents/Claude/Inchofshadowcode/
  scene_intelligence/
    sc_engagement.py              # Main engine (1,738 lines) — MUST READ
    sc_engagement_config.py       # All tunable values — MUST READ
    sc_browser_likes.py           # Chrome cookie likes/reposts (270 lines) — MUST READ
    sc_follow_tracker.json        # Live follows (8 active, all due April 28) — MUST READ
    engagement_log.json           # Shared log (SC + IG, 91 contacts) — MUST READ
    promotion_log.json            # Campaign data (farewell-single: 56 targets) — MUST READ
    release_context.json          # Active release: Farewell, EBM/Acid — MUST READ
    ig_blocked_accounts.json      # 12 Israeli accounts (NEW) — engine must read this
    ig_personal_network.json      # 25 personal contacts (NEW) — engine must read this
    enriched_contacts.json        # Master contact database (972 contacts)
    nina_follow_log.json          # Nina Protocol follows (NOT SC — separate platform, ignore)
    sc_build_browser_session.py   # Playwright browser session builder (fallback)
    sc_extract_chrome_cookies.py  # Chrome cookie extractor
  plans/
    master-plan.md                # Full project vision — MUST READ
    sc-engagement-automation.md   # SC strategy doc — MUST READ
    ig-engagement-strategy.md     # IG strategy — MUST READ (Parts 3, 4, 5, 8)
    soundcloud-seo-audit.txt      # Previous SC SEO audit — useful context
  data_intelligence/              # New directory (may not exist yet — create if needed)
    competitive_intel.json        # Scene-level copy/tag/posting intelligence
    seo_versions.json             # Your own approved copy versions + performance
  .sc_user_token.json             # OAuth token (gitignored)
  .sc_browser_state.json          # Chrome cookie session (gitignored) — check staleness
  sc_auth_callback.py             # Re-authentication script
```

---

## Rules that carry over from IG — non-negotiable

These were confirmed in the IG session and apply to SC without modification:

- Never enter a password in any browser under any circumstances
- Never accept privacy changes, terms updates, or settings notifications
- Never open any DM or inbox
- Never click any link in the browser
- Never interact with any Settings screen
- Never engage with sponsored or promoted content
- Israeli accounts: blocked on all platforms, no exceptions
- Personal network contacts: never engage, no exceptions
- circuit breakers: stop immediately on any unexpected auth challenge, account restriction,
  rate limit that looks like a block (not a standard 429 retry), or any screen that is
  not the expected normal flow

---

## Style note

Be direct and honest. If something in the current SC engine is wrong, mediocre, or risky
— say so. The goal is a robust, long-running automation that doesn't get the account
flagged and actually grows the right audience. Quality over speed.
