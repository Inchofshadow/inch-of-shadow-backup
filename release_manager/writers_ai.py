"""The two copy writers' model call, for either provider (Machine-27, 2026-10-21).

bio_manager and seo_copy_generator build their prompts as before; this sends the same system and
user prompt to Claude (claude_api) or to GPT (openai_api) and hands back the raw JSON text and the
token usage. Everything after that (fence strip, parsing, the copy pass) stays in each writer.
"""
from __future__ import annotations

PROVIDERS = ("claude", "openai")
LABELS = {"claude": "Claude", "openai": "GPT"}


def write(system: str, user: str, *, provider: str = "claude", max_tokens: int, effort: str, what: str,
          claude_model: str | None = None) -> tuple[str, dict]:
    """(raw text, {"input_tokens", "output_tokens", "cost_usd", "model"}). Raises ValueError with our own message."""
    if provider not in PROVIDERS:
        raise ValueError(f"unknown writer: {provider}")
    if provider == "openai":
        from release_manager import openai_api
        client = openai_api.client()
        raw, usage = openai_api.ask_json_free(client, instructions=system, text=user, effort=effort, what=what)
        if not raw:
            raise ValueError("GPT returned no text")
        return raw, {**usage, "model": openai_api.MODEL}
    from release_manager import claude_api
    client = claude_api.client()
    kwargs = {"model": claude_model} if claude_model else {}
    message = claude_api.ask(client, max_tokens=max_tokens, system=system, effort=effort,
                             messages=[{"role": "user", "content": user}], what=what, **kwargs)
    raw = claude_api.text_of(message)
    if not raw:
        raise ValueError("Claude returned no text")
    return raw, {**claude_api.usage_of(message), "model": kwargs.get("model") or claude_api.MODEL}
