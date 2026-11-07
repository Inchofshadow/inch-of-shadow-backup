# One daily brief (draft spec, 2026-11-05)

NOT LIVE. Proposal P2 option A. Builds on the existing 🎬 Socials digest (`stats/socials_digest.py`,
task `socials-daily-digest`, 20:00), which already reads the day's reports and `plans/targets.json`.
The Socials chat owns that script; the brief would extend it or wrap it, with the Socials chat's agreement.

## What Amir sees at 20:00 (one message, one chat)

```
Inch of Shadow · Thu 11-05

🔴 Problems        (only when there is one; else this block is gone)
   YouTube login expired · 2 days. Fix: run yt_auth.py, click Allow.

🔥 Now
   🎵 Release 2 · HTN cover 🙋 · 🎵 Release 9 · Symphonic submit 🙋🌐
   🎬 Socials 14 · Bandcamp Friday 🙋 · 27 · IG like list 🎃 · 29 · SC inbox 🎃🌐
   💶 Income 5 · Radar weekly run 🎃
   (areas with nothing Now are left out)

🎯 Nov 30   IG 969 → 996 · SC 470 → 510 · Spotify listeners 94 (rung 90 ✅)

🤖 Ran today   IG ✅ 10/10 · SC ✅ 10/10 · sweep ✅ · stats ✅   (one line, details in files)

🙋 Waiting on you today: 3   → decision page (weekly)
```

Rules:
- Max about 12 lines. Problems first, always.
- A line appears only when it changed or needs him.
- Session reports, the SC 08:30 report and maintenance verdicts still get written to files; the brief
  links them only on a 🔴.
- macOS popups only for 🔴: detection/challenge, a login expired, a real test failure (two nights in a row).

## What goes quiet
| Today | After |
|---|---|
| SC 08:30 daily report (message) | file only, one 🤖 line in the brief |
| SC 10:00 session report (message) | file only, one 🤖 line |
| IG 15:00 session report (message) | file only, one 🤖 line |
| SC 13:00 retry one-liner | silent unless it ran |
| SC 06:30 / 07:30 refresh one-liners | silent |
| Heartbeat popup 22:30 | popup only for 🔴 |
| 🎬 Socials digest 20:00 | becomes this brief |

## Data sources (all exist today)
`docs/reports/*session*`, `scene_intelligence/autonomy_state.json`, `stats_snapshots/*`,
`plans/targets.json`, both ticket boards (`bucket`, `who`, `chrome`), `docs/reports/dispatch-log.md`.

## Open for Amir
Which chat gets it (⚙️ System, or a new "Inch of Shadow · daily" chat), and 20:00 or a morning time.
