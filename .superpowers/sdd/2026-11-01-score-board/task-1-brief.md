### Task 1: Targets file and ladder maths

**Files:**
- Create: `plans/targets.json`
- Create: `stats/targets.py`
- Test: `tests/test_targets.py`

**Interfaces:**
- Produces: `load_targets(path: Path = TARGETS_PATH) -> dict` (validated; raises `ValueError` naming the metric on a bad shape), `ladder_value(metric: dict, period: dict, on: date) -> float | None` (linear between baseline-at-period-start and the dated rungs, clamped to the ends; `None` for non-ladder kinds or a null baseline), `light_for_ladder(value: float | None, ladder_today: float | None) -> tuple[str, str]` (light, text like "+12 past rung" / "-9 to rung" / "collecting"), `light_for_floor(value: float | None, floor: float) -> tuple[str, str]`, `progress_pct(baseline: float, target: float, value: float) -> int | None` (0-100 clamped, `None` when target == baseline), `current_rung(metric: dict, on: date) -> tuple[str, float] | None` (the next rung date and value).
- The file shape (exact keys, first period):

```json
{
  "period": {"start": "2026-11-01", "end": "2026-12-31", "approved_by": "Amir", "approved_on": "2026-11-01"},
  "metrics": {
    "ig_followers":          {"label": "IG followers", "unit": "followers", "kind": "ladder", "source": "snapshot:instagram.followers",
                              "baseline": {"value": null, "date": null}, "rate_per_month": 30, "rungs": {}, "target": null,
                              "rule": "six-month pre-pause average 29.4/month rounded to 30; baseline = first board reading on 2026-11-02, rungs = baseline + 30 and + 60"},
    "ig_followback_pct":     {"label": "IG follow-back, new cohorts", "unit": "%", "kind": "floor", "source": "followback:since_may_pct",
                              "baseline": {"value": 23, "date": "2026-10-10"}, "floor": 20,
                              "rule": "mean of the May to Sep 2026 cohorts (23.2) minus 3, rounded down to 5"},
    "ig_reach_30d":          {"label": "IG reach, 30 days", "unit": "accounts", "kind": "collecting", "source": "snapshot:instagram.reach_30d|manual:instagram_insights.reach_30d"},
    "sc_followers":          {"label": "SoundCloud followers", "unit": "followers", "kind": "ladder", "source": "snapshot:soundcloud.followers",
                              "baseline": {"value": 447, "date": "2026-10-31"}, "rungs": {"2026-11-30": 510, "2026-12-31": 600}, "target": 600,
                              "rule": "SC-07 ladder, Amir confirmed 2026-09-01, unchanged"},
    "spotify_monthly_active": {"label": "Spotify monthly active listeners", "unit": "listeners", "kind": "ladder", "source": "s4a:weeks.monthly_active",
                              "baseline": {"value": 96, "date": "2026-10-30"}, "rungs": {"2026-11-30": 90, "2026-12-31": 110}, "target": 110,
                              "rule": "Nov = 12-week mean 91.75 rounded to 90; Dec = best 4-week mean of the last six months, 109 (Oct 5 to 30), rounded to 110"},
    "tiktok_followers":      {"label": "TikTok followers", "unit": "followers", "kind": "collecting", "source": "manual:tiktok.followers"}
  }
}
```

- [ ] **Step 1: Write the failing tests**

```python
from datetime import date
from stats.targets import load_targets, ladder_value, light_for_ladder, light_for_floor, progress_pct, current_rung

SC = {"kind": "ladder", "baseline": {"value": 447, "date": "2026-10-31"}, "rungs": {"2026-11-30": 510, "2026-12-31": 600}, "target": 600}
PERIOD = {"start": "2026-11-01", "end": "2026-12-31"}

def test_ladder_is_linear_between_rungs_and_clamped():
    assert ladder_value(SC, PERIOD, date(2026, 11, 1)) == 447
    assert round(ladder_value(SC, PERIOD, date(2026, 11, 30))) == 510
    assert round(ladder_value(SC, PERIOD, date(2026, 11, 15))) == 477        # 447 + 63 * 14/29 rounded
    assert ladder_value(SC, PERIOD, date(2026, 10, 1)) == 447                 # before start: baseline
    assert ladder_value(SC, PERIOD, date(2027, 2, 1)) == 600                  # after end: last rung
    assert ladder_value({"kind": "ladder", "baseline": {"value": None, "date": None}, "rungs": {}, "target": None}, PERIOD, date(2026, 11, 2)) is None

def test_lights_follow_the_95_85_bands():
    assert light_for_ladder(510, 510)[0] == "green"
    assert light_for_ladder(485, 510)[0] == "green"       # 95.1%
    assert light_for_ladder(440, 510)[0] == "amber"       # 86%
    assert light_for_ladder(400, 510)[0] == "red"
    assert light_for_ladder(None, 510) == ("none", "collecting")
    assert light_for_ladder(522, 510)[1] == "+12 past rung"
    assert light_for_ladder(501, 510)[1] == "-9 to rung"

def test_floor_lights():
    assert light_for_floor(23, 20)[0] == "green"
    assert light_for_floor(17, 20)[0] == "amber"
    assert light_for_floor(12, 20)[0] == "red"
    assert light_for_floor(None, 20)[0] == "none"

def test_progress_and_current_rung():
    assert progress_pct(447, 600, 510) == 41
    assert progress_pct(447, 600, 700) == 100 and progress_pct(447, 600, 400) == 0
    assert progress_pct(96, 96, 100) is None
    assert current_rung(SC, date(2026, 11, 15)) == ("2026-11-30", 510)
    assert current_rung(SC, date(2026, 12, 15)) == ("2026-12-31", 600)
    assert current_rung(SC, date(2027, 1, 5)) is None

def test_targets_file_loads_and_validates(tmp_path):
    t = load_targets()
    assert set(t["metrics"]) == {"ig_followers", "ig_followback_pct", "ig_reach_30d", "sc_followers", "spotify_monthly_active", "tiktok_followers"}
    bad = tmp_path / "t.json"; bad.write_text('{"period": {"start": "2026-11-01", "end": "2026-12-31"}, "metrics": {"x": {"kind": "ladder"}}}')
    import pytest
    with pytest.raises(ValueError, match="x"):
        load_targets(bad)
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest tests/test_targets.py -q`
Expected: FAIL, `ModuleNotFoundError: stats.targets`

- [ ] **Step 3: Write `plans/targets.json` exactly as in the Interfaces block**

- [ ] **Step 4: Implement `stats/targets.py`**

`TARGETS_PATH = Path(__file__).parent.parent / "plans" / "targets.json"`. Ladder: the points are `(period.start, baseline.value)` plus each rung sorted by date; before the first point return the baseline, after the last return the last rung, between them interpolate linearly on days. Light text: integer delta against the rung value rounded, "past rung" when >= 0, "to rung" when < 0. Validation: every metric needs `kind` in {ladder, floor, collecting} and `label`; ladder needs `baseline`, `rungs`, `target`; floor needs `floor` and `baseline`.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python3 -m pytest tests/test_targets.py -q`
Expected: 5 passed

- [ ] **Step 6: Commit**

```bash
git add plans/targets.json stats/targets.py tests/test_targets.py
git commit -m "feat(stats): targets file and ladder maths for the score board"
```

---

