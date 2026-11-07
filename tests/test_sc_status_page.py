"""SC status page (RM 2.0 slice 4, SC chat answer 2026-11-06): /sc-automation is a read-only status
view; the run route and the test-auth route are gone, and the page carries no button that calls them."""
import pytest


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("FLASK_SECRET_KEY", "test")
    from release_manager.webapp import app
    app.config["TESTING"] = True
    return app.test_client()


def test_run_and_test_auth_routes_are_gone_and_status_page_renders(client):
    assert client.post("/api/sc-automation/run", json={"dry_run": True}).status_code == 404
    assert client.get("/api/sc-automation/test-auth").status_code == 404

    r = client.get("/sc-automation")
    assert r.status_code == 200
    html = r.data.decode()
    assert "Read-only status" in html and "Follow Tracker" in html
    for gone in ("/api/sc-automation/run", "/api/sc-automation/test-auth", "testAuth(", "runEngine("):
        assert gone not in html, gone
