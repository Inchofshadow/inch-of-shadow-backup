"""Machine-23: Claude subject sharpener on the Imagine page (fake client, nothing sent)."""

import json
from types import SimpleNamespace

import pytest

from release_manager import imagine_subject as sh


class FakeClient:
    def __init__(self, reply, stop="end_turn"):
        self.calls, self.reply, self.stop = [], reply, stop
        self.messages = self

    def create(self, **kw):
        self.calls.append(kw)
        return SimpleNamespace(
            content=[SimpleNamespace(type="thinking", thinking=""),
                     SimpleNamespace(type="text", text=json.dumps(self.reply))],
            stop_reason=self.stop, usage=SimpleNamespace(input_tokens=1500, output_tokens=120))


GOOD = {"subject": "A single pale rose on a wet black stone ledge at night — close up, low in the frame.",
        "why": "Added light, distance and placement."}


def test_sharpen_sends_subject_and_full_prompt_and_cleans_dashes():
    c = FakeClient(GOOD)
    out = sh.sharpen("  a rose on stone ", "USE: cover\n\nCONSTRAINTS:\n- No domes.", "cover", client=c)
    kw = c.calls[0]
    assert kw["model"] == "claude-opus-5-5" and kw["output_config"]["effort"] == "low"
    assert kw["output_config"]["format"]["type"] == "json_schema"
    assert kw["extra_body"] == {"fallbacks": "default"}
    text = kw["messages"][0]["content"]
    assert "a rose on stone" in text and "No domes." in text
    assert "—" not in out["subject"] and out["subject"].startswith("A single pale rose")
    assert out["cost_usd"] == pytest.approx(1500 * 4e-6 + 120 * 20e-6)


@pytest.mark.parametrize("subject", ["", "   ", "x" * 2501])
def test_empty_or_long_subject_is_refused_before_any_call(subject):
    c = FakeClient(GOOD)
    with pytest.raises(sh.SharpenError):
        sh.sharpen(subject, "USE: cover", client=c)
    assert c.calls == []


@pytest.mark.parametrize("stop,reply", [("refusal", GOOD), ("end_turn", {"subject": " ", "why": ""})])
def test_refusal_and_empty_answer_raise(stop, reply):
    with pytest.raises(sh.SharpenError):
        sh.sharpen("a rose", "USE: cover", client=FakeClient(reply, stop=stop))


def test_route_returns_suggestion_and_errors(monkeypatch):
    from release_manager import webapp
    monkeypatch.setattr(sh, "_client", lambda: FakeClient(GOOD))
    app = webapp.app
    app.config["WTF_CSRF_ENABLED"] = False
    c = app.test_client()
    r = c.post("/imagine/sharpen", json={"kind": "cover", "subject": "a rose on stone"})
    j = r.get_json()
    assert r.status_code == 200 and j["subject"].startswith("A single pale rose") and "why" in j
    r = c.post("/imagine/sharpen", json={"kind": "cover", "subject": ""})
    assert r.status_code == 400 and not r.get_json()["ok"]


@pytest.mark.parametrize("raw,want", [
    ("a flock of 10\u201312 ravens", "a flock of 10-12 ravens"),
    ("a rose on stone \u2014 close up", "a rose on stone, close up"),
    ("about 2 \u2013 3 metres away", "about 2-3 metres away"),
    ('"quoted"', "quoted"),
])
def test_clean_keeps_number_ranges_and_drops_other_dashes(raw, want):
    assert sh._clean(raw) == want
