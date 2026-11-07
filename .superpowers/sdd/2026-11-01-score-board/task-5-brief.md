### Task 5: Score board builder

**Files:**
- Create: `release_manager/score_board.py`
- Test: `tests/test_score_board.py`

**Interfaces:**
- Consumes: Task 1 (`load_targets`, `ladder_value`, `light_for_ladder`, `light_for_floor`, `progress_pct`, `current_rung`), `stats.storage.get_time_series`, `get_overview`, `get_manual_latest`, `list_snapshots`; `stats.spotify_s4a.load()` for the S4A weeks; `stats_snapshots/ig_followback.json`; `release_manager.stats_tracks.sparkline`.
- Produces: `build(today: date | None = None) -> dict` with keys:
  - `score`: `{"on_pace": bool, "green": int, "amber": int, "red": int, "none": int, "with_data": int, "line": str}`; `line` reads e.g. "ON PACE, 3/4 GREEN, 1 DRIFTING, 2 COLLECTING".
  - `cards`: list of 6 dicts in the targets file order: `{key, label, source, unit, value: str, raw: float | None, light, light_text, rung_line: str | None, progress: int | None, base_line: str | None, as_of: str | None, points: str}`. `rung_line` like "NOV 30 510, +12 PAST RUNG"; `base_line` like "447 BASE, NOV 30 510 RUNG, 600 TARGET".
  - `health`: list of 8 dicts `{key, label, ok: bool | None, detail: str, href: str | None}` in this order: ratio >= 1.0, last IG session score >= 8, vetted pool >= 30, HikerAPI requests > 10000 (that is $10 at Standard), detection events last 7 days == 0, newest snapshot <= 2 days, newest export <= 40 days, newest Spotify read <= 10 days. `ok` is `None` when the source is missing; `pass_count` and `total` at `health_summary`.
  - `trends`: list of 3 trend-only cards `{key, label, value: str, points: str, as_of: str | None}`: YouTube subscribers (`snapshot:youtube.subscribers`), Spotify followers (`s4a:weeks.followers`), Bandcamp followers (`manual:bandcamp.followers`). The spec's fourth one, SoundCloud follow-back %, is left out of this version: no file holds it as a series yet (one line to Amir, not built silently).
  - `ladders`: list of `{key, label, svg: str}` for ladder metrics with a baseline, `svg` a complete `<svg viewBox="0 0 520 200">` string drawn server-side: the real line (last 120 days of the series), the dashed staircase through baseline and rungs, a dotted baseline, a vertical "today" line, rung labels, x-axis month ticks.
- Series per source string: `snapshot:<platform>.<metric>` via `get_time_series(platform, metric, days=400)`; `s4a:weeks.monthly_active` via the S4A weeks dict as `[{date: end, value}]`; `followback:since_may_pct` as one point from the followback file; `manual:<platform>.<metric>` via `get_time_series` (manual platforms are merged there); a `|` lists sources in priority order, first non-empty wins.
- Value and as_of: the last point of the series; if the newest snapshot lacks the platform, the last point is still the last good reading (this is what `get_time_series` already returns), and `as_of` carries its date (review focus 1).

- [ ] **Step 1: Write the failing tests**

```python
from datetime import date
from release_manager import score_board as sb

def test_build_has_six_cards_in_targets_order_and_a_score_line():
    b = sb.build(today=date(2026, 11, 15))
    assert [c["key"] for c in b["cards"]] == ["ig_followers", "ig_followback_pct", "ig_reach_30d", "sc_followers", "spotify_monthly_active", "tiktok_followers"]
    assert b["score"]["with_data"] + b["score"]["none"] == 6
    assert b["score"]["line"].startswith(("ON PACE", "BEHIND"))
    tiktok = b["cards"][-1]
    assert tiktok["light"] == "none" and tiktok["light_text"] == "collecting" and tiktok["progress"] is None

def test_collecting_metric_is_excluded_from_the_score_and_has_no_ladder(monkeypatch):
    t = sb.load_targets()
    t["metrics"]["sc_followers"]["baseline"] = {"value": None, "date": None}
    monkeypatch.setattr(sb, "load_targets", lambda: t)
    b = sb.build(today=date(2026, 11, 15))
    sc = next(c for c in b["cards"] if c["key"] == "sc_followers")
    assert sc["light"] == "none" and "sc_followers" not in [l["key"] for l in b["ladders"]]

def test_missing_platform_in_newest_snapshot_keeps_last_good_reading(monkeypatch):
    series = [{"date": "2026-11-02", "value": 950}]
    monkeypatch.setattr(sb, "series_for", lambda source: series if source.startswith("snapshot:instagram") else [])
    b = sb.build(today=date(2026, 11, 15))
    ig = next(c for c in b["cards"] if c["key"] == "ig_followers")
    assert ig["value"] == "950" and ig["as_of"] == "2026-11-02"

def test_trend_cards():
    t = sb.build(today=date(2026, 11, 15))["trends"]
    assert [x["key"] for x in t] == ["yt_subscribers", "spotify_followers", "bandcamp_followers"]

def test_health_row_has_eight_checks():
    h = sb.build(today=date(2026, 11, 15))["health"]
    assert [x["key"] for x in h] == ["ratio", "session_score", "vetted_pool", "hikerapi_balance", "detections", "snapshot_age", "export_age", "spotify_read_age"]
    assert all(x["ok"] in (True, False, None) for x in h)

def test_ladder_svg_contains_the_rungs_and_today():
    b = sb.build(today=date(2026, 11, 15))
    sc = next(l for l in b["ladders"] if l["key"] == "sc_followers")
    assert sc["svg"].startswith("<svg") and "510" in sc["svg"] and "600" in sc["svg"] and "today" in sc["svg"]
```

`series_for(source: str) -> list[dict]` is the module-level resolver the tests patch.

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest tests/test_score_board.py -q`
Expected: FAIL, module not found

- [ ] **Step 3: Implement `release_manager/score_board.py`**

Health sources (all read-only): ratio from the newest snapshot's `instagram.followers / following`; last IG score = the last `autonomy_state.json` `recent[]` entry with `platform == "ig"`; vetted pool = entries in `ig_target_list.json["queue"]` with `status == "pending"` and a truthy `audit_date`; HikerAPI from the newest snapshot's `hikerapi.requests`; detections = entries in `scene_intelligence/detection_events.json` dated within 7 days (read the file first for its shape); snapshot age from `list_snapshots()[0]`; export age from `stats.ig_followback.newest_export_dir(Path("data"))`; Spotify read age from the newest `read_at` in the S4A weeks. Ladder SVG: x = days from period start to end mapped to 40..500, y = value range of min(series, baseline)..max(target, series) with 10% padding mapped to 180..20; staircase as a dashed `<polyline>` through the ladder points; series as a solid `<polyline>`; rung labels as `<text>`; "today" as a `<line>` plus `<text>today</text>`. Colours by class names only (`sb-line`, `sb-ladder`, `sb-base`, `sb-today`), no inline colours.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m pytest tests/test_score_board.py tests/test_targets.py -q`
Expected: all passed

- [ ] **Step 5: Commit**

```bash
git add release_manager/score_board.py tests/test_score_board.py
git commit -m "feat(stats): score board builder with cards, health row and ladder charts"
```

---

