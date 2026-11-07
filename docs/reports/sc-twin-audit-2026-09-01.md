# SC Twin-Bug Audit — 2026-09-01

**Scope:** the SoundCloud engagement stack only — `sc_engagement.py`, `sc_engagement_config.py`, `sc_weekly_health.py`, `sc_log_manual.py`, `check_sc_follows.py`, `sc_browser_likes.py`, `enrich_soundcloud.py`, the SC halves of `close_loops.py` and `json_io.py`, and the live state files (`sc_follow_tracker.json`, `engagement_log.json`, `sc_following_audit.json`, `autonomy_state.json`, `detection_events.json`, discovery/candidate/brief artifacts).
**Method:** read-only. Every IG bug class from [ig-automation-review-2026-08-25.md](ig-automation-review-2026-08-25.md) and the 08-30 findings was hunted for an SC sibling; every claim below is verified in code (file:line) and cross-checked against the state files on disk. Nothing was edited, no API was called, no browser was opened.
**Context:** the IG fixes of 2026-08-26..31 (`5d32453`, `1fb66fa`, `16070d1`, `4fd330a`…) built `ig_ops_guards.py`, the ledger law, the engagement-log key fix, and the fail-closed sweep — **for IG only**. None of it was wired into SC.

Account ratio at last health pass (SOP ratio block):

| | 2026-08-23 | 2026-08-28 | floor | target |
|---|---|---|---|---|
| followers : following | 222/300 = **0.74** | 227/324 = **0.70** | 1:1 | 1.4–1.6:1 |

---

## Executive summary

The SC stack is the IG stack **before** the August fixes. The two headline IG findings both have live SC siblings:

1. **Nothing enforces anything on SC.** The gate module built to close IG-L1 (`ig_ops_guards.py`) even ships an `"sc"` platform alias (`ig_ops_guards.py:130`) — but no SC script imports it. `pauses.sc`, SC detection cooldowns, the SOP caps, and the session brief's approval gate are all prose. There is no SC ledger or call budget of any kind.
2. **A reciprocator was churned and nobody noticed for 7 weeks.** `la-ramazotti` (display name "Italo Fundamentalo", followed back 2026-07-02, 281 followers) was unfollowed between 07-02 and 07-11 with **no unfollow logged anywhere**. A second, 0-follower account with the *identical display name* was the legitimate sweep target and is *still followed*. The 07-11 weekly report listed the drift neutrally in a 32-name list; drift detection never cross-checks `followed_back`, so the churn was invisible. Same mechanism as IG's @infoluences/@xoobinwood: name-keyed operations + silence read as ground truth.

## Findings (ranked)

### P0

**F1 — SC enforcement gap: pause, cooldown, budgets, approval gate all read by no SC code** *(class 8)*
- `autonomy_state.json` `pauses.sc` is enforced only *inside* `close_loops.py` (observe-and-report mode, `close_loops.py:759-767`). No engagement entrypoint checks it: `sc_engagement.py`, `sc_weekly_health.py`, `sc_log_manual.py`, `check_sc_follows.py`, `enrich_soundcloud.py` — zero imports of `ig_ops_guards` (grep verified). The module's `standard_gates("sc")` would work today; nothing calls it.
- `detection_events.json` holds a real SC event (2026-07-21 DataDome, 2 incidents). No SC script reads the file; a fresh SC CAPTCHA would impose a cooldown that nothing enforces (IG-L1 twin, fixed on IG 08-31, open on SC).
- `close_loops.py --resume --platform sc` has no authorization check (`close_loops.py:736-752`) — IG-L1's `--resume` half, still open on both platforms.
- **No SC daily ledger / call budget exists at all.** The engine's daily budgets (`sc_engagement.py:2313-2315`) bind only engine runs; live sessions are Chrome clicks logged after the fact via `--log-action`, which enforces nothing (IG-L2 twin). `sc_weekly_health.py`'s `API_BUDGET_HARD_CAP=30` covers only its 3-5 direct calls; its own docstring admits the ~65 discovery calls per run bypass the counter (`sc_weekly_health.py:27-31`) — and discovery runs **even under `--dry-run`** (`sc_weekly_health.py:481-488`).
- The session brief's approval gate is un-enforced prose: `sc_next_session_brief.md` still reads `STATUS: DRAFT - AWAITING AMIR APPROVAL` while the 2026-08-28 session it describes demonstrably ran (5 of its targets carry `followed_at: 2026-08-28` in the tracker; `sc_session_report_20260828.md` exists). Approval may have happened in chat, but the artifact that encodes the gate records a violation and nothing checks it.

**F2 — Reciprocity fails OPEN in the engine sweep; live churn confirmed** *(class 1)*
- Code: `update_follow_back_status()` returns `0` both for "no new follow-backs" and "follower fetch FAILED" (`sc_engagement.py:2147-2150`), and `run_engagement()` proceeds straight into the unfollow sweep either way (`sc_engagement.py:2349-2353`). A dead token or one failed page means the sweep fires on stale `followed_back` flags — the sweep has **no per-account live "follows you" re-check** (unlike IG's, which the 08-25 review validated as good). `fetch_all_follower_ids` itself fails closed (`sc_engagement.py:2114-2138`, good), but its caller ignores the distinction.
- Exposure: **128 entries are sweep-eligible right now** (past window, `followed_back: false`); an accidental `python3 sc_engagement.py` live run would fire 15 of them (`UNFOLLOWS_PER_SESSION`) on whatever the flags said last — against the standing rule that Amir does unfollows manually. The automated sweep still runs by default on every full/unfollow-only engine invocation (`sc_engagement.py:2346`).
- Live churn found: tracker has **two entries named "Italo Fundamentalo"** — `5169413` (0 followers, followed 05-29, non-reciprocator, the batch-1 target in `sc_unfollow_batches.md`, still followed) and `175272490` / `la-ramazotti` (281 followers, followed 07-02, `followed_back: true` same day, **`no_longer_following: true`**). No `sc_unfollow` for either uid exists in `engagement_log.json`; the disappearance surfaced only as one line in the 07-11 weekly drift list. A reciprocator was unfollowed, most plausibly by display-name confusion, and no alarm exists that would ever have caught it: `update_tracker`'s drift check (`sc_weekly_health.py:236-238`) sets the flag without checking `followed_back`, and `generate_report` prints drift with no reciprocator cross-check.
- Also class-1: the 6 tracker entries with null `user_id` (all Apr/May, sources fan/chrome_mcp) are invisible to BOTH the follow-back check and drift check forever — `if uid and ...` skips them (`sc_weekly_health.py:227-238`); slug resolution has resolved 0 of them across months of health runs (every weekly report since June: "Missing user_id: 6 (resolved this run: 0)"). Today all 6 are shielded by `no_longer_engage`/dead flags, so no live sweep risk — but the pattern is the IG "26/28 null user_ids" twin at smaller scale, and the health report stamps the count without ever escalating it.

**F3 — sc_log_manual.py: silent corrupt-file resets + non-atomic writes on both shared state files** *(class 7)*
The exact clobber class `json_io.py` was built to kill (audit P2-10), alive in the one script that touches both shared files:
- `_load_eng_log` returns `{"log": {}}` on a corrupt 925KB engagement log (`sc_log_manual.py:153-163`); `_save_eng_log` then plain-overwrites it (`sc_log_manual.py:166-168`). One corrupt byte + one manual log = every cooldown and all history gone.
- `_load_tracker` returns an empty tracker on corruption (`sc_log_manual.py:171-187`); `_save_tracker` plain-overwrites (`sc_log_manual.py:190-192`). Same for the 238KB tracker: never-refollow protection included.
- Neither write is tmp+rename; a crash mid-write corrupts the file even without pre-existing corruption.
Other non-atomic writers of shared state: `sc_weekly_health.py:477` (tracker), `:295-305` (candidates), `:312` (audit); `enrich_soundcloud.py:233-234` (the 2.3MB contacts DB). All bypass `json_io.atomic_write_json`, which the engine itself uses correctly.

### High

**F4 — sc_weekly_health "backup" is written AFTER mutation; stamp-vs-measurement leaks** *(class 2)*
- `update_tracker()` mutates the tracker in memory first, *then* writes `sc_follow_tracker.bak.<ts>_health.json` (`sc_weekly_health.py:213-248`) — the backup preserves the run's own damage, not the pre-run state. Every one of the ~40 `_health` baks in `backups/sweep-20260831/` is post-mutation.
- The weekly report line "Pending (within 14-day window): 157" is a false stamp: the counter is simply "not followed_back and not drifted" with **no window check** (`sc_weekly_health.py:334-337`) — 128 of those 157 are *past* the window.
- `close_loops.close_sc` runs its detection scan on the session report file, and silently scans an empty string when the report is missing (`close_loops.py:690-695`) — a day with logged actions but no report can score 10/10 with zero detection evidence. The green score stamps a measurement that never ran (IG "staleness gate green while data empty" twin).
- `sc_following_audit.json` has **two writers with two schemas**: `sc_weekly_health.save_audit` (counts, the current content) and `check_sc_follows.main` (candidate lists, `check_sc_follows.py:227-234`). Whichever runs last silently redefines the file.

**F5 — Counter drift + accounting incoherence in the tracker** *(class 3)*
Memory said the stats block was stale; quantified:
- `stats.total_unfollowed` = **55** vs `len(permanently_unfollowed)` = **54** (the IG 261-vs-283 twin, smaller).
- `stats.total_followed` = 645 = `len(follows)` — `recompute_tracker_stats` (`sc_engagement.py:681`) overwrites the *cumulative* counter with the *current list length* on every save, while `add_follow_record`/`sc_log_manual` still increment it as cumulative (`sc_engagement.py:717`, `sc_log_manual.py:319`). The historical "422 total followed" meaning is unrecoverable from the tracker; hard-deleted entries (~55) vanished from the denominator, quietly inflating every follow-back rate ever computed from it.
- **41 entries sit in `follows` AND in `permanently_unfollowed`** — two unfollow representations applied simultaneously (the soft `no_longer_following` flag plus the never-refollow list, which per `remove_follow_record` should only accompany a hard delete). Two of the 41 are **reciprocators** (Gerry Mawhinney, KrissaTúttubyssa & DoriExploratori: `followed_back: true`) now permanently banned from ever being re-followed by discovery (`sc_engagement.py:1600`). Reported as data per the no-refollow rule; the accounting inconsistency is the finding.
- 8 entries carry `followers` as a *string* ("93", "23556", …) — they silently fail every numeric band/seed filter that doesn't coerce (e.g. `_reciprocator_seeds` treats them as 0, `sc_engagement.py:1532-1535`).
- `sc_unfollow_batches.md` (08-23) is a stale execution artifact: 89 rows vs 128 now eligible, and it operates by display name/permalink — the exact keying that churned la-ramazotti.

**F6 — Engagement-log key mismatch, quantified** *(class 4)*
- **113 tracker contacts have logged actions under a key that is NOT the canonical name-derived key** (slug keys like `jericho-one-2`, `mascarp0ne`, `djhematoma` vs canon `jericho_one`, `mascarpone`, `hematoma`). The engine's cooldown lookups key by canonical `_contact_key(name)` (`sc_engagement.py:905-908`, used at `:1400`), so those contacts' like history is invisible to `was_recently_liked` — they can be re-served before the 30-day cooldown. IG's 77-entry twin, here 113.
- **519 of 785 `sc_like` entries carry no `user_id`** (and 50/646 follows) — history is not reassemblable when a display name changes, which is precisely how the Italo Fundamentalo collision became untraceable.
- The engine's own unfollow logging still has the fixed-elsewhere prefix bug: it keys `discovery_<uid>` only when `source == "discovery"`, but the engine emits `discovery_v2` (`sc_engagement.py:2233` vs the fix at `:1819`) — engine unfollows of discovery_v2 entries get name-keyed.
- Manual actions are logged as `sc_like_manual` / `sc_follow_manual` / `sc_unfollow_manual` (`sc_log_manual.py`), which **no budget or cap counts**: `get_today_action_counts` counts only the four exact engine action names (`sc_engagement.py:766-776`), and `close_loops.SC_CAPS` checks exact keys (`close_loops.py:534-539`). A manual like also never arms the `was_recently_liked` cooldown (action name mismatch, `sc_engagement.py:797`).
- `sc_log_manual.log_manual_follow` hardcodes a **7-day** unfollow window (`sc_log_manual.py:272`) vs the config's 14 (`sc_engagement_config.py:97`) — manual follows get half the reciprocity window. And a manual follow whose resolve fails is written to the log but **not to the tracker** (`sc_log_manual.py:307-318`) — followed on SC, tracked nowhere, never checked for follow-back.

**F7 — The 600-1000 experiment was never evaluated; the promised instrumentation was never built** *(class 6)*
- Config demanded: "DECISION RULE: measure follow-back BY BAND each health pass… evaluate ~2026-07-17" (`sc_engagement_config.py:264-272`). `sc_weekly_health.generate_report` has **no band section** (only by-source and by-month, `:391-403`); zero weekly reports mention bands (grep verified). 07-17 passed silently — the IG "3% famous anchors and nobody knew" twin: a pre-committed measurement that nothing measures.
- Computed now from the tracker (follows since 07-03, mature ≥14d): **100-300: 8/53 (15%) · 300-600: 3/55 (5%) · 600-1000: 13/91 (14%)**. By the pre-committed rule (≥10% keep, <5% revert) the 600-1000 tier **passes** — and the *middle* band 300-600 is now the weakest, which the 4/4/4 session split keeps feeding anyway (per sc-discovery-supply-notes this is a known seed-exhaustion symptom, not a rewrite prompt — but it's unmeasured in any report).
- Per-source yield IS measured weekly (good; discovery_v2 13%, chrome_mcp 22%, fan 26%, release_boost 4%). Per-*seed* yield is unmeasurable: discovery candidates record `source: "discovery_v2"` but not which seed surfaced them (`sc_engagement.py:1720-1736`) — 78 seeds crawl, none has ever been individually scored.
- `discovery_candidates_20260828.json` still contains **zc_ned** (the reposts-only curator the same-day `_has_own_uploads` fix was written to exclude — the candidates were generated at 12:41, the fix landed 14:45). Mitigated by a manual DO-NOT-FOLLOW note in the brief; the file itself is the loaded gun. 5 of its 50 candidates are also already followed (08-28 session), so the "50 eligible / 38 bench" arithmetic in any future brief drawn from it is stale.

### Medium

**F8 — Three conflicting cap laws** *(class 8, IG-L3 twin)*
`sc_engagement_config.MODES["moderate"]` says 30 likes/15 follows per **day** (`sc_engagement_config.py:34-37`); SOP §4.1 and `close_loops.SC_CAPS` say 24 likes/12 follows per **session**, repost 1/session (`docs/sc-engagement-sop.md:103-107`, `close_loops.py:57`). An engine full run at its own default mode would immediately score two "cap violations" in close_loops and pause SC autonomy for obeying its config. Also SOP says unfollows are "Sunday only" — encoded nowhere in code. Pick one law (the IG resolution was: config is THE LAW, prose follows).

**F9 — Corrupt-file fail-opens in the engine's periphery** *(class 7)*
`load_eng_log`/`load_follow_tracker`/`_load_si_contacts` correctly hard-stop (json_io, good). But: `_load_promotion_log` silently returns empty on corruption (`sc_engagement.py:1087-1088`) — active campaigns silently vanish from pre-warming; `_load_never_engage_keys` logs a warning and **continues with the protection degraded** when the blocked/personal lists are unreadable (`sc_engagement.py:1479-1490`) — the never-engage exclusion fails open (IG-L4 flavor: a protection list that degrades instead of stopping); `_load_token_file` returns `{}` (`sc_engagement.py:306-307`, minor).

**F10 — check_sc_follows.py is partially dead** *(classes 2+4)*
Its by-ID matching reads `soundcloud_id` — a field present on **0 of 1,206** contacts (`check_sc_follows.py:100`; the real field is `soundcloud_user_id`), so ID matching never fires and everything falls to slug/name. The docstring's "Report C" (tracker entries no longer in your followings) was never implemented — `tracked_ids` is computed (`:138`) and never used. The script stamps an audit file while performing less than it advertises.

### Low / estate ages *(classes 5+9)*

| file | last write | note |
|---|---|---|
| `session_reports.json` | 2026-05-12 (111d) | frozen; the IG side retired its gate off this file 08-31; **no SC reader** — archivable |
| `engagement_log.json` embedded `queue_soundcloud` / `discovery_seeds` / `queue_date` | 2026-07-11 (52d) | frozen embedded state, read by no code (grep) — dead weight inside a live file |
| `nina_follow_log.json` / `nina_hub_stats.json` | 06-01 / 06-11 (~3 months) | frozen side pipeline (IG paid-audience twin, but no active consumer found) |
| `promotion_log.json` | 2026-08-15 | **57 `not_sent` targets on the-deceiver-single still count as an ACTIVE campaign** (`PROMO_TRIGGER_STATUSES`, `sc_engagement_config.py:414`) — any engine run would bump them with priority +1000 (`sc_engagement.py:1330`) for a release that shipped in June |
| `discovery_candidates_*.json` | only 20260828 remains | older snapshots swept to backups 08-31; `_resolve_profile_url`'s local lookup (`sc_engagement.py:971`) now can't resolve URLs for any pre-08-28 follow |
| `sc_following_audit.json` | 2026-08-28, 106B | healthy age, but two-schema file (F4) |
| tracker/eng-log backups | archived to `backups/sweep-20260831/` (56 tracker baks) + state committed in git | **retention OK** — the IG "no rollback point" finding does not reproduce; only caveat is F4 (baks are post-mutation) |
| dead-handle flags | 8 `marked_dead_at` entries, none re-checked since 06-01 | checker-leaves-404s-forever twin, dormant |

## Validated as good

`json_io.py` and the engine's own state I/O (atomic writes, hard-stop on corruption — `sc_engagement.py:651, 691, 749`); `fetch_all_follower_ids` pagination fails closed (`:2114-2138`); the sweep honors `no_longer_engage`/`no_longer_following`/`followed_back` flags and caps at 15 with a consecutive-failure breaker (`:2184-2249`); discovery excludes own account, known ids, permanently_unfollowed, never-engage, default slugs, reposts-only curators (`:1583-1700`); `_resolve_log_key` and `_resolve_profile_url` fix the 07-10/08-08 fabrication classes going forward; close_loops' negation-aware detection scan fixed the "No CAPTCHA" false-positive class (`close_loops.py:173-199`); per-source yield is genuinely measured weekly; SC state is committed to git with the 08-31 backup sweep.

## Decisions for Amir

1. **Wire the existing gates into SC (F1).** `standard_gates("sc")` already exists — one import + call at the top of `sc_engagement.py` main, `sc_weekly_health.py` main, and `sc_log_manual.py` main. Same for an SC ledger/budget decision: extend the IG per-endpoint law or explicitly rule SC exempt. (This is the T-003 batch, SC edition.)
2. **Fail the sweep closed (F2):** should `run_engagement` abort the unfollow sweep when the follow-back refresh fails (`update_follow_back_status` returning a failure signal instead of 0)? And given you do unfollows manually — should the engine's automated sweep be disabled outright (default run currently includes it, 128 eligible)?
3. **The la-ramazotti churn (F2):** confirm the reconstruction (name-collision manual unfollow, ~07-02..07-11). Per the standing rule I make no re-follow suggestion; decide whether drift reports should hard-flag any drifted entry with `followed_back: true` so this class becomes visible.
4. **Retire or fix `sc_log_manual.py` (F3, F6):** it's the worst offender (silent resets, plain writes, 7-day window, tracker-skipping follows). Options: port it to `json_io` + config constants, or retire it in favor of `--log-action` which already does most of this safely.
5. **Pick one cap law (F8):** config vs SOP §4.1 vs close_loops. IG precedent: config is THE LAW, prose mirrors it.
6. **Rule on the 600-1000 experiment (F7)** with the numbers now computed (600-1000 mature: 13/91 = 14% → keep per your own pre-committed rule; 300-600 at 5% is the new question). Decide whether the by-band table gets added to `sc_weekly_health.generate_report` so the next experiment can't go unmeasured.
7. **Tracker accounting definition (F5):** same decision as IG #5 — define `total_followed`/`total_unfollowed` (cumulative vs derived), reconcile the 55-vs-54, and rule on the 41 double-represented entries (esp. the 2 reciprocators in the never-refollow list).
8. **Housekeeping batch (F4, F9, F10, estate):** pre-mutation backups in the health run, atomic writes in the three stragglers, one schema for `sc_following_audit.json`, close the-deceiver campaign statuses, archive `session_reports.json` + the frozen embedded queues, fix or delete `check_sc_follows.py`. Small, mechanical, one session.

---
*Read-only audit by Claude (Fable), 2026-09-01 session. No code, state, API, or browser touched. Twin reference: [ig-automation-review-2026-08-25.md](ig-automation-review-2026-08-25.md), [ig-system-findings-2026-08-30.md](ig-system-findings-2026-08-30.md), IG fix commits 2026-08-26..31.*
