"""System 72: the one daily brief (stats/daily_brief.py) over fixture files."""
import json
from datetime import date

import pytest

from stats import daily_brief as db

REAL_SPEND_WARNINGS = db.spend_warnings  # the env fixture stubs it; the fallback test calls the real one
D = date(2026, 11, 5)  # a Thursday: not an IG session day
IG_DAY = date(2026, 11, 4)  # a Wednesday: IG session day


def _w(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _j(p, data):
    _w(p, json.dumps(data))


@pytest.fixture
def env(tmp_path, monkeypatch):
    root = tmp_path
    monkeypatch.setattr(db, "ROOT", root)
    monkeypatch.setattr(db, "REPORTS", root / "docs" / "reports")
    monkeypatch.setattr(db, "SI", root / "si")
    monkeypatch.setattr(db, "SNAPS", root / "snaps")
    monkeypatch.setattr(db, "TARGETS", root / "targets.json")
    monkeypatch.setattr(db, "BOARDS", (root / "tickets.json", root / "cp-tickets.json"))
    monkeypatch.setattr(db, "STATE_FILE", root / "snaps" / "daily_brief_state.json")
    monkeypatch.setattr(db, "HANDOVER", root / "system.md")
    monkeypatch.setattr(db, "S4A_FILE", root / "snaps" / "spotify_s4a.json")
    monkeypatch.setattr(db, "SPEND_LATEST", root / "snaps" / "spend_latest.json")
    monkeypatch.setattr(db, "IG_TOKEN_STATE", root / "ig_token_state.json")
    monkeypatch.setattr(db, "DISPATCH_LOG", root / "docs" / "reports" / "dispatch-log.md")
    monkeypatch.setattr(db, "spend_warnings", lambda d: [])

    _w(root / "docs" / "reports" / "loop-close-sc-2026-11-05.md",
       "# SC loop\n\n**Score: 10/10**\n\nLogged actions: sc_follow: 20, sc_like: 30, sc_unfollow: 32\n")
    _w(root / "si" / "sc_session_report_20261105.md",
       "No challenge, no popup, no login prompt. No detection event written.\n\n"
       "## 16:15 sweep run 2 of 3\n\nAll unfollows verified. No CHURN ALERT.\n")
    _w(root / "docs" / "reports" / "dispatch-log.md",
       "- 2026-11-05T09:31:13 \u2014 **run: contact re-enrichment (provider)** \u2014 exit 0\n")
    _j(root / "snaps" / "snapshot_2026-11-05T20-17-25.json",
       {"timestamp": "2026-11-05T20:17:25",
        "platforms": {"instagram": {"followers": 971}, "soundcloud": {"followers": 473, "following": 445}}})
    _j(root / "snaps" / "spotify_s4a.json",
       {"weeks": {"2026-10-19": {"monthly_active": 115}, "2026-11-02": {"monthly_active": 94}}})
    _j(root / "snaps" / "spend_latest.json", {"made": "2026-11-05T20:15:08", "warnings": []})
    _j(root / "ig_token_state.json", {"issued": "2026-11-04", "expires": "2027-01-03"})
    _j(root / "targets.json", {"metrics": {
        "ig_followers": {"kind": "ladder", "source": "snapshot:instagram.followers",
                         "rungs": {"2026-11-30": 996, "2026-12-31": 1026}},
        "sc_followers": {"kind": "ladder", "source": "snapshot:soundcloud.followers",
                         "rungs": {"2026-11-30": 510, "2026-12-31": 600}},
        "spotify_monthly_active": {"kind": "ladder", "source": "s4a:weeks.monthly_active",
                                   "rungs": {"2026-11-30": 90, "2026-12-31": 110}},
        "email_list": {"kind": "ladder", "label": "Email list", "source": "manual:email_list.subscribers",
                       "rungs": {"2026-12-31": 50}},
        "tiktok_followers": {"kind": "collecting", "source": "manual:tiktok.followers"},
    }})
    _j(root / "tickets.json", {"tickets": [
        {"id": "R-02", "area": "Release", "area_no": 2, "bucket": "now", "who": "amir", "chrome": False,
         "label": "HTN cover", "status": "in-progress"},
        {"id": "R-07", "area": "Release", "area_no": 9, "bucket": "now", "who": "amir", "chrome": True,
         "label": "Symphonic submit", "status": "waiting"},
        {"id": "BC-06", "area": "Socials", "area_no": 14, "bucket": "now", "who": "amir", "chrome": False,
         "label": "Bandcamp Friday", "status": "in-progress"},
        {"id": "G-14", "area": "Socials", "area_no": 29, "bucket": "now", "who": "claude", "chrome": True,
         "label": "SoundCloud inbox replies", "status": "waiting"},
        {"id": "ST-01", "area": "Studio", "area_no": 1, "bucket": "next", "who": "amir", "chrome": False,
         "label": "MPC programs", "status": "proposed"},
        {"id": "OLD", "area": "Income", "area_no": 1, "bucket": "now", "who": "amir", "chrome": False,
         "label": "Closed one", "status": "done"},
    ]})
    _j(root / "cp-tickets.json", {"tickets": [
        {"id": "Machine-99", "area": "System", "area_no": 61, "bucket": "now", "who": "claude", "chrome": False,
         "label": "Board refresh", "status": "in-progress"},
    ]})
    return root


def test_quiet_day_has_no_problems_block_and_the_right_blocks(env):
    text = db.build(D)
    lines = text.splitlines()
    assert lines[0] == "Inch of Shadow · Thu 11-05"
    assert "🔴" not in text and "💶 Spend" not in text
    assert "🔥 Now" in text
    assert "   🎵 Release 2 · HTN cover 🙋 · 9 · Symphonic submit 🙋🌐" in lines
    assert "   🎬 Socials 14 · Bandcamp Friday 🙋 · 29 · SoundCloud inbox replies 🎃🌐" in lines
    assert "   ⚙️ System 61 · Board refresh 🎃" in lines  # second board merged
    assert "Studio" not in text and "Closed one" not in text  # nothing Now / done tickets left out
    assert "🎯 Nov 30   IG 971 → 996 · SC 473 → 510 · Spotify listeners 94 (rung 90 ✅)" in lines
    assert "Email list" not in text  # manual source: no reading, so no entry
    assert "🤖 Ran today   IG ⏸ · SC ✅ 10/10 · sweep ✅ · dispatch ✅ · stats ✅ · spend ✅" in lines
    assert "🙋 Waiting on you today: 3 · HTN cover · Symphonic submit · Bandcamp Friday" in lines
    assert len([ln for ln in lines if ln.strip()]) <= 12
    assert "\u2014" not in text  # no em-dashes


def test_problems_come_first(env):
    (env / "docs" / "reports" / "loop-close-sc-2026-11-05.md").unlink()
    _w(env / "docs" / "reports" / "dispatch-log.md",
       "- 2026-11-05T09:31:13 \u2014 **notify-amir** \u2014 engagement_log.json at 1637KB > 1500KB \u2014 schedule the archival job\n"
       "- 2026-11-03T22:30:25 \u2014 **watchdog** \u2014 ALERT \u2014 TEST SUITE RED: 5 failed, 1058 passed\n"
       "- 2026-11-04T22:30:27 \u2014 **watchdog** \u2014 ALERT \u2014 TEST SUITE RED: 1 failed, 1080 passed\n")
    _j(env / "ig_token_state.json", {"issued": "2026-09-10", "expires": "2026-11-08"})
    board = json.loads((env / "tickets.json").read_text())
    board["tickets"].append({"id": "M-01", "area": "Socials", "area_no": 2, "bucket": "next", "who": "amir",
                             "chrome": True, "label": "YouTube login renewal", "status": "waiting",
                             "blocked_on": "Login expired ~2026-10-28 (last renewal 10-21). Amir runs yt_auth.py"})
    _j(env / "tickets.json", board)
    text = db.build(D)
    lines = text.splitlines()
    assert lines[2] == "🔴 Problems"
    red = "\n".join(lines[3:lines.index("🔥 Now")])
    assert "SC: no session logged" in red
    assert "🎬 Socials 2 · YouTube login renewal · Login expired ~2026-10-28" in red
    assert "engagement_log.json at 1637KB > 1500KB · schedule the archival job" in red
    assert "Test suite red 2 nights (11-04: 1 failed, 1080 passed)" in red
    assert "IG Graph token expires in 3 days (2026-11-08)" in red
    assert "\u2014" not in text
    assert "🤖 Ran today   IG ⏸ · SC ❌ · sweep ✅" in text


def test_ig_session_day_without_a_log_is_red_and_halts_are_red(env):
    text = db.build(IG_DAY)
    assert "IG session day, nothing logged" in text and "IG ❌" in text
    _w(env / "docs" / "reports" / "loop-close-ig-2026-11-04.md",
       "# IG loop\n\n**Score: 10/10**\n\nActions: ig_follow: 16, ig_like: 22, session_halt: 1\n")
    text = db.build(IG_DAY)
    assert "IG session halted (popup or safety stop)" in text and "IG ✅ 10/10" in text


def test_detection_words_are_red_only_without_a_no_before_them(env):
    _w(env / "si" / "sc_session_report_20261105.md",
       "No challenge, no popup. A CAPTCHA slider appeared at 10:12 and was cleared by Amir.\n")
    text = db.build(D)
    assert "SC CAPTCHA · scene_intelligence/sc_session_report_20261105.md" in text
    assert "SC challenge" not in text


def test_default_run_writes_nothing_and_write_saves_brief_and_state(env):
    db.build(D)
    assert not (env / "docs" / "reports" / "daily-brief-2026-11-05.md").exists()
    assert not db.STATE_FILE.exists()
    text = db.build(D, write=True)
    assert (env / "docs" / "reports" / "daily-brief-2026-11-05.md").read_text() == text + "\n"
    state = json.loads(db.STATE_FILE.read_text())
    assert state["reds"] == {"2026-11-05": []} and state["updated"] == "2026-11-05"
    assert not (env / "system.md").exists()  # no repeat, no proposal


def test_red_repeat_marks_ticket_and_proposes_once(env):
    _w(env / "docs" / "reports" / "dispatch-log.md",
       "- 2026-11-05T09:31:13 \u2014 **notify-amir** \u2014 engagement_log.json at 1637KB > 1500KB \u2014 schedule the archival job\n")
    _j(db.STATE_FILE, {"reds": {"2026-11-04": ["engagement_log.json at 1609KB > 1500KB · schedule the archival job"]},
                       "proposed": {}})
    _w(env / "system.md", "# System handover\n\n## Spend\nsomething\n")
    text = db.build(D)  # print only: marker shown, nothing written
    assert "   engagement_log.json at 1637KB > 1500KB · schedule the archival job → ticket" in text
    assert "Proposed from the brief" not in (env / "system.md").read_text()

    db.build(D, write=True)
    hand = (env / "system.md").read_text()
    assert hand.count("## Proposed from the brief") == 1
    assert ("- 2026-11-05 · proposed ⚙️ System ticket · engagement_log.json at 1637KB > 1500KB · "
            "schedule the archival job · red on 11-04 and 11-05") in hand
    assert "\u2014" not in hand
    state = json.loads(db.STATE_FILE.read_text())
    assert state["reds"]["2026-11-05"] == ["engagement_log.json at 1637KB > 1500KB · schedule the archival job"]
    assert list(state["proposed"]) == ["engagement_log.json at #KB > #KB · schedule the archival job"]

    db.build(D, write=True)  # second run the same evening: no duplicate proposal
    assert (env / "system.md").read_text().count("proposed ⚙️ System ticket") == 1


def test_proposals_land_inside_an_existing_section_not_at_the_file_end(env):
    _w(env / "docs" / "reports" / "dispatch-log.md",
       "- 2026-11-05T09:31:13 \u2014 **notify-amir** \u2014 provider balance low: 0 requests left\n")
    _j(db.STATE_FILE, {"reds": {"2026-11-04": ["provider balance low: 0 requests left"]}, "proposed": {}})
    _w(env / "system.md", "# System handover\n\n## Proposed from the brief\nExplainer line.\n- 2026-11-01 · older one\n\n"
                          "## Later section\nkeep me last\n")
    db.build(D, write=True)
    hand = (env / "system.md").read_text()
    assert hand.index("- 2026-11-01 · older one") < hand.index("- 2026-11-05 · proposed") < hand.index("## Later section")
    assert hand.endswith("## Later section\nkeep me last\n")


def test_a_red_line_seen_once_gets_no_marker(env):
    _w(env / "docs" / "reports" / "dispatch-log.md",
       "- 2026-11-05T09:31:13 \u2014 **notify-amir** \u2014 provider balance low: 0 requests left\n")
    _j(db.STATE_FILE, {"reds": {"2026-11-03": ["provider balance low: 0 requests left"]}, "proposed": {}})
    text = db.build(D, write=True)
    assert "provider balance low: 0 requests left" in text and "→ ticket" not in text
    assert not (env / "system.md").exists()


def test_targets_stale_snapshot_and_missing_board(env):
    (env / "snaps" / "snapshot_2026-11-05T20-17-25.json").unlink()
    _j(env / "snaps" / "snapshot_2026-11-02T08-45-00.json",
       {"timestamp": "2026-11-02T08:45:00",
        "platforms": {"instagram": {"followers": 971}, "soundcloud": {"followers": 473, "following": 445}}})
    text = db.build(D)
    assert "IG 971 → 996 (stale, read 11-02)" in text and "stats ✅" not in text   # daily source, window 24 h
    _j(env / "snaps" / "snapshot_2026-11-05T08-45-00.json",   # a newer snapshot that skipped Instagram: the 11-02 reading stands
       {"timestamp": "2026-11-05T08:45:00",
        "platforms": {"instagram": {"skipped": "HikerAPI 429"}, "soundcloud": {"followers": 480, "following": 445}}})
    text = db.build(D)
    assert "IG 971 → 996 (stale, read 11-02)" in text and "SC 480 → 510" in text
    (env / "targets.json").unlink()
    assert "🎯" not in db.build(D)


def test_spend_line_only_when_spend_warns(env, monkeypatch):
    monkeypatch.setattr(db, "spend_warnings", lambda d: ["HikerAPI: warn: balance $8.20 under $10"])
    text = db.build(D)
    assert text.splitlines()[-1] == "💶 Spend ⚠️ HikerAPI: warn: balance $8.20 under $10 · python3 stats/spend.py"


def test_spend_warnings_fall_back_to_the_written_page(env, monkeypatch):
    import sys
    import stats
    _j(env / "snaps" / "spend_latest.json", {"made": "2026-11-05T20:15:08", "warnings": ["Claude API: warn: 72%"]})
    monkeypatch.setitem(sys.modules, "stats.spend", None)  # import fails -> read spend_latest.json
    monkeypatch.delattr(stats, "spend", raising=False)  # even when another test imported it first
    assert REAL_SPEND_WARNINGS(D) == ["Claude API: warn: 72%"]


def test_main_prints_and_write_flag(env, capsys):
    assert db.main(["2026-11-05"]) == 0
    assert capsys.readouterr().out.startswith("Inch of Shadow · Thu 11-05")
    db.main(["2026-11-05", "--write"])
    assert (env / "docs" / "reports" / "daily-brief-2026-11-05.md").exists()
