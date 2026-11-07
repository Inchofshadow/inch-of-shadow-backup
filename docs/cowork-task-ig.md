# IG ENGAGEMENT SESSION — single-operator playbook (2.0)

**Since 2026-08-31 this file is self-contained: it is the ONLY mandatory
read before a session.** (The 1.0 stack demanded ~3,200 lines across three
docs before the first click.) `docs/ig-engagement-sop.md` stays the deep
reference for WHY; this file is the WHAT. The scheduled task ("ig-engagement",
daily 15:00 Berlin) reads this file at run time and executes the BODY —
edits here take effect on the next fire. Archived 1.0 playbook: git tag
`ig-automation-1.0`.

**Operator model:** one operator — Claude in this app is hands AND brain,
clicking via claude-in-chrome in Amir's real Chrome. Amir is the captain:
he confirms pre-flight and action #1, and only he resumes pauses. CC/Cowork
never runs sessions (decommissioned 2026-08-27).

---

## BODY

This task fires DAILY at 15:00 Berlin. First: check the day of week.

DAY ROUTING — action days Mon/Wed/Fri/Sat; on Tue/Thu/Sun send Amir one
line and stop: "Today is <day>. No IG engagement today — I run
Mon/Wed/Fri/Sat at 15:00 Berlin."

== ALLOWED TERMINAL COMMANDS (exactly these patterns, nothing else) ==

1. python3 scene_intelligence/ig_log_action.py --action-type <type> [flags]
   (LOG EVERY CLICK WITH THIS — 2026-09-18. It reads the Berlin clock
   itself, auto-increments `sequence`, and appends the line. You never
   build a timestamp or a JSON string by hand again. `--help` lists the
   flags; see STREAMING JSONL below.
   WHY IT IS A SCRIPT: approvals are exact-match, and the old raw-shell
   append was a different command string on every line, so every single
   click raised a fresh permission prompt. On 2026-09-18 the scheduled
   session froze on four of them for ~7 hours and landed 1 follow. This
   command is covered by ONE wildcard allow rule, exactly like SC's
   `sc_engagement.py --log-action`.)
2. python3 scene_intelligence/ig_engagement.py --plan-only --no-preflight
   (today's plan; local, zero IG API calls)
3. python3 scene_intelligence/ig_daily_ledger.py --claim ig_session --kind browser
   (sign today's ledger BEFORE the first click; also `--show` to read it)
4. python3 scene_intelligence/close_loops.py --platform ig   (final step)
5. python3 -c "from scene_intelligence.ig_ops_guards import active_detection_cooldown as a; print(a(platform='ig', kind='session'))"
   (hard gate 2 — pre-approved 2026-09-11 after it stalled a run on a prompt)
6a. python3 scene_intelligence/ig_session_state.py
   (STATE READ, added 2026-09-18 — tracker, queue depth, builder age,
   promo/release flags. Read-only. Use THIS instead of an inline
   `python3 -c` state script: the improvised one stalled the 09-18 run for
   210 minutes on its approval prompt. Volumes still come from the plan
   file, never from this summary.)
6. python3 scene_intelligence/ig_session_confirm.py --check
   and, to wait for it: python3 scene_intelligence/ig_session_confirm.py --wait 900
   (pre-confirm flag, added 2026-09-17 — see PRE-CONFIRM FLAG below; local,
   zero API; prints "confirmed <ts>" or "none". Never run it with --set or
   --clear: --set is Amir's yes and only he, or his chat, writes it.)
7. Nothing else. No other scripts, no file edits except the session JSONL,
   no --live, no --force, no --resume, no --override-ledger (Amir's alone).

== STANDING CONFIRM (2026-10-07, Amir: "remove the confirm") ==

Since 2026-10-07 sessions run WITHOUT a per-session confirm. The file
`scene_intelligence/ig_standing_confirm.json` is Amir's standing yes: while
it exists, allowed command #6 prints "confirmed (standing ...)" at BOTH
gates and you continue without waiting at either. Still send each gate's
frame text, for the record. Amir ends it by saying "stop" (his chat runs
`--standing off`); you never run `--standing` yourself.
The standing confirm covers ONLY the two gates. Popups, warnings, CAPTCHAs,
pauses.ig, a detection cooldown and a missing pinned browser still STOP the
session exactly as before. The per-session flag below still works and is
the fallback when the standing confirm is off.

== PRE-CONFIRM FLAG (2026-09-17 — after the 4-hour stall of 2026-09-16) ==

Amir's two standing confirms (pre-flight, and after action #1) happen
inside THIS run. Confirms he types in his normal chat never reach it: on
2026-09-16 the run waited four hours on the action-#1 confirm and ended
with one click. So Amir can now confirm in advance: he says "confirm" in
his chat (or runs `ig_session_confirm.py --set` himself) any time before
the session, which writes `scene_intelligence/ig_session_confirm.json`
dated today.

At BOTH gates run allowed command #6 first:
- "confirmed <ts>" → that IS Amir's explicit confirm for that gate. Still
  send him the gate's frame text so he sees it, then continue without
  waiting.
- "none" → wait with ONE command and nothing else (2026-10-07):
      python3 scene_intelligence/ig_session_confirm.py --wait 900
  It returns the moment the flag appears (exit 0) or after 15 min (exit 1).
  NEVER write your own `until ... sleep` loop: that is a new command string
  every run, it raised a permission prompt both times on 10-07, and the two
  "15-minute" waits became 44 minutes and 2 hours 50 minutes.
  If Amir replies "confirm" in THIS chat instead of setting the flag, that
  reply counts for BOTH gates (pre-flight and action #1) -- do not wait
  again at action #1. On 10-07 his chat reply passed pre-flight and the run
  then halted at action #1 looking for a flag that was never going to come.
  Bounded window: 15 min at pre-flight, 15 min after action #1. Then end
  safely (append the session_halt event with reason "safety", note which
  gate timed out). Never wait open-ended again.
The flag covers ONLY those two gates. Popups, warnings, CAPTCHAs, pauses,
and a broken Chrome connection still need Amir live — a flag never
resumes any of those. The loop-closer deletes the flag after the merge; a
flag from another day is ignored by --check automatically.

== HARD STATE GATES (before anything else, no clicks) ==

RUN ALL THREE GATES WITH ONE COMMAND (2026-09-21):
    python3 scene_intelligence/ig_session_state.py --gates
It prints the Berlin time, gate 1 (pauses.ig), gate 2 (session detection
cooldown), gate 3 (ledger), and the pre-confirm flag, then a VERDICT.
Exit 0 = "gates clear", continue. Exit 3 = "STOP" with the reasons: stop
and tell Amir. Do NOT read autonomy_state.json by hand and do NOT chain
your own `python3 -c ...; python3 -c ...` gate line: that improvised line
is a new string every run and stalled the 09-21 run on a permission prompt
before its first gate. The notes below explain what each gate means.

1. `scene_intelligence/autonomy_state.json` → **pauses.ig** (per-platform
   key; the legacy top-level "paused" key is dead — reading it passed a real
   pause on 2026-08-29). If pauses.ig is not null: STOP IMMEDIATELY, tell
   Amir the reason + timestamp, wait for HIS resume
   (`close_loops.py --resume --platform ig`). Never proceed, never resume.
2. Detection cooldown, SESSION kind (2026-09-06 amendment: API-surface
   throttles such as the 429 do NOT block browser sessions; account-level
   events such as CAPTCHA / action block / login challenge DO). Run:
     python3 -c "from scene_intelligence.ig_ops_guards import active_detection_cooldown as a; print(a(platform='ig', kind='session'))"
   (allowed command #5). If it prints anything other than None: STOP and
   tell Amir. Do not read detection_events.json by hand for this gate.
3. The ledger is NOT claimed here any more (2026-09-11): it is claimed at the
   start of PRE-FLIGHT, after the browser and scope checks pass. Claiming
   first let a browser failure burn the whole day's slot at zero clicks.
   Read-only check now: `ig_daily_ledger.py --show` — if an ig_session with
   clicks already ran today, STOP (never two sessions a day).

== PICK THE BROWSER — PINNED DEVICE (2026-09-11, same pin as SC) ==

Connection NAMES are useless: they are session-local and reset to anonymous
"Browser 1..4" on every reconnect (verified 2026-09-08, and this halted the
09-04, 09-07 and 09-11 runs). Device IDs are stable. So:

  call list_connected_browsers, then select_browser with deviceId
  a9ab2708-3093-4af1-946d-6bceb13293ef  (the Inch of Shadow Chrome profile)

- If that deviceId is NOT in the list: STOP, append session_halt
  (infrastructure: pinned browser not connected), no clicks. If Amir is
  present he can use the connect prompt instead; never pick a connection
  yourself.
- Never select, probe or act in any other connection, whatever it is named.
- The pin only chooses the window. The SCOPE CHECK below (@inch_of_shadow
  + "Edit profile" on the public profile page) is what PROVES it. If the
  scope check fails on the pinned device: STOP and tell Amir — the pin is
  stale.

== SCOPE CHECK (SOP §4.0 — all five must pass before any click) ==

[ ] CHROME PROFILE is the pinned device (deviceId above was selected and
    is connected). The extension CANNOT open Chrome's own avatar menu or
    read chrome://settings, and the permission system blocks attempts to
    (09-21 and 09-26 halted on exactly this). So: do NOT try. Never
    navigate to chrome://, google.com or any account page for an email.
[ ] IG account is @inch_of_shadow: open https://www.instagram.com/inch_of_shadow/
    and read the header. It must show the handle inch_of_shadow AND an
    "Edit profile" button (only the logged-in owner sees that button; a
    visitor sees Follow/Message). Handle + "Edit profile" on the pinned
    device = the account is PROVEN. Anything else → STOP, tell Amir.
[ ] Not incognito, not guest, not another browser (the pin guarantees this).
[ ] Never touch /accounts/ or Edit profile itself — read the button, do not
    click it (Amir, 09-11).
[ ] Confirm to Amir in one line: pinned device + @inch_of_shadow + Edit
    profile seen. The Chrome profile email is NOT a required signal any
    more (2026-09-26); if it happens to be visible on instagram.com, note
    it, otherwise say "email not readable" and continue.

NEVER touch adjacent accounts: @doublefigure_band, @ambertone.studios,
@collective.dada — off-limits as operator and as targets.

== POPUPS (SOP §4.0B) ==

ANY popup / banner / notification at ANY point: STOP. Click nothing on it
(not X, not Not Now, not outside it). Quote it verbatim to Amir and wait.
He reads, he clicks, you resume only on his explicit confirm.

== STRICT RULES (each exists because something specific went wrong) ==

1. NEVER write to ig_follow_tracker.json or ANY state JSON directly. You
   append to the session JSONL only; the loop-closer's merge syncs the
   tracker (2026-05-31: direct tracker writes drifted stats by 4).
2. NEVER set unfollow_after dates anywhere — the merge computes them.
3. NEVER claim results the loop-closer did not print. Quote its output
   VERBATIM; if it errors, say exactly that and leave the merge unclaimed.
4. JSONL timestamps are REAL CLOCK READS at the moment of the click. Since
   2026-09-18 allowed command #1 reads the clock itself when it writes the
   line, so run it right after the click and the stamp is correct by
   construction. Never synthesize, spread, or project a timestamp, and
   never pass a hand-made one (the fabrication guard trips on future
   stamps; two real sessions were flagged for synthesized clocks).
5. One timezone: Berlin. Allowed command #1 emits the correct +02:00/+01:00
   offset for the season. Never mix zones in one JSONL.
6. FABRICATION-CHECK after action #1: after the FIRST successful click,
   STOP: "Action #1 done: <action> on @<handle>. Please verify in your
   Chrome tab before I continue." Wait for explicit confirm — unless
   allowed command #6 prints "confirmed" (PRE-CONFIRM FLAG), which counts
   as that confirm; otherwise max 15 min, then end safely (2026-09-17). If
   Amir doesn't see it, the Chrome connection is broken — end the session.

== PRE-FLIGHT (both confirms are Amir's standing rule, 2026-08-30) ==

[ ] Scope check passed (above).
[ ] The ledger is claimed AFTER the confirm frame below (moved 2026-09-26:
    the 09-26 run claimed first, halted at the gate with zero clicks, and
    the claim then blocked the real session). Do not claim here.
[ ] Amir used IG manually today (2-3 min warm-up)? If he is present, ask.
    If the pre-confirm flag is set (allowed command #6 prints "confirmed"),
    do NOT wait on this question: note "warm-up not verified" in the report
    and continue (2026-09-28). The warm-up is a nicety, not a gate.
[ ] Ledger read (`--show`): today's API load. The law: action sessions
    never stack on a heavy-read day (>50 est. calls today → defer).
[ ] Any ACCOUNT-LEVEL detection (CAPTCHA, action block, login challenge,
    popup) in the last 72h → refuse (§4.2). API-surface throttles
    (429 / soft throttle on profile reads) do NOT block sessions —
    the engine's gate knows the difference (2026-09-06).
[ ] Slot: 15:00 Berlin; late start acceptable to 22:00. After 22:00 → skip
    the day (night clicking is a bot pattern).
[ ] Active pre-release campaign in promotion_log.json? (Engine handles
    promo priority; just note it.)

Frame: "Today's action session. Ledger shows <X> est. API calls today.
Volumes come from the plan file. Confirm?" — WAIT FOR EXPLICIT CONFIRM,
unless allowed command #6 prints "confirmed" (PRE-CONFIRM FLAG): then
send the frame and continue. No response in 15 min → end safely, no
clicks, day NOT consumed (zero-click halt).
CONFIRMED → NOW claim the ledger (allowed command #3), then the first click.

== STATE READ + PLAN (no clicks yet) ==

Read: ig_follow_tracker.json (last_session, active count) ·
ig_target_list.json (queue size; builder >14d old → flag, don't refuse) ·
promotion_log.json (skip promo_window_closed campaigns) ·
release_context.json (active release) · ig_blocked_accounts.json +
ig_personal_network.json (cross-check before any click).

READING THE PLAN FILE (2026-09-21): open `scene_intelligence/session_plan_<date>.json`
with the Read tool, never through Bash. A Bash read such as
`python3 -m json.tool ... | head -150` is not a listed command and prompted
on 09-21. (If you must use Bash, exactly
`python3 -m json.tool scene_intelligence/session_plan_<date>.json` is
pre-approved; do not pipe or reshape it.)

MANDATORY — generate the plan (allowed command #2). The engine applies
every filter (blocked/personal, recency, ratio, label cap, vetted-only
reach, the export-gated unfollow sweep) and writes
`session_plan_<today>.json`. **The plan file's volumes are the session's
volumes — never numbers remembered from docs.** (Set by CURRENT_PHASE in
ig_engagement_config.py.) Engage ONLY handles from the plan file. If the
command errors: STOP, tell Amir, never hand-pick.

== REACH (like-then-follow) ==

Source: the plan file (drawn from queue entries with status="pending" and
a fresh audit_date — REACH_VETTED_ONLY). Never pull entries with any other
status (violations on 2026-05-11/13 required artist cleanup).

Live-check each candidate at follow time: public · 200-2,500 followers ·
>=12 posts · bio present · ratio < 8:1 · last post <= 60 days (Amir, 2026-09-11:
"two months is fine for a post"; config REACH.max_post_recency_days) · not verified · no Hebrew/Israeli signals.
Fail → skip `filter_failed_at_runtime`, take the next pending.

FOLLOW BUTTON NOT RENDERED (IG desktop bug, real and current): no action
button on the profile → reload the profile (typed URL, full reload), wait
3-5s, up to TWO reloads. Still absent → log
reason=button_missing_after_reload, move on. Never counts toward breakers.

NO "SUGGESTED FOR YOU" (Amir, 2026-09-08: "not worth it"; rule re-stated
2026-09-14 after a session used it anyway). Never pull follow candidates
from Instagram's Suggested-for-You panel, on any page, for any reason.
A dry queue means fewer follows today, not different candidates. Follow
supply is ONLY: the plan file's reach_follows, then passed vets. If both are
exhausted, stop following and say so in the report.

== VET IN BROWSER (added 2026-09-06 — replaces the API freshness audit) ==

Source: the plan file's `vet_profiles` list (present only when the vetted
pool is under 30; up to 6 handles). These are NOT follows. They are
profile views, done the way a person browses: open the profile, read what
is on the page, open the newest post to see its date, leave.
Since 2026-09-11 the list is filled FIRST from candidates the old API audit
already cleared on size, ratio and bio and dropped only for a stale post
(least-stale first); a pass revives them into the pool. Then unvetted names.

For each handle log exactly ONE line with allowed command #1, values as
read on the page:
  python3 scene_intelligence/ig_log_action.py --action-type ig_vet \
      --handle <handle> --followers N --following N --posts N \
      --public --last-post-days N --bio "<the bio text, verbatim>"
  (private profile: `--private` and drop the counts)
- followers / following / posts: the counts in the profile header ("1,234" →
  1234, "1.2K" → 1200 is fine, the merge parses both).
- private: true if the profile shows the private notice.
- last_post_days: days since the newest post's date (open it, read the date
  under the caption). If the profile is private or has no posts, omit it.
- bio: REQUIRED (2026-09-08). Copy the bio text under the name. If the account
  genuinely has no bio, send "bio": "" — that is a fail, not a missing field.
  Without it the merge cannot vet the entry at all, because the engine applies
  its own bio check to anything carrying follower data and would reject the
  candidate forever. The bio also feeds the Hebrew / Israeli-signal guard.
- NO "verdict" field. The merge decides pass/fail from these values using the
  SAME thresholds the engine will apply later (`_meta.vet_checklist` in the
  plan file). A line missing any required value is ignored — nothing gets
  vetted by assertion.

Pace: vets are interleaved with the session like any other profile visit
(one every few minutes), never batched at the start or end.

Follow-now rule: a vet that passes may be followed in the same session
(log ig_vet first, then the normal like-then-follow with its own ig_follow
line). The follow CEILING for the session is `_meta.follows_target` in the
plan file (the phase target), NOT the length of `reach_follows`: fill it
first from `reach_follows`, then from passed vets. Nothing else.
When the queue is dry (`reach_follows` empty), passed vets are the only
follow supply, up to that same ceiling.

== SCENE (likes) ==

Source: the plan file. The engine already excludes: blocked/personal/hidden
handles, always-skip categories (venue/media/festival/platform/distributor),
score <3, labels >5,000 followers, anything >15,000, dead handles — and
enforces the 70/30 DJ-vs-label cap (MAX_LABEL_LIKE_RATIO). Trust the plan;
never hand-pick.

NEVER engage own-release labels (@mmdiscos, @stereo.society, @nanadisc) or
closed-campaign contacts. If one surfaces: don't click, tell Amir.

== UNFOLLOWS (export-gated) ==

Source: ONLY the plan file's sweep list. The engine refuses candidates
whose reciprocity isn't proven by a recent export covering their whole
follow-back window (SWEEP_* constants) — an empty sweep on a given day is
correct behavior, not a failure. Reciprocity truth comes from Amir's
~30-day IG data export; there is no same-day checker anymore.

RECIPROCATOR VISUAL GUARD (mandatory, second layer): before clicking
"Following", zoom-check BOTH the header zone AND the bio zone for any
"Follows you" / mutual indicator (single-zone checks missed the badge).
Indicator present → ABORT, append exactly:
  {"ts":"...","action":"ig_unfollow_aborted","handle":"<no_at>","track":"unfollow","reason":"visible_reciprocator","indicator_seen":"Follows you"}
(the merge auto-marks followed_back from THIS action name — never log it
as a generic skip). The badge is ground truth over the tracker.

`followed_back: true` in the tracker = permanent keep under the current
(provisional, under data review ~Nov 2026) skip rule — independent of
keep_following. Never reason "keep_following=false so it's OK" (that exact
reasoning churned 7 reciprocators on 2026-07-15).

Click "Following" → "Unfollow"; verify the button returns to "Follow"
(retry once; else skip unfollow_did_not_register). Wait 20-40s.

== EXECUTION STYLE ==

INTERLEAVED, never batched: 1 Reach → 2-3 Scene likes → 1 Unfollow →
repeat until the plan's counts are done. Spread evenly.

Per-profile: land via typed URL only · header dwell 2-3s · grid scroll
2-3s · pre-action pause 2-3s · pick the most recent eligible post (grey
heart, not sponsored, regular post, within the source's recency window;
Scene like-eligibility <= 90 days) · try top 3 posts, else skip
all_recent_sponsored_or_already_liked · ONE like per profile.

Waits: Reach heart→follow 15-25s, after follow 25-45s; Scene 12-20s
between; distraction pause 30-60s every 4-6 actions.

CLICK VERIFICATION (use small zoom-region captures, not full-page
screenshots — full-page capture is what killed the 2026-08-26 session):
heart red within 1s (retry once, else skip click_did_not_register);
Follow → "Following" within 1s (retry once); "Requested" = private —
don't log as a follow, tell Amir to retract on phone. Batch predictable
click sequences (browser_batch) and reload the tab between phases if
Chrome gets slow.

STREAMING JSONL (mandatory): after EVERY action run allowed command #1,
which appends the line to `scene_intelligence/ig_session_<YYYY-MM-DD>.jsonl`
and prints what it wrote. NEVER hand-write the JSON, the timestamp, or the
sequence, and never use `echo >> ...jsonl` (2026-09-18: that shape prompted
on every line and froze the session for hours).

  python3 scene_intelligence/ig_log_action.py --action-type ig_like \
      --handle bovaflux --track reach --pre-warm --post-url <url>
  python3 scene_intelligence/ig_log_action.py --action-type ig_follow \
      --handle bovaflux --track reach --source "<seed handles>"
  python3 scene_intelligence/ig_log_action.py --action-type ig_skip \
      --handle nervecollect --track scene --reason <why> --tier T2 --category label
  python3 scene_intelligence/ig_log_action.py --action-type session_halt \
      --reason "safety: <what>"

Types: ig_like · ig_follow · ig_unfollow · ig_skip · ig_like_skipped ·
ig_unfollow_aborted · ig_vet · session_halt · session_interrupted.
The script refuses a line the merge could not use (a skip with no reason, a
vet missing bio/counts) — fix the flags, never work around it by writing
the file directly. Append-only. If the write fails it exits non-zero: STOP
and tell Amir, never batch-write later (a 2026-05-08 failure lost 10 like
names).

== CIRCUIT BREAKERS ==

Class A — IG signals (429, cascading 400s, could_not_resolve, popup,
action block, captcha, login/phone challenge): STOP at 3 consecutive
same-reason; 48-72h cooldown per §4.2.
Class B — data-quality skips: STOP at 5 consecutive same-reason; no IG
cooldown; flag for the next quiet-day audit.
Class C — 5 consecutive skips of mixed reasons: STOP.
Excluded from all counts: button_missing_after_reload, ig_unfollow_aborted.
Immediate stop, always: any popup / verification / action block.

== ENDING EARLY (scorer contract, T-006) ==

If the session ends before its targets for a GOOD reason, append ONE final
JSONL event so the scorer treats it as protocol compliance, not
under-delivery:
  {"ts":"...","action":"session_halt","reason":"safety: <what>", ...}   or
  {"ts":"...","action":"session_halt","reason":"infrastructure: <what>", ...}
safety = you found something wrong (bad data, protection gap) and stopped
to escalate. infrastructure = Chrome/renderer/token/tooling died. Anything
else is NOT a halt reason and volumes score normally. A halt never masks a
CAPTCHA — detection deductions always apply.

MID-SESSION PAUSE >15 min waiting on Amir → refresh + re-verify scope;
>60 min → end safely (slot consumed). SESSION DURATION target <= 50 min.
OFF-LIMITS surfaces: Activity, Notifications, Search, Reels feed, Saved,
Inbox, Stories tray, Explore, profile dropdown/logout, DMs.
OUT-OF-SCOPE requests mid-session: decline politely, note for after.
NETWORK/BROWSER failure: stop, log session_interrupted (or session_halt
infrastructure if targets unmet), report what completed. Slot consumed.

== POST-SESSION (self-closing) ==

FINAL STEP — run allowed command #4 (close_loops). Local, zero API. It
merges (fabrication guard), scores 0-10, writes the loop-close report.
Quote its output VERBATIM. Never --force / --resume (Amir's alone).

Report to Amir, short (his rule): loop-closer score + any NEEDS-AMIR line
verbatim · follows N/<plan> with sources · likes M/<plan> by tier + DJ/label
split · unfollows U/<plan> + visual-guard aborts · notable skips by class ·
private/Requested to retract · anomalies · duration · files written ·
"Next session: next of Mon/Wed/Fri/Sat at 15:00 Berlin."

== THIS SESSION NEVER DOES ==

Run any IG-API script (the four allowed commands make zero IG API calls) ·
edit state JSONs (STRICT 1) · invent dates or numbers (STRICT 2-4) ·
--live/--force/--resume/--override-ledger · story views, comments, DMs,
link clicks, settings · post or reply (Amir publishes; 60-min comment rule
is his) · follow back fans (Amir's manual call) · engage own-release labels
or closed campaigns · unfollow anyone showing "Follows you" · clear pauses
or cooldowns (Amir's alone, permanently).

Deep reference: docs/ig-engagement-sop.md (rules rationale + history).
