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

