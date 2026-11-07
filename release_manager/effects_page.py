"""Effects page (Machine-20): reads docs/brand/effects/effects.json.

The only write is the "mine" flag, set when Amir picks an effect on the page. Example images
live in docs/brand/effects/examples and are served only if a record names them.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

INDEX = Path("docs") / "brand" / "effects" / "effects.json"
EFFECTS_SUBDIR = Path("docs") / "brand" / "effects"
REQUIRED = ("id", "name", "family", "kind", "make", "face_safe", "what", "how", "source", "example", "mine")


class EffectsError(ValueError):
    """effects.json is missing, unreadable or fails validation."""


def load(project_root: Path) -> dict:
    p = project_root / INDEX
    if not p.is_file():
        raise EffectsError(f"no index at {p}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EffectsError(f"not valid JSON: {exc}") from exc
    errs = validate(data)
    if errs:
        raise EffectsError("; ".join(errs[:10]))
    return data


def validate(data: dict) -> list[str]:
    errs: list[str] = []
    if not isinstance(data, dict) or not isinstance(data.get("effects"), list):
        return ["top level needs an 'effects' list"]
    allowed = data.get("allowed") or {}
    seen = set()
    for r in data["effects"]:
        rid = r.get("id", "?")
        if rid in seen:
            errs.append(f"{rid}: duplicate id")
        seen.add(rid)
        for f in REQUIRED:
            if f not in r:
                errs.append(f"{rid}: missing '{f}'")
        for field in ("family", "kind", "make"):
            if allowed.get(field) and r.get(field) not in allowed[field]:
                errs.append(f"{rid}: {field} '{r.get(field)}' unknown")
        if "signature" in r and not isinstance(r["signature"], bool):
            errs.append(f"{rid}: signature must be true or false")
        if r.get("make") == "ai" and r.get("face_safe"):
            errs.append(f"{rid}: an AI effect cannot be face safe")
        ex = r.get("example") or ""
        if ex and (not ex.startswith("examples/") or ".." in ex or ex.startswith("/")):
            errs.append(f"{rid}: example must sit under examples/")
    return errs


def by_id(data: dict, rid: str):
    for r in data["effects"]:
        if r["id"] == rid:
            return r
    return None


def example_path(project_root: Path, r: dict):
    """The example file for a record, only if it exists inside the effects folder."""
    ex = (r or {}).get("example") or ""
    if not ex:
        return None
    base = (project_root / EFFECTS_SUBDIR).resolve()
    p = (base / ex).resolve()
    if base not in p.parents or not p.is_file():
        return None
    return p


def filter_effects(effects: list, args) -> list:
    fam, kind, make = args.get("family") or "", args.get("kind") or "", args.get("make") or ""
    q = (args.get("q") or "").strip().lower()
    out = []
    for r in effects:
        if fam and r["family"] != fam:
            continue
        if kind and r["kind"] != kind:
            continue
        if make == "safe" and not r["face_safe"]:
            continue
        if make and make != "safe" and r["make"] != make:
            continue
        if args.get("mine") and not r.get("mine"):
            continue
        if args.get("signature") and not r.get("signature"):
            continue
        if q and q not in " ".join([r["name"], r["what"], r["how"], r.get("notes", "")]).lower():
            continue
        out.append(r)
    return out


def counts(data: dict) -> dict:
    eff = data["effects"]
    fams = (data.get("allowed") or {}).get("family") or {}
    return {
        "family": [{"value": k, "label": v, "count": sum(1 for r in eff if r["family"] == k)} for k, v in fams.items()],
        "mine": sum(1 for r in eff if r.get("mine")),
        "signature": sum(1 for r in eff if r.get("signature")),
        "safe": sum(1 for r in eff if r["face_safe"]),
        "ai": sum(1 for r in eff if r["make"] == "ai"),
        "examples": sum(1 for r in eff if r.get("example")),
    }


FLAGS = ("mine", "signature")      # mine = "I like it" (the star); signature = the few that are the brand
USES = ("cover", "reel", "poster", "canvas")


def set_flag(project_root: Path, rid: str, field: str, value: bool) -> bool:
    """Set one record's flag and write the file atomically. False if the id or the flag is unknown."""
    if field not in FLAGS:
        return False
    data = load(project_root)
    r = by_id(data, rid)
    if r is None:
        return False
    r[field] = bool(value)
    p = project_root / INDEX
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".effects-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, p)
    return True


def set_mine(project_root: Path, rid: str, value: bool) -> bool:
    return set_flag(project_root, rid, "mine", value)


def release_effects(rel: dict) -> list:
    """The effects a release uses: [{"id", "used_in": [...]}] from brand.effects."""
    out = []
    for e in ((rel or {}).get("brand") or {}).get("effects") or []:
        if isinstance(e, dict) and e.get("id"):
            out.append({"id": e["id"], "used_in": [u for u in (e.get("used_in") or []) if u in USES]})
    return out


def set_release_effect(rel: dict, eid: str, used_in=None, remove: bool = False) -> dict:
    """Add, update or remove one effect in rel['brand']['effects']; keeps order, never duplicates."""
    brand = rel.setdefault("brand", {})
    cur = [e for e in release_effects(rel) if e["id"] != eid]
    if not remove:
        old = next((e for e in release_effects(rel) if e["id"] == eid), None)
        uses = [u for u in (used_in if used_in is not None else (old or {}).get("used_in", [])) if u in USES]
        entry = {"id": eid, "used_in": sorted(set(uses), key=USES.index)}
        idx = next((i for i, e in enumerate(release_effects(rel)) if e["id"] == eid), None)
        cur.insert(idx if idx is not None else len(cur), entry)
    brand["effects"] = cur
    return rel


def rows(data: dict, effects: list) -> list:
    """Effects grouped into one row per family, in the index's family order; empty families left out."""
    fams = (data.get("allowed") or {}).get("family") or {}
    out = []
    for k, label in fams.items():
        items = [r for r in effects if r["family"] == k]
        if items:
            names = ((data.get("allowed") or {}).get("groups") or {}).get(k) or []
            groups = []
            if names:
                pos = {n: i for i, n in enumerate(names)}
                items = sorted(items, key=lambda r: pos.get(r.get("group"), len(names)))   # stable: picks stay first inside a group
                groups = [{"name": n, "n": sum(1 for r in items if r.get("group") == n)} for n in names]
                groups = [g for g in groups if g["n"]]
                if len(groups) < 2:
                    groups = []          # one group is no choice: no buttons
            out.append({"family": k, "label": label, "cards": items, "groups": groups})
    return out


def counts_by_kind(data: dict) -> dict:
    """How many effects sit on each tab: still = Photo, motion = Video."""
    out = {"still": 0, "motion": 0}
    for r in data["effects"]:
        if r.get("kind") in out:
            out[r["kind"]] += 1
    return out


def sort_effects(data: dict, effects: list) -> list:
    """Amir's picks first, then by family in the index's order (our looks lead), then file order."""
    order = {k: i for i, k in enumerate(((data.get("allowed") or {}).get("family") or {}).keys())}
    pos = {r["id"]: i for i, r in enumerate(data["effects"])}
    return sorted(effects, key=lambda r: (not r.get("mine"), order.get(r["family"], 99), pos.get(r["id"], 0)))
