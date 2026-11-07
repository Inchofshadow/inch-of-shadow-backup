"""The last pass over generated copy (SEO Copy, Bio Manager), added 2026-10-15.

Two offline tools from the repo root run on every string the writers return,
after the model and before the page:

  copy_clean.clean      invisible characters out, odd spaces to plain, dashes to
                        commas, curly quotes straight (the house rule in code)
  caption_check.check   the Instagram caption, assembled with its hashtags,
                        against the rules in docs/brand/voice.md

Nothing here calls a network. Keys starting with "_" (usage, this pass's own
notes) are left alone.
"""
from __future__ import annotations

import os
import sys
from typing import Any

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import caption_check  # noqa: E402
import copy_clean  # noqa: E402


def clean_fields(result: dict) -> int:
    """Clean every string (and every string inside a list) in place.
    Returns the number of changes made across all fields."""
    changes = 0
    for key, val in list(result.items()):
        if key.startswith("_"):
            continue
        if isinstance(val, str):
            text, rep = copy_clean.clean(val)
            result[key] = text
            changes += rep["total"]
        elif isinstance(val, list):
            new = []
            for item in val:
                if isinstance(item, str):
                    text, rep = copy_clean.clean(item)
                    new.append(text)
                    changes += rep["total"]
                else:
                    new.append(item)
            result[key] = new
    return changes


def assemble_instagram(result: dict) -> str:
    """Caption plus the hashtag line, the way it is pasted."""
    caption = (result.get("instagram_caption") or "").rstrip()
    tags = result.get("instagram_hashtags") or []
    if isinstance(tags, str):
        tags = [t for t in tags.replace(",", " ").split() if t]
    tags = ["#" + t.strip().lstrip("#") for t in tags if str(t).strip()]
    if caption and tags:
        return caption + "\n\n" + " ".join(tags)
    return caption or " ".join(tags)


def _keywords(release: dict | None) -> list:
    meta = (release or {}).get("metadata", {}) or {}
    kws = []
    for key in ("genre_primary",):
        v = (meta.get(key) or "").strip()
        if v:
            kws.append(v)
    return kws


def finalise_copy(result: dict, release: dict | None = None) -> dict:
    """SEO Copy: clean every field, then check the Instagram caption.
    Adds result["_clean"] = {"changes": n} and, when an Instagram caption is
    present, result["_check"]["instagram"] = the check report plus its text."""
    changes = clean_fields(result)
    result["_clean"] = {"changes": changes}
    if result.get("instagram_caption"):
        text = assemble_instagram(result)
        rep = caption_check.check(text, _keywords(release))
        rep["text"] = caption_check.format_report(rep)
        result.setdefault("_check", {})["instagram"] = rep
    return result


def finalise_bios(result: dict) -> dict:
    """Bio Manager: clean every bio. Bios have no hashtags and no feed cut, so
    the caption check does not apply."""
    changes = clean_fields(result)
    result["_clean"] = {"changes": changes}
    return result
