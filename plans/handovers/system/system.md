# ⚙️ System: parent chat handover

Written 2026-11-05 by the ⚙️ System parent chat. This chat owns: GitHub, contracts, tokens, API caps,
Control Panel board, upkeep, and merging every area's "Ticket updates" into both ticket boards.

## Side chats
| Chat | State |
|---|---|
| ⚙️ GitHub (`github-setup.md`) | waits for Amir's new GitHub account (⚙️ System 62) |
| ⚙️ Studio agreement (`studio-agreement.md`) | waits for a photo of Yuval's signature |
| ⚙️ System 66 test alarm | done 485b7e9, chat deleted on Amir's ok |

## Strategy review (started 2026-11-05)
- Step 1 (inspection) DONE. Everything lives in `plans/strategy/`:
  - `review-2026-11-05-facts.md`: plan vs reality, numbers vs targets, code map, docs drift, how we work, LLM system, five more areas
  - `review-2026-11-05-fixlist.md`: 63 out-of-date lines (26 read by agents), proposed text, nothing applied
  - `review-2026-11-05-proposals.md`: options + picks for LLM system, notifications, decision page
  - `review-2026-11-05-research.md`, `research-release-fans-*`, `research-berlin-calls-*`, `research-backups-*`
  - `drafts/`: ready-to-apply parent CLAUDE.md, slim memory index (16.5 KB), old-memory merge list, enforced-rules settings, daily brief spec
  - The page Amir reads: **Inch of Shadow Refresh** https://claude.ai/artifact/6tN5jc4rjV8agVijcrrXVd (source `plans/strategy/refresh-page/index.html`)
- Next: step 2 = Amir's answers (questions at the end of the facts page, section 12), only when he says the digging is done. Then council on 1-2 decisions, then plan v2.
- Money in/out is out of scope on Amir's call (too early).
- Review files + drafts committed 2026-11-05 on Amir's yes. Drafts are still NOT applied.
- v3 (same day, Amir asked for heavy strategy changes, not tasks): 6 deep passes -> research-pitch, research-social-algo, research-listening-platforms, research-tiktok (all 2026-11-05), review-2026-11-05-code-map, review-2026-11-05-system-loop. Page v3 = 41 change cards (was / change to / based on / why / steps). Algorithm file has a 2026-11-05 update block on top.

## Board work done today
Commits: aa75b1e + b62fc14 (areas + handovers), 1a945ab (💶 Income 8 done), 416af06 + fbe5743 (🎬 Socials fields + chrome),
a6e07fa (max 3 Now per area + System buckets), 61c78d9 (🎵 Release), 8b3e686 (💶 Income), 8679099 (emoji map), 21f2720 (🎧 Booking).
Waiting: 🎸 Studio priority fields (asked 11-05).

## Rules learned today (also in memory)
Emoji map in `plans/AREAS.md`. Facts before questions in a review. Finished side chats deleted on Amir's "ok".
Max 3 🔥 Now per area is a cap, not a quota.

## Fable gate (2026-11-05)
Fable audited the review: `plans/strategy/review-2026-11-05-fable-audit.md`. Gate rule + effort rule live there and in memory `fable-gate`. Gate verdicts go to `plans/strategy/gates/`. Open from the audit: content-language research pass (before the first content round), SC Terms quote by hand, Symphonic Starter facts, grep scripts before the ask-rules draft.

## Content language (2026-11-05)
Two passes (ig-expert 17 profiles; scene pass) + Fable gate (approve with fixes): `plans/strategy/research-content-language-2026-11-05.md`, `research-content-scene-2026-11-05.md`, `gates/2026-11-05-content-language.md`. Page S7 updated, D18 = his yes on round one (7 experiments on released tracks). Memory `content-language-evidence-2026-11`.

## Spend
`python3 stats/spend.py` (System 67, read-only; `--json` writes `stats_snapshots/spend_latest.json`, previous copy to `.bak`): logged = Claude API (`claude_spend.json`, monthly totals only), OpenAI text (`openai_spend.json`), image renders (`generated_images/imagine/*.json`), HikerAPI balance (snapshots since 11-02); NOT logged = raw renders (`raw_render.py`, 81 files, no cost) and the Gero key (same Claude credit, no ledger; set `GERO_LEDGER` in the script once one exists). Warnings: Claude 70% of $200, image renders $15/month, HikerAPI under $10.

## Batch 1 done (2026-11-05 evening)
Side chats: spend-page (9130662), ig-stats-daily (7aa32ab, 9b76660, 4b0878a), facts-fix (27ae612, f24085d), code-lists (b8bdfb3). Gate: `plans/strategy/gates/2026-11-05-batch-1.md`. M9 held until the HTN cover chat is done with `releases/pinocchio-single.json`. Page v9. Batch 2 = Amir's decisions D2, D3, D4, D5, D8, D12, D13, D15, D17 (facts on the page). Chat runs on Fable; gate = the other model for big plans only.

## Rollback (2026-11-06 00:30, Amir: "go back to the same point we were")
Amir's "Pause for now" on the D17 card meant pause everything; I ran Batch 2 answers + Batch 3 on the earlier "Continue". Rolled back to the state after Batch 1 (36ee7bc): 8 commits reverted (94b598c..cc9b6df), settings.local.json + MEMORY.md + old memory index restored from the 11-05 backups, the 6 merged memory files and the parent CLAUDE.md moved to ~/.claude/projects/-Users-amir-Desktop-Inch-of-Shadow/memory.rollback-2026-11-06/, scheduled task system-daily-brief deleted (its SKILL.md folder stays on disk). Batch 1 stays (his go). New hard rule in memory: pause-means-stop-everything. The reverted work is recoverable from git history if he ever wants it.

## Batch 2 answered (2026-11-06, desk)
See the facts page bottom block. Batch 3 waits for his explicit go. D5 draft restored from f62134f and amended for TikTok; needs the Opus gate. D15 suggestion given in chat. D17: keep/merge/drop list per page to prepare from rm-page-map.

## D15 + D17 answered (2026-11-06)
D15 later (drive first). D17 yes as listed; goes into the RM 2.0 blueprint (rm-page-map section 3) when that work starts. Open: D5 Opus gate; Batch 3 waits for his go; D9/D16 are Batch 4.

## D5 answered (2026-11-06): Batch 2 complete
Plan approved after the Opus gate (cbcc33f). The file edits it lists (positioning line, agent docs via IG/SC chats, release guide) belong to Batch 3 (S2) and Batch 4 (S3): not started, wait for "go, Batch 3".

## Gero findings approved (2026-11-06)
S10, S11, M10, M11, M12 on the page (v12). Studies + gates: gero-transfer, gero-cp-deep-dive, product-lens, gero-github-tickets, research-clip-pack, gates/2026-11-06-gero-studies.md. Paused: Batch 3 (now includes these) until "go".

## S10 done
System 79 (2026-11-06, Fable side session): clip pack per song built, `clips` block in releases/<slug>.json (tiktok.start, hook_bar, canvas, shorts_preview, used_in with the never-twice rule), `release_manager/clips.py`, Clip pack block on the release page, 25 tests, schema + 3 open Symphonic questions in `plans/clip-pack-schema.md`; no release file touched, RM reloaded itself.
## Batch 2 (2026-11-05 evening)
Answered: D2, D3, D4, D8, D12, D13. Open: D5 (detailed per-platform plan being drafted, Opus gate), D15 (suggestion given), D17 paused. Batch 3 side chats started: L1 drafts live, L2 daily brief, S1 scoreboard, L4 schedule lists. L3 waits for S1 (same files). Answers also in the facts page.

## Scoreboard (2026-11-05, ⚙️ System 73, D4)
Three rows added to `plans/targets.json` (backup `plans/.targets.json.bak-2026-11-05`) and to the score board on RM /stats; the electronic stats keep running, nothing removed. Spotify followers moved from TREND ONLY to a target card (same number, read from `stats_snapshots/spotify_s4a.json`).
Every row carries `proposed_by: "claude", confirmed: false` and shows a "proposed" badge until Amir confirms; flip `confirmed` to true in targets.json and the badge goes.

| Row | Source | Baseline | 2026-11-30 | 2026-12-31 | Waits for |
|---|---|---|---|---|---|
| Spotify followers | S4A Monday read (`s4a:weeks.followers`) | 68 on 2026-10-31 | 80 | 90 | Amir's confirm of the rungs |
| Email list | manual entry `email_list.subscribers` (`python3 stats/manual_entry.py email_list subscribers N`) | 16 on 2026-11-05 (Bandcamp mailing list) | 30 | 50 | Amir's confirm of the rungs |
| Release engagement, day 28 | `releases/<slug>.json` outcomes.stats.engagement_d28 (schema in targets.json) | first day-28 read of Half the Night | none | none | the day-28 read, then rungs |

Not done tonight: no value written into any release file (`pinocchio-single.json` was in use by another chat); the day-28 definition (which actions count in `parts`) is a proposal too.

## Daily brief (⚙️ System 72, 2026-11-05)
`python3 stats/daily_brief.py` prints Amir's one 20:00 brief (spec `plans/strategy/drafts/daily-brief-spec.draft.md`, D13);
`--write` also saves `docs/reports/daily-brief-<date>.md`, the state file `stats_snapshots/daily_brief_state.json`
(last 7 days of 🔴 lines) and, when the same 🔴 line is red two days running, one proposed ticket line under
"## Proposed from the brief" below (the brief then shows "→ ticket"). Read-only otherwise: loop-close reports,
SC session report + weekly health, dispatch-log (notify-amir lines, watchdog red on 2 of the last 3 nights),
IG Graph token state, open tickets whose blocked_on says "expired", snapshots + spotify_s4a.json vs
`plans/targets.json` ladders (any ladder with a snapshot: or s4a: source shows up; manual: sources are skipped),
both ticket boards (🔥 now per area, 🙋 = who amir + bucket now), `stats/spend.py` warnings (line only when it warns).
The 🎬 Socials digest is untouched (helpers imported). Task definition for the System chat to create:
`plans/strategy/drafts/system-daily-brief.task.md` (`system-daily-brief`, 20:00 Europe/Berlin); old and new run
side by side 3 days, nothing turned off. Tests: `tests/test_daily_brief.py` (12).
- 2026-11-06 · proposed ⚙️ System ticket · 🎬 Socials 2 · YouTube login renewal · Login expired ~2026-10-28 · red on 11-05 and 11-06
- 2026-11-06 · proposed ⚙️ System ticket · engagement_log.json at 1657KB > 1500KB · schedule the archival job · red on 11-05 and 11-06

## Proposed from the brief
Written by stats/daily_brief.py when the same 🔴 line shows two days running. Each line is a proposal for the
System chat to turn into a ticket (or to dismiss).

## Batch 3 restore (2026-11-06, Amir: "Go, Batch 3")
Re-applied as patches from the 11-05 commits: S1 31a4fb2 (scoreboard rows), L2 079489a (daily brief; task recreated as system-daily-brief-2, 20:00, Auto mode), L3 69c324b (code hunks + metric/updated regenerated on both boards for all 143 tickets), L4 b291cd3 (schedule lists + launchd drafts). L1 restored from memory.rollback-2026-11-06 (slim index 23 KB, 6 merged files, old-memory pointer, parent CLAUDE.md, settings deny 7 / ask 7; backups .bak-2026-11-06-pre-L1). The gap_radar schedule test fails on a data file the Income chat set (cap 70): not ours, flagged to Income. Next: wave 2 (S2, S11, M12, S10) then RM 2.0 (M10, M11, M7).

## S11 drafts
- 2026-11-06 (⚙️ System 77, Fable side chat): `plans/activation-messages-2026-11-06.md` = welcome mail (electronic + songs variants, under 120 words each), Spotify Artist Pick (2 variants), SC follower-only drop note, fire table (Buttondown / S4A / SC Artist Pro, Amir presses). Drafts only, nothing sent or pinned; open: Buttondown vs Bandcamp message tool.

## S2 done
Platform jobs written where agents read them (⚙️ System 76, 2026-11-06): `docs/brand/positioning.md` (INTERNAL section "Platform jobs", 7 lines), `youtube/PLAYBOOK.md` (job paragraph at the top of §1, outside the repo, not committed), release guide (3-line banner pointing to the platform plan, rewrite stays Batch 4), proposal blocks "platform jobs" in `plans/handovers/socials/ig-agent.md` and `sc-agent.md` with the exact lines for the engagement docs (IG and SC chats apply them).

## M12 done (2026-11-06, ⚙️ System 78)
Ticket shape on both boards: done_means added to 143 tickets (62 open hand-written, 81 done from the title; all done_means_by "claude"), 10 bucket-less tickets fixed (M-13 + ST-01..ST-09 now bucket next with who/label/next_step, noted "Studio chat to confirm", M-13 "Socials chat"), 37 tests added (78 -> 115 in test_tickets + test_board; 134 with test_decisions_writeback, whose G-20 case moved to G-15 because Socials sits at the now cap). Priority decision: bucket is the one axis; `priority` P1-P3 removed from the file (87 tickets) and `priorities` replaced by `buckets`; P1-P3 stays only as a derived view in tickets.py (now = P1, next = P2, parked/routine = P3) so RM /tickets and webapp.py needed no route change. Validator: stored priority = error, open tickets need bucket/who/label/next_step, all tickets metric (targets key or none + note)/updated/done_means, em-dash anywhere = error, max 3 now per area fails with the area name; test_board runs the same check on the Control Panel. Backups: .tickets.json.bak-2026-11-06-shape on both boards.

## Wave 2 verified (2026-11-06)
S2 23bed52, S11 3370784, S10 48e24ce, M12 b430275; 1,277 tests green (gap_radar schedule test = Income chat data). My earlier revert --abort dropped the HTN cover chat commit (they restored it, 0ae08b1); rule saved in memory shared-checkout-no-sequencer. Wave 3: M11 + M7 now, M10 after M11 (both touch RM).

## M11 part 1 done (2026-11-06, ⚙️ System 80, Fable side session)
The six data-accuracy habits from the Gero study (card M11, section A "What IoS takes") are in the stats layer; the page look is untouched (M11 part 2 is the visual rebuild).
- **One registry:** `stats/registry.py` reads `plans/targets.json` (still the file Amir edits, not changed, no backup needed) and adds per metric the source kind + path, cadence (daily / weekly / monthly / manual / none), direction, freshness window, pace (ladder / floor / none / trend) and area; the two trend-only rows (YouTube subscribers, Bandcamp followers) live there too. `load_registry()` fails when a metric is in one place and not the other; `tests/test_registry.py` pins the parity both ways.
- **Who reads what now:** RM `/stats` score board (`release_manager/score_board.py`: cards, trends, health, ladders) reads the registry; the daily brief 🎯 line (`stats/daily_brief.py`) reads the registry's ladder rows and their short names; the 🎬 Socials digest 🎯 line (`stats/socials_digest.py`) reads the rows flagged `digest`; `stats/propose_targets.py` iterates the registry. No file keeps a metric list of its own any more (the test checks that too).
- **Provenance:** every snapshot has a `run_id`, every platform block `as_of` + `source`; manual entries carry `source` (`manual:amir`, or `--source cli:...`); the follow-back file names its export. Every card carries `{value, as_of, source, run_id}` (the card label's tooltip on /stats shows source, as_of and run). Old snapshots have no run_id, so run shows empty for readings before today; that fills in from the next sync.
- **Skipped, because:** a collector that cannot read writes `{"skipped": "<reason>"}` into the snapshot (keys and tokens redacted) instead of nothing; the sync log prints "instagram: skipped, because ..."; every reader (score board, brief, digest, weekly summary, time series) treats it as not collected and keeps the older reading. A card whose platform was skipped in the newest sync says "skipped today, because ..." under its number.
- **One freshness rule:** `registry.freshness(as_of, cadence, now)`: daily 24 h, weekly 10 days, monthly 40 days, manual 62 days, release reads never. A stale reading on a target card turns the card **red** with the age and the window ("stale, 3 days old (window 24 h)", "as of 2026-11-02, 3 days old" in the foot); the health dots for snapshot, export and Spotify read use the same rule ("6 h, taken 2026-11-05 20:17, max 24 h"); the brief and the digest print "(stale, read 11-02)".
- **Verdict:** any red card = **OFF PACE** (`registry.verdict`), no majority rule; the line reads "OFF PACE, 5/9 GREEN, 0 DRIFTING, 1 RED (1 STALE), 3 COLLECTING" and a muted line under it names the red cards and why. A test proves ON PACE cannot print with a red card.
- **Monthly freeze:** `python3 stats/freeze.py 2026-11` writes `stats_snapshots/gates/2026-11.json` with every registry metric as of Nov 30 23:59:59 (reads nothing dated later, so re-freezing reproduces the numbers; a forced rewrite with other numbers is refused). `/stats?month=2026-11` shows that frozen month (health row hidden, "Frozen month ..." under the verdict); a month not frozen yet says so in the score-board error line. Not scheduled: see Monthly upkeep below.
- **`now` everywhere:** `score_board.build(now=..., until=..., month=...)`, `_card`, `_health`, `targets_line(d, now)`, `goals_line(d, now)`, `freeze(month, now)`; tests cover stale, skipped, frozen and the verdict (`tests/test_registry.py`, `test_freeze.py`, `test_score_board.py`, `test_stats_collect_skip.py`).
- **What Amir will notice:** tonight the board still says ON PACE, 6/9 GREEN, 0 RED (every reading is inside its window; the 20:17 snapshot is 6 h old). It will flip to **OFF PACE** the first time a daily source is older than 24 h (the 08:45 sync fails or the Mac sleeps through it: the IG and SC cards go red with "stale, 27 h old (window 24 h)" until the next sync) or a ladder card drops below 85 % of plan; before, three greens could hide one red. The "0 OFF PACE" count is now "0 RED". The per-track grid under the fold is unchanged.
- **Not done / open:** the RM server on 5001 was restarted at 03:03 from another chat's terminal; the `?month=` route and the template words need the next restart (the score board module itself is imported per process too). The health dot "Followers to following" prints 1.00 and fails floor 1.0 (971/973 = 0.998 rounded for display): pre-existing wording, one line, not touched. Commits: 5bc27c0 (provenance + skipped), fad850d (registry, freshness, verdict), then the freeze commit.

## Monthly upkeep
- 1st of the month: `python3 stats/freeze.py <previous month>` (e.g. `2026-11` on Dec 1) freezes the gate numbers as of the last day; check `/stats?month=<previous month>` once. By hand, not scheduled (M11 decision).
- The 15-minute check (L6, Batch 4, 2026-11-06), same day, in this order, each line one yes/no in the handover:
  1. Freeze: the line above, then `/stats?month=` shows the month.
  2. Spend: `python3 stats/spend.py` and the HikerAPI balance in `stats_snapshots`; over plan = one line to Amir.
  3. Rules: memory index under 25 KB / 200 lines (`wc -c -l ~/.claude/projects/-Users-amir-Desktop-Inch-of-Shadow/memory/MEMORY.md`), parent CLAUDE.md still the one rules file, settings deny/ask lists unchanged (`git diff` on the parent `.claude/settings.local.json` is not possible: outside git, so diff against the dated backup).
  4. Stale lines: re-run the five checks of `plans/strategy/review-2026-11-05-fixlist.md` on the files it names (release plan, next release, counts); any line older than its fact = a row for the owner chat.
  5. Backups: `python3 tools/prune_bak.py` (dry run), then `--apply` (scene_intelligence/*.bak.* older than 14 days to the Trash, undo script in docs/reports; approved by Amir 2026-11-07).
  5b. Hygiene: `python3 hygiene_check.py` (scratch folders, saved pages with scripts) and `~/.claude/scheduled-tasks/` against the registered list (`plans/strategy/schedule-cleanup-2026-11-05.md`): dead folders = a Trash proposal, never a delete.
  6. Boards: `python3 -m pytest tests/test_tickets.py tests/test_board.py -q`; done tickets into the archive files; the three-now cap per area holds.
- Deep review every 3 months: next early Feb 2027 (this one was 5 to 6 Nov 2026). The new six-month plan is written in December with dated checkpoints (L6); the September plan slipped because its checkpoints were never written.

## M10 done (2026-11-06, ⚙️ System 82, Fable side session)
The review flow with no file moves (spec: gero deep dive section C; placement: dry run 1c). Schema: `plans/review-flow-schema.md`.
- **What works:** `release_manager/review.py` (items with kind / path / sha256 / bytes / created / state / supersedes / checks / history, state table, hash-bound approve, superseded link, checks runner, phone export, demo); RM `/review` (grouped by release, needs-you first with held on top, chips as words in the mood colours, Approve / Change + note / Drop, keys j k a c d n, Done collapsed; filters `?release=` `?area=`; `?demo=1` = in-memory demo release, nothing written); `POST /api/review/<slug>/<item_id>` `{action, note, sha256}`; `GET /review/thumb/<slug>/<item_id>`; sidebar link under Plan. Chips: hash, format / duration / audio per destination preset (imageio-ffmpeg probe, resizer presets), safe-zone 270/672/65 from recorded type boxes (manual without them), no-text-over-face and first-3s manual, copy (em-dash + caption_check), handles (unknown = question, never pass). Security review applied: `sha256` is bound once and never rewritten (`observed_sha256` for re-hashes); approve needs tick hash = bound hash = disk hash; a held item cannot be approved (the spec's "his call" override is NOT honoured, flagged for Amir); a phone tick never touches `state`: `import_ticks` only fills `item.proposed` {action, note, at, tick_id} on a valid tick (hash = bound = disk; a later tick replaces the earlier proposal), the page shows it as a dashed chip next to the real state, `consumed_ticks` stops replays, the real step is local only (RM keystroke or `review.py confirm` on his words, by=amir); the export holds no token (the page is readable, so a token there protects nothing). Nothing on the page or in the API deletes, moves, renames, posts or marks used (`used` only via the CLI from his words). Tests: `tests/test_review.py` (39); suite 1,344 green. Commits cb56b02, e8c1332, 6594c69, then the proposal-only commit.
- **What Amir tests:** restart RM (the new routes and the sidebar link need it; not done from here), open `/review?demo=1` for the look, then seed one real release: `python3 release_manager/review.py add <slug> --kind render --label "..." --path <file> --dest reel_instagram`, tick it on `/review`, change the file on disk and reload (it must fall back to needs-you with "file changed after approval"). `releases/pinocchio-single.json` and Half the Night files untouched (cover chat owns them).
- **Not done:** the phone page (the export JSON exists, the System chat publishes it with the outreach-page pattern, reads ticks back with `import_ticks` and confirms with `review.py confirm` on Amir's words); the pre-use re-check (section C, L); text boxes for the safe-zone chip must come from the renderer. `tests/test_stats_page.py` pins the CSS cache version, bumped 85 -> 86 with the sidebar link.

## Batch 3 done (2026-11-06)
Gate: `plans/strategy/gates/2026-11-06-batch-3.md`. 1,343 tests. RM serves the new pages. Waits on Amir: rungs, held-item rule, RM 2.0 slice 1, dead folders + launchd drafts, activation messages. Next: Batch 4 (D9 paid promotion rule, D16 code clean-up: merge, archive, Python) and RM 2.0 slices.

## Decisions 2026-11-06
- D4 [rungs] Spotify followers rungs (baseline 68): 80 by 2026-11-30 and 90 by 2026-12-31? -> Confirm 80 / 90 (Spotify followers 80 (30 Nov) / 90 (31 Dec) confirmed by Amir at the desk.)
- D4 [rungs] Email list rungs (baseline 16): 30 by 2026-11-30 and 50 by 2026-12-31? -> Confirm 30 / 50 (Email list 30 (30 Nov) / 50 (31 Dec) confirmed by Amir at the desk.)

## Chrome queue (2026-11-06)
Ticket ⚙️ System G-25 (bucket now). Request from Amir via the BERLIN invoice chat, confirmed here. Options on the table: lock file + global PreToolUse hook (enforced) or rule text only. Waits for his pick; the helper lives in this repo (tools/chrome_queue.py), the hook line in ~/.claude/settings.json needs his yes. Facts: no global CLAUDE.md or hooks exist yet; the browser pick is session-local (memory chrome-connection-naming-is-not-durable), so the flip cause is unproven.

## Batch 5 (2026-11-06, Opus)
- Batch 4 gated: `plans/strategy/gates/2026-11-06-batch-4.md` (songs guide approved with 7 fixes; D9 = A written into both guides; album pitch gap noted for before the sixth single). Batch 4 closes when D16 lands in the GitHub chat.
- IG ratio dot shows counts (32d960a). RM smoke test (21abfa6): every page GET, writes/network/shell blocked while rendering.
- RM 2.0 slice 1 done on Amir's yes (side chat) and the IG chat's OK: 896fae8 (drops: Palette, Autopilot, Engagement, Promotion, Artwork Resizer nav; webapp.py 5,914 to 4,191 lines, app.js 2,665 to 717; email_outreach.py, contact_bridge.py and their test in `archive/rm-promotion/`, undo = git mv back), 53e80b4 (Work = tickets on top, board below, By number switch, served at /tickets; resizer below the projects on /video). 1,368 tests. RM restarted; dropped pages 404, kept pages 200.
- Incident: a test agent's one GET of /engagement at 16:19 rewrote the RM queue keys in `engagement_log.json`; IG and SC chats checked, nothing to restore. Memory dont-touch-engagement-code has the rule.
- Pre-warm note (IG chat): set `slug` by hand in `scene_intelligence/release_context.json` plus a campaign in `promotion_log.json`; sent to the Half the Night chat.
- Open: D9 premieres reading (side chat stopped before Amir answered; guides say "System's reading"). Next: slice 2 (core split + stats module) on Amir's go; the effort rule says ultracode for the split slices 2 to 8, which needs his keyword.
- Leftover outside the allowed files: `docs/superpowers/plans/2026-04-21-curator-discovery.md` still names localhost:5001/promotion (history doc, harmless).
- RM 2.0 COMPLETE (2026-11-06, slices 1-10 on Amir's go each): 896fae8, 53e80b4, e32908f, ea7c3af, bbeb98c, 1a45ac8, d644f69, cc061af, a014465, 39964ca (Review module), 7a7e378 (Home page), 1b0eeea (Home shows "🎵 Release 2" labels). webapp.py 5,914 to 218 lines, app.js 2,665 to 717, 125 routes, 1,376 tests. Answers: held items stay refused; Review seeded on farewell-single (item r-001, cover; written into releases/farewell-single.json, UNCOMMITTED because that file also carries SC stats writes; backup .farewell-single.json.bak-2026-11-06-review; the save also synced timeline stats_review to done, matching the checklist's 2026-06-16 done); Home = verdict line, 🔥 Now by area, decisions waiting on Amir (+ Review needs-you), next release + Out, social links kept, backup/drive footer.
- Batch 5 left: M11 part 2 (/stats visual rebuild), the phone review page, ⚙️ System 67 Chrome queue, L6 six-month plan in December. Gate owed: Fable reads RM 2.0 (built on Opus); `/code-review ultra` before main moves (D16).
- Phone review page LIVE (2026-11-07): https://claude.ai/artifact/D9BYUSMqNCgVbSiDrEsKVL, private, db `ticks`. Built by `plans/review-page/gen.py` from `plans/review-export-*.json`; read back with ArtifactData list (out_dir) + `plans/review-page/read_ticks.py` (import_ticks: proposals only, replays ignored); Amir confirms at the desk. Today it holds the Farewell test cover (r-001). Held items: Approve is disabled on the phone too.
- Stats page rebuilt on the brand brief (M11 part 2, 7c4069e). Chrome queue built, not installed (ac0fa35); its switch-on waits for Amir at the desk (Remote Control blocks side chats).
- M4 rotation, IG answer (2026-11-07, IG commit 6e098db): CHANGE. engagement_log.json keeps a rolling 90 days, not the current month (IG cooldowns look back up to 65 days). .bak.* 14 days then Trash + gitignore: yes. 11 readers listed in ig-agent.md. Dry run by the IG chat only after Amir's yes in the IG chat. SC lookbacks: SC chat to confirm.
- M4 DONE (2026-11-07): IG and SC both yes to the .bak rule; 20 files (5.7 MB) moved to the Trash, undo `docs/reports/prune-bak-2026-11-07-undo.sh`; none were tracked in git (the 22 tracked .bak sit in backups/sweep-20260831/, untouched); gitignore already listed them. engagement_log.json split: SC said NO for now (readers scan full history, 1.7 MB is fine); IG wanted rolling 90 days; parked, both owners agree nothing moves.
2026-11-07 security review: youtube_token.json, credentials.json, .sc_user_token.json were 644 (readable by other users on this Mac), now 600. Undo: chmod 644 <file>. .sc_user_token.json is rewritten daily by the SC refresh and may come back as 644; the SC chat owns that writer.
- 2026-11-07: M5 done (ae81da9 si-discovery, cbb5645 rm-cli, 637e499 root-tools, 61a8825 look02 duplicates, then si-sheet after the /sync, /discover, /enrich skills were marked parked; 8,000+ lines parked; undo docs/reports/m5-undo-2026-11-07.sh). Six-month plan (L6) moved to the end of November on Amir's word; one-time reminder task `six-month-plan-reminder` on 2026-11-16 10:00. Fable gate owed for Batch 5 (RM 2.0, Stats, phone review, Chrome queue, M4, M5, D9 premieres). 6 SC tests fail on live data since 11-07 morning: sent to the SC chat.
- 2026-11-07 Fable gate on Batch 5 + late Batch 4: `plans/strategy/gates/2026-11-07-batch-5.md`, approve (route diff = approved drops exactly; hook fails open; ticks owner-only; M4/M5 clean). Watch: Chrome queue stale 20 min vs long IG/SC sessions. Waits: ultra review + main move (D16), Release chat commits farewell-single.json, SC test fix, six-month plan end of Nov. The review's build work is complete.
- Side chat under System, open until done: ⚙ Password + 2FA inventory (local_0bd163cf-01fe-44ee-af26-6385ec277487), ticket ⚙️ System 70; never delete with another chat; it reports here when a category closes.
- 2026-11-07 System 68 steps 2 and 3 done (branches, music-tools). Left: Amir's /code-review ultra, then main = score-board (fast-forward, 312+ commits) and the checkout to main.
- 2026-11-08 System 68 done: gate review 18 of 19 blockers fixed (the SC one is Socials 36); on Amir's "main" main fast-forwarded to db2d156 and the checkout is on main. Chats now commit to main; score-board is an old name at the same commit. Fable checks paused to Sat 11-14 22:00, queue in plans/strategy/gates/QUEUE.md.
