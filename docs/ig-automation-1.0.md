# IG Automation 1.0 — archive manifest

**What this is:** the complete, working state of the first IG engagement automation
("IG Automation 1.0", April 22 → August 30, 2026), frozen so Amir can return to it
any time. Git tag: **`ig-automation-1.0`**.

## What 1.0 was
- CC-era architecture: Claude-in-Chrome as hands, Claude Code as brain, Amir as captain;
  later hybrid (from 2026-08-26 sessions ran from Claude Code via the ig-engagement task).
- Engine + rails: `scene_intelligence/ig_engagement.py`, `ig_engagement_config.py` (phases,
  caps, human-like timing), queue builder / freshness audit / follow-back checker /
  merge / close_loops, 1-script daily ledger, session JSONL logging.
- Docs: `docs/ig-engagement-sop.md` (1,564 lines), `docs/ig-agent-context.md`,
  `docs/cowork-task-ig.md` + the retired CC paste bodies.
- Results over the program: followers 790 → 925, ratio recovered to ~1:1, 315 automation
  follows, 10 active reciprocators at close, all documented incidents infrastructure-level
  (never an account warning).

## Why it closed
Full audit 2026-08-30: `docs/reports/ig-system-findings-2026-08-30.md` (uptime analysis,
enforcement gaps, API risk map, decisions D1-D7). Superseded by **2.0**: single-operator
sessions, zero-token dispatcher, per-endpoint API law, export-only reciprocity,
ticket-driven work (`TICKETS.md`).

## How to go back
```bash
git checkout ig-automation-1.0
```
or browse it read-only: `git show ig-automation-1.0:docs/ig-engagement-sop.md` etc.
Nothing was deleted going into 2.0 — retired docs/files were moved, not removed, and
every state file has dated backups in `scene_intelligence/backups/`.
