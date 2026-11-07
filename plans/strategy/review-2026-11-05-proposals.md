# Strategy review: draft proposals (2026-11-05)

DRAFTS ONLY. Nothing here is applied. Each part lists options and my pick (marked ⭐). Amir
decides in step 2/3. Facts behind them: `review-2026-11-05-facts.md` sections 9-11.

---

## P1. LLM system: one memory, one entry point, enforced must-nevers

### P1.1 Two memories → one
Fact: the parent folder memory (146 files, current) and the code-folder memory (65 files, last
touched 2026-07-26, still says "2026 plan: 3 EPs", "Email Outreach done", "in Tel Aviv until
08-03"). Chats started in the code folder, and per the docs its worktrees (🎬 YouTube, 🎬 Bandcamp),
read the old one.

| Option | What | Risk |
|---|---|---|
| A ⭐ | Back up the old code-folder memory, then point it at the parent memory (one folder for all chats). Useful old facts get copied into parent files first, after Amir ticks a list | Low; undo = restore the backup |
| B | Keep both; put a top line in the old index: "outdated, read the parent memory" | Chats still load stale facts first |
| C | Leave as is | Stale rules keep reaching side chats |

### P1.2 Memory index over the limit
Fact: 28 KB, limit 25 KB (or 200 lines); the newest rules are cut.

| Option | What |
|---|---|
| A ⭐ | Shorten every index line to one short hook (≤150 chars); merge rules that were updated several times (e.g. side-chat delete x3) into one file; move superseded rules to an `_archive` file not in the index. Target ≤15 KB, so there is room to grow |
| B | Only trim the longest lines to get under 25 KB (will be over again in a week) |

### P1.3 No rules file where chats start
Fact: chats start in `Inch of Shadow/`; it has no CLAUDE.md; project rules load only after a
code-folder file is touched; our own skills (`/release`, `/ig`, `/sc`, `/promo`) appear late.

| Option | What |
|---|---|
| A ⭐ | A short `Inch of Shadow/CLAUDE.md` (≤60 lines): who Amir is, the 6 areas + emoji map, where things live (boards, handovers, facts), the HARD RULES in one line each, "read Inchofshadowcode/CLAUDE.md for code work". Plus symlink the 9 code-folder skills into the parent `.claude/skills` (as was done for agents on 10-22) |
| B | Start every chat in the code folder instead (loses the parent folder's files and the newer memory) |

### P1.4 Must-never rules that a hook or setting can enforce
Fact: 12 HARD RULES, all prose, 0 hooks. The docs: prose can be skipped, hooks and permission
rules cannot. Only the mechanical ones can move; judgement rules stay prose.

| Rule | Enforce how | Pick |
|---|---|---|
| Repo never pushed / no remote | permission deny: `git push`, `git remote add` | ⭐ |
| Never move/rename/delete his files without a yes | permission ask: `mv`, `rm`, `trash`, `rsync --delete` outside scratch | ⭐ |
| Serum .fxp: never rewrite the chunk | hook: block writes to `*.fxp` / `*.serumpreset` | ⭐ |
| No email search without ask | permission ask on the Gmail tools (every call shows a card) | ⭐ |
| No touching IG settings (/accounts/, Edit profile) | hook on browser navigate: block URLs with `/accounts/` | maybe |
| Temporary files: no raw HTML left | Stop hook runs `hygiene_check.py` read-only and warns | maybe |
| Scope, verify first, taste 📌, archive first, handles, AI on images, areas | judgement: stay prose | stays |

### P1.5 Keep it consistent
- ⭐ Monthly 15-minute rule review (1st of the month, in ⚙️ System): run `/doctor`, list stale or
  contradicting lines, Amir ticks what goes. Fits the existing 1st/15th maintenance.
- ⭐ When a rule changes, update its one file; never append a third "UPDATE" block.

---

## P2. Notifications: calm by default, loud only for red

Fact: about 6 reports a day in different chats + 2 macOS popups; the heartbeat popped a false
"TEST SUITE RED" for 5 nights; ~21 of the newest 40 sidebar chats are finished automated runs.

| Option | What |
|---|---|
| A ⭐ | **One daily brief at 20:00** (extend the 🎬 Socials digest into an all-area brief, posted in one chat): 🔴 problems first, then 🔥 Now per area (max 3 each), numbers vs the Nov-Dec targets in one line, anything that waits on Amir today. Session reports, SC morning report and maintenance verdicts go to files only, and a 🔴 line in the brief links them. macOS popups only for 🔴 (detection, login expired, real test failure) |
| B | Keep per-area digests (Socials exists; add one per area) |
| C | Keep as is |

Also (any option):
- ⭐ Automated-run chats: archive them automatically after they finish (the app has an
  auto-archive setting; ⚙️ System would read it first and show Amir before changing).
- ⭐ Remove the ~25 leftover one-time task folders in `~/.claude/scheduled-tasks` after a
  dry-run list (files rule: his yes first).

---

## P3. Work method: fewer open loops on Amir

Fact: 32 of 55 open tickets wait on Amir, plus 38 open decisions in handovers.

| Option | What |
|---|---|
| A ⭐ | **Decision day**: once a week (his pick of day), one page with every open "🙋 Amir" item as a one-line choice + my recommendation, answered by ticks on the phone (same pattern as the outreach page). Everything parked stays off it |
| B | Each parent chat asks its own decisions when he opens it (today's way) |
| C | Close or park anything waiting on him for more than 30 days, automatically, with a list he can undo |

Combined with the 🔥 max-3 rule, A keeps the daily load at "what is Now" and the weekly load at
"one decision page".
