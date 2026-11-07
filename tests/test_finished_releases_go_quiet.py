"""Refresh step 3 (audit 2026-09-26, findings 2 and 3): a release long past its date raises no overdue items."""
from release_manager.timeline import is_finished, QUIET_AFTER_DAYS
from release_manager.webapp import app
import release_manager.views.release as release_view   # Home lives here since RM 2.0 slice 7 (home.html since slice 10)


def test_is_finished_only_after_the_quiet_window():
    rel = {"release_date": "2026-07-10"}
    assert not is_finished(rel, today="2026-07-20")
    assert not is_finished(rel, today="2026-08-09")            # day 30 exactly is still live
    assert is_finished(rel, today="2026-08-10")
    assert not is_finished({"release_date": ""}, today="2026-09-26")
    assert not is_finished({}, today="2026-09-26")


def test_dashboard_and_autopilot_ignore_finished_releases(monkeypatch):
    old = {"slug": "old", "metadata": {"title": "Old", "artist": "x", "release_type": "Single"},
           "release_date": "2026-01-01", "distribution": {},
           "timeline": [{"id": "t", "label": "Release day", "date": "2026-01-01", "done": False, "weeks_before": 0}],
           "checklist": [{"id": "c", "label": "Old task", "category": "metadata", "done": False, "due_date": "2025-12-20", "done_date": "", "notes": ""}],
           "tracks": []}
    fresh = dict(old, slug="new", release_date="2099-01-01",
                 timeline=[{"id": "t", "label": "Release day", "date": "2026-01-01", "done": False, "weeks_before": 0}],
                 checklist=[{"id": "c", "label": "New task", "category": "metadata", "done": False, "due_date": "2025-12-20", "done_date": "", "notes": ""}])
    monkeypatch.setattr(release_view, "list_releases", lambda: [old, fresh])
    monkeypatch.setattr(release_view, "artwork_url_for", lambda slug: None)
    c = app.test_client()
    dash = c.get("/").get_data(as_text=True)
    assert "Release day" in dash                                 # the fresh release's overdue milestone is in the overdue list
    assert "New task" in dash and "Old task" not in dash          # the overdue list sits in Home's release block
    out = dash[dash.index("<summary>Out: 1</summary>"):]
    assert "Old" in out and "Out since 2026-01-01" in out          # the finished release is quiet, under Out


def test_home_lists_a_finished_release_under_out_since_not_next():
    from release_manager.webapp import app
    from release_manager.storage import list_releases
    from release_manager.timeline import is_finished
    finished = [r for r in list_releases() if is_finished(r)]
    html = app.test_client().get("/").get_data(as_text=True)
    for r in finished:
        assert f"Out since {r['release_date']}" in html
