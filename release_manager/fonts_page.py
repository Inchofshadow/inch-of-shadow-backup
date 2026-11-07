"""Fonts page (Machine-19): reads docs/brand/fonts/fonts.json, never writes it.

Every face is shown from a local file under docs/brand/fonts (served by the Release Manager,
only files the index lists) or from a macOS system font by name. No CDN, no download.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

INDEX = Path("docs") / "brand" / "fonts" / "fonts.json"
FONTS_SUBDIR = Path("docs") / "brand" / "fonts"
REQUIRED = ("id", "name", "group", "status", "licence", "files", "system", "sources")

# what a badge says, by licence
BADGE = {
    "owned": "OWNED", "free": "FREE", "trial": "TRIAL, looking only", "canva only": "CANVA only",
    "system": "MAC system", "personal use only": "PERSONAL use only", "none": "NOT owned",
}
# which licences may go into public work as they are
PUBLIC_OK = {"owned", "free"}


class FontsError(ValueError):
    """fonts.json is missing, unreadable or fails validation."""


def load(project_root: Path) -> dict:
    p = project_root / INDEX
    if not p.is_file():
        raise FontsError(f"no index at {p}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FontsError(f"not valid JSON: {exc}") from exc
    errs = validate(data)
    if errs:
        raise FontsError("; ".join(errs[:10]))
    return data


def validate(data: dict) -> list[str]:
    errs: list[str] = []
    if not isinstance(data, dict) or not isinstance(data.get("fonts"), list):
        return ["top level needs a 'fonts' list"]
    allowed = data.get("allowed") or {}
    seen = set()
    for r in data["fonts"]:
        rid = r.get("id", "?")
        if rid in seen:
            errs.append(f"{rid}: duplicate id")
        seen.add(rid)
        for f in REQUIRED:
            if f not in r:
                errs.append(f"{rid}: missing '{f}'")
        if allowed.get("group") and r.get("group") not in allowed["group"]:
            errs.append(f"{rid}: group '{r.get('group')}' unknown")
        for field in ("status", "licence"):
            if allowed.get(field) and r.get(field) not in allowed[field]:
                errs.append(f"{rid}: {field} '{r.get(field)}' not allowed")
        for f in r.get("files") or []:
            if ".." in Path(f).parts or f.startswith("/"):
                errs.append(f"{rid}: file path leaves the fonts folder: {f}")
    return errs


# --- picking the file a card shows -------------------------------------------------------

_PREFER = ("display", "regular", "book", "roman", "medium", "bold", "italic")


def primary_file(r: dict) -> str | None:
    """The one file a card is set in: the one the tools use if any, else a regular/display cut."""
    files = r.get("files") or []
    if not files:
        return None
    statics = [f for f in files if "variable" not in f.lower() and "vf" not in Path(f).stem.lower()] or files

    def score(f: str) -> tuple:
        stem = Path(f).stem.lower()
        rank = next((i for i, w in enumerate(_PREFER) if w in stem), len(_PREFER))
        return (rank, "italic" in stem and rank != _PREFER.index("italic"), len(stem))
    return sorted(statics, key=score)[0]


def style_label(file_rel: str) -> str:
    stem = Path(file_rel).stem
    stem = re.sub(r"(?i)[-_ ]?trial", "", stem)
    return stem.replace("-", " ").replace("_", " ").strip()


def css_family(rid: str, i: int = 0) -> str:
    return f"f-{rid}-{i}"


def face_rules(r: dict, url_for_file, all_files: bool = False) -> list[dict]:
    """@font-face rules for a record: [{family, src, label}]. System fonts use local()."""
    out = []
    files = r.get("files") or []
    chosen = files if all_files else ([primary_file(r)] if files else [])
    for i, f in enumerate(chosen):
        if not f:
            continue
        fmt = "opentype" if f.lower().endswith(".otf") else "truetype"
        out.append({"family": css_family(r["id"], i), "src": f"url('{url_for_file(r['id'], f)}') format('{fmt}')",
                    "label": style_label(f), "file": f})
    if not out:
        for j, name in enumerate(r.get("system") or []):
            out.append({"family": css_family(r["id"], 100 + j), "src": f"local('{name}')", "label": name, "file": ""})
    return out


def shape(r: dict) -> dict:
    """The fields the templates need on top of the record."""
    return dict(r, badge=BADGE.get(r["licence"], r["licence"]), public_ok=r["licence"] in PUBLIC_OK,
                has_file=bool(r.get("files")) or bool(r.get("system")),
                n_styles=len(r.get("files") or []) or len(r.get("system") or []))


# --- filters -----------------------------------------------------------------------------

def filter_fonts(fonts: list[dict], args) -> list[dict]:
    group = (args.get("group") or "").strip()
    status = (args.get("status") or "").strip()
    licence = (args.get("licence") or "").strip()
    where = (args.get("where") or "").strip()
    q = (args.get("q") or "").strip().lower()
    out = []
    for r in fonts:
        if group and r.get("group") != group:
            continue
        if status and r.get("status") != status:
            continue
        if licence and r.get("licence") != licence:
            continue
        if where == "mac" and not (r.get("files") or r.get("system")):
            continue
        if where == "nofile" and (r.get("files") or r.get("system")):
            continue
        if where == "canva" and r.get("canva") != "yes":
            continue
        if q:
            hay = " ".join(str(r.get(k, "")) for k in ("name", "seen_on", "get_hint", "tags", "notes", "status_note", "canva_note")).lower()
            if q not in hay:
                continue
        out.append(r)
    return out


STATUS_ORDER = {"default now": 0, "fallback": 1, "guest": 2, "potential": 3, "idea": 4, "in the tools": 5, "set aside": 6, "out as main": 7}


def sort_fonts(fonts: list[dict], sort: str) -> list[dict]:
    if sort == "name":
        return sorted(fonts, key=lambda r: r["name"].lower())
    if sort == "status":
        return sorted(fonts, key=lambda r: (STATUS_ORDER.get(r["status"], 9), r["group"], r["name"].lower()))
    return sorted(fonts, key=lambda r: (r["group"], STATUS_ORDER.get(r["status"], 9), r["name"].lower()))


def counts(data: dict, fonts: list[dict]) -> dict:
    allowed = data.get("allowed") or {}
    return {
        "group": [{"value": g, "label": label, "count": sum(1 for r in fonts if r["group"] == g)} for g, label in allowed.get("group", {}).items()],
        "status": [{"value": s, "count": sum(1 for r in fonts if r["status"] == s)} for s in allowed.get("status", [])],
        "licence": [{"value": s, "count": sum(1 for r in fonts if r["licence"] == s)} for s in allowed.get("licence", [])],
        "mac": sum(1 for r in fonts if r.get("files") or r.get("system")),
        "canva": sum(1 for r in fonts if r.get("canva") == "yes"),
    }


def by_id(data: dict, rid: str) -> dict | None:
    return next((r for r in data["fonts"] if r["id"] == rid), None)


def file_allowed(project_root: Path, r: dict, file_rel: str) -> Path | None:
    """A font file is served only when the record lists it and it sits inside docs/brand/fonts."""
    if file_rel not in (r.get("files") or []):
        return None
    base = (project_root / FONTS_SUBDIR).resolve()
    p = (base / file_rel).resolve()
    if base not in p.parents or not p.is_file():
        return None
    return p


def for_release(data: dict, title_font: str) -> dict | None:
    """The record a release's brand.title_font names (by id or by name), if any."""
    t = (title_font or "").strip().lower()
    if not t:
        return None
    return next((r for r in data["fonts"] if r["id"] == t or r["name"].lower() == t), None)


def releases_using(project_root: Path, r: dict) -> list[dict]:
    """Releases whose brand.title_font names this face."""
    out = []
    for f in sorted((project_root / "releases").glob("*.json")):
        if ".bak" in f.name:
            continue
        try:
            rel = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        tf = ((rel.get("brand") or {}).get("title_font") or "").strip().lower()
        if tf and (tf == r["id"] or tf == r["name"].lower()):
            out.append({"slug": rel.get("slug") or f.stem, "title": (rel.get("metadata") or {}).get("title", f.stem)})
    return out
