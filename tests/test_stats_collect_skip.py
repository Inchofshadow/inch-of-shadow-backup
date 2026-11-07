"""collect_all skips the named platforms; a failed read is {"skipped": reason}, never None or 0;
every snapshot reading carries provenance; readers treat skipped as not collected. No network."""
import json
from datetime import datetime

from stats import collectors, storage


def test_collect_all_skips_the_named_platforms(monkeypatch):
    called = []
    for name in ("spotify", "soundcloud", "youtube", "instagram_daily", "hikerapi_balance"):
        monkeypatch.setattr(collectors, f"collect_{name}", lambda n=name: called.append(n) or {"ok": 1})
    out = collectors.collect_all(skip=("instagram",))
    assert "instagram_daily" not in called
    assert "instagram" not in out["platforms"] and "instagram" not in out["errors"]
    assert set(out["platforms"]) == {"spotify", "soundcloud", "youtube", "hikerapi"}
    assert out["skipped"] == {}


def test_a_failed_collector_writes_skipped_because_never_a_zero(monkeypatch):
    monkeypatch.setattr(collectors, "collect_spotify", lambda: {"skipped": "Spotify albums call answered HTTP 429"})
    monkeypatch.setattr(collectors, "collect_soundcloud", lambda: None)
    monkeypatch.setattr(collectors, "collect_youtube", lambda: (_ for _ in ()).throw(RuntimeError("boom https://x?key=SECRET")))
    monkeypatch.setattr(collectors, "collect_instagram_daily", lambda: {"followers": 971, "source": "hikerapi"})
    monkeypatch.setattr(collectors, "collect_hikerapi_balance", lambda: {"requests": 83000})
    out = collectors.collect_all()
    assert out["platforms"]["spotify"] == {"skipped": "Spotify albums call answered HTTP 429"}
    assert out["platforms"]["soundcloud"] == {"skipped": "collector returned nothing"}
    assert out["platforms"]["youtube"] == {"skipped": "RuntimeError: boom https://x?key=<redacted>"}
    assert out["errors"] == ["spotify", "soundcloud", "youtube"]
    assert out["skipped"] == {"spotify": "Spotify albums call answered HTTP 429", "soundcloud": "collector returned nothing",
                              "youtube": "RuntimeError: boom https://x?key=<redacted>"}
    assert out["platforms"]["instagram"]["followers"] == 971
    assert "SECRET" not in json.dumps(out)


def test_reason_of_never_prints_a_secret(monkeypatch):
    monkeypatch.setattr(collectors, "META_IG_ACCESS_TOKEN", "tok-abc")
    monkeypatch.setattr(collectors, "YOUTUBE_API_KEY", "yt-key-1")
    text = collectors.reason_of(ValueError("GET https://g/me?access_token=tok-abc&fields=id failed; key yt-key-1"))
    assert "tok-abc" not in text and "yt-key-1" not in text and text.startswith("ValueError: ")


def test_snapshot_carries_run_id_and_every_block_an_as_of_and_source(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "SNAPSHOTS_DIR", tmp_path)
    now = datetime(2026, 11, 6, 8, 45, 10)
    name = storage.save_snapshot({"platforms": {"soundcloud": {"followers": 473}, "instagram": {"followers": 971, "source": "hikerapi"},
                                                "youtube": {"skipped": "YouTube channels call answered HTTP 403"}},
                                  "errors": ["youtube"], "skipped": {"youtube": "YouTube channels call answered HTTP 403"}}, now=now)
    snap = json.loads((tmp_path / name).read_text())
    assert name == "snapshot_2026-11-06T08-45-10.json" and snap["run_id"] == "sync:2026-11-06T08-45-10"
    assert snap["platforms"]["soundcloud"] == {"followers": 473, "as_of": "2026-11-06T08:45:10", "source": "soundcloud_api"}
    assert snap["platforms"]["instagram"]["source"] == "hikerapi" and snap["platforms"]["instagram"]["as_of"] == "2026-11-06T08:45:10"
    assert snap["platforms"]["youtube"] == {"skipped": "YouTube channels call answered HTTP 403", "as_of": "2026-11-06T08:45:10"}
    assert storage.skipped_in(snap, "youtube") == "YouTube channels call answered HTTP 403" and storage.skipped_in(snap, "soundcloud") is None


def test_readings_carry_provenance_and_skip_the_skipped_block(monkeypatch):
    now = datetime(2026, 11, 6, 12, 0)
    snaps = [  # newest first, as list_snapshots returns them
        {"timestamp": "2026-11-06T08:45:10", "run_id": "sync:2026-11-06T08-45-10",
         "platforms": {"instagram": {"skipped": "HikerAPI 429", "as_of": "2026-11-06T08:45:10"}}},
        {"timestamp": "2026-11-05T20:17:25", "run_id": "sync:2026-11-05T20-17-25",
         "platforms": {"instagram": {"followers": 971, "as_of": "2026-11-05T20:17:25", "source": "hikerapi"}}},
        {"timestamp": "2026-11-04T08:45:00",
         "platforms": {"instagram": {"followers": 969}}},
    ]
    monkeypatch.setattr(storage, "list_snapshots", lambda: snaps)
    monkeypatch.setattr(storage, "load_manual_entries", lambda: {"entries": [
        {"platform": "email_list", "date": "2026-11-05", "timestamp": "2026-11-05T20:46:22", "source": "manual:amir", "subscribers": 16}]})
    r = storage.get_readings("instagram", "followers", 30, now=now)
    assert r == [{"date": "2026-11-04", "value": 969, "as_of": "2026-11-04T08:45:00", "source": "hikerapi", "run_id": None},
                 {"date": "2026-11-05", "value": 971, "as_of": "2026-11-05T20:17:25", "source": "hikerapi", "run_id": "sync:2026-11-05T20-17-25"}]
    assert storage.get_time_series("instagram", "followers", 30)[-1] == {"date": "2026-11-05", "value": 971}   # skipped day = no point, no 0
    e = storage.get_readings("email_list", "subscribers", 30, now=now)
    assert e == [{"date": "2026-11-05", "value": 16, "as_of": "2026-11-05", "source": "manual:amir", "run_id": "manual:2026-11-05T20:46:22"}]


def test_manual_entry_carries_its_source(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "MANUAL_FILE", tmp_path / "manual_entries.json")
    monkeypatch.setattr(storage, "SNAPSHOTS_DIR", tmp_path)
    e = storage.save_manual_entry("email_list", {"subscribers": 17}, date="2026-11-06")
    assert e["source"] == "manual:amir"
    e = storage.save_manual_entry("bandcamp", {"followers": 52}, date="2026-11-06", source="import:bandcamp-csv")
    assert e["source"] == "import:bandcamp-csv"
    from stats import manual_entry
    assert manual_entry.main(["tiktok", "followers", "3", "--date", "2026-11-06", "--source", "manual:amir"]) == 0
    assert storage.get_manual_latest("tiktok")["source"] == "manual:amir"
