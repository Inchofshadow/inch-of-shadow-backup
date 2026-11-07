"""System 67: the read-only spend report (stats/spend.py) over fixture ledgers."""

import json
from datetime import datetime

import pytest

from stats import spend


NOW = datetime(2026, 11, 5, 12, 0)


def _write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data))


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(spend, "CLAUDE_LEDGER", tmp_path / "claude_spend.json")
    monkeypatch.setattr(spend, "OPENAI_LEDGER", tmp_path / "openai_spend.json")
    monkeypatch.setattr(spend, "IMAGINE_DIR", tmp_path / "imagine")
    monkeypatch.setattr(spend, "RAW_RENDER_DIR", tmp_path / "pinocchio-single")
    monkeypatch.setattr(spend, "SNAPSHOTS", tmp_path / "snaps")
    monkeypatch.setattr(spend, "GERO_LEDGER", tmp_path / "gero" / "claude_spend.json")
    monkeypatch.setattr(spend, "OUT_FILE", tmp_path / "spend_latest.json")
    (tmp_path / "snaps").mkdir()
    return tmp_path


def claude_ledger(env, nov_usd=36.13737, nov_calls=68):
    _write(env / "claude_spend.json", {
        "months": {
            "2026-10": {"usd": 0.49117, "calls": 11, "by": {"review": {"usd": 0.19659, "calls": 6}}},
            "2026-11": {"usd": nov_usd, "calls": nov_calls, "by": {
                "gap_radar_crowding": {"usd": 32.6837, "calls": 51},
                "gap_radar": {"usd": 2.06135, "calls": 2}}}},
        "last": {"what": "gap_radar_crowding", "made": "2026-11-05T06:33:42", "cost_usd": 0.99593}})


def render(env, made, cost, model="gpt-image-2.5-flare", quality="low", with_png=True):
    stem = f"pinocchio-single_{made.replace('-', '').replace(':', '').replace('T', '-')}"
    _write(env / "imagine" / f"{stem}.json", {"id": stem, "file": f"{stem}.png", "made": made, "model": model,
                                             "quality": quality, "size": "1024x1024", "cost_usd": cost,
                                             "decision": None, "release": "pinocchio-single"})
    if with_png:
        (env / "imagine" / f"{stem}.png").write_bytes(b"png")


def snapshot(env, stamp, requests):
    _write(env / "snaps" / f"snapshot_{stamp}.json", {
        "timestamp": stamp, "errors": [],
        "platforms": {"hikerapi": {"requests": requests, "balance": {"requests": requests, "rate": 11,
                                                                      "currency": "USD", "amount": requests / 1000}}}})


# ------------------------------------------------------------------ Claude

def test_claude_month_to_date_and_biggest_line_item(env):
    claude_ledger(env)
    row = spend.claude_row(NOW)
    assert row["service"] == "Claude API"
    assert row["mtd_usd"] == pytest.approx(36.137, abs=0.001)
    assert row["calls"] == 68
    assert row["biggest"].startswith("gap_radar_crowding $32.68")
    assert row["status"] == "ok"


def test_claude_last_30_days_is_months_only_never_a_guess(env):
    claude_ledger(env)
    row = spend.claude_row(NOW)
    assert row["last30_usd"] is None
    assert row["last30_note"] == "months only"


def test_claude_warns_at_70_percent_of_the_credit(env):
    claude_ledger(env, nov_usd=140.0)
    row = spend.claude_row(NOW)
    assert row["status"].startswith("warn")
    assert "70%" in row["status"]
    claude_ledger(env, nov_usd=139.99)
    assert spend.claude_row(NOW)["status"] == "ok"


def test_claude_without_a_ledger_says_not_logged(env):
    row = spend.claude_row(NOW)
    assert row["mtd_usd"] is None
    assert row["status"] == "not logged"


# ------------------------------------------------------------------ OpenAI / images

def test_image_renders_sum_month_and_last_30_days(env):
    render(env, "2026-10-14T03:33:43", 0.00739)          # 22 days before NOW: in the 30-day window, not this month
    render(env, "2026-11-03T22:00:00", 0.053, quality="medium")
    render(env, "2026-11-04T10:00:00", 0.211, model="gpt-image-2.5-sunburst", quality="high")
    render(env, "2026-09-01T10:00:00", 5.0)              # outside both windows
    row = spend.images_row(NOW)
    assert row["mtd_usd"] == pytest.approx(0.264, abs=0.001)
    assert row["last30_usd"] == pytest.approx(0.27139, abs=0.0001)
    assert row["calls"] == 2
    assert row["biggest"].startswith("gpt-image-2.5-sunburst high $0.21")
    assert row["status"] == "ok"


def test_image_renders_warn_over_15_dollars_a_month(env):
    for i in range(1, 8):
        render(env, f"2026-11-0{i}T10:00:00", 2.2, quality="high")
    row = spend.images_row(NOW)
    assert row["mtd_usd"] == pytest.approx(15.4, abs=0.001)
    assert row["status"].startswith("warn")
    assert "$15" in row["status"]


def test_image_record_without_its_png_is_skipped_like_imagine_does(env):
    render(env, "2026-11-03T22:00:00", 0.5, with_png=False)
    row = spend.images_row(NOW)
    assert row["mtd_usd"] == 0.0
    assert row["calls"] == 0


def test_raw_renders_are_counted_as_files_but_cost_is_not_logged(env):
    (env / "pinocchio-single").mkdir()
    for i in range(3):
        (env / "pinocchio-single" / f"x-{i}.png").write_bytes(b"png")
    row = spend.raw_renders_row(NOW)
    assert row["calls"] == 3
    assert row["mtd_usd"] is None and row["last30_usd"] is None
    assert row["status"] == "not logged"
    assert "3 files" in row["biggest"]


def test_openai_text_row_reads_its_monthly_ledger(env):
    _write(env / "openai_spend.json", {"months": {"2026-10": {"usd": 0.04489, "calls": 3, "by": {
        "bios": {"usd": 0.02258, "calls": 1}, "review": {"usd": 0.00619, "calls": 1}}}}, "last": {}})
    row = spend.openai_text_row(NOW)
    assert row["mtd_usd"] == 0.0            # nothing in November
    assert row["calls"] == 0
    assert row["last30_note"] == "months only"
    assert row["status"] == "ok"
    assert spend.openai_text_row(datetime(2026, 10, 30))["biggest"].startswith("bios $0.02")


# ------------------------------------------------------------------ HikerAPI

def test_hikerapi_balance_and_spend_from_snapshot_drops(env):
    snapshot(env, "2026-11-02T07-45-09", 84000)
    snapshot(env, "2026-11-03T07-45-09", 83851)
    snapshot(env, "2026-11-04T08-45-09", 83592)
    snapshot(env, "2026-11-05T08-45-10", 83421)
    row = spend.hikerapi_row(NOW)
    assert row["balance_usd"] == pytest.approx(83.421, abs=0.001)
    assert row["mtd_usd"] == pytest.approx(0.579, abs=0.0001)     # 579 requests at $0.001
    assert row["last30_usd"] == pytest.approx(0.579, abs=0.0001)
    assert row["calls"] == 579
    assert "11-04" in row["biggest"] and "259" in row["biggest"]
    assert row["status"] == "ok"


def test_hikerapi_top_up_is_not_counted_as_spend(env):
    snapshot(env, "2026-11-01T08-45-00", 0)
    snapshot(env, "2026-11-02T08-45-00", 84000)       # top-up: an increase
    snapshot(env, "2026-11-03T08-45-00", 83800)
    row = spend.hikerapi_row(NOW)
    assert row["calls"] == 200
    assert row["mtd_usd"] == pytest.approx(0.2, abs=0.0001)


def test_hikerapi_warns_under_10_dollars(env):
    snapshot(env, "2026-11-04T08-45-09", 9999)
    snapshot(env, "2026-11-05T08-45-10", 9990)
    row = spend.hikerapi_row(NOW)
    assert row["status"].startswith("warn")
    assert "$10" in row["status"]


def test_hikerapi_without_snapshots_says_not_logged(env):
    row = spend.hikerapi_row(NOW)
    assert row["balance_usd"] is None
    assert row["status"] == "not logged"


def test_hikerapi_old_snapshots_only_is_stale_not_a_guess(env):
    snapshot(env, "2026-09-20T08-45-00", 50000)
    snapshot(env, "2026-09-21T08-45-00", 49000)
    row = spend.hikerapi_row(NOW)
    assert row["balance_usd"] == pytest.approx(49.0)
    assert row["mtd_usd"] == 0.0 and row["last30_usd"] == 0.0
    assert "stale" in row["status"]


# ------------------------------------------------------------------ Gero, report, JSON

def test_gero_row_is_not_logged_until_a_ledger_exists(env):
    row = spend.gero_row(NOW)
    assert row["status"] == "not logged"
    assert row["mtd_usd"] is None


def test_gero_row_reads_a_ledger_in_the_same_shape_once_it_exists(env):
    _write(env / "gero" / "claude_spend.json", {"months": {"2026-11": {"usd": 3.0, "calls": 4, "by": {
        "seo": {"usd": 3.0, "calls": 4}}}}})
    row = spend.gero_row(NOW)
    assert row["mtd_usd"] == 3.0
    assert row["status"] == "ok"


def test_claude_credit_status_adds_gero_to_the_same_credit(env):
    claude_ledger(env, nov_usd=100.0)
    _write(env / "gero" / "claude_spend.json", {"months": {"2026-11": {"usd": 45.0, "calls": 4, "by": {}}}})
    rows = spend.build(NOW)["rows"]
    claude = next(r for r in rows if r["service"] == "Claude API")
    assert claude["status"].startswith("warn")          # 100 + 45 = 145 >= 140


def test_report_table_has_every_service_and_the_gaps(env):
    claude_ledger(env)
    snapshot(env, "2026-11-05T08-45-10", 83421)
    text = spend.render(spend.build(NOW))
    for name in ("Claude API", "OpenAI text", "Image renders", "Raw renders", "HikerAPI", "Gero key"):
        assert name in text
    assert "not logged" in text
    assert "months only" in text
    assert "--" not in text.replace("---", "")  # no em-dash stand-ins in copy


def test_json_writes_latest_and_backs_up_the_previous_one(env):
    claude_ledger(env)
    spend.write_json(spend.build(NOW))
    first = json.loads(spend.OUT_FILE.read_text())
    assert first["rows"][0]["service"] == "Claude API"
    assert not spend.OUT_FILE.with_suffix(".json.bak").exists()
    claude_ledger(env, nov_usd=50.0)
    spend.write_json(spend.build(NOW))
    bak = json.loads(spend.OUT_FILE.with_suffix(".json.bak").read_text())
    assert bak == first
    assert json.loads(spend.OUT_FILE.read_text())["rows"][0]["mtd_usd"] == 50.0


def test_build_carries_the_caps_and_warnings_list(env):
    claude_ledger(env, nov_usd=150.0)
    snapshot(env, "2026-11-05T08-45-10", 5000)
    out = spend.build(NOW)
    assert out["caps"] == {"claude_credit_usd": 200.0, "claude_warn_pct": 70, "openai_images_month_usd": 15.0,
                           "hikerapi_min_balance_usd": 10.0}
    assert len(out["warnings"]) == 2
    assert out["made"].startswith("2026-11-05")


def test_main_prints_the_table_without_writing(env, capsys):
    claude_ledger(env)
    spend.main([], NOW)
    out = capsys.readouterr().out
    assert "Claude API" in out
    assert not spend.OUT_FILE.exists()
    spend.main(["--json"], NOW)
    assert spend.OUT_FILE.exists()
