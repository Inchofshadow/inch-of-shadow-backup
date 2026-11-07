# archive/rm-cli

What: `release_manager/cli.py`, the old terminal front end of the Release Manager (715 lines).

Why: dead-code list `plans/strategy/dead-code-list-2026-11-05.md` row A5. Nothing imports it
(no code, no test, no scheduled task, no launchd job, no skill), the 2026-07-04 full audit found it
unrunnable (bare imports collide with the package), and the web UI
(`python -m release_manager.webapp`) does the same job.

Date: 2026-11-07. Approved by Amir 2026-11-07 ("Yes, your picks").

Undo (from the repo root):

```bash
git mv archive/rm-cli/cli.py release_manager/cli.py
git rm -q archive/rm-cli/README.md
```
