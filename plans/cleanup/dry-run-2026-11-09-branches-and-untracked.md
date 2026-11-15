# Dry run 2026-11-09: leftover branches and files outside git

Read-only. Nothing was moved, deleted or committed by this list. Each group waits for Amir's tick.

## A. Branches and worktrees

| Branch | State | Worktree | Proposal |
|---|---|---|---|
| `score-board` | fully in main (same work, main moved on) | none | delete the name |
| `claude/gap-radar-gero-fcc8d8` | fully in main (GR-07, 11-05) | none | delete the name |
| `claude/gap-radar-profiles-ffbe27` | fully in main (GR-03, 11-05) | none | delete the name |
| `claude/socials-youtube-e6decb` | fully in main (11-05) | `.claude/worktrees/gap-radar-gero-fcc8d8`, 0 uncommitted, untouched since 11-05 | remove the worktree, delete the name |
| `claude/socials-bandcamp-0893b7` | **6 commits NOT in main** (11-06): the Bandcamp Friday message drafts v1 to v3, the signed version, the record "sent to 53 followers", and a one-line naming fix in farewell-single.json | `.claude/worktrees/gap-radar-profiles-ffbe27`, 0 uncommitted | bring the work into main first (one commit at a time with `git apply --3way`, never a sequencer), then remove the worktree and delete the name |

Undo for a deleted name: `git branch <name> <sha>` (the shas are in `git reflog` and in this list's commit). Tags `archive/curator-discovery` and `ig-automation-1.0` stay.
Note: 🎬 Socials 14 (Bandcamp Friday) is still "in progress" on the board, but that branch records the message as sent on 11-06. It closes once the record is in main.

## B. Files outside git (78 new, plus other chats' unsaved edits)

### B1. Commit as records (git already tracks files of the same kind; nothing changes on disk)
- Daily records: 15 in `docs/reports/` (daily briefs 11-06 to 11-08, Socials digests 11-05 to 11-08, IG and SC loop-close reports, Gap Radar logs), 6 stats snapshots in `stats_snapshots/`, 2 SC session reports (11-06, 11-07).
- Gap Radar reports: 14 entries in `gap_radar/reports/` (11-05 to 11-07).
- Plans and notes: `plans/half-the-night-cover-*` (5), `plans/genre-cover-board-2026-11-03.md`, `plans/symphonic-genre-list-2026-11-03.md`, `plans/research/` (2), `plans/app-factory/PLAN.md`, `plans/income-500-new-chat-prompt.md`, `plans/review-export-farewell-single.json`, `plans/handovers/system/passwords-2fa.md` (handover only, no account data), `plans/handovers/release/inbox/` (2 screenshots).
- Cleanup tools and their logs: `plans/cleanup/CLEANUP-LIST.md`, `scan_dupes.py`, `trash_a.py`, `trash-a-log-20261105-041355.json`, `undo-trash-a-20261105-041355.py`, `dupes.json`, `dupes-100k.json`.
- `plans/outreach-page/ticks-export-2026-11-05/` (420 KB, the phone-page ticks of 11-05; contact data, so it stays LOCKED in the GitHub backup).

### B2. Keep on disk, ignore in git from now on (backup copies)
- 11 ticket and target backups `plans/.tickets.json.bak-*`, `plans/.targets.json.bak-*`, `plans/control-panel/.tickets.json.bak-*`; 1 handover backup `plans/handovers/system/.system.md.bak-*`; 3 release backups `releases/*farewell-single*.bak*`.
- One `.gitignore` block: `*.bak-20*` and `*.bak.20*` (the 34 backups git already tracks stay tracked).

### B3. To the Trash (after the tick)
- `plans/cleanup/backup-dryrun-2026-11-06.json` (2.1 MB): an old dry-run file list of the backup, superseded by every weekly run.

### B4. Yours to OK
- `CLAUDE.md` (code folder): your backup exception text (11-06/07) is in the file but was never committed. Proposal: commit it as written.

### B5. Not mine, left alone
- Other chats' own unsaved edits: the IG and SC state files in `scene_intelligence/` (engagement data, their owner chats commit them), 5 handovers, `docs/ig-session-scorecard.md`, `plans/strategy/review-2026-11-05-facts.md`, `stats_snapshots/claude_spend.json`, `stats_snapshots/daily_brief_state.json`, `stats/ig_token_state.json`, `releases/pinocchio-single.json`.

## Applied 2026-11-09 (Amir: "Yes, apply all")
- Bandcamp work into main one commit at a time (`git apply --3way`): 2427af4, 953e2b0, 89166ce, d8ffe77, 53b6e5d, 0479ef0; main now matches the branch for those files. Old tip tagged `archive/socials-bandcamp-0893b7` (f999db1).
- Worktrees removed: `.claude/worktrees/gap-radar-gero-fcc8d8`, `.claude/worktrees/gap-radar-profiles-ffbe27` (both clean).
- Names deleted (undo `git branch <name> <sha>`): score-board db2d156, claude/gap-radar-gero-fcc8d8 5d1e36d, claude/gap-radar-profiles-ffbe27 2e88ae3, claude/socials-youtube-e6decb edcaf06, claude/socials-bandcamp-0893b7 f999db1.
- Records committed: 4c8f358 (52 files), 8f35960 (126 files). CLAUDE.md: 536b9d4. Ignore block: 936b1db.
- To the Trash: `plans/cleanup/backup-dryrun-2026-11-06.json` -> `~/.Trash/backup-dryrun-2026-11-06.json`.
- 🎬 Socials 14 (Bandcamp Friday) closed from the branch record.
