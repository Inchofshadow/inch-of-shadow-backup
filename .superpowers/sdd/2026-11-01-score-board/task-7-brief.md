### Task 7: Proposal script and the Instagram baseline on 2026-11-02

**Files:**
- Create: `stats/propose_targets.py`
- Test: `tests/test_propose_targets.py`

**Interfaces:**
- Consumes: `get_time_series`, S4A weeks, Task 1 file.
- Produces: `six_month_rate(series: list[dict], end: date, exclude: tuple[str, str] | None = None) -> float | None` (per-30.4-day rate over the last 183 days ending at `end`, from the first to the last reading in the window; the `exclude` date range is ignored for both ends), `round5(x: float) -> int`, `propose(today: date) -> dict` printing one line per metric with the rule and the proposed numbers (never writes), and `set_ig_baseline(value: int, on: date, path: Path = TARGETS_PATH) -> dict` which writes `baseline`, two rungs (`on` + 1 calendar month end and the period end) and `target` for `ig_followers` ONLY when its baseline is null (a second call raises `RuntimeError("baseline already set")`). CLI: `python3 stats/propose_targets.py` prints; `--set-ig-baseline` reads the newest snapshot's `instagram.followers` and calls `set_ig_baseline`.

- [ ] **Step 1: Write the failing tests**

```python
import json
from datetime import date
from stats.propose_targets import six_month_rate, round5, set_ig_baseline

def test_six_month_rate_matches_the_spec_number():
    s = [{"date": "2026-04-03", "value": 777}, {"date": "2026-07-19", "value": 890}, {"date": "2026-09-26", "value": 948}, {"date": "2026-10-10", "value": 955}]
    assert round(six_month_rate(s, date(2026, 9, 26)), 1) == 29.4
    assert round5(29.4) == 30 and round5(91.75) == 90 and round5(109) == 110

def test_set_ig_baseline_writes_once(tmp_path):
    p = tmp_path / "targets.json"
    p.write_text(json.dumps({"period": {"start": "2026-11-01", "end": "2026-12-31"},
                             "metrics": {"ig_followers": {"label": "x", "kind": "ladder", "baseline": {"value": None, "date": None},
                                                          "rate_per_month": 30, "rungs": {}, "target": None}}}))
    m = set_ig_baseline(950, date(2026, 11, 2), path=p)["metrics"]["ig_followers"]
    assert m["baseline"] == {"value": 950, "date": "2026-11-02"} and m["rungs"] == {"2026-11-30": 980, "2026-12-31": 1010} and m["target"] == 1010
    import pytest
    with pytest.raises(RuntimeError):
        set_ig_baseline(951, date(2026, 11, 3), path=p)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_propose_targets.py -q`
Expected: FAIL, module not found

- [ ] **Step 3: Implement `stats/propose_targets.py`**

- [ ] **Step 4: Run the tests**

Run: `python3 -m pytest tests/test_propose_targets.py -q`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add stats/propose_targets.py tests/test_propose_targets.py
git commit -m "feat(stats): target proposal script and one-shot Instagram baseline"
```

- [ ] **Step 6: On 2026-11-02, after the first daily sync with Instagram (Amir's go)**

Run: `python3 stats/propose_targets.py --set-ig-baseline`
Expected: prints the ig_followers block with the baseline and the two rungs; `git commit -am "chore(stats): Instagram baseline for the Nov-Dec 2026 period"`.

---

