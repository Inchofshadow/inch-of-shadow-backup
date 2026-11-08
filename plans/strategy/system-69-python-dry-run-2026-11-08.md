# System 69 dry run: which Python every job runs on (2026-11-08, read-only)

Nothing was changed. This lists what runs on the old Python 3.9 (end of life since October 2025) and the options to move it.

## What runs today

**5 LaunchAgents (Inch of Shadow), all on the Command Line Tools 3.9 binary**
(`/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9`, the binary that has Full Disk Access since 2026-09-03):

| Agent | When | Script | Engagement? |
|---|---|---|---|
| com.inchofshadow.ig-dispatcher | daily 09:30 | scene_intelligence/ig_dispatcher.py | yes, IG owner |
| com.inchofshadow.ig-heartbeat | daily 22:30 | scene_intelligence/ig_heartbeat.py | yes, IG owner |
| com.inchofshadow.ig-token-refresh | daily 10:30 | stats/ig_token_refresh.py | no |
| com.inchofshadow.stats-sync | daily 08:45 | stats/daily_sync.py | no |
| com.inchofshadow.gap-radar | Sun 05:00 | gap_radar/schedule.py | no |

**Release Manager:** started by hand with `python3` = `/usr/bin/python3` (3.9.6).

**Scheduled Claude tasks:** 20 recurring tasks call plain `python3` (resolves to 3.9.6); 14 of them are IG/SC engagement tasks
(ig-engagement, sc-engagement, sc-engagement-retry, ig-pre-session-checker, ig-post-session-close, and so on). Plus about 17 dated one-off tasks from Sep to Nov that no longer fire.

**Not ours, left alone:** the Berlin apartment agents (`/usr/bin/python3`) and the Gero agents (zsh scripts).

**Pythons on the machine:** 3.9.6 (system), 3.11.15 (uv-managed, `~/.local/bin/python3.11`, already installed). No 3.12. `uv` 0.12.3 is in `~/.local/bin`.
Packages today: Pillow 11.3, Flask 3.1, numpy 2.0.2, onnxruntime 1.19.2, rembg 2.0.61, anthropic 0.84, openai 2.41, gspread 6.1 (all have 3.11/3.12 wheels).

## Options

- **A. Project environment on 3.11, no download (recommended).** `uv venv --python 3.11 .venv` in Inchofshadowcode, install requirements.txt into it.
  Re-point the 3 non-engagement agents and Release Manager first, run each by hand. 3.11 has security fixes until October 2027.
  Amir grants Full Disk Access to the new binary once (System Settings, one click per binary).
  The 2 IG agents and the 14 engagement tasks move only through the IG and SC owner chats, on a non-session day.
- **B. Same as A on 3.12.** Needs `uv python install 3.12` (a download from the official uv Python builds, about 40 MB). Security fixes until October 2028.
- **C. Park it.** Nothing breaks today; 3.9 just gets no more security fixes.

## Rules that apply
- Never on an IG or SC session day for the engagement pieces; engagement code and config are hands off for every chat but the owners.
- Record each old path before changing it (memory record-before-changing); keep the old plist as `.bak`.
- Exit 2 "Operation not permitted" after a switch = the new binary has no Full Disk Access yet.
