"""Tests for the live-driver identity gate added 2026-07-05 (audit P1-6).

Before this fix build_live_driver() loaded cookies from .env and started
acting with no check of WHOSE session it was (finding 19; wrong-profile
incident 2026-06-10).
"""
import pytest

import scene_intelligence.ig_live_driver as d


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("IG_SESSION_ID", "fake-session")
    monkeypatch.setenv("IG_CSRF_TOKEN", "fake-csrf")
    monkeypatch.setenv("IG_USER_ID", "111")


def test_correct_identity_returns_driver(creds, monkeypatch):
    monkeypatch.setattr(d, "verify_session",
                        lambda s, c: {"username": "inch_of_shadow", "pk": "111"})
    driver = d.build_live_driver()
    assert isinstance(driver, d.RequestsBrowserDriver)


def test_wrong_username_refuses(creds, monkeypatch):
    monkeypatch.setattr(d, "verify_session",
                        lambda s, c: {"username": "someone_else", "pk": "111"})
    with pytest.raises(SystemExit, match="IDENTITY CHECK FAILED"):
        d.build_live_driver()


def test_unverifiable_identity_fails_closed(creds, monkeypatch):
    # verify_session's attempt-4 path: valid session, unknown identity
    monkeypatch.setattr(d, "verify_session",
                        lambda s, c: {"username": "", "pk": ""})
    with pytest.raises(SystemExit, match="UNVERIFIABLE"):
        d.build_live_driver()


def test_pk_mismatch_refuses(creds, monkeypatch):
    monkeypatch.setattr(d, "verify_session",
                        lambda s, c: {"username": "inch_of_shadow", "pk": "999"})
    with pytest.raises(SystemExit, match="does not\n?.*match IG_USER_ID"):
        d.build_live_driver()


def test_missing_pk_allowed_on_username_match(creds, monkeypatch):
    # HTML-parse path can return username without pk - username match suffices
    monkeypatch.setattr(d, "verify_session",
                        lambda s, c: {"username": "inch_of_shadow", "pk": ""})
    driver = d.build_live_driver()
    assert isinstance(driver, d.RequestsBrowserDriver)
