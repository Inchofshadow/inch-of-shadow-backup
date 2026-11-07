"""Control Panel Board: ticket file validation, view model, seed, route."""
import json
from pathlib import Path

import pytest

from release_manager.board import (
    BoardError, build_view, effective_status, load_board, validate,
)

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "plans" / "control-panel" / "tickets.json"


def ticket(**over):
    base = {
        "id": "Look-01", "lane": "Control Panel", "category": "Look", "floor": 1,
        "title": "Type system", "why": "w", "serves": "s", "question": "q",
        "status": "proposed", "blocked_on": [], "size": "S", "references": [],
        "decision": "", "decided_on": "", "outputs": [], "notes": [],
    }
    base.update(over)
    return base


def board(*tickets):
    return {"version": 1, "updated": "2026-09-13",
            "deadline": {"floors": [1, 2], "date": "2026-09-20"},
            "tickets": list(tickets)}


def test_valid_minimal_board_has_no_errors():
    assert validate(board(ticket())) == []


@pytest.mark.parametrize("field", ["why", "serves", "question"])
def test_missing_core_field_is_an_error(field):
    t = ticket(); t[field] = ""
    errs = validate(board(t))
    assert any(field in e and "Look-01" in e for e in errs)


def test_bad_status_is_an_error():
    errs = validate(board(ticket(status="maybe")))
    assert any("status" in e for e in errs)


def test_bad_category_is_an_error():
    errs = validate(board(ticket(category="Vibes")))
    assert any("category" in e for e in errs)


def test_id_prefix_must_match_category():
    errs = validate(board(ticket(id="Words-01", category="Look")))
    assert any("id must be Look-NN" in e for e in errs)


@pytest.mark.parametrize("bad_id", ["Look-1", "Look-001", "Look-0\"1"])
def test_id_format_rejects_non_two_digit_ids(bad_id):
    errs = validate(board(ticket(id=bad_id)))
    assert any("id must be Look-NN" in e for e in errs)


def test_id_format_accepts_two_digit_id():
    errs = validate(board(ticket(id="Look-00")))
    assert not any("id must be" in e for e in errs)


def test_blocked_on_non_list_is_one_error_not_per_character():
    errs = validate(board(ticket(blocked_on="Look-01")))
    matches = [e for e in errs if "blocked_on" in e]
    assert matches == ["Look-01: blocked_on must be a list"]


def test_lane_must_match_category():
    errs = validate(board(ticket(lane="Marketing")))
    assert any("lane" in e for e in errs)


def test_duplicate_id_is_an_error():
    errs = validate(board(ticket(), ticket()))
    assert any("duplicate" in e for e in errs)


def test_dangling_blocked_on_is_an_error():
    errs = validate(board(ticket(blocked_on=["Look-99"])))
    assert any("Look-99" in e for e in errs)


def test_floor_must_be_1_to_6():
    errs = validate(board(ticket(floor=9)))
    assert any("floor" in e for e in errs)


def test_load_board_raises_on_invalid_file(tmp_path):
    p = tmp_path / "t.json"
    p.write_text(json.dumps(board(ticket(status="nope"))))
    with pytest.raises(BoardError):
        load_board(p)


def test_load_board_raises_on_corrupt_json(tmp_path):
    p = tmp_path / "t.json"
    p.write_text("{not json")
    with pytest.raises(BoardError):
        load_board(p)


def test_load_board_returns_data(tmp_path):
    p = tmp_path / "t.json"
    p.write_text(json.dumps(board(ticket())))
    assert load_board(p)["tickets"][0]["id"] == "Look-01"


def test_load_board_raises_on_non_object_top_level(tmp_path):
    p = tmp_path / "t.json"
    p.write_text("[]")
    with pytest.raises(BoardError):
        load_board(p)


def test_effective_status_blocked_when_parent_not_done():
    parent = ticket(id="Look-01", status="proposed")
    child = ticket(id="Look-02", status="proposed", blocked_on=["Look-01"])
    by_id = {t["id"]: t for t in (parent, child)}
    assert effective_status(child, by_id) == "blocked"
    assert effective_status(parent, by_id) == "proposed"


def test_effective_status_unblocks_when_parent_done():
    parent = ticket(id="Look-01", status="done")
    child = ticket(id="Look-02", status="approved", blocked_on=["Look-01"])
    by_id = {t["id"]: t for t in (parent, child)}
    assert effective_status(child, by_id) == "approved"


def test_done_stays_done_even_if_blocked_on_open():
    parent = ticket(id="Look-01", status="proposed")
    child = ticket(id="Look-02", status="done", blocked_on=["Look-01"])
    by_id = {t["id"]: t for t in (parent, child)}
    assert effective_status(child, by_id) == "done"


def test_build_view_has_six_floors_in_order_and_current_floor():
    data = board(
        ticket(id="Look-01", floor=1, status="done"),
        ticket(id="Look-02", floor=2, status="proposed", blocked_on=["Look-01"]),
        ticket(id="Formats-01", category="Formats", floor=3, status="proposed",
               blocked_on=["Look-02"]),
    )
    view = build_view(data)
    assert [f["n"] for f in view["floors"]] == [1, 2, 3, 4, 5, 6]
    assert view["floors"][0]["name"] == "Foundation"
    assert view["floors"][0]["after"] is None and view["floors"][1]["after"] == 1
    assert view["current_floor"] == 2
    assert [f["is_current"] for f in view["floors"]] == [False, True, False, False, False, False]


def test_build_view_cards_carry_needs_unblocks_and_counts():
    data = board(
        ticket(id="Look-01", floor=1, status="proposed"),
        ticket(id="Look-02", floor=2, status="proposed", blocked_on=["Look-01"]),
    )
    view = build_view(data)
    f1, f2 = view["floors"][0], view["floors"][1]
    assert f1["tickets"][0]["unblocks"] == ["Look-02"]
    assert f2["tickets"][0]["needs"] == ["Look-01"]
    assert f2["tickets"][0]["status"] == "blocked"
    assert view["counts"] == {"proposed": 1, "approved": 0, "in-progress": 0,
                              "blocked": 1, "done": 0}
    assert view["waiting_on_amir"] == 1
    assert view["deadline"]["date"] == "2026-09-20"


def test_category_slug():
    from release_manager.board import category_slug
    assert category_slug("Ads and data") == "ads-and-data"
    assert category_slug("Look") == "look"


def test_build_view_categories_ordered_control_panel_then_marketing():
    data = board(
        ticket(id="Formats-01", category="Formats", floor=3),
        ticket(id="Look-01", floor=1),
        ticket(id="Mkt-01", category="Campaign", lane="Marketing", floor=6),
    )
    view = build_view(data)
    assert view["categories"] == [
        {"name": "Look", "slug": "look"},
        {"name": "Formats", "slug": "formats"},
        {"name": "Campaign", "slug": "campaign"},
    ]


def test_board_css_disables_hidden_attribute_override():
    css_path = ROOT / "release_manager" / "static" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".board-page [hidden] { display: none !important; }" in css


# The ticket file is a living document: tickets get added and closed every day.
# These tests check the rules the page depends on, not a frozen list of ids or statuses.
SEED_IDS = {
    "Words-01", "Words-03", "Look-00", "Look-01", "Look-03", "Look-04", "Look-08",
    "Words-02", "Look-02", "Look-05", "Look-06", "Look-09", "Look-07",
    "Formats-01", "Formats-02", "Formats-03", "Formats-04",
    "Machine-01", "Machine-02", "Look-10", "Machine-03", "Machine-04",
    "Mkt-01",
    "Formats-05", "Measure-01", "Machine-05",
}


def test_seed_file_is_valid_and_complete():
    data = load_board(SEED)
    ids = {t["id"] for t in data["tickets"]}
    # Since 2026-11-06 done tickets leave the board (Amir) and live in tickets-done-archive.json
    # next to it; the 09-13 seed stays a subset of board + archive, never lost.
    archive = json.loads(SEED.with_name("tickets-done-archive.json").read_text(encoding="utf-8"))
    archived = {t["id"] for t in archive["tickets"]}
    assert not (ids & archived), ids & archived
    assert SEED_IDS <= ids | archived, SEED_IDS - (ids | archived)
    for t in data["tickets"]:
        assert t["why"] and t["serves"] and t["question"], t["id"]


def test_seed_statuses_and_current_floor():
    data = load_board(SEED)
    view = build_view(data)
    raw = {t["id"]: t for t in data["tickets"]}
    cards = [c for f in view["floors"] for c in f["tickets"]]
    for c in cards:
        t = raw[c["id"]]
        open_deps = [d for d in t.get("blocked_on") or [] if raw[d]["status"] != "done"]
        if t["status"] == "done":
            assert c["status"] == "done", c["id"]
        elif open_deps:
            assert c["status"] == "blocked", c["id"]
        else:
            assert c["status"] == t["status"], c["id"]
    open_floors = [c["floor"] for c in cards if c["status"] != "done"]
    assert view["current_floor"] == (min(open_floors) if open_floors else 6)
    assert view["deadline"] == (data.get("deadline") or {})


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("FLASK_SECRET_KEY", "test")
    from release_manager.webapp import app
    app.config["TESTING"] = True
    return app.test_client()


def test_board_route_renders_every_seed_ticket(client):
    r = client.get("/board")
    assert r.status_code == 200
    html = r.data.decode()
    open_ids = {t["id"] for t in load_board(SEED)["tickets"]}
    for tid in SEED_IDS & open_ids:          # done seed tickets sit in the archive, not on the page
        assert tid in html
    assert "Foundation" in html and "Marketing" in html


def test_board_route_shows_derived_blocked_status(client):
    html = client.get("/board").data.decode()
    data = load_board(SEED)
    raw = {t["id"]: t for t in data["tickets"]}
    derived = [t["id"] for t in data["tickets"]
               if t["status"] not in ("done", "blocked")
               and any(raw[d]["status"] != "done" for d in t.get("blocked_on") or [])]
    if not derived:
        pytest.skip("no ticket is currently blocked by an open dependency")
    # stored as proposed/approved, but a dependency is still open, so the page shows blocked
    assert f'data-id="{derived[0]}" data-status="blocked"' in html


def test_board_route_has_plan_link_in_sidebar(client):
    html = client.get("/board").data.decode()
    assert 'href="/board"' in html


def test_board_route_detail_section_still_hidden(client):
    html = client.get("/board").data.decode()
    assert '<section class="tdetail" id="tdetail" hidden>' in html


def test_board_route_has_category_chip_and_card_attribute(client):
    html = client.get("/board").data.decode()
    assert 'data-filter="cat:look"' in html
    assert 'data-cat="look"' in html


# --- the ticket shape shared with plans/tickets.json (System 78, 2026-11-06) ---

def test_seed_control_panel_tickets_pass_the_shared_shape_check():
    """board.py validates the Control Panel fields; the loop fields (bucket, who, label,
    next_step, metric, updated, done_means, no em-dash, no stored priority) are checked
    by release_manager.tickets so both boards fail the same way."""
    from release_manager.tickets import _check_loop_fields, check_now_cap, metric_keys
    data = load_board(SEED)
    keys = metric_keys()
    for t in data["tickets"]:
        assert _check_loop_fields(t["id"], t, keys) == [], t["id"]
    assert check_now_cap(data["tickets"]) == []
