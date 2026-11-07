# Retired launchd agents

Retired 2026-07-05 (Amir's decision, audit fix-plan item 25).

Both agents had NEVER run successfully: macOS TCC blocks a headless
launchd python3 from reading anything under ~/Desktop, so every
scheduled run since installation died with "Operation not permitted"
(exit 2) before executing a single line. Fixing them required granting
Full Disk Access to python3; Amir chose manual mode instead
(privacy-first, and the manual routine was already the documented SOP).

- `com.inchofshadow.sc-health-refresh.plist` - ran sc_weekly_health.py
  Sun+Wed 08:00. Manual replacement: Claude Code runs
  `python3 scene_intelligence/sc_weekly_health.py` on Wednesdays
  (~15-70 read-only SC API calls, pre-announced), exactly as
  docs/sc-agent-context.md and the cowork task bodies already describe.
- `com.inchofshadow.stats-sync.plist` - ran stats/daily_sync.py daily
  08:00. Manual replacement: run on request / when working with the
  Stats Dashboard.

Do not reinstall without deciding the TCC question first.
