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