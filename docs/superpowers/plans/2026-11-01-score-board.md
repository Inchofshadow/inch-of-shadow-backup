# Score Board Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put six growth metrics with written targets, lights, a monthly ladder and ladder charts at the top of the Release Manager's `/stats` page, fed daily without any manual habit beyond the monthly export (and, in variant b, a Monday screenshot).

**Architecture:** A `plans/targets.json` file holds the approved baselines and rungs; `stats/targets.py` reads it and does the ladder maths and the lights; `release_manager/score_board.py` joins targets with the snapshot series, the follow-back file, the manual entries and the health sources into one dict the template renders as cards, a health row and server-side SVG ladder charts. Two small data feeds are added: a light daily Instagram collector (Graph, with HikerAPI as the fallback or the main source depending on the probe) and a follow-back script that reproduces the 2026-10-10 analysis from the tracker and the newest All-time export.

**Tech Stack:** Python 3.9 (system), Flask, Jinja2, pytest, `requests`, inline SVG. No chart library, no CDN, no new dependency.

**Spec:** `docs/superpowers/specs/2026-11-01-score-board-design.md`

## Global Constraints

- Python 3.9 syntax (no `match`, no `X | Y` at runtime outside annotations; keep `from __future__ import annotations`).
- No emojis in code or output. No em-dashes in page copy.
- Hands off the engagement automation code and state: `scene_intelligence/ig_engagement*.py`, `ig_live_driver.py`, `ig_follow_tracker.json`, `ig_target_list.json`, `autonomy_state.json` are READ ONLY here. The only shared touch points are `ig_data_provider.Provider` (read) and `ig_daily_ledger.check_and_claim` (claim).
- Every Instagram API read goes through `check_and_claim` first. `LedgerRefused` is a `SystemExit`; collectors catch it and return `None`, never crash the sync.
- No private-client Instagram read. Graph (`graph.instagram.com`, own token) or HikerAPI only.
- Dark theme only, existing tokens in `release_manager/static/style.css`, Marcellus for big numbers, Inter for the rest, inline SVG. Bump `style.css?v=73` to `v=74` in `base.html` when CSS changes.
- Claude never restarts the Release Manager server; Amir reloads it.
- Lights: ladder metrics green at >= 95% of today's ladder value, amber at >= 85%, red below; floor metrics green at or above the floor, amber within 5 points below, red below that; no reading = "collecting" (grey).
- "On pace" when green >= half of the metrics that have data (rounded up).
- Repo is local-only git: commit, never push, never add a remote.

## Review Focus

1. A snapshot where `platforms.instagram` is missing (the sync failed that day): the IG card must show the last good reading with its date, not an empty card or a crash. Pinned in Task 5.
2. `targets.json` with a metric whose `baseline.value` is `null` (IG before 2026-11-02): the card says "collecting", the ladder chart is skipped, the score line excludes it. Pinned in Task 1 and Task 5.
3. Today outside the period (before start or after end): ladder maths must clamp to the first/last rung, not extrapolate. Pinned in Task 1.
4. The follow-back script on an export older than the tracker's newest cohort (a cohort with 0 "back" because the export predates it): that cohort is reported with `pct: null`, not 0%. Pinned in Task 3.
5. Two syncs in one day (launchd at 08:45 and the "Sync now" button): the second ledger claim is refused; the collector returns `None` and the snapshot still saves the other platforms. Pinned in Task 4.

---

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

### Task 2: Manual entries for the new keys and the entry CLI

**Files:**
- Modify: `stats/storage.py:86-103` (`save_manual_entry`), `:147` and `:211` (the manual platform tuples)
- Create: `stats/manual_entry.py`
- Test: `tests/test_manual_entry.py`

**Interfaces:**
- Produces: `MANUAL_PLATFORMS = ("bandcamp", "beatport", "apple_music", "instagram_insights", "tiktok")` in `stats/storage.py`, used at both former tuple sites; `save_manual_entry(platform: str, data: dict, date: str | None = None) -> dict` (explicit `date` "YYYY-MM-DD" overrides today); CLI `python3 stats/manual_entry.py <platform> <metric> <value> [--date YYYY-MM-DD]` writing one entry `{platform, date, timestamp, <metric>: value}` and printing the saved entry.
- Consumes: `load_manual_entries()`, `atomic_write_json` as already used in `storage.py`.

- [ ] **Step 1: Write the failing tests**

```python
import json, subprocess, sys
from stats import storage

def test_manual_platforms_include_the_new_keys():
    assert "instagram_insights" in storage.MANUAL_PLATFORMS and "tiktok" in storage.MANUAL_PLATFORMS

def test_save_manual_entry_accepts_a_date(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "MANUAL_FILE", tmp_path / "manual_entries.json")
    monkeypatch.setattr(storage, "SNAPSHOTS_DIR", tmp_path)
    e = storage.save_manual_entry("bandcamp", {"followers": 51}, date="2026-10-21")
    assert e["date"] == "2026-10-21" and e["followers"] == 51
    assert storage.get_time_series("bandcamp", "followers", days=400)[-1] == {"date": "2026-10-21", "value": 51}

def test_cli_writes_an_entry(tmp_path, monkeypatch):
    env = {"STATS_MANUAL_FILE": str(tmp_path / "m.json")}
    out = subprocess.run([sys.executable, "stats/manual_entry.py", "instagram_insights", "reach_30d", "1234", "--date", "2026-11-03"],
                         capture_output=True, text=True, env={**__import__('os').environ, **env})
    assert out.returncode == 0 and "reach_30d" in out.stdout
    saved = json.loads((tmp_path / "m.json").read_text())["entries"][0]
    assert saved["platform"] == "instagram_insights" and saved["reach_30d"] == 1234 and saved["date"] == "2026-11-03"
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest tests/test_manual_entry.py -q`
Expected: FAIL on `MANUAL_PLATFORMS`

- [ ] **Step 3: Implement**

In `storage.py`: the constant, the optional `date` parameter (validate with `datetime.strptime`), and `MANUAL_FILE = Path(os.getenv("STATS_MANUAL_FILE", SNAPSHOTS_DIR / "manual_entries.json"))` so the CLI test can redirect it. In `manual_entry.py`: argparse, value parsed as int when it has no dot else float, calls `save_manual_entry`, prints `json.dumps(entry)`.

- [ ] **Step 4: Run the tests, plus the existing storage tests**

Run: `python3 -m pytest tests/test_manual_entry.py tests/test_stats_page.py tests/test_weekly_view.py -q`
Expected: all passed

- [ ] **Step 5: Backfill the Bandcamp baseline and commit**

Run: `python3 stats/manual_entry.py bandcamp followers 51 --date 2026-10-21`
Expected: prints the entry; `stats_snapshots/manual_entries.json` now exists with one entry.

```bash
git add stats/storage.py stats/manual_entry.py tests/test_manual_entry.py stats_snapshots/manual_entries.json
git commit -m "feat(stats): manual entries for IG reach, TikTok and Bandcamp followers, with a CLI"
```

---

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

### Task 4: Daily Instagram sample and HikerAPI balance in the sync

**Files:**
- Modify: `stats/collectors.py:460-470` (token constants) and `:667-690` (`collect_all`)
- Modify: `stats/daily_sync.py` (docstring only: the scheduled run no longer skips Instagram)
- Modify: `plans/control-panel/launchd-stats-sync.plist.draft` (drop `--skip instagram`); the live plist `~/Library/LaunchAgents/com.inchofshadow.stats-sync.plist` is Amir's file: change it only after his go, then `launchctl unload` + `load`.
- Test: `tests/test_collect_instagram_daily.py`

**Interfaces:**
- Produces: `IG_DAILY_SOURCE = os.getenv("IG_DAILY_SOURCE", "graph")` ("graph" or "hikerapi", set in `.env` once the probe decides); `collect_instagram_daily() -> dict | None` returning `{"followers": int, "following": int, "media_count": int, "reach_30d": int | None, "source": "graph" | "hikerapi"}`; `collect_hikerapi_balance() -> dict | None` returning `{"requests": int | None, "balance": <raw>}`; `collect_all` runs `("instagram", collect_instagram_daily)` in place of `collect_instagram` and adds `("hikerapi", collect_hikerapi_balance)`.
- Graph variant: one ledger claim `check_and_claim(script="stats_daily_sync", kind="api", est_calls=2, endpoint="graph_insights")`, then `GET https://graph.instagram.com/v21.0/me?fields=id,username,media_count,followers_count,follows_count` and `GET .../me/insights?metric=reach&period=days_28&metric_type=total_value` (reach_30d = that total; `None` if the insights call fails). Falls back to the HikerAPI variant if the Graph profile call is not 200.
- HikerAPI variant: `check_and_claim(script="stats_daily_sync", kind="provider", est_calls=1, endpoint="user_by_username")`, then `Provider().profile("inch_of_shadow")` normalised with `normalise_profile`; `reach_30d` is `None` (the manual entry covers it).
- `LedgerRefused` (a `SystemExit`) is caught in both variants and returns `None`. Any other exception also returns `None` (`collect_all` already records the platform in `errors`).
- `collect_instagram()` stays in the file untouched (other callers), it is just no longer in `collect_all`.

- [ ] **Step 1: Write the failing tests**

```python
import stats.collectors as c

class R:  # minimal requests.Response stand-in
    def __init__(self, code, data): self.status_code, self._d = code, data
    def json(self): return self._d

def test_graph_variant_reads_profile_and_reach(monkeypatch):
    monkeypatch.setattr(c, "IG_DAILY_SOURCE", "graph"); monkeypatch.setattr(c, "META_IG_ACCESS_TOKEN", "t")
    monkeypatch.setattr(c, "_claim", lambda **kw: None)
    calls = []
    def fake_get(url, params=None, timeout=None):
        calls.append(url)
        if url.endswith("/me"): return R(200, {"followers_count": 951, "follows_count": 970, "media_count": 85})
        return R(200, {"data": [{"name": "reach", "total_value": {"value": 2310}}]})
    monkeypatch.setattr(c.requests, "get", fake_get)
    assert c.collect_instagram_daily() == {"followers": 951, "following": 970, "media_count": 85, "reach_30d": 2310, "source": "graph"}
    assert len(calls) == 2

def test_ledger_refusal_returns_none_and_sync_keeps_other_platforms(monkeypatch):
    from scene_intelligence.ig_daily_ledger import LedgerRefused
    def refuse(**kw): raise LedgerRefused(4)
    monkeypatch.setattr(c, "_claim", refuse)
    assert c.collect_instagram_daily() is None
    monkeypatch.setattr(c, "collect_spotify", lambda: {"ok": 1}); monkeypatch.setattr(c, "collect_soundcloud", lambda: None)
    monkeypatch.setattr(c, "collect_youtube", lambda: None); monkeypatch.setattr(c, "collect_hikerapi_balance", lambda: {"requests": 83000})
    out = c.collect_all()
    assert out["platforms"]["spotify"] == {"ok": 1} and "instagram" in out["errors"] and out["platforms"]["hikerapi"]["requests"] == 83000

def test_hikerapi_variant(monkeypatch):
    monkeypatch.setattr(c, "IG_DAILY_SOURCE", "hikerapi"); monkeypatch.setattr(c, "_claim", lambda **kw: None)
    class P:
        def profile(self, u): return {"username": u, "follower_count": 952, "following_count": 971, "media_count": 85}
    monkeypatch.setattr(c, "_provider", lambda: P())
    out = c.collect_instagram_daily()
    assert out["followers"] == 952 and out["reach_30d"] is None and out["source"] == "hikerapi"
```

`_claim(**kw)` is a one-line wrapper around `check_and_claim` and `_provider()` returns `Provider()`, both module-level so tests can patch them. Check `normalise_profile` in `ig_data_provider.py` for the real key names and use them in the fake.

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest tests/test_collect_instagram_daily.py -q`
Expected: FAIL, `collect_instagram_daily` missing

- [ ] **Step 3: Implement in `stats/collectors.py`**

Imports of the ledger and provider are inside the functions (they live in `scene_intelligence/`, which the sync must not import at module load if it is missing). `collect_hikerapi_balance` calls `Provider().balance()` and returns `{"requests": bal.get("requests"), "balance": bal}`; no ledger claim (it is not an Instagram read; the dispatcher makes the same call).

- [ ] **Step 4: Run the tests and the whole stats suite**

Run: `python3 -m pytest tests/test_collect_instagram_daily.py tests/test_stats_page.py tests/test_weekly_summary.py -q`
Expected: all passed

- [ ] **Step 5: Update the docstring and the plist draft, commit**

In `daily_sync.py` replace the `--skip instagram` usage line with "`--skip instagram` is no longer the scheduled default (score board, 2026-11)". In the plist draft remove the two `<string>` lines `--skip` and `instagram`.

```bash
git add stats/collectors.py stats/daily_sync.py plans/control-panel/launchd-stats-sync.plist.draft tests/test_collect_instagram_daily.py
git commit -m "feat(stats): daily Instagram sample (Graph or HikerAPI, ledger-claimed) and HikerAPI balance in the sync"
```

- [ ] **Step 6: Live plist (after Amir's go, in the 09:00-21:00 window)**

Edit `~/Library/LaunchAgents/com.inchofshadow.stats-sync.plist` the same way, then:
Run: `launchctl unload ~/Library/LaunchAgents/com.inchofshadow.stats-sync.plist && launchctl load ~/Library/LaunchAgents/com.inchofshadow.stats-sync.plist && launchctl list | grep stats-sync`
Expected: one line with the label and exit status 0 or "-".

---

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

### Task 6: Page, template and CSS

**Files:**
- Modify: `release_manager/webapp.py:5135-5140` (`stats_page`)
- Modify: `release_manager/templates/stats.html:18-21` (replace the `.st-score` block)
- Modify: `release_manager/static/style.css` (append a `/* Score board */` block after the Measure-03 block at ~6296), `release_manager/templates/base.html:9` (`v=73` to `v=74`)
- Test: `tests/test_stats_page.py` (extend), `tests/test_score_board.py` (one render test)

**Interfaces:**
- Consumes: Task 5 `score_board.build()`.
- Produces: `stats_page()` passes `board=score_board.build()`; the template renders, in order, the score line (`.sb-score`), the six cards (`.sb-grid` 3 columns, `.sb-card.sb-<light>`), the health row (`.sb-health`, dots `.sb-dot.ok|.fail|.unknown`, "7/8 pass"), the ladder charts (`.sb-ladders`, two per row), the three trend-only cards (`.sb-trends`, header "TREND ONLY, no target"), then everything the page already had from `{% if weekly %}` down, untouched.
- Copy, exact: page subtitle becomes "Growth against the written targets in plans/targets.json. A light compares today with the ladder: green on track, amber drifting, red behind, grey collecting."; card footer "as of {date}"; health header "HEALTH"; ladder header "LADDER" with the muted note "the line is reality, the steps are the plan".

- [ ] **Step 1: Write the failing tests**

```python
from release_manager.webapp import app

def test_stats_page_renders_the_score_board():
    html = app.test_client().get("/stats").get_data(as_text=True)
    assert 'class="sb-score"' in html and "IG followers" in html and "TikTok followers" in html
    assert "HEALTH" in html and "LADDER" in html and "the line is reality" in html and "TREND ONLY" in html
    assert "collecting" in html
    for track in ("Instagram", "SoundCloud", "YouTube", "Spotify", "Bandcamp"):   # the old grid is still there
        assert track in html
    assert "style.css?v=74" in html
```

Keep the existing `test_stats_page_renders_the_score_line_and_every_track` but change its first assertion from `"growing" in html` to `"GREEN" in html` (the old score line is gone).

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_stats_page.py -q`
Expected: FAIL on `sb-score`

- [ ] **Step 3: Implement the route, the template and the CSS**

Grid: `grid-template-columns: repeat(3, 1fr)`, one column under 900px. Card: big number in `var(--font-heading)` 30px like `.st-value`; light classes map to the existing status colours (`--color-done-text`, `--color-warning-text`, `--color-overdue-text`, grey `--text-muted` or the closest existing muted token); progress bar 3px with the light's colour; mono source key in 11px. SVG classes: `.sb-line` stroke `currentColor`, `.sb-ladder` stroke `var(--text-accent)` dashed 4 2, `.sb-base` dotted, `.sb-today` stroke `var(--color-warning-text)`.

- [ ] **Step 4: Run the page tests and look at it**

Run: `python3 -m pytest tests/test_stats_page.py tests/test_score_board.py -q`
Expected: all passed
Then ask Amir to reload the Release Manager and open `/stats`; take a screenshot in the built-in browser at `http://127.0.0.1:5001/stats` once he confirms the reload (Claude does not restart the server).

- [ ] **Step 5: Commit**

```bash
git add release_manager/webapp.py release_manager/templates/stats.html release_manager/templates/base.html release_manager/static/style.css tests/test_stats_page.py
git commit -m "feat(stats): score board on top of the Stats page"
```

---

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

### Task 8: Monday habit line (variant b only) and the ticket close

**Files:**
- Modify (variant b only): `~/.claude/scheduled-tasks/spotify-s4a-weekly-read/SKILL.md`, the closing report section: add the line "Instagram Insights: send the Accounts reached (30 days) screenshot in chat; it is stored with `python3 stats/manual_entry.py instagram_insights reach_30d <n> --date <today>`."
- Modify: `plans/tickets.json`: G-09 status "done" with a note pointing at the spec, the plan and the page; `plans/control-panel/tickets.json` Measure-03: note "targets per metric added 2026-11, see Score board".

- [ ] **Step 1: Full test run**

Run: `python3 -m pytest tests -q`
Expected: the 5 pre-existing failures (watchdog red, non-stats) and nothing new; every test from Tasks 1 to 7 passing.

- [ ] **Step 2: Ticket notes and commit**

```bash
git add plans/tickets.json plans/control-panel/tickets.json
git commit -m "chore(tickets): score board shipped (G-09), Measure-03 targets note"
```
