# Gate: Python 3.9 to 3.11 for every job (⚙️ System 69) (2026-11-15, Fable, on Amir's "gate")

Opus did the switch between 11-08 and 11-11, the engagement part on Amir's "do it now" before this read. So this gate checks a live setup after the fact. Record: `plans/strategy/system-69-python-switch-2026-11-08.md`.

## Verdict: approve. Nothing to fix.

| Claim | Checked today | Result |
|---|---|---|
| All 5 LaunchAgents run the 3.11 binary and load the venv | each plist's program + `PYTHONEXECUTABLE` | ✅ 5 of 5 |
| That pattern really gives the venv | ran the real binary with `PYTHONEXECUTABLE` set | ✅ Python 3.11.15, `sys.prefix` = `.venv`, `sys.executable` = `.venv/bin/python3` (so scripts the dispatcher starts get the venv too); anthropic 0.84.0, playwright and browser-cookie3 import |
| Every agent's last run was clean | `launchctl print` | ✅ all five: last exit code 0 |
| Gap Radar's scheduled run works after the log fix | its log, Sun 11-15 05:00 | ✅ ran on schedule: "Done: 0 profiles", $0 (cap) |
| Every approved `python3` command has a venv twin | parent `settings.local.json` | ✅ 26 script rules, 0 without a twin; old rules kept as the undo path |
| The session docs call the venv | `docs/cowork-task-ig.md`, `docs/sc-engagement-sop.md`, `docs/sc-agent-context.md` | ✅ no plain `python3 <script>` command left |
| Live sessions ran without stopping on a prompt | Socials digests + loop-close files | ✅ SoundCloud 11-12, 11-13, 11-14 and Instagram 11-13, 11-14 all closed; 11-12 and 11-13 scored 10/10 |
| The lock file carries the two late packages | `requirements-lock.txt` | ✅ playwright and browser-cookie3 are in it |

## Watch items (no action now)
- The plists name the folder `cpython-3.11.15-...`. If uv ever replaces that patch version, the path changes and the agents stop with a clear error. The switch file already says so.
- The sweep's own approval rules (`ig_sweep.py *`, the ledger claim) are not added yet. They belong to the sweep task creation (gate `2026-11-15-ig-sweep.md`).

## Found on the way, not a Python problem
- **The Sat 11-14 20:00 daily brief and Socials digest did not run.** Both task runs failed at 20:02 and 20:08 with "You've hit your weekly limit, resets 10pm". No brief or digest file exists for 11-14. The 15:00 Instagram session and the SoundCloud session earlier that day ran. A scheduled run that starts after the weekly limit is reached fails without a word to Amir.
