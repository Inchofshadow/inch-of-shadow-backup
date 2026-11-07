"""The shared Claude call helper (G-08 F4): request shape, stop reasons, reading by block type."""

import json
from types import SimpleNamespace

import pytest

from release_manager import claude_api


class Fake:
    def __init__(self, stop="end_turn"):
        self.calls, self.stop = [], stop
        self.messages = self

    def create(self, **kw):
        self.calls.append(kw)
        return SimpleNamespace(content=[SimpleNamespace(type="thinking", thinking=""),
                                        SimpleNamespace(type="text", text="hello "),
                                        SimpleNamespace(type="text", text="world")],
                               stop_reason=self.stop, usage=SimpleNamespace(input_tokens=1000, output_tokens=100))


def test_ask_sends_effort_schema_and_fallback_and_reads_text_blocks():
    c = Fake()
    m = claude_api.ask(c, max_tokens=10, system="s", messages=[{"role": "user", "content": "u"}],
                       effort="low", schema={"type": "object"})
    kw = c.calls[0]
    assert kw["model"] == "claude-opus-5-5" and kw["max_tokens"] == 10
    assert kw["output_config"] == {"effort": "low", "format": {"type": "json_schema", "schema": {"type": "object"}}}
    assert kw["extra_body"] == {"fallbacks": "default"}
    assert kw["extra_headers"] == {"anthropic-beta": claude_api.FALLBACK_BETA}
    assert claude_api.text_of(m) == "hello world"
    assert claude_api.usage_of(m) == {"input_tokens": 1000, "output_tokens": 100,
                                      "cost_usd": pytest.approx(1000 * 4e-6 + 100 * 20e-6)}


def test_ask_without_schema_sends_effort_only():
    c = Fake()
    claude_api.ask(c, max_tokens=10, system="s", messages=[], effort="medium")
    assert c.calls[0]["output_config"] == {"effort": "medium"}


@pytest.mark.parametrize("stop,needle", [("refusal", "declined this review"), ("max_tokens", "ran out of tokens")])
def test_ask_raises_our_own_error_on_refusal_and_cut_off(stop, needle):
    with pytest.raises(claude_api.ClaudeError, match=needle):
        claude_api.ask(Fake(stop), max_tokens=10, system="s", messages=[], effort="low", what="review")


def test_client_needs_the_key(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    with pytest.raises(claude_api.ClaudeError, match="ANTHROPIC_API_KEY"):
        claude_api.client(tmp_path / "no.env")


def test_every_call_lands_in_the_monthly_ledger():
    claude_api.ask(Fake(), max_tokens=10, system="s", messages=[], effort="low", what="review")
    claude_api.ask(Fake(), max_tokens=10, system="s", messages=[], effort="low", what="bios")
    s = claude_api.month_spend()
    assert s["calls"] == 2 and s["usd"] == pytest.approx(2 * (1000 * 4e-6 + 100 * 20e-6), abs=1e-4)
    assert s["limit"] == claude_api.LIMIT_USD and claude_api.limit_note() == ""
    led = json.loads(claude_api.LEDGER.read_text())
    assert set(led["months"][s["month"]]["by"]) == {"review", "bios"}


def test_nothing_is_sent_once_the_month_hits_the_limit(monkeypatch):
    monkeypatch.setattr(claude_api, "LIMIT_USD", 0.01)
    c = Fake()
    for _ in range(3):
        try:
            claude_api.ask(c, max_tokens=10, system="s", messages=[], effort="low")
        except claude_api.LimitReached:
            break
    assert len(c.calls) == 2                       # the third call was refused before sending
    note = claude_api.limit_note()
    assert note.startswith("Monthly Claude API limit reached") and "LIMIT_USD" in note
    with pytest.raises(claude_api.LimitReached):
        claude_api.ask(c, max_tokens=10, system="s", messages=[], effort="low")
    assert len(c.calls) == 2
