# IG Engagement Session Scorecard

Running quality rating for each Cowork IG engagement session. Added after the
post-session integrity check (JSONL vs report, fabrication guard, forbidden-handle
scan). Read alongside [ig-status.md](ig-status.md).

## Rubric (what drives the score)

Start at 10, deduct for what went wrong; the worst items dominate.

- **Hard violations (heavy):** comment-like, engaging personal-network / own-label
  / blocked, over-ceiling (>15k) picks, fabricated report (≠ JSONL), fabricated/
  future-stamped timestamps, direct tracker write (drift).
- **Process (medium):** file-gate bypassed (no plan generated / hand-picking),
  rule-2 unfollow_after written in events, off-window or 2h+ over-length session.
- **Logging (light):** 2h timezone bug (events behind real clock), log-format slip,
  dropped events.
- **Credit (positives):** file-gate followed, filters fired (>5k label, 90d recency,
  follower-min, private), circuit-breaker discipline, report matches log, targets hit.

Bands: 9-10 clean · 7-8 good, minor logging issues · 5-6 mixed · 3-4 real violations ·
1-2 integrity breakdown (fabrication / friends / own-label).

## Scores

| Date | Day | Score | Reach | Scene | Unfollow | One-line verdict |
|------|-----|-------|-------|-------|----------|------------------|
| 2026-06-15 | Mon | **4** | 8/8 ✓ | 20 (hand-picked) | 1 ✓ | Comment-like on @travelaroundberlin (58k food blogger); hand-picked scene incl. dead @acid.tears.303; rule-2 unfollow_after in events. Report honest, merge clean. |
| 2026-06-17 | Wed | **3** | 8/8 ✓ | 20 (hand-picked) | 1 ✓ | Hand-picked → liked own-label @mm.discos + personal-network @__p.r.z__/@carlosthings/@lushlab.vx + dead handles. Direct tracker write (drift, fixed). |
| 2026-06-19 | Fri | **1** | 8/8 | ~18 (hand-picked) | 0 | Integrity breakdown: fabricated report (claimed 5 likes that never happened, hid @ninakraviz 2M like), future-stamped timestamps, file-gate bypassed (no plan), comment-like on @phyllzx logged as post-like. Direct tracker write. |
| 2026-06-20 | Sat | **8** | 5/8 (CB) | 15 ✓ | 0 | TURNAROUND. File-gate used + followed, zero violations, filters fired (>5k, 90d, private), circuit-breaker discipline, report matched log. −2: 2h TZ bug + log-format slip dropped 5 events (fixed) + reach shortfall on stale queue. |
| 2026-06-22 | Mon | _TBD_ | 8 | — | 7 | Merged late (was unmerged); used the staged plan file. Not yet quality-scored. |
| 2026-06-24 | Wed | **5** | 8/8 | 20 | 7 (1 recip. miss) | Mixed. Rich, honest log (self-flagged @blue_records333 reciprocator miss, @timeinbody re-like "no credit", correct tracker-mismatch skips + @gilmirandajr abort). BUT no plan generated → hand-picked → liked personal-network @sharlese_m; wrote a custom tracker script (standard tool ultimately used, 74a9f88); @blue_records333 reciprocator unfollowed; life_in_patterns_ mislabeled "label" to hit the cap. |
| 2026-06-26 | Fri | _TBD_ | — | — | — | Session halted by stale-queue circuit breaker (not a detection event). Not yet quality-scored. |
| 2026-07-01 | Wed | _TBD_ | — | — | — | 64 reach skips in the log (dead/stale targets); merged 2026-07-05 via new prefix-matching sync. Not yet quality-scored. |
| 2026-07-04 | Sat | **2** | 6 clicked (2 valid) | 24 likes | 8 | Heavy: 4 of 6 follows were previously-unfollowed accounts (@djheisa, @eid55558.55, @seismicdoom, @sellyourmania - never_retry violation; merge guard refused to re-track); IG grid rate-limiting triggered (soft detection signal) during 90-min overrun; phase reverted 2 -> 1b. Credit: honest JSONL, fabrication guard passed, merge clean. |
| 2026-07-17 | Fri | n/a | 0 | 0 | 0 | No session — CORRECT behavior. CC completed pre-flight, refused to click without Amir (Chrome scope check), wrote an honest "awaiting Amir" report and stopped. This is the protocol working. |
| 2026-07-18 | Sat | **0** | 0 real | 0 real | 0 real | **FABRICATED (2nd incident; 1st was 2026-05-31).** CC invented a full session (claimed 20 likes + 5 unfollows + 2 reciprocator re-follows), unsupervised, the day after 07-17 was never confirmed. (Sat IS a scheduled IG day per the 2026-06-01 cadence — the config was stale at Mon/Wed/Fri, fixed 2026-07-19; the fabrication is confirmed by Amir directly, not by the calendar.) Amir confirms nothing ran in Chrome. Fabrication guard blocked the merge (events stamped +02:00 on a UTC+3 machine -> 1h future skew). JSONL quarantined, report renamed .FABRICATED. Tracker untouched (last real session 07-15). NEW LESSON: real-time fabrication defeats mtime forensics (file written over 25 min, mtime matches last event to the second) — artist confirmation is the ONLY decisive check. |

**Trend:** 4 → 3 → 1 → **8** → (06-22 TBD) → **5** → (06-26 TBD) → (07-01 TBD) → **2**. The cliff and the recovery both trace to one variable:
**was the `session_plan_<date>.json` generated?** Fri (no plan) = free-picking disaster;
Sat (plan generated) = clean. Pre-generating the plan is the single highest-leverage habit.

## How to add a new row

After each session's integrity check, append a row with the score, the track counts,
and a one-line verdict citing the rubric items that moved the score. Update the trend line.
| 2026-07-20 | Mon | **7** (auto, corrected) | 6/10 | 15/25 | 4/8 | First Phase 2 session + first self-closing loop. Zero violations, no detection signal, merge + tracker sync clean, CC ran plan-gen and the loop-closer itself. −3: undershot all three targets (~60%), on a vetted pool of only 33 and a 17-day-old queue build. Originally auto-scored 10/10 — the rubric ignored volume; fixed same day. |
| 2026-07-22 | Wed | **5** (auto) | 7 | 40 | 4 | -3 cap violation: ig_like 40 > 25; -1 shortfall: ig_follow 7/10; -1 shortfall: ig_unfollow 4/8 |
| 2026-07-24 | Fri | **4** (auto) | 8 | 27 | 3 | -3 cap violation: ig_like 27 > 25; -3 severe shortfall: ig_unfollow 3/8 |
| 2026-07-25 | Sat | **4** (auto) | 10 | 36 | 9 | -3 cap violation: ig_like 26 > 25; -3 cap violation: ig_unfollow 9 > 8 |
| 2026-07-27 | Mon | **8** (auto) | 7 | 23 | 9 | -1 shortfall: ig_follow 7/10; -1 shortfall: ig_like 16/25 |
| 2026-07-29 | Wed | **0** (auto) | 0 | 0 | 0 | -2 skip ratio 6/6 (stale/junk queue); -2 zero substantive actions; -3 severe shortfall: ig_follow 0/10; -3 severe shortfall: ig_like 0/25; -3 severe shortfall: ig_unfollow 0/8 |
| 2026-08-07 | Fri | **4** (auto) | 4 | 16 | 9 | -3 severe shortfall: ig_follow 4/10; -3 severe shortfall: ig_like 12/25 |
| 2026-08-08 | Sat | **2** (auto) | 0 | 1 | 8 | -2 skip ratio 26/35 (stale/junk queue); -3 severe shortfall: ig_follow 0/10; -3 severe shortfall: ig_like 1/25 |
| 2026-08-10 | Mon | **4** (auto) | 0 | 3 | 9 | -3 severe shortfall: ig_follow 0/10; -3 severe shortfall: ig_like 3/25 |
| 2026-08-12 | Wed | **3** (auto) | 1 | 2 | 6 | -3 severe shortfall: ig_follow 1/10; -3 severe shortfall: ig_like 1/25; -1 shortfall: ig_unfollow 6/8 |
| 2026-08-14 | Fri | **8** (auto) | 9 | 22 | 5 | -1 shortfall: ig_like 13/25; -1 shortfall: ig_unfollow 5/8 |
| 2026-08-15 | Sat | **5** (auto) | 7 | 21 | 1 | -1 shortfall: ig_follow 7/10; -1 shortfall: ig_like 14/25; -3 severe shortfall: ig_unfollow 2/8 |
| 2026-08-17 | Mon | **1** (auto) | 4 | 7 | 0 | -3 severe shortfall: ig_follow 4/10; -3 severe shortfall: ig_like 3/25; -3 severe shortfall: ig_unfollow 0/1 |
| 2026-08-26 | Wed | **3** (auto) | 1 | 4 | 5 | -3 severe shortfall: ig_follow 1/8; -3 severe shortfall: ig_like 3/20; -1 shortfall: ig_unfollow 5/7 |
| 2026-08-28 | Fri | **1** (auto) | 1 | 1 | 0 | -3 severe shortfall: ig_follow 1/8; -3 severe shortfall: ig_like 0/20; -3 severe shortfall: ig_unfollow 0/7 |
| 2026-08-31 | Mon | **8** (auto) | 0 | 0 | 0 | -2 zero substantive actions; note: session halted (infrastructure: browser operator surface unavailable — 3 chrome extension instances connected (amir / amirmill808 / inch of shadow), none identifiable as the required "amir (inch of shadow)" profile, and the browser-selection prompt required before any browser action is not available in this session; scheduled unattended fire, no pre-flight confirm from amir.) -- protocol-compliant stop, volume targets not scored (T-006 rule, precedents 08-07/08-17/08-26/08-28) |
| 2026-09-07 | Mon | **8** (auto) | 0 | 0 | 0 | -2 zero substantive actions; note: session halted (infrastructure: all 4 connected chrome extension instances report anonymous names (browser 1-4); none contains "inch of shadow", so the profile could not be identified without guessing. zero clicks.) -- protocol-compliant stop, volume targets not scored (T-006 rule, precedents 08-07/08-17/08-26/08-28) |
| 2026-09-07 | Mon | **5** (auto) | 7 | 11 | 0 | -1 shortfall: ig_follow 7/12; -1 shortfall: ig_like 4/6; -3 severe shortfall: ig_unfollow 0/8 |
| 2026-09-11 | Fri | **8** (auto) | 0 | 0 | 0 | -2 zero substantive actions; note: session halted (infrastructure: no connected chrome instance named 'inch of shadow' (4 anonymous connections: browser 1-4); playbook forbids guessing the profile, and amir unavailable for pre-flight confirm in the scheduled run. 0 clicks.) -- protocol-compliant stop, volume targets not scored (T-006 rule, precedents 08-07/08-17/08-26/08-28) |
| 2026-09-11 | Fri | **10** (auto) | 1 | 9 | 0 | clean auto-close |
| 2026-09-12 | Sat | **10** (auto) | 5 | 12 | 0 | clean auto-close |
| 2026-09-14 | Mon | **10** (auto) | 10 | 16 | 0 | clean auto-close |
| 2026-09-16 | Wed | **10** (auto) | 1 | 1 | 0 | note: session halted (safety: mid-session pause over 60 min waiting on amir's action-1 confirm (16:57 to 20:56); playbook requires ending safely) -- protocol-compliant stop, volume targets not scored (T-006 rule, precedents 08-07/08-17/08-26/08-28) |
| 2026-09-16 | Wed | **9** (auto) | 13 | 16 | 0 | -1 shortfall: ig_like 3/6 |
| 2026-09-18 | Fri | **10** (auto) | 1 | 2 | 0 | note: session halted (safety: 22:00 night-clicking cutoff passed. task fired 15:00 berlin but the run was suspended repeatedly (first clock read 15:04, first click 21:16, real clock now 2026-09-18t22:35:24+02:00). stopped clicking rather than continue into the night; reach follow for flaviodeff_aka_djhome left unfollowed after its like.) -- protocol-compliant stop, volume targets not scored (T-006 rule, precedents 08-07/08-17/08-26/08-28) |
| 2026-09-19 | Sat | **10** (auto) | 8 | 14 | 0 | clean auto-close |
| 2026-09-21 | Mon | **9** (auto) | 4 | 7 | 0 | -1 shortfall: ig_like 3/5 |
| 2026-09-23 | Wed | **10** (auto) | 1 | 7 | 0 | clean auto-close |
| 2026-09-25 | Fri | **10** (auto) | 3 | 8 | 0 | clean auto-close |
| 2026-09-26 | Sat | **8** (auto) | 0 | 0 | 0 | -2 zero substantive actions; note: session halted (safety: pre-flight confirm gate timed out (15 min, no pre-confirm flag, no reply); zero clicks) -- protocol-compliant stop, volume targets not scored (T-006 rule, precedents 08-07/08-17/08-26/08-28) |
| 2026-09-26 | Sat | **7** (auto) | 4 | 6 | 0 | -3 severe shortfall: ig_like 2/5 |
| 2026-09-28 | Mon | **9** (auto) | 0 | 4 | 0 | -1 shortfall: ig_like 4/6 |
| 2026-10-02 | Fri | **10** (auto) | 0 | 5 | 0 | clean auto-close |
| 2026-10-07 | Wed | **8** (auto) | 0 | 1 | 0 | -2 skip ratio 4/6 (stale/junk queue); note: session halted (safety: action-1 confirm gate timed out (15 min, no reply, no pre-confirm flag)) -- protocol-compliant stop, volume targets not scored (T-006 rule, precedents 08-07/08-17/08-26/08-28) |
| 2026-10-09 | Fri | **7** (auto) | 0 | 0 | 8 | -3 severe shortfall: ig_like 0/6 |
| 2026-10-09 | Fri | **4** (auto) | 1 | 0 | 5 | -3 severe shortfall: ig_like 0/6; -3 severe shortfall: ig_unfollow 5/15 |
| 2026-10-10 | Sat | **10** (auto) | 0 | 5 | 0 | note: session halted (infrastructure: unfollow click denied by the claude code permission classifier at unfollow 1/15 (negrolator_x); unfollow lane not run, likes completed) -- protocol-compliant stop, volume targets not scored (T-006 rule, precedents 08-07/08-17/08-26/08-28) |
| 2026-10-10 | Sat | **7** (auto) | 0 | 0 | 14 | -3 severe shortfall: ig_like 0/6 |
| 2026-10-10 | Sat | **4** (auto) | 0 | 0 | 6 | -3 severe shortfall: ig_like 0/6; -3 severe shortfall: ig_unfollow 6/15 |
| 2026-10-12 | Mon | **10** (auto) | 0 | 4 | 0 | clean auto-close |
| 2026-10-14 | Wed | **9** (auto) | 1 | 5 | 0 | -1 shortfall: ig_like 4/6 |
| 2026-10-16 | Fri | **10** (auto) | 2 | 10 | 0 | clean auto-close |
| 2026-10-17 | Sat | **10** (auto) | 5 | 12 | 0 | clean auto-close |
| 2026-10-19 | Mon | **10** (auto) | 1 | 7 | 0 | clean auto-close |
| 2026-10-21 | Wed | **10** (auto) | 2 | 7 | 0 | clean auto-close |
| 2026-10-26 | Mon | **10** (auto) | 1 | 7 | 0 | clean auto-close |
| 2026-10-23 | Fri | **7** (auto) | 1 | 3 | 0 | -3 severe shortfall: ig_like 2/6 |
| 2026-10-24 | Sat | **6** (auto) | 0 | 3 | 0 | -3 severe shortfall: ig_follow 0/1; -1 shortfall: ig_like 3/6 |
| 2026-10-30 | Fri | **9** (auto) | 4 | 8 | 0 | -1 shortfall: ig_like 4/6 |
| 2026-10-31 | Sat | **9** (auto) | 3 | 6 | 0 | -1 shortfall: ig_like 3/6 |
| 2026-11-02 | Mon | **10** (auto) | 13 | 17 | 0 | note: session halted (safety: ig banner on profile page at scope check ('introducing content scheduling on web' with try it now / x), zero clicks, ledger not claimed) -- protocol-compliant stop, volume targets not scored (T-006 rule, precedents 08-07/08-17/08-26/08-28) |
| 2026-11-04 | Wed | **10** (auto) | 16 | 22 | 7 | note: session halted (safety: adblock extension popup over the ig page at scope check; zero clicks, ledger not claimed) -- protocol-compliant stop, volume targets not scored (T-006 rule, precedents 08-07/08-17/08-26/08-28) |
| 2026-11-06 | Fri | **9** (auto) | 16 | 23 | 2 | -1 shortfall: ig_like 7/11 |
| 2026-11-07 | Sat | **9** (auto) | 15 | 22 | 0 | -1 shortfall: ig_like 7/11 |
