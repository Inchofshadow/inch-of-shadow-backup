# Scheduled task: system-daily-brief (draft, 2026-11-05)

For the ⚙️ System chat to create. Runs side by side with the existing reports and the 🎬 Socials
digest (`socials-daily-digest`, 20:00) for 3 days first; nothing is turned off by this task.

| Field | Value |
|---|---|
| name | `system-daily-brief` |
| schedule | daily 20:00, Europe/Berlin |
| chat | ⚙️ System (Amir's D13 pick, 2026-11-05) |
| working directory | `/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode` |
| script | `stats/daily_brief.py` (⚙️ System 72) |

## Prompt

```
Run `python3 stats/daily_brief.py --write` in /Users/amir/Desktop/Inch of Shadow/Inchofshadowcode
and post the printed brief as the message, exactly as printed, nothing else. No commentary, no
summary, no questions. If the script fails, post the last 5 lines of the error instead and stop.
```

## What the run writes
- `docs/reports/daily-brief-<date>.md` (the brief)
- `stats_snapshots/daily_brief_state.json` (last 7 days of 🔴 lines, for the red-repeats rule)
- a proposed ticket line under "## Proposed from the brief" in `plans/handovers/system/system.md`,
  only when the same 🔴 line shows two days running

## After 3 days side by side
Compare `docs/reports/daily-brief-*.md` with the socials digest and the chat reports it replaces
(spec table "What goes quiet" in `daily-brief-spec.draft.md`); then the Socials chat decides about its
digest and the other reports go file-only. Not part of this task.
