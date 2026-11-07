# IG Ops Autopilot — design (2026-08-27, approved direction by Amir)

**Problem:** the system depends on a human remembering to run scripts in the
right order with the right spacing ("checker in the morning, audit on a quiet
day, builder every two weeks, 3h apart"). Missed windows are the #1 cause of
degraded sessions. Second: engagement sessions should run from Claude Code
(this app) from now on, not from CC/Cowork.

## Part 1 — the dispatcher (zero Claude tokens)

One deterministic Python script, `scene_intelligence/ig_dispatcher.py`, run
automatically every morning (~09:30 Berlin). It decides what the day needs and
runs it, with one shared call budget. No model, no tokens, no human.

Decision rules (priority order, all state-driven):
1. HARD GATES first: autonomy pause set -> do nothing, notify. Detection event
   within its cooldown window -> do nothing, notify. (This finally makes
   detection_events.json/autonomy_state.json ENFORCED - closes review gap L1
   for the API side.)
2. Session day (Mon/Wed/Fri/Sat): run follow-back checker (~15 calls) so the
   sweep has same-day data. Reserve remaining headroom for the session. Nothing
   else API-heavy.
3. Quiet day (Tue/Thu): exactly ONE maintenance job, chosen by need:
   a. vetted pool < 30 -> freshness audit (--count sized to budget)
   b. else builder age > 14d -> queue builder
   c. else borderline-contact recheck due -> recheck
   d. else nothing (log "nothing needed")
4. Sunday: off.
5. Budget ledger: dispatcher tracks estimated calls per script in the daily
   ledger (extend entries with est_calls); hard stop before 150/day; target
   <100. Spacing solved structurally: one dispatcher, sequential, one slot.
6. Every decision (run OR skip) appended to docs/reports/dispatch-log.md:
   date, what, why, calls, outcome.

Scheduling mechanism: launchd agent (survives app being closed; pure Python
needs no Claude). Notification on failure via the existing notify_mac pattern.
Scheduled-task fallback if Amir prefers seeing it in the app.

Prerequisite small fixes folded in: consecutive-400 breaker in the audit;
perma-400 accounts retired after N failures; checker/audit accept --max-calls.

## Part 2 — sessions run from Claude Code (this app)

Already true mechanically: the "ig-engagement" scheduled task (daily 11:00,
created 2026-08-26) runs IN this app and reads docs/cowork-task-ig.md live.
Wednesday's session proved the claude-in-chrome path works. Remaining work:
1. Rewrite docs/cowork-task-ig.md from "CC + reminder architecture" to the
   single-operator model: this app is hands AND brain; same hard rules
   (plan-file-only targets, JSONL log, popup stop, Amir confirms pre-flight
   and action #1; adjacent-account scope rules unchanged).
2. Session claims the daily ledger at start (decision #3, approved) via
   `python3 scene_intelligence/ig_daily_ledger.py --claim ig_session` (add
   tiny CLI; --override-ledger semantics for the checker+session combo day).
3. Update ig-agent-context.md roles section + SOP §2; retire CC-specific
   passages; Amir deletes any remaining Cowork tasks.
4. Chrome stability: Wednesday died on screenshot capture. Mitigations in the
   playbook: prefer zoom-region captures (small), reload tab between phases,
   reconnect procedure documented, end-safely rule unchanged.

## Part 3 — tokens and model for sessions

- API/maintenance side: ZERO tokens after Part 1 (pure Python).
- Plan + loop close: already scripts. ZERO tokens.
- The session itself is the only token consumer. Levers, in order of impact:
  1. Model: engagement clicking is strict rule-following with vision checks.
     Recommendation: Sonnet 5 for scheduled session runs (large cost drop vs
     Opus/Fable-class, fully capable of the playbook). Keep Fable/Opus for
     reviews, audits, code. Mechanism: the scheduled task runs on the app's
     default model -- set default to Sonnet, or /model per interactive session.
  2. Zoom-region verification instead of full screenshots (a heart check is
     ~500x100px, ~10x cheaper than full-page).
  3. Batched click sequences (browser_batch) - fewer round trips.
  4. Playbook slimming for the single-operator model (shorter mandatory read).
- Escalation rule: anything unexpected (popup, detection, layout change) ->
  the session STOPS and reports; judgment calls stay with Amir + the big model.

## Rollout
- Fri 2026-08-28: one-time scheduled task runs the checker 10:10 (created);
  session 11:00 via existing task. Manual watch, last CC-era day.
- Sun 2026-08-31: implementation session — dispatcher + audit fixes + ledger
  CLI + playbook rewrite + structural batch from the review (pause hard-block
  everywhere, atomic ledger write, reconcile protections, engagement-log key
  fix). Test suite + dry-runs; launchd install; delete one-time tasks.
- Week after: watch dispatch-log daily, tune budgets.

## Part 4 — DATA MAINTENANCE REGISTRY (added 2026-08-31; missing from the
## original design — caught by Amir when 472/488 contacts turned out to be
## 3-6 months stale)

The original dispatcher design only covered OPERATIONAL jobs (checker, audit,
builder). Data itself also rots, and nothing owned that. These jobs are
stats-TRIGGERED, not calendar-triggered: the dispatcher evaluates the trigger
each quiet day and runs the highest-priority job whose trigger fires. If
nothing fires, nothing runs.

| Job | Trigger (evaluated from local state, 0 calls) | Cost / batch |
|---|---|---|
| Contact re-enrichment | any contact ig_enriched_at > 90d (currently 472) | 40-50 profile fetches/day, oldest first, resumable cursor |
| Seed yield review | every 2nd builder run: recompute per-seed yield from queue provenance; report seeds <5% for Amir retire/replace call | 0 calls (local) |
| Reciprocity export refresh | followback_verified_at older than the sweep window across entries (T-002 export flow) | export walk or Amir data-download |
| Guard-held label recheck | any contact excluded by LABEL_CEILING_STALE_GUARD | ~1 call per held label |
| Dead-handle purge | ig_handle_dead or repeated perma-400s | 0 calls (local flag sweep) |
| Cookie age probe | first API call of the day doubles as the probe (already true) | 0 extra |
| Queue compaction | skipped_stale > 60% of queue | 0 calls (local) |

Priority when several fire on one quiet day: reciprocity > guard-held labels >
re-enrichment batch > builder > audit > seed review > compaction.
Rule of the registry: ANY new data file or measurement added to the system
MUST land here with a trigger, or it will silently rot like enrichment did.

Seed policy (2026-08-31, from the first yield analysis): seeds are judged on
measured yield, not fame. Winning profile: label, 1-6.5k followers, genre
bullseye, human-run. Big anchors (lebanonhanover 3.4%) retired; five cut,
six stats-derived added (incl. Amir's samo_records). Review at every 2nd
builder run per the registry.

### Registry amendments — 2026-08-31 full data-estate sweep (Amir-approved)

The first registry pass was still incomplete; a whole-estate inventory found
eight more. Lesson folded into the standing rule: the registry is only
trustworthy after a FULL file sweep, so the sweep itself is now a job here.

ONE-TIME FIXES (do first, highest value):
| # | Fix | Detail |
|---|---|---|
| A | Engagement-log key normalization | 77 of 1,854 keys are display-name-styled ("Samo Records") and invisible to handle-based cooldown lookups -> contacts re-served early. Merge into handle keys via the SI name->ig_username mapping; backup first; verify cooldowns see merged history. |
| B | Paid-audience pipeline repair | ig_paid_audience_seed.json frozen at 54 entries since May while total_followed hit 315. The engine only appends on engine-native --live runs, which never happen now -> browser-session merges must feed it. Backfill from tracker + engagement_log, then wire into the merge. This is the future ad-targeting dataset. |
| C | session_reports.json retirement | 111d stale, 2 entries, still a gate source for the legacy engine path. Once 2.0 gates (detection_events + autonomy_state) are confirmed the only live path, archive it and delete the corrupt-reset hazard in save_session_report. |

RECURRING JOBS (stats-triggered, joining the Part 4 table):
| Job | Trigger | Cost |
|---|---|---|
| Follower-side refresh (roster, notable, verified-classified) | any of the three files > 45d old (currently 78d) | roster walk ~5-19 calls on a quiet day; feeds mutual-follow seeds + social proof + reciprocity export |
| Legacy IG-enrichment fold-in | ig_enriched_contacts/ig_enrich_queue referenced by any consumer | fold into main re-enrichment batches; if no consumer remains, freeze + archive |
| Content-data refresh (voice profile, collaborators) | > 120d old | local rebuild scripts, 0 API |
| backups/ retention | dir > 20MB or file > 60d | keep 60d + one monthly keeper; local |
| engagement_log archival | log > 1.5MB or events > 6k | move events > 12mo to engagement_log_archive_<year>.json; cooldowns read <=90d so safe; churn history lives in the tracker, NOT pruned |
| Full data-estate sweep | quarterly, or after any new tool ships | the inventory that produced this amendment; 0 API |

Priority insert: one-time fixes A/B/C ahead of everything except reciprocity;
follower-side refresh slots after re-enrichment batches.

### Registry status update 2026-09-01 (T-016)
- Re-enrichment rung: LIVE in dispatcher (08-31).
- Seed-yield report: LIVE — auto-generated after every builder run.
- Follower-side refresh: SUPERSEDED by the monthly export (roster walks are
  banned since 08-30; the export carries followers+following+timestamps and
  the manual-follows intake diff runs on each export). Legacy roster files
  (ig_follower_roster / notable / verified-classified) stay frozen as
  June snapshots — consumers should read the newest export instead.
- Content-data refresh (voice profile, collaborators): trigger 120d, not yet
  fired (currently ~90d). Estate sweep: quarterly, next ~Dec 1.


## Amendment 2026-09-14 — reads move to a data provider (T-024)

The 09-14 test (10 reads after 8 quiet days) got a 429 on call 1. Conclusion:
Instagram fingerprints the Python client; the flag does not decay. Decision
(Amir): every Instagram READ goes through HikerAPI (key in .env). Effects on
the registry: the timing law (one API job/day, daytime, rest day, 150 ceiling,
session-day reservation) no longer applies to reads — it protected the
account, and provider reads never touch it. The ledger keeps a `provider`
kind with a money cap (`PROVIDER.daily_call_cap`). Dispatcher provider day:
audit sized by backlog (100/day while unchecked > 300, else 60), builder only
when unchecked < 200, best-yield seeds first with new seeds interleaved.
Follows per session are unchanged (that is the account-side pace Instagram
watches). The old direct-read code stays for reference but is switched off
(`IG_DIRECT_API_ENABLED=False`).
