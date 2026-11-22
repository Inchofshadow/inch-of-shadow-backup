# 🎬 Socials: IG agent handover

Chat: IG agent (Instagram engagement + SI upkeep on HikerAPI). Written 2026-11-05.

## Where things stand

- IG sessions run normally again: Mon/Wed/Fri/Sat at 15:00 Berlin. The pause from 11-04 was cleared and the `ig-engagement` task was turned back on.
- New caps since 2026-11-04 (Amir: "Yes, run it"): **12 likes / 16 follows / 8 unfollows**. Before that the caps were 6 / 12 / 15. The backup is `scene_intelligence/backups/ig_engagement_config.pre-caps-2026-11-04.py`.
- First session on the new caps (Wed 11-04, 17:14-17:52) scored 10/10: 16/16 follows, 7/7 unfollows, 5/12 scene likes + 1 prominent like. The likes fell short because 7 of the 12 scene accounts were inactive, private or gone. There were no IG popups or warnings.
- Unfollows no longer wait for the IG export. The tracker gets follow-back verification from the HikerAPI follower list (🎬 Socials 26).
- Vetted follow pool: 15 → **39** after a manual freshness audit (100 checked, 57 fresh, 32 stale, 8 retired). 461 accounts are still unchecked. The dispatcher re-audits automatically once the pool drops below 30.
- HikerAPI: about 83.6k requests of balance, cap 300/day.

## Decisions made (this chat)

- Unfollow verification comes from the HikerAPI follower list. Accounts that are absent from the list are trusted as non-followers only when the list is complete and within 2% of the profile count. Present = followed back.
- Own follower/following lists are refreshed **weekly** (about 50 calls). The dispatcher runs SI follow flags first, then the follow-back verification, then the contact re-check.
- The SI contact re-check runs on HikerAPI (up to 40 a day, inside the 300 cap). A handle is flagged dead only after "missing" on two different days.
- HikerAPI above 300/day: ask Amir with a reason each time.

## Open decisions (Amir)

- @justbedeadon was followed in the 11-04 session, but the bio is personal and political, not music. Keep or unfollow? This is Amir's call.
- The scene like list is stale (7 of 12 were dead on 11-04). It needs a refresh of the scene/T1-T2 like targets, or a lower likes cap.
- 🎬 Socials 21 (session profile checks 15 → 6) is still only approved.
- 🎬 Socials 23 (Claude scene-fit score on the unvetted queue) is still only approved.

## 🎬 Socials 27 · Instagram like list refresh (2026-11-06)

- Checked 63 like targets on HikerAPI (122 calls, read-only): 42 active, 20 to remove (2 T1/T2, 18 T3).
- Cause: only 23 SI contacts fit T1/T2, all on cooldown, so the engine falls back to T3 (budget 0%). The list supports about 2 likes per session against a cap of 12.
- Proposal + raw data: `plans/ig-like-list-2026-11/proposal.md`, `like_targets_check.json`. Nothing written to engagement data.
- 2026-11-06 13:10 Amir "b": likes 12 -> 3 (e6e592c), then REVERTED at 13:20 (3c46084): Amir wants MORE likes, he misread option B. Cap is 12 again.
- Amir "Yes, take them off" (the 20): done for 3 via SI fields (backup `scene_intelligence/backups/enriched_contacts.json.bak.20261106_socials27`): piecinski + thisisdjkitty `ig_is_private`, xmtsk `ig_handle_dead`. SI file not committed (live data, other chats' changes mixed in).
- Open: the other 17 (16 inactive + gesloten_cirkel, no posts) need a field the engine skips. The `hidden` list in engagement_log.json is also read by sc_engagement.py, so it was NOT used. Needs a small engine change (skip "no post in 90+ days") = engagement code, ask Amir.
- 2026-11-06 Amir "Yes, find more": handle search on 45 SI contacts (109 calls) -> 3 confirmed. Amir "Yes, add the 3": @mori_ra (T1), @fane.e.label (T2), @alfamatrix (T2) written to SI 13:18 (backup `enriched_contacts.json.bak.20261106_socials27_add3`, field `ig_handle_source`). If an SI sheet sync ever overwrites SI, re-check these 3.
- Score 4-5 SI list is nearly used up; more like targets need new SI contacts (not started, Amir's call). Labels 5k-8k left out by the 5,000 label ceiling (aufnahme + wiedergabe, Sonic Groove), Amir's call.

## ⚙️ System 69 · Python 3.9 -> project venv (DONE 2026-11-11)

- DONE 11-11 21:20 by the System 69 side chat on Amir's "do it now" (no need to do it on Sat 11-14). Record, checks and undo lines: `plans/strategy/system-69-python-switch-2026-11-08.md`, section "IG + SC part moved". Read the first live runs (Thu 11-12 SC 06:30-10:00, dispatcher 09:30; IG Fri 15:00). A run stuck on an approval = add the `.venv/bin/python` prefix rule for that command.

## IG ratio 1.2:1 by Dec 31 (asked by ⚙️ System 11-12)

- Plan: `plans/ig-ratio-plan-2026-11-12.md`. Found: unfollows stalled since 11-06 because the 11-10 follower list had 103 duplicates (876 unique of 992), so the follow-back check refused it; si_follow_flags applied it anyway (row count, not unique) and flipped 8 SI "follows you" flags. Amir chose B ("go", 11-12).
- Done 11-12: si_follow_flags dedupes rows and checks coverage by unique names (fetch refetched 11-12: v1 gave 286/993, g2 gave 689 unique of 992 rows, so HikerAPI follower paging is unreliable). Picks list = following 11-12 minus union of follower lists 11-03/11-10/11-12 minus engine follows, personal, keeps, blocked, outreach: 322 (122 SI contacts, 77 verified). Files: plans/ig-sweep-2026-11/ (build_list.py, candidates.json, build_page.py). Picks page https://claude.ai/artifact/8W74pNWcQcfxa4ZnGdyQuu (db collection `picks`, doc id = IG user_id, choice keep|unfollow), source plans/ig-sweep-page/index.html.
- 11-12 Amir "sort them better" + "Yes, fetch them": profiles on HikerAPI (fetch_profiles.py -> profiles.json; 100 done 11-12, one-time tasks ig-sweep-profiles-fri-1113 / -sat-1114 at 11:30 fetch the rest + rebuild + republish). Page v3 groups by IG account type, biggest first, two-tap 'mark all open as unfollow' per group. teder.fm tagged 'your radio?' (ask Amir).
- 11-12 Amir "Yes, pre-mark": rule = keep songs lane/bands (bio keywords or Musician/band under 20k) + small scene (music account, SI score 4-5, under 10k); unfollow big (10k+/verified), other, gone/private. Suggestions live in the page source only (field s), NOT in db; db `picks` = his taps, which win. First 100: 29 keep / 71 unfollow. At go time, final list = his picks + suggestion for unpicked rows (confirm with him).
- 11-12 Amir "check no one I messaged for booking gets unfollowed": cross_check.py (DM threads in the 4 IG exports with an inbox, only participants + sender counts read; handles/names in outreach-batches, promotion_log, dj_promo_targets, booking + outreach md files) -> 86 of 322 matched, own page section, suggested Keep. 7 of his 11 unfollow taps are contacts (mosaique_records, dollkraut, juniorfairplay, 030303records, oxi_club, identified_patient, ruben_keyko): his taps stand unless he flips them. 10-10 export has no inbox, so DMs after 08-30 are not covered.
- 11-12 picks snapshot (plans/ig-sweep-2026-11/picks_snapshot.json): 77 unfollow / 5 keep. Amir "Leave as unfollow" on the 20 contacts among his unfollow taps (unhumangr, oxi_club, mosaique_records, sinchicollective, tunik303, aya.loveu, dollkraut, shiwabiwa, zivezehu, juniorfairplay, sacredbones, identified_patient, 030303records, lcdsoundsystem, theblocktlv, tai_rona, yehezkelraz, mikeyhoresh, ruben_keyko, orsivan1): don't re-ask. Linked-to-contact rule added (bio tags a contact -> Keep section).
- 11-13 HTN send list (from 🎧 HTN EP DJ promo chat): Amir "the 7 keep only kendel": kendal_ritmofatale -> Keep; 030303records, hilltown.disco, mosaique_records, dollkraut, juniorfairplay, tunik303 stay Unfollow. Amir wants to follow localsuicide, innershades, quadratschulz (verified live 11-13, not followed yet). distantgaze_records: Amir 'mark unfollow' -> plans/ig-sweep-2026-11/extra_unfollows.json (engine-tracked, not on the page). The 3 follows (localsuicide, innershades, quadratschulz): Amir follows them by hand (11-13), no engine change.
- 11-14 Amir "Stop likes too": the 17 going accounts that were like targets got SI ig_blocked=True + ig_blocked_reason (19 SI rows, some handles twice; backup scene_intelligence/backups/enriched_contacts.json.bak.20261114_stop_likes). Only ig_engagement.py reads that field (SC uses ig_blocked_accounts.json, not touched). If Amir flips one back to Keep, remove its flag. List: zaatar___ tunik303 adriani.alessandro unhumangr dollkraut juniorfairplay grammaintel 030303records hilltown.disco discopastors sdh_______ dystopian_vectors downtemporituals tikoa.pnk musar_recordings kotoekk orpheuthewizard.
- 11-14 Amir "sweep plan approve", "A", "approve": sweep runs Tue/Thu/Sun 16:00, 30 per run, 6 runs Tue 11-17 to Sun 11-29; follows 16 -> 10 (f6def47, backup ig_engagement_config.pre-follows10-2026-11-14.py); Dec 5 check (ratio >= 1.2 -> follows back to 16). Build brief plans/ig-sweep-2026-11/BUILD-BRIEF.md; build proposed as its own session (ig-sweep-build, task_f5dea987). First live run only after Amir sees the dry run + Fable read.
- 11-14 evening, sweep build (side session ig-sweep-build): `scene_intelligence/ig_sweep.py` (plan --dry-run / plan --fetch-if-stale / gates / close), `ig_log_action.py --sweep` (own log ig_sweep_<date>.jsonl, track sweep, only unfollow/abort/skip/halt), runbook `docs/cowork-task-ig-sweep.md`, tests `tests/test_ig_sweep.py` (15). Close writes every sweep unfollow to tracker unfollowed_history (source manual_sweep_2026_11) so the engine never re-follows; state in plans/ig-sweep-2026-11/sweep_state.json. Never touches close_loops or the session day gate. Final list 183 (his 237 taps + page suggestions + distantgaze); dry run 11-17: 176 eligible, 30 named, 7 held on HTN files until 12-21 (djhellofficial, matthias.superluminal, identified_patient, adriani.alessandro, grammaintel, discopastors, melaniehavenss; text match, Amir can release). 4 picks sit in unfollowed_history but are still followed (serpientesounds, eid55558.55, djheisa, justbedeadon): planned again. Dry run: plans/ig-sweep-2026-11/dry-run-2026-11-17.md. Each run fetches own lists when > 2 days old (~85 HikerAPI calls). The 6 tasks + allow rules: plans/ig-sweep-2026-11/scheduled-task-prompt.md, NOT created yet (wait for Amir's look at the dry run + Fable read).
- 11-15 Fable gate (plans/strategy/gates/2026-11-15-ig-sweep.md): approve with fixes. Done: fix 3 (live run needs today's picks copy) + fix 4 (blocked plan rebuilt) 3f62af6; fix 1 (Amir "Dispatcher smaller", "Yes, make it"): on the 6 sweep days the dispatcher audits 60 fewer names and skips the SI re-check (SWEEP_DAYS in ig_dispatcher.py, tests/test_dispatcher_sweep_days.py); fix 2 = memory exception (lists stand in for the export, this sweep only).
- 11-16 extra sweep run (Amir, sweep chat): 30/30 unfollowed, 0 Follow Backs, 0 skips, no warnings. Following 1,060 -> 1,030, followers 1,008. Ratio 0.95 -> 0.98. RUN_DATES = 7 runs (11-16 + the 6). New rule (Amir 11-16): every run shows the batch names first and waits for his "go" (runbook step 1d + all 6 tasks). Commits d29c176, cf85dd6. 144 eligible left; run 2 Tue 11-17 16:00.
- 11-15 Amir "Yes, create them": 6 one-time tasks ig-sweep-run-1-1117 / -2-1119 / -3-1122 / -4-1124 / -5-1126 / -6-1129, 16:00 Berlin, saved in Auto mode. Allow rules for ig_sweep.py / --claim ig_sweep / ArtifactData NOT added (the safety check refused the settings edit; Auto mode runs should not need them; Amir adds them if a run stops on a prompt).
- Next: read run 1 (Tue 11-17) report. Then: save bios/contact info of the ticked accounts (HikerAPI, ~1 call each), re-check outreach, plan ~8 extra unfollows per session (needs engine support for untracked unfollows, Amir's go per the engagement-code rule). Engine unfollows (option A part) still stalled: the reciprocity check needs a follower list within 2%; not solved yet.

## Links

- Half the Night Bandcamp pre-order LIVE 11-13. IG links always with a campaign tag, never bare: bio ...half-the-night?campaign=ig-bio, story ...?campaign=ig-story (full list in releases/pinocchio-single.json, c18d301). Bio/profile edits need Amir's yes.

## IG follow pool refill (11-14, asked by 🎬 Socials)

- Pool 0 followable on 11-14 (39 audited pending all rejected: 20 bio too short, 9 SI contacts, rest following too high). Unchecked tail (255) is from the 09-01 builder and yields almost nothing.
- 11-14 Amir "Yes, run it now": cap 300 -> 370 for the day (backup scene_intelligence/backups/ig_engagement_config.pre-cap370-2026-11-14.py), builder on 8 dispatcher seeds: 1,010 names, only 9 new (single-seed names are dropped by the builder's 2-seed rule). Cap restored to 300 right after (config identical to HEAD). Day total 362.
- Sun 11-15 09:00 one-time task ig-pool-refill-sun-1115: builder on 12 best-yield seeds x 400 (~204 calls) + audit up to 40. Mon 09:30 dispatcher audits more. Expected pool by Mon 15:00 ~25-35 (estimate).
- Idea for later (not done, engine code): keep single-seed names that pass the static filters instead of dropping them; the 11-14 run threw away 985.

## Key files

- `scene_intelligence/ig_engagement_config.py`: PHASE_LIMITS[2] caps; PROVIDER.daily_call_cap = 300
- `scene_intelligence/ig_dispatcher.py`: provider day (audit / builder / SI upkeep)
- `scene_intelligence/ig_reciprocity_from_lists.py`: follow-back verification from lists (new)
- `scene_intelligence/si_follow_flags.py`: own lists fetch + SI follow flags
- `scene_intelligence/ig_reenrich_contacts.py`: SI contact re-check on HikerAPI
- `scene_intelligence/ig_follow_tracker.json`, `autonomy_state.json`, `ig_daily_ledger.json`
- Reports: `docs/reports/loop-close-ig-2026-11-04.md`, `docs/reports/dispatch-log.md`

## Not merged / only living here

- Committed on branch `score-board`: 79c51e9 (🎬 Socials 24 + 25) and 500a5f0 (🎬 Socials 26). `main` is 57 commits behind `score-board`.
- The caps change (12 / 16 / 8) is committed: 1e6e8fd.
- No side chats or forks from this chat hold other work.

## Tickets this chat touches

🎬 Socials 4 (IG export, less urgent now), 🎬 Socials 21, 🎬 Socials 23, 🎬 Socials 24, 🎬 Socials 25, 🎬 Socials 26.

## Ticket updates (for the System chat to merge)

- 2026-11-20 · 🎬 Socials 21 (profile checks 15 -> 6): already DONE since 2026-11-03 (M-10, Amir standing go 11-01). ig_engagement_config.py IN_SESSION_VET.per_session = 6 on disk; no edit made 11-20. Live proof: Fri 11-20 plan session_plan_2026-11-20.json handed the session 6 vet_profiles (+ 11 reach_follows). Vets are only handed when the followable pool is under 30, so on 11-20 the pool was below the 30 floor (board 39 was the 11-15 count). System chat: close Socials 21.

- 11-15 Fable gate on aa09659/f6def47 (plans/strategy/gates/2026-11-15-parent-lists-part-1.md): fix 1 DONE 3d82f38 (runbook: "Follow Back" after an unfollow click = re-follow + log + report, Amir yes). Fix 2 DONE (Amir "check each one live"): ig_unfollow_precheck.py, run by the dispatcher first on session days, searches Amir's followers per candidate (~12 calls); engine unfollows only entries cleared that day (UNFOLLOW_PRECHECK_REQUIRED). First live: Mon 11-16 09:30 + 15:00.

- 🎬 Socials · Instagram follower list reliability: DONE 2026-11-14 (Amir "we must fix it"). ig_reciprocity_from_lists.py combines every follower list from the last 12 days (own-lists, failed-own-lists, probe-g2, dj07). Applied 11-14: 996 combined vs 993 on the profile, trusted; 113 verified non-followers, 1 new follow-back. Engine unfollows resume Mon 11-16 (7 eligible now; more after the weekly list refresh). Commit in the IG chat.

- 🎬 Socials 27 · Instagram like list refresh: 11-14 note. 3 dead removed, 3 new added (mori_ra, fane.e.label, alfamatrix), 17 sweep accounts taken out of likes. 11-16 (Amir via Socials, "Yes, take him off"): microlith_ out of likes too (SI ig_blocked; never followed, no post since Feb 2017; backup enriched_contacts.json.bak.20261116_microlith). Active like pool now ~25. Keep open (pool too small for 12 likes a session).
- NEW (proposed), 🎬 Socials · Instagram sweep run: build the in-session unfollow of Amir's picks (untracked follows, ~8 extra a session, live check per profile, never on HTN send list until 12-21). Needs Amir's final go on the picks + his yes for the engine change. Plan: plans/ig-ratio-plan-2026-11-12.md.
- NEW (proposed), 🎬 Socials · Instagram follower list reliability: HikerAPI follower paging repeats pages (11-10: 876 unique of 992; 11-12: 286 and 689), so the follow-back check stalls and engine unfollows stopped since 11-06. Option: union of several fetches within 2 days, or the IG All-time export.

- 🎬 Socials 38 · IG health check churn count: DONE 2026-11-08 (Amir "Yes, fix both"). Reads follow_back and followed_back; churned reciprocators now 51 (was 48, +arale.music, degherlband, labeldiskoduro).
- 🎬 Socials 39 · SI follow flags guards: DONE 2026-11-08. usable() refuses lists without a profile count; a failed or incomplete fetch is saved as failed-own-lists-DATE.json, so the dispatcher retries next day. Tests: tests/test_si_follow_flags_guards.py.

- 🎬 Socials 37 · IG merge log KeyError: DONE 2026-11-08 (Amir "Yes, fix it"). Counter added in ig_merge_session_log.py + tests/test_ig_merge_keep_pending_skip.py. No session hit it since 08-27 (last such skip 08-26), so no data lost.

- M4 state file rotation (reply 2026-11-07, IG lane): CHANGE. Keep a rolling 90 days in engagement_log.json, not only the current month: IG cooldowns look back up to 65 days (T4 50-65, prominent 60, T2 30-45), so a month cut would re-like people too early. Readers: 11 scripts (ig_engagement, ig_merge_session_log, close_loops, ig_dispatcher, ig_health_check, push_to_sheets + 5 SC scripts; SC side is the SC chat's). .bak.* 14 days + .gitignore: yes for IG. Dry run: IG chat, only after Amir says yes here (engagement state rule).
- M4 dry run done 2026-11-07 (`plans/state-rotation-dry-run-2026-11-07.md`): 90-day cut = 1.7 MB -> ~0.9 MB. push_to_sheets last_engaged fixed (Amir "Keep existing dates"). Real run still waits on Amir's yes + SC chat OK.

- 🎬 Socials 26 (M-13): in-progress → **done**. The first swept session ran on 11-04: 7/7 unfollows, the visual check passed, 0 aborted.
- 🎬 Socials 4 (M-03): add a note. The export is no longer needed for unfollows (🎬 Socials 26). It is still useful for manual-follow intake and as an all-time cross-check.
- New ticket, 🎬 Socials (next free number): "Refresh the IG scene like list. 7 of 12 targets were inactive, private or gone on 11-04, so likes ran 5/12." Status proposed.

## Proposed fact fixes from ⚙️ System (2026-11-05)

Not applied: these files sit next to the engagement automation, so nobody edits them from the System chat. Source: `plans/strategy/review-2026-11-05-fixlist.md`. Truth: songs are the main line since 2026-09-13 (not public); next release Half the Night EP (Half the Night + Pinocchio), date open, as early as possible, not 2026-11-06; no 3 EPs; targets in `plans/targets.json`.

- Row 1, `docs/ig-agent-context.md:23`. Now: "Songs (guitars and voice) become the main line from 2027". Proposed: Songs (guitars and voice) are the main line since 2026-09-13, not public yet; the electronic lane continues alongside.
- Row 2, `docs/ig-agent-context.md:34`. Now: "Next: Pinocchio single (2026-11-06)." Proposed: Next: Half the Night EP (Half the Night + Pinocchio). Date open, as early as possible.
- Row 3, `docs/ig-agent-context.md:46`. Now: "(currently: Pinocchio, single, 2026-11-06)". Proposed: (currently: Half the Night EP, date open); release framing flexes per release, not per EP.
- Row 4, `docs/ig-agent-context.md:29`. Now: "790 -> 1,200-1,500 followers in 6 months (April 2026 -> October 2026)". Proposed: Goal: the Nov-Dec rungs in `plans/targets.json` (996 by 30 Nov, 1026 by 31 Dec).
- Row 5, `docs/ig-agent-context.md:52`. Now: "Followers | 790 | 1,200-1,500". Proposed: mark 790 as the April 2026 baseline; point the target column to `plans/targets.json`.
- Row 6, `docs/ig-agent-context.md:1009`. Now: "(790 followers, target 1,200-1,500 in 6mo)". Proposed: (targets: `plans/targets.json`).
- Row 7, `docs/ig-agent-context.md:454-455`. Now: "Techno Trance EP uses set ... Downtempo / Exotic EP uses". Proposed: remove both lines, these EPs are no longer planned.
- Row 8, `docs/ig-agent-context.md:604`. Now: "promotion_log.json -- currently farewell-single". Proposed: no active campaign now; check `promotion_log.json`, Farewell is finished.
- Row 9, `docs/ig-agent-context.md:12-13`. Now: "plans/strategy/inch-of-shadow-marketing-guide.md (broader marketing context)". Proposed: add that these are electronic-era docs (History banner since 11-05); Beatport and label-demo parts no longer apply.
- Row 10, `docs/ig-engagement-sop.md:17`. Now: "790 -> 1,200-1,500 followers in 6 months ... currently Phase 1 (10 follows". Proposed: goal = `plans/targets.json` rungs; caps per config (12/16/8 since 11-04); add the songs lane.
- Row 56, `plans/ig-engagement-strategy.md:5`. Now: "Grow @inch_of_shadow from 790 -> 1,200+ followers in 6 months". Proposed: mark expired (Oct 2026, unmet); current goal: `plans/targets.json`.
- Not a row: `scene_intelligence/release_context.json` still carries Pinocchio, single, 2026-11-06. Same fix as row 3, whoever owns that file.

## Proposed from ⚙️ System (2026-11-06): platform jobs

Not applied: these files sit next to the engagement automation, so nobody edits them from the System chat. Source: `plans/strategy/platform-plan-songs-2026-11-05.md` (approved by Amir 2026-11-06, D5). Exact lines to add, for the IG chat to place:

- `docs/ig-agent-context.md`, in the goal block near the top (rows 1-5 above touch the same lines), add:
  > **Instagram's job (songs lane, approved 2026-11-06):** bring traffic. The face, the process, the first hours of each release. Instagram is not where fans are held; that is Spotify and the email list. Every release-day post and every content experiment points there.
- `docs/ig-agent-context.md`, same block, the measures line:
  > **What we measure for this job:** views per follower vs 0.77x, non-follower share, sends, profile visits and follows per release. Follower count is a rung in `plans/targets.json`, not the job.
- `docs/ig-engagement-sop.md`, under the goal (row 10 above), add one line:
  > Engagement supports Instagram's one job, bringing traffic to the songs; it is measured by follows and profile visits per release, not by follow volume. Full plan: `plans/strategy/platform-plan-songs-2026-11-05.md`.
- `plans/ig-engagement-strategy.md`, next to the expired goal (row 56 above):
  > Current frame: one job per platform (approved 2026-11-06), Instagram = traffic. See `docs/brand/positioning.md`, section "Platform jobs".


## Proposed from ⚙️ System (2026-11-06): state file rotation (M4, Batch 4)

Not applied; the engagement state is yours. Facts today: `scene_intelligence/engagement_log.json` is 1.7 MB and
grows every session; the SC tracker health refresh writes a 500 KB `.bak` three times a day (55 untracked
`.bak.*` files in `scene_intelligence/` now). Proposal, for your yes and your dry run:
- `engagement_log.json` keeps the current month; older months move to `scene_intelligence/archive/engagement_log-YYYY-MM.json.gz` by a small script you own, run on the 1st; every reader that scans history reads the archive too (list the readers first).
- `.bak.*` files: keep 14 days, then Trash (never rm), and add `scene_intelligence/*.bak.*` to `.gitignore` so they never enter git (the 23 files under `backups/sweep-20260831/` stay as they are).
- Test: one session after the rotation must log, score and report exactly as before.
Reply in your handover's "Ticket updates" with yes / change / no.
## Ticket updates

- 2026-11-18 · IG profile picture picks (side session, asked by 🎬 IG chat on Amir's 11-18 ask). Current picture: set 2026-04-17 per the IG exports (profile_photos.json, 04-22..08-30; the image file itself is not in any export, 10-10 export has no media), so it predates both 2026 shoots. 5 picks from her shoot set, all eyes to the lens: in-003 (starry blue, white shirt, songs), out-087 (golden hour, songs, leaf shadows busy at 40 px), in-125 (red gel, electronic lane), in-189 (green gel, her 2★, songs/both), in-129 (B&W noir, songs). out-055 left out: full body, face too small for a circle. Local crop + circle mask only, no AI. Page https://claude.ai/artifact/U5nhhV8Kz1YECdvotoiFtJ (db `ticks`, doc id = photo id, field v). Files + 1080 upload squares + build.py/page.py: plans/ig-profile-picture-2026-11/. Open: Fable gate read, Amir's tick. Amir changes the picture himself. Note: frame.md says the thorn-ring mark (Look-02) is meant for the profile picture once he draws it; these picks are for until then.
- 2026-11-18 round 2 (Amir: "more options, with sunglasses too, gaze into the camera not a must"): same page, now 15 in 3 groups. Sunglasses: out-027, in-056, out-149, out-190, out-001. Looking away: out-166, in-193, in-238, out-151, in-023. in-205 (rose in teeth) tried and dropped: the face sits at the photo's right edge and can't be centred in a circle. Ticks: db `ticks`, empty so far. Fable gate still open.
- 2026-11-18 round 3 (Amir: "add option to remove", "not sure you cropped well"): all 15 recropped with one rule (head measured by eye: hair-to-chin = 48% of the circle, 14% room above the hair, head centred; HEADS in build.py). Upload files rebuilt. Page now has V + X per card (db `ticks`: fields v, x); X dims the card, tap again to bring it back. Ticks so far (V): in-129, out-027, out-149, out-190; none removed.
- 2026-11-18 round 4 (Amir "give me more options now"): his marks before it: V in-129, out-027, out-149, out-190, in-238, out-166; X in-003, in-023, in-056, in-125, in-189, in-193, out-001, out-087, out-151 (dislikes green/teal gels, golden-hour sun, bright sepia). 12 new in 3 groups, same crop rule: B&W in-124, in-136, out-023, out-050; sunglasses out-037, out-067, out-077, out-117; red/looking away in-138, in-210, in-225, out-011. Page now 27 options.
- 2026-11-18 round 5 (Amir "more options now" + "option to click the image and zoom in"): his marks after round 4: new V in-138, in-210, out-037, out-067, out-077; new X in-124, in-136, in-225, out-011, out-023, out-050, out-117 (no plain straight-on B&W, no bars, no very close). 12 new: sunglasses out-038, out-024, out-076, out-128, out-145, out-049, out-025; red/noir in-211, in-214, in-232, in-135, in-001. Page = 39 options. Tap to zoom: every whole photo and big circle opens large (zoom/ files published with the page, 1800 px whole photo + 1080 crop); tap again = full size.
- 2026-11-18 round 6, last (Amir "few with the black tank but not only those", "I'm looking for my full hair to be present"): marks before it: V in-129 in-138 in-210 in-214 in-232 in-238 out-027 out-037 out-049 out-067 out-077 out-145 out-149 out-166 out-190; X in-001 in-003 in-023 in-056 in-124 in-125 in-135 in-136 in-189 in-193 in-225 out-001 out-011 out-023 out-024 out-025 out-050 out-076 out-087 out-117 out-151. New 8: black tank out-026, out-035, out-039, out-129; plus in-212, in-209, out-142, out-079. Crop rule changed for ALL 47 (full hair): head 48% -> 45% of the circle, room above hair 14% -> 18%. out-166 and in-225: her photo itself cuts the hair top (noted on the cards). Page = 47 options. 📌 Taste signal (not a rule, no read-back yet): full hair visible matters to him for the profile picture.
- 2026-11-18 FINAL MARKS (Amir "I ticked my picks"): 21 V: night flash sunglasses out-027 out-037 out-039 out-067; memorial/day sunglasses out-149 out-077 out-145 out-079 out-142 out-190 out-049; noir/red in-129 in-138 in-238 in-209 in-210 in-211 in-212 in-214 in-232 out-166. 23 X. Unmarked: out-035 out-038 out-128. Side-by-side sheet: plans/ig-profile-picture-2026-11/ticked-21.png. Not yet narrowed to one. Upload file for the winner = plans/ig-profile-picture-2026-11/upload_1080_<id>.jpg; Amir changes the picture himself.
- 2026-11-19 page v7 (Amir "refresh the artifact"): top section "Your 21 picks, by feeling" (3 mood groups with circles + what the set says), a feeling line on every card (catalogue tag), filters All / Only my V / Hide removed. Ticks untouched.
- 2026-11-19 round 7 finals (Amir: "continue with 37 39, more from this family? also 142 079 077"): page v9 opens with "Finals: night flash family" (out-037, out-039, out-038, out-036; that series has no other edits) and "Finals: memorial evening family" (out-142, out-079, out-077 + siblings out-080, out-081, out-082, out-150, out-083, out-152, out-144, out-078). Removed cards now hide fully (filter "Open picks" default). Next asked: try effects on them (print_looks.py, 26 local looks, face-safe) as a mixer page, waiting on his go.
- 2026-11-19 effects mixer (Amir "Yes, build it"): page v10 has an "Effects mixer" section at the top. All 26 print_looks.py looks rendered locally on the 5 finalists (out-037, out-039, out-142, out-079, out-077), 640 px each, in plans/ig-profile-picture-2026-11/looks/ (mix_build.py). Look A + look B as opacity layers (B blend mode selectable), strength sliders, live 110/40 px circles on light/dark, tap to enlarge, Save = db `looks` (doc = photo_timestamp; fields ph, a, wa, b, wb, bm). Next: when he saves a winner, render the real 1080 upload with the same setting (B is layered, not chained).
- 2026-11-19 mixer fix (Amir "nothing changes in the slider"): cause = look A started as None, so the strength slider had nothing to fade. Now look A starts on S3 Riso, sliders are disabled with "(pick look first)" until a look is chosen, and a tap strip of all 26 looks (round previews of the current photo) sets look A. Also .zoom[hidden] guard. Tested in Playwright on the local file: slider 29% -> layer opacity 0.29, look tap, photo switch, look B slider 81%. Page v12.
- 2026-11-19 tournament (Amir "show me the final, let's make the tournament, clean similar options"): db `looks` cleaned, 15 exact duplicate saves deleted (12 unique settings left, all on out-037). Page v13 opens with "Tournament": 11 entrants = 5 finalist photos plain (037, 039, 142, 079, 077) + 6 distinct out-037 effect versions (Riso 68; Riso 80 + Night flash 20; Riso 100 + Blowout 8; Riso 68 + Monotint 70; Monotint 100 + Monotint night 11; Monotint 100 + Cyanotype 21). Near-twins left out of the bracket but kept in saves. Winner-stays format, 10 taps, progress in db `tournament/run`. Renders: tourney/ (tourney_build.py). Next: 1080 upload of the champion with the same setting.
- 2026-11-19 DECISION (Amir "we will choose 37"): new IG profile picture = out-037 (her edit Outdoor/Outdoor Shoot/Edited, night flash, black tank, glasses pulled down). Tournament state when he chose: 037 plain beat 039, 142, 079; stopped at match 4 (077 and the 6 effect versions not played). Upload file (plain): plans/ig-profile-picture-2026-11/upload_1080_out-037.jpg, 1080x1080, full-hair crop. Amir changes the picture himself. Old picture: set 2026-04-17, image not saved on disk (exports have no media).
- 2026-11-19 tournament round 2 (Amir "the tournament with 37 effects"): page v14, tournament now out-037 only: plain + the 6 effect versions, 6 taps, progress in db `tournament/run37` (round 1 result kept in `tournament/run`). Next: 1080 upload with the champion's exact setting.
- 2026-11-20 FINAL (Amir "Riso 68%"): out-037 + Riso 68% (print_looks riso blended 0.68 over the original at 1080, local, no AI). Upload file: plans/ig-profile-picture-2026-11/upload_1080_out-037_riso68.jpg (1080x1080, q95); size check final-037-riso68.png (160/110/40 px, light + dark). Last tournament run's champion was Riso 100 + Blowout 8; he picked Riso 68. Amir changes the picture himself. Open: Fable gate read.
- 2026-11-20 also rendered for comparison: upload_1080_out-037_riso100-blowout8.jpg (tournament champion setting). Side chat closed by Amir. Lessons: first crops were inconsistent until one head-measured rule (45% head / 18% room above hair); mixer shipped with look A empty so sliders did nothing (fixed); tournament db keeps only the last run.
