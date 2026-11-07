"""Imagine draft review (Machine-22, 2026-10-20).

Claude looks at a generated image next to the exact prompt that made it (which already holds the
brand core, the release brief and the never list) and says whether it is ready for a paid final
render, what is wrong, and ONE wording change for the next try.

Rules kept here:
- only images the model generated are reviewed; composites and anything holding Amir's photo are
  refused, so his face is never sent;
- nothing is re-rendered: the suggestion is shown, Amir decides and clicks;
- the review, its token usage and its cost are written into the image's JSON record.

Paid from the Max plan's monthly Claude API credit (claude-opus-5-5, a few cents per review).
"""
from __future__ import annotations

import base64
import io
import json
from datetime import datetime

from release_manager import claude_api
from release_manager import imagine as im

MODEL = claude_api.MODEL
EFFORT = "medium"
MAX_TOKENS = 16000
MAX_EDGE = 1568                     # downscale before sending: enough detail, fewer image tokens

AREAS = ("text", "anatomy", "palette", "never-list", "composition", "brief", "ai-look", "technical")

SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["pass", "fix"]},
        "summary": {"type": "string"},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "area": {"type": "string", "enum": list(AREAS)},
                    "note": {"type": "string"},
                },
                "required": ["area", "note"],
                "additionalProperties": False,
            },
        },
        "prompt_fix": {"type": "string"},
    },
    "required": ["verdict", "summary", "issues", "prompt_fix"],
    "additionalProperties": False,
}

SYSTEM = """You review AI image drafts for Inch of Shadow, a Berlin musician, before he pays for a final render.

You get the draft, the exact prompt that made it, and the CURRENT RULES: today's never list, brand core and release brief. The rules can be newer than the prompt; when they differ, today's rules win, and a draft that breaks them is a "fix". Judge the image only against the prompt and these rules. Do not bring in your own taste or a style they do not ask for.

Check, in this order:
- text: any letters, numbers, logos, signatures or watermarks, even small or half-formed
- anatomy: broken hands, faces, limbs or objects that do not hold together
- palette: colours or white balance the prompt rules out
- never-list: anything the CONSTRAINTS section or today's never list forbids
- composition: the composition rules (quiet title area, one focal point, room for a figure, plain paper)
- brief: does it show the subject and the concept, or something else
- ai-look: plastic skin, airbrushed gradients, over-sharpened detail, generic AI gloss
- technical: artefacts, seams, banding, cut-off edges

verdict is "pass" when it is good enough to render as a final as it is, "fix" when a change to the prompt would clearly help. Only list real problems you can see; an empty list is fine.

prompt_fix is ONE concrete change to the prompt wording for the next try, written as the words to add or replace. Empty when the verdict is pass. Never name a living artist. No em-dashes anywhere. Plain, short English."""


class ReviewError(claude_api.ClaudeError):
    pass


def reviewable(rec: dict | None) -> tuple[bool, str]:
    """Only images the model made. Composites carry his photo, so they are never sent."""
    if not rec:
        return False, "unknown image"
    if rec.get("kind") == "composite" or rec.get("photo") or rec.get("plate"):
        return False, "composites hold your photo, they are not sent for review"
    # a render the model made carries a real quality; a local composite stores "-" and no model name
    if rec.get("quality") not in im.QUALITIES or not rec.get("model"):
        return False, "only images the model generated are reviewed"
    if not (im.OUT / rec.get("file", "")).is_file():
        return False, "the image file is missing"
    return True, ""


def _image_b64(path) -> tuple[str, str]:
    from PIL import Image
    with Image.open(path) as img:
        img = img.convert("RGB")
        img.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode(), "image/png"


def current_rules(rec: dict) -> str:
    """Today's never list, brand core and release brief: drafts can predate a rule."""
    kind = rec.get("kind") or ""
    never = im.ELEMENT_NEVER if kind in ("element", "illustration") else im.never_global()
    brief = {}
    slug = rec.get("release") or ""
    f = im.ROOT / "releases" / f"{slug}.json"
    if slug and slug.replace("-", "").isalnum() and f.is_file():
        try:
            brief = im.brief_of(json.loads(f.read_text()))
        except (OSError, ValueError):
            brief = {}
    never = list(never) + [l.strip() for l in (brief.get("never") or "").splitlines() if l.strip()]
    parts = ["Never list:\n" + "\n".join(f"- {n}" for n in never),
             "Brand core:\n" + im.core(kind)]
    if brief.get("concept") or brief.get("mood"):
        parts.append(f"Release brief: concept: {brief.get('concept') or '-'}; mood: {brief.get('mood') or '-'}")
    return "\n\n".join(parts)


def _client():
    return claude_api.client(im.ROOT / ".env")


def review(image_id: str, client=None) -> dict:
    """Review one image, save the result into its record and return the record."""
    rec = im.record(image_id)
    ok, why = reviewable(rec)
    if not ok:
        raise ReviewError(why)
    data, media = _image_b64(im.OUT / rec["file"])
    client = client or _client()
    try:
        message = claude_api.ask(
            client, max_tokens=MAX_TOKENS, system=SYSTEM, effort=EFFORT, schema=SCHEMA, what="review",
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media, "data": data}},
                {"type": "text", "text": _brief_text(rec)},
            ]}])
    except claude_api.ClaudeError as e:
        raise ReviewError(str(e)) from e
    try:
        result = json.loads(claude_api.text_of(message))
    except ValueError as e:
        raise ReviewError("the review came back unreadable") from e
    return _save(image_id, rec, "review", result, MODEL, claude_api.usage_of(message))


def _brief_text(rec: dict) -> str:
    return (f"Kind of image: {rec.get('kind') or 'free'}\n\n"
            f"The exact prompt that made it:\n\n{rec.get('prompt') or ''}\n\n"
            f"CURRENT RULES (today, may be newer than the prompt):\n\n{current_rules(rec)}")


def _save(image_id: str, rec: dict, key: str, result: dict, model: str, usage: dict) -> dict:
    """Clean a reviewer's answer and store it under `key` in the image's record."""
    result["issues"] = [i for i in result.get("issues") or [] if i.get("area") in AREAS and i.get("note")]
    if result.get("verdict") == "pass":
        result["prompt_fix"] = ""
    result.update({
        "model": model,
        "made": datetime.now().isoformat(timespec="seconds"),
        "usage": {"input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"]},
        "cost_usd": usage["cost_usd"],
    })
    rec = im.record(image_id) or rec          # re-read: a decision or the other review may have landed meanwhile
    rec[key] = result
    (im.OUT / f"{image_id}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    return rec


def review_openai(image_id: str, client=None) -> dict:
    """Machine-26: the same review by OpenAI's model, same input, same schema, saved as 'review_openai'.
    The image and prompt already go to OpenAI for the render, so nothing new leaves the Mac."""
    from release_manager import openai_api
    rec = im.record(image_id)
    ok, why = reviewable(rec)
    if not ok:
        raise ReviewError(why)
    data, media = _image_b64(im.OUT / rec["file"])
    try:
        client = client or openai_api.client(im.ROOT / ".env")
        result, usage = openai_api.ask_json(
            client, instructions=SYSTEM, schema=SCHEMA, name="draft_review", effort=EFFORT, what="review",
            content=[openai_api.image_part(data, media), openai_api.text_part(_brief_text(rec))])
    except openai_api.OpenAIError as e:
        raise ReviewError(str(e)) from e
    return _save(image_id, rec, "review_openai", result, openai_api.MODEL, usage)
