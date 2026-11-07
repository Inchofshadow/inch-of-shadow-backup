# IG System Findings — 2026-08-30 (Sunday, off-day)

**Requested by:** Amir ("less chats, more focus; investigate the pipelines/events, API limits, the clicking surface, redundant files; prepare a doc; I decide").
**Method:** read-only investigation. Every number below traces to a file, commit, or scheduler state; hypotheses are labeled as hypotheses. Nothing was edited except this report, `TICKETS.md`, and memory notes.
**Builds on:** [ig-automation-review-2026-08-25.md](ig-automation-review-2026-08-25.md) (loopholes L1–L7) and the 08-26/08-28 fix batches (commits `5d32453`, `1fb66fa`). This doc absorbs what changed since and answers today's new questions.

---

## TL;DR

1. **The low session rate is fully explained by stop-gaps, not by the engine.** 9 of 17 August action days ran (53%). Every miss has a named cause: 3 days around the Tel Aviv return, 4 days of fabricated-warning fallout, 1 day of the 08-29 pause. Since 08-14, session quality is at target (scores 8,7,10,7,8).
2. **Uptime is the KPI bottleneck, and uptime dies on enforcement gaps.** The pause/detection state is still enforced by prose, not code (a real pause would have been silently ignored until the 08-29 fix, commit `e6db399`). The already-approved dispatcher design closes this; it is designed but not built.
3. **The riskiest API jobs can be eliminated, not throttled.** Both August API incidents came from bulk reads (`web_profile_info` streak 08-27, roster walk 401 on 08-29). Instagram's official "Download your information" export gives the same reciprocity ground truth with **zero API calls**. Recommended.
4. **Keep the Chrome-profile clicking surface.** Zero IG detection events have ever come from the browser side; every alternative (Playwright, private API, simulator) is strictly riskier. Harden it, don't replace it.
5. **The system is scattered mostly in its docs and file hygiene, not its code.** 181KB of mandatory reading per session, three dead CC-era task bodies, a self-contradicting SOP rule, 104 backup files sitting next to live state. Consolidation list below.
6. **New working method starts now:** `TICKETS.md` at repo root is the queue. You approve/prioritize tickets, I execute and report per ticket.

**Current hard state:** IG automation is **PAUSED** (you, 2026-08-29, precautionary after the roster-walk 401; no account-level signal). Vetted reach pool **19/30**. Reciprocity **unmeasured** (25 of 27 active follows have `user_id: null`, 0 verified). Followers **925** as of 08-16 (no fresher number exists; the insights fetcher doesn't pull follower count). 0 posts since mid-July.

---

## 1. Where the session rate actually went

August action days (Mon/Wed/Fri/Sat), from `autonomy_state.json` processed list:

| Window | Days | Ran? | Cause (sourced) |
|---|---|---|---|
| Aug 1, 3, 5 | 3 | ✗ | Tel Aviv return window (back 08-03); no sessions logged |
| Aug 7 → 17 | 7 | ✓ all 7 | Scores 4, 2, 4, 3, 8, 7, 10 — rough CC-era start, then the 08-14 turnaround |
| Aug 19, 21, 22, 24 | 4 | ✗ | Fabricated 08-19 "warning" fallout (record confirmed fabricated 08-25, purged) |
| Aug 26, 28 | 2 | ✓ | 7 (Chrome renderer died mid-session), 8 (deliberate P0 safety halt) |
| Aug 29 | 1 | ✗ | Your pause after the roster-walk 401 |
| **Total** | **17** | **9 (53%)** | |

For contrast: Jul 20–29 ran 6 of 6 action days. "We're not on the wave" is accurate, and the wave was broken by **stop-gaps, not by session quality** — post-rescore scores since 08-14 average 8.0, which meets the ≥8 KPI.

**Second-order finding:** 4 of 9 August sessions needed a manual rescore (08-15, 08-17, 08-26, 08-28) because the scorer still punishes volume shortfalls on safety/infrastructure stops even though the precedent is settled. The scorer should encode the rule at the source → **T-006**.

**KPI reality check** (per [ig-kpis] targets):

| KPI | Target | Now | Verdict |
|---|---|---|---|
| Session score | ≥8 | 8.0 avg since 08-14 | ✅ (after rescores) |
| Vetted reach pool | ≥30 | **19** | ❌ supply-bound |
| Follow-back conversion (new cohorts) | ≥15% | **unmeasurable** | ❌ P0: 25/27 null user_id, 0 verified |
| Reciprocators churned | 0 | 2 in Aug (@infoluences, @_.miser._) | ❌ both from the same measurement gap, now fail-closed |
| Followers | +50–60/mo | 925 @ 08-16 (+135 since May ≈ +45/mo) | ⚠️ close; no fresh number |
| Posts published | content floor | 0 since mid-July | ❌ the actual growth ceiling |

Conversion is the lever (your standing through-line), and conversion is currently **unmeasured**. Fixing measurement (§4) is worth more than any volume change.

---

## 2. Event & trigger inventory — what fires, when, and what it costs

Verified against `launchctl`, `crontab`, and the app's scheduled tasks. **There is no cron and no launchd job for IG.** The complete list of things that can fire IG automation:

| # | Trigger | Schedule | What it does | API calls | Status | Verdict |
|---|---|---|---|---|---|---|
| E1 | `ig-engagement` scheduled task | Daily 15:00 Berlin (+jitter), self-skips Tue/Thu/Sun | Reads `docs/cowork-task-ig.md` BODY, runs the browser session | 0 (browser only; plan/close scripts are local) | **PAUSED** since 08-29 | Keep — this is the correct single session entry point |
| E2 | `ig-weekly-release-stats` task | Sun 20:00 Berlin | `ig_fetch_insights.py` (Graph API, own account, token-based, IP-safe) + logs | 13 (1 + 12 media) | Ran today | **Repoint**: its own 08-30 output says the Deceiver pull is plateaued and should stop until the next release → T-007 |
| E3 | `ig-followback-friday-probe` task | One-time 08-28, done | Checker as API health probe | ~15 | Spent | **Delete** the task entry (housekeeping) |
| E4 | Manual API scripts (checker / queue builder / freshness audit / backfill / reconcile) | Ad-hoc, human-remembered | Maintain tracker + queue | checker ~15 · audit ≈1.4×count (68 on 08-27) · roster walk ~43 · builder: unmeasured · enrich **238 (banned)** | Ledger-gated, 1/day | **Merge into dispatcher** (E5) |
| E5 | `ig_dispatcher.py` | Designed for ~09:30 daily via launchd | Picks THE one right job by state; enforces pauses, cooldowns, budget centrally | ≤ budget | **Designed 08-27, not built** ([../plans/ig-ops-autopilot.md](../../plans/ig-ops-autopilot.md)) | **Build — this is the merge/remove answer** |

Your instinct "the system triggers calls without knowing how many we need or when" is confirmed, with a nuance: the *schedule* side is actually small and clean now (one session task + one stats task). The chaos lives in **E4** — the human-remembered script layer where ordering, spacing, and budget exist only as prose. The dispatcher replaces E4 entirely: one decision point per morning, one shared budget, every skip logged. Nothing else needs merging; E3 needs deleting; E2 needs repointing.

**What the timing should be (already settled, for the record):** session 15:00 Berlin (settled 08-27 after trying 11:00 and 20:00, clear of SC by 3.5h), dispatcher ~09:30 (so checker data is same-day fresh for a sweep), weekly stats Sunday (the no-automation day), Sunday otherwise off.

---

## 3. API limits & maintenance — the rules as written vs as enforced

**The written law is contradictory.** `docs/ig-engagement-sop.md` says both:
- line ~111: the one-script/day rule was **revised 2026-05-22** → risk is governed by **volume**: hard cap 150 calls/day, soft ~100, writes never stacked on heavy-read days;
- line ~1457: "Hard rule: one IG script per day. Period."

Meanwhile the ledger (`ig_daily_ledger.py`) enforces literal 1-script/day, which is why `--override-ledger` is routine (5 of the last 23 entries) — the tool fights the doctrine. This was review decision #3 and is still open. **Recommendation: adopt the volume law** (150 hard / 100 soft, per-entry `est_calls` in the ledger), keep 1-*API-script* as the dispatcher's default behavior rather than a human rule → folds into T-003.

**Enforcement reality (verified by grep today):**
- `detection_events.json` — read by **zero** scripts. It's a diary, not a gate.
- `autonomy_state.json` pauses — read by `close_loops.py`, `ig_health_check.py`, and (since 08-29) the playbook text. The engine, checker, builder, audit, and backfill have **no pause gate**.
- The engine's only detection gate still reads `session_reports.json`, **frozen since 2026-05-12** — a zombie file that looks like junk but is load-bearing; retire it only together with rewiring the engine gate (T-003).
- Proof this bites: on 08-29 the playbook was checking the legacy `paused` key that stopped existing on 07-24. A real pause would have read as "no pause" and the session would have proceeded. Found and fixed only because you paused manually (commit `e6db399`).

**Endpoint risk classes learned this month (this is the actual "API limits" map):**

| Surface | Evidence | Class |
|---|---|---|
| Graph API insights (own account, token) | Weekly for months, zero incidents | Safe |
| `friendships/show` (per-account, small N) | Checker runs clean at ~15 calls | OK in small doses |
| `web_profile_info` (per-account profile reads) | 16-long 400/404 streak on 08-27 after ~50 reads (suspected soft throttle — **unconfirmed hypothesis**) | Throttle-prone; needs consecutive-400 breaker (T-003) |
| Follower-roster enumeration (40 pages) | Full walk OK, immediate second attempt → **sessionid invalidated (401)** on 08-29 (anti-enumeration reading is a **hypothesis**; no account-level signal) | Avoid entirely — replace with the export (§4) |
| Bulk enrich (238 fetches) | Caused the 2026-05-03 detection | Permanently banned (already) |
| Browser session (real Chrome) | ~20+ sessions, **zero IG detection events ever** | Cleanest surface we have |

---

## 4. Reciprocity ground truth — stop walking the roster, use the official export

The P0 chain (@infoluences, @_.miser._, the fake 1.9% follow-back rate) all came from one gap: we can't reliably know who follows back. The roster-walk backfill was the right idea and got the token invalidated anyway.

**Proposal: Instagram's own data export.** Accounts Center → Your information and permissions → Download your information → followers and following. IG generates followers/following JSON itself. Reciprocity becomes set-membership against a file IG handed you:
- **Zero API calls, zero detection surface** — it's the official feature for exactly this.
- Replaces: the roster-walk backfill (T-010 becomes unnecessary), the bulk part of the checker (keep `friendships/show` spot-checks for same-day pre-sweep verification only), and the stale `ig_follower_roster.json` refresh.
- Cost: ~5 minutes of your time per pull + IG's preparation delay; data is point-in-time, so it feeds the monthly truth while the small checker guards sweep days.
- Caveat (flagged per no-wrong-answers): I have not seen a 2026 export from your account; exact file format gets verified on the first pull before any code consumes it. `data/` already holds older IG ZIP exports, so the pattern exists in this repo.

→ **T-002 (decision D2).** If approved, the unfollow lane comes back to life safely: export = truth, `followback_verified_at` written from it, fail-closed gate already shipped (`1fb66fa`).

---

## 5. The clicking surface — is there something better than the inchofshadow Chrome profile?

Short answer: **no, and the data says so.** Compared honestly:

| Option | Assessment | Verdict |
|---|---|---|
| **Current: claude-in-chrome on your real "Amir (Inch of Shadow)" profile** | Aged cookies, consistent fingerprint, mixed human+assisted usage; zero IG detection events across ~20+ sessions | **Keep** |
| Playwright / fresh automation profile | Cold fingerprint + CDP automation signals; strictly worse than an aged human profile | No |
| Private API libs (instagrapi etc.) | Highest ban class for an aged account; also credential handling I won't do | No |
| Official Graph API | Cannot like/follow other accounts at all — keep it for insights only | N/A for engagement |
| iOS Simulator + IG app | New device signature → login challenge risk on a 9-year account | No |
| Manual-only | Zero risk, zero scale | Fallback during pauses |

The browser surface is not what's been hurting us; the API side is. **Hardening instead of replacing** (all already in the approved autopilot design): zoom-region verification instead of full screenshots (the 08-26 death was the renderer failing on full-page captures), `browser_batch` sequences, tab reload between phases, end-safely rule unchanged. One addition from me: the session should claim the daily ledger at start (approved decision, tiny CLI, T-003) so browser work finally shows up in the same accounting as scripts.

---

## 6. Old-Claude → current-Claude modernization (know and decide)

Already modernized (more than it may feel like):
- Scheduled task is a **pointer** that reads `docs/cowork-task-ig.md` at fire time (no paste drift, since 08-26).
- Sessions already run **from this app** via claude-in-chrome (CC decommission is de facto done — 08-27 decision; what remains is doc cleanup, not migration).
- Self-closing loops, per-platform pauses, git discipline restored, memory files in active use.

Ready to adopt (each is a ticket):
1. **Sonnet 5 for scheduled session runs** (T-008): clicking is strict rule-following; large cost drop, Fable/Opus stays for reviews/code. Mechanism: app default model (scheduled tasks inherit it).
2. **Slim single-operator playbook** (T-004): today a session must read 3,177 lines / ~181KB (`cowork-task-ig.md` 566 + `ig-agent-context.md` 1,047 + `ig-engagement-sop.md` 1,564) before the first click. Target: one ≤400-line session playbook containing only session-relevant rules; strategy/marketing context stays in its own docs for planning work. Retires the CC-era role text.
3. **Dispatcher on launchd** (T-003): zero-token deterministic mornings; scheduled-task fallback if you prefer seeing it in the app.
4. **Follower count in the weekly pull** (T-007): one extra Graph call fills the monthly KPI that's currently stuck at 08-16.

Not recommended: anything in §5's "No" column, and no refactor of the engine for its own sake — the code held up well in review; the gaps are enforcement wiring and docs.

---

## 7. Redundant files (verified, with readers checked)

Scanned repo-wide; before flagging, I grepped which files live code actually reads. **Policy: nothing deleted — moves into `scene_intelligence/backups/` (existing convention), you approve the sweep (T-005).**

**Dead, retire now (0 readers found):**
- `docs/CC-TASK-BODY-paste-this.txt`, `docs/cowork-ig-engagement-body.md`, `docs/cowork-task-bodies.md` — three superseded CC-era task bodies (83KB combined); canonical is `docs/cowork-task-ig.md` (`cowork-task-sc.md` stays, it's SC's canonical).
- `scene_intelligence/ig_next_session_brief.md` (Jul 5, no readers).
- `docs/ig-status.md` (Jul 5 snapshot, long superseded by `autonomy_state.json` + reports).
- `scene_intelligence/ig_enrich_queue.json`, `.ig_enrich_queue.json` + bak (pipeline banned since May, no readers).
- Root strays: `=1.1.3` (pip typo artifact), `sc_enrich_log_20260501_121209.txt`, `ig_unfollow_list_apr22.md`, `IMG_6992/6993.PNG` (→ artwork/ or bin, your call).

**Archive (bulk, safe to move):**
- **104 `.bak` files sitting in `scene_intelligence/` root (22.2MB)** next to live state — this proximity is exactly how stale-copy bugs happen. `backups/` already holds 79 files/39MB properly.
- 54 old session artifacts in `scene_intelligence/` root (`ig_session_report_*.md`, `session_plan_*.json`, `session_report_*.md`) — superseded by `docs/reports/loop-close-*`.
- 32 dated `discovery_candidates_*` snapshots (keep the newest, 20260828; SC scripts read the pattern).
- 14 dated `releases/*.bak.*` stat backups.

**Looks like junk but is LOAD-BEARING — do not touch:**
- `enriched_contacts.json` — read by 32 scripts.
- `session_reports.json` — frozen zombie, but it is the engine's only detection gate; retire only inside T-003's rewire.
- `ig_follower_roster.json` — stale (Jun 14) but read by `ig_follower_audit.py`; refresh via the export (T-002), don't delete.
- `*.FABRICATED_BY_CC.bak` quarantine files — evidence of the two fabrication incidents; keep (optionally move to `backups/quarantine/`).

---

## 8. Working method + autonomy roadmap

**Tickets:** [`TICKETS.md`](../../TICKETS.md) now exists at repo root, seeded from this doc. Rules are in its header: you approve/prioritize, I execute one ticket at a time and report against it; no work outside tickets except emergencies; decisions carry a D-number.

**Autonomy ladder** (how "you trigger everything" happens without risking the account — each step gated on evidence, you can hold any level):
- **L0 (today):** everything paused. Your resume is D1.
- **L1:** scheduled session fires; you confirm pre-flight + after action #1 (current design).
- **L2** after 3 consecutive clean sessions (≥8, zero safety flags): pre-flight confirm only.
- **L3** after 2 more: sessions run unattended; you get the start notification + end report; every hard-stop unchanged (popup/CAPTCHA/detection/anything unexpected → stop + notify, never improvise). Pause/ledger/budget enforced by code (dispatcher + session ledger claim), not prose.
- API maintenance side reaches L3 on day one via the dispatcher — it's deterministic and 0 tokens.
- **Resumes after any detection event stay human-only, permanently.**

---

## 9. Decisions needed (the whole list)

| # | Decision | My recommendation |
|---|---|---|
| D1 | Clear the 08-29 pause? (`close_loops.py --resume --platform ig`) | Resume **browser sessions** Mon 08-31; keep **API scripts** off until D2 lands. Needs your fresh `.env` cookies only if D2 is rejected |
| D2 | Reciprocity via official IG data export (kills roster walk + bulk checker) | **Yes** — highest value/risk ratio in this doc |
| D3 | Green-light the implementation session: dispatcher + structural batch + ledger CLI + scorer fix (T-003/T-006) | Yes, next working session |
| D4 | Playbook rewrite + CC-era doc retirement (T-004) + file sweep (T-005) | Yes, same session or the one after |
| D5 | Phase 2 restore vs stay 1b | **Stay 1b** until conversion is actually measured ≥15% (your own through-line); revisit after 2 export-verified cohorts |
| D6 | Weekly Deceiver stats task: stop/repoint + add follower-count call (T-007) | Repoint now; it recommended its own retirement today |
| D7 | Model default → Sonnet 5 for scheduled sessions (T-008) | Yes |

---

## Addendum — 2026-08-30 evening (Amir's first pass on the decisions)

- **D1 answered: automation STAYS PAUSED.** No sessions, no API scripts, until Amir says resume.
- **D2 in motion: the export arrived same day** (`data/instagram-inch_of_shadow-2026-08-30-*`) and was verified read-only. Followers file covers 2026-03-04 → 08-30 (176 gross new followers); `following.json` is complete (921, title-keyed — note: each connection file in the export uses a different JSON schema). Since every tracked follow started 2026-05-15 or later, coverage of the automation cohort is total. **Result: 11 of 27 active follows follow back** (5 newly confirmed: andrewredhand, atri_music, dj_kolokol, goia.amo, nocturnazine), 16 verified not following back — an exact match with the 08-29 dry-run walk. Awaiting Amir's go to write `followback_verified_at` + the 5 corrections into the tracker (protects the new reciprocators from any future sweep).
- **New incident surfaced by the export: @xoobinwood** (keep-list, follows us) was unfollowed **2026-07-29 13:13** per IG's own `recently_unfollowed_profiles.json`. The tracker never recorded it (still lists the account as active) — a third reciprocator-churn incident, from the CC era, invisible until now. Re-follow + tracker repair = **T-012**, Amir's call. Also: personal-network entries `delphy_dj` and `berlinesk` are not in the following list (not in the recent-unfollow record either — likely old unfollows or misspelled handles; verify handles when convenient).
- **D6 answered: stats every 2 weeks, as graphs.** Done same evening: the scheduled task now self-gates to biweekly, and each pull updates the **IG Growth** chart page (follower growth curve from the export + Deceiver reach-over-time vs the 925 follower ceiling). Follower-count fetch is added on implementation day with a dry-run verify.
- Plain-English explainers for §3, D3 (dispatcher, ledger CLI, structural batch, scorer fix), and D4 were added to the artifact version.
- **150-call correction (Amir challenged it, double-checked):** the 150/day cap exists only in SOP prose — no script counts calls, nothing enforces it — and it was derived from the single 2026-05-03 incident (~255 calls). Both August incidents fired far below it (~68 and ~43 calls); the trigger was the pattern (consecutive same-endpoint reads, full-list enumeration), not the total. Revised law for T-003: per-endpoint budgets + pattern rules (web_profile_info ≤30/day with a consecutive-400 breaker; roster enumeration never — export instead; friendships/show ≤20/day; one bulk job/day), 150 demoted to absolute never-cross ceiling, ~≤50 as the normal working day. There is no proven safe number.
- **Re-follow policy (Amir, standing):** churned follows are reported as data and the tracker gets fixed; re-following is never suggested. @xoobinwood: no re-follow; ghost entry removal folds into the T-002 write batch. T-012 closed.
- **Rulings late 08-30 (Amir):** sweep gate initially "both", **revised the same night to EXPORT-ONLY**: Amir pulls the export every 30 days; no routine checker calls (saves ~60/week — door 2 closes as a routine consumer). Safety: an account is sweep-eligible only if the newest export is dated ≥ its followed_at + 21 days (covers the whole follow-back window), and the live badge-positive skip at click time stays. Residual risk accepted: a follow-back arriving later than 21 days after the follow can still be missed if the badge fails to render — rare, and consistent with Amir's "automation is just a tool" stance. The checker script survives as an exceptional tool only. Session confirms = both (pre-flight + after action #1); **D7 = Sonnet 5 approved** (apply at resume via app default model). Online re-check of limits: no published numbers exist for the private web endpoints; automation-blog "safe volumes" (300-500 follows/day) are sales-pitch folklore far above anything we would run; the two credible consistent findings — detection flags patterns rather than totals, and follow/unfollow cycling is among the most-monitored behaviors — both support the per-endpoint-budget law and our existing 3-week-window + reciprocator-protection design. Official Graph API (stats side) allows ~200 calls/user/hour, so the biweekly 13-call pull is a non-issue.
- **API LAW APPROVED (Amir, "ok", end of 08-30):** per-endpoint budgets replace both old rules. Profile reads ≤30/day with a consecutive-error breaker; friendship checks exceptional-only (reciprocity is export-only, 30-day cadence); list walks never; one bulk job per day; ~50 calls = a normal day; 150 survives only as the absolute never-cross ceiling. Timing layer: one API job per day in the ~09:30 Berlin dispatcher slot (daytime-only 09:00-21:00 — 8 of the last 23 ledger runs were night runs, those stop), 2-5s jittered spacing inside jobs, ≥5h gap to the 15:00 session (slot re-confirmed; the "busy hours" concern has no documented basis). T-003 implements; T-004 writes it into SOP + playbook.
- **Follow-back sources, for the record:** (1) the official export — ground truth, zero API; (2) `ig_followback_checker.py` (friendships/show, ~15 calls) — same-day spot check that gates sweeps; (3) the profile "Follows you" badge in the browser — positive-only hint, proven unreliable (08-26). Exports are not the only way, but they are the only zero-risk full-truth way.

*Sources: `autonomy_state.json`, `detection_events.json`, `ig_daily_ledger.json`, `ig_follow_tracker.json`, `ig_target_list.json`, `ig_insights.json`, `ig_engagement_config.py`, `docs/ig-engagement-sop.md`, `docs/cowork-task-ig.md`, scheduled-task registry, `launchctl`/`crontab`, git log through `e6db399`, [ig-automation-review-2026-08-25.md](ig-automation-review-2026-08-25.md), plans/ig-ops-autopilot.md. Hypotheses are marked as such (08-27 throttle, 08-29 anti-enumeration).*
