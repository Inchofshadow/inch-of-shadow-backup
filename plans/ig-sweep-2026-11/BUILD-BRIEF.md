# IG sweep run: build brief (2026-11-14)

## What and why

Amir follows ~1,046 accounts on Instagram (@inch_of_shadow) with ~997 followers (ratio 0.95). Goal: 1.2:1 by mid-December. Half the Night EP is out Fri 12-11, and the sweep has to be finished a week before.
On the picks page he marked about 181 of his own older follows (not engine-tracked) that do not follow him back as Unfollow. This build makes those unfollows happen.

## Decisions (Amir, in the IG chat)

- 11-12: option B (sweep his older non-followers). 11-14: "sweep plan approve", "A", "approve".
- Sweep runs on **Tue/Thu/Sun at 16:00 Berlin**, **30 unfollows per run**, 6 runs: Tue 11-17, Thu 11-19, Sun 11-22, Tue 11-24, Thu 11-26, Sun 11-29. Done by Sun 11-29.
- Regular sessions (Mon/Wed/Fri/Sat 15:00) stay as they are: 10 follows (changed 16 -> 10 on 11-14, commit f6def47), 8 engine unfollows, likes.
- Dec 5 check: if ratio >= 1.2, follows back to 16.
- The first live run only after a dry run of its 30 names is shown to Amir. A second-model (Fable) read of this plan comes before the first live run.

## The final list

- Picks: db collection `picks` on https://claude.ai/artifact/8W74pNWcQcfxa4ZnGdyQuu (doc id = IG user_id, field `choice` keep|unfollow). Read it with ArtifactData. His taps win.
- Untapped rows: the page's suggestion (field `s` in ROWS inside plans/ig-sweep-page/index.html). Undecided rows (no tap, no suggestion) stay followed.
- Extra: plans/ig-sweep-2026-11/extra_unfollows.json (distantgaze_records, engine-tracked).
- Source data: plans/ig-sweep-2026-11/candidates.json, profiles.json, cross_check.json, picks_snapshot.json. Contacts of all 321 saved: plans/ig-follow-contacts-2026-11.md/.json.

## Never unfollow (checked again before every run)

- Anyone in a follower list from the last 2 days, plus a fresh fetch before each run if the newest list is older than 2 days (combine lists: scene_intelligence/ig_reciprocity_from_lists.py has recent_lists/combined_roster).
- The HTN EP send list until 12-21 (from the 🎧 HTN EP DJ promo chat, 11-13): plans/handovers/booking/htn-dj-promo.md and plans/htn-label-drafts-batch*-2026-11-11.md. Exception, Amir's own call: he kept Unfollow on 030303records, hilltown.disco, mosaique_records, dollkraut, juniorfairplay, tunik303 (11-13). distantgaze_records: Amir "mark unfollow".
- Personal network and keep_following (scene_intelligence/ig_personal_network.json, tracker keep_following), protected accounts (memory ig-protected-accounts).
- Any profile that shows "Follows you" at click time: abort that one (ig_unfollow_aborted, visible_reciprocator).

## How sessions work today (read these first)

- Runbook: docs/cowork-task-ig.md (the scheduled task ig-engagement runs its BODY in Amir's Chrome). Every click is logged with scene_intelligence/ig_log_action.py. State gates: ig_session_state.py --gates. Ledger: ig_daily_ledger.py --claim ... --kind browser.
- Merge + scoring: scene_intelligence/ig_merge_session_log.py and close_loops.py --platform ig. Off-day runs (Tue/Thu/Sun) trip two guards; see memory ig-offschedule-session-recovery (merge --force, close_loops --resume).
- These are untracked follows (not in ig_follow_tracker.json active_follows). Check how the merge records untracked unfollows (unfollows_not_found) and make sure each lands in unfollowed history (never re-followed), the same way the SC sweep 11-03 did (memory sc-manual-follow-sweep-2026-11; SC used UNFOLLOW_CATCHUP_DAYS + one-time sc-sweep-run tasks).
- Chrome: one chat in Chrome at a time (memory chrome-queue-on), the inch_of_shadow profile, never during the automation windows (SC 10:00, IG 15:00 Mon/Wed/Fri/Sat, Spotify Mon 08:00). Never close his tabs.

## Done means

1. A sweep plan file per run (30 names, protections applied, fresh follower check), built by a script with --dry-run.
2. A sweep runbook (or a sweep mode in the existing one) for the browser run: gates, ledger claim, per-profile "Follows you" check, logging, halt on any popup/warning/CAPTCHA.
3. Merge and close that count the sweep unfollows and keep them out of future follows.
4. Tests for the plan script and the merge path.
5. Dry run of Tue 11-17's 30 names shown to Amir; Fable read; then 6 one-time scheduled tasks (Tue/Thu/Sun 16:00).
6. Handover updated (plans/handovers/socials/ig-agent.md), commits of only the files changed.

Rules: engagement code/config/state changes are covered by Amir's yes above, for this build only. HikerAPI cap 300/day (the Sun 11-15 09:00 pool refill uses ~284). No pushing.
