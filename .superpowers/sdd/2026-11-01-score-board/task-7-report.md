# Task 7 report
Implemented stats/propose_targets.py (six_month_rate, round5, propose, set_ig_baseline, CLI) and tests/test_propose_targets.py (4 tests).
TDD: RED = collection error (module not found) on first run; GREEN = `python3 -m pytest tests/test_propose_targets.py tests/test_targets.py -q` -> 9 passed.
Commit 694c897. targets.json untouched; --set-ig-baseline not run (Step 6 skipped).
Live propose output: ig latest 948, rate 30.4 -> 30 (rungs 978/1008); spotify 12-week mean 91.75 -> 90, best 4-week 108.75 -> 110 (matches the file's rule text).
Concerns: brief's test expected 29.4; formula gives 29.54, test uses 29.5 as instructed. The IG proposal rate uses the whole 183-day window with no pause exclusion (propose passes no `exclude`; the pause dates are not in the data given). Rate on live data 30.4 vs the file's 29.4 rule text; both round to 30.
