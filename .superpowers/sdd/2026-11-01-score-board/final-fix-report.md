# Score board: final review fix wave

Commit: f3937e9 fix(stats): final review wave for the score board (branch score-board)

## Per item

| Item | Change | Test |
|---|---|---|
| C1 | stats/storage.py:121 `get_time_series` walks snapshots newest first, keeps the first value per date (the newest reading), adds a date to `seen_dates` only when a value was taken. Manual entries merge for dates with no snapshot value (newest manual entry of a day wins). Live check: `get_time_series('bandcamp','followers',400)` -> `[{'date': '2026-10-21', 'value': 51}]` | tests/test_time_series_same_day.py (4 tests: later same-day snapshot with the platform, newest same-day value, manual entry on a day with an unrelated snapshot, snapshot beats manual) |
| C2 | stats/collectors.py:694-705 `_ig_daily_graph`: the api claim is wrapped; `SystemExit` (OpsGate, LedgerRefused) falls back to `_ig_daily_hikerapi()`; KeyboardInterrupt re-raised | tests/test_collect_instagram_daily.py `test_graph_claim_gate_falls_back_to_hikerapi`; the refusal test now refuses both claims and asserts `["api", "provider"]` and None |
| I1 | release_manager/webapp.py:5141 try/except around `score_board.build()`, passes `board`/`board_error`; stats.html:17-19 renders `.sb-error` "Score board unavailable: ..." and skips board + trends; style.css:6300 `.sb-error` rule (no cache-bust bump, the page test pins v=74) | tests/test_stats_page.py `test_stats_page_survives_a_broken_score_board` |
| I2 | stats/daily_sync.py:28 `refresh_followback()` called after the snapshot save; compares the newest export date with `export_date` in ig_followback.json (missing = refresh), calls `ig_followback.write()`; failures print one line | tests/test_daily_sync_followback.py (newer, equal, missing file, failure) |
| I3 | release_manager/score_board.py:137 `_rung_line`: "-2 VS PLAN TODAY, 63 TO NOV 30 510" / "+45 VS PLAN TODAY, 12 PAST NOV 30 510" | tests/test_score_board.py `test_rung_line_reads_delta_vs_plan_and_distance_to_rung` |
| I4 | tests/test_stats_collect_skip.py fakes all five collectors incl. `collect_instagram_daily` and `collect_hikerapi_balance`; expected set includes "hikerapi". Read back: no unpatched collector remains | same file |
| I6 | stats/targets.py:39-43 ladder anchor = max(period.start, baseline.date). stats/propose_targets.py: `rate_per_month` ValueError, `on > period.end` ValueError (:103-108); `earliest_ig_reading` (:120) + CLI `--set-ig-baseline [--value N] [--date YYYY-MM-DD]` | tests/test_targets.py `test_ladder_anchors_at_a_later_baseline_date`; tests/test_propose_targets.py `test_set_ig_baseline_guards`, `test_earliest_ig_reading_on_or_after_period_start`, `test_cli_uses_earliest_reading_and_overrides` (targets path and writer patched, plans/targets.json untouched) |
| I7 | score_board.py:243 `_health`: every detail names the as-of date ("0.98 on 2026-09-27, floor 1.0", "9 on 2026-10-31, min 8", "2 days, taken 2026-10-31, max 2", "23 days, export of 2026-10-10, max 40", ...), href = repo-relative source path or None. stats.html health dot: path appended to the `title`, the old `<a href>` removed (a file path is not a route) | tests/test_score_board.py `test_health_row_has_eight_checks` (non-empty detail, href str or None) + `test_health_details_carry_the_as_of_date_and_source` |
| T3 | tests/test_ig_followback.py resolves `data/instagram-inch_of_shadow-2026-10-10-*` by glob from the repo root, skips if absent, same expected numbers. stats/ig_followback.py:52 export-month cohort `pct: None` (counts and `partial` kept); CLI already prints n/a. stats_snapshots/ig_followback.json regenerated (2026-10: followed 20, back 0, pct null; since May 23%) | `test_export_month_cohort_is_partial_with_no_pct`, `test_reproduces_the_2026_10_10_analysis` |
| T5 | score_board.py:179 `_score`: red word OFF PACE, COLLECTING headline + on_pace False when no data, green out of all metrics; `_iso`/`_num`/`_clean_series`/`_clean_metric` (:69-104) skip malformed series points and rungs in series_for, _card, ladder_svg, _mon; `_fmt` tolerates non-numeric | tests/test_score_board.py `test_score_on_pace_behind_and_collecting`, `test_bad_points_and_rungs_are_skipped` |
| Order | stats.html: trends block moved into its own `<section class="sb" aria-label="Trends">` after the This week block, before the per-track grid | tests/test_stats_page.py `test_trends_come_after_this_week_and_before_the_track_grid` |

Live board now: "ON PACE, 3/6 GREEN, 0 DRIFTING, 0 OFF PACE, 3 COLLECTING"; SC rung line "-2 VS PLAN TODAY, 63 TO NOV 30 510".

## Test output

```
$ python3 -m pytest tests/test_targets.py tests/test_manual_entry.py tests/test_ig_followback.py tests/test_collect_instagram_daily.py tests/test_score_board.py tests/test_stats_page.py tests/test_propose_targets.py tests/test_stats_collect_skip.py tests/test_time_series_same_day.py tests/test_weekly_view.py tests/test_weekly_summary.py -q
58 passed, 1 warning in 1.76s
(+ tests/test_daily_sync_followback.py: 62 passed)

$ python3 -m pytest tests -q 2>&1 | tail
FAILED tests/test_in_session_vet.py::test_select_vets_only_when_pool_low
FAILED tests/test_shoot_page.py::test_every_photo_has_a_cover_idea_and_the_page_draws_it
FAILED tests/test_shoot_page.py::test_cover_fonts_exist_and_the_page_sets_the_idea_in_one
FAILED tests/test_shoot_page.py::test_covers_page_and_every_cover_carries_the_name_and_an_ink
FAILED tests/test_tickets.py::test_seed_every_ticket_has_short_why_and_helps   (AssertionError: DJ-01)
5 failed, 1025 passed, 1 warning in 18.31s
```

Only the 5 known pre-existing failures.

## Concerns

- Score line format: I show all four counts always, so the all-collecting line is "COLLECTING, 0/6 GREEN, 0 DRIFTING, 0 OFF PACE, 6 COLLECTING" (the brief's example left out "0 OFF PACE"; I picked one consistent rule). Easy to change if the exact example matters.
- `_ig_daily_graph` still returns None with no fallback when META_IG_ACCESS_TOKEN is empty (out of scope, noted only).
- `.sb-error` CSS added without bumping style.css?v=74 (the page test pins 74); a hard reload may be needed once.
- The regenerated ig_followback.json uses the current follow tracker, which the automation keeps modifying (uncommitted, not mine); the 10-10 numbers still reproduce.
- Period start/end dates in targets.json are not guarded inside score_board (config, not series); a bad one is caught by the I1 page guard.
