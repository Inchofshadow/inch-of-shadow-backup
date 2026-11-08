# System 68 review gate before the main move (run 2026-11-07, finished 2026-11-08)

**System 68 ultra = 19 blocking, 528 non-blocking, 26 not verified (11 of them possibly blocking)**

## What this is

- Ticket System 68, decision D16: move `main` onto `score-board` (317 commits, pure fast-forward, checked with `git merge-tree`).
- Amir's standard is `/code-review ultra` before any merge to main. It refused this branch: its limits are 500 files and 8,000 changed lines, the branch diff is 1,001 files and 426,000 lines (code alone 276 files, 46,000 lines). No setting changes that cap.
- Amir chose instead (2026-11-07, this chat) a multi-agent review run in the Inchofshadowcode chat with Ultracode on. This file is its result. It is not the ultra product.
- Method: one agent mapped which code is live (launchd plists, the Flask webapp and its imports, skills, scheduled tasks: 127 live paths). Then two reviewers per batch of changed code files (lenses: correctness, security). Every finding rated medium or higher in a bug category (correctness, security, robustness) went to three independent refuters (reproduce, context and liveness, severity); a finding survives with two or more keep votes. Low, style, dead-code and test notes were not refuted and are listed as non-blocking, unverified.
- Scope: the 231 code files (`.py .html .js .css .sh`) changed between main and score-board that still exist. Reviewers also read 180 or so imported or neighbouring files, so findings outside the 231 appear too. Data files (JSON, Markdown, CSV) were not reviewed. 79 of the 231 were missed by the first pass (my batch list was wrong) and got a second pass with the same method. The second pass hit the usage cap during its refute stage; those findings are listed separately as not verified.
- Blocking rule (from the ticket brief): a correctness or security bug in live code, severity medium or higher. Everything else is non-blocking. Robustness findings (crash on odd input, no guard) are non-blocking. Nothing was fixed; fixes are decided in the System chat.
- The 'live' flag is the refuters' majority view of whether the code runs daily (launchd, webapp, skill, scheduled task) or is a one-off script, draft or test.

## Blocking (19)

### High (1)

- `release_manager/playground.py:292` Kept layouts are silently truncated to 40; the live file is at 38, so the next keeps destroy Amir's oldest picks (kept 3/3, live)
  layouts_toggle appends the new keep and slices to the last 40 with no warning, no backup and no error to the page. plans/playground-wall/pinocchio-single-layouts.json currently holds 38 kept layouts (Half the Night, the live release), so the 41st Keep click drops keep #1 for good, the 42nd drops #2, and so on; the page shows nothing. The git history shows Amir archives these keeps by hand (commits a48f3cb, 0dea146), so they are wanted data. Because layout_snap_save names snapshots by list position (keep-%02d from n), every snap also shifts to the wrong layout once an entry is dropped from the ...

### Medium (18)

- `fetch_text.py:125` UTF-8 pages without a header charset are decoded as ISO-8859-1, producing mojibake in saved notes (kept 3/3, live)
  requests fills r.encoding with 'ISO-8859-1' for any text/* Content-Type that lacks a charset parameter (requests 2.32.5 utils.get_encoding_from_headers: `if "text" in content_type: return "ISO-8859-1"`). So the `or "utf-8"` fallback on line 125 is never reached for an HTML page, and a UTF-8 page that declares its charset only in <meta> (common on small venue/label/promoter sites) is decoded byte-for-byte as Latin-1: every non-ASCII character is corrupted ('Müller' -> 'MÃ¼ller', 'Straße' -> 'StraÃŸe'). The research tool then writes the corrupted contact names and addresses into the .md notes th...
- `gap_radar/schedule.py:152` last_run is recorded only after the whole loop, and nothing stops two runs overlapping (kept 3/3, live)
  The 5-day wait guard reads gap_radar/schedule_state.json, but that file is written once, after every profile has run. A run that is stopped or crashes after it has already paid for analyses leaves no last_run, so the next launchd run (Sun 05:00) does not wait as designed. There is also no lock file or pid check, so a manual run and the scheduled run (or two manual runs) can run the same profiles at the same time and both pay. Both already happened on 2026-11-06: the 02:50 and 03:07 runs overlapped (handover: 'Waste: about $8-10'); the 03:07 run was stopped mid-loop (docs/reports/gap-radar-laun...
- `plans/review-page/read_ticks.py:29` Ticks are imported in filename order, not in tick time order, so an older tick can overwrite a newer proposal (kept 3/3, live)
  Ticks are collected with `sorted(base.rglob("*.json"))`, i.e. ordered by the db doc id (file stem), and passed to review.import_ticks in that order. import_ticks applies them sequentially and documents 'a later valid tick replaces an earlier proposal', so the LAST tick in list order wins. The page itself shows the newest tick by `orderBy("at","asc")`. Scenario: Amir taps Approve on r-001 (doc id 'k7...'), changes his mind and taps Drop (doc id 'a2...'). The page shows 'You proposed drop'. read_ticks processes 'a2...' (drop) first, then 'k7...' (approve), so item.proposed ends as approve; `revi...
- `release_manager/checklist.py:243` migrate_checklist silently deletes every checklist item that is not in the lane template, including done history (kept 3/3, live)
  migrate_checklist rebuilds the list from generate_checklist(timeline, lane) and only copies done/done_date/notes for ids that exist in the fresh template; any other item is dropped. releases/the-deceiver-single.json (lane None) carries 25 items that are in no template (dsp_cover_swap, ig_cover_image, ig_presave_post, ig_reel_clip, ig_canvas, soundcloud_live, hypeddit_smartlink, discogs_submit, beatport_claim, web3_uploads ...) with their done state. release_detail (views/release.py 266-269) runs this migration automatically on a GET and then save_release(rel) whenever expected_ids(lane) - cl_i...
- `release_manager/outreach.py:98` Missing instagram_verified key is treated as verified, hiding the (check) flag (kept 1/1, live); same issue also at 98: Missing instagram_verified key is treated as verified, hiding the (check) flag
  The unverified flag is `not t.get("instagram_verified", True)`, so a target that has an IG handle but no `instagram_verified` key at all is shown as verified. 14 targets in booking_targets.json are in that state (Soho House Berlin, Hotel Telegraphenamt ROOT Bar, Monkey Bar, Michelberger Hotel, The Social Hub Berlin, Dorotheá, Crackers, Bar Tausend, ...) and 8 of them are in the batches, so their cards render the IG link without the "(check)" marker the template adds for unverified handles. Unknown should not default to verified: only 115 of 168 targets with an instagram field carry the key, an...
- `release_manager/review.py:67` Documented CLI form `python3 release_manager/review.py ...` cannot import release_manager (kept 3/3, live)
  review.py does not put the repo root on sys.path (unlike plans/review-page/read_ticks.py lines 18-19 and copy_pass.py). Run as a script, sys.path[0] is `<repo>/release_manager`, so `from release_manager import storage` raises ModuleNotFoundError before argparse runs. Verified: no .pth or PYTHONPATH makes the package importable (`python3 -I -c 'import release_manager'` from a neutral cwd fails). The invocation the docs give Amir and the System chat is exactly this form: plans/review-flow-schema.md lines 19, 122, 136, 145-151 (`python3 release_manager/review.py add|check|export|confirm|used|list...
- `release_manager/review.py:1002` 'Later tick replaces the earlier proposal' is by list order, not by the tick's time (kept 3/3, live)
  import_ticks overwrites item['proposed'] unconditionally for each valid tick in list order and never compares the incoming t['at'] (or ticked_at) with the existing proposal. The only caller, plans/review-page/read_ticks.py line 29, builds the list with `sorted(base.rglob('*.json'))`, i.e. ordered by ArtifactData doc id (the file stem), not by time. Scenario: Amir taps 'change: shorter' then 'approve' on the phone; the approve doc id sorts before the change doc id -> the item ends with proposed=change although his last word was approve. Then `review.py confirm <slug> r-001` without --action tak...
- `release_manager/templates/playground_layout.html:1054` Tournament bye breaks the round: first match skipped, then a crash when the bye slot is reached (kept 3/3, live)
  tPairs (line 1045) puts a lone entry LAST in the match list, but tAdvance pushes that bye winner onto r.w immediately. r.w is positional: tMatch() returns r.m[r.w.length] and the bracket marks win/lose with r.w[mi] === id. With an odd round (3, 5 or 7 unique keeps, or 6 keeps whose 3 winners make the next round), w = [bye] so tMatch() returns r.m[1] and match 0 is never played (its two keeps are drawn as 'lose'). After one pick, w.length === 2 and tMatch() returns the singleton r.m[2]; tShow then evaluates keptLabel(KEPT[mm[1]], mm[1]) with mm[1] undefined, so fromKept(undefined) throws TypeEr...
- `release_manager/templates/sc_automation.html:73` "Active follows" KPI, "to unfollow" count and the Follow Tracker table include the 931 entries already soft-unfollowed (kept 3/3, live)
  The template labels status.follow_tracker.total_active as "Active follows" and lists status.follow_tracker.entries as the tracker with a Pending/Followed back status column. get_status() (scene_intelligence/sc_engagement.py:3005-3031) fills total_active with len(follows), entries with the raw follows list and pending_unfollow with every row where not followed_back and unfollow_after <= today, never excluding no_longer_following. The tracker's own stats code (sc_engagement.py:746-757) documents that soft-unfollowed rows STAY in follows and defines active_follows = len(follows) - gone. On the li...
- `release_manager/templates/video.html:58` Frame-by-hand shape chips reuse class rz-chip, so clicking one unticks every size (kept 3/3, live)
  The four shape buttons (9:16, 4:5, 1:1, 16:9) carry class "rz-chip", the same class the preset chips use. static/resizer.js attaches its preset handler to every .rz-chip (line 199): on click it reads chip.dataset.preset, which is undefined for a shape chip, so want=[] and all=false, and it then sets b.checked=false on every templates checkbox, removes 'active' from every chip (including the shape chip that the frame handler just marked active a moment earlier) and re-runs count(). Scenario: Amir ticks the Reel set, picks 9:16 to drag a frame by hand, and his three ticked sizes silently vanish;...
- `release_manager/templates/video.html:66` Error re-renders drop the hand frames, trim, chosen source and the release list (kept 3/3, live)
  The template guards `frames_json` and `trim` with `is defined`, which hides that the two error returns in views/studio.py (581-586 'Not a video file' and 606-611 'No video selected') pass neither of them, nor posted_video, release_options or preselected_release. After either flash the page comes back with the frames input empty, trim fields empty, the source select reset and the metadata release dropdown containing only '-- Select release --' (iterating an Undefined yields nothing). Scenario: Amir drags frames for 9:16 and 16:9, sets a trim, forgets to pick a video, presses Make, gets 'No vide...
- `release_manager/views/release.py:612` track_delete renumbers tracks but not the clips block, so clip data moves to the wrong track (kept 3/3, live); same issue also at 613: track_delete renumbers tracks but not their clip-pack blocks, so clip timecodes shift to the wrong track and the last block is lost
  After popping a track the loop sets t["number"] = i + 1 for the remaining tracks, but rel["clips"]["tracks"] (keyed by track number, see clips.ensure_clips) is left untouched. Delete track 2 of 3 on a release with clips: tracks become [1, 2(old 3)]; ensure_clips then maps existing blocks by number, so the former track 3 inherits the DELETED track's TikTok start, hook bar, canvas and used_in log, and the former track 3's own clip block is silently dropped on the next save (save_release_clips / page_rows). The release page shows and the next clips edit persists wrong data with no error.
- `release_manager/views/release.py:946` Resizer reports success when process_image produced nothing (unreadable or HEIC source) (kept 3/3, live)
  artwork_resizer.process_image swallows Image.open failures and returns [] (and swallows per-export errors, appending nothing). The view then flashes "Resized 0 images." as a success and runs `open resized/`. Realistic trigger: ARTWORK_EXTENSIONS accepts .heic/.heif and the upload branch even renames Photos drops to .heic (line 862), but no HEIF plugin (pillow_heif) is installed anywhere in the project, so every HEIC source fails to open and the user is told it succeeded. Same for a truncated or non-image file with an image extension.
- `release_manager/views/words.py:176` Release slug from the JSON body reaches the filesystem unvalidated, allowing traversal reads and a live-release overwrite (kept 3/3, live)
  api_seo_copy_pick, api_seo_copy_generate (line 114) and api_seo_copy_generate_both (line 156) take `slug` straight from the request body and pass it to storage.load_release, which builds `RELEASES_DIR / f"{slug}.json"` with no character check and no containment check (storage.py:26-28, 59-63). Concrete failure: POST /api/seo-copy/pick with {"slug": "../releases/farewell-single.bak.20261106_review", "key": "spotify_pitch", "value": "x"} loads the stale backup (it exists and carries slug "farewell-single"), then save_release writes it to releases/<data["slug"]>.json = releases/farewell-single.js...
- `release_manager/views/words.py:205` Bios take the release with the largest release_date as 'latest release', including a future or placeholder-dated one (kept 3/3, live)
  api_bios_generate and api_bios_generate_both use `releases[-1]`; list_releases() sorts ascending by release_date with no filter on today's date or a released status. bio_manager._build_user_prompt turns that into 'Latest release: <title> (<type>) ... Release date: <date>' and the model writes all seven bios as though that release is out. Scenario: a planned release file with a provisional date later than today exists in releases/ (the repo today holds pinocchio-single.json, title 'Half the Night', dated 2026-11-06, while the EP's date is still open per the project notes); every generated bio t...
- `scene_intelligence/sc_engagement.py:3026` get_status() hands the SC status page every tracker entry ever followed as an "active follow", unfollowed ones included (kept 3/3, live)
  The follow tracker keeps unfollowed entries in `follows` as soft-flagged rows (`no_longer_following` / `unfollowed_at`, see lines 746-756 and 807-820), but get_status() builds the dashboard summary from the raw list: `total_active = len(follows)`, `entries = follows`, and `pending_unfollow` filters only on `followed_back` and `unfollow_after`. On the live file (1328 entries, 931 no_longer_following, tracker stats say active_follows 397) the /sc-automation page shows "Active follows 1328", "459 to unfollow" and a Follow Tracker table whose first 50 rows are the oldest entries (followed_at 2026-...
- `stats/daily_brief.py:106` _flagged raises false 🔴 problems for 'Challenge: none' style lines in the SC session report (kept 3/3, live)
  _flagged only suppresses a detection word when 'no' appears in the fragment BEFORE the word in the same sentence (split on '[.;:]\s'). The real SC reports write the closing checklist as 'Challenge: none. Throttle: none. Popup / takeover: none.' The fragment before 'Challenge' is empty (it follows '. ') and 'none' does not match '\bno\b', so 'challenge' and 'takeover' are flagged. This already happened live: docs/reports/daily-brief-2026-11-06.md shows '🔴 Problems / SC challenge · scene_intelligence/sc_session_report_20261106.md / SC takeover · ...' and stats_snapshots/daily_brief_state.json st...
- `stats/daily_brief.py:285` write_proposals finds the section by plain substring, so a prose mention of the heading sends proposals into the wrong section (kept 3/3, live)
  write_proposals locates the section with text.index(HANDOVER_SECTION) (a bare substring search for '## Proposed from the brief'), then looks for the next '^## ' heading after it. In the live plans/handovers/system/system.md the phrase is quoted in prose inside the '## Daily brief' section (line 83: 'one proposed ticket line under "## Proposed from the brief" below') BEFORE the real heading on line 94. index() hits the prose mention, the '^## ' search then finds the real heading, and the proposals are inserted just above it, i.e. at the END of the '## Daily brief' section. That is exactly where...

## Not verified: refuters stopped at the usage limit (26)

Reported by the second-pass reviewers on 2026-11-08; the three refuters per finding could not run because the Fable usage cap was reached. Treat these as raw reports. The correctness and security ones in live code would count as blocking if they hold.

### Possibly blocking: correctness or security (11)

- `scene_intelligence/ig_merge_session_log.py:621` Queue sync raises KeyError on a keep-pending reach skip (button_missing_after_reload) (high, correctness)
  update_queue_from_events() initialises `counts` with nine keys (lines 527-530) but line 621 increments `counts["queue_skip_render_bug_kept_pending"]`, a key that is never created, so a plain dict raises KeyError. The branch fires for any `ig_skip` event with track `reach` whose reason starts with `button_missing` on a handle that is in ig_target_list.json. That reason is the SOP's own vocabulary: docs/cowork-task-ig.md line 270 tells the daily ig-engagement task to "log reason=button_missing_after_reload, move on", and real session logs carry reach skips in exactly this shape (e.g. backups/ig_...
- `stats/ig_followback.py:36` cohorts() drops every unfollowed_history entry written by the live unfollow code (key followed_at vs followed_date) (high, correctness)
  cohorts() reads the follow date of history entries only from the key 'followed_date', but two of the three writers that move an entry from active_follows into unfollowed_history store it under 'followed_at': scene_intelligence/ig_engagement.py:2262-2267 (the engine's unfollow) and scene_intelligence/ig_reconcile_followings.py:229-232 (drift reconciliation); only ig_merge_session_log.py:470-473 uses 'followed_date'. In the live tracker right now 39 history entries carry 'followed_at' and no 'followed_date' (dates such as 2026-05-01, 2026-05-06, 2026-05-13), so the `if not day: continue` branch ...
- `references/look02/moon/moon.py:5` moon.py imports siblings that live one folder up, so it cannot run from its own folder, and writes its sheets elsewhere (medium, correctness)
  moon.py sits in references/look02/moon/ but imports logo_sketches, logo_round_d and logo_round_b as top-level modules; those files are in references/look02/ (and archive/look02-duplicates/), not in moon/. `python3 moon.py` from moon/ (or `python3 moon/moon.py`) fails with ModuleNotFoundError: No module named 'logo_sketches'. Even with PYTHONPATH pointing at the parent, `S` is logo_sketches' own folder (S = Path(__file__).parent in logo_sketches.py), so main() saves moon_engraved.jpg / moon_in_name.jpg to references/look02/, not to moon/ where INDEX.md lists them. The script in its current loca...
- `release_manager/outreach.py:152` Outreach page hot-links contact images from 25 third-party hosts on every page view (medium, security)
  build_view passes profile.image through unfiltered and outreach.html renders it as <img src="{{ c.image }}">. The live data (plans/outreach-batches.json) holds 42 such URLs on hosts like static.ra.co, privatclub-berlin.de, crackersberlin.com, tausendberlin.com, 25hours-hotels.com, i1.sndcdn.com. Every load of /outreach makes Amir's browser fetch from all of them, sending his IP and (no Referrer-Policy is set anywhere in the app) a Referer of http://127.0.0.1:5001/outreach to the booking targets' own web servers. This is an outbound request to third parties the project rule forbids without expl...
- `release_manager/tickets.py:123` validate rejects a done ticket whose bucket or who is an empty string (medium, correctness)
  The shape rule (module docstring, SHAPE_FIELDS_OPEN, _missing) says done tickets need no bucket/who and treats '' as absent, and test_card_priority_is_derived_from_bucket builds ticket(id='R-03', status='done', bucket='') as a legitimate card (test_tickets.py:115). But the bucket/who checks run on key presence, so a done ticket with "bucket": "" (the natural edit when closing a ticket) gets 'bad bucket' and load_tickets raises TicketsError; the /tickets route then answers 500 (views/work.py _work_page: 500 when tickets_error). The seeds currently avoid this only because done tickets keep a val...
- `scene_intelligence/contact_index.py:35` Own-lists glob ignores the folder si_follow_flags now writes to, so follow annotations go stale. (medium, correctness)
  contact_index only globs plans/outreach-page/dj07-own-lists-*.json for the followers/following sets. si_follow_flags.py (run weekly by the live ig_dispatcher with --fetch --apply) writes its fresh lists to scene_intelligence/own_lists/own-lists-DATE.json (LISTS_DIR = SI_DIR / 'own_lists', line 141 'out = LISTS_DIR / f"own-lists-{today.isoformat()}.json"') and its own newest_lists() searches both folders. Once the dispatcher's first fetch lands, every contact_index run keeps annotating follows_amir / amir_follows / warm_outreach from the 2026-11-03 dj07 file forever, and the 'sources' field in ...
- `scene_intelligence/ig_health_check.py:128` Reciprocator-churn check reads `follow_back` while part of the history carries `followed_back`. (medium, correctness)
  Check 5 counts churned reciprocators with x.get('follow_back') is True. In the current ig_follow_tracker.json the unfollowed_history entries carry both spellings: 48 rows have follow_back=True and 3 rows (arale.music, degherlband, labeldiskoduro) have only followed_back=True with follow_back absent. Those 3 churned reciprocators are silently excluded from the warning, which is exactly the kind of silent miss this script exists to catch. The active_follows branch two lines above uses the other key (followed_back).
- `scene_intelligence/si_cleanup.py:305` Cleanup plan with contact names, IG handles and outreach status is written to docs/reports/, which the GitHub backup snapshot ships in plain text (medium, security)
  `plan` writes PLAN_MD = docs/reports/si-cleanup-plan-2026-11-03.md containing every booking/outreach contact's name, IG handle, city, source and the merge groups. docs/reports/ is outside every LOCKED prefix in plans/cleanup/backup_snapshot.py (data/, plans/outreach-page/, scene_intelligence/), and the snapshot's `has_people_data` heuristic only counts the markers `"username"`, `"handle"`, `"user_id"`, `instagram.com/`, `soundcloud.com/` or emails; the markdown table carries bare handles (e.g. `sohohouse`, `telegraphenamt.berlin`), so it scores 0 markers, 0 emails and is classified PLAIN. Conf...
- `scene_intelligence/si_follow_flags.py:77` Coverage guard is skipped when the profile count is missing, so a short or empty 'complete' list can flip every contact to not-following (medium, correctness)
  usable() only checks `got < 97% of want` when `want` is truthy. normalise_profile() gives follower_count/following_count = None when the provider omits them (_int(None) -> None), and `int(prof.get(count_key) or 0)` turns that into 0, disabling the guard. At the same time pull() marks a list complete on `not page` (a 404 chunk returns None -> _unpack_chunk -> ([], None)), so a first-page 404 yields followers=[] with followers_complete=True. With --apply (the dispatcher's mode) apply() then sets ig_i_follow/ig_follows_me/ig_mutual = False on all 551 contacts with a handle, exactly the mass flip ...
- `scene_intelligence/si_follow_flags.py:141` A failed or incomplete --fetch still writes a dated own-lists file, which blocks the dispatcher's weekly retry (medium, correctness)
  fetch_lists() writes own-lists-<today>.json unconditionally, also when the pull hit the FETCH_BUDGET (complete=False), when a ProviderError aborted one side (res['error'] set, 'followers'/'following' key missing), or when a 404 page ended a list early. main() then correctly refuses to apply it (usable() -> return 2), but newest_lists()/lists_age_days() pick that file by its stem date, so the dispatcher (ig_dispatcher._provider_si_upkeep, line 444: `if (age is None or age >= FOLLOW_LISTS_MAX_AGE_DAYS) ...`) sees age 0 and does not retry for 7 days; the same-script ledger rule already blocks a s...
- `tools/prune_bak.py:32` Glob also prunes the manual IG tracker migration backups, contrary to the stated premise (medium, correctness)
  The docstring justifies the rule with "Nothing reads these files; only sc_weekly_health.py writes them", but `folder.glob("*.bak.*")` matches every `*.bak.*` in scene_intelligence/, and the folder currently holds `ig_follow_tracker.json.bak.20261104_pre_provider_recip` (mtime Nov 2) and `ig_follow_tracker.json.bak.20261105_pre_justbedeadon` (mtime Nov 5), mode 0600, hand-made restore points for the IG tracker migrations (dict with active_follows/unfollowed_history). They are not sc_weekly_health output. On the next monthly run after ~2026-11-16/19 they will be moved to the Trash under the rule...

### Robustness, non-blocking if it holds (15)

- `gap_radar/gap_radar.py:294` HikerAPI ledger claim is written before the Provider is known to be usable (medium)
- `plans/decisions_writeback.py:215` Any .md file under the repo root is accepted as a write target, not only handovers (medium)
- `plans/decisions_writeback.py:242` A second run on the same day overwrites the backup with the already-changed file (medium)
- `release_manager/outreach.py:150` Unvalidated profile, categories and notes shapes crash build_view with a bare 500 instead of the validation error page (medium)
- `release_manager/outreach.py:206` set_try does an unlocked read-modify-write of the batch file; concurrent ticks lose one (medium)
- `release_manager/outreach.py:216` set_try rewrites the whole batch file from memory, silently dropping concurrent edits, with no backup (medium)
- `scene_intelligence/bandcamp_supporter_match.py:280` `--out` outside the repo (or a relative path) crashes after the file is written. (medium)
- `scene_intelligence/ig_reciprocity_from_lists.py:84` Missing or malformed `fetched` in the list file raises an uncaught ValueError in a live dispatcher job. (medium)
- `scene_intelligence/si_cleanup.py:275` `apply` detects a stale plan by record count only, so merges can hit the wrong records. (medium)
- `scene_intelligence/si_cleanup.py:312` Single fixed backup path is overwritten by every apply, and undo overwrites SI without saving the current state (medium)
- `scene_intelligence/si_follow_flags.py:142` A failed or incomplete --fetch still writes an own-lists file, which then counts as fresh for a week. (medium)
- `scene_intelligence/si_follow_flags.py:164` --undo restores a single-slot backup blindly and discards every later write to enriched_contacts.json. (medium)
- `tests/test_sc_status_page.py:18` Status-page test runs get_status() against the real tracker and log files and can create the real sc_follow_tracker.json (medium)
- `tools/prune_bak.py:68` Files are moved before any record is written; a mid-loop exception leaves moved files with no undo and no report; same issue also at 70: A second run on the same day overwrites the undo script and listing with an empty one; 71: A second --apply run on the same day overwrites the undo script, even with nothing to move (medium)
- `tools/prune_bak.py:74` A later same-day run replaces the 'applied' report with a '0 file(s) dry run' listing (medium)

## Non-blocking, verified (131)

Survived the refuters but either not live code, or robustness rather than a wrong result, or low after re-rating.

### Medium (22)

- `gap_radar/crowding.py:143` check() loses every finished verdict when one gap hits a non-ClaudeError exception (kept 3/3, live)
  The per-gap loop only catches claude_api.ClaudeError. An anthropic.APIError (429 RateLimitError, 529 overloaded, APIConnectionError/timeout from client.messages.create) or an AttributeError from vet() when the model returns `competitors` as a list of strings instead of dicts (line 96 `c.get(...)`) propagates out of check(); the verdicts of all gaps already checked in this report are only returned at the end (line 148) and are thrown away, although their cost (~$0.60 per gap) is already in the ledger. In the Sunday launchd run (schedule.py) this prints '<profile> failed: ...' and the report is ...
- `music-tools/drumrack/drumrack_tool.py:486` --in-place os.rename has no existence check and silently overwrites a different file that already carries the target name (kept 3/3, not live)
  Names are machine_code_nn with nn counted over the kept samples only. Run 1 with --all --in-place renames a.wav -> M_BD_01.wav and b.wav -> M_BD_02.wav. Run 2 with picks keeping only b: the kept list is [M_BD_02.wav], counter restarts at 01, dst = M_BD_01.wav exists (file a), and os.rename on macOS replaces it. Sample a is lost without any message.
- `music-tools/drumrack/drumrack_tool.py:494` --in-place together with --convert reads the original path after it has been renamed, crashing mid-run (kept 3/3, not live); same issue also at 496: ReceivingNote runs past 127 when a machine has more pads than the rack can hold
  In process_machine the in-place branch does os.rename(d["fp"], dst) (line 486) and then line 494 calls convert_for_digitakt(d["fp"], ...) on the old path. sf.read raises (file not found) on the first sample whose name changed, after that file and any earlier ones were already renamed on disk, so the originals are partly renamed and no rack is written.
- `music-tools/drumrack/drumrack_tool_v2.py:546` Normalised and non-WAV copies are silently written as 16-bit, losing the source bit depth (kept 3/3, not live)
  copy_or_normalise only does a byte copy when peak_db is None AND the source is .wav. Otherwise it reads to float and calls sf.write(dst, y, sr) with no subtype; the destination name always ends in .wav (newname = base + ".wav"), so soundfile's WAV default PCM_16 applies. Scenario: a 24-bit WAV library built with `--peak-db -6`, or any 24-bit AIFF/FLAC library built without flags, produces 16-bit 'renamed copies' that the README describes as clean-named copies; the .adg pads then point at the degraded files. Fix: pass subtype=sf.info(src).subtype (or PCM_24 when the source is 24-bit).
- `music-tools/drumrack/drumrack_tool_v2.py:765` select_max divides by zero when there are more instrument types than --max-pads (kept 3/3, not live)
  quota starts at max(1, ...) per type, so with more types than max_pads the sum exceeds the cap and the trim loop (line 757-758) decrements groups to quota 0. The emit loop then hits `step = len(g) / q` with q == 0. Scenario: a TR-808 folder with 13 types (BD SD RS CP CH OH LT MT HT CB CL CG MA), `build --convert --max-pads 8` (8 = Digitakt track count): quotas all 1, five trimmed to 0, then ZeroDivisionError on the first zero-quota group; the build aborts after renamed copies for earlier machines were already written. Needs `if q <= 0: continue` (or a smarter trim).
- `music-tools/drumrack/drumrack_tool_v2.py:802` --in-place renames originals in bulk with no dry run, no confirmation and no undo script, against the project's bulk-rename rule (kept 3/3, not live)
  The in-place branch renames every selected original immediately (`os.rename`) as soon as the flag is passed; there is no --dry-run, no listing of old->new before acting, and the only mapping (build_report.csv) is written at the very end of cmd_build, so an interrupted run (Ctrl-C, unreadable file in copy/convert, the --convert crash above) leaves renamed files with no record. Combined with `--all` it renames every audio file under the library. For .aif/.aiff/.flac originals the report's 'renamed' column also lists `base + ".wav"` (line 796) while the file on disk kept its real extension (line ...
- `music-tools/drumrack/drumrack_tool_v2.py:809` --in-place together with --convert reads the original path after it was renamed, crashing mid-run (kept 3/3, not live)
  In process_machine the in-place branch renames the original (line 802: os.rename(d["fp"], dst)) but never updates d["fp"]. Three lines later the --convert branch calls convert_for_digitakt(d["fp"], ...), which does sf.read(src) on the now non-existent old path and raises. Scenario: `build LIB --in-place --convert` on any machine: the first sample is renamed on disk, then the run aborts with a soundfile error; the remaining samples are untouched, no .adg is written, and build_report.csv (the only old-name -> new-name record for a destructive rename) is never written because the exception propag...
- `music-tools/drumrack/serum_sort/rename_inside.py:13` read_name decodes the UTF-8 prgName as latin1, producing mojibake names that went onto disk (kept 3/3, not live)
  Serum stores the 28-byte prgName as UTF-8 (the backup of Keys_Órgano.fxp has bytes c3 93 = 'Ó' at offset 35). read_name decodes it with latin1, so 'Keys - Órgano' is read as 'Keys - Ã\x93rgano'. That string was carried into names.json ('inside': 'Keys - Ã\u0093rgano', 'new': 'KY HipHop - Ã\u0093rgano') and became the real filename: both live Serum folders now contain 'KY HipHop - Ã\u0093rgano.fxp' (ls bytes c3 83 c2 93). Every preset with a non-ASCII inside name (Órgano, älskar, ...) is misread the same way.
- `music-tools/drumrack/serum_sort/rename_inside.py:20` rename_fxp rewrites the Serum .fxp compressed chunk, the operation that crashed Serum 1 and is now hard rule 6 (kept 3/3, not live)
  rename_fxp() zlib-decompresses the .fxp data block at offset 60, patches 30 bytes at offset 18802, recompresses with zlib level 9 and rewrites byteSize/chunkSize, then overwrites the preset in place. This is exactly the 2026-10-20 incident recorded in memory (serum-fxp-never-rewrite-chunk.md: SerumDSP::LoadPreset -> setChunk -> memmove EXC_BAD_ACCESS in Live; all 298 .fxp restored from backups) and in music-tools/STATUS.md ('Rule: never modify an .fxp chunk'). The script is still a working CLI (python3 rename_inside.py <path> <name> ...) with no guard, no dry-run and a docstring that presents ...
- `plans/outreach-page/outreach.html:309` Second tap on a card while its DB write is in flight is dropped, then the snapshot reverts the UI (kept 3/3, not live)
  setTick updates the local map and repaints, but if `busy[id]` is set (a previous write for the same card has not resolved) it returns without writing and without queueing the new value. Scenario: tap V (write true starts, busy=true), then tap X within the write latency: local shows X, no write is sent, busy clears when write 1 lands, and the ticks snapshot (line 333) then overwrites the local map with the DB's `true`, so the card jumps back to V. The user's second decision is lost with no notice (dbnote is only shown on a rejected write, not on a skipped one).
- `plans/strategy/drafts/launchd/sc_refresh.sh:47` Log allowlist drops the only diagnostics for gate exits and crashes, and exit 1 from a crash is reported as 'token expired' (kept 3/3, not live)
  The wrapper captures all of sc_weekly_health.py's output into OUT and writes to the log only lines matching the fixed grep -E allowlist (line 47); nothing else of OUT reaches any file (launchd's StandardOutPath gets nothing because stdout was captured). Two realistic exits produce no matching line: (a) a pause or cooldown: ig_ops_guards.standard_gates raises OpsGate(SystemExit) with code 6/8 after printing '[PAUSE GATE] ...' or '[COOLDOWN GATE] ... until YYYY-MM-DD HH:MM' (ig_ops_guards.py 110-116, 251-256); neither string matches the allowlist, so the log shows only '=== ... exit=6' and the n...
- `release_manager/playground.py:114` A kept-list file that fails to parse is read as empty and then overwritten with one entry on the next toggle (kept 3/3, live)
  wall_kept (and layouts_kept 247, elements_kept 306, colours_kept 364, fonts_hidden 401, wall_hidden 426) wrap the read in `except Exception: return []`. Every *_toggle then computes the new list from that empty result and `write_text`s it back, so a file that is temporarily unreadable (partial write from a crash mid write_text, a stray hand edit, a permission error, a non-UTF8 byte) is replaced by a list with a single item: all earlier picks are gone with no error and no backup. The writes themselves are plain `f.write_text(...)`, not the mkstemp+os.replace pattern effects_page.set_flag uses, ...
- `release_manager/storage.py:28` release_path() joins the raw slug, so a URL naming a .bak file loads it and Save brief overwrites the live release with it (kept 3/3, live)
  release_path does no validation of the slug. views/imagine.py:68 passes request.args['release'] straight to load_release, and /imagine/brief (views/imagine.py:206) does the same with the JSON body, then calls save_release(rel), which writes to release_path(rel['slug']) rather than to the file it was loaded from. releases/ holds backups such as farewell-single.bak.20261106_review.json whose inner slug is 'farewell-single'. Scenario: open /imagine?release=farewell-single.bak.20261106_review (the backup renders as a normal release), click Save brief: atomic_write_json replaces releases/farewell-s...
- `release_manager/templates/playground_layout.html:301` Kept layouts store the colour save by index; removing a save shifts or crashes every keep (kept 3/3, live)
  Each kept layout carries save as a position in SAVES (colours_kept). The colours page can un-keep a colour save (playground.colours_toggle removes it from the list), after which indexes shift: a keep with save=2 silently renders on what used to be save 3, and a keep whose index is now out of range makes basePick throw TypeError (SAVES[st.save] is undefined). artCanvas calls pickFor synchronously before returning a promise, so the throw escapes render(...).catch and aborts renderKept mid-loop (loadKept's then-chain rejects, markKept/abFromUrl never run), and likewise breaks abDraw, galDraw, tTh...
- `release_manager/templates/playground_layout.html:422` artCanvas throws synchronously for an out-of-range save, which skips every .catch and leaves draw() locked (busy stays true) until the page is reloaded (kept 3/3, live)
  artCanvas() evaluates `pickFor(st)` before it returns a promise (line 422), and pickFor -> basePick reads `SAVES[st.save].pick`. When st.save is >= SAVES.length (a keep whose colour save was removed, see the previous finding, or a corrupt localStorage `d.save` that is not a number so the clamp on line 295 does not fire), that is a synchronous TypeError, not a rejected promise. Every caller is written as `render(...).then(...).catch(...)`, so the exception escapes them all. In draw() the flag is set first (`busy = true`) and only reset inside .then/.catch; after the throw it stays true forever ...
- `release_manager/views/release.py:272` release_detail GET rewrites the release file and drops checklist items not in the current template, with no backup (kept 3/3, live)
  Viewing /release/<slug> runs a migration: when any expected checklist id is missing, migrate_checklist() regenerates the list from the template and keeps only ids that still exist (its docstring: "Removed items are dropped"), then save_release() writes the file. A GET therefore performs a destructive write: any checklist item whose id was renamed or removed in checklist.py loses its done state, done_date and notes the first time Amir opens the page, and unlike the clips path (backup_release_file) nothing is saved first.
- `release_manager/views/release.py:368` api_release_delete permanently unlinks a release file with no backup or Trash, and can delete .bak snapshots by slug (kept 3/3, live)
  POST /api/release/<slug>/delete calls storage.delete_release(), which does path.unlink() on releases/<slug>.json. There is no copy to the Trash and no .bak (contrast clips.save_release_clips, which backs up first, and photo_editor_delete, which moves to the Trash). Because release_exists() only checks the file exists, a slug such as `farewell-single.bak.20261106_review` deletes one of the backup snapshots that live in releases/. No template on score-board renders the old `.card-menu-delete` button (grep of templates/ finds none), so the endpoint is live without any UI, reachable to any same-or...
- `release_manager/views/release.py:867` Resizer upload is written into artwork/ under the client filename, overwriting a same-named master without backup (kept 3/3, live); same issue also at 868: Resizer upload overwrites an existing source master in artwork/ with the same filename, without warning
  On the Artwork Resizer POST an uploaded file is saved as ARTWORK_DIR / secure_filename(filename). Dropping a file from Photos or Finder whose name matches an existing master (IMG_6455.jpeg is the documented example name) overwrites that source artwork in place; no copy, no .bak, no Trash. The resizer's job is to produce resized/ outputs, yet it mutates the source folder as a side effect.
- `scene_intelligence/ig_reenrich_contacts.py:188` Provider fetch catches only ProviderError; a network exception aborts the run before the save, losing the batch (kept 3/3, live)
  In the live provider path (the dispatcher runs this daily; ledger shows provider runs on 11-05/06/07), fetch() wraps prov.profile(u) in `except ProviderError` only. Provider._get (ig_data_provider.py) calls `self.s.get(...)` with no try/except, so a requests.ConnectionError / ReadTimeout (ProviderError subclasses RuntimeError, not RequestException) propagates out of fetch -> run_batch -> main. The save block at lines 216-222 is never reached: every contact already refreshed in memory that run is discarded, the paid HikerAPI calls were spent, and the ledger slot claimed at line 180 blocks a rer...
- `scene_intelligence/sc_buy_links.py:203` The applied-log is only written after the loop completes, so every abort path loses the record of rows already changed on SoundCloud (kept 3/3, not live)
  results is accumulated in memory and written to buy-links-applied-*.json only at line 203-205. The three abort paths inside the loop (SystemExit on non-200 PUT at line 194, SystemExit on unexpected diff at line 202, and any HealthCheckError/APIBudgetExceeded raised by _api_get) all leave the function before that write. Rows already PUT to SoundCloud are then unrecorded, which defeats the 'record-before-changing' audit the module docstring promises. Evidence on disk: 9 tracks carry the new campaign links, yet data/soundcloud contains no buy-links-applied-*.json at all.
- `stats/collectors.py:210` SoundCloud token refresh overwrites the shared credential file non-atomically and drops keys the other SC scripts rely on (kept 3/3, live)
  _sc_refresh_token() rewrites .sc_user_token.json with open(..., 'w') + json.dump of the raw refresh response. (1) The write is truncate-then-dump, not atomic: a kill or exception between truncate and dump (the 08:45 launchd stats-sync run) leaves an empty/invalid JSON file, and every other SoundCloud job that shares the file (sc_engagement 10:00 and 13:00, sc_weekly_health 06:30/07:30/08:30, check_sc_follows) then reads {} ('No user token file found') and stays dead until a manual re-auth. (2) It writes the response verbatim: if SoundCloud omits refresh_token in a refresh response, the only co...
- `stats/daily_brief.py:276` write_proposals replaces the whole System handover when the file cannot be read (kept 3/3, live)
  The live task system-daily-brief-2 runs `python3 stats/daily_brief.py --write` daily at 20:00. When a red line repeats two days running, write_proposals() does `text = _read(HANDOVER) or ""` and then `HANDOVER.write_text(...)`. _read (stats/socials_digest.py:41-45) swallows any OSError and returns None, so a transient read failure on plans/handovers/system/system.md (permission denied, I/O error, the file momentarily absent while an editor or sync tool does an atomic replace) makes text == "". Then `HANDOVER_SECTION not in text` is true, the base becomes "\n\n## Proposed from the brief\n..." a...

### Low (109)

- `bandcamp_links.py:112` One release with a non-page Bandcamp URL aborts --write for every release with an uncaught ValueError (kept 3/3, not live)
- `bandcamp_links.py:115` --write with --channel replaces the whole stored link set with only the chosen channel(s) (kept 3/3, not live)
- `copy_clean.py:55` Double hyphen inside a URL is rewritten to a comma, breaking the link (kept 3/3, live)
- `docs/reports/m5-undo-2026-11-07.sh:33` Undo script un-parks the A2 si-sheet group although its header says A2 is not touched, and does so after the success message (kept 3/3, not live)
- `gap_radar/profile_check.py:82` A Reddit 403 or a 200 with no entries is cached forever as 'missing' (kept 3/3, live)
- `gap_radar/schedule.py:28` The run-state file lives in the current checkout while the ledger is forced to the main checkout (kept 3/3, live)
- `gap_radar/schedule.py:61` A wait in the first week silently drops that month's monthly list and crowding checks (kept 3/3, live)
- `gap_radar/schedule.py:83` plan() ignores schedule.json's 'paused' list; a paused profile still runs and spends (kept 2/3, live)
- `gap_radar/schedule.py:109` too_soon can veto the month's only monthly run (kept 2/3, live)
- `gap_radar/schedule.py:128` A bad profile aborts the whole scheduled run instead of being skipped (kept 3/3, live)
- `gap_radar/sources_extra.py:72` Stack Exchange item parsing sits outside the per-query try, so one malformed item aborts the whole weekly collection (kept 3/3, live)
- `hygiene_check.py:32` Saved-page detection depends on attribute order, so common saved pages are not flagged (kept 3/3, live)
- `music-tools/drumrack/drumrack_tool.py:327` Sample paths are spliced into the .adg XML without XML escaping (kept 3/3, not live)
- `music-tools/drumrack/drumrack_tool.py:428` Picks are unioned across every *.picks.json found and browser re-downloads are ignored, so narrowing a selection never takes effect (kept 3/3, not live)
- `music-tools/drumrack/drumrack_tool_v2.py:405` Audition page injects sample filenames and codes into innerHTML without escaping (XSS from a malicious sample-pack filename) (kept 3/3, not live)
- `music-tools/drumrack/drumrack_tool_v2.py:723` Type code from any *.picks.json (including ~/Downloads) is unvalidated and becomes part of the output filename, allowing path traversal in copy and in-place rename (kept 3/3, not live)
- `music-tools/drumrack/misc_fix/apply_racks.py:25` Re-run overwrites the pristine .adg backup; renames happen before the backup (kept 3/3, not live)
- `music-tools/drumrack/misc_fix/identify.py:20` dur() divides by zero for WAVs with fewer than 8 bits per sample (kept 3/3, not live)
- `music-tools/drumrack/misc_fix/identify.py:26` aud() crashes on an empty ffmpeg decode instead of skipping the file (kept 3/3, not live)
- `music-tools/drumrack/serum_sort/rename_inside.py:17` rename_fxp writes the new name as latin1 although Serum stores the field as UTF-8 (kept 3/3, not live)
- `music-tools/drumrack/serum_sort/undo_moves.sh:4` undo_moves.sh uses pre-rename filenames; run on its own (or first) it fails for every file the later rename scripts touched (kept 3/3, not live)
- `music-tools/drumrack/serum_sort/undo_other_filenames.sh:126` Undo lines 126-127 contain a literal '\x93' escape instead of the real character, so that preset is never undone (kept 3/3, not live)
- `music-tools/drumrack/serum_sort/undo_trackremakes_filenames.sh:5` Undo script reverts a two-step rename in the wrong order, so one run leaves 5 presets (x2 trees) at the intermediate name (kept 3/3, not live)
- `music-tools/drumrack/snare_pitch/body_pitch.py:10` One unreadable or missing input file aborts the whole run before the CSV is written (kept 3/3, not live)
- `music-tools/drumrack/snare_pitch/body_pitch.py:11` Peak within the last 10 ms of the file yields an empty analysis window and a silently bogus row (kept 3/3, not live)
- `music-tools/drumrack/snare_pitch/build_cc_racks.py:47` Unknown stem crashes mid-build after copies are made; undo script only written at the end (kept 2/3, not live)
- `music-tools/drumrack/snare_pitch/build_cc_racks.py:62` Generated undo script deletes whole folders with rm -rf instead of Trash (kept 3/3, not live)
- `music-tools/drumrack/snare_pitch/build_key_racks.py:96` Generated undo script deletes whole folders with rm -rf instead of Trash (kept 3/3, not live)
- `music-tools/drumrack/snare_pitch/cc_style_match.py:49` Output path argument is first read after the whole library scan, so a missing argument throws away minutes of work (kept 3/3, not live)
- `music-tools/drumrack/snare_pitch/compare_wh_rack.py:27` A missing or moved pad sample crashes the script after the output CSV was already truncated, leaving wh_rack_vs_cc.csv partial (kept 3/3, not live)
- `music-tools/drumrack/snare_pitch/score_wh_folder.py:12` Same CWD-relative CSV paths as compare_wh_rack.py: fails unless run from inside snare_pitch/ (kept 2/3, not live)
- `music-tools/drumrack/snare_pitch/undo_cc_racks.sh:3` Undo permanently rm -rf's three whole folders that are now a live sample set, not only the build output (kept 3/3, not live)
- `music-tools/drumrack/vocal_keys/key_check.py:13` Files shorter than one FFT window produce an all-zero chroma and NaN correlations (kept 3/3, not live)
- `music-tools/drumrack/vocal_keys/key_check.py:29` parse_key crashes with ValueError on theoretically valid spellings Cb, Fb, E#, B# (kept 3/3, not live)
- `music-tools/drumrack/vocal_keys/key_check.py:35` One unreadable .wav aborts the whole folder scan and no CSV is written (kept 3/3, not live)
- `music-tools/drumrack/vocal_keys/key_check.py:41` One-shot with no key in its filename is reported as DIFFERENT instead of 'no key in name' (kept 3/3, not live)
- `music-tools/drumrack/vocal_keys/undo_stickz_sort.sh:3` cd is not checked; if it fails, mkdir -p creates the whole Stickz folder tree in the caller's working directory (kept 3/3, not live)
- `music-tools/drumrack/zerog_pitch/scan.py:11` Loop folder 'Melody loops' is analysed and tagged although the script's rule says loops are skipped (kept 2/3, not live)
- `music-tools/dupes/scan_dupes.py:13` WAV data chunk declared with size 0 hashes as empty, so all such files group as duplicates (kept 3/3, not live)
- `plans/decisions_writeback.py:130` metric field is not validated against plans/targets.json keys, so a typo makes tickets.json fail the board validator (kept 3/3, not live)
- `plans/decisions_writeback.py:135` Control Panel board accepts status 'waiting', which release_manager/board.py rejects (kept 3/3, not live)
- `plans/decisions_writeback.py:144` metric 'none' guard checks the on-disk ticket, not the metric_note write in the same decision (kept 3/3, not live)
- `plans/decisions_writeback.py:216` Handover .md target is not checked to exist, so a typo creates a stray file or crashes mid-run (kept 3/3, not live)
- `plans/decisions_writeback.py:241` Second run on the same day overwrites the backup with already-modified content (kept 3/3, not live)
- `plans/outreach-page/dj07_lists.py:29` A ProviderError mid-pagination discards every user fetched so far, after the day's ledger claim is already recorded (kept 3/3, not live)
- `plans/outreach-page/drafts_round1.py:772` Re-running the round-1 script clobbers later-revised drafts and statuses with no backup (kept 3/3, not live)
- `plans/outreach-page/history.py:17` Demo/promo email history is never loaded: plist() returns an empty list for promotion_log.json (kept 3/3, not live)
- `plans/outreach-page/outreach.html:298` paint() dereferences a card element that may not exist, killing all filtering and counts (kept 3/3, not live)
- `plans/outreach-page/outreach.html:301` 'Never contacted' and 'Contacted before' chips both exclude cards whose only prior contact is rank 6 (they follow you) (kept 3/3, not live)
- `plans/outreach-page/outreach.html:323` window.claude.use('db') has no rejection handler, so a failed capability load leaves the 'ticks not saving' note hidden (kept 2/3, not live)
- `plans/outreach-page/outreach.html:333` DB tick snapshot replaces the ticks seeded from the embedded data, so seeded decisions vanish or flip once the DB loads (kept 3/3, not live)
- `plans/outreach-page/recovered/index.html:140` A second tick while a DB write is in flight is never persisted and gets reverted (kept 3/3, not live)
- `plans/outreach-page/research-mixseries/build.py:32` Output paths are relative to the current directory, not the script folder (kept 3/3, not live)
- `plans/outreach-page/research-mixseries/build.py:81` Output paths are relative to the shell cwd, so the summary lands outside the repo when run from anywhere but its own folder (kept 2/3, not live)
- `plans/outreach-page/research-mixseries/fetch.sh:6` A non-empty error page counts as a successful fetch and is never retried (kept 3/3, not live)
- `plans/review-page/gen.py:195` Every db snapshot rebuilds the whole page, wiping a note Amir is typing and detaching the Saving/Saved message (kept 3/3, not live)
- `plans/review-page/read_ticks.py:29` A wrong or missing ticks directory prints 'no ticks' and exits 0 instead of failing (kept 3/3, not live)
- `plans/review-page/read_ticks.py:34` A non-dict JSON file in the ticks dir crashes the whole read-back before any tick is processed (kept 3/3, not live)
- `plans/sc-sweep-page/index.html:109` A pick tapped before the db capability resolves is silently discarded when the first snapshot arrives (kept 3/3, not live)
- `plans/strategy/drafts/launchd/sc_refresh.sh:68` Slot-3 commit sweeps up anything another chat has staged, not just the SC data files (kept 3/3, not live)
- `plans/undo-release-backups-2026-11-04.sh:5` The git fallback of every undo line cannot restore anything: the paths were already deleted in the same commit (kept 3/3, not live)
- `references/look02/all_picks.py:30` all_picks.py opens cover_notype.png beside itself, but the file only exists under references/look02/scripts/ (kept 3/3, not live)
- `references/look02/logo_round_c.py:143` logo_round_c.py main block crashes: photo mock-up opens pull/out-022_reel.jpg from the wrong folder (kept 3/3, not live)
- `references/look02/logo_round_c.py:148` Round C __main__ crashes on A.photo_corner: pull/out-022_reel.jpg is not beside the kept script (kept 2/2, not live)
- `references/look02/logo_round_f.py:109` Round F __main__ crashes on A.photo_corner for the same missing pull/ folder (kept 3/3, not live)
- `references/look02/logo_round_g.py:114` Running logo_round_g.py from references/look02 crashes with FileNotFoundError: the pull/ fixture is not beside the surviving copy (kept 3/3, not live)
- `references/look02/v2/logo_v2.py:5` logo_v2.py cannot be imported or run from its folder: its three imports live in the parent directory (kept 3/3, not live)
- `references/look02/v3/logo_v3.py:5` logo_v3.py cannot import its helpers from the folder it lives in (kept 2/3, not live)
- `release_manager/bio_manager.py:58` artist_profile.json is written non-atomically and read without corruption handling, so one bad write takes down every Words page (kept 3/3, live)
- `release_manager/copy_pass.py:58` assemble_instagram crashes on a non-string hashtag item (None/number) after a paid model call (kept 3/3, live)
- `release_manager/imagine.py:349` The paid render calls image_generator.get_client(), which sys.exit()s on a missing key; SystemExit escapes the routes' except Exception (kept 3/3, live)
- `release_manager/imagine.py:444` composite() builds the image id and output path from the unsanitized release string stored on the plate record (kept 2/3, live)
- `release_manager/review.py:388` refresh() binds a late-arriving file's hash but leaves the failing 'file missing' chips, so the item stays held (kept 3/3, live); same issue also at 389: refresh() binds a late-arriving file's hash but leaves the stale failing 'file missing' hash chip, so the item stays held
- `release_manager/review.py:630` Handle vouch list absorbs 110 JSON field names as verified handles (kept 3/3, live)
- `release_manager/score_board.py:301` A malformed baseline date/value or a non-numeric floor in targets.json raises out of _card and takes the whole board down (kept 2/3, live)
- `release_manager/static/app.js:156` Validate button crashes silently when the API returns an error JSON (no `warnings` key) (kept 3/3, live)
- `release_manager/static/app.js:711` Preselected-release auto-fill overwrites the posted metadata overrides after a resizer POST (kept 3/3, live)
- `release_manager/static/imagine.js:231` 'Try the fix' auto-runs the two paid AI reviews on every result, including Final-quality renders (kept 3/3, live)
- `release_manager/static/imagine.js:253` Composite 'Make it' button stays disabled forever when the server answers with a non-JSON error (kept 3/3, live)
- `release_manager/storage.py:145` Release delete API unlinks the JSON permanently instead of moving it to the Trash (kept 3/3, live)
- `release_manager/templates/base.html:6` Every page raises UndefinedError when Flask-WTF is absent, defeating core.py's ImportError fallback (kept 3/3, live)
- `release_manager/templates/playground.html:215` Cover images are cache-busted with the base image's version, so a re-exported cover shows stale for up to an hour (kept 3/3, live)
- `release_manager/templates/playground_layout.html:1024` Tournament thumbnail cache is keyed by keep index and never invalidated (kept 3/3, live)
- `release_manager/templates/playground_wall.html:172` Cover name restored from localStorage is never checked against the covers that exist (kept 3/3, live)
- `release_manager/templates/playground_wall.html:461` Compare modal throws TypeError when the cover list is empty (kept 3/3, live)
- `release_manager/templates/sc_automation.html:119` Follow Tracker row status is decided on followed_back alone, so unfollowed entries render as "Pending" (kept 3/3, live)
- `release_manager/templates/video.html:667` Metadata block loses its mode and manual fields after every Video Resizer POST (kept 3/3, live)
- `release_manager/views/release.py:702` Uploading a cover in a different format leaves the old <slug>.<ext> in place, so the release page can keep showing the old artwork (kept 3/3, live)
- `release_manager/views/release.py:895` metadata_release form value reaches the filesystem unsanitized (path traversal read on any *.json) (kept 3/3, live)
- `release_manager/views/release.py:935` Preview sheet is picked by substring match in arbitrary directory order, so another image's or a stale preview can be shown (kept 3/3, live)
- `release_manager/views/shoot.py:504` imagine: sources accept non-image files, so /edit, /edit/preview and /edit/save 500 on a .json record (kept 3/3, live); same issue also at 504: The imagine branch of _edit_source skips the image-extension check, so a JSON record 500s the editor
- `release_manager/views/studio.py:597` Video upload silently overwrites an existing source master of the same name in videos/ (kept 3/3, live)
- `release_manager/views/words.py:132` Single-writer Generate overwrites a picked SEO field but leaves its written_by record pointing at the old writer (kept 3/3, live)
- `release_manager/views/words.py:257` Bio Save Edit and Undo change the current bio but keep the previous writer's written_by (kept 3/3, live)
- `scene_intelligence/ig_reenrich_contacts.py:202` Direct-API path: 401/429 SystemExit from _fetch_profile skips the save after the ledger claim (kept 3/3, live)
- `scene_intelligence/ig_reenrich_contacts.py:204` Direct-API path turns transient fetch errors into 'missing', which can flag a live handle dead (kept 3/3, live)
- `scene_intelligence/sc_buy_links.py:134` The plan Amir approves records the OLD purchase_title as new_purchase_title, while apply() writes the constant 'Buy on Bandcamp' (kept 3/3, not live)
- `scene_intelligence/sc_buy_links.py:184` apply() exceeds sc_weekly_health's 30-call hard cap on any plan with more than 10 change rows and aborts mid-run with an uncaught exception (kept 3/3, not live)
- `scene_intelligence/sc_buy_links.py:185` apply writes a purchase_title the approved plan never showed (kept 3/3, not live)
- `scene_intelligence/sc_buy_links.py:197` changed_fields treats the nested, volatile 'user' object as stable, so a follower-count change between the two reads aborts a correctly applied row (kept 3/3, not live)
- `scene_intelligence/sc_engagement.py:2999` "Last 30 SC actions" sorts by day-only date, so on a 30+ action day the panel shows an arbitrary subset (kept 3/3, live)
- `stats/bandcamp_import.py:64` A non-numeric 'paid to you' cell raises ValueError out of parse_bandcamp_csv (only the file read is guarded) (kept 3/3, live)
- `stats/daily_brief.py:160` Sweep check is hard-wired to a '## 16:15 sweep run' heading, so a sweep started at another time is silently ignored (kept 3/3, live)
- `stats/daily_brief.py:163` Sweep check matches the plain English word 'stop' case-insensitively and reports 'SC sweep stopped early' (kept 3/3, live)
- `stats/propose_targets.py:109` set_ig_baseline writes a rung dated after the period end when period.end is not a month end (kept 3/3, not live)
- `stats/socials_digest.py:196` now_line() crashes the daily digest on a ticket whose title is null (kept 2/3, live)
- `stats/storage.py:117` Corrupt manual_entries.json raises SystemExit inside Flask request handlers, killing the request with no response (kept 3/3, live)
- `stats/storage.py:150` get_manual_latest returns the last-appended entry, not the latest-dated one (kept 3/3, live)
- `video_resizer.py:534` Trim window is never validated (start >= end, end past duration) (kept 3/3, live)

## Non-blocking, low, not verified (397)

Style, dead code, test gaps and low-severity notes straight from the reviewers, no refute pass. Treat as a to-look-at list, not as confirmed.

### correctness (53)

- `bandcamp_links.py:66` campaign_url drops blank-valued query params and re-encodes others, not just the campaign key
- `caption_check.py:76` GREETING_RE flags captions that open with 'Hi-hat' as a greeting
- `copy_clean.py:104` Leading-dash list-marker rewrite is not counted in the report
- `copy_clean.py:124` Dash-to-comma pass rewrites '--' and en dashes inside URLs and hashtags despite the 'never touches URLs, #hashtags' contract
- `gap_radar/crowding.py:64` _norm strips the trailing slash before cutting the fragment, so '/#frag' URLs never match
- `gap_radar/crowding.py:144` A ClaudeError on a pause_turn continuation records cost_usd 0.0 though earlier turns were billed
- `gap_radar/profile_check.py:145` keyword_yield treats multi-term quoted phrases as one contiguous phrase, so they always read as dead
- `gap_radar/schedule.py:142` Scheduled path skips the GR-10 profile pre-check and yield line
- `music-tools/drumrack/drumrack_tool.py:383` sanitize() collisions silently drop a whole machine folder from scan and build
- `music-tools/drumrack/drumrack_tool.py:492` Non-WAV sources are rewritten with soundfile's default subtype, silently reducing 24-bit files to 16-bit
- `music-tools/drumrack/drumrack_tool_v2.py:566` Output-folder exclusion is a bare string-prefix test, so sibling folders sharing the prefix are skipped
- `music-tools/drumrack/drumrack_tool_v2.py:798` In --in-place mode the report's 'renamed' column and --peak-db do not match what happens on disk
- `music-tools/drumrack/snare_pitch/body_pitch.py:16` Sample name is derived by chopping 4 characters, wrong for .aiff and extensionless names
- `music-tools/drumrack/snare_pitch/compare_wh_rack.py:14` Pads whose sample is not under Samples/Imported or not lowercase .wav are silently dropped
- `music-tools/drumrack/snare_pitch/wh_rack_vs_cc.csv:3` Committed wh_rack_vs_cc.csv is stale: 'same audio as CC rack pad' is blank for pads that are byte-identical to rack-1 plan files
- `music-tools/drumrack/vocal_keys/key_check.py:34` '.WAV' files pass the extension filter but can never match the key regex
- `music-tools/drumrack/vocal_keys/undo_stickz_sort.sh:118` Undo leaves the emptied 'Chops by Key' tree behind
- `music-tools/drumrack/zerog_pitch/scan.py:15` Disc label is the last character of the folder name, so 'DISC 10' and later would be reported as disc '0'
- `music-tools/dupes/scan_dupes.py:19` AIFF SSND hash ignores the chunk's offset field
- `music-tools/dupes/scan_dupes.py:43` Every project inside PROJECTS/DONE is reported as the song "DONE"
- `music-tools/plan.html:224` Machine lists do not match their counts: 27 names labelled 28, 10 labelled 11, 47 named under a '49' headline
- `plans/outreach-page/drafts_round1.py:391` BIMFest 'draft' is a note to Amir but is stored as a sendable draft body with status 'drafted'
- `plans/outreach-page/history.py:32` 'engaged' actions count for Instagram history but not SoundCloud; follow entries are labelled 'liked'
- `plans/review-page/gen.py:25` Page hides approved items although export and import_ticks treat them as open and tickable
- `plans/review-page/read_ticks.py:58` Release file is re-saved (with reconcile and updated_at bump) on every re-run even when every tick was already consumed
- `plans/strategy/refresh-page/index.html:441` Batch filter compares the free-text 'when' field by exact equality, so cards whose status text was updated drop out of every batch
- `release_manager/archive.py:271` A paragraph line that starts with a number and a dot (e.g. '2026. Berlin') is rendered as an ordered list
- `release_manager/outreach.py:202` set_try accepts 1/0/1.0 as a tick value and stores a non-boolean the page then shows as undecided
- `release_manager/review.py:114` HANDLE_RE misses handles after quotes, colons or commas, so they go unchecked
- `release_manager/review.py:983` Phone proposals are accepted on draft and change items but can never be confirmed
- `release_manager/score_board.py:128` Numeric-string readings pass _clean_series but vanish from the sparkline
- `release_manager/score_board.py:442` A detection event with count 0 is counted as 1; same issue also at 444: A detection event with count 0 is counted as 1
- `release_manager/static/app.js:133` Unchecking an overdue checklist item does not restore its overdue styling until reload
- `release_manager/static/app.js:272` showToast is called with a boolean type, producing the unstyled class `toast-true`
- `release_manager/templates/_words_seo.html:248` Copy button double-decodes entities and the data-text attribute never escapes '&', so copy text with entity-like sequences is altered
- `release_manager/templates/playground.html:12` Index page says no release has a base artwork while listing the releases that do
- `release_manager/templates/playground_layout.html:1125` Cut-paper checkbox has no effect on a save whose own pick has line 0
- `release_manager/templates/playground_wall.html:377` Big-view load guard checks the look but not the cover, so a stale load can paint the wrong cover
- `release_manager/tickets.py:163` The 'max 3 now per area' cap is counted per file, so one area can hold up to 6 now-tickets across the two boards
- `release_manager/views/release.py:898` Metadata mode 'release' with an unknown slug silently embeds nothing
- `release_manager/views/release.py:934` Preview sheet lookup takes the first _preview_* whose name merely contains the stem, in directory order
- `release_manager/views/shoot.py:308` _cover_font reports the fallback face's label but the unknown key's CSS family
- `scene_intelligence/ig_reciprocity_from_lists.py:68` stats.last_checked is bumped but stats.last_checked_source still names the old IG export.
- `scene_intelligence/ig_reenrich_contacts.py:194` Direct-API path skips the IG pause check that the provider path performs
- `scene_intelligence/sc_buy_links.py:135` 'unchanged' classification compares only purchase_url, so an item with the right URL but a missing button text is never fixed
- `scene_intelligence/si_cleanup.py:108` Outreach data for an import is looked up by the row's first name, so handle-joined outreach contacts lose email/url.
- `stats/bandcamp_import.py:210` first_sale becomes '' when any sale date fails to parse
- `stats/collectors.py:773` Ledger refusal is stored as the bare exit code ('4'), the refusal text is dropped
- `stats/daily_brief.py:373` 🎯 line takes its rung date from the first ladder metric only and prints it for all of them
- `stats/daily_brief.py:394` 'spend ✅' in the Ran-today line depends on spend_latest.json, which the brief never refreshes
- `stats/propose_targets.py:107` set_ig_baseline checks the date against period.end but not period.start
- `stats/socials_digest.py:173` goals_line falls back to the expired last rung after the period ends
- `video_resizer.py:475` Canvas over-size warning names a CRF the file was never encoded at

### security (22)

- `fetch_text.py:102` Peer-IP check runs after the GET has already reached the rebound address; the docstring overstates what it closes
- `gap_radar/perplexity_test.py:63` Sends gap-report content (forum-derived pain and pay-signal text, product ideas) to Perplexity, a third-party service with no recorded approval
- `metadata_utils.py:52` metadata_from_release uses an unvalidated form value as a file path (traversal into any .json)
- `music-tools/drumrack/drumrack_tool.py:262` Filenames are injected into the audition page via innerHTML and raw json.dumps without HTML/script escaping
- `music-tools/drumrack/drumrack_tool_v2.py:405` Audition page inserts file names into innerHTML and the samples JSON into <script> without HTML escaping
- `music-tools/plan.html:4` Static local plan page loads fonts from Google on every open
- `plans/outreach-page/outreach.html:2` The private contact page loads a stylesheet from fonts.googleapis.com on every open
- `plans/review-page/gen.py:35` Private review page fetches Google Fonts, an unapproved third-party request the outreach-page pattern did not make
- `plans/sc-sweep-page/index.html:68` Third-party contact emails are baked into a page meant to be published as a claude.ai artifact
- `plans/strategy/refresh-page/index.html:5` Strategy page loads fonts from Google on every open although the brand font is local
- `plans/strategy/refresh-page/index.html:406` Page built for artifact publishing names a third party with a negative claim
- `release_manager/archive.py:220` render_markdown passes javascript:/data: hrefs through unchanged when link_base is the default "".
- `release_manager/static/app.js:18` CSRF fetch wrapper attaches the token to protocol-relative cross-origin URLs
- `release_manager/templates/fonts.html:5` @font-face src is emitted with |safe from fonts.json strings, the only unescaped output in the batch
- `release_manager/templates/outreach.html:54` Outreach page hotlinks contact images from a third-party host on every load
- `release_manager/templates/review.html:72` Review page puts the item's stored file path into the HTML (title attribute)
- `release_manager/templates/video.html:9` Absolute filesystem paths of the videos folder and each project are rendered into the page
- `release_manager/views/imagine.py:109` Generic exception text, including absolute filesystem paths, is returned to the browser
- `release_manager/views/words.py:87` Raw exception text, which can include absolute paths, is returned to the browser
- `release_manager/views/words.py:114` Slug from the JSON body is used unvalidated as a filename component
- `stats/ig_token_refresh.py:67` Interrupted write_token() can leave a plaintext copy of all .env secrets as .env.tmp.* in the repo root, which .gitignore does not cover
- `video_resizer.py:402` ffmpeg stderr tail (with absolute disk paths) is passed through to the web page

### robustness (118)

- `bandcamp_links.py:109` --write crashes mid-run on a release whose platform_links is null or whose bandcamp URL is not a track/album page
- `docs/reports/prune-bak-2026-11-07-undo.sh:3` Undo script has no existence check or set -e; once the Trash is emptied it only prints 20 mv errors
- `fetch_text.py:48` check_url only catches socket.gaierror; an over-long or invalid IDNA hostname raises UnicodeError uncaught
- `fetch_text.py:104` Peer-IP check refuses every fetch when a local HTTP(S) proxy is configured, and leaks the open response on refusal
- `fonts_library.py:315` match() rewrites fonts.json (the declared source of truth) in place with no temp-file swap or backup
- `gap_radar/crowding.py:93` Verdict is matched case-sensitively; 'Open'/'Crowded' silently become 'unclear'
- `gap_radar/perplexity_test.py:69` The --budget hard stop is silently disabled when the reply carries no usage.cost.total_cost
- `gap_radar/perplexity_test.py:95` Budget is checked before each call, so the run overshoots --budget by one call; empty report crashes dry-run
- `gap_radar/schedule.py:56` A malformed last_run in the state file crashes the run before anything is done
- `gap_radar/sources_extra.py:89` youtube() loads .env from its own checkout, not main_root()
- `hygiene_check.py:27` The .then(...) => eval loader pattern misses arrow functions without parentheses
- `metadata_utils.py:56` metadata_from_release crashes when a release JSON has "metadata": null
- `metadata_utils.py:127` A release_date that is not YYYY-MM-DD is written as an invalid EXIF DateTime
- `music-tools/drumrack/drumrack_tool.py:104` Unreadable audio files are dropped silently from scan and build
- `music-tools/drumrack/drumrack_tool.py:450` Invalid --map-start (or C-2) is silently replaced by 36
- `music-tools/drumrack/drumrack_tool_v2.py:489` Relative sample path is spliced into a re.sub replacement string unescaped
- `music-tools/drumrack/drumrack_tool_v2.py:658` load_picks lists ~/Downloads and the cwd without catching PermissionError
- `music-tools/drumrack/drumrack_tool_v2.py:671` load_picks crashes on a malformed picks file (non-numeric 'saved' or non-dict JSON) instead of skipping it
- `music-tools/drumrack/misc_fix/apply_digitakt.py:14` Uppercase .WAV files are skipped silently and block the folder cleanup
- `music-tools/drumrack/misc_fix/apply_digitakt.py:18` Destination type folder is never created before shutil.move
- `music-tools/drumrack/misc_fix/apply_racks.py:23` .asd sidecar left orphaned when the target sidecar already exists
- `music-tools/drumrack/serum_sort/rename_inside.py:9` backup() keys backups by current path, so a rename after a filename mv saves the already-modified file as the 'original'
- `music-tools/drumrack/serum_sort/rename_inside.py:40` Odd number of CLI arguments silently drops the last path
- `music-tools/drumrack/snare_pitch/body_pitch.py:17` The first argument is opened for writing with no check, so a swapped argument order overwrites a sample file
- `music-tools/drumrack/snare_pitch/build_cc_racks.py:37` Input and output paths are relative to the CWD, unlike the sibling scripts
- `music-tools/drumrack/snare_pitch/build_cc_racks.py:50` Name-clash check covers the per-rack copy folder but not the shared Digitakt folder
- `music-tools/drumrack/snare_pitch/build_cc_racks.py:60` Undo script is written only after the whole build succeeds, so a mid-build crash leaves output with no undo
- `music-tools/drumrack/snare_pitch/compare_wh_rack.py:18` feats()/audio_md5() calls have no error guard, unlike cc_style_match.py; one unreadable file aborts the run
- `music-tools/drumrack/snare_pitch/score_wh_folder.py:25` Input and output CSVs are cwd-relative; re-running from the folder silently overwrites wh_folder_matches.csv, an input to build_key_racks.py and plan_cc_racks.py
- `music-tools/drumrack/zerog_pitch/undo_rename.sh:3` Unguarded cd and plain mv: a failed cd produces 517 noisy failures and the script exits non-zero even on full success; same issue also at 4: mv without -n silently overwrites an existing untagged file
- `music-tools/drumrack/zerog_pitch/undo_rename.sh:1037` Script exits non-zero on a fully successful undo when the last .asd file does not exist
- `music-tools/dupes/scan_dupes.py:30` Unreadable or malformed audio files are silently dropped from the duplicate scan; same issue also at 31: Unreadable audio files are dropped silently; the printed 'scanned' count still includes them
- `music-tools/plan.html:1` No doctype, charset or viewport: the file has 65 non-ASCII characters and renders in quirks mode when opened from disk
- `plans/decisions_writeback.py:79` Duplicate decision ids are accepted; the real decisions-2026-11-06.json has two D4
- `plans/decisions_writeback.py:151` Text writes (next_step, metric_note) are not checked for em-dashes, which the board validator rejects
- `plans/ig-like-list-2026-11/check_like_targets.py:78` media_count None (provider omitted the field) is recorded as status no_posts
- `plans/outreach-page/dj07_lists.py:45` p.profile() can return None and the next line indexes it
- `plans/outreach-page/history.py:67` Output file written through unclosed temporaries; same pattern in drafts_round1.py line 777
- `plans/outreach-page/merge_organisers.py:18` plans/outreach-batches.json is rewritten in place without an atomic temp-file swap
- `plans/outreach-page/outreach.html:167` Pitch-group key is inserted into HTML and an attribute without esc()
- `plans/outreach-page/recovered/index.html:116` c.img is written into the src attribute without escaping
- `plans/outreach-page/research-fetish/_build/make_entries.py:43` entries.json is overwritten unconditionally with no backup and an unclosed file handle
- `plans/outreach-page/research-mixseries/fetch.sh:7` Fetch failures are swallowed with no final report
- `plans/outreach-page/research-mixseries/parse.py:3` Scrape files are opened without an explicit encoding
- `plans/outreach-page/research-mixseries/parse.py:8` Title is taken from the second SoundCloud link by position
- `plans/review-page/gen.py:27` Every plans/review-export-*.json is folded into the page, stale ones included, and a file without slug raises KeyError
- `plans/review-page/gen.py:196` A failed ticks listing is swallowed silently and the 10 s warning is never cleared
- `plans/review-page/gen.py:206` Embedded JSON only escapes '</', so a '<!--<script' sequence in review text breaks the page
- `plans/strategy/refresh-page/index.html:1` Standalone HTML file has no doctype, charset or viewport meta
- `plans/undo-release-backups-2026-11-04.sh:3` No `set -e`/exit status: a failed restore is not reported to the caller
- `references/look02/logo_round_g.py:50` glitch(): band height can round to 0 for small n, making the while loop never terminate
- `references/look02/logo_round_g.py:123` Re-running the script overwrites the kept draft sheets in place with no backup
- `release_manager/archive.py:176` safe_path catches only OSError, so a NUL byte in the requested path gives a 500 instead of a 404.
- `release_manager/display.py:39` progress_bar returns a bar wider than width when done exceeds total
- `release_manager/effects_page.py:99` filter_effects and validate assume well-typed records: a null notes or a non-dict record raises instead of failing validation
- `release_manager/effects_page.py:132` set_flag rewrites effects.json with mkstemp's 0600 mode, dropping the file's original permissions
- `release_manager/effects_page.py:154` set_release_effect fails on a release whose brand key is JSON null
- `release_manager/fonts_page.py:106` face_rules builds raw CSS that the templates emit with |safe; an apostrophe in a listed font path or system name breaks the whole style block
- `release_manager/outreach.py:184` categories not validated; a non-object value crashes build_view with an unhandled 500
- `release_manager/photo_edit.py:24` clean_params raises on non-numeric or null values and the save route turns that into a 500
- `release_manager/playground.py:29` base_path and save_version crash when brand.playground is JSON null
- `release_manager/playground.py:96` sized() writes its cache file in place, unlike the atomic temp-and-replace used by the other cache writers
- `release_manager/playground.py:132` wall_toggle's strength clamp catches ValueError/TypeError but not OverflowError, so JSON 1e400 crashes the route
- `release_manager/review.py:383` An approved item whose file disappeared keeps its approval
- `release_manager/review.py:499` When video_resizer cannot import, every destination is reported as 'unknown preset'
- `release_manager/score_board.py:405` Health ratio check casts snapshot counts with int() after accepting them with _num(), so a numeric string with a decimal point crashes the whole board
- `release_manager/score_board.py:410` _health crashes when autonomy_state.json parses to a non-dict
- `release_manager/static/imagine.js:51` The Show prompt and Generate click chains have no catch, so a non-JSON server error leaves the page silent
- `release_manager/static/imagine.js:199` Text typed into the Try-the-fix box is discarded when the second reviewer's answer arrives
- `release_manager/static/imagine.js:245` Decision click gives no feedback when the server rejects it or the request fails
- `release_manager/templates/_words_seo.html:148` Array fields with a non-string item throw during rendering after the copy was already saved
- `release_manager/templates/base.html:57` Sidebar 'Cover: Half the Night' link hardcodes slug pinocchio-single and 404s when that release has no kept colours
- `release_manager/templates/outreach.html:129` Tick save has no error path: a non-JSON or network failure is swallowed and the card silently keeps its old state
- `release_manager/templates/playground.html:611` Version delete reports 'deleted' without checking the response and has no error handler
- `release_manager/templates/playground_elements.html:90` Concurrent draw() calls can leave a pane showing a stale element combination
- `release_manager/templates/playground_elements.html:105` Keep toggle ignores an error reply and has no catch, so a failed keep gives no feedback
- `release_manager/templates/playground_layout.html:325` A failed layer load is cached as a rejected promise for the rest of the session
- `release_manager/templates/playground_layout.html:550` Effect images and their blob URLs are cached without bound and never revoked; same issue also at 552: Failed effect render is silent and re-uploads the picture on every redraw
- `release_manager/templates/playground_wall.html:264` Keep and remove POSTs swallow error responses silently
- `release_manager/views/imagine.py:48` An unknown or 'custom' preset makes /imagine/prompt return a 500 instead of a 400
- `release_manager/views/playground.py:51` Playground page executes a script that lives outside the repository
- `release_manager/views/playground.py:339` A non-string version name in the POST body makes /api/playground/<slug>/versions return 500 instead of 400
- `release_manager/views/release.py:506` Non-numeric bpm in the track forms raises ValueError and returns a 500
- `release_manager/views/release.py:817` format and focal are passed through unvalidated to the resizer
- `release_manager/views/release.py:922` COVER_MODE is a module global toggled per request on a threaded server
- `release_manager/views/review.py:102` Every refused tick rewrites the release file and a daily backup even when nothing changed
- `release_manager/views/shoot.py:47` _shoot_tools re-executes shoot_pull on every call, growing sys.path by one entry each time; same issue also at 48: Re-executing shoot_pull.py on every _shoot_tools call grows sys.path by one duplicate entry per call
- `release_manager/views/shoot.py:144` _edit_recipe caches a half-initialised module if exec_module raises, breaking every photo page until restart
- `release_manager/views/shoot.py:169` Background grade jobs swallow every exception: a failing grade never surfaces; same issue also at 170: Background grade futures are discarded, so any failure in a warm-up grade is swallowed silently
- `release_manager/views/shoot.py:567` photo_editor_save converts untyped JSON params with int()/float() and returns a 500 on bad values instead of a JSON error
- `release_manager/views/shoot.py:573` Saved-copy filename has one-second resolution and is written without an existence check, so a same-second save overwrites the previous copy and its record
- `release_manager/views/shoot.py:599` /edit/delete given the .json record moves only the record, orphaning and hiding the image
- `release_manager/views/shoot.py:609` photo_editor_delete given the .json record moves only the record and leaves the .jpg copy orphaned
- `release_manager/views/studio.py:418` One malformed HyperFrames project folder breaks the whole /video page
- `release_manager/views/studio.py:567` Non-numeric trim values raise an unhandled ValueError (500) in the video resizer POST
- `release_manager/views/words.py:44` Words page indexes metadata.title and metadata.release_type directly, so one malformed release file takes down /words, /seo-copy and /bios
- `release_manager/views/words.py:84` A writer's ValueError is passed through unlabelled and unlogged, so a malformed GPT/Claude reply shows up as a bare json error
- `release_manager/views/words.py:96` `.strip()` on request JSON values crashes with AttributeError when the value is null or a number
- `release_manager/views/words.py:328` PUT /api/bios/profile replaces the whole links dict, so a partial links payload deletes the other links
- `scene_intelligence/archive/UNDO-nina-move-2026-10-10.sh:3` Undo script uses plain mv, which silently overwrites any same-named file recreated in scene_intelligence/
- `scene_intelligence/ig_merge_session_log.py:630` Queue write assumes a `_meta` object exists in ig_target_list.json
- `scene_intelligence/ig_reciprocity_from_lists.py:103` Same-day backup name is overwritten by a second run that day
- `scene_intelligence/sc_buy_links.py:189` The write PUT bypasses the guarded-request layer the module header promises
- `scene_intelligence/sc_buy_links.py:219` apply accepts any plan file; the 'waiting for Amir's go' status is never checked or flipped
- `scene_intelligence/si_follow_flags.py:198` Backup copy assumes scene_intelligence/backups/ exists (gitignored), no mkdir before copy2
- `stats/bandcamp_import.py:145` An unexpected date format silently yields first_sale == '' and a '(none)' month bucket
- `stats/collectors.py:293` A null playback_count or likes_count on one SoundCloud track skips the whole SoundCloud block for the day
- `stats/daily_brief.py:290` The 20:00 brief rewrites the hand-maintained System handover in place with no backup and no atomic rename
- `stats/daily_sync.py:61` '--skip' given as the last argument crashes with IndexError before any collection
- `stats/ig_token_refresh.py:103` plan() raises on a malformed date in the state file, so the daily launchd run tracebacks with no notification
- `stats/propose_targets.py:102` --set-ig-baseline tracebacks instead of printing a message when the baseline is already set
- `stats/socials_digest.py:50` _counts lets \s* cross a line break so counts can be read from the following line
- `stats/socials_digest.py:123` yt_line counts directories and stat()s every entry of ../youtube/backups unguarded
- `stats/socials_digest.py:149` _latest_snapshot_value crashes on a snapshot whose platforms is null
- `stats/storage.py:54` Two snapshots saved in the same second overwrite each other
- `stats/storage.py:85` list_snapshots silently drops any snapshot that fails to parse
- `stats/storage.py:138` Caller data can overwrite the entry's platform/date/timestamp/source
- `tools/chrome_queue.py:80` A corrupt lock.json or queue.json makes every CLI command crash and the live hook fail open silently

### dead-code (60)

- `bandcamp_links.py:78` Redundant None guard in _release_url
- `daily_digest.py:0` Batch file does not exist in the working tree or any git ref
- `deploy/retired/daily-brief.sh:0` Batch file does not exist in the working tree or any git ref
- `fonts_library.py:146` migrate() and its alias tables are dead since fonts.json exists
- `gap_radar/gap_radar.py:344` Batch file gap_radar/sources.py does not exist on score-board (or main); the live module is sources_extra.py
- `music-tools/drumrack/drumrack_tool.py:451` --tune-root is parsed and passed but never used
- `music-tools/drumrack/drumrack_tool_v2.py:2` Three .bak copies of this script are tracked in git next to it
- `music-tools/drumrack/drumrack_tool_v2.py:388` MINCONF constant in the audition page JS is never used
- `music-tools/drumrack/snare_pitch/build_cc_racks.py:5` Unused import math
- `music-tools/drumrack/tools/cc_mapper.py:0` Six of the seven batch paths do not exist on score-board (or in any branch's history)
- `music-tools/drumrack/vocal_keys/key_check.py:25` First parse_key regex is dead code; its looser conventions ('m' suffix, space-separated key) are not supported by the live regex
- `music-tools/dupes/scan_dupes.py:4` Unused import sys and unused loop index i
- `plans/ig-like-list-2026-11/find_handles.py:8` datetime and timezone are imported but never used
- `plans/outreach-page/history.py:63` Dead expression: a 200-character regex/list-comprehension guarded by `if False else None`
- `plans/outreach-page/outreach.html:141` Batch manifest names two files that do not exist on score-board: outreach.js and research-fetish/_build/build_page.py
- `plans/outreach-page/recovered/index.html:79` Field draft is present on all 114 cards but never read
- `qa_outreach.py:1` Seven batch paths do not exist on score-board, main, or any commit (manifest error, not a code defect)
- `references/look02/logo_round_f.py:45` Dead computations in reflection() and light_and_shadow()
- `references/look02/logo_round_f.py:58` light_and_shadow builds two text masks that are immediately overwritten; reflection builds an unused 'fade'
- `references/look02/logo_round_g.py:34` label_tape: the 'serrated ends' loop is an empty pass loop
- `references/look02/moon/moon.py:70` wordmark's caps parameter and the ImageFilter import are unused
- `references/look02/v2/logo_v2.py:187` bitmap(): tile, f and dd are built and then discarded
- `release_manager/display.py:1` display.py is dead in the live tree: nothing outside archive/ imports it
- `release_manager/outreach.py:14` CHANNELS is dead: contact channels are never checked against it
- `release_manager/outreach.py:158` ig_handle is computed per contact but never used
- `release_manager/playground.py:469` looks() and look_image() insert into sys.path on every call and re-import os inside functions
- `release_manager/review.py:816` sort_key() is dead code and load_all()'s docstring describes a refresh it does not do
- `release_manager/score_board.py:100` The release slug added by _release_series is dropped before any caller sees it
- `release_manager/score_board.py:325` Dead assignment in the floor branch of _card
- `release_manager/score_board.py:475` ladder_svg takes a `today` parameter it never uses
- `release_manager/static/app.js:38` Mobile nav toggle block is dead: base.html has no #nav-toggle / #nav-links
- `release_manager/static/app.js:224` Release-card menu and delete handlers bind to markup no template renders
- `release_manager/static/app.js:228` Release-card 3-dot menu and delete handlers are dead: no template renders .card-menu-btn / .release-card-wrap
- `release_manager/static/style.css:2177` Dead responsive blocks for a top nav and an old stats layout that no template renders
- `release_manager/static/style.css:6492` `.cover-type` is styled in full and then unconditionally hidden 27 lines later; the class is used by no template
- `release_manager/templates/effect_detail.html:18` The recipe table block is dead: no effects record carries a recipe field
- `release_manager/templates/photo_editor.html:6` data-reveal attribute on #ed is never read by photo_editor.js
- `release_manager/templates/playground.html:53` brand.playground.title in the release file is never read; the title field is seeded from metadata.title only
- `release_manager/templates/playground.html:540` The 'applying' guard in saveState never fires because draw() is deferred to requestAnimationFrame
- `release_manager/templates/playground_layout.html:486` Unreachable `else if (false)` branch left in the per-pixel loop
- `release_manager/templates/playground_layout.html:659` IG grid drawing code, its CSS and the igfeed context are dead: no #igg element exists on this page
- `release_manager/templates/playground_layout.html:759` Hidden colour-save column is still fully rendered and resized on every load
- `release_manager/templates/playground_layout.html:1034` Dead assignments and unused variables; same issue also at 1035: TSKIP is computed and then immediately overwritten
- `release_manager/templates/playground_wall.html:476` Hidden effect <select> and its onchange handler are dead code
- `release_manager/templates/release.html:1` File named in the batch does not exist on score-board or main
- `release_manager/templates/score_board.html:1` File named in the batch does not exist on score-board or main
- `release_manager/views/shoot.py:416` POST /shoot/<photo_id>/pull is not reachable from any template or script
- `release_manager/views/shoot.py:594` Duplicate `import shutil` inside photo_editor_delete
- `release_manager/views/words.py:128` Redundant local alias of SEO_FIELD_MAP
- `release_manager/webapp.py:15` Most module-level imports are dead after the RM 2.0 split
- `scene_intelligence/archive/UNDO-nina-move-2026-10-10.sh:1` Six of the eight batch paths do not exist on score-board or in any git history
- `scene_intelligence/ig_ops_guards.py:104` Unreachable `return None` after the return in blocks_sessions
- `scene_intelligence/sc_buy_links.py:1` Four of the five batch files do not exist on score-board or anywhere in git
- `scene_intelligence/si_cleanup.py:110` `bid` is assigned and never used.
- `scene_intelligence/si_follow_flags.py:122` pull() takes an unused `side` argument and apply()'s return value is never used
- `stats/collectors.py:489` collect_instagram() is dead code and violates the module's own skipped-contract
- `stats/storage.py:96` load_snapshot has no callers
- `stats/storage.py:245` get_growth compares an Instagram key ('recent_reach') that snapshots never contain
- `stats/weekly_view.py:191` Dead conditional: both branches yield 'weeks'
- `tests/test_stats_page.py:52` Redundant local import of score_board already imported at module level

### tests (71)

- `gap_radar/profile_check.py:76` The only network-facing logic (_reddit_exists, _se_exists) has no tests
- `music-tools/drumrack/snare_pitch/cc_style_match.py:8` No tests for feats()/note() although three scripts and the rack plan depend on their numbers
- `music-tools/drumrack/tests/test_detect_type.py:7` Only detect_type is tested; select_max, build_branch, load_picks and process_machine have no tests
- `plans/review-page/read_ticks.py:1` No test covers read_ticks.py or gen.py; only import_ticks is tested
- `release_manager/checklist_formats.py:1` Six of the eight files assigned to this batch do not exist on score-board (batch manifest is stale)
- `release_manager/outreach.py:25` No tests cover validate, build_view or set_try
- `release_manager/stats_page.py:1` Six of the eight batch paths do not exist in the repository or its history
- `release_manager/templates/playground_layout.html:1047` No tests cover the tournament bracket, A/B, kept round-trip or layout state logic
- `release_manager/views/release.py:600` No test covers track_delete together with a clips block, or the resizer POST with a real image
- `release_manager/views/words.py:92` No tests cover the single-writer SEO save path or the bios undo/applied/profile routes
- `release_manager/views/work.py:95` No test covers POST /outreach/tick or outreach.set_try, the only write on the Outreach page
- `scene_intelligence/ig_daily_ledger.py:364` No test covers the --claim CLI, release_claim or the provider cap, although they are live paths
- `scene_intelligence/ig_health_check.py:49` All checks run at import time, so the script cannot be unit-tested and has no tests.
- `scene_intelligence/ig_reenrich_contacts.py:67` pick_batch, _is_guard_held and apply_profile have no tests; main's save path is untested
- `stats/bandcamp_import.py:163` No test exercises parse_bandcamp_csv or a campaign value in a real-format referrer
- `tests/conftest.py:1` Four files of this batch do not exist on score-board
- `tests/test_archive.py:1` Six of the eight files in this batch do not exist on any branch.
- `tests/test_archive.py:33` Real-index test indexes r["thumb"] although thumb is optional in the schema and the route
- `tests/test_archive.py:145` New test hardcodes live artwork and archive content that the nightly heartbeat suite then depends on.
- `tests/test_artwork_resizer.py:148` The --cover test re-implements the profile filter instead of exercising main()'s
- `tests/test_bandcamp_links.py:53` No test for the --channel subset on a release that already has links, nor for _targets/_release_url/main
- `tests/test_bandcamp_supporter_match.py:111` main()'s write path is never tested; only --dry-run is covered
- `tests/test_brand_context_writers.py:20` Nightly test asserts on live, hand-edited data (pinocchio-single.json genres, proof.md venue list)
- `tests/test_checklist_formats.py:56` The 'old releases stay as they were' test only uses template-generated items, so the real data-loss case is untested
- `tests/test_checklist_formats.py:64` Two checklist tests depend on a file outside the repository and skip silently when it is absent
- `tests/test_close_loops.py:26` Several IG scoring tests read the live phase config and the live ig_follow_tracker.json instead of fixtures
- `tests/test_daily_brief.py:138` Detection-word test covers only the 'no <word>' form, not the 'Word: none' checklist the real SC reports use
- `tests/test_daily_brief.py:181` Proposal-placement test does not cover the heading phrase appearing in prose before the real heading
- `tests/test_dashboard_lines.py:10` Home test asserts live backup and board data instead of fixtures
- `tests/test_decisions_writeback.py:60` Assertions are pinned to the current contents of the live tickets and targets files
- `tests/test_decisions_writeback.py:88` Test writes to ticket G-15, which left plans/tickets.json on 2026-11-07, so the test fails
- `tests/test_dispatcher.py:35` Nightly test suite writes a junk seed-yield report into the real docs/reports folder
- `tests/test_dispatcher.py:107` Builder-branch tests write a real report file into docs/reports/ on every run
- `tests/test_dispatcher.py:201` get_pause patch on the dispatcher module is a no-op; provider-day tests read the live autonomy_state.json
- `tests/test_fonts_page.py:25` test_the_real_index_is_valid_and_its_files_exist can only pass on this Mac: the index points at gitignored trial fonts; same issue also at 28: Tests pin curated fonts.json data that changes by design
- `tests/test_freeze.py:30` monkeypatch of freeze.GATES_DIR does not reach freeze()'s default argument
- `tests/test_freeze.py:90` freeze.main bypasses the patched GATES_DIR and reads the real gates file
- `tests/test_gap_radar_profile_check.py:65` import claude_api only resolves through another test module's sys.path side effect
- `tests/test_gap_radar_schedule.py:1` schedule.main() has no test: the state write, the SystemExit isolation and the dry-run path are untested
- `tests/test_gap_radar_sources_extra.py:108` github error path and stackexchange backoff untested
- `tests/test_home_page.py:8` Test asserts on the live ticket board, so the nightly suite goes red on a data state
- `tests/test_ig_followback.py:34` Reproduction test hard-codes cohort counts against the live, mutable follow tracker
- `tests/test_ig_token_refresh.py:75` Refresh failure paths of run() untested
- `tests/test_in_session_vet.py:53` No test covers the keep-pending (button_missing) reach-skip branch of the queue sync
- `tests/test_ledger.py:1` Four batch test files do not exist on score-board (or in any commit)
- `tests/test_photo_editor_page.py:13` Traversal assertion for /edit is satisfied by the extension filter, not by traversal blocking; same issue also at 15: Preview test writes into the real ~/.cache and depends on the live artwork/ folder
- `tests/test_playground.py:35` client fixture disables CSRF and sets TESTING on the shared app for the rest of the session
- `tests/test_playground.py:151` Nightly tests hard-depend on specific production artwork files and releases
- `tests/test_review.py:270` Handles test never exercises known_handles() on the real tracker files
- `tests/test_review.py:277` No test covers the file-appears-after-submit path or the script-style CLI invocation
- `tests/test_review.py:538` Client fixture disables CSRF and sets TESTING on the shared app without restoring
- `tests/test_review.py:635` The --demo CLI test and the ?demo=1 page test leave media temp dirs behind every nightly run
- `tests/test_sc_buy_links.py:1` Tests cover only the pure mapping helpers; apply(), changed_fields(), record(), plan() and latest_snapshot() have no tests
- `tests/test_sc_follow_tracker.py:1` Two files named in this review batch do not exist on score-board
- `tests/test_sc_supply_aware_score.py:84` Test input exceeds the current follow cap, so it exercises a cap-violation day instead of the clean 50-click day it describes
- `tests/test_score_board.py:1` No test covers a malformed targets.json baseline/floor or malformed state files in _health
- `tests/test_score_board.py:217` D4 row test pins live S4A and manual-entry data, so the next Monday S4A read turns the nightly heartbeat red
- `tests/test_score_board.py:253` Release-source test asserts the live releases/ folder has no day-28 read, and its RELEASES_DIR monkeypatch is a no-op
- `tests/test_spend.py:53` HikerAPI fixtures use a timestamp shape the real snapshots never have
- `tests/test_stats_bandcamp_card.py:34` Test sets app.config['TESTING']=True on the shared Flask app and never restores it; same issue also at 35: Bandcamp card page test renders the whole live /stats page, so unrelated live-data errors fail it
- `tests/test_stats_page.py:1` Four of the eight batch files do not exist on score-board (not reviewable)
- `tests/test_stats_page.py:24` GET /stats in the tests fetches thumbnails from the network and writes into the repo
- `tests/test_stats_page.py:39` Nightly stats page tests are pinned to live data and a hard-coded CSS version string
- `tests/test_stats_page.py:44` Stats page tests assert the current live data state, so they go red as the data moves
- `tests/test_targets.py:48` Targets tests assert the exact live metric set and rung values of plans/targets.json
- `tests/test_targets.py:77` Tests pin live target values that the targets file itself says will change
- `tests/test_tickets.py:290` Section ordering test depends on the current buckets of R-01 and R-05
- `tests/test_tickets.py:328` Raw-text assertion against JSON-escaped card data
- `tests/test_tickets.py:432` Live-data test fails on a calendar date: no rung after 2026-12-31
- `tests/test_tickets.py:441` By-number route tests pin live ticket ids that vanish when those tickets are closed
- `tools/prune_bak.py:29` No test covers prune_bak (candidates age cut-off, trash_target collisions, undo output)

### style (73)

- `bandcamp_links.py:128` Positional target is silently ignored when --write is given
- `caption_check.py:185` HASHTAGS FAIL note states a false fact ('Instagram's cap is 5')
- `docs/reports/m5-undo-2026-11-07.sh:34` The A2 si-sheet undo block was appended after the final 'M5 moves undone' message and leaves archive/si-sheet/README.md behind
- `fonts_library.py:351` An unknown subcommand silently runs 'check' and exits 0
- `gap_radar/profile_check.py:146` keyword_yield re-tokenises every post for every keyword
- `gap_radar/schedule.py:102` Run label says 'weekly' for a monthly run when crowding is set to never
- `gap_radar/schedule.py:156` Exit code is 0 even when every profile failed or was skipped
- `hygiene_check.py:39` The scan walks the worktree copies under .claude/worktrees, so hits are reported several times
- `music-tools/drumrack/drumrack_tool_v2.py:273` Shell-pitch tagging of snares/claps contradicts the README and the scan summary count
- `music-tools/drumrack/misc_fix/identify.py:81` Existing-file numbering is re-globbed once per result row
- `music-tools/drumrack/misc_fix/identify.py:92` misc_renames.json written through an unclosed file handle
- `music-tools/drumrack/serum_sort/rename_inside.py:21` Chunk name field offset is hard-coded and only guarded by total chunk length; docstring and code disagree on its width
- `music-tools/drumrack/serum_sort/undo_moves.sh:5` Undo script deletes the Serum 1 copies with rm instead of moving them to the Trash
- `music-tools/drumrack/snare_pitch/body_pitch.py:2` Docstring describes the low band as <400 Hz but the code uses 60-400 Hz
- `music-tools/drumrack/snare_pitch/body_pitch.py:21` Import placed at the bottom of the module
- `music-tools/drumrack/snare_pitch/compare_wh_rack.py:6` Helpers are imported by exec-ing a text slice of cc_style_match.py up to the first '\nCC='
- `music-tools/drumrack/snare_pitch/undo_cc_racks.sh:1` Shebang but file is not executable (mode 644); must be run as `sh undo_cc_racks.sh`
- `music-tools/dupes/scan_dupes.py:24` SKIP check uses continue without pruning os.walk dirs, so excluded trees are still walked
- `music-tools/dupes/scan_dupes.py:53` Output file and gzip handles are opened without a context manager
- `music-tools/samples_audit/samples_audit.py:1` Batch file does not exist in the working tree or in any git history
- `music-tools/samples_audit/undo_move.sh:1` Batch file does not exist in the working tree or in any git history
- `plans/ig-like-list-2026-11/check_like_targets.py:1` Batch manifest names six files that do not exist on score-board (not a code defect)
- `plans/outreach-page/dj07_check.py:7` Docstring says passed contacts are skipped, but queue() has no status filter
- `plans/outreach-page/outreach.html:93` .sub is defined twice; the later uppercase heading rule overrides the intro paragraphs
- `plans/outreach-page/recovered/index.html:72` No filter chip or legend entry for score 1 although three cards carry score 1
- `plans/outreach-page/research-fetish/_build/make_entries.py:31` Wasteland Berlin entry uses "" for a missing ra_url where every other entry uses None
- `plans/outreach-page/research-fetish/_build/make_entries.py:42` Output path is hard-coded to one machine and the file handle is never closed
- `plans/outreach-page/research-mixseries/build.py:25` Place cell for Intergalactic FM renders the same text twice
- `plans/review-page/gen.py:124` Every 'render' gets the 9:16 'tall' thumbnail box regardless of its real aspect ratio
- `plans/review-page/read_ticks.py:59` Release file is re-saved (reconcile, updated_at bump, daily .bak) even when every tick was already consumed
- `plans/strategy/drafts/launchd/sc_refresh.sh:13` Header comment points at the wrong line of stats/socials_digest.py
- `plans/strategy/drafts/launchd/sc_retry_gate.sh:23` Retry-gate log name escapes the launchd-log gitignore and differs from the plist's log path
- `plans/strategy/refresh-page/index.html:386` Card data contradicts itself: M4 is 'Batch 4' and '✅ Done 7 Nov', D9/M7 shown both open and done
- `references/look02/INDEX.md:3` INDEX.md points at scripts/ as the runnable set, but scripts/ no longer holds any script
- `references/look02/all_picks.py:67` Last picks_in_place row: the T-shirt mock-up runs past the sheet and the 'T-shirt' caption is drawn over it
- `references/look02/all_picks.py:75` all_picks.py and families.py run main() at import time with no __name__ guard
- `references/look02/logo_round_g.py:2` Unused imports: math, shift, INK
- `release_manager/outreach.py:3` Docstring and data 'about' say the page never writes, but set_try writes the batch file
- `release_manager/playground.py:586` layout_snap_save stores every release's snaps under the hard-coded htn-noir folder
- `release_manager/review.py:300` Approve refusal says 'file changed after approval' for items never approved
- `release_manager/review.py:646` known_handles() is rebuilt per item: two 1.5k-entry JSON reads and a git subprocess each time
- `release_manager/review.py:732` load_all() docstring claims the hash check is refreshed in memory; the function does no refresh
- `release_manager/score_board.py:66` Snapshot series use the wall clock, not build(now=...)
- `release_manager/score_board.py:575` build() re-reads and re-parses every snapshot file once per metric
- `release_manager/shoot_board.py:1` Batch file release_manager/shoot_board.py does not exist on score-board
- `release_manager/static/app.js:270` showToast called with boolean true as the type, producing class 'toast-true'
- `release_manager/static/style.css:2256` `var(--accent)` is never defined, so the Words/SEO page loses its selected-state and warning colours
- `release_manager/static/style.css:6281` `var(--font-body)` and `var(--bg-main)` are undefined custom properties
- `release_manager/static/style.css:6681` `var(--border)` is never defined, so every `border: 1px solid var(--border)` shorthand collapses to no border
- `release_manager/templates/_words_seo.html:2` SEO tab says generated copy is 'never stored' but /api/seo-copy/generate saves it into the release JSON
- `release_manager/templates/photo_editor.html:60` Preview edge 1600 is hardcoded in the template instead of using EDIT_PREVIEW_EDGE
- `release_manager/templates/playground_wall.html:364` Title-size slider redraws tiles and the big view but not the kept strip or the IG-grid float
- `release_manager/templates/review.html:138` Key press during an in-flight tick replaces the status with the button's hotkey letter
- `release_manager/templates/sc_automation.html:88` Page text claims auto-unfollows and an engine run on a page that declares itself read-only
- `release_manager/views/release.py:105` Raw exception text (with internal file paths) is rendered to the client on Home and the resizer page
- `release_manager/views/release.py:410` copyright is the only edit-form field that cannot be cleared
- `release_manager/views/shoot.py:424` Unknown photo id on /shoot/<id>/pull returns 400 instead of 404
- `release_manager/views/shoot.py:485` Module constants EDIT_PREVIEWS / EDIT_PREVIEW_EDGE glued to the end of _edit_copies without a blank line
- `release_manager/webapp.py:10` Docstring usage and the repo_root comment are stale
- `scene_intelligence/ig_reenrich_contacts.py:225` A breaker stop or an all-failed batch still exits 0
- `scene_intelligence/si_cleanup.py:314` SI master and plan files are written without an explicit encoding.
- `scene_intelligence/si_follow_flags.py:149` _write duplicates json_io.atomic_write_json with a weaker variant (temp file left behind on failure, 0600 mode)
- `shadow_archive.py:44` render and next-id let ArchiveError escape as a traceback while check reports it cleanly
- `shadow_archive.py:60` An unknown subcommand silently runs 'check' and exits 0
- `stats/socials_digest.py:148` Snapshot and tickets files are opened without being closed
- `tests/test_dispatcher.py:11` Module imported twice under two names (disp and _disp) and pytest imported twice
- `tests/test_gap_radar_profiles.py:68` Monkeypatching gr.HERE makes collect() leave a pytest tmp dir on sys.path for the session
- `tests/test_in_session_vet.py:109` Stale comment: says the live per_session value is a temporary 15, config is back to 6
- `tests/test_playground.py:144` Redundant in-function `import pytest` and reliance on the module's re-exported Path
- `tests/test_registry.py:108` No-op assertion that also reads the clock in a test file declared clock-free
- `tests/test_spend.py:225` Em-dash check depends on column widths mod 3
- `tests/test_tickets.py:1` Module docstring is not a docstring: import placed before it
- `tools/prune_bak.py:4` Docstring misstates who writes the .bak files; IG tracker restore points are swept too

## Refuted (10)

Reported, then rejected by two or more of three refuters. Listed so nobody re-finds them.

- `music-tools/drumrack/misc_fix/apply_racks.py:22` Sample files are renamed before the rack rewrite can fail, leaving a broken rack with no undo. Why: The code order is as described: for each machine the .wav/.asd renames (lines 22-23) happen before the rack is backed up, decoded and rewritten (lines 25-31), so an exception in that block would leave renamed samples and an unchanged rack. But the defect is not reachable in practice. (1) Thi
- `music-tools/drumrack/snare_pitch/compare_wh_rack.py:16` Input/output CSVs are opened relative to the CWD while the sibling module is resolved via __file__. Why: The mechanics the finding describes are accurate (line 16/17/24 open bare names resolved against the CWD, while line 5 locates cc_style_match.py via __file__), but it is not a defect in context. Every sibling script in music-tools/drumrack/snare_pitch/ uses the same convention of bare CSV na
- `music-tools/dupes/scan_dupes.py:44` Reference check only reads <Path Value>, so projects saved in Live 10 or older format are invisible. Why: The format claim is accurate in the abstract (Live 10 and older .als files store sample refs as RelativePathElement/Name and have no <Path Value>), and line 44 does read only <Path Value="...">. But the defect is not reachable with the inputs this script actually scans. I decompressed every
- `plans/ig-like-list-2026-11/check_like_targets.py:63` Ledger claim is written before Provider() can fail on a missing key, burning the once-a-day slot and the call budget. Why: The code order is as reported (plans/ig-like-list-2026-11/check_like_targets.py lines 63-65: check_and_claim, then Provider()), but it is not a defect against this codebase's own rules. scene_intelligence/ig_daily_ledger.py's module docstring states the law explicitly: "Every IG API entrypoi
- `plans/outreach-page/recovered/index.html:160` DB snapshot replaces the ticks baked into the card data, so 29 preset decisions vanish once the page connects. Why: The code path is as described (line 83 seeds ticks from the embedded JSON; the onSnapshot callback at line 157-160 does `ticks = next; paint()` with only DB documents), but it is the intended design, not a defect. The page's own subtitle says "Ticks save on this page": the db `ticks` collect
- `release_manager/core.py:43` CSRF protection silently disappears if Flask-WTF fails to import. Why: The try/except fallback exists as described (core.py:41-44, 103-104), but the finding's central claim, that the loss of CSRF is silent and that nothing at startup or in the tests would reveal it, is false. CSRFProtect is also what registers the `csrf_token` Jinja global, and release_manager/
- `release_manager/templates/playground_wall.html:260` Kept state and toggle ignore the palette, so a pick kept with R. Missing is un-kept from the original-colour view. Why: The mechanics the finding describes are accurate: isKept (playground_wall.html line 260) and the server's wall_toggle (playground.py lines 136-139, key = (cover, look)) ignore palette and wet, variant() only rewrites cover names for role colours (moonlit etc.), so with the ledger's {1a-red-o
- `release_manager/templates/playground_wall.html:262` Wall keep/remove POSTs send no CSRF token, so the global CSRFProtect refuses them and the page swallows the error. Why: The POSTs do carry a CSRF token. playground_wall.html extends base.html, and base.html renders `<meta name="csrf-token" content="{{ csrf_token() }}">` (line 6) and loads release_manager/static/app.js synchronously at the end of body (line 103). app.js lines 5-33 install a global `window.fetc
- `stats/bandcamp_import.py:188` Campaign detection only reads the classified 'referrer' column; the item-url query is stripped and 'referrer url' is never read. Why: The finding is a conditional hypothesis ("if the campaign parameter surfaces in item url or referrer url rather than in the referrer label"), and nothing in the code or data confirms that condition. The project's own research note (plans/bandcamp-discovery-research-2026-10-21.md line 53) cit
- `stats/collectors.py:705` Ledger claim hardcodes script='stats_daily_sync' for every caller, so the webapp Sync button and the launchd daily sync block each other's Instagram read. Why: The mechanics are as reported (stats/collectors.py:705 claims script="stats_daily_sync" for every caller; ig_daily_ledger._claim_provider refuses a second same-day claim of the same script; release_manager/views/stats.py:62 and :98 call collect_all()), but this is the documented, deliberatel

## Numbers

| | |
|---|---|
| Files in scope | 231 (plus imported files the reviewers opened) |
| Confirmed findings | 150 |
| Blocking | 19 |
| Non-blocking, verified | 131 |
| Non-blocking, low, not verified | 397 |
| Not verified (limit) | 26 |
| Refuted | 10 |

