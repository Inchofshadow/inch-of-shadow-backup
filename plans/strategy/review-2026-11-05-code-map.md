# Strategy review: code map (2026-11-05)

Read-only audit of all code in `Inchofshadowcode/` plus the code that lives next to it
(`../youtube/tools`, `../videos/*`, untracked `music-tools/`). Nothing was edited, moved or
deleted. Builds on `review-2026-11-05-facts.md` sections 3, 8, 11; those facts are not repeated.
Evidence: `git log -1` per file, launchd plists, the 16 registered scheduled tasks, imports,
`docs/reports/*`, file dates. No secret values were printed.

## Headline numbers

| What | Number |
|---|---|
| Python in git (outside tests) | 181 files, 60,977 lines |
| Python outside git | music-tools 22 files / 2,200 lines (untracked); youtube/tools 8 / 819 (parent folder, no git); videos/blank-wave scripts 4 (no git) |
| Tests | 149 files, 12,457 lines. **Run today: 1,136 passed, 0 failed, 21 s** (`pytest -q -x`). Green again after red 10-29 to 11-04 |
| Release Manager | 12,880 lines Python + 6,790 lines templates; `webapp.py` alone 5,685 lines, 142 routes (55 `/api`, ~25 pages) |
| Biggest single files | sc_engagement.py 3,937, ig_engagement.py 2,822, push_to_sheets.py 1,369, artwork_resizer.py 1,151, close_loops.py 1,013 |
| Run automatically | 4 launchd jobs + 11 recurring scheduled tasks; they reach ~35 modules (IG engine, SC engine, stats) |
| Commits | 730 total, 187 since Oct 1. Daily work sits on branch `score-board`, **91 commits ahead of `main`** (main last 11-01). 17 stale branches from June-July |
| Code with no run, no commit since Sep and no recent use | ~13,000 lines (classes DORMANT / ELECTRONIC-ERA below) |

## The big table

Auto = launchd or scheduled task runs it (or imports it). Manual = run by hand or via RM, with a
dated trace Oct-Nov. Tests = number of test files that touch the group.

| # | Group | Purpose (1 line) | Files / LOC | Last commit | Run | Tests | Class | Evidence |
|---|---|---|---|---|---|---|---|---|
| 1 | IG engine (`scene_intelligence/ig_*`, `close_loops`, `json_io`) | IG follow/like sessions, queue, ledger, guards, dispatcher, loop close | 30 / 13,203 | 11-05 (config) | Auto: launchd dispatcher 09:30, heartbeat 22:30; task `ig-engagement` 15:00; `ig-weekly-release-stats` Sun | 13+ (ig_engagement 11, close_loops 13, merge 8) | ACTIVE-CORE | 46 `loop-close-ig-*` reports, latest 11-04; dispatch-log 11-05 |
| 1a | ...inside it: `ig_enrich_instagram`, `ig_enrich_helper`, `ig_followback_checker`, `ig_reconcile_followings`, `ig_backfill_reciprocity`, `ig_show_automation_follows`, `ig_build_voice_profile`, `ig_import_manual_2026-06-03` | Direct-read era helpers and one-offs | 8 / ~2,100 | 05-11 to 09-03 | None found | 0-1 each | DORMANT | Direct IG reads retired 09 (HikerAPI since 09-14); si-audit 11-03: "ig enrichment last 2026-04-28"; `ig_reenrich_contacts` (dispatcher) now does this job, so also DUPLICATE |
| 2 | SC engine (`sc_*`, `check_sc_follows`) | SC follow/like/unfollow sessions, 3 daily discovery refreshes, maintenance | 12 / 7,228 | 11-03 | Auto: tasks 06:30, 07:30, 08:30, 10:00, 13:00, 1st/15th, sweep 11-06 | 30 for sc_engagement | ACTIVE-CORE | 72 `loop-close-sc-*`, `sc-weekly-20261105.md`, session report 11-05 |
| 2a | ...`sc_unfollow_cleanup.py` (1 line), `check_sc_follows`, `sc_build_browser_session`, `sc_log_manual` | Old stubs and manual intake | 4 / 821 | 06-14 to 09-01 | None found | 0-1 | DORMANT | 1-line stub; last mention sc-twin-audit 09-10 |
| 2b | `sc_release_stats.py` + task `sc-weekly-release-stats` | Weekly SC stats for The Deceiver and Farewell | 1 / 127 | 09-11 | Auto Fri 18:00 | 1 | ELECTRONIC-ERA | Task description names only Deceiver + Farewell; runs every week |
| 3 | SI contact store (`contact_index`, `si_cleanup`, `si_follow_flags`, `bandcamp_supporter_match`) | One contact DB, flags, cleanup plan | 4 / 1,099 | 11-03 / 11-04 | Imported by dispatcher (flags) + manual | 1 each | ACTIVE-SIDE | `si-audit-2026-11-03.md`, `si-cleanup-plan-2026-11-03.md` |
| 4 | SI discovery + enrichment (`discover_contacts`, `enrich_*`, `extract_*` incl. RA + rekordbox, `re_enrich_discogs`, `fetch_youtube_subs`, `update_scores`, `classify_subtypes`, `scrape_label_emails`, `scene_plan_recency_filter`) | Build the industry contact DB from DJ sets, RA, Discogs, labels | 15 / ~6,500 | 04-07 to 09-01 | None | 0 for 13 of 15 | DORMANT + ELECTRONIC-ERA | si-audit 11-03: "Discogs/Spotify/YouTube/URL enrichers (scripts from March)" not run; sources are DJ world (rekordbox, RA, Discogs) |
| 5 | `push_to_sheets.py` | Push SI to the Google Sheet | 1 / 1,369 | 07-19 | Manual (`/sync` skill) | 1 | DORMANT | No commit since July; only mention since is the 11-03 audit proposing to drop ~45 dead columns |
| 6 | Curator pipeline (`curator_*`, `discover_curators`) | Spotify playlist curator DB + pitch sheet | 6 / 951 | 06-09 to 07-05 | None | 4 | DORMANT + ELECTRONIC-ERA | R-03 curator list on hold since 10-01; last doc mention 07-04 |
| 7 | Promo shortlists + release health (`promo_dj/label/press_shortlist`, `release_status`, `release_weekly_health`) | DJ, label-demo, press lists; per-release health | 5 / 719 | 06-03 to 07-19 | None | 1 each | ELECTRONIC-ERA | Label demo waves superseded (fixlist rows 20-22); last report `release-health-20260805.md` |
| 8 | Stats (`stats/*`) | Daily collectors, S4A weekly read, targets, score board inputs, IG token refresh, Socials digest, Bandcamp CSV | 14 / 2,845 | 11-05 | Auto: launchd stats-sync 08:45 (`--skip instagram`), token refresh 10:30; tasks S4A Mon, digest 20:00 | 1-3 each; **`socials_digest.py` 0** | ACTIVE-CORE | `stats-sync-launchd.log` 11-05 "Platforms: spotify, soundcloud, youtube, hikerapi" |
| 9 | Release Manager core (`webapp`, `checklist`, `timeline`, `tickets`, `board`, `score_board`, `stats_tracks`, `outreach`, `playground`, `effects_page`, `fonts_page`, `archive`, `imagine*`, `claude_api`, `openai_api`, `radar_page`, copy writers) | Flask UI on port 5001 | 30 / ~11,300 | 11-05 | Manual (started from a terminal) | 22 files import webapp | ACTIVE-CORE | Data under playground-wall, effects, archive changed 11-04/05; no usage log (facts 11D) |
| 9a | RM leftovers: `email_outreach.py`, `contact_bridge.py`, `cli.py`, `reconcile.py`, `models.py`, `display.py` | Label/press email sender, old CLI front end, old model | 6 / ~1,590 | 04-07 to 09-20 | email_outreach + contact_bridge imported by webapp; cli none | 0-1 | DORMANT; `cli.py` DUPLICATE of the web UI | `email_send_state.json` does not exist (never sent); last mention 07-19 |
| 10 | Image + brand tools (root `artwork_resizer`, `video_resizer`, `image_generator`, `edit_recipe`, `shoot_catalogue`, `shoot_pull`, `print_looks`, `shadow_archive`, `fonts_library`, `letter_slides`; `docs/brand/kit/scripts/*`) | Covers, resizes, AI renders, shoot catalogue, looks | 19 / 6,152 | 09-20 to 11-03 | Manual via RM; webapp imports most | 1-3 for root tools; 1 of 9 kit scripts | ACTIVE-SIDE (`letter_slides` DORMANT) | `artwork/edits` 11-05, `generated_images` 11-04; cover direction docs 11-04/05 name print_looks + image_generator |
| 11 | Copy tools (`caption_check`, `copy_clean`, `description_scorer`, `metadata_utils`) | Clean and check copy; tag metadata | 4 / 972 | 04-07 to 11-03 | caption/copy via RM `copy_pass` | 1 / 1 / 0 / 0 | ACTIVE-SIDE; `description_scorer` DORMANT + DUPLICATE of caption_check/SEO checks | description_scorer imported by nothing, last commit 06-14 |
| 12 | `bandcamp_links.py`, `fetch_text.py`, `hygiene_check.py` | ?campaign links; safe text fetch; repo hygiene | 3 / 395 | 10-24 to 11-03 | hygiene via task `sc-monthly-maintenance`; others manual | 1 each | ACTIVE-SIDE | Named in 11-05 agent docs + memory |
| 13 | `gap_radar/` | Research engine, many profiles (IoS, income, apartment, Gero) | 5 / 1,259 | 11-05 | Manual only: plist is a `.draft`; `schedule.py` refuses while caps are null | 1-2 each | ACTIVE-SIDE | 6 reports, latest 11-05 04:08; `schedule.json` points at `/Users/amir/apartmentcode/...` (other project inside this repo) |
| 14 | `references/look02/**` logo scripts | Logo rounds b-g, moon, v2, v3 | 28 / 3,880 | 09-25 and 11-03 | None | 0 | DUPLICATE + DORMANT | Same 14 scripts exist twice (`scripts/` 09-25 and top-level/`v2`/`v3`/`moon` 11-03, same line counts); logo is parked |
| 15 | `plans/outreach-page/**` scripts | One-off builders for DJ outreach batches and drafts | 10 / 1,416 | 11-03 | Manual one-offs | 0 | ACTIVE-SIDE (code inside `plans/`) | Booking batches 11-02/03 |
| 16 | `../youtube/tools/` (NOT in git) | YouTube metadata apply, release, thumbnails, snapshot | 8 / 819 | files 08-16 to 09-21 | None; last `youtube/stats` 10-13 | 0 | DORMANT; `yt_snapshot` DUPLICATE of `stats/collectors.collect_youtube` | YouTube login expired ~10-28 (facts 11C), so `yt_apply`/`yt_release` cannot run: BROKEN until re-login |
| 17 | `music-tools/` (untracked, 215 MB) | Drum racks, Serum sort, snare keys, dupes, PROJECTS backup | 22 / 2,200 | files to 10-25 | Manual | 1 own test | ACTIVE-SIDE; `drumrack_tool` v1 vs v2 DUPLICATE; `dupes/scan_dupes.py` vs `plans/cleanup/scan_dupes.py` DUPLICATE | Not in git, so no history and no backup beyond Intenso |
| 18 | `plans/cleanup/*.py` (untracked) | 11-05 trash job + undo script | 3 / 88 | 11-05 | Manual one-off | 0 | ACTIVE-SIDE one-off | Undo script dated 11-05 04:13 |
| 19 | `../videos/blank-wave-130-story/*.py` (no git) | Story renders for the guest mix | 4 / 306 | 10-09 to 10-11 | One-off | 0 | DORMANT (done) | G-02 closed 10-13 |

**BROKEN today:** nothing in the tests. Live faults: (a) launchd heartbeat last exit = 1 (from the 11-04
red run; clears tonight if green); (b) `engagement_log.json` warning "1637KB > 1500KB, schedule the
archival job" posted by the dispatcher every day since 10-29, and no archival job exists; (c) YouTube
OAuth expired, so group 16 cannot write; (d) HikerAPI balance hit 0 on 10-30/31 (`dispatch-log.md`),
since topped up.

## Release Manager pages

Data date = newest file the page reads. "Since Oct 1" = changed on or after 2026-10-01.

| Page | Reads | Data date | Since Oct 1 | Note |
|---|---|---|---|---|
| `/` Dashboard (+ `/autopilot` redirects here) | releases, tickets, brand | 11-05 | yes | `/autopilot` is a dead redirect |
| `/release/<slug>` (+ new, edit, track) | `releases/*.json` | 11-04 | yes | Only 3 releases (Deceiver, Farewell, Pinocchio). **The Half the Night EP has no file**: it lives inside `pinocchio-single.json`, whose `release_date` is still 2026-11-06 |
| `/tickets` | `plans/tickets.json`, outreach, booking_targets | 11-05 | yes | booking_targets 10-21 |
| `/board` | `plans/control-panel/tickets.json` | 11-05 | yes | |
| `/outreach` | `plans/outreach-batches.json` | 11-02 | yes | |
| `/palette` | `theme.json` | 04-21 | **no** | |
| `/edit` | `artwork/edits/` | 11-05 | yes | |
| `/imagine` | `generated_images/`, `docs/brand/ai-test-set.json` | 11-04 | yes | test set 09-27 |
| `/artwork-resizer` | writes `resized/` | empty since 10-11 | **no** | |
| `/video-resizer` | writes `resized_video/` | only `.gitkeep` | **no** | |
| `/video` | `../videos/` | 10-11 | yes | |
| `/seo-copy` | `seo_copy_artifacts/` | 09-27 | **no** | |
| `/bios` | `artist_profile.json` | 09-21 | **no** | Bio still electronic-era (fixlist) |
| `/engagement` | `enriched_contacts.json`, `engagement_log.json` | 11-05 | yes | written by automation, not by the page |
| `/promotion` | `promotion_log.json`, contacts | 09-01 | **no** | ELECTRONIC-ERA (Farewell campaign) |
| `/shoot` (+ covers, pfp) | `plans/control-panel/shoot-catalogue.json` | 10-14 | yes | |
| `/fonts` | `docs/brand/fonts/fonts.json` | 10-14 | yes | |
| `/playground/<slug>` (+ wall, elements, colours, ig-grid) | `plans/playground-wall/` | 11-05 | yes | uncommitted edits today |
| `/effects` | `docs/brand/effects/effects.json` | 11-04 | yes | |
| `/archive` | `docs/brand/shadow-archive/index.json` | 11-04 | yes | |
| `/stats` (+ score board) | `stats_snapshots/`, `plans/targets.json` | 11-05 | yes | |
| `/sc-automation` | `sc_follow_tracker.json` | 11-05 | yes | |
| `/radar` | `gap_radar/reports/` | 11-05 | yes | |

Summary: 24 pages; 17 with data changed since Oct 1, 7 without (`/palette`, `/artwork-resizer`,
`/video-resizer`, `/seo-copy`, `/bios`, `/promotion`, `/autopilot`). "Data changed" is not "Amir used
it" (facts 11D).

## Gaps vs the songs strategy (each tied to a plan line)

| Need | Plan line | What the code does now |
|---|---|---|
| Song progress (mix, master, vocals per song) | `next-six-months.md:44` "Songs to finished mixes" | Nothing. The release model only knows releases with tracks; no song entity, no stage |
| Pre-save / smart link with follow ask | `next-six-months.md:46, 54, 74`; `career-strategy.md:48`; `research-release-fans-2026-11-05.md:66` (Feature.fm Free) | Only a checklist item `presave_links` in `release_manager/checklist.py:176`. No link record, no count |
| Spotify followers as a tracked target | `next-six-months.md:80` "Followers are the one that matters" | `stats/spotify_s4a.py` already parses `followers` weekly, but `plans/targets.json` and the score board leave it out |
| Email list | `career-strategy.md:48, 197, 219` | Not measured; Bandcamp list (16) only via a manual 3-monthly export; `bandcamp_import.py` reads sales CSV only |
| Bridge test readout (watch time, shares per reel clip) | `next-six-months.md:56` | IG skipped in the daily sync; own-post insights last saved 10-04; no per-reel watch-time field anywhere |
| TikTok | `career-strategy.md:64` "Dec: TikTok opens"; `next-six-months.md:66` | Only a manual-entry slot (`stats/storage.py:20`) and a resizer target. No collector, no target |
| EP as one release | release handover (EP = Half the Night + Pinocchio) | EP stored inside a single's slug with a stale date (see RM table) |

## Risks

- **Secrets: OK.** `.env` (mode 600), `credentials.json`, `youtube_oauth.json`, `youtube_token.json`,
  `.sc_user_token.json`, `sc_auth_callback.py` all ignored and never in git history. 35 modules read
  keys from env. A pattern grep over all tracked files found 10 hits, all false positives (base64
  image data in `plans/outreach-page/images.json` + `outreach.html`, slugs like "sk-rad..." in research
  notes, a memory draft). No real key in code.
- **Personal data in git:** `enriched_contacts.json` (2.4 MB, 1,336 contacts) is tracked, plus 97
  tracked files in `scene_intelligence/backups/` and 23 tracked `.bak` files; two worktrees under
  `.claude/worktrees/` hold full copies. Fine while the repo is local; matters the day it goes to GitHub
  (System 62).
- **Single points of failure:** one Mac; git local only; daily work on branch `score-board`, 91 commits
  ahead of `main`; `../youtube/tools` and `music-tools/` code not in git at all; every launchd job runs
  `/Library/Developer/CommandLineTools/.../python3.9` (Python 3.9.6, end of life Oct 2025; the
  LibreSSL warning shows in every log), pinned there because of Full Disk Access; SC/IG sessions
  need Chrome on screen with the right profile.
- **State size:** `enriched_contacts.json` 2.4 MB, `engagement_log.json` 1.6 MB (over its own 1.5 MB
  cap for 8 days), `ig_target_list.json` 1.1 MB, `sc_follow_tracker.json` 490 KB with 3 new 480 KB
  `.bak` copies per day (52 `.bak` files in the SI root now); `scene_intelligence/backups/` 49 MB;
  `data/` (IG exports, ignored) 893 MB. `.git` is 47 MB and grows with the daily SC data commit.
- **One huge file:** `release_manager/webapp.py` 5,685 lines / 142 routes; every page change touches it,
  which is how parallel chats collide (uncommitted edits to it right now).
- **Tests:** 1,136 pass in 21 s. Gaps: `stats/socials_digest.py` (new, runs daily) has no test; 8 of 9
  brand kit scripts, all outreach-page scripts, youtube tools and most of group 4 have none. Today's
  green includes uncommitted edits to `tests/test_playground.py`.
- **Scope creep inside the repo:** `gap_radar/schedule.json` lists apartment-project and Gero profiles;
  `USES.md` says Gero code never comes in, but the engine and its schedule already reach outside.

## Recommended strategy changes for the code

**1. Songs get their own record**
- Was: no file knows how far each song is (facts §1); the code is release-shaped.
- Change to: `songs/<slug>.json` (stage: demo / vocals / mix / master / artwork; date; next step) + a
  small RM `/songs` page + one line on the score board ("songs at master").
- Based on: `next-six-months.md:44`; facts §12 question 1.
- Why: the main line has zero code while the older lane has ~45,000 lines.
- Steps: Amir names the songs and stages; schema + loader + page + test; no automation.
- Songs.

**2. Fan capture metrics join the targets**
- Was: targets cover IG, SC and Spotify listeners only; Spotify followers are parsed but unused;
  email list and pre-saves are not counted.
- Change to: add Spotify followers (from `spotify_s4a.json`), Bandcamp mailing list and pre-save count
  (both via `stats/manual_entry.py`) to `plans/targets.json` and the score board.
- Based on: `next-six-months.md:80`, `career-strategy.md:48`, `research-release-fans-2026-11-05.md:66`.
- Why: these are the owned-fan numbers the songs launch needs; the data path half exists.
- Steps: Amir sets rungs; extend targets schema; score board rows; tests.
- Songs.

**3. Releases become projects, with an open date**
- Was: the Half the Night EP lives in `pinocchio-single.json` with `release_date` 2026-11-06.
- Change to: a release file for the EP (type EP/single, date may be "open"), Pinocchio as a track of it;
  the dashboard and the 7+ docs read the date from this one file.
- Based on: release handover 11-05; facts §7 (date written in 7+ places).
- Why: one source of truth for the next release stops the drift.
- Steps: schema allows null date; migrate file with backup; update dashboard; fixlist rows point here.
- Both.

**4. Instagram own-post insights daily (Graph API, not HikerAPI)**
- Was: daily sync runs `--skip instagram`; own-post reach last saved 10-04.
- Change to: a daily or per-post read of own posts/reels (reach, plays, shares, saves, watch time) with the
  Graph token that already auto-refreshes; stored in `stats_snapshots/`.
- Based on: `next-six-months.md:56` (bridge test reads watch time and shares per clip).
- Why: the bridge test cannot be judged without it. Stats only, not engagement code.
- Steps: check what the Graph token returns for reels; add collector; test; then drop `--skip instagram`.
- Songs.

**5. Park the electronic-era and dead code**
- Was: ~13,000 lines nobody runs (groups 1a, 2a, 4, 5, 6, 7, 9a, 11 `description_scorer`, 14 duplicates,
  RM `cli.py`), plus the weekly `sc-weekly-release-stats` task still pulling Deceiver + Farewell.
- Change to: move them to an `archive/` folder or a tagged branch (tests with them); repoint or stop
  the Friday task; drop `/promotion` and `/autopilot` from the menu.
- Based on: si-audit 11-03 (enrichers not run since April/May), fixlist rows 19-22, this table.
- Why: less to read for every agent and every audit; fewer false "tools" in skills.
- Steps: dry-run list (old/new/reason) for Amir's yes (ask-before-moving rule); move; run tests; undo
  script. IG/SC engine files only with the CC/Fable owners' consent.
- Electronic.

**6. One branch, all code in git, a modern Python**
- Was: work on `score-board` 91 ahead of `main`, 17 stale branches; `youtube/tools`, `music-tools`
  code and video scripts outside git; launchd on Python 3.9 (EOL).
- Change to: merge to `main` and work there; bring the code (not media) of youtube/tools and
  music-tools into the repo; offsite copy when the GitHub account exists, only after the full
  history scrub that the CLAUDE.md publication rule requires; plan a move to Python 3.12
  in a venv with pinned `requirements.txt`, then grant Full Disk Access to that binary.
- Based on: facts §11C (no remote, System 62); `launchd-needs-full-disk-access` memory.
- Why: one disk or one bad merge can lose months of work today.
- Steps: merge + delete merged branches (Amir yes); copy code folders in; Python move as its own ticket
  with a test run under each launchd job.
- Both.

**7. State files rotate on a schedule**
- Was: `engagement_log.json` over cap for 8 days with a daily warning and no job; 3 tracker `.bak`
  copies per day; 120 backup/bak files in git.
- Change to: monthly rotation (current month live, older months to `archive/<yyyy-mm>.json.gz`);
  `.bak` files ignored by git and kept 14 days.
- Based on: `dispatch-log.md` 10-29 to 11-05; facts §8.
- Why: smaller files, faster sessions, smaller git, and less personal data in history.
- Steps: this is engagement state, so propose to Amir and the CC/Fable owners first; dry run; rotate;
  tests on the readers (close_loops, score board).
- Both.

**8. Split the RM web app and log page use**
- Was: one 5,685-line `webapp.py`; no record of which pages are opened (facts 11D); 7 pages with no
  data change since Oct 1.
- Change to: a one-line page-view log first (date, path) for 4 weeks; then split `webapp.py` into
  Flask blueprints per area (Release, Studio, Socials, Stats) and drop pages nobody opened.
- Based on: facts §11D and §12 question 7; RM pages table above.
- Why: answers "built vs used" with data, and parallel chats stop editing the same file.
- Steps: add log (tiny, tested); read it on 12-03; split one area at a time with the 22 webapp tests green.
- Both.
