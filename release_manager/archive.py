"""Shadow Archive: the reference library (docs/brand/shadow-archive/) for the /archive page.

The index file is the only source of truth; Claude writes it at intake, this module reads
it. Nothing here writes a file. Markdown is rendered by a small converter of our own, enough
for the notes, recipes and playbooks in the archive (headings, lists, tables, links, bold,
code, rules); no library is installed for it.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ARCHIVE_DIR_NAME = Path("docs") / "brand" / "shadow-archive"
INDEX_NAME = "index.json"
REQUIRED = ("id", "title", "source", "kind", "topics", "lane", "weight", "amir_reason",
            "added", "read_level", "notes")
# Machine-28 (2026-10-21): our own ideas live in the same archive. origin "ours" marks them; they carry an
# execution line (how it was made and whether that works yet) and need no weight.
ORIGINS = ("reference", "ours")


class ArchiveError(ValueError):
    """The index file is missing, unreadable or fails validation."""


# --- loading and validation ------------------------------------------------------------

def archive_dir(project_root: Path) -> Path:
    return project_root / ARCHIVE_DIR_NAME


def load_index(project_root: Path) -> dict:
    path = archive_dir(project_root) / INDEX_NAME
    if not path.is_file():
        raise ArchiveError(f"no index at {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ArchiveError(f"index.json is not valid JSON: {exc}") from exc
    errors = validate(data)
    if errors:
        raise ArchiveError("; ".join(errors))
    return data


def validate(data: dict) -> list[str]:
    """Errors as strings; empty list = valid. Allowed values come from the file itself."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["top level must be an object"]
    allowed = data.get("allowed") or {}
    refs = data.get("references")
    if not isinstance(refs, list):
        return ["'references' must be a list"]
    seen: set[str] = set()
    for r in refs:
        if not isinstance(r, dict):
            errors.append("a reference is not an object")
            continue
        rid = str(r.get("id", "?"))
        if not re.fullmatch(r"R-\d{3,}", rid):
            errors.append(f"{rid}: id must look like R-001")
        if rid in seen:
            errors.append(f"{rid}: duplicate id")
        seen.add(rid)
        ours = r.get("origin") == "ours"
        if r.get("origin", "reference") not in ORIGINS:
            errors.append(f"{rid}: origin must be one of {', '.join(ORIGINS)}")
        for f in REQUIRED:
            if f not in r and not (ours and f == "weight"):
                errors.append(f"{rid}: missing '{f}'")
        if ours and not str(r.get("execution") or "").strip():
            errors.append(f"{rid}: our ideas need an execution line")
        for field in ("kind", "lane", "weight", "read_level"):
            if ours and field == "weight" and "weight" not in r:
                continue
            vals = allowed.get(field)
            if vals and r.get(field) not in vals:
                errors.append(f"{rid}: {field} '{r.get(field)}' not in allowed.{field}")
        topics = r.get("topics")
        if not isinstance(topics, list) or not topics:
            errors.append(f"{rid}: topics must be a non-empty list")
        elif allowed.get("topics"):
            for t in topics:
                if t not in allowed["topics"]:
                    errors.append(f"{rid}: topic '{t}' not in allowed.topics")
        if not isinstance(r.get("releases", []), list):
            errors.append(f"{rid}: releases must be a list of slugs")
        for c in r.get("children") or []:
            if not isinstance(c, dict) or not c.get("path"):
                errors.append(f"{rid}: a child needs a path")
    return errors


# --- shaping for the page --------------------------------------------------------------

def filter_refs(refs: list[dict], args) -> list[dict]:
    """Apply the page's filters (origin, kind, topic, lane, release, weight, q). Empty = no filter."""
    origin = (args.get("origin") or "").strip()
    kind = (args.get("kind") or "").strip()
    topic = (args.get("topic") or "").strip()
    lane = (args.get("lane") or "").strip()
    release = (args.get("release") or "").strip()
    weight = (args.get("weight") or "").strip()
    q = (args.get("q") or "").strip().lower()
    out = []
    for r in refs:
        if origin and r.get("origin", "reference") != origin:
            continue
        if kind and r.get("kind") != kind:
            continue
        if topic and topic not in (r.get("topics") or []):
            continue
        if lane and r.get("lane") != lane and r.get("lane") != "both":
            continue
        if release and release not in (r.get("releases") or []):
            continue
        if weight and r.get("weight") != weight:
            continue
        if q:
            hay = " ".join(str(r.get(k, "")) for k in
                           ("id", "title", "source", "summary", "amir_reason", "do_not", "execution")).lower()
            hay += " " + " ".join(r.get("topics") or [])
            if q not in hay:
                continue
        out.append(r)
    return out


def sort_refs(refs: list[dict], sort: str) -> list[dict]:
    if sort == "id":
        return sorted(refs, key=lambda r: r["id"])
    # newest first, ties by id descending
    return sorted(refs, key=lambda r: (r.get("added", ""), r["id"]), reverse=True)


def facets(data: dict, refs: list[dict]) -> dict:
    """The filter menus: allowed values with counts over the full set, plus release slugs."""
    allowed = data.get("allowed") or {}

    def count(field, multi=False):
        rows = []
        for v in allowed.get(field, []):
            if multi:
                n = sum(1 for r in refs if v in (r.get(field) or []))
            else:
                n = sum(1 for r in refs if r.get(field) == v)
            rows.append({"value": v, "count": n})
        return rows

    releases = sorted({s for r in refs for s in (r.get("releases") or [])})
    origin = [{"value": o, "count": sum(1 for r in refs if r.get("origin", "reference") == o)} for o in ORIGINS]
    return {"kind": count("kind"), "topics": count("topics", multi=True), "lane": count("lane"),
            "weight": count("weight"), "releases": releases, "origin": origin}


def by_id(data: dict, rid: str) -> dict | None:
    return next((r for r in data.get("references", []) if r.get("id") == rid), None)


def for_release(data: dict, slug: str) -> list[dict]:
    return [r for r in data.get("references", []) if slug in (r.get("releases") or [])]


# --- files inside the archive ----------------------------------------------------------

def safe_path(project_root: Path, rel: str) -> Path | None:
    """A path inside the archive folder, or None. No '..', no absolute paths, no symlink escape."""
    base = archive_dir(project_root).resolve()
    if not rel or rel.startswith(("/", "\\")) or ".." in Path(rel).parts:
        return None
    try:
        p = (base / rel).resolve()
    except OSError:
        return None
    if base not in p.parents and p != base:
        return None
    return p


def list_dir(p: Path) -> list[dict]:
    """Markdown files in a folder of the archive (the per-video notes), by name."""
    rows = []
    for f in sorted(p.glob("*.md")):
        title = f.stem
        try:
            first = f.read_text(encoding="utf-8").splitlines()[0]
            if first.startswith("# "):
                title = first[2:].strip()
        except (OSError, IndexError):
            pass
        rows.append({"name": f.name, "title": title})
    return rows


# --- markdown -> html (small, ours) ---------------------------------------------------

_INLINE_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_INLINE_BOLD = re.compile(r"\*\*(.+?)\*\*")
_INLINE_CODE = re.compile(r"`([^`]+)`")
_INLINE_STRIKE = re.compile(r"~~(.+?)~~")


def _inline(text: str, link_base: str) -> str:
    """Escape, then bold, code, strikethrough and links. Relative .md links go through link_base."""
    text = html.escape(text, quote=False)
    text = _INLINE_CODE.sub(r"<code>\1</code>", text)
    text = _INLINE_BOLD.sub(r"<strong>\1</strong>", text)
    text = _INLINE_STRIKE.sub(r"<s>\1</s>", text)

    def link(m):
        label, href = m.group(1), m.group(2)
        href = html.unescape(href)
        if href.startswith("#"):
            return f'<a href="{html.escape(href, quote=True)}">{label}</a>'
        if href.startswith(("http://", "https://")):
            return f'<a href="{html.escape(href, quote=True)}" target="_blank" rel="noopener">{label}</a>'
        if link_base is not None:
            return f'<a href="{html.escape(link_base + href, quote=True)}">{label}</a>'
        return label
    return _INLINE_LINK.sub(link, text)


def _slug(text: str) -> str:
    """GitHub-style heading id, so the links written in the recipe files (#berserk-eclipse) resolve."""
    t = re.sub(r"[^\w\s-]", "", text.strip().lower())
    return re.sub(r"\s+", "-", t)


def render_markdown(md: str, link_base: str = "") -> str:
    """Enough markdown for the archive. link_base is prefixed to relative links (a route that
    resolves them against the file's own folder). Unknown constructs render as paragraphs."""
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    para: list[str] = []

    def flush_para():
        if para:
            out.append("<p>" + _inline(" ".join(s.strip() for s in para), link_base) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            flush_para(); i += 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            flush_para()
            lvl = len(m.group(1))
            out.append(f'<h{lvl} id="{_slug(m.group(2))}">{_inline(m.group(2), link_base)}</h{lvl}>')
            i += 1; continue
        if re.fullmatch(r"-{3,}|\*{3,}", stripped):
            flush_para(); out.append("<hr>"); i += 1; continue
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            flush_para()
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<table><thead><tr>" + "".join(f"<th>{_inline(c, link_base)}</th>" for c in header)
                       + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{_inline(c, link_base)}</td>" for c in r) + "</tr>" for r in rows)
                       + "</tbody></table>")
            continue
        if re.match(r"^\s*([-*+]|\d+[.)])\s+", line):
            flush_para()
            i = _render_list(lines, i, out, link_base)
            continue
        para.append(line)
        i += 1
    flush_para()
    return "\n".join(out)


def _list_item(line: str):
    m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
    if not m:
        return None
    indent = len(m.group(1).replace("\t", "  "))
    ordered = m.group(2)[0].isdigit()
    return indent, ordered, m.group(3)


def _render_list(lines: list[str], i: int, out: list[str], link_base: str) -> int:
    """Nested lists by indentation. Returns the index after the list."""
    first = _list_item(lines[i])
    base_indent, ordered = first[0], first[1]
    tag = "ol" if ordered else "ul"
    out.append(f"<{tag}>")
    while i < len(lines):
        item = _list_item(lines[i])
        if item is None:
            # a continuation line belongs to the current item when indented, else the list ends
            if lines[i].strip() and lines[i].startswith(" " * (base_indent + 2)) and out and out[-1].endswith("</li>"):
                out[-1] = out[-1][:-5] + " " + _inline(lines[i].strip(), link_base) + "</li>"
                i += 1; continue
            break
        indent, _, text = item
        if indent < base_indent:
            break
        if indent > base_indent:
            # a nested list inside the last item
            if out and out[-1].endswith("</li>"):
                out[-1] = out[-1][:-5]
                i = _render_list(lines, i, out, link_base)
                out.append("</li>")
            else:
                i = _render_list(lines, i, out, link_base)
            continue
        out.append(f"<li>{_inline(text, link_base)}</li>")
        i += 1
    out.append(f"</{tag}>")
    return i


# --- README generation (kept in sync by the shadow_archive.py script) -------------------

def render_readme(data: dict) -> str:
    refs = sort_refs(data.get("references", []), "id")
    lines = ["# Shadow Archive", "",
             "Amir's references, collected so the design knowledge builds up over time and feeds real release art. "
             "A reference can be anything: a reel, a post, a creator, a cover, an image, a poster, a film still, a website, a song, a word or a mood.", "",
             "This file is generated from `index.json` by `python3 shadow_archive.py render`; edit the index and the notes in `refs/`, not this file. "
             "The Release Manager shows the same index at /archive.", ""]
    for r in data.get("rules", []):
        lines.append(f"- {r}")
    lines += ["", "## By topic", ""]
    for t in (data.get("allowed") or {}).get("topics", []):
        ids = [r["id"] for r in refs if t in (r.get("topics") or [])]
        lines.append(f"- **{t}:** {', '.join(ids) if ids else ''}".rstrip())
    ours = [r for r in refs if r.get("origin") == "ours"]
    if ours:
        lines += ["", "## Our own ideas", ""]
        for r in ours:
            lines.append(f"- **{r['id']} {r['title']}:** {r.get('execution', '')}")
    lines += ["", "## By weight", ""]
    for w in (data.get("allowed") or {}).get("weight", []):
        ids = [r["id"] for r in refs if r.get("weight") == w]
        lines.append(f"- **{w}:** {', '.join(ids) if ids else ''}".rstrip())
    tagged = [r for r in refs if r.get("releases")]
    if tagged:
        lines += ["", "## Tagged by Amir for a release", ""]
        for r in tagged:
            lines.append(f"- {r['id']}: {', '.join(r['releases'])}" + (f" ({r['release_notes']})" if r.get("release_notes") else ""))
    lines += ["", "## The references", ""]
    for r in refs:
        lines.append(f"### {r['id']} · {r['title']}")
        lines.append("")
        lines.append(f"- **Source:** {r['source']} · " + " · ".join(r.get("urls") or []))
        lines.append(f"- **Kind:** {r['kind']} · **Topics:** {', '.join(r['topics'])} · **Lane:** {r['lane']}"
                     + (f" · **Weight:** {r['weight']}" if r.get('weight') else " · **Ours**")
                     + f" · **Read:** {r['read_level']} · **Added:** {r['added']}")
        if r.get("execution"):
            lines.append(f"- **Execution:** {r['execution']}")
        lines.append(f"- **{'What Amir said' if r.get('origin') == 'ours' else 'Why Amir sent it'}:** {r['amir_reason']}")
        if r.get("do_not"):
            lines.append(f"- **Not for us:** {r['do_not']}")
        if r.get("summary"):
            lines.append(f"- **In short:** {r['summary']}")
        lines.append(f"- **Notes:** [{r['notes']}]({r['notes']})")
        for c in r.get("children") or []:
            lines.append(f"- {c.get('label', c['path'])}: [{c['path']}]({c['path']})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
