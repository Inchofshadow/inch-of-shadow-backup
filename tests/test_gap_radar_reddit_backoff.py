"""GR-10: Reddit 429 back-off and skip-with-reason, all HTTP mocked."""
import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gap_radar"))
import gap_radar as g  # noqa: E402

FEED = b'<feed xmlns="http://www.w3.org/2005/Atom"></feed>'


class FakeResp:
    def __init__(self, status):
        self.status_code, self.content = status, FEED

    def raise_for_status(self):
        if self.status_code >= 400:
            e = requests.HTTPError(str(self.status_code))
            e.response = self
            raise e


@pytest.fixture
def fake_http(monkeypatch):
    calls, waits = [], []
    monkeypatch.setattr(g.time, "sleep", lambda s: waits.append(s))

    def install(statuses):
        it = iter(statuses)

        def fake_get(url, **kw):
            calls.append(url.split("/r/")[1].split("/")[0])
            return FakeResp(next(it))
        monkeypatch.setattr(g.requests, "get", fake_get)
    return install, calls, waits


def test_one_429_then_ok_keeps_the_sub(fake_http, capsys):
    install, calls, waits = fake_http
    install([429, 200])
    g.reddit(subs=["ableton"], phrases=["x"])
    assert calls == ["ableton", "ableton"]
    assert 60 in waits
    assert "skipped" not in capsys.readouterr().out


def test_two_blocked_subs_in_a_row_stop_reddit_with_reason(fake_http, capsys):
    install, calls, waits = fake_http
    install([200] + [429] * 6)
    g.reddit(subs=["synth", "djs", "goth", "berlin", "techno"], phrases=["x"])
    out = capsys.readouterr().out
    assert "berlin" not in calls and "techno" not in calls
    assert 60 in waits and 180 in waits
    assert "r/djs: skipped, still 429 after back-off" in out
    assert "skipping the last 2 subs this run: berlin, techno" in out
    assert "reason: 429" in out


def test_ok_sub_resets_the_blocked_count(fake_http, capsys):
    install, calls, _ = fake_http
    install([429, 429, 429, 200, 429, 429, 429, 200])
    g.reddit(subs=["djs", "synth", "goth", "techno"], phrases=["x"])
    assert calls[-1] == "techno"
    assert "rate-limited" not in capsys.readouterr().out


def test_other_http_error_skips_sub_short_line(fake_http, capsys):
    install, calls, _ = fake_http
    install([500, 200])
    g.reddit(subs=["djs", "synth"], phrases=["x"])
    out = capsys.readouterr().out
    assert "r/djs: skipped, HTTP 500" in out
    assert "https://" not in out
    assert calls == ["djs", "synth"]
