# IG SWEEP RUN: runbook (2026-11)

Amir's ~181 Unfollow picks (his own older follows that do not follow back) are
unfollowed in their own browser runs: **Tue 11-17, Thu 11-19, Sun 11-22,
Tue 11-24, Thu 11-26, Sun 11-29, 16:00 Berlin, 30 per run.** Changed: extra
runs 11-16 and 11-18; Amir 11-19: the last two runs are **Fri 11-20 + Sun
11-22**, the 11-24/26/29 tasks are disabled. Fri 11-20 got no go before 21:00;
Amir 11-20: run on **Sat 11-21** instead, Sun 11-22 stays the last run. Decided by Amir
11-14 ("sweep plan approve", "A", "approve"); build brief
`plans/ig-sweep-2026-11/BUILD-BRIEF.md`. Each run is one one-time scheduled
task `ig-sweep-run-N-MMDD` that reads THIS file and runs the BODY.

The regular session playbook (`docs/cowork-task-ig.md`) is NOT used for a
sweep run: no likes, no follows, no vets, no plan-only engine call, no
close_loops. Its Chrome, scope, popup and click rules apply here unchanged.

---

## BODY

== ALLOWED COMMANDS (exactly these, run in Inchofshadowcode/) ==

1. .venv/bin/python scene_intelligence/ig_sweep.py gates
2. .venv/bin/python scene_intelligence/ig_sweep.py plan --fetch-if-stale
   (step 1d only: `plan --fetch-if-stale --rebuild`)
3. .venv/bin/python scene_intelligence/ig_daily_ledger.py --claim ig_sweep --kind browser
   (and `--show` to read it)
4. .venv/bin/python scene_intelligence/ig_log_action.py --sweep --action-type <type> --handle <h> [--reason "..."]
5. .venv/bin/python scene_intelligence/ig_sweep.py close
6. ArtifactData `list` on https://claude.ai/artifact/8W74pNWcQcfxa4ZnGdyQuu,
   collection `picks`, query limit 1000, out_dir
   `plans/ig-sweep-2026-11/picks_live/<today YYYY-MM-DD>` (read only, never write)
7. Read the plan file `plans/ig-sweep-2026-11/runs/run-<today>.json` with the Read tool.
Nothing else: no inline `python -c`, no edits to any state file, no --force,
no --resume; --rebuild only in step 1d, before the first click.

== STEP 1: PICKS + PLAN (no Chrome yet) ==

a. Command 6: save today's copy of Amir's taps (his taps win; a late flip to
   Keep must count). If it fails: STOP, no clicks, tell Amir. The live plan
   refuses an older copy (gate fix 3, 11-15) and prints "no picks copy for
   <date>".
b. Command 2. It fetches the own follower/following lists through HikerAPI
   first when the newest list is more than 2 days old (~85 calls, inside the
   300/day cap), then writes the run's plan file. It applies every
   protection: anyone in any follower list of the last 12 days, the HTN EP
   send list until 12-21, personal network + keep_following, protected
   accounts, blocked accounts, accounts no longer followed, earlier sweep
   results. Exit 3 or a "BLOCKED" line = STOP, no clicks, tell Amir the lines.
   A blocked plan is replaced the next time command 2 runs (gate fix 4), as
   long as no click is logged; a good plan is kept.
c. Command 1 (gates). Exit 3 = STOP and tell Amir the reasons. The gates check:
   a sweep run date, 16:00-22:00 Berlin, pauses.ig, the session detection
   cooldown, today not already closed, a plan file with names.
d. SHOW THE BATCH, THEN WAIT (Amir 11-16: "before a sweep I wanna see the
   batch names"). Post the run's names as a table (#, handle, group,
   followers, tap/suggestion) plus the held list, and END THE TURN. No
   Chrome, no clicks until Amir answers "go" (or similar) in this chat.
   If he names handles that stay: he taps Keep on the picks page (or says
   so); then redo step 1a + command 2 with --rebuild (allowed only here,
   before any click), show the new batch, wait again.

== STEP 2: BROWSER + SCOPE (same as the session playbook) ==

- Pinned device only: list_connected_browsers, then select_browser
  deviceId a9ab2708-3093-4af1-946d-6bceb13293ef. Not listed = STOP, no
  clicks (log `session_halt --reason "infrastructure: pinned browser not connected"`).
- Chrome queue: a refused Chrome call ("held by ...") = wait up to 15 min,
  then STOP. Never route around the hook.
- Scope check: open https://www.instagram.com/inch_of_shadow/ by typed URL,
  read handle inch_of_shadow AND the "Edit profile" button (read it, never
  click it). Anything else = STOP.
- Never close Amir's tabs. Work in one tab.
- Then claim the ledger (command 3), right before the first profile.

== STEP 3: THE UNFOLLOWS (only the plan file's `names`, in order) ==

For each name:
1. Open https://www.instagram.com/<handle>/ by typed URL. Dwell 2-3 s.
2. Profile missing ("Sorry, this page isn't available") or no Following
   button after up to two full reloads: log
   `ig_skip --reason profile_unavailable` (or `button_missing_after_reload`), next.
3. RECIPROCATOR GUARD: zoom-check the header zone AND the bio zone for
   "Follows you" or any mutual sign. Present = do not click; log
   `ig_unfollow_aborted --reason visible_reciprocator`, next.
4. Click "Following" ONCE. Read the menu that opened. Never click the
   button's coordinates again while the menu is open (10-10: the second
   click lands on "Add to close friends list"). Click "Unfollow" in the menu
   (and confirm "Unfollow" if IG asks).
5. Read the button:
   - "Follow" = done: log `ig_unfollow` (command 4).
   - "Follow Back" = they DO follow Amir (10-09 lesson): click "Follow Back"
     at once, verify "Following", log
     `ig_unfollow_aborted --reason follow_back_after_click_refollowed`. Tell
     Amir in the report.
   - still "Following": retry steps 4-5 once, else log
     `ig_skip --reason unfollow_did_not_register`.
6. Wait 30-60 s before the next profile; a 60-120 s pause every 6-8 profiles.
   30 profiles take about 30-40 min.

Log right after each click with command 4; never hand-write the JSONL.

== STOP RULES ==

- ANY popup, banner, warning, "Try again later", action block, CAPTCHA,
  login or phone challenge: STOP at once, click nothing on it, log
  `session_halt --reason "safety: <verbatim text>"`, run close (step 4),
  quote it to Amir. Only Amir resumes.
- 3 skips in a row with the same IG-side reason, or 5 skips in a row of any
  kind: STOP with `session_halt --reason "safety: <n> skips in a row"`.
- 22:00 Berlin reached (was 21:00 until Amir 11-21): stop with `session_halt --reason "safety: 22:00 cutoff"`.
- Chrome/connection dies: `session_interrupted --reason "infrastructure: <what>"`.

== STEP 4: CLOSE ==

Command 5. It refuses a log with any handle that is not in today's plan, or
any action that is not a sweep action. It writes each unfollow into
`ig_follow_tracker.json` unfollowed_history (source `manual_sweep_2026_11`,
so the engine never follows them again), the engagement log, and
`plans/ig-sweep-2026-11/sweep_state.json` (done / aborted / skipped, read by
the next plan), archives the JSONL, and saves `docs/reports/ig-sweep-<date>.md`.
A detection signal in a halt sets pauses.ig (Amir resumes). Quote its output.

== REPORT (short, Amir's rules) ==

Score line + Growth line from close, verbatim. Then: EVERY "Follow Back"
re-follow by handle, on its own line at the top (a follower the lists
missed; Amir must see each one, gate 11-15). Then: aborted handles + why,
skips, any halt, duration, HikerAPI calls used by the fetch (from the plan
output). Following count before -> after with the ratio (prev -> now). No
pings to the Socials chat for sweeps unless Amir asks.

== NEVER ==

Likes, follows (except the instant Follow Back re-follow in step 3.5),
comments, DMs, stories, settings, /accounts/, Edit profile, Suggested for
You, any handle not in the plan file, editing state files, --force,
--rebuild after a click, --resume, clearing a pause, any click before
Amir's go on the shown batch.
