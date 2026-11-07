"""The two copy writers on Opus 5.5 (G-04): the reply is read by block type, refusals and
cut-offs raise, the request carries effort and the server-side fallback. Fake client, nothing sent."""

import json
from types import SimpleNamespace

import anthropic
import pytest

from release_manager import bio_manager, seo_copy_generator


class FakeAnthropic:
    """Stands in for anthropic.Anthropic: records the request, answers with a thinking block first."""
    calls: list = []
    reply: dict = {}
    stop: str = "end_turn"

    def __init__(self, api_key=None):
        self.messages = self

    def create(self, **kw):
        FakeAnthropic.calls.append(kw)
        return SimpleNamespace(
            content=[SimpleNamespace(type="thinking", thinking=""),
                     SimpleNamespace(type="text", text=json.dumps(FakeAnthropic.reply))],
            stop_reason=FakeAnthropic.stop,
            usage=SimpleNamespace(input_tokens=3000, output_tokens=900))


@pytest.fixture
def fake(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(anthropic, "Anthropic", FakeAnthropic)
    FakeAnthropic.calls, FakeAnthropic.reply, FakeAnthropic.stop = [], {}, "end_turn"
    return FakeAnthropic


RELEASE = {"slug": "test-song", "release_date": "2026-11-06",
           "metadata": {"title": "Test Song", "artist": "Inch of Shadow", "release_type": "Single",
                        "genre_primary": "post-punk"},
           "tracks": [{"title": "Test Song", "bpm": 110, "key": "A minor"}]}


def test_seo_writer_reads_text_blocks_and_sends_effort_and_fallback(fake):
    fake.reply = {"spotify_pitch": "A pitch.", "spotify_artist_pick": "A pick."}
    out = seo_copy_generator.generate_copy(RELEASE, ["spotify"], "authentic")
    kw = fake.calls[0]
    assert kw["model"] == "claude-opus-5-5"
    assert kw["output_config"] == {"effort": "medium"}
    assert kw["extra_body"] == {"fallbacks": "default"}
    assert kw["extra_headers"] == {"anthropic-beta": "server-side-fallback-2026-07-01"}
    assert "temperature" not in kw and "top_p" not in kw
    assert out["spotify_pitch"] == "A pitch."
    assert out["_usage"] == {"input_tokens": 3000, "output_tokens": 900, "model": "claude-opus-5-5"}


def test_bio_writer_reads_text_blocks_and_fills_every_platform(fake):
    fake.reply = {"bandcamp": "Short.", "spotify": "Longer."}
    out = bio_manager.generate_bios({"artist": "Inch of Shadow", "links": {}}, RELEASE)
    kw = fake.calls[0]
    assert kw["model"] == "claude-opus-5-5" and kw["output_config"] == {"effort": "medium"}
    assert out["bandcamp"] == "Short." and out["spotify"] == "Longer."
    assert all(pid in out for pid in bio_manager.PLATFORM_ORDER)


@pytest.mark.parametrize("stop,needle", [("refusal", "declined"), ("max_tokens", "ran out")])
def test_both_writers_raise_on_refusal_and_cut_off(fake, stop, needle):
    fake.reply, fake.stop = {"spotify": "x"}, stop
    with pytest.raises(ValueError, match=needle):
        seo_copy_generator.generate_copy(RELEASE, ["spotify"], "authentic")
    with pytest.raises(ValueError, match=needle):
        bio_manager.generate_bios({"artist": "Inch of Shadow", "links": {}})


def test_missing_key_raises_before_any_call(fake, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        bio_manager.generate_bios({"artist": "Inch of Shadow", "links": {}})
    assert fake.calls == []



class FakeOpenAI:
    """Stands in for openai.OpenAI: the Responses API with a free-shape JSON answer."""
    calls: list = []
    reply: dict = {}

    def __init__(self, api_key=None):
        self.responses = self

    def create(self, **kw):
        FakeOpenAI.calls.append(kw)
        return SimpleNamespace(status="completed", output_text=json.dumps(FakeOpenAI.reply),
                               usage=SimpleNamespace(input_tokens=2500, output_tokens=700))


@pytest.fixture
def fake_openai(monkeypatch):
    import openai
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(openai, "OpenAI", FakeOpenAI)
    FakeOpenAI.calls, FakeOpenAI.reply = [], {}
    return FakeOpenAI


def test_both_writers_send_the_same_prompts_to_gpt(fake, fake_openai):
    fake_openai.reply = {"spotify_pitch": "GPT pitch.", "spotify_artist_pick": "GPT pick."}
    seo_copy_generator.generate_copy(RELEASE, ["spotify"], "authentic")
    out = seo_copy_generator.generate_copy(RELEASE, ["spotify"], "authentic", provider="openai")
    claude_kw, gpt_kw = fake.calls[0], fake_openai.calls[0]
    assert gpt_kw["model"] == "gpt-6.1-sol" and gpt_kw["text"] == {"format": {"type": "json_object"}}
    assert gpt_kw["instructions"] == claude_kw["system"]
    assert gpt_kw["input"][0]["content"][0]["text"].startswith(claude_kw["messages"][0]["content"])
    assert out["spotify_pitch"] == "GPT pitch." and out["_usage"]["model"] == "gpt-6.1-sol"

    fake_openai.reply = {"bandcamp": "GPT short."}
    bios = bio_manager.generate_bios({"artist": "Inch of Shadow", "links": {}}, RELEASE, provider="openai")
    assert bios["bandcamp"] == "GPT short." and all(pid in bios for pid in bio_manager.PLATFORM_ORDER)


def test_unknown_writer_is_refused(fake):
    with pytest.raises(ValueError, match="unknown writer"):
        bio_manager.generate_bios({"artist": "Inch of Shadow", "links": {}}, provider="gemini")
    assert fake.calls == []
