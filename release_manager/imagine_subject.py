"""Imagine subject sharpener (Machine-23, 2026-10-20).

Amir types a rough idea; Claude rewrites it as ONE precise visual sentence. Claude sees the whole
assembled prompt (use, details, composition, brand core, never list, release brief) so the new
subject fits it, but only layer 4, the subject, changes. The suggestion is shown on the page and
is used only when Amir clicks "Use it"; nothing is rendered from here.

Paid from the Max plan's monthly Claude API credit (claude-opus-5-5, about a cent per sharpen).
"""
from __future__ import annotations

import json
import re
from datetime import datetime

from release_manager import claude_api
from release_manager import imagine as im

MODEL = claude_api.MODEL
EFFORT = "low"                      # he waits for it: keep it quick
MAX_TOKENS = 8000
MAX_SUBJECT = 2500                  # his detailed subjects run to ~1000 characters

SCHEMA = {
    "type": "object",
    "properties": {
        "subject": {"type": "string"},
        "why": {"type": "string"},
    },
    "required": ["subject", "why"],
    "additionalProperties": False,
}

SYSTEM = """You sharpen the SUBJECT line of an image prompt for Inch of Shadow, a Berlin musician.

You get his rough subject and the full prompt it sits in. Rewrite only the subject. Keep his idea; do not swap it for a different one.

- A short, rough subject: turn it into ONE sentence that says exactly what we see, under 45 words.
- An already detailed subject: keep EVERY detail he wrote (each object, count, colour, amount, material, "no other colour" style limit). Only make vague parts concrete, fix what conflicts with the prompt, and tidy the wording. It may stay as long as his.

Make it concrete: the main thing and its material, where it is, the light on it, how close we are, where it sits in the frame. Few elements, one focal point. Fit the prompt's use, details, composition and brand core; never ask for anything its constraints forbid.

Never name an artist or an existing work. No familiar religious symbols. Never describe Amir or any real person as part of the picture. No text or lettering in the image. No em-dashes. Plain English.

why: one short sentence on what you changed."""


class SharpenError(claude_api.ClaudeError):
    pass


def _client():
    return claude_api.client(im.ROOT / ".env")


def _clean(text: str) -> str:
    """One line, no em- or en-dashes: a dash between digits is a range and becomes a hyphen
    (10–12 ravens -> 10-12 ravens); any other dash becomes a comma pause."""
    text = " ".join((text or "").split())
    text = re.sub(r"(?<=\d)\s*[\u2013\u2014]\s*(?=\d)", "-", text)
    text = re.sub(r"\s*[\u2013\u2014]\s*", ", ", text)
    return re.sub(r"\s+,", ",", text).strip().strip('"').strip()


def sharpen(subject: str, prompt: str, kind: str = "", client=None) -> dict:
    """Return {"subject", "why", "usage", "cost_usd", "model", "made"}; never renders anything."""
    subject = " ".join((subject or "").split())
    if not subject:
        raise SharpenError("the subject is empty")
    if len(subject) > MAX_SUBJECT:
        raise SharpenError("the subject is too long for one image, shorten it first")
    client = client or _client()
    try:
        message = claude_api.ask(
            client, max_tokens=MAX_TOKENS, system=SYSTEM, effort=EFFORT, schema=SCHEMA, what="rewrite",
            messages=[{"role": "user", "content":
                       f"Kind of image: {kind or 'free'}\n\nHis rough subject:\n{subject}\n\n"
                       f"The full prompt it sits in:\n\n{prompt}"}])
    except claude_api.ClaudeError as e:
        raise SharpenError(str(e)) from e
    try:
        result = json.loads(claude_api.text_of(message))
    except ValueError as e:
        raise SharpenError("the rewrite came back unreadable") from e
    new = _clean(result.get("subject", ""))
    if not new:
        raise SharpenError("Claude returned an empty subject")
    usage = claude_api.usage_of(message)
    return {"subject": new, "why": _clean(result.get("why", "")), "model": MODEL,
            "made": datetime.now().isoformat(timespec="seconds"),
            "usage": {"input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"]},
            "cost_usd": usage["cost_usd"]}
