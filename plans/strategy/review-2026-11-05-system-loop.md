# Strategy review: system, costs, schedules and the one loop (2026-11-05)

READ-ONLY audit. Nothing was changed. Builds on `review-2026-11-05-facts.md` sections 8-11,
`review-2026-11-05-proposals.md` (P1-P3) and `drafts/README.md`; those are not repeated, only
referenced. Per-module inventory lives in `review-2026-11-05-code-map.md`.
"est." = estimate. "inferred" = read from indirect evidence, not checked live.

---

## 1. Cost and API map

| # | Service (key name in `.env`) | Who calls it, how often | Real use, last 30 days | Waste found | Saving (est.) |
|---|---|---|---|---|---|
| 1 | **HikerAPI** (`HIKERAPI_KEY`), $0.001/request, cap 300/day | `ig_dispatcher.py` 09:30 daily: freshness audit (logged as 200 calls/run while pool < 30) or contact re-enrich (40); `stats/collectors.py` balance read 08:45; ad-hoc DJ-07 runs (147 calls on 11-03); Gap Radar uses the leftover | Balance **0 from 10-27 to 11-01** (6 days, 6 identical "notify-amir" lines, `docs/reports/dispatch-log.md`). Topped up to $84.00 (snapshot 11-02); $83.42 on 11-05 = **579 requests in 3 days, about $0.19/day, about $5.8/month** (est.) | (a) The ledger only stores `est_calls`; `actual_calls` is empty on all 57 runs (`scene_intelligence/ig_daily_ledger.json`). (b) The low-balance message says "$5 ≈ 4 months" (`ig_dispatcher.py:389`); real burn makes $5 last about 26 days, so the warning came only at zero. | Money is small. The saving is **no more dry weeks**: a stats-side warning when balance < $10 (about 50 days ahead). Dispatcher text fix = ticket for the IG chat (engagement code, hands off). |
| 2 | **Claude API credit** (`ANTHROPIC_API_KEY`), $200/month, expires monthly, Release Manager cap `LIMIT_USD = 150` (`release_manager/claude_api.py:24`) | RM writers (bios, SEO copy, reviews, imagine), Gap Radar (`gap_radar/crowding.py`), weekly stats | Oct: **$0.49**, 11 calls. Nov 1-5: **$36.14**, 68 calls, of which `gap_radar_crowding` **$32.68 / 51 calls** (90%). Last crowding call: 200,113 input tokens, 8 web searches, $1.00 (`stats_snapshots/claude_spend.json`) | (a) Crowding runs at `effort="high"`, `max_uses: 8` searches, up to 4 resumes per gap (`crowding.py:24,25,115`). (b) The Gero key uses the same credit (memory `claude-api-credit`) but is **not in this ledger**, so the $150 cap and the Gap Radar "IoS reserve" cannot see it. (c) The first grant (10-20) expires 11-14: about $160 of it will expire unused (est.) | Crowding: 4 searches + medium effort + a cached verdict per gap name: **about -50% per profile ($8 -> $3-4, est.)**. One ledger line for Gero spend. Unused credit is lost value, not money: put scheduled text jobs (weekly summary, digest wording) on it before the monthly reset. |
| 3 | **OpenAI** (`OPENAI_API_KEY`): images + second-opinion text | `release_manager/imagine.py` (logged), `image_generator.py`, `artwork/edits/half-the-night-build/raw_render.py` (**not logged**), `openai_api.py` | Text Oct $0.04. Imagine log: 23 renders, $0.49 (Sep-Oct), **0 of 23 have a decision recorded**. `raw_render.py`: **82 renders 11-03 to 11-05 with no cost record** (`generated_images/pinocchio-single/`); est. $1-4 | No cap at all on OpenAI; raw renders invisible to any ledger; decisions not written back, so "which prompts work" cannot be learned | Log raw renders into the imagine ledger + a monthly cap (e.g. $15). Saving is control, not dollars (est. < $5/month today). |
| 4 | **SoundCloud API** (`SOUNDCLOUD_CLIENT_ID/SECRET`, `SC_BROWSER_TOKEN`), 100 reads/hour | `sc_weekly_health.py` 3x daily (06:30, 07:30, 08:30), each until the hourly budget; stats sync 08:45 (`/me`, `/me/tracks`, `/me/followers?limit=200`); Fri `sc_release_stats.py` (2 calls) | About 290 reads/day (est. 3 x ~95 + 3). Supply: the last 14 candidate files hold **1,557 candidates; 318 were followed** (sessions follow 20/day, `sc_follow_tracker.json`). Since the 3-run schedule (10-27): 99-183 candidates/day for 20 follows | (a) About 80% of crawled candidates are not followed on their day (carry-over to later days not verified). (b) The 08:45 stats call sits in the same hour as the 08:30 refresh, which runs the budget to "nearly used". (c) `follower_countries`/`follower_cities` are written daily and **read by nothing** (only `stats/collectors.py:267-296`) | Engagement-side, Amir's call (3 runs decided 10-25): 2 runs instead of 3 = **-95 reads/day and -7 scheduled chats/week** (est.). Drop the geography sample or make it monthly: -1 read/day. Move stats sync to 09:45 (outside the refresh hour). |
| 5 | **Spotify Web API** (`SPOTIFY_CLIENT_ID/SECRET`), free | Stats sync 08:45 daily: artist, top-tracks, albums, then one call per album | `followers` and `popularity` are **null on all 36 snapshots 10-01 to 11-05**, `top_tracks` empty (dev-mode app). Real numbers come from the Monday S4A Chrome read | Daily calls return only the catalogue list, which changes on release day only | Weekly (Monday) or on release; drop the two null fields from the weekly diff (`stats/storage.py:191`). Saves noise, not money. |
| 6 | **YouTube Data API** (`YOUTUBE_API_KEY`), free 10,000 units/day | Stats sync 08:45 daily (channels + playlistItems + videos, about 3-5 units) | Subscribers 5 on every snapshot since 09-27. OAuth login for uploads expired about 10-28 (ticket M-01 due 09-20, overdue) | None worth fixing on quota | Weekly is enough. The real gap is the upload login (M-01). |
| 7 | **Meta Graph API** (`META_IG_ACCESS_TOKEN`), free | `ig_fetch_insights.py` (biweekly Sun task), token refresh launchd 10:30 | Token expired, so the 10-18 and 11-01 IG stats runs pulled nothing (task run summaries). Fixed 11-03 (auto-refresh) | `ig_content` timeseries last point 10-04 (`releases/the-deceiver-single.json`); the task still tracks July posts of The Deceiver | Repoint the task to "newest posts" or pause it until the next post exists. |
| 8 | **Google Sheets** (`GOOGLE_CREDENTIALS_FILE`, `GOOGLE_SHEETS_ID`), free | `/sync` skill -> `push_to_sheets.py`, manual only | `label_tiers.json` ("regenerates on every push") last written 2026-09-01, so **no push since about 09-01** (inferred) | The `/sync` skill defaults to sync-back (`.claude/skills/sync/SKILL.md:13-15`); memory `si-sheet-sharing-and-push` says always `--no-sync` | Decide: retire the Sheet, or push weekly with `--no-sync`. |
| 9 | Discogs (`DISCOGS_TOKEN`), Gmail app password (`GMAIL_APP_PASSWORD`, `email_outreach.py`) | On demand only | n/a | none | none |
| 10 | **Symphonic Starter + Beatport add-on** ($10/month, renews the 8th; memory `symphonic-account-number`) | Distribution | Beatport is not used for new releases since bridge plan v2 (fixlist rows 20, 28, 45-55) | Paying for a store the plan dropped | **$120/year** IF the back catalogue stays on Beatport without the add-on. Unknown: ask Symphonic before the next renewal (**11-08, in 3 days**). |
| 11 | Claude Max 20x (EUR 180/month) | Every chat + all 16 scheduled tasks | About 52 scheduled runs/week (section 2) | About 24 of 52 runs/week end in one line or a silent skip (13:00 retry 7/week, mostly "SKIP"; IG task fires on 3 non-session days; refresh 1/3 and 2/3 = 14 one-liners) | Not money (flat plan), but usage headroom and **about 24 sidebar chats/week less** if moved to launchd. |
| 12 | Canva | Manual design | Plan level not recorded on disk | unknown | Record the plan + price once in the cost page. |
| 13 | IG session cookies (`IG_SESSION_ID`, `IG_CSRF_TOKEN`) | Old direct-read scripts (`ig_followback_checker.py:102`, `ig_audit_queue_freshness.py:96`) | Direct reads OFF since 09-14 (`IG_DIRECT_API_ENABLED = False`) | A live login cookie of his account sits in a plain file it no longer needs | Risk, not cost: blank them after the IG chat confirms nothing reads them. |

Total paid spend today, est.: HikerAPI ~$6/month + OpenAI < $5 + Beatport $10 + Symphonic + Canva + Max.
The only fast money saving is Beatport. The rest is about control: one view, real counts, early warnings.

---

## 2. Schedule map

| Time | Job (runner) | Output | Who reads it | Flag |
|---|---|---|---|---|
| 06:30 | SC refresh 1/3 (`sc-weekly-health`, Claude task) | candidates file, `sc-weekly-<date>.md` (overwritten) | one-line chat | pure script: launchd candidate |
| 07:30 | SC refresh 2/3 (`sc-refresh-0730`) | same file | one-line chat | pure script: launchd candidate |
| 08:30 | SC refresh 3/3 + daily SC report + git commit (`sc-refresh-0830`) | report, commit | Amir (SC chat) | keep; report could go into the brief |
| 08:45 | stats sync (launchd `stats-sync`, `--skip instagram`) | `stats_snapshots/snapshot_*.json`, Monday weekly summary | score board, digest | **IG skipped, see B4**; same SC hour as 08:30 |
| 09:30 | IG dispatcher (launchd) | `dispatch-log.md`, popups | Amir via popup | repeats the same notify daily (8 days "engagement_log over cap") |
| 10:00 | SC session (Claude task) | `loop-close-sc-*.md`, session report | Amir, digest | keep |
| 10:30 | IG token refresh (launchd) | `ig-token-refresh.log` | nobody unless it fails | fine |
| 13:00 | SC retry (Claude task) | silent SKIP almost always | nobody | 12 runs, every summary seen = SKIP; gate could live in launchd |
| 15:00 | IG session (Claude task, fires DAILY, skips Tue/Thu/Sun) | `loop-close-ig-*.md`, report | Amir, digest | cron `* * 1,3,5,6` removes 3 empty chats/week |
| 20:00 | Socials digest (Claude task, new 11-05) | `socials-digest-<date>.md` + message | Amir | the seed of the one brief |
| 22:30 | heartbeat (launchd) | `dispatch-log.md`, popup | Amir | false "TEST SUITE RED" 10-26 to 11-04 (fixed 11-05) |
| Mon 08:11 | Spotify S4A read (Claude task, Chrome) | `generated_images/s4a_raw/`, weekly summary | score board | odd folder for stats raw text |
| Fri 18:00 | SC release stats (Claude task) | `releases/*.json` timeseries | nobody named | static tracks 4-6 months old: monthly is enough |
| Sun 20:00 | IG release stats, biweekly gate (Claude task) | `releases/the-deceiver-single.json`, artifact | Amir | tracks July posts; 2 empty runs (token) |
| 1st+15th 12:00 | SC maintenance (Claude task) | `sc-maintenance-*.md` + commit | Amir | fits a monthly system review |
| Fri 11-06 16:15 | SC sweep 3/3 (one-time) | unfollows | Amir | last one; folder is dead after |
| (draft) | Gap Radar weekly (`gap_radar/launchd/*.plist.draft`) | reports | Amir | not live; caps null (`gap_radar/schedule.json`) |
| other | `com.amir.berlin-*` (3), `io.gerowallet.*` (4) | other projects | n/a | share the Mac and Chrome; apartment Chrome blocked SC before (memory) |

Dead: 41 folders in `~/.claude/scheduled-tasks`, 16 registered, so **25 leftover one-time folders**
(e.g. `ig-resume-wed-0902`, `sc-finish-session-0925b`, `sc-unfollow-catchup-0917`).

Merge options: refresh 1/3 + 2/3 + 13:00 gate -> one launchd script (no LLM); Fri SC stats ->
monthly inside SC maintenance; SC morning report + digest -> one 20:00 brief (proposals P2).

---

## 3. The loop and where it breaks

```
GOAL ──> PLAN ──> TICKETS ──> WORK ──> DATA ──> REPORT ──> DECISION ──┐
 ^                                                                    │
 └────────────────────────────────────────────────────────────────────┘
```

| Link | Carried today by | Break | Evidence |
|---|---|---|---|
| Goal | `plans/targets.json` (metrics, Nov-Dec), `docs/brand/positioning.md`, `next-six-months.md` (09-13) | **B1. Goals live in 4+ places and disagree.** SC ladder copied in code; IG goal still "790 -> 1,200-1,500" in agent docs; no song, release or booking goal in `targets.json` | `sc_engagement_config.py:579`, `sc_maintenance.py:51`, `docs/ig-agent-context.md:29` (fixlist #4) |
| Goal -> Plan | strategy docs | **B2. Plan is stale.** 63 stale lines in docs agents read; Pinocchio date still 2026-11-06 in the release file; `release_context.json` empty since 08-15 | `review-2026-11-05-fixlist.md`; `releases/pinocchio-single.json` `release_date`; `scene_intelligence/release_context.json` |
| Plan -> Tickets | 2 boards: `plans/tickets.json` (80), `plans/control-panel/tickets.json` (56) | **B3. Tickets do not name the target they move.** `helps` is prose on all 47 open; no `metric` field. 3 open tickets past due (R-02 09-28, M-01 09-20, M-04 10-01). No per-ticket "updated" date, so staleness is invisible | `plans/tickets.json` fields block |
| Tickets -> Work | parent chats + side chats, 13 handovers | **B4a. Handovers merged by hand**, 38 open decisions in handovers next to 32 tickets waiting on Amir | facts 11.A |
| Work -> Data | snapshots, ledgers, release JSONs | **B4. Data for the #1 target is not collected.** Score-board spec says drop `--skip instagram`; the plist still has it, so IG followers has one reading (11-02, 966). IG reach: never entered (`manual_entries.json` has only Bandcamp). HikerAPI ledger = estimates only. 82 raw renders unlogged | `com.inchofshadow.stats-sync.plist:11`; spec `docs/superpowers/specs/2026-11-01-score-board-design.md:174`; snapshots 10-01 to 11-05 |
| Data -> Report | 215 files in `docs/reports`, digest, RM pages, popups | **B5. Too many reports, some read nothing.** 6 chats + 2 popups a day; SC geography and Spotify null fields written daily; `sc-weekly-<date>.md` overwritten 3x/day; RM has no usage log | facts 9, 11.D; `stats/collectors.py:267` |
| Report -> Decision | Amir reads chats | **B6. Red lines repeat without becoming tickets.** "engagement_log over cap" 8 days in a row, "TEST SUITE RED" 9 nights, "balance 0" 6 days: each needed one ticket, got a daily line | `docs/reports/dispatch-log.md` 10-26 to 11-05 |
| Decision -> Goal | memory files, handovers, boards | **B7. Decisions are not written back to goals.** `targets.json` has no review date inside the period; digest shows a stale IG number (`stats/socials_digest.py:159-163` reads the newest snapshot that has IG, i.e. 11-02); Google Sheet unpushed since about 09-01 (inferred) | as cited |
| Rules under all links | memory + CLAUDE.md | **B8. Rules not loaded or not enforced.** Two memories, index 28.3 KB over the limit, no parent CLAUDE.md, 0 hooks (facts 10; drafts ready) | `MEMORY.md` 28,307 bytes |
| Money under all links | 3 separate ledgers | **B9. No single spend view.** Claude (no Gero), OpenAI (no raw renders), HikerAPI (estimates), subscriptions nowhere. Worktree copies of `claude_spend.json` exist (`.claude/worktrees/*/stats_snapshots/`); a run from a worktree would book spend there | as cited |
| Time under all links | 16 tasks + 4 launchd | **B10. About 24 of 52 weekly runs carry no decision**; 25 dead task folders | section 2 |

---

## 4. Upgrade options per break (small to big)

| Break | Option | Effort | Saves | Risk |
|---|---|---|---|---|
| B4 | Drop `--skip instagram` from the stats plist and use the spec's 1-call HikerAPI read (stats side, not engagement code) | 15 min | IG target becomes measurable daily; 1 call/day ($0.03/month) | Low; spec already approved |
| B4 | Log `raw_render.py` renders into the imagine ledger; write `actual_calls` back in the HikerAPI ledger (the latter is an IG-chat ticket) | 30 min | true OpenAI + HikerAPI numbers | Low |
| B9 | `stats/spend.py`: one table from the 3 ledgers + HikerAPI balance + a subscriptions list (Symphonic, Beatport, Canva, Max) with warn lines (HikerAPI < $10, Claude > 70% of credit, OpenAI > $15) | 1-2 h | stops dry weeks like 10-27; Amir's money in one line | Low |
| B9 | Gap Radar crowding: 4 searches, medium effort, cache per gap | 30 min | about $4 per profile (est.) | Medium: fewer sources per verdict |
| B10 | Cron fix IG task to Mon/Wed/Fri/Sat; move refresh 1/3, 2/3 and the 13:00 gate to one launchd script; delete 25 dead folders after a dry-run list | 1 h + his yes | about 24 chats/week; fewer permission-prompt stalls | Medium: SC side is his decision (10-25); launchd needs FDA (solved) |
| B5 | Drop SC geography and Spotify daily calls to weekly; move stats sync to 09:45 | 20 min | about 10 API calls/day, SC hour clash | Low |
| B6 | Brief rule: any red line seen 2 days running opens a ticket automatically (in `plans/tickets.json`, `who: claude`, section System) and stops repeating | 1 h | Amir's attention; ends 8-day repeats | Low |
| B3 | Add `metric` (a key from `targets.json`, or "none") and `updated` to every ticket; RM /tickets groups by metric | 1 h | shows which work moves which number; staleness visible | Low |
| B1 | `targets.json` as the only goal file: add release, songs and booking goals (dates only, his words); a check flags drift vs the SC ladder copy in engagement config (read-only, no edit there) | 1 h + his answers to facts 12.1-12.3 | ends 4-place drift | Low |
| B8 | Apply the 5 ready drafts (parent CLAUDE.md, slim index, memory merge, enforced settings, brief spec) | 1 h, his yes per draft | stale rules out of side chats | Low, backups planned |
| B8 | Hooks: **SessionStart** prints today's brief headline (3 lines from the newest brief file); **PreToolUse** blocks `*.fxp` writes, `git push`, `/accounts/` URLs; **Stop** on scheduled runs auto-archives finished chats | 2 h | rules enforced, not remembered; Amir starts each chat already briefed | Medium: a wrong hook blocks work; test on one rule first |
| B7 | Weekly decision page (P3) writes answers straight into `targets.json`, tickets and handovers (one script), then the page clears | half a day | about 30 min/week of re-asking (est.) | Low |
| B4a | Skill `/handover-close`: writes the handover, updates the ticket and the "decisions" list in one step | half a day | hand merging | Low |
| B2 | Apply fixlist A rows (26) in one pass; then a monthly `/doctor` + stale-line scan on the 1st | 2 h | agents stop acting on Nov-6 and 3-EP facts | Low |
| B7 | Sheet: retire, or a weekly `--no-sync` push inside the brief job | 15 min | one less silent copy | Low |

---

## 5. The one loop (one page, 11 steps)

1. **Goals** live in one file, `plans/targets.json`: numbers (IG, SC, Spotify, Bandcamp list) AND
   dated goals (next release, songs, booking), each with a review date.
2. **Monthly (1st, with SC maintenance)**: Claude proposes rung changes from the data; Amir ticks;
   the script writes them into `targets.json`. Nothing else holds a goal.
3. **Tickets** carry `metric` (a target key or "none"), `who`, `due`, `updated`. One board file for
   areas, Control Panel as a section of it (or keep two files, but one RM view).
4. **Work** happens in area chats; closing a ticket runs `/handover-close` (ticket, handover,
   decisions list updated in one step).
5. **Data**: every job writes one snapshot or ledger line with REAL counts: stats sync 09:45 incl.
   the IG 1-call read; HikerAPI actual calls; every paid render or Claude call in its ledger.
6. **Spend**: `stats/spend.py` folds all ledgers + balances + subscriptions into one table, with
   warn thresholds.
7. **Automation** runs on launchd when it is a pure script; a Claude task only when judgement or
   browser work is needed (sessions, S4A read, the brief).
8. **One brief at 20:00** (the Socials digest grown to all areas, proposals P2): 🔴 first, then
   targets vs rungs (one line each), spend line, "🙋 waits on Amir today" (max 3), Now per area.
9. **Red rule**: a 🔴 that repeats a second day becomes a ticket (`who: claude`) and leaves the brief.
10. **Weekly decision page** (his day): every 🙋 item as a one-line choice; answers are written back
    by script into targets, tickets and handovers.
11. **SessionStart hook** shows the latest brief headline in every new chat, so every chat starts
    from the same truth; the parent CLAUDE.md and one memory carry the rules.

Breaks closed: B1 (1-2), B2 (2, monthly scan), B3 (3), B4a (4), B4 (5), B9 (6), B10 (7),
B5 (8), B6 (9), B7 (10), B8 (11).

---

## 6. Recommended strategy changes (max 8)

**1. One brief instead of six reports**
- Was: about 6 chat reports + 2 popups a day, red lines repeated daily (`dispatch-log.md`).
- Change to: one 20:00 all-area brief (step 8) + the red-to-ticket rule (step 9). SC morning and
  session reports go to files; popups only for real red.
- Based on: facts 9; dispatch log 10-26 to 11-05; `stats/socials_digest.py` already reads the
  loop-close files, SC health, targets and tickets.
- Why: Amir is the bottleneck (32 tickets + 38 decisions); repeated lines hide real red.
- Steps: extend `socials_digest.py` -> `daily_brief.py`; add the red-repeat ticket rule; switch SC
  report steps to "write file only"; run both in parallel 3 days, then turn off the old messages.
- Saves: about 5 messages/day; est. 10-15 min/day of his reading.

**2. Scripts on launchd, judgement on Claude tasks**
- Was: 52 scheduled Claude runs/week, about 24 with no decision; 25 dead folders.
- Change to: refresh 1/3 + 2/3 + 13:00 gate in one launchd script; IG task cron Mon/Wed/Fri/Sat;
  Fri SC stats folded into monthly maintenance; dead folders removed after a dry-run list.
- Based on: `list_task_runs` (retry: every summary SKIP; IG: empty runs on 11-01, 11-03, 11-05);
  section 2.
- Why: fewer chats, fewer permission stalls (10-27 freeze), same data.
- Steps: dry-run list of folders -> his yes; IG chat confirms the SC/IG schedule change (engagement
  side); write the launchd plist with the FDA python path; watch 3 days.
- Saves: about 24 chats/week; SC: -95 reads/day if he also picks 2 refresh runs.

**3. Measure the #1 target daily**
- Was: IG followers read once (11-02); plist still `--skip instagram` though the 11-01 spec drops it.
- Change to: the 1-call HikerAPI read in stats sync at 09:45; IG reach entered every Monday with the
  S4A read.
- Based on: plist line 11; spec line 174; snapshots; `manual_entries.json`.
- Why: the score board and digest show a 3-day-old IG number and will drift further.
- Steps: edit the plist args, reload, check the next snapshot has `instagram`.
- Saves: no cost (about $0.03/month); restores the main goal signal.

**4. One spend page with early warnings**
- Was: 3 ledgers, Gero and raw renders missing, HikerAPI ran dry 6 days, wrong "$5 ≈ 4 months" text.
- Change to: `stats/spend.py` + a spend line in the brief; caps: Claude 70% warn, OpenAI $15/month,
  HikerAPI warn under $10.
- Based on: section 1 rows 1-3.
- Why: money and supply problems show up a month early instead of at zero.
- Steps: build the script (read-only over ledgers); add the Gero ledger path; log raw renders;
  ticket for the IG chat to fix the dispatcher text and write `actual_calls`.
- Saves: avoids repeats of the 10-27 stall (6 days without vetting supply).

**5. Decide Beatport before 11-08**
- Was: $10/month Beatport add-on, Beatport dropped for new releases.
- Change to: ask Symphonic whether old releases stay live without the add-on; cancel if yes.
- Based on: memory `symphonic-account-number`; fixlist rows 20, 28, 45-55.
- Why: the only clear money saving in the system.
- Steps: Amir sends one Symphonic ticket (draft on request); decide on the answer.
- Saves: $120/year.

**6. Goals in one file, tickets tied to them**
- Was: goals in 4+ places; tickets with prose `helps`, 3 overdue, no `updated` date.
- Change to: `targets.json` holds all goals with review dates; every ticket gets `metric` +
  `updated`; RM /tickets groups by metric; a read-only drift check vs the engagement configs.
- Based on: B1, B3 evidence.
- Why: shows which work moves which number, and kills the 790 -> 1,500 kind of drift.
- Steps: Amir answers facts 12.1-12.3; Claude adds fields to both boards; RM view; drift check in
  the monthly review.
- Saves: est. 20 min/week of "what is this ticket for"; fewer stale goals in agent docs.

**7. Close the decision loop weekly**
- Was: decisions asked in many chats; answers land in handovers by hand; Sheet unpushed since about 09-01.
- Change to: the weekly decision page (P3) with a write-back script into targets, tickets and
  handovers; `/handover-close` skill; Sheet retired or pushed weekly with `--no-sync`.
- Based on: facts 11.A; B4a, B7.
- Why: a decision should change a file once, not be re-asked.
- Steps: build the page from the outreach-page pattern (db ticks); write-back script; skill.
- Saves: est. 30 min/week of re-asking and merging.

**8. Rules that load and rules that hold**
- Was: two memories, index over the limit, no parent CLAUDE.md, 0 hooks.
- Change to: apply the 5 drafts in `plans/strategy/drafts/`; add 3 hooks (SessionStart brief headline,
  PreToolUse guards for `.fxp`/`git push`/`/accounts/`, auto-archive on scheduled-run stop);
  monthly `/doctor` + stale-line scan on the 1st.
- Based on: facts 10; proposals P1; fixlist (63 stale lines).
- Why: the cheapest fix for wrong actions is a rule that cannot be skipped.
- Steps: his yes per draft; one hook at a time, tested in a side chat; then the monthly review.
- Saves: fewer wrong-fact actions in side chats; est. 5 min per new chat of re-briefing.
