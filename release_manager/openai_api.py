"""One place for the OpenAI text calls the Release Manager makes (Machine-26, 2026-10-21).

Same shape as claude_api.py: a client from the key in .env, one request helper, the reply's text,
the cost. Model and prices checked on 2026-10-21 against the key's model list and OpenAI's pricing
page (gpt-6.1-sol: text + image in, structured outputs, Responses API, $2 / $10 per 1M tokens).

Paid from Amir's OpenAI balance (the same one the image renders use). Every call's cost goes into
stats_snapshots/openai_spend.json; no cap here, the prepaid balance is the limit.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL = "gpt-6.1-sol"
RATE_IN, RATE_OUT = 2 / 1e6, 10 / 1e6          # gpt-6.1-sol, USD per token, standard tier
LEDGER = ROOT / "stats_snapshots" / "openai_spend.json"


class OpenAIError(ValueError):
    """Our own message for the page: the key is missing, or the reply is unusable."""


def client(env_file: Path | None = None):
    from dotenv import load_dotenv
    from openai import OpenAI
    load_dotenv(env_file or ROOT / ".env")
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise OpenAIError("OPENAI_API_KEY not set in .env")
    return OpenAI(api_key=key)


def ask_json(client, *, instructions: str, content: list, schema: dict, name: str,
             effort: str = "medium", model: str = MODEL, what: str = "generation") -> tuple[dict, dict]:
    """One Responses API request with a strict JSON schema. Returns (parsed reply, usage with cost)."""
    r = client.responses.create(
        model=model,
        instructions=instructions,
        reasoning={"effort": effort},
        input=[{"role": "user", "content": content}],
        text={"format": {"type": "json_schema", "name": name, "strict": True, "schema": schema}},
    )
    usage = usage_of(r)
    _record(what, model, usage)
    if getattr(r, "status", "completed") != "completed":
        raise OpenAIError(f"GPT did not finish this {what} (status {r.status})")
    try:
        return json.loads(r.output_text or ""), usage
    except ValueError as e:
        raise OpenAIError(f"GPT's {what} came back unreadable") from e


def ask_json_free(client, *, instructions: str, text: str, effort: str = "medium", model: str = MODEL,
                  what: str = "generation") -> tuple[str, dict]:
    """One Responses API request whose answer must be a JSON object of any shape (the copy writers'
    own key lists). Returns (raw text, usage with cost)."""
    r = client.responses.create(
        model=model,
        instructions=instructions,
        reasoning={"effort": effort},
        input=[{"role": "user", "content": [text_part(text + "\n\nReturn the answer as one JSON object.")]}],
        text={"format": {"type": "json_object"}},
    )
    usage = usage_of(r)
    _record(what, model, usage)
    if getattr(r, "status", "completed") != "completed":
        raise OpenAIError(f"GPT did not finish this {what} (status {r.status})")
    return (r.output_text or "").strip(), usage


def image_part(b64: str, media: str = "image/png") -> dict:
    return {"type": "input_image", "image_url": f"data:{media};base64,{b64}"}


def text_part(text: str) -> dict:
    return {"type": "input_text", "text": text}


def usage_of(r) -> dict:
    u = r.usage
    return {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
            "cost_usd": round(u.input_tokens * RATE_IN + u.output_tokens * RATE_OUT, 5)}


def _ledger() -> dict:
    try:
        return json.loads(LEDGER.read_text())
    except (OSError, ValueError):
        return {"months": {}}


def month_spend(now: datetime | None = None) -> dict:
    ym = (now or datetime.now()).strftime("%Y-%m")
    m = _ledger().get("months", {}).get(ym, {})
    return {"month": ym, "usd": round(float(m.get("usd") or 0), 4), "calls": int(m.get("calls") or 0)}


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
