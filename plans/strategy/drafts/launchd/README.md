# launchd drafts (schedule cleanup, 2026-11-05)

DRAFT, not installed, needs the SC chat's ok + Amir's yes. Nothing here runs. The list and
the reasoning are in `plans/strategy/schedule-cleanup-2026-11-05.md`.

| Draft | Replaces (Claude task) | Runs | Chat saved | Undo |
|---|---|---|---|---|
| `com.inchofshadow.sc-refresh.plist.draft` + `sc_refresh.sh` | `sc-weekly-health` 06:30, `sc-refresh-0730`, and `sc-refresh-0830` if the SC chat agrees | `sc_weekly_health.py` at 06:30, 07:30, 08:30; slot 3 commits the data | 14/week (21 with the 08:30 slot) | `launchctl unload`, delete the plist, re-enable the tasks |
| `com.inchofshadow.sc-retry-gate.plist.draft` + `sc_retry_gate.sh` | the daily cron of `sc-engagement-retry` | `sc_engagement.py --retry-gate` at 13:00; notification only on RUN | 7/week | `launchctl unload`, delete the plist, put the cron back |
| `com.inchofshadow.sc-release-stats.plist.draft` + `sc_release_stats.sh` | `sc-weekly-release-stats` Fri 18:00 | `sc_release_stats.py` Fri 18:00 (or monthly, see the plist comment) | 1/week | `launchctl unload`, delete the plist, re-enable the task |

All three use the interpreter of `com.inchofshadow.stats-sync.plist`
(`/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9`,
Full Disk Access granted). Checked 2026-11-05: that binary imports `requests` and `dotenv`, prints
`--help` for `sc_weekly_health.py` and `sc_release_stats.py`, and ran `sc_engagement.py --retry-gate`
(local read, no SoundCloud call) with exit 0.

Install order when approved (one at a time, watch 3 days each):
1. `cp <script>.sh deploy/launchd/ && chmod +x deploy/launchd/<script>.sh`
2. `cp <name>.plist.draft ~/Library/LaunchAgents/<name>.plist`
3. `launchctl load ~/Library/LaunchAgents/<name>.plist`
4. disable the Claude task it replaces (the SC chat does this; the task folder stays until the dry-run list is approved)
5. after 3 clean days: the task's cron is removed, or the task deleted

Not in this folder: the IG task's day fix (`0 15 * * 1,3,5,6`) is a cron change on the Claude task, not launchd; it is a proposal to the IG chat.
