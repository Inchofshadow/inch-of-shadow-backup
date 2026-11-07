#!/usr/bin/env python3
"""The font collection (Machine-19): docs/brand/fonts/fonts.json and its tools.

    python3 fonts_library.py migrate     build fonts.json once from font-library.md, font-sources.md
                                          and release_manager/cover_fonts.py (refuses if it exists)
    python3 fonts_library.py match       find each face's files under docs/brand/fonts and write them in
    python3 fonts_library.py check       validate fonts.json and that every listed file exists
    python3 fonts_library.py next-id     a free id for a new name: next-id "Some Face"

fonts.json is the source of truth once it exists. Nothing on disk is moved or renamed.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BRAND = ROOT / "docs" / "brand"
FONTS_DIR = BRAND / "fonts"
DATA = FONTS_DIR / "fonts.json"
LIBRARY_MD = BRAND / "font-library.md"
SOURCES_MD = BRAND / "font-sources.md"

ALLOWED = {
    "group": {
        "A": "Tall, narrow, Deco: display capitals with high contrast",
        "B": "Soft, warm, 1970s: swash and heavy serifs, drawn by hand",
        "C": "Sharp, high-contrast serifs: editorial and fashion",
        "D": "Flared and carved capitals",
        "E": "Gothic romance: uncial, blackletter and Art Nouveau",
        "F": "Plain partners: the quiet font next to the loud one",
        "G": "Scripts and handwriting",
        "H": "Slab, stencil, typewriter and book faces",
        "I": "Retro-future: 1980s science fiction and machine letters",
        "J": "Heavy condensed sans, slanted: the loud one",
    },
    "status": ["default now", "fallback", "guest", "potential", "idea", "set aside", "out as main", "in the tools"],
    "licence": ["owned", "free", "trial", "canva only", "system", "personal use only", "none"],
}


# --- markdown tables ------------------------------------------------------------------------

def _tables(md: str) -> list[tuple[str, list[str], list[list[str]]]]:
    """(section heading, header, rows) for every table in a markdown file."""
    out, section, lines, i = [], "", md.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("## "):
            section = ln[3:].strip()
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|\s*-", lines[i + 1]):
            header = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append((section, header, rows))
            continue
        i += 1
    return out


def _clean_name(cell: str) -> str:
    """'**Albertus Nova** [in Canva, ...]' -> 'Albertus Nova'. Keeps the parenthesised foundry."""
    s = re.sub(r"\[[^\]]*\]", "", cell)
    s = s.replace("**", "").strip()
    return re.sub(r"\s+", " ", s)


def _bracket_notes(cell: str) -> str:
    return " ".join(m.strip() for m in re.findall(r"\[([^\]]*)\]", cell)).replace("**", "")


def _slug(name: str) -> str:
    s = re.sub(r"\(.*?\)", "", name).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "font"


def _canva(cell_notes: str) -> str:
    t = cell_notes.lower()
    if "not in canva" in t:
        return "no"
    if "in canva" in t:
        return "yes"
    return "unknown"


# --- migrate ---------------------------------------------------------------------------------

# Sources rows whose name does not match the library row's name on its own.
SOURCE_ALIAS = {
    "bookmania": "bookman-swash-italic",
    "thor": "thor",
    "signal-sirene": "signal",
    "signal-a-grungier-single-weight": "signal",
    "lhf-matthews-thin": "matthews-thin",
    "lhf-gloria": "gloria",
    "lhf-conclave": "conclave",
    "lhf-scriptana": "scriptana-sofia-script-stanford-script",
    "lhf-sofia-script": "scriptana-sofia-script-stanford-script",
    "lhf-stanford-script": "scriptana-sofia-script-stanford-script",
    "lhf-henderson": "henderson-state-fair-birgitta",
    "lhf-state-fair-4-font-set": "henderson-state-fair-birgitta",
    "lhf-birgitta": "henderson-state-fair-birgitta",
    "gothic-the-cohen-face": "gothic",
    "eurostile": "eurostile-microgramma",
    "microgramma": "eurostile-microgramma",
    "futura": "futura-itc-franklin-gothic-gill-sans-neuzeit-s",
    "futura-black": "futura-itc-franklin-gothic-gill-sans-neuzeit-s",
    "itc-franklin-gothic": "futura-itc-franklin-gothic-gill-sans-neuzeit-s",
    "neuzeit-s": "futura-itc-franklin-gothic-gill-sans-neuzeit-s",
    "ano": "alias-ano-lateral",
    "lateral": "alias-ano-lateral",
    "abc-favorit": "abc-favorit-onlysans-cf-asty",
    "clarendon-modern-text-cut": "clarendon-stencil-lettering",
    "clarendon-classic-display-cut": "clarendon-stencil-lettering",
    "century-expanded": "century-expanded-primer-melior-bold-condensed",
    "primer": "century-expanded-primer-melior-bold-condensed",
    "melior": "century-expanded-primer-melior-bold-condensed",
    "melior-bold-condensed": "century-expanded-primer-melior-bold-condensed",
    "ocr-b": "ocr-b-marvin-visions",
    "marvin-visions": "ocr-b-marvin-visions",
    "hollandse-mediaeval": "hollandse-mediaeval",
    "earth-the-star-crystal-title": "earth",
    "canela": "canela-domaine-display-romie",
    "domaine-display": "canela-domaine-display-romie",
    "romie": "canela-domaine-display-romie",
    "harbour": "harbour",
    "mohave-jost": None,            # "see the free table"
    "marcellus": "marcellus",
    "antique-olive": "antique-olive",
}

# Faces in the free table, matched to library rows (or new rows when the library has none).
FREE_ALIAS = {"marcellus": "marcellus", "jost": "jost-light", "mohave": "mohave",
              "ocr-b-matthew-skala-s-cut": "ocr-b-marvin-visions",
              "viking-by-steffmann-the-practical-thor-stand-in": "thor",
              "fdi-lettograph-the-signal-sirene-revival": "signal"}


def migrate() -> int:
    if DATA.exists():
        print(f"{DATA} exists already; it is the source of truth now. Nothing written.")
        return 1
    lib = LIBRARY_MD.read_text(encoding="utf-8")
    src = SOURCES_MD.read_text(encoding="utf-8")
    records: dict[str, dict] = {}
    order: list[str] = []

    # 1. the library, one record per row, every cell kept
    for section, header, rows in _tables(lib):
        m = re.match(r"([A-J])\. ", section)
        if not m:
            continue
        group = m.group(1)
        for row in rows:
            cells = dict(zip(header, row))
            raw = cells.get("Font", "")
            name = _clean_name(raw)
            rid = _slug(name)
            base, n = rid, 2
            while rid in records:                # a face listed in two groups gets a second record
                rid = f"{base}-{group.lower()}"
                if rid in records:
                    rid = f"{base}-{n}"; n += 1
            status_cell = cells.get("Status", "").replace("**", "")
            status = next((s for s in ALLOWED["status"] if status_cell.lower().startswith(s)), "potential")
            records[rid] = {
                "id": rid, "name": name, "group": group, "status": status,
                "status_note": status_cell if status_cell.lower() != status else "",
                "seen_on": cells.get("Seen on", ""),
                "get_hint": cells.get("Get it", ""),
                "canva": _canva(_bracket_notes(raw)), "canva_note": _bracket_notes(raw),
                "sources": [], "licence": "none", "files": [], "system": [], "tags": "",
                "in_tools_as": [], "releases": [], "archive_refs": [], "notes": "",
            }
            order.append(rid)

    # 2. the sources file
    unmatched = []
    for section, header, rows in _tables(src):
        if section.startswith("Read this") or section.startswith("Already on disk"):
            continue
        for row in rows:
            cells = dict(zip(header, row))
            name = _clean_name(cells.get("Font", "") or cells.get("Foundry", ""))
            key = _slug(name)
            if section.startswith("The free ones"):
                target = FREE_ALIAS.get(key)
                entry = {"label": name, "where": cells.get("Where", ""), "price": "free",
                         "trial": "", "licence_text": cells.get("Licence", ""), "on_disk": cells.get("On disk?", "")}
            else:
                target = SOURCE_ALIAS.get(key, key) if key in SOURCE_ALIAS else key
                entry = {"label": name, "where": cells.get("Where to get it", ""), "price": cells.get("Price", ""),
                         "trial": cells.get("Trial", "")}
            if target is None:
                continue
            if target not in records:
                hits = [r for r in records if r.startswith(target) or target.startswith(r)]
                target = hits[0] if len(hits) == 1 else None
            if target is None:
                unmatched.append(f"{section}: {name}")
                continue
            records[target]["sources"].append(entry)

    # 3. licence from what the files say
    for r in records.values():
        txt = " ".join([r["get_hint"], r["status_note"]] + [s.get("licence_text", "") + " " + s.get("price", "") for s in r["sources"]]).lower()
        if any(s.get("price") == "free" for s in r["sources"]) or "sil ofl" in txt or "free (sil ofl)" in txt:
            r["licence"] = "free"
        elif "trial on disk" in txt or any("on disk" in (s.get("trial") or "").lower() and "yes" in (s.get("trial") or "").lower() for s in r["sources"]):
            r["licence"] = "trial"
        elif "the bundle on disk" in r["seen_on"].lower() or any("on disk" in (s.get("trial") or "").lower() for s in r["sources"]):
            r["licence"] = "trial"
        elif r["canva"] == "yes":
            r["licence"] = "canva only"
        if "personal use" in txt and r["licence"] != "free":
            r["licence"] = "personal use only" if r["licence"] == "none" else r["licence"]

    # 4. the faces the tools use (cover_fonts.py), joined to their library row or added
    sys.path.insert(0, str(ROOT))
    from release_manager.cover_fonts import FONTS as COVER
    tool_rows = {
        "marcellus": "marcellus", "jost": "jost-light", "mohave": "mohave", "ocrb": "ocr-b-marvin-visions",
        "ogg": "ogg", "editorial_i": "editorial-new", "editorial_ub": "editorial-new", "migra_xl": "migra",
        "reckless": "reckless", "apoc": "apoc", "saol": "saol-display", "alpina_c": "gt-alpina",
        "matthews": "matthews-thin", "gloria": "gloria", "conclave": "conclave",
        "stanford": "scriptana-sofia-script-stanford-script", "henderson": "henderson-state-fair-birgitta",
        "impact": "impact", "futura_xb": "futura-condensed-extrabold",
    }
    for key, f in COVER.items():
        rid = tool_rows.get(key)
        if rid not in records:
            rid = _slug(f["label"])
            if rid not in records:
                records[rid] = {
                    "id": rid, "name": f["label"], "group": f["group"], "status": "in the tools",
                    "status_note": "on the Shoot page's cover ideas; not from Amir's research",
                    "seen_on": "", "get_hint": "", "canva": "unknown", "canva_note": "", "sources": [],
                    "licence": "system" if f.get("local") else "trial", "files": [], "system": [], "tags": "",
                    "in_tools_as": [], "releases": [], "archive_refs": [], "notes": "",
                }
                order.append(rid)
        r = records[rid]
        r["in_tools_as"].append(key)
        r["tags"] = " ".join(dict.fromkeys((r["tags"] + " " + f.get("tags", "")).split()))
        if f.get("file"):
            r["files"].append(f["file"])
        if f.get("local"):
            r["system"].append(f["local"])
            if r["licence"] == "none":
                r["licence"] = "system"

    # facts the tables carry in prose
    if "albertus-nova" in records:
        records["albertus-nova"]["licence"] = "canva only"
        records["albertus-nova"]["notes"] = "Brand face for now (frame.md face block). No file owned; the local tools draw Marcellus until the licence is bought. Read the logo clause before it becomes the wordmark."
    for rid in ("impact", "futura-condensed-extrabold"):
        if rid in records:
            records[rid]["licence"] = "system"
            records[rid]["notes"] = "On this Mac with macOS; a release licence is NOT checked."

    data = {
        "what": "The font collection: one record per row of Amir's font research, joined to where to get each face, the files on this Mac and the faces the tools use. Source of truth since 2026-10-11 (Machine-19); font-library.md and font-sources.md keep their prose. The /fonts page reads this file.",
        "version": 1, "updated": "2026-10-11",
        "allowed": {"group": ALLOWED["group"], "status": ALLOWED["status"], "licence": ALLOWED["licence"]},
        "rules": [
            "A font in Canva is not a font owned: no file, Canva designs only.",
            "Trial files are for looking at on screen. Nothing made with them goes out.",
            "Read the logo clause before a face becomes the wordmark.",
            "Statuses are Amir's. A face enters as potential until he has seen it on his own photos.",
            "Nothing on disk is moved or renamed by these tools.",
        ],
        "fonts": [records[r] for r in order],
    }
    DATA.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {DATA}: {len(order)} records")
    if unmatched:
        print("sources rows not joined to a record:")
        for u in unmatched:
            print("  -", u)
    return 0


# --- files on disk ---------------------------------------------------------------------------

FONT_EXT = {".otf", ".ttf"}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def match() -> int:
    """Add files under docs/brand/fonts whose name carries the face's name. Keeps what is there."""
    data = json.loads(DATA.read_text(encoding="utf-8"))
    files = [p for p in FONTS_DIR.rglob("*") if p.suffix.lower() in FONT_EXT]
    rel = {p: str(p.relative_to(FONTS_DIR)) for p in files}
    added = 0
    for r in data["fonts"]:
        names = [n.strip() for n in re.split(r",| \+ |/", re.sub(r"\(.*?\)", "", r["name"])) if n.strip()]
        keys = [_norm(n) for n in names if len(_norm(n)) >= 4]
        if not keys:
            continue
        have = set(r["files"])
        for p, rp in rel.items():
            stem = _norm(p.stem)
            if any(k in stem for k in keys) and rp not in have:
                r["files"].append(rp); have.add(rp); added += 1
        r["files"].sort()
    DATA.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    with_files = sum(1 for r in data["fonts"] if r["files"])
    print(f"{added} files added; {with_files} of {len(data['fonts'])} records have files on disk")
    return 0


# --- check -----------------------------------------------------------------------------------

def check() -> int:
    sys.path.insert(0, str(ROOT))
    from release_manager import fonts_page
    try:
        data = fonts_page.load(ROOT)
    except fonts_page.FontsError as exc:
        print(f"fonts.json: {exc}")
        return 1
    missing = [(r["id"], f) for r in data["fonts"] for f in r["files"] if not (FONTS_DIR / f).is_file()]
    for rid, f in missing:
        print(f"{rid}: file missing: {f}")
    print(f"{len(data['fonts'])} fonts, {len(missing)} missing files")
    return 1 if missing else 0


def next_id() -> int:
    name = " ".join(sys.argv[2:]) or "font"
    data = json.loads(DATA.read_text(encoding="utf-8"))
    ids = {r["id"] for r in data["fonts"]}
    rid, n = _slug(name), 2
    while rid in ids:
        rid = f"{_slug(name)}-{n}"; n += 1
    print(rid)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    sys.exit({"migrate": migrate, "match": match, "check": check, "next-id": next_id}.get(cmd, check)())
