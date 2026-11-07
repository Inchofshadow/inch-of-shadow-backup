# IG Engagement Automation Review — 2026-08-25

**Scope:** the IG engagement automation only (engine, driver, queue builder, freshness audit, follow-back checker, merge/reconcile/accounting scripts, ledger, health check, config, and the live state JSONs). Narrower and deeper than the 2026-07-04 full-repo audit ([full-audit-2026-07-04.md](full-audit-2026-07-04.md)); this one verified how the safety rules hold up *after* the July fixes landed.
**Method:** 4 parallel read-only reviewers (core engine / driver+rails / queue+targeting / accounting+reconciliation), findings verified in code with line numbers, live state files cross-checked on disk. Nothing was edited during the review.
**Requested by:** Amir, 2026-08-25 ("review all the scripts, find loopholes, tell me what decisions I need to take").

**Status column updated 2026-08-26** — several findings were fixed the next day (commits `6ea945f` checkpoint, `5d32453` fix batch); each is marked.

---

## Executive summary

The day-to-day machinery (caps, timing, protected-account checks inside the sweep, confirm-before-count) held up well. The two biggest safety *promises*, however, were not enforced anywhere:

1. **The detection pause is enforced by nothing.** `detection_events.json` and `autonomy_state.json` are read by zero code. The engine's only detection gate reads `session_reports.json` — frozen at 2026-05-12 with no circuit-breaker entries. A CAPTCHA that pauses autonomy does not stop any script. `close_loops.py --resume` has no authorization check. The health check reports a live pause as a WARNING whose verdict says "safe to run". **OPEN.**
2. **Real sessions are invisible to the daily ledger.** The 1-script/day ledger binds Python entrypoints only; browser-driven sessions (the only kind that actually runs) never claim it. ~13 live sessions since 07-20 left no ledger trace. `--override-ledger` was used on 4 of 19 entries — routine, not exceptional. **OPEN** (decision pending: should sessions claim the slot?).

## Loopholes (ranked)

| # | Finding | Status |
|---|---------|--------|
| L1 | Detection pause read by no code; `--resume` unauthorized; health check calls a pause "safe to run" | OPEN |
| L2 | CC/browser sessions never claim the ledger; rule cannot see half the system | OPEN |
| L3 | One-flag bypasses: `--override-ledger` (used 4/19), `--no-preflight` skips schedule+hour+FB-breaker on live runs (CLI recommends it when the breaker trips), `--phase 2` bypasses the Phase-2 hold | OPEN |
| L4 | Corrupt-JSON resets: `save_session_report` silently replaces an unparseable reports file (dry runs write too → detection history laundered); queue builder `_load_json` silently empties blocklist/tracker/personal-network and can overwrite the 1,515-entry queue with a fresh batch | OPEN |
| L5 | `ig_reconcile_followings.py` has no keep/followed-back exemption — a partial roster fetch (60-page cap, or IG's empty-page soft-fail) moves protected accounts to `unfollowed_history`, permanently blacklisting them | OPEN |
| L6 | Verification-class stop superseded by any later softer breaker event (guard keeps only the latest); `cooldown_ack` is an unauthenticated JSON field | OPEN |
| L7 | Protection lists apply at queue-add time only; nothing re-screens existing entries (3 blocked + 3 personal accounts sat inert in the queue; pending set verified clean) | OPEN |

## Live-data issues found (all fixed 2026-08-26 with Amir's approval)

- 4 protected accounts carried `followed_back: true` AND `overdue_unfollow: true` simultaneously (mosaikbeats, perpetual_midnight84, rotkha.delirium, xoobinwood) — flags cleared. **FIXED**
- `molly.lollen` was the only personal-network entry without `keep_following: true` — flag added; all 37 entries covered. **FIXED**
- Tracker accounting: `stats.total_unfollowed` (261) vs `len(unfollowed_history)` (283); reconcile decrements `total_followed` (inflates the follow-back-rate denominator); stray `stats.total_follows` key. **OPEN** (definition decision needed)
- ~1 month of changes to safety-critical scripts uncommitted — no rollback point. **FIXED** (checkpoint `6ea945f`, 125 files)

## Bugs (second tier)

- **Locking/atomicity:** ledger claim is read-modify-write with plain overwrite (two writers both claim); queue builder and freshness audit hold the queue in memory for 5–15 min of API calls then write the whole file (clobbers concurrent edits); audit write not tmp+rename; merge double-counts `engagement_log` on crash-then-rerun (idempotency guard runs last). OPEN
- **Engagement-log key mismatch:** engine writes likes/skips under SI *name*, cooldowns look up by *handle* → cooldowns silently fail for affected contacts (log is 1753/1830 handle-keyed). OPEN
- **Follower gate skipped on unknown counts:** `if live_followers_int and ...` lets 0/None bypass the 200 minimum. OPEN
- **Circuit-breaker substring-matches the whole response body** (bio containing "action blocked" trips a 48h cooldown — same class as SC's "No CAPTCHA" false positive; fails safe). OPEN
- Smaller: like-before-follow likes uncounted; freshness audit discards all enrichment unless ≥1 stale found; UTC/local day-boundary window 00:00–02:00 Berlin; build-time queue filters decorative on missing fields (only real gate = "≥2 seeds"); history-entry schema fork (reconcile vs merge fields); checker leaves 404'd accounts active forever. OPEN

## Validated as good

Unfollow sweep honors keep-flags, follow-backs, and does a live "follows you" re-check before acting; ledger fails closed on corrupt files; engine state writes atomic; dry runs touch no live state; driver identity gate fails closed; confirm-before-count discipline real (`_friendship_confirmed`).

## Decisions taken since (2026-08-26)

- Phase stays **1b** (the Phase-2 downgrade's justification was the fabricated Aug-19 warning, but restore still awaits an explicit go).
- Scheduled task recreated as a **pointer** to `docs/cowork-task-ig.md` (reads the BODY at run time; hard-stop if unreadable) — kills task/doc sync drift; doc's stale Phase-2 volumes corrected to 1b.
- Same-day fix batch shipped after the Wed session confirmed two failure modes live (reciprocator badge unreliable → @infoluences churn; render bug = no Follow button): `FOLLOWBACK_MAX_STALE_DAYS=1`, `REACH_VETTED_ONLY`, `LABEL_CEILING_STALE_GUARD`, `NO_NEW_CONTENT_COOLDOWN_DAYS=30`, merge recognizes `button_missing_after_reload`. See commit `5d32453`.

## Still-open decision list (Amir)

1. Should the autonomy pause hard-block all entrypoints, and who may `--resume`? (L1)
2. Should browser sessions claim the daily ledger slot? (L2)
3. Reconcile the SOP §4.1 150-call/day budget with the 1-script/day ledger — pick one law. (L3)
4. Restore Phase 2 (10F/8U/25L) or stay 1b?
5. Tracker accounting definition (`total_unfollowed` vs history length; stop reconcile decrementing `total_followed`).
6. Structural fix session for L4–L7 + the atomicity/locking bug class (coordinate so it doesn't clash with CC).
