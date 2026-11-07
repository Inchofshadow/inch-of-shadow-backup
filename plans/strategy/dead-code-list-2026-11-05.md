# Dead code: dry-run list (2026-11-05)

Batch 1 of the ⚙️ System strategy refresh, M5 "park the code nobody runs".
This is a LIST. Nothing was moved, deleted or edited. Every row waits for Amir's yes
(ask-before-moving rule). Groups follow `review-2026-11-05-code-map.md`.

How each row was checked (today, on branch `score-board`):
- lines: `wc -l`; last commit: `git log -1 --format=%as -- <file>`
- "nobody imports it": `grep -rE "\b<stem>\b"` over every `.py`, `.sh` and `.command` in the repo
  (tests, worktrees and `backups/` excluded), then the import lines read by hand
- scheduled runs: the 41 `~/.claude/scheduled-tasks/*/SKILL.md` and the 20 `~/Library/LaunchAgents/*.plist`
- skills and agents: `.claude/skills/*`, `.claude/agents/*`, parent `.claude/`, `CLAUDE.md`
- last run: newest output file the script writes, or the newest report in `docs/reports/`

Rules applied:
- anything that feeds the stats, the Release Manager or the electronic catalogue is NOT dead
  (section C lists what stays for that reason)
- engagement automation (`scene_intelligence/ig_*`, `sc_*`, dispatcher, close_loops) is owned by the
  IG and SC chats: section B is information for those owners, never a candidate
- REVIEW = I am not sure; the row needs a look before the move, not just a yes

## Headline

| | Files | Lines |
|---|---|---|
| Candidate code (section A) | 43 `.py` + 2 launchers (45 rows) | 12,521 |
| Tests that move with it | 11 | 654 |
| Rows marked REVIEW | 9 | |
| Owned by IG/SC chats, listed only (section B) | 14 | 3,471 |
| Outside git, note only (section D) | 12 | 1,125 |

Proposed layout: `archive/<group>/` inside the repo, moved with `git mv` so history stays.
Tests go to `archive/<group>/tests/` so pytest (which collects `tests/` only) stops running them.
One `archive/README.md` names the date, this file and the undo command.

## A. Candidates

### A1. SI discovery and enrichment (code-map group 4) -> `archive/si-discovery/`

Why as a group: these built the industry contact DB from DJ sets, Resident Advisor, Discogs,
Spotify and label sites. The si-audit of 2026-11-03 found the last enrichment on 2026-04-28.
Direct IG reads were retired on 2026-09-14 (HikerAPI since). The data file they wrote
(`enriched_contacts.json`) stays where it is; it is live and read by the IG queue, the contact
index, the follow flags and the RM. Only the scripts move.

| Path | Lines | Last commit | Last run evidence | Imported by | Why candidate | Destination | REVIEW |
|---|---|---|---|---|---|---|---|
| `scene_intelligence/discover_contacts.py` | 864 | 2026-04-07 | none; `raw_contacts.json` 2026-03-03 | nothing | DJ-set discovery, no run since spring | `archive/si-discovery/` | |
| `scene_intelligence/extract_contacts.py` | 916 | 2026-04-07 | `raw_contacts.json` 2026-03-03 | A1 siblings, `push_to_sheets` (A2), `promo_dj_shortlist` (A4), `ig_import_manual_2026-06-03` (B) | parser for the discovery run | `archive/si-discovery/` | moves only together with A2 and A4 |
| `scene_intelligence/extract_ra.py` | 295 | 2026-04-07 | `ra_contacts.json` does not exist | `extract_contacts`, `promo_dj_shortlist` | RA scraper, DJ world | `archive/si-discovery/` | |
| `scene_intelligence/extract_rekordbox.py` | 441 | 2026-06-14 | none | nothing | rekordbox export reader, DJ world | `archive/si-discovery/` | |
| `scene_intelligence/enrich_contacts.py` | 366 | 2026-07-05 | si-audit: last enrichment 2026-04-28 | A1 siblings only | enrichment driver | `archive/si-discovery/` | |
| `scene_intelligence/enrich_soundcloud.py` | 539 | 2026-09-01 | no `sc_enrich_log_*` file exists | `discover_curators` (A3), `run_sc_enrich.command` | SC profile enrichment, 100 reads/hour cap makes a 750-profile pass impractical | `archive/si-discovery/` | REVIEW: newest commit in the group (09-01); ask the SC chat if it still wants this path |
| `scene_intelligence/enrich_spotify.py` | 421 | 2026-04-07 | none | `discover_contacts`, `discover_curators` | Spotify enrichment | `archive/si-discovery/` | |
| `scene_intelligence/enrich_urls.py` | 627 | 2026-04-07 | none | nothing | website and link enrichment | `archive/si-discovery/` | |
| `scene_intelligence/enrich_youtube.py` | 665 | 2026-04-07 | none | `discover_contacts` | YouTube enrichment | `archive/si-discovery/` | |
| `scene_intelligence/re_enrich_discogs.py` | 351 | 2026-04-07 | none | nothing | Discogs re-enrichment | `archive/si-discovery/` | |
| `scene_intelligence/fetch_youtube_subs.py` | 232 | 2026-04-07 | `subscriptions.csv` does not exist | nothing | YouTube subscriptions import | `archive/si-discovery/` | |
| `scene_intelligence/update_scores.py` | 61 | 2026-04-07 | none | nothing | contact score refresh for the old pipeline | `archive/si-discovery/` | |
| `scene_intelligence/classify_subtypes.py` | 444 | 2026-07-05 | none | nothing | contact subtype classifier | `archive/si-discovery/` | |
| `scene_intelligence/scrape_label_emails.py` | 169 | 2026-04-07 | none | nothing | label email scraper (label demo waves superseded) | `archive/si-discovery/` | |
| `scene_intelligence/scene_plan_recency_filter.py` | 118 | 2026-06-26 | none | nothing | one-off filter from June | `archive/si-discovery/` | |

Tests: none (0 of 15 files has a test).
Also moves: `run_sc_enrich.command` (root launcher for `enrich_soundcloud`).
Mentions to update after a move: local skills `.claude/skills/discover/SKILL.md` and
`.claude/skills/enrich/SKILL.md` (git-ignored, on this Mac only).
Stays: `scene_intelligence/utils.py` (imported by `webapp.py` and `email_outreach.py`).

### A2. Google Sheet push (group 5) -> `archive/si-sheet/`

| Path | Lines | Last commit | Last run evidence | Imported by | Why candidate | Destination | REVIEW |
|---|---|---|---|---|---|---|---|
| `scene_intelligence/push_to_sheets.py` | 1,369 | 2026-07-19 | `sheet_push_snapshot.json` 2026-09-01 | `sync.sh`, `runsync`, `discover_contacts`, `classify_subtypes` (both A1) | last push two months ago; the 11-03 si-audit proposes dropping ~45 dead sheet columns instead of keeping the pusher | `archive/si-sheet/` | REVIEW: the master sheet is still shared invite-only; Amir decides whether the sheet stays a view of SI at all |
| `sync.sh` | 2 | 2026-06-14 | same | - | launcher for the above | `archive/si-sheet/` | |
| `runsync` | 2 | 2026-06-14 | same | - | launcher for the above | `archive/si-sheet/` | |

Tests: `tests/test_sheets_sync_safety.py` (155 lines) moves with it.
Mentions to update: local skill `.claude/skills/sync/SKILL.md`; memory `si-sheet-sharing-and-push`.

### A3. Spotify curator pipeline (group 6) -> `archive/curators/`

| Path | Lines | Last commit | Last run evidence | Imported by | Why candidate | Destination | REVIEW |
|---|---|---|---|---|---|---|---|
| `scene_intelligence/discover_curators.py` | 539 | 2026-06-09 | `playlist_curator_targets.json` 2026-06-15 | A3 siblings | curator discovery | `archive/curators/` | REVIEW: ticket R-03 (curator list) is `waiting`, on hold since 10-01, not closed |
| `scene_intelligence/curator_config.py` | 65 | 2026-07-05 | same | `discover_curators` | config for the above | `archive/curators/` | same |
| `scene_intelligence/curator_enrich.py` | 127 | 2026-06-09 | same | `curator_extract_routes` | contact routes for curators | `archive/curators/` | same |
| `scene_intelligence/curator_extract_routes.py` | 77 | 2026-07-05 | same | nothing | second pass on playlist descriptions | `archive/curators/` | same |
| `scene_intelligence/curator_check_adds.py` | 99 | 2026-06-10 | none | nothing | checks playlist adds after a pitch | `archive/curators/` | same |
| `scene_intelligence/curator_pitch_sheet.py` | 44 | 2026-06-09 | none | nothing | pitch sheet export | `archive/curators/` | same |

Tests (5, 260 lines): `test_discover_curators.py`, `test_curator_config.py`, `test_curator_enrich.py`,
`test_curator_check_adds.py`, `test_curator_pitch_sheet.py`.
Mentions to update (tracked): `.claude/agents/promotion-expert.md`, `.claude/skills/promo/SKILL.md`.
Data stays: `scene_intelligence/playlist_curator_targets.json`.

### A4. Promo shortlists and release health (group 7) -> `archive/promo-electronic/`

| Path | Lines | Last commit | Last run evidence | Imported by | Why candidate | Destination | REVIEW |
|---|---|---|---|---|---|---|---|
| `scene_intelligence/promo_dj_shortlist.py` | 107 | 2026-07-05 | `dj_promo_targets.json` changed 2026-10-10 | `promo_label_shortlist`, `promo_press_shortlist` | DJ shortlist for the electronic drops | `archive/promo-electronic/` | REVIEW: only this script and `release_weekly_health` write that file, so one of them ran on 10-10 or the file was edited by hand |
| `scene_intelligence/promo_label_shortlist.py` | 109 | 2026-07-05 | `label_tiers.json` 2026-09-01 | nothing | label demo waves (superseded, fixlist rows 20-22) | `archive/promo-electronic/` | |
| `scene_intelligence/promo_press_shortlist.py` | 152 | 2026-07-05 | none | nothing | press shortlist | `archive/promo-electronic/` | |
| `scene_intelligence/release_status.py` | 105 | 2026-06-03 | none | `release_weekly_health` | release stage helper | `archive/promo-electronic/` | |
| `scene_intelligence/release_weekly_health.py` | 246 | 2026-07-19 | `docs/reports/release-health-20260805.md` | nothing (`storage.py` names it in a docstring only) | weekly release health, last report 2026-08-05 | `archive/promo-electronic/` | |

Tests (5, 239 lines): `test_promo_dj_shortlist.py`, `test_promo_label_shortlist.py`,
`test_promo_press_shortlist.py`, `test_release_status.py`, `test_release_health_backup_skip.py`.
Mentions to update: `.claude/agents/promotion-expert.md` (tracked), local `.claude/skills/release/SKILL.md`,
`.claude/skills/promo/SKILL.md` (tracked).
Data stays: `dj_promo_targets.json`, `label_tiers.json`, `promotion_log.json` (read by RM `/promotion`).

### A5. Release Manager leftovers (group 9a) -> `archive/rm-cli/`

| Path | Lines | Last commit | Last run evidence | Imported by | Why candidate | Destination | REVIEW |
|---|---|---|---|---|---|---|---|
| `release_manager/cli.py` | 715 | 2026-09-20 | none; full-audit 2026-07-04 found it unrunnable (bare imports collide with the package) | nothing; no doc names it (CLAUDE.md documents `python -m release_manager.webapp`) | terminal front end duplicated by the web UI | `archive/rm-cli/` | |

Tests: none.
Not candidates from this group (see C): `reconcile.py`, `models.py`, `display.py` (all imported by live code),
`email_outreach.py` and `contact_bridge.py` (imported by `webapp.py`; tied to the `/promotion` and `/engagement` page decision in the page map).

### A6. Root tools nobody calls (groups 10, 11) -> `archive/root-tools/`

| Path | Lines | Last commit | Last run evidence | Imported by | Why candidate | Destination | REVIEW |
|---|---|---|---|---|---|---|---|
| `description_scorer.py` | 284 | 2026-06-14 | none | nothing; no skill, no doc | scores a bio before posting; `caption_check` + the SEO checks in RM do this now | `archive/root-tools/` | |
| `letter_slides.py` | 240 | 2026-09-21 | none | nothing | renders "letter for listeners" slides | `archive/root-tools/` | REVIEW: `docs/brand/formats.md`, `frame.md` and `letter-for-listeners.md` still name it as the tool for that format, and a control-panel ticket mentions it. Amir says whether the letter format is alive |

Tests: none.

### A7. Logo scripts stored twice (group 14) -> `archive/look02-duplicates/`

13 scripts exist as two byte-identical copies (md5 checked). `references/look02/scripts/` was committed
on 2026-09-25 ("every draft kept, with an index and the runnable scripts"). The second copy
(top level, `moon/`, `v2/`, `v3/`) came in on 2026-11-03 inside a mixed commit from another session.
The 27 render images sit next to the second copy. Logo work is parked.

| Path (proposed to move) | Lines | Last commit | Identical twin (stays) | Destination | REVIEW |
|---|---|---|---|---|---|
| `references/look02/scripts/all_picks.py` | 75 | 2026-09-25 | `references/look02/all_picks.py` | `archive/look02-duplicates/` | REVIEW: which copy goes; I propose `scripts/` goes because the images sit beside the other copy, but the 09-25 commit calls `scripts/` the runnable set |
| `references/look02/scripts/families.py` | 45 | 2026-09-25 | `references/look02/families.py` | same | same |
| `references/look02/scripts/logo_sketches.py` | 197 | 2026-09-25 | `references/look02/logo_sketches.py` | same | same |
| `references/look02/scripts/logo_round_b.py` | 165 | 2026-09-25 | `references/look02/logo_round_b.py` | same | same |
| `references/look02/scripts/logo_round_c.py` | 159 | 2026-09-25 | `references/look02/logo_round_c.py` | same | same |
| `references/look02/scripts/logo_round_d.py` | 145 | 2026-09-25 | `references/look02/logo_round_d.py` | same | same |
| `references/look02/scripts/logo_round_e.py` | 132 | 2026-09-25 | `references/look02/logo_round_e.py` | same | same |
| `references/look02/scripts/logo_round_f.py` | 124 | 2026-09-25 | `references/look02/logo_round_f.py` | same | same |
| `references/look02/scripts/logo_round_g.py` | 129 | 2026-09-25 | `references/look02/logo_round_g.py` | same | same |
| `references/look02/scripts/moon.py` | 133 | 2026-09-25 | `references/look02/moon/moon.py` | same | same |
| `references/look02/scripts/compare_v2.py` | 45 | 2026-09-25 | `references/look02/v2/compare_v2.py` | same | same |
| `references/look02/scripts/logo_v2.py` | 216 | 2026-09-25 | `references/look02/v2/logo_v2.py` | same | same |
| `references/look02/scripts/logo_v3.py` | 169 | 2026-09-25 | `references/look02/v3/logo_v3.py` | same | same |

Tests: none. Also in `scripts/`: `pull/` with 3 reel jpgs (not duplicated, stays).

## B. Owned by the IG and SC chats: listed only, no destination

The code map called these DORMANT. The grep today shows several are reachable from live code or
a scheduled task, so the owners should read this before anyone touches them. Not candidates.

| Path | Lines | Last commit | What the grep found today |
|---|---|---|---|
| `scene_intelligence/ig_enrich_instagram.py` | 496 | 2026-08-31 | no importer, no task; named in `.claude/agents/ig-expert.md`; direct IG reads retired 09-14 |
| `scene_intelligence/ig_enrich_helper.py` | 85 | 2026-06-14 | nothing |
| `scene_intelligence/ig_followback_checker.py` | 624 | 2026-09-03 | LIVE: imported by `ig_live_driver`, `ig_audit_queue_freshness`, `ig_tracker_stats`, `ig_reconcile_followings`, `ig_backfill_reciprocity`; named by 5 scheduled tasks |
| `scene_intelligence/ig_reconcile_followings.py` | 283 | 2026-09-03 | in the job list of `ig_daily_ledger.py` (line 59) |
| `scene_intelligence/ig_backfill_reciprocity.py` | 294 | 2026-09-03 | in the job list of `ig_daily_ledger.py`; task `ig-reciprocity-backfill-saturday` |
| `scene_intelligence/ig_show_automation_follows.py` | 127 | 2026-05-11 | nothing |
| `scene_intelligence/ig_build_voice_profile.py` | 145 | 2026-06-02 | its output `ig_voice_profile.json` changed 2026-11-03, so it ran this week; test + local `ig` skill |
| `scene_intelligence/ig_import_manual_2026-06-03.py` | 120 | 2026-06-14 | one-off import; imports `extract_contacts` (A1), so an A1 move breaks it |
| `scene_intelligence/sc_unfollow_cleanup.py` | 1 | 2026-06-14 | one comment line: "Deprecated" |
| `scene_intelligence/check_sc_follows.py` | 268 | 2026-09-01 | test `test_sc_unfollow_lane_sc02.py` only |
| `scene_intelligence/sc_build_browser_session.py` | 83 | 2026-06-14 | nothing |
| `scene_intelligence/sc_log_manual.py` | 469 | 2026-09-01 | named in a comment in `sc_engagement.py`; test `test_sc_log_manual_sc03.py` |
| `scene_intelligence/sc_extract_chrome_cookies.py` | 307 | 2026-07-05 | `sc_engagement.py` tells the operator to re-run it when cookies die: operational |
| `scene_intelligence/sc_browser_likes.py` | 269 | 2026-06-14 | LIVE: imported by `sc_engagement.py` |

## C. Looked at, stays (not dead by the rules)

| Path | Why it stays |
|---|---|
| `scene_intelligence/sc_release_stats.py` + task `sc-weekly-release-stats` (Fri 18:00) | feeds `releases/*.json` SC stats for The Deceiver and Farewell; electronic catalogue stats stay. Separate question for Amir: should the Friday task also cover Pinocchio / Half the Night? |
| `release_manager/email_outreach.py` (713), `contact_bridge.py` (314) | imported by `webapp.py` for `/promotion` and `/engagement`; `email_send_state.json` never existed, so no email was ever sent. Moves only if the page map drops `/promotion` |
| `release_manager/reconcile.py`, `models.py`, `display.py`, `storage.py`, `paths.py` | imported by live RM and stats code |
| `scene_intelligence/utils.py` | imported by `webapp.py`, `email_outreach.py` |
| `scene_intelligence/sc_weekly_health.py`, `sc_buy_links.py`, `si_*`, `contact_index.py`, `bandcamp_supporter_match.py` | run by tasks or imported by checklist/dispatcher |
| `stats/*` (14 files) | launchd 08:45 sync, token refresh, S4A Monday read, digest 20:00 |
| `gap_radar/*` | reports up to 11-05 |
| root tools `artwork_resizer`, `video_resizer`, `image_generator`, `edit_recipe`, `shoot_*`, `print_looks`, `shadow_archive`, `fonts_library`, `caption_check`, `copy_clean`, `metadata_utils`, `bandcamp_links`, `fetch_text`, `hygiene_check` | imported by RM or named in live docs; `fonts_library` has no importer but was committed 11-03 |
| `docs/brand/kit/scripts/*` (9) | brand kit; `frame_tokens.py` is loaded by `webapp.py` |
| `plans/outreach-page/*.py` (10, 1,416 lines) | booking batches 11-02/03, live work |
| `deploy/retired/*` | already a retired folder (2 plists, README) |
| `plans/cleanup/*.py` (untracked) | 11-05 trash job and its undo script; keep until that job is settled |

## D. Outside git: note only, nothing to `git mv`

| Path | Files / lines | State | Suggestion |
|---|---|---|---|
| `../youtube/tools/*.py` | 8 / 819 | no run since `youtube/stats` 10-13; YouTube OAuth expired ~10-28, so `yt_apply`/`yt_release` cannot run; local `release` and `release-prep` skills name `yt_release.py` | bring the code (not the pngs) into the repo first (code-map change 6), then decide |
| `../videos/blank-wave-130-story/*.py` | 4 / 306 | one-off story renders for Guest Mix 130, closed 10-13 | leave with the video folder |
| `music-tools/` (untracked, 215 MB) | 22 / 2,200 | active side tools, not dead; two duplicates inside (`drumrack_tool` v1/v2, `dupes/scan_dupes.py` vs `plans/cleanup/scan_dupes.py`) | not part of this list |

## E. Move order and checks

1. Amir ticks rows (or whole groups). REVIEW rows need an answer, not a tick.
2. `mkdir archive && git mv` per group, tests into `archive/<group>/tests/`, write `archive/README.md`.
3. `pytest -q -x` must stay at 1,125 passed (1,136 today minus the 11 moved test files' cases; the exact
   number comes from the run).
4. `python -m release_manager.webapp` starts and `/`, `/stats`, `/engagement`, `/promotion` load.
5. Update the tracked mentions: `.claude/agents/promotion-expert.md`, `.claude/skills/promo/SKILL.md`.
   Local skills (`discover`, `enrich`, `sync`, `release`) are git-ignored; edit on this Mac.
6. One commit: `⚙️ System 71: park dead code (list of 2026-11-05)`.
7. IG/SC rows (section B) are never part of this commit.

## F. Undo

Before the commit (moves staged but not committed):

```bash
git reset --hard HEAD
```

After the commit, one command puts every file back where it was:

```bash
git revert --no-edit $(git log -1 --format=%H --grep="System 71: park dead code")
```

Equivalent by hand (reverse of every `git mv` in section A; run from the repo root):

```bash
for p in discover_contacts extract_contacts extract_ra extract_rekordbox enrich_contacts enrich_soundcloud enrich_spotify enrich_urls enrich_youtube re_enrich_discogs fetch_youtube_subs update_scores classify_subtypes scrape_label_emails scene_plan_recency_filter; do git mv "archive/si-discovery/$p.py" "scene_intelligence/$p.py"; done
git mv archive/si-discovery/run_sc_enrich.command run_sc_enrich.command
git mv archive/si-sheet/push_to_sheets.py scene_intelligence/push_to_sheets.py
git mv archive/si-sheet/sync.sh sync.sh
git mv archive/si-sheet/runsync runsync
git mv archive/si-sheet/tests/test_sheets_sync_safety.py tests/test_sheets_sync_safety.py
for p in discover_curators curator_config curator_enrich curator_extract_routes curator_check_adds curator_pitch_sheet; do git mv "archive/curators/$p.py" "scene_intelligence/$p.py"; done
for t in test_discover_curators test_curator_config test_curator_enrich test_curator_check_adds test_curator_pitch_sheet; do git mv "archive/curators/tests/$t.py" "tests/$t.py"; done
for p in promo_dj_shortlist promo_label_shortlist promo_press_shortlist release_status release_weekly_health; do git mv "archive/promo-electronic/$p.py" "scene_intelligence/$p.py"; done
for t in test_promo_dj_shortlist test_promo_label_shortlist test_promo_press_shortlist test_release_status test_release_health_backup_skip; do git mv "archive/promo-electronic/tests/$t.py" "tests/$t.py"; done
git mv archive/rm-cli/cli.py release_manager/cli.py
git mv archive/root-tools/description_scorer.py description_scorer.py
git mv archive/root-tools/letter_slides.py letter_slides.py
for p in all_picks families logo_sketches logo_round_b logo_round_c logo_round_d logo_round_e logo_round_f logo_round_g moon compare_v2 logo_v2 logo_v3; do git mv "archive/look02-duplicates/$p.py" "references/look02/scripts/$p.py"; done
git rm -q archive/README.md && rmdir -p archive 2>/dev/null; true
```
