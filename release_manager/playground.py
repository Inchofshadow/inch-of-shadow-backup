"""Artwork playground (Machine-21): one page per release to try looks, colour, accent and fonts
on a base artwork, with Spotify, record (2c) and Instagram previews.

The base image is named in releases/<slug>.json brand.playground.base and must sit under
artwork/. Looks are rendered locally by print_looks.py and cached in the temp folder; nothing
is written into the project. The page composes and exports in the browser.
"""
from __future__ import annotations

import hashlib
import os
import re
import tempfile
from pathlib import Path

CACHE = Path(tempfile.gettempdir()) / "ios-playground-cache"
SLUG = re.compile(r"[a-z0-9-]+")

# accent swatches: one colour at most on a cover (Amir 2026-10-13)
ACCENTS = [
    ("none", ""), ("APC gold", "#C08A3E"), ("oxblood", "#7A1F2B"), ("signal red", "#B3262E"),
    ("cobalt", "#2E4A8B"), ("sage", "#6E8B6A"), ("moon violet", "#6B5E8C"), ("bone", "#EDE6DA"),
]


def base_path(project_root: Path, rel: dict, key: str = "base") -> Path | None:
    """The release's playground base image (or another image named under brand.playground, such as
    accent_layer), only if it sits inside artwork/ and exists."""
    raw = ((rel or {}).get("brand") or {}).get("playground", {}).get(key) or ""
    if not raw:
        return None
    root = (project_root / "artwork").resolve()
    p = (project_root / raw).resolve()
    if root not in p.parents or not p.is_file():
        return None
    return p


# extra covers to switch between in the page: every image in a folder named
# artwork/**/playground-covers/<slug>/ (no release-file edit needed; Half the Night noir, 2026-11-04)
COVER_EXT = {".png", ".jpg", ".jpeg", ".webp"}
COVER_NAME = re.compile(r"[A-Za-z0-9._-]+")


def cover_dirs(project_root: Path, slug: str) -> list[Path]:
    if not SLUG.fullmatch(slug or ""):
        return []
    root = (project_root / "artwork").resolve()
    out = []
    for d in sorted(root.glob("**/playground-covers/" + slug)):
        d = d.resolve()
        if d.is_dir() and root in d.parents:
            out.append(d)
    return out


def covers(project_root: Path, slug: str) -> list[dict]:
    """The selectable covers: name (the file name, unique per release) and a readable label."""
    seen, out = set(), []
    for d in cover_dirs(project_root, slug):
        for f in sorted(d.iterdir()):
            if (f.suffix.lower() in COVER_EXT and f.is_file() and COVER_NAME.fullmatch(f.name) and f.name not in seen
                    and ".title." not in f.name):
                seen.add(f.name)
                out.append({"name": f.name, "label": f.stem.replace("-", " ").replace("_", " ")})
    return out


def cover_path(project_root: Path, slug: str, name: str) -> Path | None:
    """One cover by its file name only (no paths), looked up in that release's cover folders."""
    if not COVER_NAME.fullmatch(name or ""):
        return None
    for d in cover_dirs(project_root, slug):
        p = (d / name).resolve()
        if p.parent == d and p.is_file() and p.suffix.lower() in COVER_EXT:
            return p
    return None


def overlay_path(project_root: Path, slug: str, name: str) -> Path | None:
    """Optional title overlay for a cover: '<cover stem>.title.png' next to it (white text on transparent)."""
    p = cover_path(project_root, slug, name)
    if p is None:
        return None
    o = p.with_name(p.stem + ".title.png")
    return o if o.is_file() else None


def sized(src: Path, w: int) -> Path:
    """A smaller JPEG copy for the effects wall tiles, cached next to the look cache."""
    from PIL import Image
    w = max(120, min(1080, int(w)))
    h = hashlib.sha1((str(src) + str(src.stat().st_mtime)).encode()).hexdigest()[:16]
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"sz-{h}-{w}.jpg"
    if not out.exists():
        im = Image.open(src).convert("RGB")
        im.thumbnail((w, w), Image.LANCZOS)
        im.save(out, quality=86)
    return out


# effects wall: kept picks per release (plans/playground-wall/<slug>.json, never the release file)
MAX_KEPT = 80


def wall_file(project_root: Path, slug: str) -> Path:
    return project_root / "plans" / "playground-wall" / f"{slug}.json"


def wall_kept(project_root: Path, slug: str) -> list:
    import json as _json
    f = wall_file(project_root, slug)
    try:
        return list(_json.loads(f.read_text()).get("kept") or [])
    except Exception:
        return []


def wall_toggle(project_root: Path, slug: str, item: dict, now: str) -> list:
    """Keep or un-keep one pick {cover, look, wet, palette}. Raises ValueError on bad input."""
    import json as _json
    if not SLUG.fullmatch(slug or "") or not isinstance(item, dict):
        raise ValueError("bad pick")
    cover = str(item.get("cover") or "")
    look = str(item.get("look") or "")
    if cover and not COVER_NAME.fullmatch(cover):
        raise ValueError("bad cover")
    if look and not re.fullmatch(r"[a-z0-9]+", look):
        raise ValueError("bad look")
    try:
        wet = max(0, min(100, int(item.get("wet", 100))))
    except (TypeError, ValueError):
        raise ValueError("bad strength")
    palette = str(item.get("palette") or "")
    if palette and not re.fullmatch(r"[a-z]{1,20}", palette):
        raise ValueError("bad palette")
    kept = wall_kept(project_root, slug)
    key = (cover, look)
    rest = [k for k in kept if (k.get("cover"), k.get("look")) != key]
    if len(rest) == len(kept):
        rest.append({"cover": cover, "look": look, "wet": wet, "palette": palette, "saved": now})
    f = wall_file(project_root, slug)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(_json.dumps({"kept": rest[-MAX_KEPT:]}, indent=1))
    return rest[-MAX_KEPT:]


# stage 1 element builder (Half the Night main artwork, 2026-11-05): every combination is a pre-rendered file in
# artwork/**/playground-elements/<slug>/ named el-<moon>-<owl>-<stars>-<tree>-<line>.jpg, plus el.title.png
ELEMENT_NAME = re.compile(r"el-(cream|red)-(none|on)-(none|few)-(keep|remove)-[0-4]\.jpg|el\.title\.png")


def element_path(project_root: Path, slug: str, name: str) -> Path | None:
    if not SLUG.fullmatch(slug or "") or not ELEMENT_NAME.fullmatch(name or ""):
        return None
    root = (project_root / "artwork").resolve()
    for d in sorted(root.glob("**/playground-elements/" + slug)):
        p = (d / name).resolve()
        if root in p.parents and p.parent == d.resolve() and p.is_file():
            return p
    return None


# IG profile grid preview (2026-11-05): artwork/**/playground-iggrid/<slug>/grid-K<n>.jpg, one per colour save
IGGRID_NAME = re.compile(r"grid-K[0-9]{1,2}\.jpg")
IGFEED_NAME = re.compile(r"feed-[0-9]{2}\.jpg")


def iggrid_files(project_root: Path, slug: str) -> list:
    if not SLUG.fullmatch(slug or ""):
        return []
    root = (project_root / "artwork").resolve()
    out = []
    for d in sorted(root.glob("**/playground-iggrid/" + slug)):
        out += [f.name for f in d.iterdir() if IGGRID_NAME.fullmatch(f.name)]
    return sorted(set(out), key=lambda n: int(n[6:-4]))


def iggrid_feed(project_root: Path, slug: str) -> list:
    if not SLUG.fullmatch(slug or ""):
        return []
    root = (project_root / "artwork").resolve()
    out = []
    for d in sorted(root.glob("**/playground-iggrid/" + slug)):
        out += [f.name for f in d.iterdir() if IGFEED_NAME.fullmatch(f.name)]
    return sorted(set(out))


def iggrid_path(project_root: Path, slug: str, name: str) -> Path | None:
    if not SLUG.fullmatch(slug or "") or not (IGGRID_NAME.fullmatch(name or "") or IGFEED_NAME.fullmatch(name or "")):
        return None
    root = (project_root / "artwork").resolve()
    for d in sorted(root.glob("**/playground-iggrid/" + slug)):
        p = (d / name).resolve()
        if root in p.parents and p.parent == d.resolve() and p.is_file():
            return p
    return None


# stage 3b layout page (2026-11-05): title faces served to the page. macOS system faces are loaded by the
# browser with local(); only these free files are served (whitelist, no user paths).
LAYOUT_FONT_FILES = {
    "gloock": "docs/brand/fonts/free/Gloock-Regular.ttf",
    "mohave": "docs/brand/fonts/free/Mohave-700.ttf",
    "viking": "docs/brand/fonts/free/Viking-Steffmann.ttf",
    "jost3": "docs/brand/fonts/free/Jost-300.ttf",
    "jost5": "docs/brand/fonts/free/Jost-500.ttf",
    "unicook": "docs/brand/fonts/free/UnifrakturCook-Bold.ttf",
    "unimag": "docs/brand/fonts/free/UnifrakturMaguntia-Book.ttf",
    "eckmann": "docs/brand/fonts/free/CAT-Eckmann.ttf",
    "pirata": "docs/brand/fonts/free/PirataOne-Regular.ttf",
    "barlowc": "docs/brand/fonts/free/BarlowCondensed-ExtraBold.ttf",   # free (OFL) match for Avenir Next Condensed Heavy, 11-06
    "fraunces": "docs/brand/fonts/free/Fraunces144ptSuperSoft-Black.otf",   # free (OFL), title round 11-09
    "neuzeits": "docs/brand/fonts/free/CATNeuzeit Schatten.ttf",   # free (OFL), title round 11-09
    "switzer": "docs/brand/fonts/free/Switzer/Switzer-Black.otf",   # free (ITF FFL, commercial OK), title round 11-09
}


def layout_font_path(project_root: Path, key: str) -> Path | None:
    rel = LAYOUT_FONT_FILES.get(key or "")
    if not rel:
        return None
    p = (project_root / rel).resolve()
    return p if p.is_file() and project_root.resolve() in p.parents else None


# extra elements made for a layout (2026-11-05: one AI tree, cut out locally): artwork/**/playground-extras/<slug>/
EXTRA_NAME = re.compile(r"tree[0-9]{1,2}\.png")


def extra_path(project_root: Path, slug: str, name: str) -> Path | None:
    if not SLUG.fullmatch(slug or "") or not EXTRA_NAME.fullmatch(name or ""):
        return None
    root = (project_root / "artwork").resolve()
    for d in sorted(root.glob("**/playground-extras/" + slug)):
        p = (d / name).resolve()
        if root in p.parents and p.parent == d.resolve() and p.is_file():
            return p
    return None


def layouts_file(project_root: Path, slug: str) -> Path:
    return project_root / "plans" / "playground-wall" / f"{slug}-layouts.json"


def _layouts_raw(project_root: Path, slug: str) -> dict:
    import json as _json
    try:
        d = _json.loads(layouts_file(project_root, slug).read_text())
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def _layouts_for_write(project_root: Path, slug: str) -> dict:
    """The keeps file for a change. A file that exists but cannot be read is NEVER treated as empty:
    the next save would replace every keep with one (Fable gate 2026-11-15). Raises ValueError instead."""
    import json as _json
    f = layouts_file(project_root, slug)
    if not f.exists():
        return {}
    try:
        d = _json.loads(f.read_text())
    except Exception:
        raise ValueError("the keeps file cannot be read (%s): nothing saved, restore it first" % f.name)
    if not isinstance(d, dict) or not isinstance(d.get("kept", []), list):
        raise ValueError("the keeps file has an unexpected shape (%s): nothing saved" % f.name)
    return d


def _layouts_save(project_root: Path, slug: str, data: dict) -> None:
    """Write the keeps file through a temp file, so a crash never leaves it half-written."""
    import json as _json
    f = layouts_file(project_root, slug)
    f.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(f.parent), prefix="." + f.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(_json.dumps(data, indent=1))
        os.replace(tmp, f)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def with_ids(kept: list, next_id: int = 0) -> tuple[list, int]:
    """Fixed keep IDs (System 97, 2026-11-10): a keep keeps its number when others come or go.
    Keeps without an id get the next numbers in list order, so a file from before IDs gets 1..n:
    exactly the numbers the page showed (Half the Night: #50 stays #50). Returns (keeps, next free id);
    next_id never goes down, so an un-kept number is never given out again."""
    used = [k["id"] for k in kept if isinstance(k.get("id"), int) and not isinstance(k.get("id"), bool)]
    nxt = max([next_id or 0, (max(used) + 1) if used else 1])
    out, seen = [], set()
    for k in kept:
        k = dict(k)
        if not isinstance(k.get("id"), int) or isinstance(k.get("id"), bool) or k["id"] in seen:
            k["id"] = nxt
            nxt += 1
        seen.add(k["id"])
        out.append(k)
    return out, nxt


def layouts_kept(project_root: Path, slug: str) -> list:
    """The kept layouts, each with its fixed id (filled in on read for a file from before IDs; the file
    itself only changes on the next keep or un-keep, or with migrate_layout_ids)."""
    d = _layouts_raw(project_root, slug)
    return with_ids(list(d.get("kept") or []), int(d.get("next_id") or 0))[0]


def migrate_layout_ids(project_root: Path, slug: str, dry_run: bool = True) -> dict:
    """Write the fixed ids into a layouts file once. Nothing but the id (and next_id) is added: order,
    count and every other field stay as they are. dry_run only reports."""
    import json as _json
    d = _layouts_for_write(project_root, slug)
    before = list(d.get("kept") or [])
    after, nxt = with_ids(before, int(d.get("next_id") or 0))
    def bare(k):
        return {x: v for x, v in k.items() if x != "id"}
    same = len(before) == len(after) and all(bare(a) == bare(b) for a, b in zip(after, before))
    if not same:
        raise RuntimeError("migration would change a keep")
    report = {"count_before": len(before), "count_after": len(after), "ids": [k["id"] for k in after], "next_id": nxt,
              "changed": any(b.get("id") != a["id"] for a, b in zip(after, before)) or d.get("next_id") != nxt}
    if not dry_run and report["changed"]:
        _layouts_save(project_root, slug, dict(d, kept=after, next_id=nxt))
    return report


_LAYOUT_NUM = {"save": (0, 99), "lines": (1, 3), "x": (-0.5, 1.5), "y": (-0.5, 1.5), "size": (0.01, 0.5), "lead": (-0.5, 1.5),
               "track": (-0.2, 1.0), "nsize": (0.005, 0.2), "mdx": (-1.0, 1.0), "mdy": (-1.0, 1.0), "ms": (0.2, 4.0),
               "line": (0, 4), "ntrack": (-0.2, 1.0), "ntx": (-0.5, 1.5), "nty": (-0.5, 1.5), "nts": (0.05, 1.5), "fxw": (0, 100), "os": (0.3, 2.0), "lw": (0.0, 1.0), "hglow": (0.0, 1.0),   # lw: cut-line strength (11-09)
               "fgrain": (0.0, 1.0), "fcorner": (0.0, 1.0), "rim": (0.0, 1.0), "rimx": (-0.5, 1.5), "rimy": (-0.5, 1.5)}   # finish stages (System 93)
_LAYOUT_STR = {"font": r"[a-z0-9]{1,20}", "align": r"left|center|right", "color": r"[a-z]{1,12}", "npos": r"under|bottom|top",
               "nfont": r"[a-z0-9]{1,20}", "ncolor": r"[a-z]{1,12}", "tree": r"keep|remove",
               "starset": r"(-?[0-9.]{1,7},-?[0-9.]{1,7},[01](;|$)){0,40}", "ntr": r"none|left|right",
               "starplus": r"(-?[0-9.]{1,7},-?[0-9.]{1,7},[0-9]{1,2}(;|$)){0,8}",   # added stars: dx,dy,copy of star n (11-09)
               "cols": r"([a-z]{1,6}=[a-z]{1,8}(;|$)){0,8}", "rimcol": r"(auto|red|gold|ivory|cream)?", "fx": r"[a-z0-9]{0,30}", "fxmix": r"([a-z0-9]{1,30}:[0-9]{1,3}(:[a-z]{1,8})?(;|$)){0,5}"}
_LAYOUT_BOOL = ("name", "owl", "stars", "flip", "nt", "ntf", "tgrain", "tshadow")   # tgrain/tshadow: grain + soft shadow on the text (Amir's pick 11-09)


# what a keep from before a setting existed means (older pages send none of these): the picture as it was
_LAYOUT_OPTIONAL = {"lw": 1.0, "hglow": 0.0, "fgrain": 0.0, "fcorner": 0.0, "rim": 0.0, "rimx": 0.75, "rimy": 0.2, "rimcol": ""}


def _same_layout(kept: dict, clean: dict) -> bool:
    """A stored keep equals this layout; a field the keep does not have counts as its old meaning."""
    for x, v in clean.items():
        have = kept.get(x, _LAYOUT_OPTIONAL.get(x))
        if x in _LAYOUT_BOOL:
            have = bool(have)
        elif x in _LAYOUT_STR:
            have = str(have or "")
        if have != v:
            return False
    return True


def _clean_layout(item: dict) -> dict:
    if not isinstance(item, dict):
        raise ValueError("bad layout")
    out = {}
    for k, (lo, hi) in _LAYOUT_NUM.items():
        v = item.get(k, _LAYOUT_OPTIONAL.get(k))   # older pages send no lw, finish, ...
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not lo <= v <= hi:
            raise ValueError("bad " + k)
        out[k] = round(float(v), 4) if k not in ("save", "lines", "line") else int(v)
    for k, rx in _LAYOUT_STR.items():
        v = str(item.get(k) or _LAYOUT_OPTIONAL.get(k, ""))
        if not re.fullmatch(rx, v):
            raise ValueError("bad " + k)
        out[k] = v
    for k in _LAYOUT_BOOL:
        out[k] = bool(item.get(k))
    return out


LAYOUTS_MAX = 200


def layouts_toggle(project_root: Path, slug: str, item: dict, now: str) -> list:
    """Keep or un-keep one layout (text + moon placement on a colour save). Raises ValueError on bad input."""
    import json as _json
    if not SLUG.fullmatch(slug or ""):
        raise ValueError("bad slug")
    clean = _clean_layout(item)
    raw = _layouts_for_write(project_root, slug)
    kept, nxt = with_ids(list(raw.get("kept") or []), int(raw.get("next_id") or 0))
    same = [k for k in kept if _same_layout(k, clean)]
    if same:
        kept = [k for k in kept if k not in same]
    else:
        if len(kept) >= LAYOUTS_MAX:   # refuse, never drop old keeps silently (gate review 2026-11-07)
            raise ValueError("%d layouts kept already: un-keep one first" % LAYOUTS_MAX)
        kept = kept + [dict(clean, saved=now, id=nxt)]
        nxt += 1
    _layouts_save(project_root, slug, dict(raw, kept=kept, next_id=nxt))
    return kept


def elements_file(project_root: Path, slug: str) -> Path:
    return project_root / "plans" / "playground-wall" / f"{slug}-elements.json"


def elements_kept(project_root: Path, slug: str) -> list:
    import json as _json
    try:
        return list(_json.loads(elements_file(project_root, slug).read_text()).get("kept") or [])
    except Exception:
        return []


def elements_toggle(project_root: Path, slug: str, name: str, now: str) -> list:
    """Keep or un-keep one element combination by its file name. Raises ValueError on bad input."""
    import json as _json
    if not SLUG.fullmatch(slug or "") or not ELEMENT_NAME.fullmatch(name or "") or not name.startswith("el-"):
        raise ValueError("bad combination")
    kept = elements_kept(project_root, slug)
    rest = [k for k in kept if k.get("name") != name]
    if len(rest) == len(kept):
        rest.append({"name": name, "saved": now})
    f = elements_file(project_root, slug)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(_json.dumps({"kept": rest[-MAX_KEPT:]}, indent=1))
    return rest[-MAX_KEPT:]


# stage 2 colours (2026-11-05): per kept element pick, soft masks cut by build/colour_layers.py in
# artwork/**/playground-colours/<slug>/<pick>/ ; the page paints each element live
PICK_NAME = re.compile(r"el-(cream|red)-(none|on)-(none|few)-(keep|remove)-[0-4]")
COLOUR_FILES = {"base.jpg", "hill.png", "trees.png", "moon.png", "owl.png", "stars.png", "line.png", "shade.png", "meta.json"}
COLOUR_ELEMENTS = {"hill", "trees", "moon", "owl", "stars", "line"}


def colour_dirs(project_root: Path, slug: str) -> list[Path]:
    if not SLUG.fullmatch(slug or ""):
        return []
    root = (project_root / "artwork").resolve()
    return [d.resolve() for d in sorted(root.glob("**/playground-colours/" + slug)) if d.is_dir() and root in d.resolve().parents]


def colour_picks(project_root: Path, slug: str) -> list[str]:
    out = []
    for d in colour_dirs(project_root, slug):
        out += [p.name for p in sorted(d.iterdir()) if p.is_dir() and PICK_NAME.fullmatch(p.name) and (p / "meta.json").is_file()]
    return out


def colour_path(project_root: Path, slug: str, pick: str, name: str) -> Path | None:
    if not PICK_NAME.fullmatch(pick or "") or name not in COLOUR_FILES:
        return None
    for d in colour_dirs(project_root, slug):
        p = (d / pick / name).resolve()
        if p.parent.parent == d and p.is_file():
            return p
    return None


def colours_file(project_root: Path, slug: str) -> Path:
    return project_root / "plans" / "playground-wall" / f"{slug}-colours.json"


def colours_kept(project_root: Path, slug: str) -> list:
    import json as _json
    try:
        return list(_json.loads(colours_file(project_root, slug).read_text()).get("kept") or [])
    except Exception:
        return []


def colours_toggle(project_root: Path, slug: str, item: dict, now: str) -> list:
    """Keep or un-keep one coloured version {pick, cols: {element: colour}}. Raises ValueError on bad input."""
    import json as _json
    if not SLUG.fullmatch(slug or "") or not isinstance(item, dict):
        raise ValueError("bad pick")
    pick = str(item.get("pick") or "")
    cols = item.get("cols") or {}
    if not PICK_NAME.fullmatch(pick) or not isinstance(cols, dict):
        raise ValueError("bad pick")
    clean = {}
    for k, val in cols.items():
        if k not in COLOUR_ELEMENTS or not re.fullmatch(r"[a-z]{1,12}", str(val)):
            raise ValueError("bad colour")
        clean[k] = str(val)
    kept = colours_kept(project_root, slug)
    rest = [k for k in kept if not (k.get("pick") == pick and k.get("cols") == clean)]
    if len(rest) == len(kept):
        rest.append({"pick": pick, "cols": clean, "saved": now})
    f = colours_file(project_root, slug)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(_json.dumps({"kept": rest[-MAX_KEPT:]}, indent=1))
    return rest[-MAX_KEPT:]


# fonts Amir removed from the Layout page (plans/playground-wall/<slug>-fonts-hidden.json), 2026-11-06
def fonts_hidden_file(project_root: Path, slug: str) -> Path:
    return project_root / "plans" / "playground-wall" / f"{slug}-fonts-hidden.json"


def fonts_hidden(project_root: Path, slug: str) -> list:
    import json as _json
    try:
        return [str(x) for x in _json.loads(fonts_hidden_file(project_root, slug).read_text()).get("hidden") or []]
    except Exception:
        return []


def fonts_hide_toggle(project_root: Path, slug: str, key: str) -> list:
    import json as _json
    if not SLUG.fullmatch(slug or "") or not re.fullmatch(r"[tn][a-z0-9]{1,30}", key or ""):
        raise ValueError("bad font")
    h = fonts_hidden(project_root, slug)
    h = [x for x in h if x != key] if key in h else h + [key]
    f = fonts_hidden_file(project_root, slug)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(_json.dumps({"hidden": h}, indent=1))
    return h


# effects Amir removed from the wall as "doesn't fit" (plans/playground-wall/<slug>-hidden.json), 2026-11-05
def wall_hidden_file(project_root: Path, slug: str) -> Path:
    return project_root / "plans" / "playground-wall" / f"{slug}-hidden.json"


def wall_hidden(project_root: Path, slug: str) -> list:
    import json as _json
    try:
        return [str(x) for x in _json.loads(wall_hidden_file(project_root, slug).read_text()).get("hidden") or []]
    except Exception:
        return []


def wall_hide_toggle(project_root: Path, slug: str, look: str) -> list:
    import json as _json
    if not SLUG.fullmatch(slug or "") or not re.fullmatch(r"[a-z0-9]{1,30}", look or ""):
        raise ValueError("bad look")
    h = wall_hidden(project_root, slug)
    h = [x for x in h if x != look] if look in h else h + [look]
    f = wall_hidden_file(project_root, slug)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(_json.dumps({"hidden": h}, indent=1))
    return h


# looks Amir ticked for a release (Half the Night: noir side page round looks-1, 2026-11-04); the wall shows these first
WALL_PICKS = {
    "pinocchio-single": ["xerox", "halftone", "engraving", "solarisation", "dither", "scanlines", "halation",
                         "window", "nightvision", "pixelsort", "monotint"],
}


# release colour ramps (dark -> light) for the palette control; Half the Night = R. Missing ramp (plans/half-the-night-cover-v2.md)
RAMPS = {
    "pinocchio-single": {"name": "R. Missing", "stops": ["#010107", "#141530", "#43456D", "#666A9C", "#7F84B7", "#A0A7DB", "#B4C2F8"],
                         "shares": [17, 35, 36, 12]},
}


def accent_layer_path(project_root: Path, rel: dict) -> Path | None:
    """A transparent PNG drawn on top of every filter, so its colour survives (the 10% accent)."""
    return base_path(project_root, rel, "accent_layer")


def file_version(p: Path | None) -> str:
    """Changes when the file changes, so the browser never shows an old cached image."""
    return str(int(p.stat().st_mtime)) if p else ""


def looks() -> list[dict]:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import print_looks as pl
    return [{"key": k, "code": v[0], "name": v[1], "note": v[2]} for k, v in pl.LOOKS.items()]


def look_image(base: Path, look: str, scale: int = 1) -> Path:
    """The base put through one print look, cached by file content, look and scale.
    scale 2-4 runs the look on a smaller copy and enlarges it hard, so dots, pixels and
    lines get coarser (the 'size' slider)."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import print_looks as pl
    if look not in pl.LOOKS:
        raise ValueError("unknown look")
    scale = max(1, min(4, int(scale)))
    h = hashlib.sha1(base.read_bytes()).hexdigest()[:16]
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"{h}-{look}-{scale}.png"
    if not out.exists():
        import os
        from PIL import Image
        im = pl.load(base)
        tmp = out.with_name(out.name + f".{os.getpid()}.{id(im)}.tmp")
        if scale > 1:
            small = im.resize((im.width // scale, im.height // scale), Image.LANCZOS)
            pl.apply_look(small, look).resize(im.size, Image.NEAREST).save(tmp, format="PNG")
        else:
            pl.apply_look(im, look).save(tmp, format="PNG")
        os.replace(tmp, out)
    return out


def look_on_bytes(data: bytes, look: str) -> Path:
    """One print look on an image the Layout page sends (its live picture, no text). The bytes must be a
    real image of at most 1600 px; it is stored by content hash in the cache, then run like any cover."""
    from io import BytesIO
    from PIL import Image
    if not data or len(data) > 6_000_000:
        raise ValueError("bad image")
    try:
        im = Image.open(BytesIO(data))
        im.verify()
        im = Image.open(BytesIO(data)).convert("RGB")
    except Exception:
        raise ValueError("bad image")
    if max(im.size) > 1600:
        raise ValueError("image too large")
    CACHE.mkdir(parents=True, exist_ok=True)
    src = CACHE / ("layout-" + hashlib.sha1(data).hexdigest()[:16] + ".png")
    if not src.exists():   # written whole, then renamed: two requests for the same picture at once never see a half file
        import os
        tmp = src.with_name(src.name + f".{os.getpid()}.{id(data)}.tmp")
        im.save(tmp, format="PNG")
        os.replace(tmp, src)
    return look_image(src, look)


def font_choices(fonts_data: dict, url_for_file) -> list[dict]:
    """Fonts with a file on this Mac or a macOS system font, with licence badges."""
    from release_manager import fonts_page as fp
    out = []
    for r in fp.sort_fonts(fonts_data["fonts"], "group"):
        faces = fp.face_rules(r, url_for_file)
        if not faces:
            continue
        x = fp.shape(r)
        out.append({"id": r["id"], "name": r["name"], "family": faces[0]["family"], "src": faces[0]["src"],
                    "badge": x["badge"], "public_ok": x["public_ok"], "group": r["group"], "licence": r["licence"]})
    return out


MAX_VERSIONS = 60
MAX_STATE = 60_000


def versions(rel: dict) -> list:
    return list((((rel or {}).get("brand") or {}).get("playground") or {}).get("versions") or [])


def save_version(rel: dict, name: str, state, now: str) -> dict:
    """Add (or overwrite by name) one saved setting on the release. Raises ValueError on bad input."""
    import json as _json
    name = (name or "").strip()[:60]
    if not name:
        raise ValueError("give the version a name")
    if not isinstance(state, dict) or len(_json.dumps(state)) > MAX_STATE:
        raise ValueError("bad settings")
    pg = rel.setdefault("brand", {}).setdefault("playground", {})
    vs = [v for v in pg.get("versions") or [] if v.get("name") != name]
    vs.append({"name": name, "saved": now, "state": state})
    pg["versions"] = vs[-MAX_VERSIONS:]
    return rel


def delete_version(rel: dict, name: str) -> bool:
    pg = ((rel or {}).get("brand") or {}).get("playground") or {}
    vs = pg.get("versions") or []
    keep = [v for v in vs if v.get("name") != name]
    pg["versions"] = keep
    return len(keep) != len(vs)


def layout_snap_save(project_root: Path, slug: str, n: int, data: bytes) -> Path:
    """Save one kept layout as the Layout page drew it (with its effects), for a side page of picks.
    n is the keep's number; the bytes must be a real JPEG/PNG of at most 1600 px."""
    from io import BytesIO
    from PIL import Image
    if not SLUG.fullmatch(slug or "") or not (0 <= int(n) <= 999) or not data or len(data) > 6_000_000:
        raise ValueError("bad snap")
    try:
        im = Image.open(BytesIO(data))
        im.verify()
        im = Image.open(BytesIO(data))
    except Exception:
        raise ValueError("bad image")
    big = int(n) >= 900   # 900-999 = full-size exports (release cover, 11-09): up to 4000 px, square, best JPEG
    if im.format not in ("JPEG", "PNG") or max(im.size) > (4000 if big else 1600) or (big and im.size[0] != im.size[1]):
        raise ValueError("bad image")
    d = snaps_dir(project_root, slug)
    d.mkdir(parents=True, exist_ok=True)
    out = d / ("current.jpg" if int(n) == 0 else ("export-%d-%dpx.jpg" % (int(n), im.size[0])) if big else "keep-%02d.jpg" % int(n))   # 0 = what is on the editor now
    tmp = out.with_suffix(".tmp")
    if big:
        im.convert("RGB").save(tmp, "JPEG", quality=95, subsampling=0)
    else:
        im.convert("RGB").save(tmp, "JPEG", quality=90)
    os.replace(tmp, out)
    return out


# --- System 97 (2026-11-10): picture per keep, picks page, Export ---------------------------------------
def snaps_dir(project_root: Path, slug: str) -> Path:
    """Where a release's layout pictures live. Half the Night keeps its folder from the cover round."""
    if not SLUG.fullmatch(slug or ""):
        raise ValueError("bad slug")
    if slug == "pinocchio-single":
        return project_root / "artwork" / "edits" / "htn-noir" / "layout-snaps" / slug
    return project_root / "artwork" / "edits" / "layout-snaps" / slug


def _real_image(data: bytes, max_px: int):
    from io import BytesIO
    from PIL import Image
    if not data or len(data) > 40_000_000:
        raise ValueError("bad image")
    try:
        im = Image.open(BytesIO(data))
        im.verify()
        im = Image.open(BytesIO(data))
    except Exception:
        raise ValueError("bad image")
    if im.format not in ("JPEG", "PNG") or max(im.size) > max_px:
        raise ValueError("bad image")
    return im


def keep_snap_name(kid: int) -> str:
    return "id-%04d.jpg" % int(kid)


def keep_snap_save(project_root: Path, slug: str, kid: int, data: bytes) -> Path:
    """The picture of one keep, by its fixed id (id-0051.jpg). Separate names from the hand-made
    keep-NN.jpg files of the Half the Night round, so none of those is ever overwritten."""
    if not isinstance(kid, int) or not 1 <= kid <= 9999:
        raise ValueError("bad keep id")
    if kid not in {k["id"] for k in layouts_kept(project_root, slug)}:
        raise ValueError("no such keep")
    im = _real_image(data, 1600)
    d = snaps_dir(project_root, slug)
    d.mkdir(parents=True, exist_ok=True)
    out = d / keep_snap_name(kid)
    tmp = out.with_suffix(".tmp")
    im.convert("RGB").save(tmp, "JPEG", quality=90)
    os.replace(tmp, out)
    return out


def keep_snap_path(project_root: Path, slug: str, kid: int) -> Path | None:
    try:
        p = snaps_dir(project_root, slug) / keep_snap_name(int(kid))
    except (ValueError, TypeError):
        return None
    return p if p.is_file() else None


def picks_file(project_root: Path, slug: str) -> Path:
    return project_root / "plans" / "playground-wall" / f"{slug}-picks.json"


def picks_ticked(project_root: Path, slug: str) -> list:
    import json as _json
    try:
        return [int(x) for x in _json.loads(picks_file(project_root, slug).read_text()).get("ticks") or []]
    except Exception:
        return []


def picks_toggle(project_root: Path, slug: str, kid) -> list:
    """V tick on the picks page, by keep id."""
    import json as _json
    if not SLUG.fullmatch(slug or "") or not isinstance(kid, int) or isinstance(kid, bool):
        raise ValueError("bad keep id")
    if kid not in {k["id"] for k in layouts_kept(project_root, slug)}:
        raise ValueError("no such keep")
    t = picks_ticked(project_root, slug)
    t = [x for x in t if x != kid] if kid in t else t + [kid]
    f = picks_file(project_root, slug)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(_json.dumps({"ticks": t}, indent=1))
    return t


EXPORT_SIZES = (3000, 4000)   # 3000 = the store size (Symphonic), 4000 = Apple's ask


def export_save(project_root: Path, slug: str, px: int, data: bytes, stamp: str, kid: int | None = None) -> Path:
    """The final cover as the page drew it, square at 3000 or 4000 px, best JPEG. Never overwrites:
    each export gets its own time stamp (and the keep id when it came from a keep)."""
    if px not in EXPORT_SIZES or not re.fullmatch(r"[0-9]{8}-[0-9]{6}", stamp or ""):
        raise ValueError("bad export")
    im = _real_image(data, 4000)
    if im.size != (px, px):
        raise ValueError("the export must be %d x %d px" % (px, px))
    d = snaps_dir(project_root, slug) / "exports"
    d.mkdir(parents=True, exist_ok=True)
    out = d / ("cover-%s%s-%dpx.jpg" % (stamp, ("-k%d" % kid) if kid else "", px))
    if out.exists():
        raise ValueError("an export with this time stamp exists")
    tmp = out.with_suffix(".tmp")
    im.convert("RGB").save(tmp, "JPEG", quality=95, subsampling=0)
    os.replace(tmp, out)
    return out


def run_cover_resizer(project_root: Path, src: Path, timeout: int = 300) -> dict:
    """The existing cover export: artwork_resizer.py <file> --cover, run in the project (it writes resized/)."""
    import subprocess
    import sys
    src = src.resolve()
    if (project_root / "artwork").resolve() not in src.parents or not src.is_file():
        raise ValueError("bad export file")
    p = subprocess.run([sys.executable, str(project_root / "artwork_resizer.py"), str(src), "--cover"],
                       cwd=str(project_root), capture_output=True, text=True, timeout=timeout)
    made = [ln.strip()[3:].strip() for ln in p.stdout.splitlines() if ln.strip().startswith("v  ")]
    return {"ok": p.returncode == 0, "files": made, "tail": "\n".join((p.stdout + p.stderr).strip().splitlines()[-6:])}


def cover_title(rel: dict) -> str:
    """The words on the cover (System 92): brand.playground.title, else the release title in capitals.
    Half the Night: 'HALF THE NIGHT', as the page always drew it."""
    pg = ((rel or {}).get("brand") or {}).get("playground") or {}
    t = str(pg.get("title") or "").strip()
    if not t:
        t = str(((rel or {}).get("metadata") or {}).get("title") or (rel or {}).get("title") or (rel or {}).get("slug") or "").strip().upper()
    return re.sub(r"\s+", " ", t)[:60]
