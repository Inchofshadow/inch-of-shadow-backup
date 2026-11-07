import json, os, subprocess, sys
from stats import storage


def test_manual_platforms_include_the_new_keys():
    assert "instagram_insights" in storage.MANUAL_PLATFORMS and "tiktok" in storage.MANUAL_PLATFORMS
    assert "email_list" in storage.MANUAL_PLATFORMS                                   # D4, 2026-11-05


def test_email_list_entry_is_stored_with_its_note():
    series = storage.get_time_series("email_list", "subscribers", days=400)
    assert series and series[0] == {"date": "2026-11-05", "value": 16}
    e = storage.get_manual_latest("email_list")
    assert e["notes"] == "Bandcamp mailing list"


def test_save_manual_entry_accepts_a_date(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "MANUAL_FILE", tmp_path / "manual_entries.json")
    monkeypatch.setattr(storage, "SNAPSHOTS_DIR", tmp_path)
    e = storage.save_manual_entry("bandcamp", {"followers": 51}, date="2026-10-21")
    assert e["date"] == "2026-10-21" and e["followers"] == 51
    assert storage.get_time_series("bandcamp", "followers", days=400)[-1] == {"date": "2026-10-21", "value": 51}


def test_cli_writes_an_entry(tmp_path):
    env = {"STATS_MANUAL_FILE": str(tmp_path / "m.json")}
    out = subprocess.run([sys.executable, "stats/manual_entry.py", "instagram_insights", "reach_30d", "1234", "--date", "2026-11-03"],
                         capture_output=True, text=True, env={**os.environ, **env})
    assert out.returncode == 0 and "reach_30d" in out.stdout
    saved = json.loads((tmp_path / "m.json").read_text())["entries"][0]
    assert saved["platform"] == "instagram_insights" and saved["reach_30d"] == 1234 and saved["date"] == "2026-11-03"
