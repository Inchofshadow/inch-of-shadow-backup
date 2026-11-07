# Task 3 report
Implemented stats/ig_followback.py (cohorts, since_may_pct, newest_export_dir, followers_from_export, write, CLI) and tests/test_ig_followback.py. Commit def3011.
RED: pytest tests/test_ig_followback.py -> ModuleNotFoundError: stats.ig_followback (expected, module absent).
Intermediate: reproduction test failed only on since_may_pct (21 vs 23) because the 2026-10 export-month cohort (20 followed, 0 back) was pooled in. The 10-10 report counts May-Sep only (319/72 = 23%). Fix: cohorts flags the export-month cohort with "partial": True; since_may_pct skips partial and after-export (pct None) cohorts. Expected numbers untouched.
GREEN: pytest tests/test_ig_followback.py tests/test_stats_page.py -q -> 5 passed. CLI wrote stats_snapshots/ig_followback.json, ends "since May: 23%".
Concerns: report says August 34, tracker gives 35 (test expects 35; passes). Export-month cohort has an extra "partial" key beyond the brief's shape. Uses scene_intelligence.json_io.atomic_write_json (same as stats/storage.py).
