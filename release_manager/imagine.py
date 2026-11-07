"""Imagine: AI images on brand (Machine-17, 2026-09-27).

Every prompt is assembled from four layers into labelled sections, always in the same order
(docs/brand/ai-image-prompting.md, section 4):
  1. the brand core      inch_of_shadow_style.txt, verbatim, never edited per image
  2. the release brief   releases/<slug>.json "image_brief": mood pair, motifs, concept, never list,
                         anchor image, references
  3. per-image options   options/<kind>/<name>.txt (light, medium, texture, ...)
  4. the subject         one sentence from Amir
plus the global never list (docs/brand/ai-never.txt) and reference images with labelled roles.

Rules kept here: nothing is sent without Amir's click; references that are other artists' work
go in as WORDS only, never as images; his face is never an input (the background kind makes an
empty plate for the local composite). Every image is saved with a JSON record: the exact prompt,
references, model, size, quality, the real token usage and cost, and his decision.
"""
from __future__ import annotations

import base64
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "generated_images" / "imagine"
REFS = ROOT / "references" / "imagine"
CORE_FILE = ROOT / "inch_of_shadow_style.txt"
ELEMENT_CORE_FILE = ROOT / "inch_of_shadow_style_element.txt"   # the short block for ink/engraving elements
NEVER_FILE = ROOT / "docs" / "brand" / "ai-never.txt"
TEST_SET = ROOT / "docs" / "brand" / "ai-test-set.json"
OPTIONS_DIR = ROOT / "options"

MODELS = ("gpt-image-2.5-flare", "gpt-image-2.5-sunburst", "gpt-image-2")
QUALITIES = ("low", "medium", "high")
PRESETS = {                     # the two usual choices; anything else is picked by hand
    "draft": ("gpt-image-2.5-flare", "low"),
    "final": ("gpt-image-2.5-sunburst", "high"),
}
SIZES = {
    "square": ("Square", "1024x1024"),
    "square-2k": ("Square 2K (cover master, upscale locally)", "2048x2048"),
    "portrait": ("Portrait 2:3", "1024x1536"),
    "story": ("9:16 (canvas, story, reel)", "1152x2048"),
    "wide": ("16:9 (YouTube, banner)", "2048x1152"),
}
KINDS = {
    "cover": ("Cover art", "Square album cover artwork for a single. Artwork only, no lettering."),
    "background": ("Background plate", "A background plate for a photo composite: an empty place, no people, "
                                        "with room for a standing figure to be added later."),
    "texture": ("Texture", "A full-frame texture to lay under or over artwork. No objects, no horizon."),
    "free": ("Free image", "An artwork image."),
    "illustration": ("Illustrated cover", "Square album cover artwork, drawn by hand on paper. Artwork only, no lettering."),
    "element": ("Illustrated element", "One illustrated element on plain off-white paper, to be cut out and "
                                       "placed on a cover by hand. Artwork only, no lettering."),
}
# the element kind sends only what applies to a drawing on paper (Amir 2026-10-14: "only what is relevant")
ELEMENT_NEVER = ["No text, letters, numbers, logos or watermarks.",
                 "No churches, domes, crosses, or other religious symbols.",
                 "No photograph, no 3D render, no digital airbrush or soft gradients."]
TITLE_AREAS = {
    "top": "Keep the top 30% quiet: no strong edges, props or bright highlights, reserved for type added later.",
    "bottom": "Keep the bottom 30% quiet: no strong edges, props or bright highlights, reserved for type added later.",
    "none": "",
}
LIGHT_DIRECTIONS = {            # for a background plate: it must match the light on his photo
    "left": "The main light comes from the left, at about head height.",
    "right": "The main light comes from the right, at about head height.",
    "front": "The main light comes from in front of the viewer, slightly above.",
    "behind": "The main light comes from behind, as a rim or glow.",
    "above": "The main light comes from above, like a streetlight or a skylight.",
}
OPTION_KINDS = ("light", "medium", "texture", "setting", "concept", "symbols")
MULTI_KINDS = ("motif",)
REF_ROLES = ("style", "palette", "light", "composition", "texture", "mood", "redraw")   # redraw = our own earlier AI draft
# fallback prices per image (OpenAI's gpt-image-2 table, 1024 px); replaced by the logged real cost
FALLBACK = {"low": 0.006, "medium": 0.053, "high": 0.211}
RATE_OUT, RATE_IMG_IN, RATE_TEXT_IN = 30 / 1e6, 8 / 1e6, 5 / 1e6


# ---------------------------------------------------------------- the layers

def core(kind: str = "") -> str:
    f = ELEMENT_CORE_FILE if kind in ("element", "illustration") and ELEMENT_CORE_FILE.is_file() else CORE_FILE
    return f.read_text(encoding="utf-8").strip()


def never_global() -> list[str]:
    if not NEVER_FILE.is_file():
        return []
    return [l.strip() for l in NEVER_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]


def options(kind: str) -> list[str]:
    d = OPTIONS_DIR / kind
    return sorted(p.stem for p in d.glob("*.txt")) if d.is_dir() else []


def option_text(kind: str, name: str) -> str:
    if name not in options(kind):
        raise ValueError(f"unknown {kind} option: {name}")
    return (OPTIONS_DIR / kind / f"{name}.txt").read_text(encoding="utf-8").strip()


def brief_of(release: dict | None) -> dict:
    b = dict((release or {}).get("image_brief") or {})
    b.setdefault("mood", "")
    b.setdefault("motifs", [])
    b.setdefault("concept", "")
    b.setdefault("never", "")
    b.setdefault("anchor", "")
    return b


# ---------------------------------------------------------------- references

def _scope_dir(scope: str) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,80}", scope or ""):
        raise ValueError("bad reference scope")
    return REFS / scope


def refs(scope: str) -> list[dict]:
    """The references of one scope ('brand' or a release slug), from its index.json."""
    f = _scope_dir(scope) / "index.json"
    if not f.is_file():
        return []
    items = json.loads(f.read_text())
    for r in items:
        r["scope"] = scope
        r["path"] = str(_scope_dir(scope) / r["file"])
    return [r for r in items if Path(r["path"]).is_file()]


def add_ref(scope: str, filename: str, data: bytes, role: str, note: str, send: bool, owner: str) -> dict:
    """Store a reference. `send` = may go to the model as an image (his own or approved work only);
    otherwise it is used as words: its note goes into the prompt, the picture stays on the Mac."""
    if role not in REF_ROLES:
        raise ValueError("bad role")
    d = _scope_dir(scope)
    d.mkdir(parents=True, exist_ok=True)
    stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", Path(filename).stem)[:60] or "ref"
    ext = Path(filename).suffix.lower() if Path(filename).suffix.lower() in (".jpg", ".jpeg", ".png", ".webp") else ".png"
    name = f"{stem}_{datetime.now().strftime('%Y%m%d-%H%M%S')}{ext}"
    (d / name).write_bytes(data)
    idx = d / "index.json"
    items = json.loads(idx.read_text()) if idx.is_file() else []
    item = {"file": name, "role": role, "note": note.strip(), "send": bool(send and owner in ("mine", "approved")),
            "owner": owner, "added": datetime.now().isoformat(timespec="seconds")}
    items.append(item)
    idx.write_text(json.dumps(items, indent=2, ensure_ascii=False))
    return item


# ---------------------------------------------------------------- the prompt

def build_prompt(kind: str, subject: str, choice: dict, release: dict | None, moods: dict,
                 title_area: str = "top", light_direction: str = "", ref_items: list[dict] | None = None) -> str:
    """The exact text sent, in labelled sections, always in this order:
    USE, SUBJECT, DETAILS, COMPOSITION, REFERENCES, BRAND, CONSTRAINTS."""
    if kind not in KINDS:
        raise ValueError("bad kind")
    subject = " ".join((subject or "").split())
    if not subject:
        raise ValueError("the subject is empty")
    brief = brief_of(release)
    lines = [f"USE: {KINDS[kind][1]}", f"SUBJECT: {subject}"]

    details = []
    for k in OPTION_KINDS:
        if choice.get(k):
            details.append(option_text(k, choice[k]))
    motifs = list(dict.fromkeys((choice.get("motif") or []) + list(brief["motifs"])))
    for m in motifs[:2]:                                   # at most two motifs: few elements
        details.append(option_text("motif", m))
    mood_key = choice.get("mood") or brief["mood"]
    if mood_key and mood_key in moods:
        m = moods[mood_key]
        details.append(f"Palette: {m.get('name', mood_key)}, {m['light']} and {m['dark']}, used with restraint; "
                       f"check neutral white balance, no warm yellow cast unless the light asks for it.")
    if brief["concept"]:
        details.append(f"Concept of this release: {brief['concept']}")
    if details:
        lines.append("DETAILS:\n" + "\n".join(f"- {d}" for d in details))

    comp = (["Only what the subject names, on even plain paper with white space around it; no scene, no frame, no cast shadow."]
            if kind == "element" else ["One focal point with calm space around it; it must read at thumbnail size."])
    if TITLE_AREAS.get(title_area):
        comp.append(TITLE_AREAS[title_area])
    if kind == "background" and light_direction in LIGHT_DIRECTIONS:
        comp.append(LIGHT_DIRECTIONS[light_direction])
    lines.append("COMPOSITION: " + " ".join(comp))

    sent = [r for r in (ref_items or []) if r.get("send")]
    words = [r for r in (ref_items or []) if not r.get("send") and r.get("note")]
    if sent or words:
        parts = []
        for i, r in enumerate(sent, start=1):
            if r["role"] == "redraw":
                parts.append(f"Image {i}: our own earlier draft{': ' + r['note'] if r.get('note') else ''}. "
                             f"Redraw it at full quality: keep its subject, shapes and layout.")
                continue
            parts.append(f"Image {i}: {r['role']} reference{': ' + r['note'] if r.get('note') else ''}. "
                         f"Take only its {r['role']}; do not copy its subject, objects or layout.")
        for r in words:
            parts.append(f"Described reference ({r['role']}): {r['note']}")
        lines.append("REFERENCES:\n" + "\n".join(f"- {p}" for p in parts))

    lines.append("BRAND:\n" + core(kind))
    never = (ELEMENT_NEVER if kind in ("element", "illustration") else never_global()) + \
        [l.strip() for l in (brief["never"] or "").splitlines() if l.strip()]
    lines.append("CONSTRAINTS:\n" + "\n".join(f"- {n}" for n in never) +
                 "\n- Not in the style of any named living artist, and not a copy of any existing cover.")
    return "\n\n".join(lines)


# ---------------------------------------------------------------- the next round (Machine-25)

CLOSENESS = {                   # the slider's three real stops: what we control is whether the previous
    "keep": ("Keep it",         # draft goes in as the image to redraw, and how strict the wording is
             "Redraw Image 1 with exactly one change: {fix} Keep everything else as it is in Image 1: "
             "the same subject, layout, light, palette and texture."),
    "mostly": ("Mostly keep",
               "Redraw Image 1 and apply this change: {fix} Keep its subject and layout; you may change the "
               "light, texture and detail where the change needs it."),
    "free": ("Free",
             "Apply this change to the image described above: {fix} Everything else follows the sections above."),
}


_SECTION = re.compile(r"^(?:USE|SCENE|SUBJECT|DETAILS|COMPOSITION|REFERENCES|BRAND|CONSTRAINTS):", re.M)


def next_round(parent_id: str, fix: str, closeness: str) -> dict:
    """The prompt, the reference and the meta for one more draft after a review: the parent's exact
    prompt plus a THIS ROUND section with the fix. 'keep' and 'mostly' send the parent draft as the
    image to redraw (its own references are already baked into it); 'free' sends no image."""
    parent = record(parent_id)
    if parent is None or parent.get("kind") == "composite" or parent.get("photo") or parent.get("plate"):
        raise ValueError("unknown image, or a composite (never redrawn by the model)")
    if closeness not in CLOSENESS:
        raise ValueError("bad closeness")
    fix = " ".join((fix or "").split())
    if not fix:
        raise ValueError("the fix is empty")
    if not fix.endswith((".", "!", "?", '"', "\u201d", "'")):
        fix += "."
    # split on the labelled sections (older prompts used single newlines between them), drop the old
    # REFERENCES: they are already baked into the draft
    text = parent.get("prompt") or ""
    starts = [m.start() for m in _SECTION.finditer(text)]
    sections = ([text[a:b].strip() for a, b in zip(starts, starts[1:] + [len(text)])] if starts else [text.strip()])
    sections = [sec for sec in sections if sec and not sec.startswith("REFERENCES:")]
    if not sections:
        raise ValueError("the image has no prompt to continue from")
    refs = []
    if closeness != "free":
        refs = [{"file": parent["file"], "scope": "round", "role": "redraw", "send": True,
                 "path": str(OUT / parent["file"]), "note": f"step {int(parent.get('step') or 1)} of this image"}]
        at = next((i for i, sec in enumerate(sections) if sec.startswith(("BRAND:", "CONSTRAINTS:"))), len(sections))
        sections.insert(at, "REFERENCES:\n- Image 1: our own earlier draft. Redraw it at full quality: "
                        "keep its subject, shapes and layout, then apply THIS ROUND.")
    sections.append("THIS ROUND: " + CLOSENESS[closeness][1].format(fix=fix))
    meta = {k: parent.get(k) for k in ("release", "kind", "subject", "choice", "title_area") if k in parent}
    meta.update({"step": int(parent.get("step") or 1) + 1, "parent": parent_id, "closeness": closeness, "fix": fix})
    return {"prompt": "\n\n".join(sections), "refs": refs, "meta": meta, "size": parent.get("size") or "1024x1024"}


# ---------------------------------------------------------------- the log

def _records() -> list[dict]:
    if not OUT.is_dir():
        return []
    out = []
    for f in OUT.glob("*.json"):
        try:
            r = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        if (OUT / r.get("file", "")).is_file():
            out.append(r)
    return sorted(out, key=lambda r: r.get("made", ""), reverse=True)


def images(release_slug: str | None = None) -> list[dict]:
    return [r for r in _records() if release_slug is None or r.get("release") == release_slug]


def record(image_id: str) -> dict | None:
    f = OUT / f"{image_id}.json"
    if not re.fullmatch(r"[a-z0-9_.-]+", image_id or "") or not f.is_file():
        return None
    return json.loads(f.read_text())


def set_decision(image_id: str, decision: str) -> dict:
    if decision not in ("keep", "reject", "anchor", ""):
        raise ValueError("bad decision")
    r = record(image_id)
    if r is None:
        raise ValueError("unknown image")
    r["decision"] = decision or None
    r["decided"] = datetime.now().isoformat(timespec="seconds")
    (OUT / f"{image_id}.json").write_text(json.dumps(r, indent=2, ensure_ascii=False))
    return r


def month_spend(now: datetime | None = None) -> dict:
    ym = (now or datetime.now()).strftime("%Y-%m")
    rs = [r for r in _records() if r.get("made", "").startswith(ym)]
    return {"month": ym, "images": len(rs), "usd": round(sum(r.get("cost_usd") or 0 for r in rs), 4)}


def estimate(model: str, quality: str, size: str, n: int) -> dict:
    """Per-image cost from the logged real renders of the same model, quality and size; otherwise
    OpenAI's gpt-image-2 table scaled by the pixel count (2.5 prices are not published)."""
    same = [r["cost_usd"] for r in _records() if r.get("model") == model and r.get("quality") == quality
            and r.get("size") == size and r.get("cost_usd")]
    if same:
        each, basis = sum(same) / len(same), f"average of {len(same)} logged render(s)"
    else:
        w, h = (int(x) for x in size.split("x"))
        each, basis = FALLBACK[quality] * max(1.0, (w * h) / (1024 * 1024)), "OpenAI's gpt-image-2 table (estimate)"
    return {"each": round(each, 4), "total": round(each * n, 4), "basis": basis}


def option_stats() -> list[dict]:
    """Which options Amir keeps and which he rejects, from his decisions (improvement 5)."""
    tally: dict = {}
    for r in _records():
        d = r.get("decision")
        if d not in ("keep", "anchor", "reject"):
            continue
        for k, v in (r.get("choice") or {}).items():
            for name in (v if isinstance(v, list) else [v]):
                if not name or k == "mood":
                    continue
                t = tally.setdefault((k, name), {"kind": k, "name": name, "kept": 0, "rejected": 0})
                t["kept" if d in ("keep", "anchor") else "rejected"] += 1
    return sorted(tally.values(), key=lambda t: (-(t["kept"] - t["rejected"]), t["kind"], t["name"]))


# ---------------------------------------------------------------- the render (paid)

def _client():
    sys.path.insert(0, str(ROOT))
    import image_generator
    return image_generator.get_client()


def generate(prompt: str, model: str, quality: str, size: str, n: int, ref_items: list[dict],
             meta: dict, client=None) -> list[dict]:
    """The paid call. Only images marked `send` go to OpenAI; their order is the Image 1..n
    order the prompt names. Returns the saved records."""
    if model not in MODELS or quality not in QUALITIES or size not in {s for _, s in SIZES.values()}:
        raise ValueError("bad model, quality or size")
    n = max(1, min(int(n), 4))
    client = client or _client()
    sent = [Path(r["path"]) for r in ref_items if r.get("send")]
    started = datetime.now()
    if sent:
        handles = [p.open("rb") for p in sent]
        try:
            resp = client.images.edit(model=model, image=handles, prompt=prompt, size=size, quality=quality, n=n)
        finally:
            for h in handles:
                h.close()
    else:
        resp = client.images.generate(model=model, prompt=prompt, size=size, quality=quality, n=n)
    seconds = (datetime.now() - started).total_seconds()
    u = getattr(resp, "usage", None)
    u = u.model_dump() if hasattr(u, "model_dump") else (u or {})
    details = u.get("input_tokens_details") or {}
    cost = ((u.get("output_tokens") or 0) * RATE_OUT + (details.get("image_tokens") or 0) * RATE_IMG_IN
            + (details.get("text_tokens") or 0) * RATE_TEXT_IN)
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = started.strftime("%Y%m%d-%H%M%S")
    slug = re.sub(r"[^a-z0-9-]", "", (meta.get("release") or "free").lower()) or "free"
    saved = []
    for i, item in enumerate(resp.data, start=1):
        image_id = f"{slug}_{stamp}_{i}"
        (OUT / f"{image_id}.png").write_bytes(base64.b64decode(item.b64_json))
        rec = {"id": image_id, "file": f"{image_id}.png", "made": started.isoformat(timespec="seconds"),
               "model": model, "quality": quality, "size": size, "n": n, "seconds": round(seconds, 1),
               "prompt": prompt, "references": [{"file": r["file"], "scope": r["scope"], "role": r["role"],
                                                 "sent": bool(r.get("send"))} for r in ref_items],
               "usage": u, "cost_usd": round(cost / len(resp.data), 5), "decision": None, **meta}
        (OUT / f"{image_id}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
        saved.append(rec)
    return saved


# ---------------------------------------------------------------- the model test set (paid, on his go)

def test_set() -> list[dict]:
    return json.loads(TEST_SET.read_text())["prompts"] if TEST_SET.is_file() else []


def test_runs() -> list[dict]:
    """The test-set renders grouped by run, newest run first."""
    runs: dict = {}
    for r in _records():
        if r.get("test_run"):
            runs.setdefault(r["test_run"], []).append(r)
    return [{"run": k, "model": v[0].get("model"), "quality": v[0].get("quality"),
             "images": sorted(v, key=lambda x: x.get("test_key", ""))} for k, v in sorted(runs.items(), reverse=True)]


# ---------------------------------------------------------------- the composite (local, free)

def composite(plate_id: str, photo: Path, scale: float = 0.78, position: str = "center", cutout=None) -> dict:
    """Put Amir's photo onto one of our background plates, ON THE MAC: the photo is cut out
    locally (rembg, segmentation only, his face and body stay real pixels), placed standing on
    the bottom edge, and a light grain ties the two together. Nothing is sent anywhere; free."""
    from PIL import Image, ImageChops, ImageOps
    plate = record(plate_id)
    if plate is None:
        raise ValueError("unknown background plate")
    if position not in ("left", "center", "right"):
        raise ValueError("bad position")
    scale = max(0.3, min(float(scale), 1.0))
    bg = Image.open(OUT / plate["file"]).convert("RGB")
    with Image.open(photo) as p:
        p.draft("RGB", (2048, 2048))
        src = ImageOps.exif_transpose(p).convert("RGB")
    src.thumbnail((2048, 2048), Image.LANCZOS)
    if cutout is None:
        from rembg import remove
        cutout = remove
    subj = cutout(src.convert("RGBA")).convert("RGBA")
    box = subj.getchannel("A").getbbox()                      # trim the empty margin around him
    if box:
        subj = subj.crop(box)
    bw, bh = bg.size
    th = max(1, int(bh * scale))
    subj = subj.resize((max(1, int(subj.width * th / subj.height)), th), Image.LANCZOS)
    x = {"left": int(bw * 0.08), "center": (bw - subj.width) // 2, "right": bw - subj.width - int(bw * 0.08)}[position]
    comp = bg.copy()
    comp.paste(subj.convert("RGB"), (x, bh - subj.height), subj.getchannel("A"))
    noise = Image.effect_noise(comp.size, 18).convert("RGB")
    comp = Image.blend(comp, ImageChops.overlay(comp, noise), 0.05)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    image_id = f"{plate.get('release') or 'free'}_{stamp}_composite"
    comp.save(OUT / f"{image_id}.png")
    rec = {"id": image_id, "file": f"{image_id}.png", "made": datetime.now().isoformat(timespec="seconds"),
           "model": "local composite", "quality": "-", "size": f"{bw}x{bh}", "n": 1, "prompt": plate.get("prompt", ""),
           "references": [], "usage": {}, "cost_usd": 0.0, "decision": None, "release": plate.get("release"),
           "kind": "composite", "plate": plate_id, "photo": photo.name, "scale": scale, "position": position,
           "choice": plate.get("choice") or {}, "note": "local composite: his photo cut out on the Mac (rembg), nothing sent"}
    (OUT / f"{image_id}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    return rec
