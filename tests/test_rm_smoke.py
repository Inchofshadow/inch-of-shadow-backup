"""RM smoke guard (RM 2.0 slice 2, plans/strategy/rm2-dry-run-2026-11-06.md): every HTML page answers 200 or 302.

The page list comes from app.url_map: GET rules with no arguments, minus /static, /api/* and SKIP.
Pages that need a release slug are listed by hand (SLUG_PAGES). While a page renders, shelling out,
the network and any file write raise, so the test runs nothing and changes no real data file.
"""
import builtins
import io
import os
import socket
import subprocess

import pytest

import video_resizer  # noqa: F401  its import runs `ffmpeg -version` once; done here, before the no-shell-out guard
import release_manager.webapp as w
from release_manager.webapp import app

SLUG = "pinocchio-single"   # exists in releases/

SKIP = {
    "/favicon.ico": "file response, not a page",
    "/edit/preview": "image response, not a page (needs ?src=)",
    "/shoot/pfp": "file response (the profile PNG), not a page",
}

SLUG_PAGES = [
    f"/release/{SLUG}",
    f"/release/{SLUG}/edit",
    f"/release/{SLUG}/track/new",
    f"/release/{SLUG}/track/1/edit",
    f"/playground/{SLUG}",
    f"/playground/{SLUG}/layout",
    f"/playground/{SLUG}/wall",
    f"/playground/{SLUG}/elements",
    f"/playground/{SLUG}/colours",
    f"/playground/{SLUG}/ig-grid",
    f"/artwork-resizer?release={SLUG}",
    f"/seo-copy?release={SLUG}",
]

PAGES_TODAY = 22   # slice 3, 2026-11-06: /words added. Was 21 after slice 1 (/palette, /autopilot, /promotion dropped, and /engagement, skipped before); a dropped route lowers this on purpose


def _url_map_pages():
    out = []
    for r in app.url_map.iter_rules():
        if "GET" not in r.methods or r.arguments or r.endpoint == "static" or r.rule.startswith("/api/"):
            continue
        if r.rule not in SKIP:
            out.append(r.rule)
    return sorted(out)


def _edit_src():
    """/edit 404s without ?src=; open it on the first artwork file, as test_photo_editor_page does."""
    art = next(p.name for p in sorted(w.ARTWORK_DIR.iterdir()) if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    return f"/edit?src=artwork:{art}"


def _all_pages():
    return [_edit_src() if u == "/edit" else u for u in _url_map_pages()] + SLUG_PAGES


@pytest.fixture
def guarded(monkeypatch):
    """No shell-outs, no network, no file writes while a page renders."""
    def no_shell(*a, **k):
        raise RuntimeError(f"smoke test: page tried to shell out: {a[:1]}")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, no_shell)

    def no_net(*a, **k):
        raise RuntimeError("smoke test: page tried to open a network connection")

    monkeypatch.setattr(socket.socket, "connect", no_net)
    monkeypatch.setattr(socket, "create_connection", no_net)

    real_open = builtins.open

    def read_only_open(file, mode="r", *a, **k):
        if any(c in mode for c in "wax+"):
            raise RuntimeError(f"smoke test: page tried to write {file}")
        return real_open(file, mode, *a, **k)

    def no_move(*a, **k):
        raise RuntimeError(f"smoke test: page tried to move a file: {a[:2]}")

    monkeypatch.setattr(builtins, "open", read_only_open)
    monkeypatch.setattr(io, "open", read_only_open)
    monkeypatch.setattr(os, "replace", no_move)
    monkeypatch.setattr(os, "rename", no_move)
    return app.test_client()


@pytest.mark.parametrize("url", _all_pages())
def test_page_answers(guarded, url):
    r = guarded.get(url)
    assert r.status_code in (200, 302), f"{url} -> {r.status_code}"


def test_page_count_has_not_dropped():
    pages = _url_map_pages()
    assert len(pages) >= PAGES_TODAY, f"{len(pages)} pages, expected at least {PAGES_TODAY}: {pages}"


def test_every_skip_is_a_real_route():
    rules = {r.rule for r in app.url_map.iter_rules()}
    assert set(SKIP) <= rules, f"stale SKIP entries: {sorted(set(SKIP) - rules)}"
