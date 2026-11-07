### Task 3: Follow-back script (the 2026-10-10 method)

**Files:**
- Create: `stats/ig_followback.py`
- Test: `tests/test_ig_followback.py`

**Interfaces:**
- Produces: `cohorts(tracker: dict, followers: set[str], export_date: str) -> dict[str, dict]` keyed "YYYY-MM" with `{"followed": int, "back": int, "pct": float | None}`; `since_may_pct(cohorts: dict, start: str = "2026-05") -> float | None`; `newest_export_dir(data_dir: Path) -> Path | None` (newest `data/instagram-inch_of_shadow-<date>-*` by the date in the name); `followers_from_export(export_dir: Path) -> set[str]` (handles from `connections/followers_and_following/followers_1.json`, lower-cased); `write(out: Path = OUT) -> dict` writing `stats_snapshots/ig_followback.json` as `{"export_date": "YYYY-MM-DD", "computed_at": iso, "cohorts": {...}, "since_may_pct": float}`; CLI `python3 stats/ig_followback.py` runs `write()` and prints the table.
- Cohort membership: every entry in `tracker["active_follows"]` (by `followed_at[:10]`) and `tracker["unfollowed_history"]` (by `followed_date[:10]`), entries without a date skipped; a handle is "back" when its lower-cased `username` is in `followers`. A cohort whose month is after the export date has `pct: None`.
- Consumes: `scene_intelligence/ig_follow_tracker.json` (read only).

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path
import pytest
from stats.ig_followback import cohorts, since_may_pct, followers_from_export, newest_export_dir

TRACKER = {"active_follows": [{"username": "A", "followed_at": "2026-09-03T10:00"}, {"username": "b", "followed_at": "2026-09-10"}],
           "unfollowed_history": [{"username": "c", "followed_date": "2026-08-02"}, {"username": "nodate"}, {"username": "d", "followed_date": "2026-11-20"}]}

def test_cohorts_count_tracker_follows_by_month_against_the_export():
    c = cohorts(TRACKER, {"a", "c"}, export_date="2026-10-10")
    assert c["2026-09"] == {"followed": 2, "back": 1, "pct": 50.0}
    assert c["2026-08"] == {"followed": 1, "back": 1, "pct": 100.0}
    assert c["2026-11"]["pct"] is None                       # cohort after the export, review focus 4
    assert "nodate" not in str(c)
    assert since_may_pct(c) == pytest.approx(66.7, abs=0.1)   # 2 back of 3 dated follows at or before the export

EXPORT = Path("data")
@pytest.mark.skipif(not any(EXPORT.glob("instagram-inch_of_shadow-2026-10-10-*")), reason="10-10 export not on this machine")
def test_reproduces_the_2026_10_10_analysis():
    import json
    d = newest_export_dir(EXPORT)
    assert d.name.startswith("instagram-inch_of_shadow-2026-10-10")
    tracker = json.loads(Path("scene_intelligence/ig_follow_tracker.json").read_text())
    c = cohorts(tracker, followers_from_export(d), export_date="2026-10-10")
    assert (c["2026-05"]["followed"], c["2026-05"]["back"]) == (54, 14)
    assert (c["2026-06"]["followed"], c["2026-06"]["back"]) == (91, 16)
    assert (c["2026-07"]["followed"], c["2026-07"]["back"]) == (81, 18)
    assert (c["2026-08"]["followed"], c["2026-08"]["back"]) == (35, 7)
    assert (c["2026-09"]["followed"], c["2026-09"]["back"]) == (58, 17)
    assert round(since_may_pct(c)) == 23
```

Note the `export_date` keyword: add it to the `cohorts` signature, `cohorts(tracker, followers, export_date: str) -> dict`.

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest tests/test_ig_followback.py -q`
Expected: FAIL, module not found

- [ ] **Step 3: Implement `stats/ig_followback.py`**

The export's `followers_1.json` is a list of `{"string_list_data": [{"value": "<handle>", ...}]}`; take `value`. If the reproduction test disagrees with the 10-10 numbers, read `docs/reports/ig-export-analysis-2026-10-10.md` section 3 for the exact filter it used and match it; do not change the expected numbers.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m pytest tests/test_ig_followback.py -q`
Expected: 2 passed

- [ ] **Step 5: Write the file and commit**

Run: `python3 stats/ig_followback.py`
Expected: prints the cohort table ending "since May: 23%"; `stats_snapshots/ig_followback.json` exists.

```bash
git add stats/ig_followback.py tests/test_ig_followback.py stats_snapshots/ig_followback.json
git commit -m "feat(stats): follow-back by cohort from the tracker and the All-time export"
```

---

