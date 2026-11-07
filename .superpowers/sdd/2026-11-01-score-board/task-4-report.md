# Task 4 report
Implemented collect_instagram_daily (graph/hikerapi, ledger-claimed, SystemExit caught), collect_hikerapi_balance, _claim/_provider wrappers, collect_all wiring; docstring + plist draft updated (also the draft's comment text).
RED: `python3 -m pytest tests/test_collect_instagram_daily.py -q` -> 6 failed (functions missing), expected.
GREEN: `python3 -m pytest tests/test_collect_instagram_daily.py tests/test_stats_page.py tests/test_weekly_summary.py -q` -> 15 passed.
Tests: 3 from brief + fallback, reach-failure, balance tests; claim kwargs asserted for hikerapi.
Concerns: Graph variant with empty META_IG_ACCESS_TOKEN returns None without fallback (no claim made). Live plist (Step 6) not touched.

## Fix round 1
- Refusal test now sets source graph + token, records the claim and asserts it was called once (kind api) before asserting None.
- collect_hikerapi_balance returns None when balance() is falsy; test covers balance() returning None.
- Command: python3 -m pytest tests/test_collect_instagram_daily.py tests/test_stats_page.py -q -> see below result line in reply (all passed).
