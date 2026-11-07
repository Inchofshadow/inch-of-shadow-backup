"""Home (RM 2.0 slice 10): the four blocks of section 1b, the social links, and the backup/drive footer (Machine-14)."""
from release_manager import score_board
from release_manager.webapp import app, _dashboard_lines


def test_lines_have_the_four_parts():
    lines = _dashboard_lines()
    assert set(lines) == {"next", "board", "backup", "drive"}
    assert lines["board"] and lines["board"]["total"] >= lines["board"]["done"] > 0
    assert lines["backup"] and lines["backup"]["date"] >= "2026-09-24"
    html = app.test_client().get("/").get_data(as_text=True)
    assert "Next release" in html and "Last backup" in html and "Photo drive" in html
    # backup and drive are the footer: after the four blocks and the social links
    assert html.index("Social Links") < html.index("Last backup") < html.index("Photo drive")


def test_home_shows_the_verdict_line_from_the_score_board(monkeypatch):
    line = "OFF PACE, 2/9 GREEN, 1 DRIFTING, 1 RED, 5 COLLECTING"
    monkeypatch.setattr(score_board, "build", lambda *a, **k: {"score": {"line": line}})
    html = app.test_client().get("/").get_data(as_text=True)
    assert line in html
    block = html[html.index('id="home-verdict"'):html.index('id="home-now"')]
    assert 'href="/stats"' in block and line in block


def test_home_blocks_appear_in_order():
    html = app.test_client().get("/").get_data(as_text=True)
    heads = ["<h2>Score board</h2>", "<h2>🔥 Now</h2>", "<h2>Decisions waiting on Amir</h2>",
             "<h2>Next release</h2>", "<h2>Social Links</h2>"]
    pos = [html.index(h) for h in heads]
    assert pos == sorted(pos)
