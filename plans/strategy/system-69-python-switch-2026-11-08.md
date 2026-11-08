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
