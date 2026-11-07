# State file rotation: dry run (M4, IG lane, 2026-11-07)

Amir: "Yes, dry run". Read-only: nothing was moved, written or deleted.

## What a 90-day cut would do to `scene_intelligence/engagement_log.json`

Cut date: entries before 2026-08-09 move to the archive. Oldest entry: 2026-03-16.

| | IG entries | SC entries | Size |
|---|---|---|---|
| Stay in the live file | 849 | 2,936 | ~944 KB (now 1,702 KB) |
| Move to the archive (.json.gz) | 2,247 | 1,270 (+1 other) | ~72 KB zipped |

- 1,279 handles would exist only in the archive.
- `hidden` (97), `session_notes` (88) and the other top keys stay as they are; only `log` entries move.

## Readers checked (11 scripts)

| Script | Looks back | 90 days OK? |
|---|---|---|
| ig_engagement.py | like cooldowns up to 65 d, prominent 60 d, skips 7 d, no-new-content 30 d | yes |
| ig_merge_session_log.py | writes today's events; follow history comes from the tracker, not this log | yes |
| close_loops.py | that day only | yes |
| ig_health_check.py | 7 days | yes |
| ig_dispatcher.py | file size only | yes |
| sc_engagement.py | artist 30 d, track 60 d, today, week | yes (SC chat to confirm) |
| sc_maintenance.py | 30 d | yes (SC chat to confirm) |
| sc_log_manual.py, sc_weekly_health.py | write / weekly | SC chat to confirm |
| **push_to_sheets.py** | **ALL history: sets `last_engaged` per SI contact from the newest log entry** | **NO** |

## The one problem

`push_to_sheets.py` (lines 266-290) rebuilds `last_engaged` for every SI contact from the whole log, and writes "" when it finds nothing. After a cut, every contact last engaged before 2026-08-09 would lose its `last_engaged` date in SI and the sheet.

FIXED 2026-11-07 (Amir "Keep existing dates", option 2): push_to_sheets now keeps the newer of the stored and the log date, never blanks it.

Options were:
1. push_to_sheets also reads the archive (small change, SI code).
2. push_to_sheets keeps the existing `last_engaged` when the log has nothing newer (smaller change).

Also to know: the ig-expert agent reads the log for long-run analysis, so it would need to read the archive for anything older than 90 days.

## The real run (only after Amir's yes)

1. Back up engagement_log.json.
2. Move entries before the cut into `scene_intelligence/archive/engagement_log-to-2026-08-08.json.gz`.
3. Outside session hours (not 10:00 SC, not 15:00-16:00 IG on Mon/Wed/Fri/Sat), and with the SC chat's OK, since the same file holds SC data.
4. Test: the next IG and SC sessions log, score and report as before.
