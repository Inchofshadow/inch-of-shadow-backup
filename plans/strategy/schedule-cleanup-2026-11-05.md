# Schedule cleanup: dry-run list + drafts (2026-11-05)

⚙️ System 74. Follows `review-2026-11-05-system-loop.md` section 2 and rec 2. This is a LIST and a
set of DRAFTS: no schedule changed, no folder deleted, nothing installed. Every row waits for
Amir's yes (ask-before-moving rule); the IG and SC engagement schedules belong to the IG and SC
chats, so those rows are proposals to them, not edits.

How each row was checked (today, 20:40-20:50, branch `score-board`):
- folders: `ls` + `stat` (birth, modified) on the 40 folders in `~/.claude/scheduled-tasks/`
- registered or not: the app's task list (`list_scheduled_tasks`, 16 registered: 11 recurring, 5 one-time)
- last run: `lastRunAt` from that list and `list_task_runs` summaries; unregistered folders have no run
  record in the app, so "last run" is the fire date written in their own SKILL.md
- every SKILL.md read in full; the 4 plists in `~/Library/LaunchAgents/com.inchofshadow.*` read in full
- the scripts behind the drafts: `sc_weekly_health.py` (exit codes 0-4), `sc_engagement.py --retry-gate`
  (prints `RETRY VERDICT: RUN|SKIP`), `sc_release_stats.py` (2 reads); the FDA python3.9 ran `--help`
  on the first and third and the retry gate itself (local read, no SoundCloud call)
- REVIEW = I am not sure; needs a look before the move, not just a yes

Counts: 40 folders. 16 registered. **28 dead** (24 never registered any more + 4 registered one-time
tasks that already fired), **1 pending** (`sc-sweep-run-3-1106`, fires Fri 11-06 16:15), 11 recurring.
The audit's "41 / 25" was off by one each way; these are the counted numbers.

---

## 1. Dry-run list: one-time or superseded task folders

All paths are under `~/.claude/scheduled-tasks/`. Proposed action for every row is the same move:
**Trash via Finder** (drag the folder to the Trash, never `rm`). **Undo** for every row: open the
Trash, select the folder, File > Put Back (restores the exact path). Before the first move, one
copy of the whole folder for safety: Finder > Compress on `scheduled-tasks` (a zip next to it in
`~/.claude/`), delete the zip after a week.

Step 0 (owner chats, before the move): the 4 registered rows are first removed from the app's
task list (the `delete_scheduled_task` tool, in the chat that owns them), so the registry and the
folders agree; the folder is then trashed like the others.

### 1a. Never registered any more (24): cannot fire, nothing reads them

| # | Folder | Created | Fire date in SKILL.md / last run | Status | Action |
|---|---|---|---|---|---|
| 1 | `ig-cookie-probe-sun-0906` | 09-06 | one-time Sun 09-06 09:05 | spent; direct IG reads OFF since 09-14 | Trash |
| 2 | `ig-daily-health-check` | 08-19 (edited 08-25) | daily 09:30 (IG 1.0) | superseded 08-31 by the launchd dispatcher (`com.inchofshadow.ig-dispatcher`, 09:30) | Trash |
| 3 | `ig-followback-friday-probe` | 08-27 | one-time Fri 08-28 10:10 | spent; T-011 already asked to delete it | Trash |
| 4 | `ig-follows-10-to-12-review` | 06-27 | one-time, ~1 week after 07-10 | spent (Deceiver era) | Trash |
| 5 | `ig-implementation-day` | 08-31 | one-time Mon 08-31 10:00 | spent; the IG 2.0 build happened | REVIEW: the text is the shortest summary of the T-003..T-007 locked spec; check `TICKETS.md` holds it, then Trash |
| 6 | `ig-post-session-close` | 08-19 | 17:00 on session days (IG 1.0) | superseded: the 15:00 session runs `close_loops` itself (run summaries say "ran and closed") | Trash |
| 7 | `ig-pre-session-checker` | 08-23 (edited 08-25) | Mon + Fri 10:15 (IG 1.0) | superseded: `ig_followback_checker.py` is a direct-read script, OFF since 09-14 | Trash |
| 8 | `ig-reciprocity-backfill-saturday` | 08-28 | one-time Sat 08-29 10:00 | spent | Trash |
| 9 | `ig-renew-unfollows-jul10` | 07-06 | one-time Fri 07-10 | spent | Trash |
| 10 | `ig-resume-sat-0905` | 09-03 (edited 09-06) | one-time Mon 09-07 12:30 | spent | Trash |
| 11 | `ig-resume-wed-0902` | 09-02 | one-time Wed 09-02 12:30 | spent | Trash |
| 12 | `ig-weekly-queue-audit` | 08-23 (edited 08-25) | Thu 14:00 (IG 1.0) | superseded: `ig_audit_queue_freshness.py` direct reads OFF; the dispatcher audits via HikerAPI | Trash |
| 13 | `sc-discovery-refresh-0913` | 09-12 | one-time Sun 09-13 10:00 | spent | Trash |
| 14 | `sc-engagement-catchup-0911` | 09-11 | one-time Fri 09-11 17:20 | spent | Trash |
| 15 | `sc-engagement-finish-0911` | 09-11 | one-time Fri 09-11 20:10 | spent | Trash |
| 16 | `sc-finish-session-0925` | 09-25 | one-time Fri 09-25 | spent | Trash |
| 17 | `sc-finish-session-0925b` | 09-25 (edited 09-25) | one-time Fri 09-25 | spent | Trash |
| 18 | `sc-friday-discovery-refresh` | 09-24 | Fri 09:00 weekly | superseded 10-25/10-27 by the three daily refresh tasks | Trash |
| 19 | `sc-health-catchup-0912` | 09-08 | one-time Sat 09-12 11:00 | spent | Trash |
| 20 | `sc-session-followup-1006` | 10-06 | one-time Tue 10-06 | spent | Trash |
| 21 | `sc-session-manual-front-1001` | 10-01 (edited 10-01) | one-time Thu 10-01 | spent | Trash |
| 22 | `sc-sunday-sweep-reminder` | 09-01 (edited 09-29) | Sun 09:00 weekly | superseded by the daily refresh | Trash |
| 23 | `sc-unfollow-catchup-0916` | 09-15 | one-time Wed 09-16 | spent | Trash |
| 24 | `sc-unfollow-catchup-0917` | 09-15 (edited 09-17) | one-time Thu 09-17 10:00 | spent | Trash |

### 1b. Registered one-time tasks that already fired (4) + the one still pending

| # | Folder | Created | Last run (app) | Status | Owner chat | Action |
|---|---|---|---|---|---|---|
| 25 | `ig-token-refresh-live-test` | 11-03 | 11-04 10:45, succeeded (M-09 live test) | registered, disabled | ⚙️ System (stats) | step 0 (unregister), then Trash |
| 26 | `provider-cap-back-to-300` | 11-03 | 11-03 23:50, succeeded (cap back to 300) | registered, disabled | 🎬 IG chat (engagement config) | step 0, then Trash |
| 27 | `sc-sweep-run-1-1104` | 11-03 (edited 11-04) | 11-04 16:15, succeeded | registered, disabled | 🎬 SC chat | step 0, then Trash |
| 28 | `sc-sweep-run-2-1105` | 11-03 (edited 11-04) | 11-05 16:15, succeeded | registered, disabled | 🎬 SC chat | step 0, then Trash |
| 29 | `sc-sweep-run-3-1106` | 11-03 (edited 11-04) | not yet; fires Fri 11-06 16:15 | registered, enabled | 🎬 SC chat | **KEEP** until it ran; then rows 27-28 treatment |

---

## 2. Recurring tasks (11 Claude tasks + 4 launchd jobs)

"Decision inside" = does a human need to decide something in that chat (yes), or is it a script with a
one-line echo (no). "Chats/week" = sidebar chats the task opens.

| Task | Time (actual fire incl. jitter) | What it does | Output file | Who reads it | Decision inside | Owner chat | Chats/week | Proposal |
|---|---|---|---|---|---|---|---|---|
| `sc-weekly-health` "SC refresh 1/3" | 06:30 daily | `sc_weekly_health.py`: token check, follow-backs, discovery crawl to the hourly budget | `scene_intelligence/discovery_candidates_<date>.json`, `sc_follow_tracker.json`, `docs/reports/sc-weekly-<date>.md` | nobody (one-line chat); the 20:00 digest reads the md file | no | 🎬 SC | 7 | **move to launchd** (draft A, slot 1) |
| `sc-refresh-0730` "2/3" | 07:38 daily | same script, next seeds, appends to the same file | same | nobody (one-line chat) | no | 🎬 SC | 7 | **move to launchd** (draft A, slot 2) |
| `sc-refresh-0830` "3/3 + report" | 08:42 daily | same script + daily health report in chat + `git commit` of the data | same + commit | Amir (camp check, follow-backs, churn) | no (churn alarm = red line, no choice to make) | 🎬 SC | 7 | **move to launchd** (draft A, slot 3 commits), report moves into the 20:00 brief (P2); SC chat decides. Alternative: keep this one task as the single SC morning chat |
| `sc-engagement` | 10:00 daily | browser session in the pinned Chrome: U2 lane, 20 like+follow pairs, PASS C | `scene_intelligence/sc_session_report_<date>.md`, `docs/reports/loop-close-sc-<date>.md` | Amir, digest | yes (judgement + clicks) | 🎬 SC | 7 | keep |
| `sc-engagement-retry` | 13:12 daily | `sc_engagement.py --retry-gate`; a session only on RUN | one-line chat | nobody | no: 12 runs, every summary SKIP (10-25 to 11-05), 1 failed on DNS 10-26 | 🎬 SC | 7 | **move the gate to launchd** (draft B); task stays registered for a manual Run now when the notification says RUN |
| `ig-engagement` | 15:14 daily (fires 7 days, acts Mon/Wed/Fri/Sat) | browser session via `docs/cowork-task-ig.md` | `docs/reports/loop-close-ig-<date>.md`, session report | Amir, digest | yes on 4 days; no on Tue/Thu/Sun (runs of 10-16 s: 10-29, 11-01, 11-03, 11-05) | 🎬 IG | 7 (3 empty) | **propose to the IG chat**: cron `0 15 * * 1,3,5,6` (same task, 3 empty chats/week gone) |
| `socials-daily-digest` | 20:08 daily | `stats/socials_digest.py --write` + send to the 🎬 Socials chat | `docs/reports/socials-digest-<date>.md` + the message | Amir | no (it IS the message) | 🎬 Socials | 7 | keep; grows into the one brief (`drafts/daily-brief-spec.draft.md`) |
| `spotify-s4a-weekly-read` | Mon 08:11 | reads Spotify for Artists in his Chrome, `stats/spotify_s4a.py`, `weekly_summary.py --refresh-spotify` | `generated_images/s4a_raw/<date>-*.txt`, weekly summary | score board, weekly summary | no, but needs Chrome (so Claude) | ⚙️ System (stats) | 1 | keep (browser work); side note: raw text sits in `generated_images/` |
| `sc-weekly-release-stats` | Fri 18:09 | `sc_release_stats.py`: 2 reads, one datapoint per track | `releases/the-deceiver-single.json`, `releases/farewell-single.json` | nobody named (RM shows the timeseries) | no | 🎵 Release data, SC API key = 🎬 SC | 1 | **move to launchd** (draft C), weekly as now or monthly (audit) |
| `ig-weekly-release-stats` | Sun 20:01, self-gated to every 2 weeks | `ig_fetch_insights.py` (Graph) + edits the IG Growth artifact | `releases/the-deceiver-single.json` ig_content timeseries, `plans/ig-content-performance-log.md`, artifact | Amir | no decision, but the artifact edit needs Claude | 🎬 IG / Socials | 0.5 | keep, but repoint: it still tracks the July Deceiver posts; last 3 runs pulled nothing (token 190 on 10-18, 11-01 x2; renewed 11-03). Propose: pause until the next post, or point it at "newest posts" |
| `sc-monthly-maintenance` | 1st + 15th 12:11 | `sc_maintenance.py` + `hygiene_check.py` + commit of the report | `docs/reports/sc-maintenance-<date>.md` | Amir | yes (RED asks for a decision) | 🎬 SC | 0.5 | keep; if the Friday SC stats go monthly, run them in this slot |

launchd (no chats, keep as they are):

| Job | Time | Script | Output |
|---|---|---|---|
| `com.inchofshadow.stats-sync` | 08:45 | `stats/daily_sync.py` | `stats_snapshots/`, `docs/reports/stats-sync-launchd.log` |
| `com.inchofshadow.ig-dispatcher` | 09:30 | `scene_intelligence/ig_dispatcher.py` | `docs/reports/dispatch-log.md`, popups |
| `com.inchofshadow.ig-token-refresh` | 10:30 | `stats/ig_token_refresh.py` | `docs/reports/ig-token-refresh.log` |
| `com.inchofshadow.ig-heartbeat` | 22:30 | `scene_intelligence/ig_heartbeat.py` | `docs/reports/heartbeat-launchd.log`, popup |

Note for draft A: the stats sync at 08:45 reads SoundCloud in the same hour as the 08:30 refresh
(audit row 4b). The audit's 09:45 move for stats sync is a separate ⚙️ System ticket; not in this list.

---

## 3. Drafts (in `plans/strategy/drafts/launchd/`, every file headed "DRAFT, not installed, needs the SC chat's ok + Amir's yes")

| Draft | Replaces | How it keeps today's behaviour | What goes quiet |
|---|---|---|---|
| A: `com.inchofshadow.sc-refresh.plist.draft` + `sc_refresh.sh` | refresh 1/3, 2/3 (and 3/3 if the SC chat agrees) | same script, same three times (one plist, three calendar dicts); the 08:30 slot runs the same `git add` list and commit message as the task; notification on RECIPROCATOR CHURN or a non-zero exit (1 token, 2 CAPTCHA, 3 budget, 4 health, gate); one line per run in `docs/reports/sc-refresh-launchd.log` | 14 one-line chats/week (21 with the 08:30 slot); the daily report text goes into the 20:00 brief, which already reads `sc-weekly-<date>.md` |
| B: `com.inchofshadow.sc-retry-gate.plist.draft` + `sc_retry_gate.sh` | the 13:00 cron of `sc-engagement-retry` | same gate command; SKIP = one log line in `docs/reports/sc-retry-gate.log`; RUN = log line + macOS notification "Run now on sc-engagement-retry"; the Claude task stays registered for that manual start | 7 chats/week |
| C: `com.inchofshadow.sc-release-stats.plist.draft` + `sc_release_stats.sh` | `sc-weekly-release-stats` | same script, Friday 18:00 (monthly variant in the plist comment: Day 1, 12:10, before SC maintenance); output table to `docs/reports/sc-release-stats-launchd.log`; notification on error or NO DATA | 1 chat/week |

All three: interpreter `/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9`
(the stats-sync binary with Full Disk Access), `WorkingDirectory` = the repo (so `.env` loads as today),
scripts to be copied to `deploy/launchd/` on install (next to the two plists already kept there).
Verified today with that binary: `requests` + `dotenv` import, `--help` of both scripts, and the retry gate
(`RETRY VERDICT: SKIP (82 actions logged today ...)`, exit 0). Not verified: a live `sc_weekly_health.py`
run under launchd (that is the 3-day watch after install). launchd also runs a missed slot once after the
Mac wakes, which the Claude tasks do not.

Install order and undo per draft: `drafts/launchd/README.md`.

---

## 4. What Amir gains

- Chats: 52 scheduled Claude chats/week today (49 daily + 3 weekly, plus 0.5 maintenance). Drafts A (slots 1+2), B and C
  remove **22/week**; the IG cron fix (IG chat) **3 more**; the 08:30 slot (SC chat) **7 more**. Floor: **20 chats/week**
  (7 SC sessions, 4 IG sessions, 7 digests, S4A, IG stats, maintenance), all with a decision or a browser in them.
- Dead folders: 28 fewer in `~/.claude/scheduled-tasks/` (40 -> 12 after the pending sweep run is spent).
- API reads/day: the moves change nothing (same scripts, same calls: about 290 SoundCloud reads/day, 2 more on Friday).
  The only read saving is the SC chat's own option from the audit: 2 refresh slots instead of 3 = about **-95 reads/day**
  (about 195/day), one dict less in draft A. HikerAPI: untouched (300/day cap).
- Fewer permission-prompt stalls: the three moved jobs have no chat to stall (10-27 froze two runs that way).
