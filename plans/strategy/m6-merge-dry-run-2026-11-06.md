# M6 dry run: one branch, all code in git, a current Python (2026-11-06)

Batch 4 of the strategy review, decision D16. This is a LIST; nothing was merged, deleted or installed.
Checked on the shared checkout (branch `score-board`) with read-only git commands.

## 1. Merge score-board into main

| Fact | Checked with | Result |
|---|---|---|
| main is behind score-board | `git rev-list --left-right --count main...score-board` | main 0 ahead, score-board 223 ahead |
| Conflicts | `git merge-tree <base> main score-board` | 0 conflict markers: a fast-forward |
| Other chats on this checkout | `git branch` shows two `+` worktree branches | 🎬 Bandcamp and 🎬 YouTube work in their own worktrees |

So "merge to main" is a pointer move, no content changes: `git push . score-board:main` (local ref update, no
remote, no checkout). After it, main and score-board are the same commit. "Work on main" then means one
`git checkout main` on the shared checkout while no other chat is mid-edit (the working tree does not change,
only the branch name every chat sees). Amir's standard: `/code-review ultra` before merging to main, which he
triggers himself; it needs no GitHub remote.

## 2. Stale branches (19 besides main and score-board)

| Branch | Last commit | State | Proposal |
|---|---|---|---|
| sc-* (14 branches), ig-0624-merge-fix | May to July 2026 | every commit already in score-board | delete the branch names after the merge (`git branch -d`, refuses anything unmerged) |
| sc-600-1000-experiment | 2026-07-03 | merged; the experiment rule lives in memory, evaluated 07-17 | same |
| curator-discovery | 2026-05-16 | **16 commits not in score-board** | REVIEW: tag it `archive/curator-discovery` and delete the branch, or keep; the curator DB work from it was redone later (promotion-expert) |
| claude/socials-bandcamp-0893b7 | 2026-11-06 | live, 6 own commits, 🎬 Socials merges on Amir's word | leave |
| claude/socials-youtube-e6decb, claude/gap-radar-* | 2026-11-05 | merged | the worktree chats delete their own when done |

## 3. Code folders outside git

From the code map (rec 6): `music-tools/` and `youtube/tools/` are outside the repo. Adding them is one
`git add` each after Amir's yes; nothing moves. Check for secrets first (`grep -rn "key\|token"`), same
rule as `.env`.

## 4. Backup files in git

The page said "120 backup files tracked in git". Checked today: **29** `.bak` files are tracked (23 are the
deliberate `scene_intelligence/backups/sweep-20260831/releases/` set, 4 in `releases/`, 2 in `plans/`).
The other 55 `scene_intelligence/*.bak.*` files are untracked and belong to the SC tracker's health
refresh (3 per day, 500 KB each): that is the M4 rotation case, owned by the SC chat.

## 5. Python 3.12

Every scheduled job runs on `/Library/Developer/CommandLineTools/.../3.9` (end of life Oct 2025). The move is
its own ticket, after the merge: a pinned 3.12 (`python.org` installer or `uv`), one `requirements.txt`
install, every scheduled task and LaunchAgent re-pointed, each job run once by hand, Full Disk Access
granted to the new binary (memory: launchd-needs-full-disk-access). Not before Amir's yes, and not on a
session day for IG or SC.

## What waits on Amir (D16)
1. Yes to the pointer move (section 1) after his `/code-review ultra`.
2. Yes to deleting the 16 merged branch names; a call on curator-discovery.
3. Yes to adding the two folders to git.
4. Python 3.12 as a ticket, when.
