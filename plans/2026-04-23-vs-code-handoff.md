# VS Code Handoff — IG Automation Build
# Inch of Shadow — April 23, 2026

This document is the complete handoff from the Cowork strategy session to VS Code
for the technical build of the Instagram engagement automation. Read it fully before
touching any code.

The workflow is a **ping-pong** between VS Code (code, scripts, running things) and
Cowork (strategy decisions, doc updates, config reviews, reviewing outputs). Neither
session does everything. When you finish a VS Code task, results go back to Cowork
for review before the next build step starts.

---

## Project overview

Artist platform for **Inch of Shadow** (Amir Miller, Berlin). Dark disco / acid /
electro / EBM / techno. Five tools automating releases, research, promotion, and stats.
All Python, all local-first.

**Project root:** `~/Desktop/Inch of Shadow/Inchofshadowcode/`

The IG automation is Tool 3 (Promotion Engine) — specifically the engagement sub-system.
A parallel SoundCloud automation already exists and is running. The IG automation is
being built from scratch this session.

**Master strategy doc:** `plans/ig-engagement-strategy.md` — read this in full.
Everything there is current and agreed. Do not change strategy decisions without going
back to Cowork first.

---

## What was built in the Cowork session (April 23, 2026)

All of these files now exist in the project. Do not recreate or overwrite them.

### New files created

| File | Purpose | Status |
|------|---------|--------|
| `scene_intelligence/ig_engagement_config.py` | Full config — all tunable values, engagement tier table, circuit breakers, timing, file paths | Done |
| `scene_intelligence/ig_personal_network.json` | 25 personal contacts — engine never engages with these | Done |
| `scene_intelligence/ig_blocked_accounts.json` | 12 Israeli accounts + any future blocks | Done |
| `scene_intelligence/ig_follow_tracker.json` | Schema ready, empty — engine writes here | Done |
| `scene_intelligence/ig_target_list.json` | Schema ready, empty — seed with Track A targets | Done |
| `scene_intelligence/ig_enrich_instagram.py` | Enrichment script — fetches IG follower data for all SI contacts | Done — needs to be run |
| `scene_intelligence/ig_enrich_queue.json` | 268 contacts queued for enrichment | Done |
| `plans/ig-engagement-strategy.md` | Full strategy doc — fully updated | Done |
| `plans/sc-automation-session-prompt.md` | Prompt for the SC review session | Done |

### Modified files

| File | What changed |
|------|-------------|
| `scene_intelligence/enriched_contacts.json` | `alenskanner` reclassified: category=dj, score=4, genre_sub=EBM |

### Still missing (output of the enrichment pass)
| File | Created by |
|------|-----------|
| `scene_intelligence/ig_enriched_contacts.json` | `ig_enrich_instagram.py` run |

---

## Current system state — before you start

**SC automation:** Live. Two scheduled tasks running.
- `sc-weekly-engagement` — Tue/Thu/Sat ~11 AM, conservative mode
- 8 active SC follows, all from April 21, all expire (unfollow due) April 28
- `scene_intelligence/sc_follow_tracker.json` — 8 follows, 0 follow-backs so far

**IG automation:** Files built. Engine not yet written. No live sessions yet.

**SI contacts:** 972 contacts in `enriched_contacts.json`.
- 268 have IG handles (extracted into `ig_enrich_queue.json`)
- 0 currently have `ig_followers` populated — enrichment pass not run yet

**Active release context:** Farewell (EBM/Acid), releases May 15 2026.
`scene_intelligence/release_context.json` — set April 15.

**Promo campaign — farewell-single:**
56 targets. 45 sent, 3 replied, 1 played, 2 rejected, 1 bounced, 3 not sent, 1 skipped.
`scene_intelligence/promotion_log.json`

---

## The shared file map — understand before writing any code

Every file the IG engine touches is shared with other systems. Break this and you
break SC or the Release Manager.

```
enriched_contacts.json       Master contact DB. SI writes it. RM reads/writes it.
                             IG engine reads it (Track B). SC engine reads it.
                             Google Sheets syncs bi-directionally via push_to_sheets.py
                             DO NOT truncate or rewrite structure.

engagement_log.json          Shared action history. SC engine writes SC actions.
                             IG engine writes IG actions. RM reads per-contact history.
                             The "hidden" list (21 contacts) is respected by BOTH engines.
                             Structure: {log:{}, follows:{}, hidden:[], queue_instagram:[],
                             queue_soundcloud:[], discovery_seeds:[], ...}

ig_follow_tracker.json       IG-only. Engine reads/writes. Schema:
                             {_meta:{}, active_follows:[], unfollowed_history:[], stats:{}}

ig_target_list.json          Track A queue. Engine reads/writes. Schema:
                             {_meta:{}, queue:[], stats:{sources:{}}}

ig_blocked_accounts.json     Read-only for engine. Manual edits only.
                             {_meta:{}, accounts:[{username, name, location, reason, source}]}

ig_personal_network.json     Read-only for engine. Manual edits only.
                             {_meta:{}, accounts:[{username, url, keep_following, reason, note}]}

promotion_log.json           RM writes campaign data. IG engine reads for Track B priority.
                             Active campaign contacts get Tier 1 priority in Track B.

release_context.json         RM writes active release. IG engine reads for boost mode.
                             {slug, title, genre_primary, genre_secondary, set_at}

ig_engagement_config.py      Engine config. Edit this to change behaviour.
                             Never hardcode values in the engine — always read from config.
```

---

## Task 1 — Run the IG enrichment pass (VS Code)

**What:** Fetch IG follower counts, bio, post count, private status for all 268 contacts
with IG handles. Without this, Track B cannot function — the engine has no idea how
many followers anyone has and cannot apply the tier rules.

**Script:** `scene_intelligence/ig_enrich_instagram.py`

**How it works:**
- Extracts Instagram session cookies from your Chrome profile (same pattern as
  `sc_extract_chrome_cookies.py`)
- Uses Instagram's internal web API: `https://www.instagram.com/api/v1/users/web_profile_info/?username={handle}`
- Processes 268 contacts with 3.5–7s delays, 30–60s pause every 25 requests
- Saves progress after every single fetch — safe to interrupt and resume
- Patches results back into `enriched_contacts.json` automatically

**Dependencies (run once):**
```bash
pip3 install requests browser-cookie3 --break-system-packages --quiet
```

**Run from project root:**
```bash
cd ~/Desktop/"Inch of Shadow"/Inchofshadowcode

# First: dry run — prints all contacts, makes zero requests
python3 scene_intelligence/ig_enrich_instagram.py --dry-run

# Then: real run
python3 scene_intelligence/ig_enrich_instagram.py

# If interrupted: resume without re-fetching already-done contacts
python3 scene_intelligence/ig_enrich_instagram.py --resume

# Limit to first N contacts for testing
python3 scene_intelligence/ig_enrich_instagram.py --limit 10
```

**Output:**
- `scene_intelligence/ig_enriched_contacts.json` — full results per contact
- `enriched_contacts.json` — `ig_*` fields patched in-place for all successful fetches

**Data collected per contact:**
- `ig_username`, `ig_full_name`, `ig_followers`, `ig_following`, `ig_posts`
- `ig_bio`, `ig_is_private`, `ig_is_verified`, `ig_external_url`, `ig_category`
- `ig_enriched_at` (ISO timestamp)

**After it runs:** paste the summary output back to Cowork for review before moving
to Task 2. Cowork will check the distribution, flag any issues, and confirm we're
ready to build the engine.

---

## Task 2 — Build ig_engagement.py (VS Code + Cowork)

**What:** The main IG engagement engine. Does not exist yet.

**File:** `scene_intelligence/ig_engagement.py`

**Only start this after Task 1 is reviewed in Cowork.**

**What the engine does per session:**

```
1. Load config from ig_engagement_config.py
2. Load blocked accounts (ig_blocked_accounts.json)
3. Load personal network (ig_personal_network.json)
4. Load follow tracker (ig_follow_tracker.json)
5. Load engagement log (engagement_log.json)
6. Load active promo campaigns (promotion_log.json)
7. Load release context (release_context.json)

8. Run unfollow sweep first:
   - Check ig_follow_tracker.json active_follows
   - For any follow where followed_at + 7 days <= today AND followed_back = False:
     → unfollow, move to unfollowed_history, log action
   - Never unfollow if keep_following = True
   - Never unfollow if contact is in active promo campaign

9. Track B — likes (SI contacts):
   - Build queue from enriched_contacts.json filtered by tier rules
   - Priority override: contacts in active farewell-single promo campaign → Tier 1
   - For each contact in budget:
     a. Check not in blocked/personal/hidden lists
     b. Check cooldown (engagement_log.json — last like within cooldown window?)
     c. Navigate Chrome to their IG profile
     d. Scroll 4–8 seconds (human behaviour)
     e. Like most recent non-sponsored post
     f. Log to engagement_log.json with platform="instagram", action="liked"
     g. Log ig_pre_warm=True in promotion_log.json if contact is in promo campaign
     h. Wait 12–20 seconds before next action

10. Track A — follows (new peer accounts from ig_target_list.json):
    - Pull next N accounts from queue (N = phase limit from config)
    - For each:
      a. Open profile
      b. Scroll 4–8 seconds
      c. Verify still passes quality rules (public, follower count, etc.)
      d. Like most recent post → wait 15–25 seconds
      e. Follow
      f. Add to ig_follow_tracker.json active_follows with followed_at, unfollow_after
      g. Log to engagement_log.json
      h. Log discovery data to ig_paid_audience_seed.json
      i. Wait 25–45 seconds before next follow

11. Save all state files
12. Print session summary
```

**Circuit breakers — engine must stop immediately if any of these appear on screen:**
```python
STOP_SIGNALS = [
    "Action Blocked", "Try Again Later", "We've limited some features",
    "Your account has been temporarily", "Suspicious Login Attempt",
    "Verify Your Account", "Confirm Your Identity", "Enter Your Password",
    "Help Us Confirm You Own This Account", "Add Your Phone Number",
    "We Restricted Certain Activity",
]
```

**Absolute prohibitions (engine must never do these under any circumstances):**
- Enter a password
- Click any link (navigate via address bar only)
- Open any DM or inbox
- Accept any privacy change or terms update
- Interact with Settings
- Click any notification or alert button
- Engage with any post marked "Sponsored"

**Method:** Real Chrome browser via computer-use (computer-use MCP). Not Playwright,
not headless, not requests. Real Chrome with real session. Lowest detection risk.

**Session schedule (from config):**
- Days: Monday, Wednesday, Friday
- Time: 10:00–11:00 AM Berlin time
- Max duration: 20 minutes hard cap
- Never run while artist is using Instagram on mobile

**Timing between actions (from config — use randomised non-uniform distributions):**
```python
between_likes:           12–20 seconds
between_like_and_follow: 18–30 seconds
between_follows:         25–45 seconds
profile_open_to_action:  4–8 seconds (scroll first)
after_scroll:            2–4 seconds pause
distraction_pause:       30–60 seconds every 4–6 actions
like_before_follow_wait: 15–25 seconds
```

**Phase limits (from config — current phase = 1):**
```python
Phase 1 weeks 1-2:  follows=5,  unfollows=0, likes=20
Phase 1 weeks 3-6:  follows=8,  unfollows=5, likes=20
Phase 2 weeks 7-12: follows=10, unfollows=8, likes=25
Phase 3 ongoing:    follows=5,  unfollows=10, likes=20
```

**Track B tier table (from ig_engagement_config.py — do not hardcode, read from config):**

> **Updated 2026-04-24** — post-enrichment rebalance. Original spec (T1=60% / T2=20% / T3=10% / T4=10%, T2 ceiling 2000) didn't match real pool sizes after we saw the enrichment data. New values below match what the engine actually runs on. See `plans/ig-engagement-strategy.md` "Changes from v1 of this strategy" section for the full rationale.

```python
Tier 1: dj/artist, score 4-5, 200-8000 IG followers → 40% of likes budget, 25-38d cooldown
Tier 2: label,     score 4-5, 200-8000 IG followers → 35% of likes budget, 30-45d cooldown
Tier 3: dj/artist, score 3,   200-8000 IG followers → 15% of likes budget, 40-52d cooldown
Tier 4: label,     score 3,   200-8000 IG followers → 10% of likes budget, 50-65d cooldown

Additive: Prominent tier — dj/artist, score 3+, 8000-15000 followers → 1/session, 60d cooldown

Always skip: venues, media, festivals, platforms, distributors, score 1
              labels > 5,000 IG followers (buried)
              SI contacts with ig_blocked: true
Hard ceiling: 15,000 IG followers — never engage above this
```

**Always skip these contacts regardless of tier:**
- Any username in `ig_blocked_accounts.json`
- Any username in `ig_personal_network.json`
- Any contact in `engagement_log.json["hidden"]`
- Israeli accounts (location or Hebrew text in bio)
- Private accounts
- Score 1 contacts

**After each session: write a one-line session summary to engagement_log.json.**

---

## Task 3 — Seed ig_target_list.json (VS Code or manual)

**What:** Populate the Track A queue with 20–50 real peer accounts before the first
live session. The engine pulls from this queue — if it's empty, Track A does nothing.

**Sources (in priority order):**
1. Hashtag search: `#darkdisco`, `#ebm`, `#acidtechno`, `#berlinunderground`, `#coldwave`
2. Follower lists of: @mannequinrecords, @darkentriesrecords, @berghain_panoramabar,
   @clone.nl, @lies_records
3. Event follower lists: @cosmic.delay, @in.between.berlin (not @collective.dada — too
   personal, social distance filter applies)
4. RA event RSVPs for Berlin EBM/dark disco events

**Quality filter — every account must pass ALL:**
- Public account
- Profile photo present
- Bio text present (min 5 chars)
- Min 12 posts
- Min 200 followers
- Max 2,500 followers
- Max 8:1 following/followers ratio
- Posted within 21 days
- Engagement rate ≥ 0.5% (likes ÷ followers on recent posts)
- Not in blocked, personal, or engagement log hidden lists
- Not in enriched_contacts.json (SI contacts go to Track B)
- Not already followed by @inch_of_shadow
- Not previously unfollowed (check ig_follow_tracker.json unfollowed_history)
- Genre-relevant bio or posts (for hashtag-discovered accounts)
- No Hebrew text, no Israeli location

**Entry format for ig_target_list.json queue:**
```json
{
  "username": "handle",
  "url": "https://www.instagram.com/handle/",
  "ig_followers": 840,
  "ig_following": 1200,
  "ig_posts": 45,
  "ig_is_private": false,
  "ig_bio": "dark disco berlin",
  "discovery_source": "hashtag_darkdisco",
  "discovered_at": "2026-04-23",
  "genre_signals": ["dark disco", "berlin"],
  "follow_back_score": "high"
}
```

**Paid marketing seed note:** Every account added here also gets written to
`scene_intelligence/ig_paid_audience_seed.json` when followed. This is your future
paid campaign audience seed — track it from day one.

---

## Task 4 — Score 1 contact review (VS Code output → Cowork decision)

**What:** 59 contacts in SI have match_score=1 (very weak genre match). Some are
wrongly scored, some are Israeli, some should be deleted. The IG engine skips all
score 1 contacts by default, but they clutter the database.

**Run this to get the list:**
```bash
python3 -c "
import json
with open('scene_intelligence/enriched_contacts.json') as f:
    contacts = json.load(f)
score1 = [c for c in contacts if str(c.get('match_score','')) == '1']
print(f'Score 1 contacts: {len(score1)}')
for c in sorted(score1, key=lambda x: x.get('category','')):
    print(f'  {c[\"category\"]:<12} {c[\"name\"]:<30} loc:{c.get(\"location\",\"\")}')
"
```

**Paste the output to Cowork** — decisions on what to do with each one are made there,
not in VS Code.

---

## Task 5 — Review 53 dropped contacts (VS Code output → Cowork decision)

**What:** 619 IG handles exist in `raw_contacts.json` that never made it into
`enriched_contacts.json`. Most are "other" category (fans, personal contacts). But
53 are DJs (26), venues (15), labels (12), and media (6) that got dropped during
the dedup/classify pipeline. Some of these are real scene contacts.

**Run this to get the list:**
```bash
python3 -c "
import json, re

with open('scene_intelligence/raw_contacts.json') as f:
    raw = json.load(f)
with open('scene_intelligence/enriched_contacts.json') as f:
    enriched = json.load(f)

enriched_ig = set()
for c in enriched:
    for field in ['url','instagram_url','instagram','discogs_instagram']:
        v = str(c.get(field,'') or '')
        if 'instagram.com' in v:
            h = re.sub(r'https?://(?:www\.)?instagram\.com(?:/_u)?/', '', v).strip('/').lower()
            if h: enriched_ig.add(h.split('?')[0])

ig_raw = raw.get('instagram', [])
dropped = []
for c in ig_raw:
    url = str(c.get('url',''))
    if 'instagram.com' in url:
        h = re.sub(r'https?://(?:www\.)?instagram\.com(?:/_u)?/', '', url).strip('/').lower()
        h = h.split('?')[0]
        cat = c.get('category','')
        if h and h not in enriched_ig and cat in ['dj','label','venue','media','promoter']:
            dropped.append((cat, h, c.get('name','')))

for cat, handle, name in sorted(dropped):
    print(f'{cat:<12} @{handle:<30} {name}')
print(f'Total: {len(dropped)}')
"
```

**Paste the output to Cowork** — decisions made there.

---

## Key rules — never violate these in any code you write

### Security
- ALL API keys in `.env` only — never hardcoded, never committed
- `.env` always in `.gitignore`
- No command injection, no XSS, no OWASP top 10
- Sanitize all user input at system boundaries
- Never expose API keys or internal paths to client

### Privacy
- No data sent to third-party services without explicit approval
- Prefer local/self-controlled solutions
- No tracking, no analytics on web UI

### IG engine hard rules (non-negotiable, build into code as hard checks)
- Never enter a password
- Never accept privacy changes or terms updates
- Never open any DM or inbox
- Never click any link — navigate by typing address only
- Never interact with Settings screen
- Never engage with sponsored or promoted content
- Never engage with Israeli accounts (location or Hebrew text detection)
- Never engage with accounts in ig_blocked_accounts.json
- Never engage with accounts in ig_personal_network.json
- Never engage with accounts in engagement_log.json["hidden"]
- Stop immediately on any circuit breaker signal
- After soft block: 48h pause. After hard block/CAPTCHA: 72h pause.

### Coding conventions
- Python 3.9+ (system Python on macOS)
- No emojis in code or output
- All tunable values in `ig_engagement_config.py` — never hardcode in engine
- Output folders auto-created if missing
- Every file write is atomic (write to temp, rename) to prevent corruption

---

## Ping-pong workflow — what goes where

**VS Code handles:**
- Running scripts (enrichment, engine, utilities)
- Writing Python code (engine, enrichment, utilities)
- Debugging errors and edge cases
- Running the output-generating scripts (score 1 list, dropped contacts list)
- Anything that needs a real terminal or real Chrome cookies

**Cowork handles:**
- All strategy decisions — if something isn't in the strategy doc, it goes to Cowork
- Reviewing script outputs before acting on them
- Updating the strategy doc with new decisions
- Config value approvals (changing phase, adjusting tier weights)
- Reviewing the enrichment results before building the engine
- Personal network / blocked accounts decisions
- Any new rule or exception that affects the engine behaviour

**How the ping-pong works:**
1. VS Code runs a task and produces output
2. Output (file contents, script results, error messages) goes to Cowork
3. Cowork reviews, makes decisions, updates docs/config if needed
4. VS Code gets new instructions and runs the next task

**Never make a strategy decision in VS Code.** If the engine behaviour needs to change,
flag it to Cowork first. If a contact needs to be blocked or reclassified, flag it to
Cowork. Build the code exactly as specced here, and flag anything unclear.

---

## What to do first — in order

1. Read `plans/ig-engagement-strategy.md` in full (it's the source of truth)
2. Run `ig_enrich_instagram.py --dry-run` — verify the 268 contacts look right
3. Run `ig_enrich_instagram.py` — do the full enrichment pass
4. Paste the summary output to Cowork for review
5. Wait for Cowork to confirm before building the engine

---

## All file paths

```
~/Desktop/Inch of Shadow/Inchofshadowcode/
│
├── scene_intelligence/
│   ├── ig_engagement.py           # TO BUILD — main engine
│   ├── ig_engagement_config.py    # DONE — all tunable values + tier table
│   ├── ig_enrich_instagram.py     # DONE — enrichment script, needs to run
│   ├── ig_enriched_contacts.json  # MISSING — output of enrichment pass
│   ├── ig_enrich_queue.json       # DONE — 268 contacts queued
│   ├── ig_follow_tracker.json     # DONE — empty schema, engine writes here
│   ├── ig_target_list.json        # DONE — empty schema, needs seeding
│   ├── ig_blocked_accounts.json   # DONE — 12 Israeli accounts
│   ├── ig_personal_network.json   # DONE — 25 personal contacts
│   ├── ig_paid_audience_seed.json # TO CREATE — marketing seed (engine writes)
│   ├── ig_performance_log.json    # TO CREATE — manual monthly stats input
│   ├── engagement_log.json        # SHARED — IG + SC action history
│   ├── enriched_contacts.json     # MASTER — 972 SI contacts
│   ├── promotion_log.json         # SHARED — promo campaign data
│   ├── release_context.json       # SHARED — active release (Farewell, EBM/Acid)
│   ├── sc_engagement.py           # SC engine — do not modify
│   ├── sc_engagement_config.py    # SC config — do not modify
│   └── sc_follow_tracker.json     # SC follows — 8 active, all due April 28
│
├── plans/
│   ├── ig-engagement-strategy.md       # MASTER STRATEGY — read this first
│   ├── sc-engagement-automation.md     # SC strategy — separate session
│   ├── sc-automation-session-prompt.md # SC session prompt — separate session
│   ├── master-plan.md                  # Full project vision
│   └── 2026-04-23-vs-code-handoff.md   # This file (renamed 2026-04-24)
│
├── data_intelligence/             # TO CREATE — SEO/competitive intel dir
│   ├── competitive_intel.json     # TO CREATE — reference artist patterns
│   └── seo_versions.json          # TO CREATE — your copy versions + performance
│
├── release_manager/               # EXISTING — do not touch
├── releases/                      # EXISTING — release JSON files
└── .env                           # API keys — never commit
```

---

## Upcoming deadlines to be aware of

- **April 28, 2026** — SC: 8 active follows expire. Unfollow sweep will run automatically.
  Check sc_follow_tracker.json that day.

- **May 1, 2026** — Farewell single: Bandcamp Friday / pre-save links due.
  Check farewell-single checklist in Release Manager.

- **May 10–12, 2026** — Trigger `sc-release-boost` task (moderate mode, 5 days).
  Run this before Farewell drops May 15.

- **May 15, 2026** — Farewell single release day.

- **July 23, 2026** — Quarterly IG export reminder fires (scheduled task active).
  Export, parse, review following cleanup.
```
