# Strategy review, step 1: plan vs reality (2026-11-05, v2 after the deep pass)

Facts only, no proposals. Every line names its source. Steps 2-4 (Amir's answers, council on
1-2 decisions, plan v2) come after this page.

**What was read for this page.** In full: all 6 docs in `plans/strategy/`, `master-plan.md`,
`project-brief.md`, `release-lessons.md`, the IG engagement strategy (outline + goals),
`docs/brand/positioning.md`, `README.md`, the Mosseri guide outline, all 8 area handovers, both
ticket boards, `plans/targets.json`, the release files, the stats snapshots and S4A reads.
Header + goal/decision grep (helper, checked against files where it matters): the other ~70
`plans/*.md` and the `docs/**` files. Code map (helper, checked): the stats collectors, schedules,
targets and Release Manager pages.

## 1. The six-month plan (`next-six-months.md`, 09-13), item by item

| Plan item (date in plan) | Reality on 2026-11-05 | Source |
|---|---|---|
| Control panel, 14-20 Sep | Done: type, colour, motion, face rules, positioning v2, voice v2, formats. Open: logo (⚙️ System 16), TikTok formats (⚙️ System 24) | `plans/control-panel/tickets.json` |
| Reference artists, 3-5 sonic + 2-3 visual | No decided list in any file. Positioning names a neighbourhood (R. Missing, The Cure, Crystal Castles) and influences (Depeche Mode, Tool, Gesaffelstein...) | `docs/brand/positioning.md` |
| Checkpoints 25 Sep, 31 Oct | Never recorded | `next-six-months.md` |
| Pinocchio submit 28 Sep / 5 Oct | Not submitted. Now the **Half the Night EP** (Half the Night + Pinocchio). Tags locked 11-03, cover 1a picked, effects pending | 🎵 Release 1, 2, 9; release handover |
| Spotify neighbourhood curator list | On hold since 10-01, waits for seed artists | 🎵 Release 3 |
| Spotify self-pitch 9 Oct, Bandcamp pre-order 19 Oct, pre-save 26 Oct | None done (nothing delivered) | 🎵 Release 9, `bc06-nov6-half-the-night.md` |
| 2-3 reels, first song "working" content (Oct) | No IG post logged since the July Deceiver campaign. IG media count 83 (04-03) → 85 (11-03) | `ig-content-performance-log.md`, snapshot 04-03, `dj07-own-lists-2026-11-03.json` |
| Songs to finished mixes (Oct) | **No file records song progress** | none found |
| Downtempo grouping (end Oct) | Not decided | 🎵 Release 5 |
| Release 6 / 13 Nov | Not possible; release is 3-4 weeks after submit, so early Dec at best | release handover |
| Bridge test, late Nov | Not started; needs finished songs | none found |
| Song-era label list, demo wave by 11-15 | Proposed only | 🎵 Release 6 |

## 2. Numbers vs the targets Amir approved on 2026-11-01 (`plans/targets.json`)

| Metric | Baseline | Rung 30 Nov | Rung 31 Dec | Latest | Source of latest |
|---|---|---|---|---|---|
| IG followers | 966 (11-02) | 996 | 1026 | 969 (11-03) | `dj07-own-lists-2026-11-03.json` |
| IG follow-back | 23% | floor 20% | | 22.6% (10-10 export) | `stats_snapshots/ig_followback.json` |
| SC followers | 447 (10-31) | 510 | 600 | 470 (11-05) | snapshot 11-05 |
| Spotify monthly listeners | 96 (10-30) | 90 | 110 | 94 (week to 10-31) | `stats_snapshots/spotify_s4a.json` |

Ratios: IG 969 / 964 = 1.01:1, SC 470 / 457 = 1.03:1 (floor 1:1, target 1.4-1.6:1). SC ladder
(SOP): 420 by 10-31 met, ratio 1.1 by 10-31 missed; 1,000 by Aug 2027.

Numbers with **no target anywhere**: Spotify followers (64 on 09-12 → 68 on 10-31; the 09-13
plan called it "the one that matters"), YouTube (5 subscribers), Bandcamp (51 followers, 10-21),
email list, pre-saves, gigs, income.

Older goals that expired unmet: IG 790 → 1,200+ and ratio 2:1 by ~Oct 2026
(`plans/ig-engagement-strategy.md` line 5, 04-23); master plan "3 EPs in 2026" (2 singles out).

## 3. What the code measures, and what it does not

- Measured daily: SoundCloud (live), YouTube (live), HikerAPI balance. Spotify comes only from the
  Monday Spotify for Artists read; the Spotify API fields (followers, popularity) are empty in
  every recent snapshot.
- **Instagram is not collected daily** (the 08:45 sync runs with `--skip instagram`); only 2
  snapshot readings exist (10-21, 11-02). IG per-post reach was last saved 10-04.
- Not measured at all: email list size, pre-saves, gigs/bookings, income beyond the Bandcamp CSV,
  outreach replies (only hand-set statuses).
- The session scorer (`close_loops.py`) rates how the automation behaved, not audience growth.
- Source: code map of `stats/collectors.py`, `stats/daily_sync.py`, launchd plist, `stats/spotify_s4a.py`.

## 4. Work done Sep-Nov that the plan did not list

- Release Manager: 19 tickets done (Machine-10 to 28): audit + refresh, Brand, Shoot, Video,
  Imagine, Archive, Fonts, Effects, Playground, copy writers; score board + targets (11-01).
- 📱 Socials: IG + SC automation tuned (HikerAPI since 09-14, IG caps 12/16/8 since 11-04),
  YouTube catalogue (11 videos), Bandcamp traffic plan.
- 🎧 Booking: Blank Wave guest mix live 10-08; DJ outreach research (4 batches, 148 cards,
  10 drafts in his voice, 0 sent); Beate Uwe rebooked for Dec.
- 💰 Income: Gap Radar built; 4 runs, 40 ideas, 0 vetted; ~$36 of the $200 Claude credit in Nov.
- 🎛️ Studio: sample library (41 racks, snares by key, Serum sort), PROJECTS backup 10-25.
- ⚙️ System: six areas + handovers, GitHub backup design, 12 skills installed 11-05.

## 5. Dates that are close or already passed

| Date | What | Source |
|---|---|---|
| 26 Oct (passed) | Tallinn Music Week open call | `plans/festival-targets-2026-27.md` |
| **6 Nov (tomorrow)** | CTM Vorspiel open call (Berlin, Jan 2027, needs a venue partner); Bandcamp Friday; Master & Servant draft dated "the 6th" | same; `bc06-nov6-half-the-night.md`; booking handover |
| 16 Nov to 10 Jan | 48 Stunden Neukölln application window | `festival-targets-2026-27.md` |
| ~15 Nov | Extra IG all-time export (unfollow sweep) | ig-kpis memory |
| 30 Nov | First rungs of the approved targets | `plans/targets.json` |
| 4 Dec | Bandcamp Friday | release guide §14 |

## 6. Which strategy docs are current, which are history

| Doc | Date | State |
|---|---|---|
| `docs/brand/positioning.md` | 09-19 | **Current.** Holds the long-run aim: living from music, touring Europe + USA, large streaming numbers, "it has to be pop" |
| career strategy §0 + `next-six-months.md` | 09-13 | Direction still valid; timeline out of date (section 1) |
| `plans/targets.json` | 11-01 | **Current**, Nov-Dec only, 4 metrics. Note: the score-board spec still says "DRAFT, waiting for approval", while the targets file records Amir's approval on 11-01 |
| marketing guide, release guide | 03-17 | Electronic-era tactics. Still useful for mechanics (save rate, pitch timing, Bandcamp Fridays); Beatport-first and Reddit parts are superseded by the light lane |
| `master-plan.md`, `project-brief.md`, career strategy §1-9 | March | Electronic-era goals (3 EPs, Beatport, label demos, management). Not marked as superseded inside the files |
| IG engagement strategy | 04-23 | Goal expired (1,200 + 2:1 by Oct) |
| web3 strategy | 04-10 | Says "ready for execution", but `release-lessons.md` declared the Web3 lane dead on 07-11 |
| sync licensing plan | 07-27 | DRAFT, 4 open decisions, no progress logged; its Dec row still has "EP3 Downtempo" |
| Light After Two business plan | 04-16 | A friend's project, not Inch of Shadow |

## 7. Files that say different things

- Pinocchio 11-06 still shown as upcoming in `docs/ig-agent-context.md`, `docs/brand/formats.md`,
  `docs/brand/frame.md`, `bc06`, the Bandcamp traffic plan and the release file's own
  `release_date` (with a "paused" block). The release handover (11-05) has it back as EP track 2.
- `docs/ig-agent-context.md` and `docs/sc-agent-context.md` (agents read these) still describe the
  electronic positioning, "three EPs", and songs "from 2027".
- Beatport and label demo waves still appear as active channels in `seo-strategy.md`,
  `release-day-playbook.md`, `release-platform-deadlines.md`, `marketing-campaign-template.md`.
- Tag lead: career strategy §0 says lead with "alternative / darkwave / post-punk"; positioning
  (later) says post-punk is "an influence, not a lead tag".
- `CLAUDE.md` tools table: Stats Dashboard "Not started", though `/stats` + score board exist.
- ig-kpis memory: follow lane "paused, 0 follows"; sessions now run 16 follows.

## 8. System facts found on the way (not strategy, listed so they are not lost)

- Test suite red every night 10-31 to 11-04 (5 failed, then 1 failed on 11-04). `docs/reports/dispatch-log.md`
- `engagement_log.json` over its size cap (1,637 KB vs 1,500 KB). `docs/reports/loop-close-ig-2026-11-04.md`

## 9. How we work (checked 2026-11-05)

**Runs and messages.** 11 recurring scheduled runs (`~/.claude/scheduled-tasks`) + 4 launchd jobs.
A normal day:

| Time | Run | Reaches Amir as |
|---|---|---|
| 06:30, 07:30 | SC refresh 1/3, 2/3 | one-line reply (hidden run) |
| 08:30 | SC refresh 3/3 | daily health report |
| 08:45 | stats sync (launchd) | nothing |
| 09:30 | IG dispatcher (launchd) | macOS popup when something is wrong |
| 10:00 | SC session | session report |
| 10:30 | IG token refresh (launchd) | nothing |
| 13:00 | SC retry | one line |
| 15:00 | IG session (Mon/Wed/Fri/Sat) | session report |
| 20:00 | 📱 Socials digest (new 11-05) | digest in the Socials chat |
| 22:30 | heartbeat (launchd) | macOS popup; it popped "TEST SUITE RED" every night 10-31 to 11-04 (fixed 11-05, ⚙️ System 66) |

Plus weekly (Mon Spotify read, Fri SC release stats, Sun IG stats) and 1st/15th SC maintenance.
The scheduled-tasks folder holds 41 task folders; only 16 are registered, so ~25 are leftover
one-time runs from Aug-Oct.

**Rules.** 145 memory files, 81 of them feedback rules, 12 marked HARD RULE. The index
(`MEMORY.md`) is 28 KB, over the 24.4 KB load limit, so its **last 15 lines are not loaded when a
chat starts**. Those are the newest rules (11-05): delete finished side chats, our code first,
Gap Radar autopilot, Mosseri before posting, GitHub account split, no relaying side-chat news.
One rule (side-chat deleting) changed three times on 11-05.

**Where the truth lives.** Two ticket boards + `TICKETS.md` history + 8 handovers + memory +
strategy docs + agent context files + Release Manager pages. The same fact (e.g. the Pinocchio
date) is written in 7+ places, which is how they drift apart (section 7).

**Things that act without a per-action yes** (each was approved once, as a standing rule):
- IG dispatcher: daily HikerAPI reads, pool audits, contact re-checks.
- IG + SC sessions: run on a standing confirm, no per-session yes.
- SC 08:30 run commits data to git every day.
- Gap Radar autopilot: chains its own tickets when one unblocks the next.
- "Auto-update the Release Manager" whenever stats or release work comes up.
- IG token refresh.
- Seven "always remind" rules: IG export, before-post checklist, photo 55, second opinion,
  SC Amplify, stats improvement ideas, Mosseri check.

**Chat length.** The rule is short bullets with emojis and "done" for a finished ticket. Several
of my replies today were 20-30 lines (the facts summaries), i.e. the rule is not being kept.

## 10. Our LLM system vs Claude Code's own guidance (checked 2026-11-05)

Yardstick: official Claude Code docs (memory, skills, sub-agents, hooks, best-practices pages,
fetched 11-05). Our side: checked on disk.

| Part | What the docs say | Ours |
|---|---|---|
| Where chats start | Rules load from the start folder upward; subfolder CLAUDE.md only when a file there is touched | Most chats start in `Inch of Shadow/` (parent), which has **no CLAUDE.md**. The project rules in `Inchofshadowcode/CLAUDE.md` load only once a chat opens a file in the code folder |
| Memory index | First 200 lines or 25 KB of MEMORY.md load; the rest does not | 28 KB, so the end is cut: the newest rules (11-05) are not loaded at start |
| Memory folders | One memory per project; worktrees share their repo's memory | **Two memories**: parent folder (146 files, current) and code folder (65 files, last touched 2026-07-26). A chat started in the code folder, or in a code worktree (🎬 YouTube, 🎬 Bandcamp side chats; inferred from the docs), reads the old July memory |
| Skills | Only the start folder's `.claude/skills` and personal skills are listed | Our own skills (`/release`, `/ig`, `/sc`, `/promo`, `/bio`, `release-prep`, `sync`, `enrich`, `discover`) live in the code folder, so a parent-folder chat sees them only **after it touches a file in the code folder** (seen live on 11-05: they appeared right after the first edit there). Until then it lists only the 17 skills installed 11-05 + brand, so "/release" at the start of a fresh chat may not be found. 31 personal video skills load their descriptions in every chat |
| Agents | `.claude/agents`, one job each, tools/model set per agent | ig-expert, promotion-expert, sc-expert (symlinked into the parent 10-22) + web-search-agent. Fine |
| Must-never rules | Memory and CLAUDE.md are read and can be skipped; hooks, deny rules and settings are enforced every time | 12 HARD RULES, all prose. **0 hooks** anywhere. 131 allow rules in the parent `settings.local.json` |
| Consistency | Conflicting instructions are resolved arbitrarily; review periodically (`/doctor` flags stale or contradicting lines) | Rules changed 2-3 times in one day (side-chat delete); agent context docs (`docs/ig-agent-context.md`, `sc-agent-context.md`) still electronic era; ~25 dead scheduled-task folders |
| Long work | `/clear` between tasks, hand off via a written spec, named sessions | Handovers per chat (good), parent + side chats (good); many finished auto-run chats stay in the sidebar |
| Unattended runs | Need a spend/turn cap and a person who approves results | IG/SC sessions run on a standing confirm with caps in config; scorer + heartbeat check them |

## 11. Five more areas (checked 2026-11-05; money in/out left out on Amir's call: too early)

**A. Your bottleneck.** 55 open tickets on both boards (29 proposed, 11 waiting, 10 in progress,
5 approved). **32 of them wait on Amir** (`who` = amir or `blocked_on` names him): Socials 10,
System 9, Release 7, Booking 3, Income 3. On top, the handovers list **38 open decisions** for
him (Studio 8, Booking 5, Release 4, Bandcamp 4, IG 4, GitHub 4, ...). 15 open tickets have no
bucket yet (Booking, Studio, Control Panel rest). Of the 40 newest sidebar chats (11-03 to 11-05),
about 21 are finished automated runs.

**B. Content output.** Last IG feed post: **2026-07-10** (The Deceiver campaign; `ig_insights.json`
lists 6 posts in 2026: Jan, May, Jun, Jul x3). Since then: Blank Wave story (stories, 10-09) and
renders in `videos/` (code-finale-reel, ios-sting, look06 title arrivals) with no posted record.
The four video playbooks exist (`videos/IOS-*.md`). What blocks a post between shoot and share
is not written anywhere.

**C. Risk & safety.**
- Mac disk: 38 GB free. Intenso backup drive: 3.1 GB free (full). Last full Inch of Shadow
  folder copy 10-19, PROJECTS 10-25 (memory `intenso-backups`); DONE + Doom + Men Machine not
  backed up anywhere current. Masters also in Dropbox.
- Code: git is local only (no remote, by rule), 46 MB history; the GitHub backup waits on the
  new account (⚙️ System 62).
- Secrets: `.env` ignored; the 5 token/secret files are not tracked. OK.
- Logins: IG Graph token valid to 2027-01-03 (auto-refresh); YouTube login expired ~10-28
  (🎬 Socials 2); YouTube Official Artist Channel requested 09-08, no result recorded.

**D. Built vs used.** The Release Manager runs (port 5001, started from a terminal) but keeps
**no usage log**, so which pages Amir opens is unknown. Indirect only: since 10-05 files changed
under playground-wall (4), effects (247), shadow-archive (169), generated_images (190), outreach
(1), fonts (1); `artist_profile.json` unchanged since 09-21. These changes can be Claude's own
work, so they do not prove use.

**E. Fans you own.** Bandcamp: 51 followers, **16 mailing-list addresses** (export 10-21; correction:
section 2 said email list unmeasured, it is 16 but only via a manual export every 3 months).
Spotify followers 68. Scene Intelligence: 1,336 contacts (industry, not fans). No smart link /
pre-save list exists yet.

## 12. Open questions only Amir can answer (input for step 2)

1. How many songs are finished, and what is missing on the rest (mix, master, vocals)?
2. For the next 6 months, the order of songs, gigs, income and the electronic EP.
3. Hours per week you can give to each.
4. Spotify followers: was it dropped as "the one that matters", or should it join the targets?
5. CTM Vorspiel (tomorrow) and 48 Stunden Neukölln: in or out?
6. Which messages do you actually want each day, and in which chat? Which of the
   "acts without a yes" items stay?
7. Which Release Manager pages do you really open?
8. What stops a post between shoot and share?

**Answered 2026-11-05 (Amir):** Q1 songs: about 8 songs, none close to master; the music is basically ready, missing vocal takes and vocal sound. Planned as singles (checked against Spotify rules: singles fit). First single not picked; picked when its vocals land. Half the Night ships as early as possible.

**Update 2026-11-05 (Amir):** songs are NOT tracked by the system (no song files, no song pipeline on the page). His next 2-3 months: 2 full songs ready, and mainly content: finding the content language and styles, with checks along the way. SC and IG automation continue as planned (not up for review). No live shows for now, DJ only; 48 Stunden Neukoelln is out.

**Batch 2 answers (Amir, 2026-11-06, at the desk; the 11-05 phone answers were discarded):** D2 Socials > Release > Income > System > Booking > Studio. D3 20+ hours/week. D4 scoreboard adds Spotify followers, day-28 release engagement, email list (rungs not yet confirmed). D5 wants the detailed per-platform plan first; TikTok to be treated as a possible carrier ("we may get exposed there"). D8 TikTok later, with the first song. D12 all four rule drafts, yes. D13 daily brief in the System chat at 20:00. D15 plans external hardware, asked for a written suggestion. D17 uses Dashboard, Releases, Playground, Stats mainly + Words/Outreach/Imagine/Effects/Archive; never the Artwork Resizer; the IG names tab no longer relevant; wants the full page list reviewed. Nothing from Batch 3 starts until he says go (pause rule).

**D15 (2026-11-06):** backup later; Amir buys the 4 TB drive first; offsite copy decided after. **D17 (2026-11-06):** yes to the keep/merge/drop list: keep Dashboard, Releases, Playground, Stats, Words (SEO copy + Bios merged), Outreach, Imagine, Effects, Archive, Fonts, Shoot, Video, Photo editor; drop Artwork Resizer, Engagement names tab, Promotion, Palette, Autopilot; merge Tickets+Board, Video Resizer into Video; SC automation page = ask the SC chat. Nothing removed before a dry run he sees.

**D5 (2026-11-06):** yes to `platform-plan-songs-2026-11-05.md` after the Opus gate. Batch 2 complete. Batch 3 has not started; it starts only on his explicit go.

**Gero follow-up (2026-11-06, Amir: "approve all"):** the five findings are approved as plan content and added to the page as S10 (clip pack), S11 (activation), M10 (review without folders; Amir will test it when built), M11 (data accuracy + dashboard), M12 (ticket shape). Batch 3 stays paused; nothing starts until his go.

## D9 answer (2026-11-06)

**Amir's exact words:** "A"

**Chosen rule (D9, paid promotion per release): A. Capped test, judged at day 28.** Own network and free routes first; then at most EUR 50 on one route per release, kept only if Spotify adds + saves at day 28 beat the unpaid release. How paid premieres (ladder EUR 30-80) sit under this cap is not stated in his answer; open for the System chat. The ⚙️ System chat writes the rule into the guides.

## RM 2.0 slice 1 answer (2026-11-06)

**Amir's exact answers (question card, side chat):**
- Drop list as one yes: "Yes, all 5" (Palette/Settings, Autopilot, Engagement names tab, Promotion, Artwork Resizer nav link; 27 routes, 4 templates, 16 tests, `email_outreach.py` + `contact_bridge.py` + `test_email_outreach_hardening.py` to `archive/rm-promotion/`, undo = `git mv` back).
- Work page shape: "Stacked (Recommended)" = tickets on top, board below, By number as a view switch.
- Video page shape: "Stacked (Recommended)" = video projects on top, resizer section below.

Still open before slice 1 runs, as in the dry run: the IG chat's OK on `release_context.json` losing its only writer. The ⚙️ System chat runs the slice.

## D9 premieres (2026-11-06)

**Amir's exact words** (side chat, answer to "Premieres under D9?" with options A one route EUR 50 / B premiere separate up to EUR 80 / C no paid premieres / D 2 routes EUR 50 shared): "mianly one route B is an option. for now 50 EUR"

Earlier in the same chat, dropped by him ("no u know what ask question again"): first pick "A", then "2 routs", then "EUR 50 total, shared".

**Reading (side chat, not his words):** mainly one paid route per release (A); a separate premiere (B) stays possible; the budget for now is EUR 50 per release. Not stated: whether a B premiere sits inside the EUR 50 or on top of it.

## RM 2.0 slices 9 and 10 answers (2026-11-06)

**Amir's exact answers (question card, side chat):**
- (a) Held items in Review: "Keep the refusal (Recommended)" = a held item cannot be approved; he fixes the file and approves the new version (Change and Drop still work).
- (b) Release that seeds Review first: "Farewell, as a test (Recommended)" = `farewell-single`, released, nothing at stake.
- (c) Home page: "The four blocks as planned (Recommended)" = verdict line, 🔥 Now by area, decisions waiting on Amir, next release + "Out"; backup/drive footer kept.
- (d) Social links block on Home: "Keep it".

Note for slice 10: section 1b of `rm2-dry-run-2026-11-06.md` lists the social links block under "Dropped"; by his answer it stays on Home. Where it sits among the four blocks is not stated in his answer. The ⚙️ System chat runs both slices.

## System 67 Chrome queue (2026-11-07)

**Amir's exact answer (question card, side chat, "Switch on the Chrome queue for all chats?"):** "Yes, switch it on (recommended)"

**Done (side chat):**
- Backup first: `~/.claude/settings.json.bak-2026-11-07-chrome-queue` (byte copy, checked with cmp). Value before: no `hooks` key in `~/.claude/settings.json`.
- Added the `hooks` block from `plans/chrome-queue-install.md` as a new top-level key (PreToolUse matcher `mcp__claude-in-chrome__.*|mcp__Control_Chrome__.*`, plus SessionEnd, both run `tools/chrome_queue_hook.py`, timeout 10). Only change to existing text: a comma after `"model": "opus"`. Python check: JSON valid, every old key unchanged, one new key `hooks`.
- Test in a scratch folder (`CHROME_QUEUE_ROOT`): first fake Chrome call = allowed (exit 0, no output, auto-claim); a second fake chat = refused with "Chrome is held by Inch of Shadow since 19:12 ... You are number 1 in line". Scratch folder deleted.
- Real root status after: "Holder: none, Chrome is free", queue empty. Chrome not opened. Tests: 25 passed.
- Live from the next chat start (running chats may need a restart to load the hook; not verified).
- Switch off: remove the `hooks` key, or copy the backup back.

## M5 dead code answers (2026-11-07)

**Amir's exact words** (side chat, answer to "Go with my picks for the M5 dead-code list?" after the side chat's recommendation, which he asked for with "what u think?"): "Yes, your picks"

Checked 11-07 before asking: all 45 section A rows still on disk, none has a commit after 2026-11-05, the 13 look02 twins still byte-identical (md5). No row dropped.

What "your picks" means, one line each:
- A1 SI discovery: YES, move to `archive/si-discovery/`, except `extract_contacts.py` and `extract_ra.py` (stay, imported by `promo_dj_shortlist` which stays) and `enrich_soundcloud.py` + `run_sc_enrich.command` (SC chat decides). 12 scripts move.
- A2 Google Sheet push: YES, move to `archive/si-sheet/` (push_to_sheets, sync.sh, runsync, test_sheets_sync_safety).
- A3 Spotify curator pipeline: NO, keep for now (Release 3 curator list is waiting, not dropped).
- A4 Promo shortlists + release health: NO, keep for now (may serve the Half the Night EP DJ promo; park after that promo).
- A5 RM CLI: YES, move `release_manager/cli.py` to `archive/rm-cli/`.
- A6 Root tools: PART, `description_scorer.py` moves to `archive/root-tools/`; `letter_slides.py` stays.
- A7 Logo duplicates: YES, move the 13 `references/look02/scripts/*.py` copies to `archive/look02-duplicates/`.
- REVIEW extract_contacts (moves only with A2 + A4): stays, since A4 stays.
- REVIEW push_to_sheets (master sheet a view of SI?): no, park the pusher; the sheet stays as it is, no more pushes.
- REVIEW curator rows (R-03 on hold): keep the scripts until Release 3 is done or dropped.
- REVIEW promo_dj_shortlist (dj_promo_targets.json changed 10-10): keep the script; the 10-10 change sits in the 10-09 IG session commit, most likely not this script.
- REVIEW letter_slides (letter format alive?): keep; three brand docs still name it.
- REVIEW look02 (which copy goes): the `scripts/` copy goes; the top-level/moon/v2/v3 copy stays beside the 27 renders.
- REVIEW enrich_soundcloud: not asked here, the SC chat answers.
