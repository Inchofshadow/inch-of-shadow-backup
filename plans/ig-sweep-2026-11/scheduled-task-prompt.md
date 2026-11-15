# IG sweep: the 6 one-time scheduled tasks

CREATED 2026-11-15 (Amir "Yes, create them"), saved in Auto mode. Allow rules below NOT added: the settings edit was refused by the safety check; Amir adds them if a run stops on a prompt.

| Task id | When (Berlin) |
|---|---|
| ig-sweep-run-1-1117 | Tue 2026-11-17 16:00 |
| ig-sweep-run-2-1119 | Thu 2026-11-19 16:00 |
| ig-sweep-run-3-1122 | Sun 2026-11-22 16:00 |
| ig-sweep-run-4-1124 | Tue 2026-11-24 16:00 |
| ig-sweep-run-5-1126 | Thu 2026-11-26 16:00 |
| ig-sweep-run-6-1129 | Sun 2026-11-29 16:00 |

Prompt (same for all six, only N and the date change):

> IG sweep run N of 6 (Amir's Unfollow picks, decided 11-14). Work in
> /Users/amir/Desktop/Inch of Shadow/Inchofshadowcode. Read
> docs/cowork-task-ig-sweep.md now and run its BODY exactly, using only its
> allowed commands. ArtifactData out_dir for step 1a:
> /Users/amir/Desktop/Inch of Shadow/Inchofshadowcode/plans/ig-sweep-2026-11/picks_live/<YYYY-MM-DD today>.
> If the gates or the plan say STOP, stop with no clicks and report the lines.
> End with the short report from the runbook.

Allow rules to add to the parent `Inch of Shadow/.claude/settings.local.json`
at the same time (prefix rules, so the run never stops on a prompt):
- `Bash(.venv/bin/python scene_intelligence/ig_sweep.py *)`
- `Bash(.venv/bin/python scene_intelligence/ig_daily_ledger.py --claim ig_sweep --kind browser)`
- the ArtifactData tool (read of the picks page)
`.venv/bin/python scene_intelligence/ig_log_action.py *` and `--show` are already covered (check the `.venv` twin exists).
