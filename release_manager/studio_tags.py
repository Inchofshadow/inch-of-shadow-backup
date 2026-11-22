"""One shared tag list for the four studio libraries (System 94, option T1, Amir's pick 2026-11-11).

docs/brand/tags.json holds the fixed list (id + what it means) and the tags of every item in the
Shadow Archive, Effects, Fonts and Imagine, keyed "archive:R-022", "effect:look-xerox", "font:gloria",
"imagine:<file>". It was filled once by the rules below (python -m release_manager.studio_tags --write);
after that the file is the source and can be edited by hand. An item that is not in the file yet
(added to a library later) gets the rule tags when it is read, so the drawer never misses it.
Only tags from the list are ever used.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAGS_FILE = ROOT / "docs" / "brand" / "tags.json"

# The first-fill list. docs/brand/tags.json holds its own copy ("tags"), and that copy is the one used
# (tag_list); this one is only the fallback when the file is missing or its list is broken.
TAGS = [
    # feeling
    ("night", "Night scenes, moonlight, dark sky"), ("daylight", "Sunny, bright, open air (on-brand too)"),
    ("warm", "Golden, amber, warm light"), ("cold", "Teal, blue, cold light"), ("dark", "Low key, black-heavy, horror edge"),
    ("dreamy", "Soft, hazy, unreal"), ("romantic", "Tender, intimate, longing"), ("eerie", "Uneasy, ghostly, strange"),
    ("dramatic", "Hard contrast, big gesture"), ("quiet", "Calm, sparse, pensive"),
    # world and era
    ("90s-noir", "90s animated noir: Batman TAS title cards, red skies, black shapes"), ("dark-deco", "Tall Art Deco shapes in the dark"),
    ("gothic", "Gothic romance, witch house, blackletter world"), ("retro-80s", "1980s screens, tape, retro-future"),
    ("y2k", "Early web, Y2K shine, games"), ("rave", "Rave flyers and neon club"), ("vintage-film", "Old film, sepia, analogue photo"),
    # how it is made
    ("grain", "Film or print grain over the picture"), ("print", "Xerox, halftone, riso, risograph and paper print"),
    ("ink-drawn", "Engraving, ink, drawn by hand"), ("cut-paper", "Cut paper layers and edges"), ("collage", "Cut-outs and collage"),
    ("glitch", "Glitch, scan lines, broken screens"), ("neon", "Neon light and colour"), ("chrome", "Chrome, metal, shine"),
    ("silhouette", "Black shapes against light"), ("glow", "Glow, halation, light bloom"),
    # things on the cover
    ("moon", "The moon"), ("owl", "The owl"), ("trees", "Trees and branches"), ("rose", "Roses (one of our motifs)"), ("birds", "Swans, ravens, birds"),
    # letters
    ("condensed", "Tall, narrow or heavy condensed letters"), ("blackletter", "Blackletter and textura"), ("serif", "Serif faces"),
    ("script", "Scripts and handwriting"),
    # releases
    ("half-the-night", "Used or saved for the Half the Night cover"),
]
TAG_IDS = [t for t, _ in TAGS]
TAG_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
RESERVED = {"untagged"}   # the drawer's own chip, never a stored tag


def tag_list(data: dict | None = None) -> list:
    """The tag list as (id, means) pairs, read from docs/brand/tags.json (Opus gate 2026-11-15: a tag added
    or renamed by hand in the file must show). Bad entries are skipped; the built-in TAGS stand in only
    when the file has no usable list."""
    data = load() if data is None else data
    rows = data.get("tags") if isinstance(data, dict) else None
    out, seen = [], set()
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        tid, means = row.get("id"), row.get("means")
        if not isinstance(tid, str) or not TAG_ID.fullmatch(tid) or tid in RESERVED or tid in seen:
            continue
        out.append((tid, means.strip()[:200] if isinstance(means, str) else ""))
        seen.add(tid)
    return out or list(TAGS)

# rules (the first fill; the file wins after that)
EFFECT_GROUP = {
    "Cold and teal": ["cold"], "Bright daylight": ["daylight"], "Film and vintage": ["vintage-film", "grain"],
    "Night and neon": ["night", "neon"], "Dark and horror": ["dark", "eerie"], "Warm and golden": ["warm"], "Red": ["dark", "dramatic"],
    "Print and paper": ["print", "grain"], "Old print": ["print", "ink-drawn"], "Photo and film": ["vintage-film"],
    "Collage and glitch": ["collage", "glitch"], "Old web and games": ["y2k"], "Y2K shine": ["y2k", "chrome"], "Rave and neon": ["rave", "neon"],
    "Camera and tape": ["vintage-film", "grain"], "Glitch": ["glitch"], "Dream and weird": ["dreamy"], "Screen and tape": ["glitch", "retro-80s"],
    "Light": ["glow"], "Metal and plastic": ["chrome"], "Craft and fibre": ["cut-paper"], "Drawn and scanned": ["ink-drawn"],
    "Cutouts and collage": ["collage", "cut-paper"], "Light and glow": ["glow"],
}
EFFECT_FAMILY = {"silhouette": ["silhouette", "night"], "illustration": ["ink-drawn"]}
FONT_GROUP = {"A": ["dark-deco", "condensed"], "B": ["warm"], "C": ["serif", "dramatic"], "D": ["serif"], "E": ["gothic", "romantic"],
              "F": ["quiet"], "G": ["script", "romantic"], "H": ["serif"], "I": ["retro-80s"], "J": ["condensed", "dramatic"]}
WORDS = [   # words in names, notes or free tags -> list tags
    (r"\bnoir\b", "90s-noir"), (r"\bdeco\b", "dark-deco"), (r"\bgothic|witch ?house|corpse", "gothic"), (r"blackletter|textura|fraktur|unifraktur", "blackletter"),
    (r"\bnight|nocturn|moonlit", "night"), (r"\bmoon", "moon"), (r"\bowl", "owl"), (r"\btrees?\b|branch|forest", "trees"), (r"\broses?\b", "rose"),
    (r"swan|raven|crow|\bbirds?\b", "birds"), (r"\bgrain", "grain"), (r"halftone|xerox|riso|letterpress|photocop", "print"),
    (r"engrav|etching|woodcut|\bink\b", "ink-drawn"), (r"cut[- ]?paper|paper cut|papercut", "cut-paper"), (r"collage|cut-?out", "collage"),
    (r"glitch|scan ?line|datamosh|pixel ?sort", "glitch"), (r"\bneon", "neon"), (r"chrome|metallic", "chrome"), (r"silhouette", "silhouette"),
    (r"\bglow|halation|bloom", "glow"), (r"dream", "dreamy"), (r"romantic|intimate|tender|yearning|longing", "romantic"),
    (r"eerie|ghost|haunt", "eerie"), (r"dramatic", "dramatic"), (r"\bquiet|\bcalm\b|pensive", "quiet"), (r"\bwarm|golden|sunny", "warm"),
    (r"vintage|sepia", "vintage-film"), (r"\bvhs\b|\bcrt\b|1980s|80s", "retro-80s"), (r"\by2k\b", "y2k"), (r"\brave\b", "rave"),
    (r"condensed|narrow", "condensed"), (r"\bscript|handwrit|swash", "script"), (r"batman", "90s-noir"),
]
# what the Half the Night cover used or saved (cover report, plans/half-the-night-cover-direction-noir.md)
HTN_LOOKS = {"xerox", "halftone", "engraving", "solarisation", "dither", "scanlines", "halation", "window", "nightvision", "pixelsort",
             "monotint", "anaglyph", "thermal", "nightflash"}
HTN_FONTS = {"barlow-condensed", "pirata-one", "cat-eckmann", "unifraktur-cook", "fraunces", "switzer", "cat-neuzeit"}


def _words(text: str) -> set:
    t = (text or "").lower()
    return {tag for rx, tag in WORDS if re.search(rx, t)}


def rule_tags(lib: str, rec: dict, ids: list | None = None) -> list:
    """The tags the rules give one library record, kept to `ids` (the file's list; the built-in list by default)."""
    ids = TAG_IDS if ids is None else ids
    out = set()
    if lib == "effect":
        out |= set(EFFECT_GROUP.get(rec.get("group") or "", [])) | set(EFFECT_FAMILY.get(rec.get("family") or "", []))
        out |= _words(" ".join([rec.get("name") or "", rec.get("what") or ""]))
        if rec.get("family") == "looks" and (rec.get("id") or "").replace("look-", "") in HTN_LOOKS:
            out.add("half-the-night")
    elif lib == "font":
        out |= set(FONT_GROUP.get(rec.get("group") or "", []))
        out |= _words(" ".join([rec.get("name") or "", rec.get("tags") if isinstance(rec.get("tags"), str) else " ".join(rec.get("tags") or [])]))
        if rec.get("id") in HTN_FONTS or "pinocchio-single" in (rec.get("releases") or []):
            out.add("half-the-night")
    elif lib == "archive":
        out |= {t for t in (rec.get("tags") or []) if isinstance(t, str) and t in ids}
        out |= _words(" ".join([rec.get("title") or "", rec.get("summary") or "", rec.get("amir_reason") or ""]))
        if "pinocchio-single" in (rec.get("releases") or []):
            out.add("half-the-night")
    elif lib == "imagine":
        out |= _words(" ".join([rec.get("subject") or "", rec.get("prompt") or ""]))
        out |= {"ink-drawn"} if rec.get("kind") in ("element", "illustration") else set()
        if rec.get("release") == "pinocchio-single":
            out.add("half-the-night")
    return [t for t in ids if t in out]


def library_records(root: Path = ROOT) -> list:
    """Every item of the four libraries as (lib, id, record)."""
    out = []
    try:
        for r in json.loads((root / "docs/brand/shadow-archive/index.json").read_text()).get("references") or []:
            out.append(("archive", r["id"], r))
    except (OSError, ValueError):
        pass
    try:
        for r in json.loads((root / "docs/brand/effects/effects.json").read_text()).get("effects") or []:
            out.append(("effect", r["id"], r))
    except (OSError, ValueError):
        pass
    try:
        for r in json.loads((root / "docs/brand/fonts/fonts.json").read_text()).get("fonts") or []:
            out.append(("font", r["id"], r))
    except (OSError, ValueError):
        pass
    try:
        from release_manager import imagine as im
        for r in im.images(None):
            out.append(("imagine", r["file"], r))
    except Exception:
        pass
    return out


def load(path: Path = TAGS_FILE) -> dict:
    try:
        d = json.loads(path.read_text())
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def tags_for(lib: str, iid: str, rec: dict, data: dict | None = None) -> list:
    """The item's tags from the file; rule tags for an item the file does not have yet. List tags only."""
    data = load() if data is None else data
    ids = [t for t, _ in tag_list(data)]
    assign = data.get("assign") if isinstance(data, dict) else None
    have = assign.get(f"{lib}:{iid}") if isinstance(assign, dict) else None
    if not isinstance(have, list):   # not listed yet, or a broken value: the rules give the tags
        return rule_tags(lib, rec, ids)
    return [t for t in have if isinstance(t, str) and t in ids]


def build(root: Path = ROOT) -> dict:
    assign = {f"{lib}:{iid}": rule_tags(lib, rec) for lib, iid, rec in library_records(root)}
    return {"what": "One shared tag list for the Shadow Archive, Effects, Fonts and Imagine (System 94, T1). "
                    "Only these tags are used. Edit an item's tags here by hand; new library items get rule tags until listed.",
            "updated": __import__("datetime").date.today().isoformat(),
            "tags": [{"id": t, "means": m} for t, m in TAGS], "assign": assign}


if __name__ == "__main__":
    import sys
    d = build()
    counts = {t: 0 for t in TAG_IDS}
    for v in d["assign"].values():
        for t in v:
            counts[t] += 1
    libs = {}
    for k, v in d["assign"].items():
        lib = k.split(":")[0]
        a = libs.setdefault(lib, [0, 0])
        a[0] += 1
        a[1] += bool(v)
    for lib, (n, tagged) in libs.items():
        print(f"{lib:8} {tagged:4} of {n:4} items tagged")
    print("tags:", ", ".join(f"{t} {c}" for t, c in counts.items()))
    if "--write" in sys.argv:
        if TAGS_FILE.exists():
            sys.exit("docs/brand/tags.json exists: it is the source now; edit it by hand")
        TAGS_FILE.write_text(json.dumps(d, indent=1, ensure_ascii=False))
        print("written", TAGS_FILE)
