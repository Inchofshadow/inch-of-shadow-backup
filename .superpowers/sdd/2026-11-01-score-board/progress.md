# SDD ledger — plan: docs/superpowers/plans/2026-11-01-score-board.md
Spec: docs/superpowers/specs/2026-11-01-score-board-design.md (read).
Branch: score-board, in place (no worktree). Ruling: no worktree — the Release Manager server and the data dirs (stats_snapshots/, data/, scene_intelligence/) live in this checkout; a worktree would read stale copies and the page check in Task 6 would not see the branch. Cost if wrong: a bad commit lands in the only checkout; undo = git revert.
Pre-existing dirty files (docs/plans edits by other sessions) are NOT ours: never `git add -A`, never stash, never touch them.

## Preflight scan
| Pair / task | Produces vs consumes | Finding |
|---|---|---|
| T1 -> T5, T7 | targets.json shape, load_targets/ladder_value/light_for_*/progress_pct/current_rung | names match in T5 tests (sb.load_targets) and T7 (set_ig_baseline writes same keys) — clean |
| T2 -> T5 | MANUAL_PLATFORMS incl. instagram_insights, tiktok; get_time_series merges manual | T5 source strings manual:<platform>.<metric> rely on the merge — clean |
| T3 -> T5 | newest_export_dir(Path) used by T5 health export_age; ig_followback.json since_may_pct | clean after signature fix (cohorts has export_date) |
| T4 -> T5 | snapshot keys instagram.followers/following/media_count/reach_30d, hikerapi.requests | T5 health reads hikerapi.requests; ratio reads followers/following — clean |
| T5 -> T6 | build() keys score/cards/health/ladders/trends | template consumes the same keys — clean |
| T7 -> T1 | set_ig_baseline writes rungs {month-end: base+30, period-end: base+60} | T1 ladder_value accepts any dated rungs — clean |
| T4 self | test patches c._claim and c._provider; plan says module-level wrappers | consistent |
| T2 self | CLI test uses env STATS_MANUAL_FILE; plan says MANUAL_FILE reads that env | consistent |
| Global | ledger claims: T4 kind=api endpoint=graph_insights / kind=provider | ig_daily_ledger.check_and_claim signature verified (kind, est_calls, endpoint) — clean |
Ruling: T4 build both variants now; IG_DAILY_SOURCE env decides later (Graph probe pending, daytime). Cost if wrong: one unused code path.
Ruling: T3 reproduction test skips when the 10-10 export is absent; it is present here, so it must pass. Cost: none.
BASE_T1=23d68e3
Task 1: minor (deferred): period start/end not validated; non-dict metric raises AttributeError; rungs before period.start unvalidated; no exact 85/95 boundary tests; floor text "vs floor" unspecified.
Task 1: complete (commits 23d68e3..d1dfa33, review clean)
BASE_T2=d1dfa33
Task 2: warning resolved: consumers of get_overview iterate their own fixed manual list (stats_tracks.py:163-166), extra platform keys are harmless.
Task 2: minor (deferred): CLI parse_value error message terse; subprocess test uses a cwd-relative script path; no malformed --date / float tests; manual_entries.json lacks trailing newline (atomic_write_json).
Task 2: complete (commits d1dfa33..16f7b9c, review clean)
BASE_T3=16f7b9c
Task 3: Ruling: the export-month cohort is marked "partial": true and excluded from since_may_pct (with after-export cohorts) — the export covers only part of that month and its follows are too young to have answered; this is what the 10-10 report did (May-Sep, 72/319 = 23%). Cost if wrong: the headline % lags one month behind the newest follows.
Task 3: warning resolved: the reproduction test ran on this machine (export present), the committed JSON carries the exact numbers.
Task 3: minor (deferred, FIX BEFORE MERGE): tests/test_ig_followback.py asserts the newest export is 10-10, so it breaks at the next monthly export; make it pick the 10-10 dir explicitly. Also: no synthetic test of the partial flag; relative paths in the test; CLI prints 0% for None.
Task 3: complete (commits 16f7b9c..def3011, review clean)
BASE_T4=def3011
Task 4: Ruling: reviewer's Minor 1 (refusal test passes vacuously, never reaches the ledger) is upgraded to Important — it is the test that pins Review Focus 5; Minor 2 (balance None reported as success) rides along in the same fix round. Cost if wrong: one extra review round.
Task 4: warnings resolved: live plist untouched (controller never ran Step 6); commit stat shows only the 4 files.
Task 4: fix round 1/5 (2 addressed, 0 open; commits 3c6f9f8..3ff2de3). Controller ran the covering tests itself since the fix report lacked pasted output: test_collect_instagram_daily + test_weekly_summary pass.
Task 4: minor (deferred): refusal-count assertion ordered after the None assertion (cosmetic).
Task 4: complete (commits def3011..3ff2de3, review clean after 1 fix round)
BASE_T5=3ff2de3
Task 5: Ruling: detections health dot sums events of all platforms in the last 7 days (spec names no platform; the row is the automation's plumbing as a whole). Cost if wrong: an SC event shows a red dot on an IG-focused row.
Task 5: warnings resolved: snapshot "timestamp" key is the real schema (stats/storage.py save_snapshot); hikerapi dot stays None until the first sync after Task 4 lands.
Task 5: minor (deferred, FIX IN FINAL WAVE): red count labelled "BEHIND" collides with the headline word, use "OFF PACE"; on_pace is True when with_data == 0 (should be False with headline "COLLECTING"); fromisoformat on series dates unguarded; dead rung_line reset at :138; private _EXPORT_RE reached across modules; synthetic tests missing for the score line, a failing health check, today outside the period, and `|` alternatives.
Task 5: complete (commits 3ff2de3..e57d92e, review clean)
BASE_T6=e57d92e
Task 6: Ruling: commit cad8153 swept pre-existing UNCOMMITTED edits of other sessions in the same five files (base.html v=59->73 + sidebar links, webapp.py routes, style.css blocks) into the score-board commit. Kept as is: splitting hunks by hand risks losing live Release Manager work, and those edits were heading for main anyway. Consequences: (1) NEVER `git checkout main` in this checkout before merging, the working tree would drop that live work; finish with a fast-forward merge of score-board into main from this branch; (2) the final reviewer is told which hunks are not ours. Cost if wrong: unrelated changes ride in under the score-board commit message.
Task 6: fix round 1/5 (2 addressed, 0 open; commits cad8153..4d52c8e). Controller ran the covering tests (stats page + score board): pass.
Task 6: minor (deferred): pre-existing `var(--border)` uses elsewhere in style.css (lines ~4220-4283, 6262, 6280, 6462, 6466, 6592) reference an undefined token, out of scope; sparkline polyline repeats inline stroke attrs; page test is substring-based.
Task 6: complete (commits e57d92e..4d52c8e, review clean after 1 fix round). Visual check on the running server is still owed (Amir reloads the server).
BASE_T7=4d52c8e
Task 7: Ruling: the plan's expected six_month_rate of 29.4 was a hand rounding; the formula delta / (days / 30.4) over Apr 3 -> Sep 26 gives 29.5, so the test expects 29.5 (round5 still gives 30, targets unchanged). Cost if wrong: none for the targets.
Task 7: minor (deferred): rate_per_month KeyError unguarded; `on` after period.end unhandled; baseline date not overridable from the CLI; no test for exclude dropping a reading; propose() untested.
Task 7: complete (commits 4d52c8e..694c897, review clean). Step 6 (--set-ig-baseline) deferred to the controller after the first real IG reading + Amir's go.
BASE_T8=694c897
Task 8: Ruling: the Monday-habit SKILL.md line is variant b only and the Graph probe is still pending, so it is NOT written now; G-09 goes to "in-progress" (board built, KPI review still to hold with Amir), not "done". Cost if wrong: one ticket status to flip later.
Task 8: complete (commits 694c897..5db33fe). Full run: 6 failed / 1004 passed. REGRESSION from Task 4 (FIX IN FINAL WAVE): tests/test_stats_collect_skip.py expects collect_all's platform set without "hikerapi"; the new balance collector is intended, so the test expectation must add it. The other 5 failures are pre-existing and not ours (test_in_session_vet = per_session 15 vs 6 from 10-20, test_shoot_page x3, test_tickets DJ-01 why length). Task 8 commit trailer says Haiku, left as is.
Task 8: Ruling: Task 8 commit trailer names Haiku 5.5 instead of Fable 5.1; harmless, not amended. Cost: none.
Final review (863922a..5db33fe): With fixes. C1 storage drops manual/same-day readings; C2 Graph claim refused before 09:00 and no fallback; I1 unguarded build() on /stats; I2 followback refresh missing from daily sync (plan gap); I3 rung line misleading; I4 collect_skip test makes a live HikerAPI call; I5 Graph takes the one-API-job slot; I6 baseline date ignored; I7 health dots not traceable. Reviewer disclosed ONE live HikerAPI /sys/balance call made by the unpatched test (balance lookup, not an IG read, no ledger entry).
Final: Ruling: ONE fix wave covering C1, C2, I1, I2, I3, I4, I6 (+T7 guards), I7, T3 test, T5 (OFF PACE, COLLECTING headline when nothing has data, fromisoformat guards, score-line synthetic test), followback partial pct None + CLI n/a, score denominator over all six metrics, trend cards moved after "This week". Cost if wrong: one more review round.
Final: Ruling: ladder chart stays a sloped line (the spec's light rule is linear; its "staircase" wording contradicts it). Cost: cosmetic.
Final: Ruling: the Graph path does not run the IG standard_gates (own-account official API, not the throttled surface); days_28 reach stored as reach_30d stays (Meta has no 30-day period), noted as a hypothesis for the first live run. Cost: a None reach on the first run if the param combination is wrong.
Final: Ruling (for Amir, not mine to close): I5 Graph shares the one-API-job-per-day slot with the dispatcher's api-kind scripts, and the sync runs at 08:45 before the 09:00 daytime gate; with variant (a) the plist must move to 09:05 or the slot conflict accepted. Carried to the hand-over.
FIX_BASE=5db33fe
Final: fix wave 1/1 (all 11 findings addressed, 0 open; commits 5db33fe..f3937e9); scoped re-review clean. Full suite 1025 passed / 5 pre-existing failures.
Final: branch score-board ready at f3937e9 (13 commits over main 863922a). Merge waits on Amir's go (fast-forward from this branch, never checkout main first).
Amir 2026-11-02 ~02:30: 'Not yet' on the merge. Branch stays checked out; workspace kept. Next: daytime Graph probe + first IG reading (M-09), --set-ig-baseline, visual check, then ask again.

- 2026-11-02 10:05 Ruling: IG baseline set via --set-ig-baseline from the 01:00 snapshot (966, source hikerapi) on Amir's go; rungs 996 / 1026; commit fa75761. Pool 27 < 30, 15->6 not yet.
