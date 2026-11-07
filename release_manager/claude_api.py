"""One place for the Claude API calls the Release Manager makes (G-08 F4, 2026-10-20).

The copy writers, the Imagine draft review and the subject sharpener all need the same three
things: a client from the key in .env, a request with the effort level and the server-side
refusal fallback, and a reply read by block type (Opus 5.5 answers can start with a thinking
block). They live here once, so a change to the model or the fallback header is one edit.

Paid from the Max plan's monthly Claude API credit; the key stays in .env.

Monthly limit (Amir, 2026-10-20): every call's cost goes into stats_snapshots/claude_spend.json,
and once a calendar month has spent LIMIT_USD nothing more is sent until the next month; the
pages show the refusal as a pop-up. Raise LIMIT_USD here to change it.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL = "claude-opus-5-5"
FALLBACK_BETA = "server-side-fallback-2026-07-01"
RATE_IN, RATE_OUT = 4 / 1e6, 20 / 1e6          # Opus 5.5, USD per token
RATE_SEARCH = 10 / 1000                         # server web search, USD per search
LIMIT_USD = 150.0
LEDGER = ROOT / "stats_snapshots" / "claude_spend.json"


class ClaudeError(ValueError):
    """Our own message for the page: the key is missing, Claude declined, or the reply is cut off."""


class LimitReached(ClaudeError):
    """The month's LIMIT_USD is spent: nothing was sent."""


def _ledger() -> dict:
    try:
        return json.loads(LEDGER.read_text())
    except (OSError, ValueError):
        return {"months": {}}


def month_spend(now: datetime | None = None) -> dict:
    """This calendar month's Claude API spend from the ledger, in USD, against the limit."""
    ym = (now or datetime.now()).strftime("%Y-%m")
    m = _ledger().get("months", {}).get(ym, {})
    return {"month": ym, "usd": round(float(m.get("usd") or 0), 4), "calls": int(m.get("calls") or 0),
            "limit": LIMIT_USD}


def limit_note(now: datetime | None = None) -> str:
    """The pop-up text when the month's limit is reached, else an empty string."""
    s = month_spend(now)
    if s["usd"] < LIMIT_USD:
        return ""
    return (f"Monthly Claude API limit reached: ${s['usd']:.2f} of ${LIMIT_USD:.0f} spent in {s['month']}. "
            f"Nothing more is sent to Claude until next month. To raise the limit, change LIMIT_USD in "
            f"release_manager/claude_api.py.")


def _record(what: str, model: str, usage: dict, now: datetime | None = None) -> None:
    ym = (now or datetime.now()).strftime("%Y-%m")
    led = _ledger()
    m = led.setdefault("months", {}).setdefault(ym, {"usd": 0.0, "calls": 0, "by": {}})
    m["usd"] = round(float(m.get("usd") or 0) + usage["cost_usd"], 5)
    m["calls"] = int(m.get("calls") or 0) + 1
    b = m.setdefault("by", {}).setdefault(what, {"usd": 0.0, "calls": 0})
    b["usd"] = round(float(b.get("usd") or 0) + usage["cost_usd"], 5)
    b["calls"] = int(b.get("calls") or 0) + 1
    led["last"] = {"what": what, "model": model, "made": (now or datetime.now()).isoformat(timespec="seconds"), **usage}
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    tmp = LEDGER.with_suffix(".tmp")
    tmp.write_text(json.dumps(led, indent=2))
    tmp.replace(LEDGER)


def client(env_file: Path | None = None):
    import anthropic
    from dotenv import load_dotenv
    load_dotenv(env_file or ROOT / ".env")
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        raise ClaudeError("ANTHROPIC_API_KEY not set in .env")
    return anthropic.Anthropic(api_key=key)


def ask(client, *, max_tokens: int, system: str, messages: list, effort: str,
        model: str = MODEL, schema: dict | None = None, what: str = "generation",
        tools: list | None = None):
    """One request: effort set explicitly, structured output when a schema is given, and a
    safety-classifier decline re-run server-side on Anthropic's recommended fallback model.
    Refused with LimitReached once the month's LIMIT_USD is spent (nothing sent). Raises
    ClaudeError on a refusal or a cut-off reply; returns the message, its cost in the ledger.
    tools (optional, GR-02 2026-11-05): passed through as the request's tools, e.g. the
    server-side web search tool; without it the request is unchanged."""
    note = limit_note()
    if note:
        raise LimitReached(note)
    output_config: dict = {"effort": effort}
    if schema is not None:
        output_config["format"] = {"type": "json_schema", "schema": schema}
    extra: dict = {"tools": tools} if tools else {}
    message = client.messages.create(
        **extra,
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
        output_config=output_config,
        extra_body={"fallbacks": "default"},
        extra_headers={"anthropic-beta": FALLBACK_BETA},
    )
    _record(what, model, usage_of(message))
    if message.stop_reason == "refusal":
        raise ClaudeError(f"Claude declined this {what} (stop_reason=refusal)")
    if message.stop_reason == "max_tokens":
        raise ClaudeError(f"Claude ran out of tokens before finishing the {what}")
    return message


def text_of(message) -> str:
    """The reply's text blocks joined; thinking blocks are skipped."""
    return "".join(b.text for b in message.content if getattr(b, "type", "") == "text").strip()


def usage_of(message, rate_in: float = RATE_IN, rate_out: float = RATE_OUT) -> dict:
    """Tokens and cost; web searches (server tool, $10 per 1000) are added when there were any."""
    u = message.usage
    out = {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
           "cost_usd": round(u.input_tokens * rate_in + u.output_tokens * rate_out, 5)}
    searches = int(getattr(getattr(u, "server_tool_use", None), "web_search_requests", 0) or 0)
    if searches:
        out["web_searches"] = searches
        out["cost_usd"] = round(out["cost_usd"] + searches * RATE_SEARCH, 5)
    return out
