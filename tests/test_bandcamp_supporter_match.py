"""bandcamp_supporter_match.py (BC-10): notes parsing, local-only matching, status order.

Synthetic files only, in tmp_path. No network.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scene_intelligence"))

import bandcamp_supporter_match as bsm  # noqa: E402


NOTES = """# title
Run the match: ignored text above the first block
## https://someartist.bandcamp.com/album/one
> a note line
Mira Leo
Dark Fan - https://bandcamp.com/darkfan99
abc
## https://other.bandcamp.com/track/two
https://bandcamp.com/darkfan99
Nobody Known
"""


def test_parse_notes_merges_people_across_releases():
    people = bsm.parse_notes(NOTES)
    by_name = {p["name"]: p for p in people}
    assert set(by_name) == {"Mira Leo", "Dark Fan", "Nobody Known"}  # 'abc' is too short
    fan = by_name["Dark Fan"]
    assert fan["bandcamp_user"] == "darkfan99"
    assert fan["releases"] == ["https://someartist.bandcamp.com/album/one",
                               "https://other.bandcamp.com/track/two"]


def test_norm_joins_name_styles():
    assert bsm.norm("Mira Leo") == bsm.norm("mira.leo") == bsm.norm("MIRA_LEO") == "miraleo"


def _write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _fixture_dirs(tmp_path: Path):
    si = tmp_path / "si"
    data = tmp_path / "data"
    _write(si / "enriched_contacts.json", [
        {"name": "Nobody Known", "category": "dj", "email": "nk@example.com"},
    ])
    _write(si / "ig_enriched_contacts.json", [])
    _write(si / "ig_follower_roster.json", [])
    _write(si / "sc_follow_tracker.json", {"follows": [
        {"name": "darkfan99", "url": "https://soundcloud.com/darkfan99?utm_source=x", "followed_back": False},
    ]})
    conn = data / "instagram-inch_of_shadow-2026-10-10-X" / "connections" / "followers_and_following"
    _write(conn / "followers_1.json", [
        {"string_list_data": [{"href": "https://www.instagram.com/mira.leo", "value": "mira.leo"}]},
    ])
    _write(conn / "following.json", {"relationships_following": []})
    # an older export must be ignored
    _write(data / "instagram-inch_of_shadow-2026-01-01-OLD" / "connections" / "followers_and_following"
           / "followers_1.json", [{"string_list_data": [{"value": "nobodyknown"}]}])
    return si, data


def test_match_statuses_and_order(tmp_path):
    si, data = _fixture_dirs(tmp_path)
    idx = bsm.build_index(si, data)
    assert idx.sources["ig_export_dir"] == "instagram-inch_of_shadow-2026-10-10-X"
    rows = bsm.match(bsm.parse_notes(NOTES), idx)
    status = {r["name"]: r["status"] for r in rows}
    assert status == {"Mira Leo": "already_follows_us_ig",
                      "Dark Fan": "in_sc_tracker",
                      "Nobody Known": "in_si"}
    assert [r["name"] for r in rows] == ["Mira Leo", "Dark Fan", "Nobody Known"]
    assert all(r["verify"] for r in rows)


def test_unknown_name_is_no_match(tmp_path):
    si, data = _fixture_dirs(tmp_path)
    rows = bsm.match([{"name": "Totally New Person", "bandcamp_user": "", "releases": ["r"]}],
                     bsm.build_index(si, data))
    assert rows[0]["status"] == "no_match" and rows[0]["matches"] == [] and not rows[0]["verify"]


def test_mailing_list_email_matches_si_and_is_not_written_out(tmp_path):
    si, data = _fixture_dirs(tmp_path)
    csv_path = tmp_path / "ml.csv"
    csv_path.write_text("email,fullname,country\nNK@example.com,Someone Else,DE\n", encoding="utf-8")
    people = bsm.parse_mailing_list(csv_path)
    rows = bsm.match(people, bsm.build_index(si, data))
    assert rows[0]["email_in_si"] is True and rows[0]["status"] == "in_si"
    assert "_email" not in rows[0]
    assert "nk@example.com" not in json.dumps(rows).lower()
    assert "_key" not in rows[0]


def test_mailing_list_without_name_never_shows_email_part(tmp_path):
    si, data = _fixture_dirs(tmp_path)
    csv_path = tmp_path / "ml.csv"
    csv_path.write_text("email,fullname\nmira.leo@example.com,\n", encoding="utf-8")
    rows = bsm.match(bsm.parse_mailing_list(csv_path), bsm.build_index(si, data))
    assert rows[0]["status"] == "already_follows_us_ig"          # matched through the email user part
    assert "mira" not in json.dumps(rows[0]["name"]).lower()
    assert "example" not in json.dumps(rows).lower()


def test_main_dry_run_writes_nothing(tmp_path, monkeypatch, capsys):
    si, data = _fixture_dirs(tmp_path)
    notes = tmp_path / "notes.md"
    notes.write_text(NOTES, encoding="utf-8")
    out = tmp_path / "out.json"
    monkeypatch.setattr(bsm, "build_index", lambda: bsm.Index())
    assert bsm.main(["--notes", str(notes), "--out", str(out), "--dry-run"]) == 0
    assert not out.exists()
    assert "check the real profile" in capsys.readouterr().out
