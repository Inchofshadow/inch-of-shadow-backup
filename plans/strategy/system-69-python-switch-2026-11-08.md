# System 69: non-engagement jobs moved to Python 3.11 (2026-11-08)

Amir picked option A (3.11, no download). Follows the dry run in `system-69-python-dry-run-2026-11-08.md`.
The 2 IG LaunchAgents (ig-dispatcher, ig-heartbeat) and the 14 IG/SC engagement scheduled tasks were NOT touched; they move only through the IG and SC owner chats, on a non-session day.

## The environment
- `Inchofshadowcode/.venv`, made with `uv venv --python 3.11.15 .venv` (uv 0.12.3, no download). `.venv/` added to `.gitignore`.
- Real binary (the one launchd runs, the one for Full Disk Access):
  `/Users/amir/.local/share/uv/python/cpython-3.11.15-macos-aarch64-none/bin/python3.11`
- Libraries pinned to the SAME versions the 3.9 setup ran (a plain install pulled anthropic 2.6, openai 3.46, Pillow 13; this ticket changes Python only). Full list: `requirements-lock.txt`.
  Rebuild: `uv venv --clear --python 3.11.15 .venv && uv pip install --python .venv/bin/python -r requirements-lock.txt`
- `requirements.txt` gained `PyYAML` and `httpx`: the code and tests import them, the 3.9 setup only had them by luck (user site-packages).
- Tests: `.venv/bin/python -m pytest -q tests` = 1411 passed (3.9 baseline: 1411 passed).

## How the agents load the venv
Launching the real binary directly skips the venv. Each plist runs the real binary and sets
`PYTHONEXECUTABLE=/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode/.venv/bin/python3`, which makes Python 3.11 use the venv (checked: `sys.prefix` = `.venv`, anthropic 0.84.0).
Launchd probe: the 3.11 binary read a Desktop file under launchd (exit 0); `/bin/cat` in the same probe got "Operation not permitted". So the binary already passes Desktop access today.
If uv ever updates 3.11 to a new patch version, that path changes and needs Full Disk Access again.

## Old values and undo (one line per agent)
All three had the same old ProgramArguments[0]:
`/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9`
Copies of the old files: `~/Library/LaunchAgents/com.inchofshadow.<name>.plist.bak-2026-11-08`.

| Agent | Old args | Check after the switch | Undo |
|---|---|---|---|
| stats-sync (08:45) | python3.9 `stats/daily_sync.py` | import check only (no same-day guard; a hand run = 2nd snapshot + 1 HikerAPI read). First real run 08:45 today. | `cd ~/Library/LaunchAgents && launchctl unload com.inchofshadow.stats-sync.plist && cp com.inchofshadow.stats-sync.plist.bak-2026-11-08 com.inchofshadow.stats-sync.plist && launchctl load com.inchofshadow.stats-sync.plist` |
| ig-token-refresh (10:30) | python3.9 `stats/ig_token_refresh.py` | launchd kickstart, exit 0: "2026-11-08: token 4 days old, 56 left ... No call." | `cd ~/Library/LaunchAgents && launchctl unload com.inchofshadow.ig-token-refresh.plist && cp com.inchofshadow.ig-token-refresh.plist.bak-2026-11-08 com.inchofshadow.ig-token-refresh.plist && launchctl load com.inchofshadow.ig-token-refresh.plist` |
| gap-radar (Sun 05:00) | python3.9 `gap_radar/schedule.py` | `--dry-run` by hand with the launchd setup, exit 0, no calls. All 7 profiles blocked by the monthly radar cap ($70.54 of $70), so today's 05:00 run spends $0. | `cd ~/Library/LaunchAgents && launchctl unload com.inchofshadow.gap-radar.plist && cp com.inchofshadow.gap-radar.plist.bak-2026-11-08 com.inchofshadow.gap-radar.plist && launchctl load com.inchofshadow.gap-radar.plist` |

## Release Manager
- Old start: `python3 -m release_manager.webapp` (= /usr/bin/python3, 3.9.6).
- New start, in Inchofshadowcode: `.venv/bin/python -m release_manager.webapp` (port 5001).
- Restarted 2026-11-08 01:07 (last request 01:03:09, no child jobs); `/` and `/tickets` answer 200.
- Undo: stop it, start it again with `python3 -m release_manager.webapp`.

## Backup snapshot
`plans/cleanup/backup_snapshot.py` walks the whole folder (it ignores .gitignore), so the weekly GitHub backup would have taken the 609 MB `.venv` (11,702 files, one of 124 MB, over GitHub's 100 MB limit). `SKIP_DIRS` now holds `.venv`; dry run after: 0 venv files, 0 files over 50 MB.
Undo: set `SKIP_DIRS = {".git"}` again.

## Still open (System 69 stays open)
- ig-dispatcher, ig-heartbeat and the 14 engagement scheduled tasks: IG and SC owner chats, non-session day.
- The 6 non-engagement recurring scheduled tasks that call plain `python3` were outside this side chat's brief.

## Non-engagement scheduled tasks (2026-11-09, System chat, Amir "Python tasks")
Only 4 non-engagement tasks still fire (system-daily-brief, the first one, and the old one-offs are folders only).
Each prompt now says `.venv/bin/python` (run in Inchofshadowcode) instead of `python3`. Old copy beside each: `SKILL.md.bak-2026-11-09-python`.
Undo one: `cp ~/.claude/scheduled-tasks/<task>/SKILL.md.bak-2026-11-09-python ~/.claude/scheduled-tasks/<task>/SKILL.md`

| Task | Old line | Check |
|---|---|---|
| system-daily-brief-2 (20:00) | `python3 stats/daily_brief.py --write` | print-only run on .venv, exit 0 |
| socials-daily-digest (20:00) | `python3 stats/socials_digest.py --write` | print-only run on .venv, exit 0 |
| github-backup-weekly (Sun 12:00) | `... && python3 plans/cleanup/backup_snapshot.py --build ...` | dry run (no --build) on .venv, exit 0 |
| spotify-s4a-weekly-read (Mon 08:00) | `python3 Inchofshadowcode/stats/spotify_s4a.py ...` and `python3 Inchofshadowcode/stats/weekly_summary.py --refresh-spotify` | moved 2026-11-09 on Amir's "Yes, add them": two prefix rules added to the parent `.claude/settings.local.json` (`Bash(Inchofshadowcode/.venv/bin/python Inchofshadowcode/stats/spotify_s4a.py *)`, same for `weekly_summary.py`; the old python3 rules kept; backup `settings.local.json.bak-2026-11-09-python`). spotify_s4a.py ran on .venv. First live run Mon 08:11. |

Slip, 2026-11-09 02:50: checking weekly_summary.py with `--help` ran it for real (the script has no help flag): it wrote a stray "Week to 2026-11-08" section into plans/weekly-stats.md and made one Claude call (about $0.03, kept in stats_snapshots/claude_spend.json). The file had no other change, so it was restored with git; the Monday runs write the real week as usual. Check scripts with `--dry-run`, never `--help`, unless the script has argparse.

## Check 2026-11-11
- stats-sync ran on 3.11 every day 11-08 to 11-11 at 08:45 (exit 0, all 5 platforms saved).
- ig-token-refresh ran every day 11-08 to 11-11 (exit 0, "No call", 53 days left on 11-11).
- gap-radar: its first scheduled run (Sun 11-08 05:00, the first since it was installed 11-05) ended with launchd "last exit code = 78: EX_CONFIG" and wrote nothing to its log, so launchd never started the script (schedule.py has no exit 78). The macOS log for that hour has rotated away; the cause is unknown.
  The same plist copied with `--dry-run` and RunAtLoad, run under launchd on 11-11 17:15: exit 0, "Done: 0 profiles". So the setup works when started now.
  Next real check: Sun 11-15 05:00 (cap-blocked, $0). If it is 78 again, read `launchctl print gui/501/com.inchofshadow.gap-radar` and `/usr/bin/log show` for that hour right away.
- Release Manager runs `.venv/bin/python -m release_manager.webapp` (pid 77743, started 11-11 17:01).

## Gap Radar exit 78 fixed (2026-11-11, System chat, on the 💶 Income chat's report)
- Cause found by test: a copy of the job failed with 78 while its log pointed at `docs/reports/gap-radar-launchd.log`, and ran with exit 0 when the log pointed outside the Desktop. So launchd could not open that log file. The stats-sync log (works) carries the macOS `com.apple.macl` privacy mark, the gap-radar log does not (hypothesis for why).
- Fix: StandardOutPath and StandardErrorPath now `~/Library/Logs/InchOfShadow/gap-radar-launchd.log` (old value above; plist backup `com.inchofshadow.gap-radar.plist.bak-2026-11-11-log`). The old log stays in docs/reports as history.
- Proof: `launchctl kickstart` of the real job 11-11: exit 0, "Done: 0 profiles", all blocked by the radar cap, $0.
- Undo: `cd ~/Library/LaunchAgents && launchctl bootout gui/501/com.inchofshadow.gap-radar && cp com.inchofshadow.gap-radar.plist.bak-2026-11-11-log com.inchofshadow.gap-radar.plist && launchctl bootstrap gui/501 ~/Library/LaunchAgents/com.inchofshadow.gap-radar.plist`
- Same pattern may explain ig-heartbeat's exit 1 (its Desktop log was last written 09-02): passed to the IG chat for its move.

## IG + SC part moved (2026-11-11 21:05-21:20, System 69 side chat, Amir "do it now")
Amir chose to do it now instead of waiting for the Fable read on Sat 11-14 (the read stays on plans/strategy/gates/QUEUE.md). Window: after the 15:00 IG session and the 20:00 digests, before the 22:30 heartbeat; no IG/SC run was going.

**venv:** added `playwright==1.58.0` and `browser-cookie3==0.20.1` (the 3.9 versions; lazy imports in sc_engagement.py, ig_enrich_instagram.py, sc_extract_chrome_cookies.py, so the test suite did not catch them). Pulled in greenlet 3.5.6, lz4, pycryptodomex, pyee. `requirements-lock.txt` refreshed. An import scan of all 61 scene_intelligence scripts + hygiene_check.py finds nothing else missing.

**LaunchAgents** (same pattern: uv 3.11.15 real binary + PYTHONEXECUTABLE; log paths unchanged, both logs carry com.apple.macl):
| Agent | Old ProgramArguments[0] | Check | Undo |
|---|---|---|---|
| ig-dispatcher (09:30) | CLT python3.9 | import check only (a --dry-run still writes DRY-RUN lines into dispatch-log.md). First real run Thu 11-12 09:30. | `cd ~/Library/LaunchAgents && launchctl unload com.inchofshadow.ig-dispatcher.plist && cp com.inchofshadow.ig-dispatcher.plist.bak-2026-11-11-python com.inchofshadow.ig-dispatcher.plist && launchctl load com.inchofshadow.ig-dispatcher.plist` |
| ig-heartbeat (22:30) | CLT python3.9 | `launchctl kickstart` 21:11: exit 0, dispatch-log "heartbeat ok (dispatch fresh, sessions on cadence, tests green)" (zero API; a second heartbeat line tonight at 22:30) | same line with ig-heartbeat |

**Scheduled tasks** (`python3 scene_intelligence/...` and `python3 hygiene_check.py` -> `.venv/bin/python ...`, run in Inchofshadowcode; warnings about inline `python3 -c` left as text). Old copy beside each: `SKILL.md.bak-2026-11-11-python`. Undo one: `cp ~/.claude/scheduled-tasks/<task>/SKILL.md.bak-2026-11-11-python ~/.claude/scheduled-tasks/<task>/SKILL.md`
ig-engagement (6 lines), ig-weekly-release-stats (2), sc-weekly-health (1), sc-refresh-0730 (1), sc-refresh-0830 (1), sc-engagement (10), sc-engagement-retry (2), sc-monthly-maintenance (2), sc-weekly-release-stats (1).
Docs the runs follow, same replacement: docs/cowork-task-ig.md (16), docs/sc-engagement-sop.md (24), docs/sc-agent-context.md (2). Undo: `git checkout caea5e1 -- docs/cowork-task-ig.md docs/sc-engagement-sop.md docs/sc-agent-context.md` (not committed yet).

**Approvals:** 49 twin rules added to the parent `.claude/settings.local.json`: every `Bash(python3 X)` rule got a `Bash(.venv/bin/python X)` twin (scratchpad-path rules skipped); the old python3 rules stay. Backup `settings.local.json.bak-2026-11-11-python` (undo = copy it back).

**Read-only checks on .venv/bin/python, 21:15:** sc_engagement --check-gates GO; --retry-gate SKIP (46 actions today); ig_session_state --gates STOP exit 3 (correct: today's session ran); ig_session_confirm --check confirmed (standing); ig_daily_ledger --show ok; hygiene_check OK. Not run by hand (they call SC/IG/Graph or write state): sc_weekly_health, sc_maintenance, sc_release_stats, ig_fetch_insights, close_loops, ig_log_action; all import cleanly.
**First live runs to read:** SC refresh 06:30 / 07:30 / 08:30, ig-dispatcher 09:30, SC session 10:00 (all Thu 11-12); IG session Fri 11-13 15:00; sc-weekly-release-stats Fri 18:00; ig-weekly-release-stats Sun 11-15 20:00; sc-monthly-maintenance Sun 11-15 12:00.
A run that stops on an approval prompt = a missing twin rule: add the `.venv/bin/python` prefix rule for that command.
Nothing on 3.9 in the Inch of Shadow jobs any more except stdlib `python3 -m json.tool` lines and the hint text in ig_ops_guards.py:115.
