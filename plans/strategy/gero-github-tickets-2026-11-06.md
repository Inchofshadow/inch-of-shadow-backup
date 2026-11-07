# Gero's GitHub flow vs the IoS ticket boards: what to take (2026-11-06)

Read-only study. Sources: `Gero-Labs/gero-control-panel` via `gh` (logged in as ThirdEye707, read only), the repo's `.github/`, `docs/pm/`, `docs/gtm/`, git log on `origin/main`, the Gero memory files, and on the IoS side `plans/tickets.json`, `plans/control-panel/tickets.json`, `release_manager/tickets.py` + `board.py`, `tests/test_tickets.py` + `test_board.py`, `plans/AREAS.md`, `plans/handovers/`, `plans/strategy/review-2026-11-05-system-loop.md` section 3, `plans/handovers/system/github-setup.md`.

Nothing was edited in either repo. No issue, PR or comment was created.

---

## 1. How Gero's flow works, end to end

```
war plan (artifact) -> issue (Why / Outcome / How we measure `metric.id` / Verify / Source)
   -> label (PM, sprint-N, size, priority) + milestone (month gate)
   -> session branch (claude/..., feat/..., pm/...) in a worktree off origin/main
   -> PR (What / Why / Verification / Not in this PR; "Generated with Claude Code")
   -> CI: jest on push to main, path-gated check on help PRs
   -> Amir squash-merges (median 0.4 h after the PR opens)
   -> deploy.yml builds + deploys Cloud Run from main
   -> pm-tickets cron reads the 3 repos hourly, grades metric citation, /pm scoreboard
   -> gate snapshot on the 1st of the month with a written verdict
```

### Numbers (gero-control-panel, 2026-11-06)

| What | Number |
|---|---|
| Repo | private, created 2026-05-27, no branch protection (free plan), squash + merge + rebase all allowed, no auto-delete of branches (85 remote branches) |
| Issues | 39 total: 25 open, 14 closed. 37 written by Amir (ThirdEye707), 2 by Adam |
| Issue bodies with the Q4 shape | Why 34, Outcome 33, How we measure 31, Verify 32, Source 30, How to execute 23 |
| Issues citing a backticked metric id | 30 of 39 |
| Labels in use | `PM` 14, `sprint-1..8` 27, `size: S/M/L` 35, `priority: high/medium/low` 36, `medium` 19, `gero-card` 2, `enhancement` 3; the 9 GitHub default labels exist and are unused |
| Milestones | `Sept 2026 , BUILD + STRIKE` (0 open / 9 closed, due 30 Sep), `Oct 2026 , CLIMB` (2 / 2), `Nov , PRESS` (0 / 1), `Dec , CLOSE` (0 / 0), `Medium syndication` (19 / 0, due 28 Feb 2027). All five still "open" |
| Time to close | median 13 days, mean 9.9, none over 30 days |
| Age of the 25 open | 20 are 3-5 days old (the Medium batch of 2026-11-02/03), two Q4 PM issues (#56, #84) open 54 and 69 days, #101 (collectors dead) 26 days |
| Issues per month | Aug 12, Sep 2, Oct 5, Nov 20 (batches, not a stream) |
| Across the 3 Q4 repos | control-panel 39, gero-website 78 (53 `seo`, median close 8 days), nexus 165 (27 `nexus-website`, median close 4 days) |
| PRs | 100: 95 merged, 2 open, 3 closed unmerged. Authors: Amir 65, Adam 34, Dudi 1. Merged by Amir 58, Adam 36 |
| PRs by Claude sessions | 89 of 100 bodies carry "Generated with Claude Code"; 502 `Co-Authored-By: Claude ...` trailers on main (near every commit) |
| PR body shape | headings: Verification 22, What 17, Summary 9, Why 8, Tests 7, Gates 6, Not in this PR 4; 41 PRs have a Test/Verify section; 49 cite a metric id; only 8 say `Closes #N`, 44 mention an issue number |
| PR open to merge | median 0.4 h; 58 within 1 h; 84 within 24 h; 5 over 7 days |
| PRs per month | Jun 11, Jul 22, Aug 18, Sep 29, Oct 15, Nov 5 |
| Branch names | `claude/*` 16, `feat/*` 13, `seo/*` 8, `fix/*` 7, `pm/*` 6, `content/*` 5, `docs/*` 4, flat names 36 |
| Commits on main | 332 since 2026-05-27; 84 squash subjects ending `(#N)`, 11 real merge commits; prefixes `feat` 155, `fix` 64, `docs` 44, `content` 15, `chore` 15, `ci` 2, `infra` 1 |
| CI | `deploy.yml`: on push to main, `jest --ci` then Docker build, push, Cloud Run deploy, curl 200 check. `help-content-gate.yml`: on PRs touching help paths only: tsc + jest + dry-run scripts against a Postgres service. There is **no PR-time test run for the app as a whole** |
| Templates and guards | no issue template, no PR template, no CODEOWNERS, no dependabot, no branch protection. The shape is held by habit and the memory file, not by the repo |
| Session hooks | `.claude/settings.json` posts SessionStart / PreToolUse / PostToolUse / Stop / SessionEnd to an org hook server (`agents.adlabs.dev`). That is Gero infrastructure, not GitHub |

### The metric tie

- `docs/pm/metrics.md` is generated from `src/lib/pm/registry-data.ts` (about 60 ids like `gsc.gero.clicks.total`), each with unit, direction, baseline (frozen 2026-08-28), target, gate flag. `npm run pm:seed` upserts them into Postgres.
- Rule (`docs/pm/ticket-metric-citation.md`): every Q4 ticket cites at least one registered id in backticks anywhere in the body. The extractor keeps only ids the registry knows; an unregistered id counts as nothing.
- `pm-tickets` cron fetches the 3 repos by label hourly, mirrors them into `pm_ticket`, and records `pm.tickets_with_valid_metric`, `pm.tickets.closed_this_sprint`, open counts. Shown on `/pm` Delivery panel.
- `/pm/manual` for the 9 metrics no API gives; a value older than 2x its frequency greys out.
- `/pm/gates`: snapshot of every gate metric on the 1st with a written verdict (issue #57).
- Weekly digest (issue #58) shown on the panel only.

### Where Gero's flow is broken today (honest)

- `pm-tickets` has written nothing since 2026-10-01 (issue #101, open 26 days): token or scheduler. So the metric-citation grade has been dark for 5 weeks.
- `CURRENT_SPRINT` is hardcoded `'sprint-2'` in `src/lib/pm/collectors/tickets.ts`; it was never bumped, so "closed this sprint" has been wrong since 1 Oct.
- All five milestones are still open, including September.
- Two Q4 PM issues (#56, #84) have sat 54 and 69 days, blocked on Adam.
- Fast squash merges lost commits twice (`pr-squash-gotcha`, `local-main-ahead-gotcha` memories). Amir's speed is the gate and also the risk.
- 85 remote branches, none auto-deleted.

---

## 2. Side by side

| | Gero (gero-control-panel) | IoS (two JSON boards) |
|---|---|---|
| Where work lives | GitHub issues in 3 repos, PRs, `/pm` scoreboard, war-plan artifact | `plans/tickets.json` (87: 54 open, 33 done) + `plans/control-panel/tickets.json` (56: 8 open, 48 done); RM `/tickets` and `/board`; `TICKETS.md` history; 14 handover files |
| Who creates | Amir writes 37 of 39 issues (in session, Claude drafts); Adam 2 | Area chats propose in the handover "Ticket updates" block; the System chat merges; Amir says "y" |
| How it is prioritised | labels `priority: high/medium/low`, `size: S/M/L`, `sprint-N`, month milestone | `priority` P1-P3 and, since 11-05, `bucket` now/next/parked/routine + `who` + `label` + `next_step` + `chrome`; cap 3 now per area (7 now today: Socials 3, Release 2, Booking 1, Income 1) |
| How it closes | PR merged (Amir, median 0.4 h), issue closed by hand with the PR link; branch stays | status `done` in JSON + a done line in `TICKETS.md`, written by the System chat |
| Tie to a number | every Q4 issue cites a registry id; graded hourly (dead since Oct 1); gate snapshot monthly | none. `helps` is prose on all open tickets, no `metric` field (review B3). `plans/targets.json` holds 6 metrics nobody cites |
| Validation | none in the repo (no templates, no protection); the rule lives in a doc + a collector | `tickets.py` validator: required `id, section, priority, title, why, helps, status`; `why`/`helps` max 220; 24 + 31 tests. It does **not** know `area`, `area_no`, `bucket`, `who`, `label`, `next_step`, `chrome`; the 3-now cap is enforced by nothing; 10 open tickets have no bucket |
| CI | jest gates deploy on push to main; one path-gated PR check | 150 test files, run by hand / nightly ("TEST SUITE RED 9 nights", review B6); no gate before a commit |
| What Amir sees | GitHub issue/PR pages (phone app works), `/pm`, `/pm/gates`, weekly digest | 6 area chats with emoji titles, RM pages on the Mac, 20:00 socials digest, popups; nothing of the board on the phone except chat |
| History | GitHub keeps created/closed/updated per issue, who merged, when | `notes[]` with dates inside each ticket; no `updated` field, so staleness is invisible (review B3) |
| Cost in Amir's minutes | not measured. Visible: he authored 37 issues and merged 58 PRs in 5 months, each merge a click within the hour; monthly gate reading | not measured. Visible: a "y" per ticket in chat, reading handover summaries; the merge work is Claude's, not his |
| Repo | private GitHub, remote, ThirdEye707 | local git, 794 commits (756 with a Claude trailer), no remote; publication rule blocks any push until a history scrub; separate IoS account planned |

---

## 3. Take NOW (no GitHub remote needed)

All of this is JSON fields + tests + one script. It fixes review breaks B3 (no metric), B4a (hand merge) and B7 (nothing written back to goals).

1. **`metric` field on every open now/next ticket.** Values = keys of `plans/targets.json` (`ig_followers`, `ig_followback_pct`, `ig_reach_30d`, `sc_followers`, `spotify_monthly_active`, `tiktok_followers`) plus whatever Release/Booking/Income targets get added. A ticket that moves no number says `metric: []` on purpose with a one-line reason (Gero has no such escape, which is why `#103`-style upkeep issues carry no label). Test: `test_open_now_next_tickets_cite_a_known_metric`. Show the share on `/tickets` like Gero's `pm.tickets_with_valid_metric`, computed from the file, no cron.
2. **Issue shape = why + metric + done means.** Add `done_means` (2-4 checkbox lines, Gero's "Outcome") and `verify` (one command, URL or file to look at). Keep `why` and `helps` as they are (220 chars). Gero's `How to execute` and `Source` are optional; `notes[]` already does that job.
3. **`updated` date per ticket**, set by the merge. GitHub gives Gero this for free; the IoS board has nothing, so a parked ticket from September looks the same as one from yesterday.
4. **Gate = milestone.** `targets.json` already has `period 2026-11-01 to 2026-12-31`. Add `gate` to tickets (`2026-11-30` or `2026-12-31`) and group `/tickets` by gate, not only by section. On the 1st, write a `plans/gates/<date>.json` snapshot of targets + a verdict line (Gero's `/pm/gates`), by hand from the System chat; no collector.
5. **Validator and tests catch up with AREAS.md.** `tickets.py` must know `area`, `area_no`, `bucket`, `who`, `label`, `next_step`, `chrome`, `metric`, `gate`, `updated`; tests for: max 3 `now` per area across both boards, `area_no` unique across both boards, every open ticket has a bucket, `due` in the past on an open ticket is flagged, `who` in `amir|claude|auto`. These are the "CI checks" a local repo can have: `pytest tests/test_tickets.py tests/test_board.py` before any board commit.
6. **Priority overlap.** `priority` P1-P3 ("now / next / later") and `bucket` now/next/parked/routine say the same thing twice. Keep `bucket`, derive the P label from it for the old pages, or drop P1-P3 in one pass. One axis, like Gero's single `priority:` label.
7. **Labels: borrow `size: S/M/L` meaning.** IoS has `size` already; adopt Gero's text (S = hours, M = 1-2 days, L = 3-5 days) so it means the same in every area chat.
8. **Handover "Ticket updates" as a strict mini-template + a merge script.** Today 12 of 14 handovers carry a free-text block that the System chat reads by hand. Give the block one line shape (`<Area> <no> | field: value | note: ...` and `NEW <Area> | title | why | helps | metric | bucket | who | size`), and a `plans/merge_handover_tickets.py --dry-run` that prints the diff before the System chat applies it. That is Gero's issue template, without GitHub.
9. **Report shape from Gero's PR bodies**: What / Why / Verification / Not in this PR. Use it as the handover result block per ticket. "Not in this PR" is the scope-discipline rule written down.
10. **Commit subject = ticket label**, as proposed in `github-setup.md` (`Release 2: ...`, `upkeep: ...`). Gero's `feat(scope): subject (#N)` is the same idea; IoS subjects today mix `docs:`, `board:`, `SC:`, `Imagine:`, `Merge:`. One pass on the convention, then `git log --grep "Release 2"` becomes the ticket history.
11. **Delivery numbers into the digest**: open per area, now per area, tickets with a metric, closed this gate, open past due. Three lines in the 20:00 digest or the score board. This is Gero's Delivery panel, local.

Not needed: a database, a cron, a registry collector. `targets.json` is the registry.

---

## 4. Take ONCE the IoS GitHub account exists

Two different things hide here, and the current backup design keeps them apart:

- **The backup repo** (`github-setup.md`): a no-history snapshot copy, pushed with a deploy key, secrets and DMs never uploaded. It is a copy, not the working repo. Issues on it would be a board next to a mirror of the code, which is fine; PRs on it make no sense (nothing is developed there).
- **A real remote for the working repo** needs the history scrub first (CLAUDE.md Repo Publication Rule). Only then can a PR flow exist.

Options for the board, in order:

| Option | What it gives | Cost | Verdict |
|---|---|---|---|
| A. Keep JSON, no issues | nothing changes; backup repo holds the files | 0 | default until the scrub |
| B. JSON stays the source, one-way mirror to GitHub Issues (script: open tickets -> issues with `area` labels, milestones = gates, close on done) | a phone view (GitHub app), free history, notifications; Amir reads, never edits there | one script, token for the IoS account only, 1 run per merge | the one to try first, once the account exists; a mirror that drifts is worse than none, so the script must be the only writer and must be run by the System chat merge |
| C. Issues become the board, JSON retired | Gero's model; RM reads issues via API | every area chat needs the token; RM pages depend on the network; the ThirdEye707 `gh` login on this Mac must never be used (memory `github-account-separation`); two accounts on one `gh` is a daily foot-gun | no, not with chats as the workplace |

PR flow with auto-fix for RM 2.0 (after the scrub, working repo pushed):

- Copy the deploy.yml shape without the deploy: a `test.yml` on `pull_request` running `pytest` (GitHub Actions is free for private repos within 2,000 minutes a month; the IoS suite is 150 files, time it first). Gero only tests on push to main; do it on the PR, which is where auto-fix bites.
- Sessions bind the PR, CI red triggers the fix, Amir merges from the phone. That is the part of Gero's setup that is worth it for code, and only for code (`release_manager/`, `stats/`, `scene_intelligence/` tooling). Tickets never go through PRs.
- Gero's two gotchas become rules from day one: PR frozen once opened (new work = new PR), branch from `origin/main` in a worktree, verify `origin/main` after merge before saying "live", turn on "automatically delete head branches".

What a local-only repo can still use today (no remote):

- worktrees per side chat (already in use), a branch per ticket named by the label (`release-2-cover-export`), `git merge --squash` into main as the "PR", `pytest` by hand before the merge (no hook without Amir's yes), a tag per gate date (`gate-2026-12-01`) so a gate snapshot is also a git point, and `git log --grep` as ticket history.

---

## 5. Verdict: move the IoS tickets to GitHub issues?

**No for now; partly later; the shape yes, today.**

Why no now:

- No remote exists and none is allowed until the history scrub. A board that lives on GitHub before the code does is a third place for goals (review B1 says there are already four).
- Amir works from chats and his phone. The chats cannot write to GitHub without a token in every chat, and the IoS account must stay apart from the `gh` login on this Mac. One wrong `gh` call pushes IoS work into ThirdEye707.
- Gero shows the tie to a number is a collector, and the collector died on 1 Oct unnoticed for weeks while the sprint constant stayed on `sprint-2`. The tie is only as good as the thing that reads it. On IoS, a `metric` field checked by a test is read every time the suite runs and needs no token, no cron, no server.
- Gero's issue count is batches (20 in one week of November), closed by hand after merge, milestones never closed. The repo keeps the dates, which is the real gain, and `updated` on the JSON gets most of it.

Why partly later: the phone. GitHub's app is a good read-only view of a board; RM pages are Mac-only. Option B (one-way mirror from JSON, written only by the System merge) gives that without moving the source of truth. Decide after the backup repo exists and the mirror script has run a month without drift.

Why the shape yes: Why / metric / done means / verify, a dated gate per ticket, `updated`, size meanings, the PR-body report block, one priority axis, and tests as the gate. All of it is a JSON change plus tests, inside the system-loop fixlist.

---

## 6. Do not take

- The org hook server (`agents.adlabs.dev` SessionStart/PreToolUse/... hooks). Gero infrastructure; IoS has 0 hooks and a rule to ask first.
- Cloud Run deploy, Docker, Postgres registry, hourly collectors, Scheduler jobs. IoS has no service to deploy; `targets.json` + snapshots cover the registry.
- `sprint-1..8` labels. Dated labels that nobody rotates (CURRENT_SPRINT stuck on sprint-2). Gates by date on the ticket do the same without a label set per quarter.
- Splitting tickets across repos by product. IoS has two boards already; the review says that is one too many, not one too few.
- GitHub default labels (`good first issue`, `help wanted`, `wontfix`...): unused at Gero, noise here.
- GitHub Projects: not used at Gero (the token lacks the scope), nothing to learn from.
- Big-batch issue creation (71 at once, 20 in a week). IoS tickets come from handovers one at a time; keep that.
- "Merge within the hour" as a habit. It lost commits twice at Gero. The auto-fix flow only works if the PR is frozen once opened.
- Issue closing by hand with a PR link as the only trace. On IoS the done line in `TICKETS.md` + `updated` + the commit label is the trace; keep it in the files.
- The war plan as a claude.ai artifact with a task board inside it. Goals stay in `targets.json` (review B1/B7), the artifact page is for the outreach ticks only.
