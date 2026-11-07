import re
"""Tickets page: plans/tickets.json validation, view model, seed, route."""
import json
from pathlib import Path

import pytest

from release_manager.tickets import (
    TicketsError, build_view, load_tickets, validate, SECTIONS, PRIORITIES,
    BUCKETS, BUCKET_PRIORITY, NOW_CAP, WHO, _check_loop_fields, check_now_cap, metric_keys,
)

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "plans" / "tickets.json"


def ticket(**over):
    base = {
        "id": "R-01", "section": "Release", "lane": "Release", "bucket": "now", "who": "claude",
        "title": "Pinocchio metadata", "why": "w", "helps": "h", "status": "approved", "blocked_on": "",
        "due": "", "size": "S", "notes": [], "label": "EP metadata", "next_step": "n",
        "metric": "release_engagement_d28", "updated": "2026-11-06", "done_means": "d", "done_means_by": "claude",
    }
    base.update(over)
    return base


def doc(*tickets):
    return {"version": 1, "updated": "2026-09-14", "tickets": list(tickets)}


def test_valid_minimal_file_has_no_errors():
    assert validate(doc(ticket())) == []


@pytest.mark.parametrize("field", ["id", "section", "title", "why", "helps", "status"])
def test_missing_required_field_is_an_error(field):
    t = ticket()
    del t[field]
    assert any(field in e for e in validate(doc(t)))


def test_bad_status_is_an_error():
    assert any("status" in e for e in validate(doc(ticket(status="maybe"))))


def test_bad_section_is_an_error():
    assert any("section" in e for e in validate(doc(ticket(section="Control Panel"))))


def test_stored_priority_is_an_error():
    # one axis since 2026-11-06: bucket is the priority, P1-P3 is derived for the page only
    errs = validate(doc(ticket(priority="P1")))
    assert any("priority is derived from bucket" in e for e in errs)


def test_duplicate_id_is_an_error():
    assert any("duplicate" in e for e in validate(doc(ticket(), ticket())))


def test_notes_must_be_a_list():
    assert any("notes" in e for e in validate(doc(ticket(notes="x"))))


def test_load_rejects_invalid_file(tmp_path):
    p = tmp_path / "t.json"
    p.write_text(json.dumps(doc(ticket(status="bad"))), encoding="utf-8")
    with pytest.raises(TicketsError):
        load_tickets(p)


def test_load_rejects_unreadable_file(tmp_path):
    with pytest.raises(TicketsError):
        load_tickets(tmp_path / "missing.json")


def test_view_sections_in_fixed_order_and_priority_sorted():
    data = doc(
        ticket(id="M-01", section="Maintenance", bucket="parked", lane="IG"),
        ticket(id="R-02", bucket="next", due="2026-09-28"),
        ticket(id="R-03", bucket="now", due="2026-10-01"),
        ticket(id="R-01", bucket="now", due="2026-09-20"),
        ticket(id="G-01", section="General", bucket="next", lane=""),
    )
    view = build_view(data)
    assert [s["name"] for s in view["sections"]] == list(SECTIONS)
    release = next(s for s in view["sections"] if s["name"] == "Release")
    assert [t["id"] for t in release["tickets"]] == ["R-01", "R-03", "R-02"]


def test_view_hides_done_from_counts_but_keeps_cards():
    data = doc(ticket(id="R-01", status="done"), ticket(id="R-02", bucket="now"),
               ticket(id="R-03", bucket="next", due="2026-09-28"))
    view = build_view(data)
    assert view["open_count"] == 2
    assert view["p1_count"] == 1
    assert view["next_due"] == {"date": "2026-09-28", "id": "R-03"}
    release = next(s for s in view["sections"] if s["name"] == "Release")
    assert len(release["tickets"]) == 3
    assert release["open_count"] == 2


def test_view_next_due_none_when_no_dates():
    view = build_view(doc(ticket()))
    assert view["next_due"] is None


def test_priorities_are_three_levels():
    assert tuple(PRIORITIES) == ("P1", "P2", "P3")


def test_card_priority_is_derived_from_bucket():
    assert BUCKET_PRIORITY == {"now": "P1", "next": "P2", "parked": "P3", "routine": "P3"}
    view = build_view(doc(ticket(id="R-01", bucket="now"), ticket(id="R-02", bucket="routine"),
                          ticket(id="R-03", status="done", bucket="")))
    cards = {c["id"]: c for s in view["sections"] for c in s["tickets"]}
    assert cards["R-01"]["priority"] == "P1" and cards["R-01"]["priority_label"] == "now"
    assert cards["R-02"]["priority"] == "P3" and cards["R-02"]["bucket"] == "routine"
    assert cards["R-03"]["priority"] == "P3"          # a done ticket needs no bucket
    assert view["now_count"] == 1 and view["p1_count"] == 1
    assert cards["R-01"]["done_means"] == "d" and cards["R-01"]["done_means_by"] == "claude"


# --- the ticket shape (System 78, 2026-11-06): one axis, done_means, cap --------

@pytest.mark.parametrize("field", ["bucket", "who", "label", "next_step", "metric", "updated", "done_means"])
def test_open_ticket_missing_shape_field_is_an_error(field):
    t = ticket()
    del t[field]
    errs = validate(doc(t))
    assert any(field in e and "R-01" in e for e in errs), errs


@pytest.mark.parametrize("field", ["bucket", "who", "label", "next_step"])
def test_done_ticket_needs_no_bucket_who_label_next_step(field):
    t = ticket(status="done")
    del t[field]
    assert validate(doc(t)) == []


@pytest.mark.parametrize("field", ["metric", "updated", "done_means"])
def test_done_ticket_still_needs_metric_updated_done_means(field):
    t = ticket(status="done")
    del t[field]
    assert any(field in e for e in validate(doc(t)))


def test_bad_bucket_is_an_error():
    assert tuple(BUCKETS) == ("now", "next", "parked", "routine")
    assert any("bucket" in e for e in validate(doc(ticket(bucket="soon"))))


def test_bad_who_is_an_error():
    assert tuple(WHO) == ("amir", "claude", "auto")
    assert any("who" in e for e in validate(doc(ticket(who="fable"))))


def test_metric_must_be_a_targets_key_or_none():
    assert any("not a plans/targets.json key" in e for e in validate(doc(ticket(metric="ig_likes"))))
    assert validate(doc(ticket(metric="ig_followers"))) == []
    assert validate(doc(ticket(metric="ig_likes")), keys={"ig_likes"}) == []     # explicit key set


def test_done_means_must_be_one_line_by_amir_or_claude():
    assert any("done_means" in e for e in validate(doc(ticket(done_means="two\nlines"))))
    assert any("done_means_by" in e for e in validate(doc(ticket(done_means_by="gpt"))))
    assert validate(doc(ticket(done_means_by="amir"))) == []


@pytest.mark.parametrize("field,value", [
    ("why", "a \u2014 b"), ("next_step", "x \u2014 y"), ("done_means", "d \u2014 e"), ("notes", ["ok", "no \u2014 way"]),
])
def test_em_dash_in_any_text_field_is_an_error(field, value):
    errs = validate(doc(ticket(**{field: value})))
    assert any("em-dash" in e and field in e for e in errs), errs


def test_now_cap_fails_with_the_area_name():
    many = [ticket(id=f"G-{i}", bucket="now", area="Socials", area_no=i) for i in range(NOW_CAP + 1)]
    errs = check_now_cap(many)
    assert len(errs) == 1 and "Socials" in errs[0] and str(NOW_CAP) in errs[0]
    assert any("Socials" in e for e in validate(doc(*many)))
    many[-1]["status"] = "done"
    assert check_now_cap(many) == []           # done tickets do not count
    assert check_now_cap([ticket(id=f"G-{i}", bucket="now", area="Socials") for i in range(NOW_CAP)]) == []


def test_metric_keys_reads_targets_and_survives_a_missing_file(tmp_path):
    assert "ig_followers" in metric_keys()
    assert metric_keys(tmp_path / "missing.json") is None


SEEDS = [ROOT / "plans" / "tickets.json", ROOT / "plans" / "control-panel" / "tickets.json"]


def _seed_tickets(path):
    return json.loads(path.read_text(encoding="utf-8"))["tickets"]


@pytest.mark.parametrize("seed", SEEDS)
def test_seed_every_ticket_passes_the_shape_check(seed):
    keys = metric_keys()
    for t in _seed_tickets(seed):
        assert _check_loop_fields(t["id"], t, keys) == [], t["id"]


@pytest.mark.parametrize("seed", SEEDS)
def test_seed_every_open_ticket_has_the_seven_fields(seed):
    for t in _seed_tickets(seed):
        if t["status"] == "done":
            continue
        for f in ("bucket", "who", "label", "next_step", "metric", "updated", "done_means"):
            assert str(t.get(f, "")).strip(), (t["id"], f)
        assert t["bucket"] in BUCKETS and t["who"] in WHO, t["id"]


@pytest.mark.parametrize("seed", SEEDS)
def test_seed_every_ticket_has_done_means_and_no_stored_priority(seed):
    for t in _seed_tickets(seed):
        assert t["done_means"].strip() and "\n" not in t["done_means"], t["id"]
        assert t.get("done_means_by") in ("amir", "claude"), t["id"]
        assert "priority" not in t, t["id"]


def test_seed_max_three_now_per_area_across_both_boards():
    tickets = [t for seed in SEEDS for t in _seed_tickets(seed)]
    assert check_now_cap(tickets) == []


@pytest.mark.parametrize("seed", SEEDS)
def test_seed_has_no_em_dash_anywhere(seed):
    assert "\u2014" not in seed.read_text(encoding="utf-8")


@pytest.mark.parametrize("seed", SEEDS)
def test_seed_fields_describe_the_shape(seed):
    data = json.loads(seed.read_text(encoding="utf-8"))
    assert {"bucket", "who", "label", "next_step", "done_means", "done_means_by"} <= set(data["fields"])
    assert "One axis" in data["area_rule"] and "done_means" in data["area_rule"]
    assert "priorities" not in data


def test_tickets_route_detail_shows_done_means_and_next_step(client):
    html = client.get("/tickets").data.decode()
    assert 'id="d-done"' in html and 'id="d-next"' in html
    assert 'id="d-done"' in client.get("/tickets?group=metric").data.decode()


# --- seed file -------------------------------------------------------------

def test_seed_file_is_valid():
    data = load_tickets(SEED)
    assert data["tickets"]


def test_seed_has_no_control_panel_tickets():
    data = load_tickets(SEED)
    for t in data["tickets"]:
        assert not t["id"].startswith(("Look-", "Words-", "Formats-", "Machine-", "Measure-", "Mkt-", "B-"))


def test_seed_covers_todays_open_release_tickets():
    ids = {t["id"] for t in load_tickets(SEED)["tickets"]}
    assert {"R-01", "R-02", "R-03", "R-04", "R-05", "R-06"} <= ids


# --- route -----------------------------------------------------------------

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("FLASK_SECRET_KEY", "test")
    from release_manager.webapp import app
    app.config["TESTING"] = True
    return app.test_client()


def test_tickets_route_renders_every_seed_ticket(client):
    r = client.get("/tickets")
    assert r.status_code == 200
    html = r.data.decode()
    for t in load_tickets(SEED)["tickets"]:
        assert f'data-id="{t["id"]}"' in html
    for s in SECTIONS:
        assert s in html


def test_tickets_route_orders_sections_and_priorities(client):
    html = client.get("/tickets").data.decode()
    assert html.index('data-section="General"') < html.index('data-section="Release"') < html.index('data-section="Maintenance"')
    assert html.index('data-id="R-01"') < html.index('data-id="R-05"')


def test_tickets_route_links_into_control_panel_board(client):
    html = client.get("/tickets").data.decode()
    assert 'id="cp-block"' in html
    assert 'href="/board"' in html


def test_tickets_route_control_panel_block_shows_board_counts(client):
    html = client.get("/tickets").data.decode()
    assert 'id="cp-open"' in html and 'id="cp-floor"' in html


def test_sidebar_has_tickets_link_on_board_and_board_links_back(client):
    html = client.get("/board").data.decode()
    assert 'href="/tickets"' in html


def test_tickets_route_survives_broken_board_file(client, monkeypatch):
    import release_manager.views.work as w   # the route lives in views/work.py (RM 2.0 slice 4)
    monkeypatch.setattr(w, "CONTROL_PANEL_FILE", Path("/nonexistent/tickets.json"))
    r = client.get("/tickets")
    assert r.status_code == 200
    assert "board unavailable" in r.data.decode()


def test_seed_every_ticket_has_short_why_and_helps():
    for t in load_tickets(SEED)["tickets"]:
        assert t["why"].strip() and t["helps"].strip()
        assert len(t["why"]) <= 220 and len(t["helps"]) <= 220, t["id"]
        assert "\u2014" not in t["why"] + t["helps"], t["id"]


def test_tickets_route_detail_shows_why_and_helps(client):
    html = client.get("/tickets").data.decode()
    assert 'id="d-why"' in html and 'id="d-helps"' in html
    first = load_tickets(SEED)["tickets"][0]
    assert first["helps"] in html  # carried in the embedded card data


# --- one loop: metric + updated, the by-number view (System 75) -------------

from release_manager.tickets import (   # noqa: E402
    NO_METRIC, area_label, build_metric_view, control_panel_cards, metric_readings,
)

CP_SEED = ROOT / "plans" / "control-panel" / "tickets.json"
TARGETS = ROOT / "plans" / "targets.json"


def _metric_keys():
    return set(json.loads(TARGETS.read_text(encoding="utf-8"))["metrics"])


def test_metric_none_without_note_is_an_error():
    assert any("metric_note" in e for e in validate(doc(ticket(metric="none"))))
    assert validate(doc(ticket(metric="none", metric_note="no number moved here"))) == []


def test_bad_updated_date_is_an_error():
    assert any("updated" in e for e in validate(doc(ticket(updated="5.11.2026"))))
    assert validate(doc(ticket(updated="2026-11-05"))) == []


@pytest.mark.parametrize("seed", [SEED, CP_SEED])
def test_seed_every_ticket_names_its_metric_and_updated(seed):
    keys = _metric_keys()
    for t in json.loads(seed.read_text(encoding="utf-8"))["tickets"]:
        assert t["metric"] in keys or t["metric"] == NO_METRIC, t["id"]
        if t["metric"] == NO_METRIC:
            assert 3 <= len(t["metric_note"].split()) <= 7, (t["id"], t["metric_note"])
            assert "—" not in t["metric_note"]
        else:
            assert "metric_note" not in t, t["id"]
        assert re.fullmatch(r"20\d\d-\d\d-\d\d", t["updated"]), t["id"]


@pytest.mark.parametrize("seed", [SEED, CP_SEED])
def test_seed_fields_and_area_rule_describe_the_loop(seed):
    data = json.loads(seed.read_text(encoding="utf-8"))
    assert {"metric", "metric_note", "updated"} <= set(data["fields"])
    assert "metric" in data["area_rule"] and "group=metric" in data["area_rule"]


def test_area_label_shows_emoji_area_and_number():
    areas = {"Socials": "\U0001F3AC Socials"}
    assert area_label({"id": "BC-06", "area": "Socials", "area_no": 14}, areas) == "\U0001F3AC Socials 14"
    assert area_label({"id": "X-01", "area": "", "area_no": ""}, areas) == "X-01"


def _readings():
    return {
        "ig_followers": {"label": "IG followers", "unit": "followers", "kind": "ladder", "value": "966",
                         "as_of": "2026-11-02", "rung": "996", "rung_date": "2026-11-30", "floor": "", "proposed": False},
        "sc_followers": {"label": "SoundCloud followers", "unit": "followers", "kind": "ladder", "value": "",
                         "as_of": "", "rung": "510", "rung_date": "2026-11-30", "floor": "", "proposed": False},
    }


def test_metric_view_groups_open_tickets_in_targets_order_none_last():
    data = doc(
        ticket(id="G-12", metric="ig_followers", bucket="now", area="Socials", area_no=27),
        ticket(id="G-01", metric="ig_followers", bucket="parked", area="Socials", area_no=1),
        ticket(id="G-15", metric="none", metric_note="backup no number moved", bucket="next"),
        ticket(id="M-13", metric="ig_followers", status="done"),
        ticket(id="R-01", metric="release_engagement_d28"),
    )
    data["areas"] = {"Socials": "\U0001F3AC Socials"}
    view = build_metric_view(data, _readings())
    keys = [g["key"] for g in view["groups"]]
    assert keys == ["ig_followers", "sc_followers", "release_engagement_d28", "none"]
    ig = view["groups"][0]
    assert ig["value"] == "966" and ig["rung"] == "996" and ig["rung_date"] == "2026-11-30"
    assert [t["id"] for t in ig["tickets"]] == ["G-12", "G-01"]      # now before parked, done dropped
    assert ig["tickets"][0]["shown_as"] == "\U0001F3AC Socials 27"
    assert view["groups"][1]["open_count"] == 0
    assert view["groups"][-1]["label"] == "No number"
    assert view["open_count"] == 4 and view["none_count"] == 1


def test_metric_view_takes_control_panel_cards():
    cp = {"tickets": [
        {"id": "Formats-04", "title": "TikTok formats", "why": "w", "serves": "s", "status": "in-progress",
         "area": "System", "area_no": 24, "bucket": "parked", "who": "amir", "metric": "tiktok_followers"},
        {"id": "Look-01", "title": "Type", "why": "w", "serves": "s", "status": "done", "metric": "none"},
    ]}
    extra = control_panel_cards(cp)
    assert [c["id"] for c in extra] == ["Formats-04"] and extra[0]["board"] == "control-panel"
    view = build_metric_view(doc(ticket(metric="ig_followers")), _readings(), extra)
    tiktok = next(g for g in view["groups"] if g["key"] == "tiktok_followers")
    assert tiktok["tickets"][0]["id"] == "Formats-04"
    assert "not in targets" in tiktok["label"]      # readings had no tiktok row


def test_metric_readings_cover_every_target_without_raising():
    from stats.targets import load_targets
    readings = metric_readings(load_targets(TARGETS))
    assert set(readings) == _metric_keys()
    for key, r in readings.items():
        assert r["label"] and set(r) >= {"value", "rung", "rung_date", "floor", "kind", "proposed"}
    ig = readings["ig_followers"]
    assert ig["kind"] == "ladder" and ig["rung"] and ig["rung_date"].startswith("2026-")


def test_tickets_route_by_metric_groups_both_boards(client):
    r = client.get("/tickets?group=metric")
    assert r.status_code == 200
    html = r.data.decode()
    assert 'data-group="ig_followers"' in html and 'data-group="none"' in html
    assert html.index('data-group="ig_followers"') < html.index('data-group="none"')
    assert 'data-id="G-12"' in html and 'data-id="Formats-04"' in html
    assert "\U0001F3AC Socials 27" in html            # tickets shown as emoji + area + number
    assert "rung " in html and "IG followers" in html
    for t in load_tickets(SEED)["tickets"]:
        if t["status"] == "done":
            assert f'data-id="{t["id"]}"' not in html


def test_tickets_route_default_view_unchanged_and_links_by_number(client):
    html = client.get("/tickets").data.decode()
    assert 'data-section="General"' in html and 'data-group=' not in html
    assert 'href="/tickets?group=metric"' in html


def test_tickets_route_by_metric_survives_broken_board_file(client, monkeypatch):
    import release_manager.views.work as w   # the route lives in views/work.py (RM 2.0 slice 4)
    monkeypatch.setattr(w, "CONTROL_PANEL_FILE", Path("/nonexistent/tickets.json"))
    r = client.get("/tickets?group=metric")
    assert r.status_code == 200 and 'data-id="G-12"' in r.data.decode()
