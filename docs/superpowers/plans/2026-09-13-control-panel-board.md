# Control Panel Board Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A validated ticket file (`plans/control-panel/tickets.json`) plus a read-only `/board` page in the Release Manager that shows the tickets as a top-down build tower.

**Architecture:** One pure-Python module `release_manager/board.py` loads, validates and shapes the ticket file into a view model (floors, derived blocked status, counts). One Flask route renders it through `board.html`, which embeds the tickets as JSON for a small inline script (filters, click-to-open detail). No writes from the page.

**Tech Stack:** Python 3.9 (system), Flask (already in the RM), Jinja2, vanilla JS, pytest 8.

**Spec:** `docs/superpowers/specs/2026-09-13-control-panel-board-design.md`

## Global Constraints

- Python 3.9 syntax only (no `match`, no `X | Y` unions at runtime; `from __future__ import annotations` is fine for hints).
- No emojis in code or output. No em-dashes in any copy.
- Read-only page: no forms, no POST routes, no writes to the ticket file from the webapp.
- Ticket ids are `<Category>-<NN>`; Marketing ids use the `Mkt-` prefix. Lane names are `Control Panel` and `Marketing`, never letters.
- Statuses: `proposed`, `approved`, `in-progress`, `blocked`, `done`. `blocked` is derived when any `blocked_on` ticket is not `done`.
- Floors: 1 Foundation, 2 Identity built, 3 Formats, 4 Machine, 5 Measurement, 6 Marketing.
- Styling uses the RM's existing CSS tokens (`--bg-secondary`, `--text-accent`, `--border-color`, `--font-heading`, `--font-mono`, ...). No new dependencies, no CDN.
- Commits are local only; never add a remote or push (repo rule, 2026-08-31).
- Tests run with `python3 -m pytest tests/test_board.py -q` from `Inchofshadowcode/`.

---

## File map

| File | Responsibility |
|---|---|
| `release_manager/board.py` (create) | constants, `load_board`, `validate`, `effective_status`, `build_view` |
| `plans/control-panel/tickets.json` (create) | the source of truth, seeded with 23 tickets |
| `release_manager/webapp.py` (modify, after the `/palette` route, ~line 385) | `GET /board` |
| `release_manager/templates/board.html` (create) | the tower page, extends `base.html` |
| `release_manager/templates/base.html` (modify, sidebar ~line 38) | "Plan" group with the Board link |
| `release_manager/static/style.css` (modify, append) | board styles |
| `tests/test_board.py` (create) | validator, view model, seed, route |
| `TICKETS.md`, `docs/brand/CONTROL-PANEL-SETUP-ROADMAP.md`, `docs/brand/VIDEO-BRAND-SESSION-KIT.md` (modify, one line each) | pointers to the board |

---

### Task 1: Loader and validator

**Files:**
- Create: `release_manager/board.py`
- Test: `tests/test_board.py`

**Interfaces:**
- Produces:
  - `STATUSES: tuple[str, ...]`, `FLOORS: dict[int, str]`, `LANE_OF: dict[str, str]` (category -> lane), `ID_PREFIX: dict[str, str]` (category -> id prefix)
  - `class BoardError(ValueError)`
  - `validate(data: dict) -> list[str]` returns a list of human-readable error strings, empty when valid
  - `load_board(path: Path) -> dict` reads JSON, raises `BoardError` (message = errors joined by newline) when invalid or unreadable

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_board.py
"""Control Panel Board: ticket file validation, view model, seed, route."""
import json
from pathlib import Path

import pytest

from release_manager.board import (
    BoardError, build_view, effective_status, load_board, validate,
)

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "plans" / "control-panel" / "tickets.json"


def ticket(**over):
    base = {
        "id": "Look-01", "lane": "Control Panel", "category": "Look", "floor": 1,
        "title": "Type system", "why": "w", "serves": "s", "question": "q",
        "status": "proposed", "blocked_on": [], "size": "S", "references": [],
        "decision": "", "decided_on": "", "outputs": [], "notes": [],
    }
    base.update(over)
    return base


def board(*tickets):
    return {"version": 1, "updated": "2026-09-13",
            "deadline": {"floors": [1, 2], "date": "2026-09-20"},
            "tickets": list(tickets)}


def test_valid_minimal_board_has_no_errors():
    assert validate(board(ticket())) == []


@pytest.mark.parametrize("field", ["why", "serves", "question"])
def test_missing_core_field_is_an_error(field):
    t = ticket(); t[field] = ""
    errs = validate(board(t))
    assert any(field in e and "Look-01" in e for e in errs)


def test_bad_status_is_an_error():
    errs = validate(board(ticket(status="maybe")))
    assert any("status" in e for e in errs)


def test_bad_category_is_an_error():
    errs = validate(board(ticket(category="Vibes")))
    assert any("category" in e for e in errs)


def test_id_prefix_must_match_category():
    errs = validate(board(ticket(id="Words-01", category="Look")))
    assert any("prefix" in e for e in errs)


def test_lane_must_match_category():
    errs = validate(board(ticket(lane="Marketing")))
    assert any("lane" in e for e in errs)


def test_duplicate_id_is_an_error():
    errs = validate(board(ticket(), ticket()))
    assert any("duplicate" in e for e in errs)


def test_dangling_blocked_on_is_an_error():
    errs = validate(board(ticket(blocked_on=["Look-99"])))
    assert any("Look-99" in e for e in errs)


def test_floor_must_be_1_to_6():
    errs = validate(board(ticket(floor=9)))
    assert any("floor" in e for e in errs)


def test_load_board_raises_on_invalid_file(tmp_path):
    p = tmp_path / "t.json"
    p.write_text(json.dumps(board(ticket(status="nope"))))
    with pytest.raises(BoardError):
        load_board(p)


def test_load_board_raises_on_corrupt_json(tmp_path):
    p = tmp_path / "t.json"
    p.write_text("{not json")
    with pytest.raises(BoardError):
        load_board(p)


def test_load_board_returns_data(tmp_path):
    p = tmp_path / "t.json"
    p.write_text(json.dumps(board(ticket())))
    assert load_board(p)["tickets"][0]["id"] == "Look-01"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd "/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode" && python3 -m pytest tests/test_board.py -q`
Expected: ImportError, `release_manager.board` does not exist.

- [ ] **Step 3: Write the loader and validator**

```python
# release_manager/board.py
"""Control Panel Board: load, validate and shape plans/control-panel/tickets.json.

The JSON file is the only source of truth. The webapp renders it and never writes it.
Spec: docs/superpowers/specs/2026-09-13-control-panel-board-design.md
"""
from __future__ import annotations

import json
from pathlib import Path

STATUSES = ("proposed", "approved", "in-progress", "blocked", "done")
SIZES = ("XS", "S", "M", "L")

FLOORS = {
    1: "Foundation",
    2: "Identity built",
    3: "Formats",
    4: "Machine",
    5: "Measurement",
    6: "Marketing",
}

# category -> lane
LANE_OF = {
    "Words": "Control Panel",
    "Look": "Control Panel",
    "Formats": "Control Panel",
    "Machine": "Control Panel",
    "Measure": "Control Panel",
    "Campaign": "Marketing",
    "Engagement": "Marketing",
    "Ads and data": "Marketing",
    "Curators and labels": "Marketing",
    "Cadence": "Marketing",
}

# category -> required id prefix
ID_PREFIX = {c: ("Mkt" if lane == "Marketing" else c) for c, lane in LANE_OF.items()}

CORE_FIELDS = ("why", "serves", "question")
REQUIRED_FIELDS = ("id", "lane", "category", "floor", "title", "status") + CORE_FIELDS


class BoardError(ValueError):
    """Raised when the ticket file is unreadable or fails validation."""


def validate(data: dict) -> list[str]:
    """Return a list of error strings. Empty list means the board is valid."""
    errors: list[str] = []
    tickets = data.get("tickets")
    if not isinstance(tickets, list):
        return ["top-level 'tickets' must be a list"]

    seen: set[str] = set()
    ids = [t.get("id") for t in tickets if isinstance(t, dict)]
    for t in tickets:
        if not isinstance(t, dict):
            errors.append("a ticket is not an object")
            continue
        tid = str(t.get("id", "?"))
        for f in REQUIRED_FIELDS:
            if f not in t or t[f] in ("", None):
                errors.append(f"{tid}: missing {f}")
        if tid in seen:
            errors.append(f"{tid}: duplicate id")
        seen.add(tid)
        if t.get("status") not in STATUSES:
            errors.append(f"{tid}: bad status {t.get('status')!r}")
        cat = t.get("category")
        if cat not in LANE_OF:
            errors.append(f"{tid}: bad category {cat!r}")
        else:
            if t.get("lane") != LANE_OF[cat]:
                errors.append(f"{tid}: lane {t.get('lane')!r} does not match category {cat!r}")
            if not tid.startswith(ID_PREFIX[cat] + "-"):
                errors.append(f"{tid}: id prefix must be {ID_PREFIX[cat]!r} for category {cat!r}")
        if t.get("floor") not in FLOORS:
            errors.append(f"{tid}: floor must be 1..6")
        if "size" in t and t["size"] not in ("",) + SIZES:
            errors.append(f"{tid}: bad size {t['size']!r}")
        for dep in t.get("blocked_on", []) or []:
            if dep not in ids:
                errors.append(f"{tid}: blocked_on names unknown ticket {dep}")
    return errors


def load_board(path: Path) -> dict:
    """Read and validate the ticket file. Raises BoardError on any problem."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise BoardError(f"cannot read {path}: {e}") from e
    errors = validate(data)
    if errors:
        raise BoardError("\n".join(errors))
    return data
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m pytest tests/test_board.py -q`
Expected: the 12 tests above pass (the file imports `build_view` and `effective_status`, which do not exist yet; add two stub lines at the bottom of `board.py` so the import works, then replace them in Task 2):

```python
def effective_status(ticket: dict, by_id: dict) -> str:  # replaced in Task 2
    return ticket["status"]


def build_view(data: dict) -> dict:  # replaced in Task 2
    return {}
```

- [ ] **Step 5: Commit**

```bash
git add release_manager/board.py tests/test_board.py
git commit -m "board: ticket file loader and validator

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: View model (derived status, floors, counts)

**Files:**
- Modify: `release_manager/board.py` (replace the two stubs)
- Test: `tests/test_board.py` (append)

**Interfaces:**
- Consumes: `FLOORS`, `LANE_OF`, `STATUSES` from Task 1.
- Produces:
  - `effective_status(ticket: dict, by_id: dict[str, dict]) -> str`
  - `category_slug(category: str) -> str` (`"Ads and data"` -> `"ads-and-data"`)
  - `build_view(data: dict) -> dict` with keys:
    - `floors`: list of `{"n": int, "name": str, "after": int|None, "is_current": bool, "tickets": [card...]}` for n in 1..6, always all six
    - card: `{"id", "title", "category", "category_slug", "lane", "status" (effective), "size", "needs": [ids not done], "unblocks": [ids], "why", "serves", "question", "references", "blocked_on", "outputs", "decision", "decided_on", "notes", "floor"}`
    - `counts`: `{"proposed": int, "approved": int, "in-progress": int, "blocked": int, "done": int}` over effective statuses
    - `current_floor`: lowest floor with any ticket whose effective status is not `done`; 6 if none
    - `waiting_on_amir`: `counts["proposed"]`
    - `deadline`: the file's `deadline` dict or `{}`
    - `updated`: the file's `updated` string or `""`

- [ ] **Step 1: Write the failing tests** (append to `tests/test_board.py`)

```python
def test_effective_status_blocked_when_parent_not_done():
    parent = ticket(id="Look-01", status="proposed")
    child = ticket(id="Look-02", status="proposed", blocked_on=["Look-01"])
    by_id = {t["id"]: t for t in (parent, child)}
    assert effective_status(child, by_id) == "blocked"
    assert effective_status(parent, by_id) == "proposed"


def test_effective_status_unblocks_when_parent_done():
    parent = ticket(id="Look-01", status="done")
    child = ticket(id="Look-02", status="approved", blocked_on=["Look-01"])
    by_id = {t["id"]: t for t in (parent, child)}
    assert effective_status(child, by_id) == "approved"


def test_done_stays_done_even_if_blocked_on_open():
    parent = ticket(id="Look-01", status="proposed")
    child = ticket(id="Look-02", status="done", blocked_on=["Look-01"])
    by_id = {t["id"]: t for t in (parent, child)}
    assert effective_status(child, by_id) == "done"


def test_build_view_has_six_floors_in_order_and_current_floor():
    data = board(
        ticket(id="Look-01", floor=1, status="done"),
        ticket(id="Look-02", floor=2, status="proposed", blocked_on=["Look-01"]),
        ticket(id="Formats-01", category="Formats", floor=3, status="proposed",
               blocked_on=["Look-02"]),
    )
    view = build_view(data)
    assert [f["n"] for f in view["floors"]] == [1, 2, 3, 4, 5, 6]
    assert view["floors"][0]["name"] == "Foundation"
    assert view["floors"][0]["after"] is None and view["floors"][1]["after"] == 1
    assert view["current_floor"] == 2
    assert [f["is_current"] for f in view["floors"]] == [False, True, False, False, False, False]


def test_build_view_cards_carry_needs_unblocks_and_counts():
    data = board(
        ticket(id="Look-01", floor=1, status="proposed"),
        ticket(id="Look-02", floor=2, status="proposed", blocked_on=["Look-01"]),
    )
    view = build_view(data)
    f1, f2 = view["floors"][0], view["floors"][1]
    assert f1["tickets"][0]["unblocks"] == ["Look-02"]
    assert f2["tickets"][0]["needs"] == ["Look-01"]
    assert f2["tickets"][0]["status"] == "blocked"
    assert view["counts"] == {"proposed": 1, "approved": 0, "in-progress": 0,
                              "blocked": 1, "done": 0}
    assert view["waiting_on_amir"] == 1
    assert view["deadline"]["date"] == "2026-09-20"


def test_category_slug():
    from release_manager.board import category_slug
    assert category_slug("Ads and data") == "ads-and-data"
    assert category_slug("Look") == "look"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest tests/test_board.py -q`
Expected: the six new tests fail (stubs return the stored status / empty dict; `category_slug` missing).

- [ ] **Step 3: Replace the stubs with the view model**

```python
def category_slug(category: str) -> str:
    return category.lower().replace(" ", "-")


def effective_status(ticket: dict, by_id: dict) -> str:
    """Stored status, except a ticket with any not-done dependency shows as blocked."""
    if ticket.get("status") == "done":
        return "done"
    for dep in ticket.get("blocked_on", []) or []:
        parent = by_id.get(dep)
        if parent is None or parent.get("status") != "done":
            return "blocked"
    return ticket["status"]


def _card(t: dict, by_id: dict, unblocks: dict) -> dict:
    needs = [d for d in (t.get("blocked_on") or [])
             if by_id.get(d, {}).get("status") != "done"]
    return {
        "id": t["id"],
        "title": t["title"],
        "category": t["category"],
        "category_slug": category_slug(t["category"]),
        "lane": t["lane"],
        "floor": t["floor"],
        "status": effective_status(t, by_id),
        "size": t.get("size", ""),
        "needs": needs,
        "unblocks": unblocks.get(t["id"], []),
        "why": t["why"],
        "serves": t["serves"],
        "question": t["question"],
        "references": t.get("references", []),
        "blocked_on": t.get("blocked_on", []),
        "outputs": t.get("outputs", []),
        "decision": t.get("decision", ""),
        "decided_on": t.get("decided_on", ""),
        "notes": t.get("notes", []),
    }


def build_view(data: dict) -> dict:
    """Shape a validated board into what the template renders."""
    tickets = data.get("tickets", [])
    by_id = {t["id"]: t for t in tickets}
    unblocks: dict[str, list[str]] = {}
    for t in tickets:
        for dep in t.get("blocked_on") or []:
            unblocks.setdefault(dep, []).append(t["id"])

    cards = [_card(t, by_id, unblocks) for t in tickets]
    counts = {s: 0 for s in STATUSES}
    for c in cards:
        counts[c["status"]] += 1

    open_floors = [c["floor"] for c in cards if c["status"] != "done"]
    current = min(open_floors) if open_floors else 6

    floors = []
    for n in sorted(FLOORS):
        floors.append({
            "n": n,
            "name": FLOORS[n],
            "after": None if n == 1 else n - 1,
            "is_current": n == current,
            "tickets": [c for c in cards if c["floor"] == n],
        })
    return {
        "floors": floors,
        "counts": counts,
        "current_floor": current,
        "waiting_on_amir": counts["proposed"],
        "deadline": data.get("deadline", {}) or {},
        "updated": data.get("updated", "") or "",
    }
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m pytest tests/test_board.py -q`
Expected: 18 passed.

- [ ] **Step 5: Commit**

```bash
git add release_manager/board.py tests/test_board.py
git commit -m "board: view model with derived blocked status and floors

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: Seed the ticket file

**Files:**
- Create: `plans/control-panel/tickets.json`
- Test: `tests/test_board.py` (append)

**Interfaces:**
- Consumes: `load_board`, `build_view`.
- Produces: the real ticket file with the 23 seed tickets from the spec.

- [ ] **Step 1: Write the failing tests** (append)

```python
SEED_IDS = {
    "Words-01", "Words-03", "Look-00", "Look-01", "Look-03", "Look-04", "Look-08",
    "Words-02", "Look-02", "Look-05", "Look-06", "Look-09", "Look-07",
    "Formats-01", "Formats-02", "Formats-03", "Formats-04",
    "Machine-01", "Machine-02", "Look-10", "Machine-03", "Machine-04",
    "Mkt-01",
}


def test_seed_file_is_valid_and_complete():
    data = load_board(SEED)
    ids = {t["id"] for t in data["tickets"]}
    assert ids == SEED_IDS
    for t in data["tickets"]:
        assert t["why"] and t["serves"] and t["question"], t["id"]


def test_seed_statuses_and_current_floor():
    view = build_view(load_board(SEED))
    by_id = {c["id"]: c for f in view["floors"] for c in f["tickets"]}
    assert by_id["Look-01"]["status"] == "approved"
    assert by_id["Look-00"]["status"] == "in-progress"
    assert by_id["Look-02"]["status"] == "blocked"
    assert by_id["Mkt-01"]["status"] == "blocked"
    assert view["current_floor"] == 1
    assert view["deadline"] == {"floors": [1, 2], "date": "2026-09-20"}
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest tests/test_board.py -q`
Expected: 2 failures, `FileNotFoundError` / `BoardError` for the missing seed.

- [ ] **Step 3: Write the seed file**

Create `plans/control-panel/tickets.json` with exactly this content:

```json
{
  "version": 1,
  "updated": "2026-09-13",
  "deadline": {"floors": [1, 2], "date": "2026-09-20"},
  "lanes": ["Control Panel", "Marketing"],
  "categories": {
    "Control Panel": ["Words", "Look", "Formats", "Machine", "Measure"],
    "Marketing": ["Campaign", "Engagement", "Ads and data", "Curators and labels", "Cadence"]
  },
  "tickets": [
    {
      "id": "Words-01", "lane": "Control Panel", "category": "Words", "floor": 1,
      "title": "The sound paragraph",
      "why": "Every bio, pitch, caption and brief has to describe the songs, and no document describes them yet. The old sound paragraph is the electronic era.",
      "serves": "positioning.md v2, Spotify and label pitch language, curator matching, image DNA (mood follows sound). Marketing: all campaign copy.",
      "question": "In your words: what makes the sound (synths, guitars, drums, playback), the voice and where it sits, tempo and feel, what a chorus does, the themes, two or three example songs, and what the songs are not.",
      "status": "proposed", "blocked_on": [], "size": "S", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/positioning.md v2, sound section"],
      "notes": ["2026-09-13 opened. Amir: answer when the board is live, not before."]
    },
    {
      "id": "Words-03", "lane": "Control Panel", "category": "Words", "floor": 1,
      "title": "Proof facts refresh",
      "why": "proof.md is the source of every public fact and still says three EPs in 2026 and nothing about Ambertone or Indigo Children releases.",
      "serves": "Bios, EPK, pitch copy, YouTube descriptions. Marketing: label and press pitches.",
      "question": "Confirm the list: labels, venues, Dark Matter, Ambertone, Indigo Children releases (Farewell, The Deceiver, Pinocchio), Double Figure rule. What to drop, what to add.",
      "status": "proposed", "blocked_on": [], "size": "XS", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/proof.md"],
      "notes": ["2026-09-13 opened."]
    },
    {
      "id": "Look-00", "lane": "Control Panel", "category": "Look", "floor": 1,
      "title": "Strip industrial, EBM, techno from the brand docs",
      "why": "The brand docs still describe the electronic era and the tools read them. Cleanup, no decision needed.",
      "serves": "Everything downstream reads clean docs.",
      "question": "None. Files: positioning.md, proof.md, CONTROL-PANEL.md, the brand section of ig-agent-context.md. Lines that name industrial, EBM, techno, three EPs, or a songs era later get removed or marked as history.",
      "status": "in-progress", "blocked_on": [], "size": "S", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/*.md", "docs/ig-agent-context.md brand section"],
      "notes": ["2026-09-13 opened as cleanup."]
    },
    {
      "id": "Look-01", "lane": "Control Panel", "category": "Look", "floor": 1,
      "title": "Type system",
      "why": "One pair of faces for every text object (reels, thumbnails, story cards, cover credits, the wordmark), or the brand fractures across tools.",
      "serves": "All formats. frame.md type section, Canva Brand Kit fonts, HyperFrames variables, image-studio cards, YouTube thumbnails. Marketing: every campaign asset inherits it.",
      "question": "Which pair: A Barlow 900 + IBM Plex Mono, B Archivo Black + Space Mono, C Anton/Oswald + JetBrains Mono, D Syne/Unbounded + IBM Plex Mono, or a new candidate from your references. Then sizes and weights per use.",
      "status": "approved", "blocked_on": [], "size": "S", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/frame.md type section", "Canva Brand Kit fonts", "videos/*/frame.md variables"],
      "notes": ["2026-09-13 approved by Amir (fonts first). Renders of A to D exist in docs/brand/VIDEO-BRAND-SESSION-KIT.md. Ask for references before showing options."]
    },
    {
      "id": "Look-03", "lane": "Control Panel", "category": "Look", "floor": 1,
      "title": "Colour numbers",
      "why": "Tools need hex values; prose palettes cannot be applied. The per-single palette rule needs a constant core to sit on.",
      "serves": "frame.md, Canva Brand Kit colours, image studio grade, HyperFrames, thumbnails. Marketing: every campaign asset.",
      "question": "Approve or adjust the hexes for the core and for oxblood, cold, sepia. Confirm the rule: each single samples its palette from its artwork, the core stays constant.",
      "status": "proposed", "blocked_on": [], "size": "S", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/frame.md colour section", "palettes/*.txt with hexes", "Canva Brand Kit colours"],
      "notes": ["2026-09-13 opened. Candidate hexes in CONTROL-PANEL-SETUP-ROADMAP.md phase 2. Ask for references (images) first."]
    },
    {
      "id": "Look-04", "lane": "Control Panel", "category": "Look", "floor": 1,
      "title": "Image DNA and motif list",
      "why": "The constant visual DNA was written for the electronic era, and the motifs that are already brand (sunglasses, black nails) are not written anywhere.",
      "serves": "Image studio prompt, shoot briefs, video frames, thumbnails, Look-05, Look-09.",
      "question": "What stays from inch_of_shadow_style.txt and what changes. The motif list. Faces lit or obscured by context. Subject mix (figures, places, objects, symbols). Real vs abstract. Medium and texture.",
      "status": "proposed", "blocked_on": [], "size": "M", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["inch_of_shadow_style.txt v2", "docs/brand/frame.md image section", "motif list"],
      "notes": ["2026-09-13 opened. Ask for references (photos, artists, posts); analyse each before options."]
    },
    {
      "id": "Look-08", "lane": "Control Panel", "category": "Look", "floor": 1,
      "title": "Shoot catalogue",
      "why": "The recent photoshoot is the first song-era image bank. Uncatalogued, no tool can use it and nobody finds the right frame later.",
      "serves": "Every photo post, thumbnails, press, the Canva library, Look-09, Look-10.",
      "question": "Where the edited photos and the raws live. Tag scheme: use (face, portrait, full body, place, detail), orientation, motifs present, grade (hero, good, spare). Each edited photo points at its raw.",
      "status": "proposed", "blocked_on": [], "size": "M", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["plans/control-panel/shoot-catalogue.json", "folder structure agreed with Amir"],
      "notes": ["2026-09-13 opened. Never move or rename Amir's files without per-action permission."]
    },
    {
      "id": "Words-02", "lane": "Control Panel", "category": "Words", "floor": 2,
      "title": "positioning.md v2",
      "why": "The file every bio and every agent reads describes the electronic era.",
      "serves": "Bios (bio skill), Spotify pitch language, IG agent brand snapshot, label pitch. Marketing: all copy.",
      "question": "Approve the rewrite: who, the sound (from Words-01), the scene, mood words, the anti-list replacing 'not bright or poppy'.",
      "status": "proposed", "blocked_on": ["Words-01", "Words-03"], "size": "S", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/positioning.md"],
      "notes": ["2026-09-13 opened. 'dark dance wave' stays as the coined phrase (Amir)."]
    },
    {
      "id": "Look-02", "lane": "Control Panel", "category": "Look", "floor": 2,
      "title": "Logo mark",
      "why": "You want one simple mark to sign any photo (a venue shot, a story) without a full artwork layer.",
      "serves": "Photo posts, stories, thumbnail corner, the sting, gig announcements, Canva Brand Kit logo. Marketing: gig and press material.",
      "question": "Direction: the inch mark (ruler tick), lowercase wordmark, monogram, or another. Size and placement rules. When the mark is used versus the no-text-in-artwork rule (two rules, two objects).",
      "status": "proposed", "blocked_on": ["Look-01"], "size": "S", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/mark.svg", "docs/brand/frame.md mark section", "Canva Brand Kit logo"],
      "notes": ["2026-09-13 opened. Ask for references first."]
    },
    {
      "id": "Look-05", "lane": "Control Panel", "category": "Look", "floor": 2,
      "title": "Face rules",
      "why": "The face is the conversion asset and the most sensitive one: never AI-redrawn, sunglasses are brand, their removal is a rare pattern-interrupt.",
      "serves": "Shoot briefs, image studio composite, reels, thumbnails, captions placement.",
      "question": "Lit or obscured, by context. Sunglasses on and off rule. What is never done with the face.",
      "status": "proposed", "blocked_on": ["Look-04"], "size": "XS", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/frame.md face section"],
      "notes": ["2026-09-13 opened."]
    },
    {
      "id": "Look-06", "lane": "Control Panel", "category": "Look", "floor": 2,
      "title": "Motion register and anti-brand",
      "why": "Every video needs one way of moving, and a written anti-brand line is what stops drift when things get made fast.",
      "serves": "HyperFrames sting, transitions, caption identity, reel briefs. Formats floor.",
      "question": "Hard cut or slow burn, or both keyed to register. Approve the anti-brand list. The sting.",
      "status": "proposed", "blocked_on": ["Look-01", "Look-03"], "size": "M", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/frame.md motion section", "rendered sting", "caption identity choice"],
      "notes": ["2026-09-13 opened. Ask for video references; run them through /video-analyze."]
    },
    {
      "id": "Look-09", "lane": "Control Panel", "category": "Look", "floor": 2,
      "title": "Our own edit recipe",
      "why": "The raws exist. A repeatable grade lets us make new images from the shoot without the photographer, matched to the palette.",
      "serves": "Future photo posts, thumbnails, Canva, the image studio grade mode.",
      "question": "Approve the recipe tested on three raws against the photographer's edits.",
      "status": "proposed", "blocked_on": ["Look-03", "Look-04", "Look-08"], "size": "M", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/edit-recipe.md", "three test edits"],
      "notes": ["2026-09-13 opened."]
    },
    {
      "id": "Look-07", "lane": "Control Panel", "category": "Look", "floor": 2,
      "title": "frame.md v1, the spec",
      "why": "The one file every tool is supposed to read does not exist yet. Mass production unlocks here.",
      "serves": "HyperFrames, image studio, Canva Brand Kit, YouTube thumbnails, IG agent. Formats and Machine floors.",
      "question": "Approve the assembled file: type, colour, mark, image, face, motion, references.",
      "status": "proposed", "blocked_on": ["Words-02", "Look-02", "Look-03", "Look-04", "Look-05", "Look-06"], "size": "S", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/frame.md"],
      "notes": ["2026-09-13 opened."]
    },
    {
      "id": "Formats-01", "lane": "Control Panel", "category": "Formats", "floor": 3,
      "title": "The fixed set per single",
      "why": "A fixed set makes each single a checklist instead of a debate, and lets the machine be wired once.",
      "serves": "Release skill checklist, content calendar, Machine-01. Marketing: the campaign template.",
      "question": "Which objects always exist per single (cover, canvas, teaser reel, release reel, lyric object, YouTube video, Shorts, TikTok, story set, thumbnail). What exists between singles. What the album wrap adds.",
      "status": "proposed", "blocked_on": ["Look-07"], "size": "M", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/formats.md", "release_manager checklist template update"],
      "notes": ["2026-09-13 opened."]
    },
    {
      "id": "Formats-02", "lane": "Control Panel", "category": "Formats", "floor": 3,
      "title": "Reel rules: one craft file wins",
      "why": "videos/IOS-REEL-CRAFT.md and plans/ig-content-craft-reference.md contradict each other on hooks, pacing and lyric reveals.",
      "serves": "Every reel brief, the IG agent, HyperFrames templates.",
      "question": "Which claims survive: the verified list wins by default, our own performance log breaks ties. Retire the loser with a pointer.",
      "status": "proposed", "blocked_on": ["Formats-01"], "size": "S", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["one craft file", "the other marked retired"],
      "notes": ["2026-09-13 opened."]
    },
    {
      "id": "Formats-03", "lane": "Control Panel", "category": "Formats", "floor": 3,
      "title": "YouTube formats",
      "why": "The YouTube agent is live and only art tracks have been used. Visualizer, Shorts, Premiere, end screens and thumbnail style are undecided.",
      "serves": "youtube/PLAYBOOK.md runbook, Machine-03. Marketing: release-day YouTube plan.",
      "question": "Per single: visualizer or art track, Shorts yes or no, Premiere yes or no, end screens and cards, thumbnail style from the type and mark decisions.",
      "status": "proposed", "blocked_on": ["Formats-01"], "size": "S", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["youtube/PLAYBOOK.md formats section"],
      "notes": ["2026-09-13 opened."]
    },
    {
      "id": "Formats-04", "lane": "Control Panel", "category": "Formats", "floor": 3,
      "title": "TikTok formats",
      "why": "No TikTok plan exists, and the March recipe (trending sounds, duets) conflicts with the voice rules.",
      "serves": "TikTok opening before the bridge single, Machine-04. Marketing: bridge campaign.",
      "question": "Two or three native formats in your voice. Cadence. What is never posted there.",
      "status": "proposed", "blocked_on": ["Formats-01"], "size": "S", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/formats.md TikTok section"],
      "notes": ["2026-09-13 opened. Ask for TikTok references; analyse them."]
    },
    {
      "id": "Machine-01", "lane": "Control Panel", "category": "Machine", "floor": 4,
      "title": "Who makes what",
      "why": "Five tools overlap (image studio, HyperFrames, Canva, YouTube agent, IG agent). Each format needs one owner or work gets done twice.",
      "serves": "Speed and consistency of every brief. Look-10, Machine-02.",
      "question": "The matrix format to tool, including what stays by hand.",
      "status": "proposed", "blocked_on": ["Formats-01"], "size": "M", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["docs/brand/machine.md"],
      "notes": ["2026-09-13 opened."]
    },
    {
      "id": "Machine-02", "lane": "Control Panel", "category": "Machine", "floor": 4,
      "title": "frame.md wired into the tools",
      "why": "Decisions must reach the tools without retyping: HyperFrames variables, Canva Brand Kit, the image studio prompt.",
      "serves": "Every render from here on.",
      "question": "None, build: HyperFrames variables file from frame.md, Canva Brand Kit upload (fonts, colours, mark), inch_of_shadow_style.txt regenerated from frame.md.",
      "status": "proposed", "blocked_on": ["Look-07"], "size": "M", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["videos/frame.md", "Canva Brand Kit", "inch_of_shadow_style.txt"],
      "notes": ["2026-09-13 opened."]
    },
    {
      "id": "Look-10", "lane": "Control Panel", "category": "Look", "floor": 4,
      "title": "Shoot in the machine",
      "why": "The catalogued shoot should be pullable by any tool: image studio grade and composite, HyperFrames footage treatments, the Canva library.",
      "serves": "Any brief that says 'hero face, vertical, sunglasses' without searching.",
      "question": "None, build: the catalogue readable by the tools, hero set uploaded to Canva assets.",
      "status": "proposed", "blocked_on": ["Look-08", "Machine-01"], "size": "S", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["catalogue consumed by tools", "Canva assets folder"],
      "notes": ["2026-09-13 opened."]
    },
    {
      "id": "Machine-03", "lane": "Control Panel", "category": "Machine", "floor": 4,
      "title": "YouTube agent hooks",
      "why": "The release skill should trigger the YouTube steps (metadata, schedule, playlists, thumbnails) instead of a separate checklist.",
      "serves": "Release day for every single. Marketing: campaign template.",
      "question": "Which steps automate and which stay manual (upload stays manual by rule).",
      "status": "proposed", "blocked_on": ["Formats-03"], "size": "S", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["release skill step list", "youtube/tools hooks"],
      "notes": ["2026-09-13 opened."]
    },
    {
      "id": "Machine-04", "lane": "Control Panel", "category": "Machine", "floor": 4,
      "title": "TikTok setup",
      "why": "The account, link and export path have to exist before the bridge single, not during it.",
      "serves": "TikTok opening 6 to 8 weeks before the bridge. Marketing: bridge campaign.",
      "question": "Profile (same name, bio line, smart link), export preset check (video_resizer TikTok preset), posting flow, who posts.",
      "status": "proposed", "blocked_on": ["Formats-04"], "size": "S", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["TikTok profile live", "posting flow written"],
      "notes": ["2026-09-13 opened."]
    },
    {
      "id": "Mkt-01", "lane": "Marketing", "category": "Campaign", "floor": 6,
      "title": "'dark dance wave' SEO check",
      "why": "The coined phrase leads the bios; whether it is unique and searchable in the genre is believed, not confirmed.",
      "serves": "Bios, name field, YouTube descriptions, the phrase's place in positioning.",
      "question": "Search results and competing uses on Spotify, SoundCloud, Bandcamp, YouTube, Google. Keep, adjust, or add a second descriptor.",
      "status": "proposed", "blocked_on": ["Words-02"], "size": "XS", "references": [],
      "decision": "", "decided_on": "",
      "outputs": ["seo note in docs/brand/positioning.md"],
      "notes": ["2026-09-13 parked by Amir until the Control Panel is done."]
    }
  ]
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m pytest tests/test_board.py -q`
Expected: 20 passed.

- [ ] **Step 5: Commit**

```bash
git add plans/control-panel/tickets.json tests/test_board.py
git commit -m "board: seed the control panel tickets (23)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: The `/board` page

**Files:**
- Modify: `release_manager/webapp.py` (insert after the `palette()` route, i.e. after the line `return render_template("palette.html", sections=sections)` near line 384)
- Modify: `release_manager/templates/base.html` (sidebar nav, insert a "Plan" group after the "Releases" group, near line 42)
- Create: `release_manager/templates/board.html`
- Modify: `release_manager/static/style.css` (append)
- Test: `tests/test_board.py` (append)

**Interfaces:**
- Consumes: `load_board`, `build_view`, `BoardError` from Tasks 1 and 2; `PROJECT_ROOT` (already defined in `webapp.py` line 140) and `render_template`.
- Produces: `GET /board` (endpoint name `board_page`), template context `view` (from `build_view`) and `cards_json` (list of all cards, JSON-serialised with Jinja's `tojson`).

- [ ] **Step 1: Write the failing route tests** (append)

```python
@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("FLASK_SECRET_KEY", "test")
    from release_manager.webapp import app
    app.config["TESTING"] = True
    return app.test_client()


def test_board_route_renders_every_seed_ticket(client):
    r = client.get("/board")
    assert r.status_code == 200
    html = r.data.decode()
    for tid in SEED_IDS:
        assert tid in html
    assert "Foundation" in html and "Marketing" in html


def test_board_route_shows_derived_blocked_status(client):
    html = client.get("/board").data.decode()
    # Look-02 is proposed in the file but blocked on Look-01 (not done)
    assert 'data-id="Look-02" data-status="blocked"' in html


def test_board_route_has_plan_link_in_sidebar(client):
    html = client.get("/board").data.decode()
    assert 'href="/board"' in html
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest tests/test_board.py -q`
Expected: 3 failures, 404 on `/board`.

- [ ] **Step 3: Add the route**

Insert into `release_manager/webapp.py` directly after the `palette()` function:

```python
@app.route("/board")
def board_page():
    """Control Panel Board: read-only tower view of plans/control-panel/tickets.json."""
    from release_manager.board import BoardError, build_view, load_board
    board_file = PROJECT_ROOT / "plans" / "control-panel" / "tickets.json"
    try:
        data = load_board(board_file)
    except BoardError as e:
        return render_template("board.html", view=None, cards_json=[], error=str(e)), 500
    view = build_view(data)
    cards = [c for f in view["floors"] for c in f["tickets"]]
    return render_template("board.html", view=view, cards_json=cards, error=None)
```

- [ ] **Step 4: Add the sidebar link**

In `release_manager/templates/base.html`, after the `Releases` sidebar group (the `<div class="sidebar-group">` that contains the Dashboard link), insert:

```html
                <div class="sidebar-group">
                    <div class="sidebar-group-label">Plan</div>
                    <a href="{{ url_for('board_page') }}" class="sidebar-link{% if request.endpoint == 'board_page' %} active{% endif %}">Board</a>
                </div>
```

- [ ] **Step 5: Write the template**

Create `release_manager/templates/board.html`:

```html
{% extends "base.html" %}
{% block title %}Board{% endblock %}

{% block content %}
<div class="board-page">
{% if error %}
    <h1>Board</h1>
    <div class="board-error">
        <strong>tickets.json is not valid.</strong>
        <pre>{{ error }}</pre>
    </div>
{% else %}
    <div class="board-top">
        <div>
            <h1>Board</h1>
            <p class="form-subtitle">Top to bottom is build order. Each floor unlocks the next. Source: plans/control-panel/tickets.json, updated {{ view.updated }}.</p>
        </div>
        <div class="board-kpis">
            <div class="board-kpi"><div class="k">Waiting on you</div><div class="v gold">{{ view.waiting_on_amir }}</div></div>
            <div class="board-kpi"><div class="k">Floor now</div><div class="v">{{ view.current_floor }} of 6</div></div>
            <div class="board-kpi"><div class="k">Deadline</div><div class="v">{{ view.deadline.date or "none" }}</div></div>
        </div>
    </div>

    <div class="board-filters" id="board-filters">
        <button class="chip on" data-filter="hide-done">Hide done</button>
        <button class="chip" data-filter="waiting">Waiting on Amir</button>
        <button class="chip" data-filter="lane:Control Panel">Control Panel</button>
        <button class="chip" data-filter="lane:Marketing">Marketing</button>
    </div>
    <div class="board-legend">
        <span><i class="sw cat-words"></i>Words</span>
        <span><i class="sw cat-look"></i>Look</span>
        <span><i class="sw cat-formats"></i>Formats</span>
        <span><i class="sw cat-machine"></i>Machine</span>
        <span><i class="sw cat-measure"></i>Measurement</span>
        <span><i class="sw cat-mkt"></i>Marketing</span>
    </div>

    <div class="tower">
    {% for f in view.floors %}
        {% if not loop.first %}<div class="connector">unlocks</div>{% endif %}
        <div class="floor{% if f.is_current %} current{% endif %}{% if f.n == 6 %} mk{% endif %}" data-floor="{{ f.n }}">
            <div class="floor-label">
                <div class="n">{{ f.n }}</div>
                <div class="name">{{ f.name }}</div>
                <div class="needs">{% if f.after %}after floor {{ f.after }}{% else %}start here{% endif %}</div>
                {% if f.is_current %}<div class="status">building now</div>{% endif %}
            </div>
            <div class="cards">
            {% for c in f.tickets %}
                <button class="tcard cat-{{ c.category_slug if c.lane == 'Control Panel' else 'mkt' }}"
                        data-id="{{ c.id }}" data-status="{{ c.status }}" data-lane="{{ c.lane }}">
                    <span class="row"><span class="tid">{{ c.id }}</span><span class="pill st-{{ c.status }}">{{ c.status }}</span></span>
                    <span class="ttitle">{{ c.title }}</span>
                    {% if c.needs %}<span class="dep">needs {{ c.needs|join(", ") }}</span>{% endif %}
                </button>
            {% else %}
                <div class="tghost">{% if f.n == 5 %}parent added when floor 3 is decided{% elif f.n == 6 %}opens after the Control Panel{% else %}empty{% endif %}</div>
            {% endfor %}
            </div>
        </div>
    {% endfor %}
    </div>

    <section class="tdetail" id="tdetail" hidden>
        <div class="head">
            <div><span class="lanechip" id="d-lane"></span><h2 id="d-title"></h2></div>
            <span class="pill" id="d-status"></span>
        </div>
        <div class="field"><div class="k">Why</div><div class="v" id="d-why"></div></div>
        <div class="field"><div class="k">Serves</div><div class="v" id="d-serves"></div></div>
        <div class="field"><div class="k">Question</div><div class="v" id="d-question"></div></div>
        <div class="field"><div class="k">References</div><div class="v" id="d-references"></div></div>
        <div class="field"><div class="k">Needs</div><div class="v" id="d-needs"></div></div>
        <div class="field"><div class="k">Unblocks</div><div class="v" id="d-unblocks"></div></div>
        <div class="field"><div class="k">Outputs</div><div class="v" id="d-outputs"></div></div>
        <div class="field"><div class="k">Decision</div><div class="v" id="d-decision"></div></div>
        <div class="field"><div class="k">Notes</div><div class="v" id="d-notes"></div></div>
    </section>

    <script id="board-data" type="application/json">{{ cards_json|tojson }}</script>
    <script>
    (function () {
        var cards = JSON.parse(document.getElementById('board-data').textContent);
        var byId = {};
        cards.forEach(function (c) { byId[c.id] = c; });

        var state = { hideDone: true, waiting: false, lane: null };
        function applyFilters() {
            document.querySelectorAll('.tcard').forEach(function (el) {
                var st = el.dataset.status, lane = el.dataset.lane, show = true;
                if (state.hideDone && st === 'done') show = false;
                if (state.waiting && st !== 'proposed') show = false;
                if (state.lane && lane !== state.lane) show = false;
                el.hidden = !show;
            });
        }
        document.getElementById('board-filters').addEventListener('click', function (e) {
            var b = e.target.closest('button'); if (!b) return;
            var f = b.dataset.filter;
            if (f === 'hide-done') { state.hideDone = !state.hideDone; b.classList.toggle('on', state.hideDone); }
            else if (f === 'waiting') { state.waiting = !state.waiting; b.classList.toggle('on', state.waiting); }
            else if (f.indexOf('lane:') === 0) {
                var lane = f.slice(5);
                state.lane = (state.lane === lane) ? null : lane;
                document.querySelectorAll('[data-filter^="lane:"]').forEach(function (x) {
                    x.classList.toggle('on', x.dataset.filter === 'lane:' + state.lane);
                });
            }
            applyFilters();
        });

        function text(id, value) { document.getElementById(id).textContent = value || '—'; }
        function list(id, items, fmt) {
            var el = document.getElementById(id); el.textContent = '';
            if (!items || !items.length) { el.textContent = '—'; return; }
            var ul = document.createElement('ul');
            items.forEach(function (it) { var li = document.createElement('li'); li.textContent = fmt ? fmt(it) : it; ul.appendChild(li); });
            el.appendChild(ul);
        }
        function open(id) {
            var c = byId[id]; if (!c) return;
            document.querySelectorAll('.tcard.open').forEach(function (x) { x.classList.remove('open'); });
            document.querySelector('.tcard[data-id="' + id + '"]').classList.add('open');
            text('d-lane', c.lane + ' · ' + c.category + ' · floor ' + c.floor + (c.size ? ' · size ' + c.size : ''));
            text('d-title', c.id + ' ' + c.title);
            var st = document.getElementById('d-status'); st.textContent = c.status; st.className = 'pill st-' + c.status;
            text('d-why', c.why); text('d-serves', c.serves); text('d-question', c.question);
            list('d-references', c.references, function (r) { return (r.type ? r.type + ': ' : '') + (r.path_or_url || '') + (r.note ? ' (' + r.note + ')' : ''); });
            list('d-needs', c.needs); list('d-unblocks', c.unblocks); list('d-outputs', c.outputs);
            text('d-decision', c.decision ? c.decision + (c.decided_on ? ' (' + c.decided_on + ')' : '') : '');
            list('d-notes', c.notes);
            var d = document.getElementById('tdetail'); d.hidden = false;
            d.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        document.querySelectorAll('.tcard').forEach(function (el) {
            el.addEventListener('click', function () { open(el.dataset.id); });
        });
        applyFilters();
    })();
    </script>
{% endif %}
</div>
{% endblock %}
```

- [ ] **Step 6: Append the styles**

Append to `release_manager/static/style.css`:

```css
/* ============================================================
   Control Panel Board (/board)
   ============================================================ */
.board-page { display: grid; gap: 18px; }
.board-top { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap; }
.board-kpis { display: flex; gap: 22px; }
.board-kpi .k { font-size: 10px; letter-spacing: .08em; text-transform: uppercase; color: var(--text-secondary); opacity: .7; }
.board-kpi .v { font-family: var(--font-heading); font-size: 20px; font-weight: 700; }
.board-kpi .v.gold { color: var(--text-accent); }
.board-error pre { background: var(--bg-tertiary); padding: 12px; border-radius: var(--radius); white-space: pre-wrap; }

.board-filters { display: flex; gap: 6px; flex-wrap: wrap; }
.board-filters .chip { border: 1px solid var(--border-color); background: var(--bg-secondary); color: var(--text-secondary); font-size: 11px; padding: 4px 9px; border-radius: 999px; cursor: pointer; font-family: var(--font-main); }
.board-filters .chip.on { border-color: var(--text-accent); color: var(--text-accent); background: var(--accent-dim); }
.board-legend { display: flex; gap: 12px; font-size: 11px; color: var(--text-secondary); flex-wrap: wrap; }
.board-legend .sw { display: inline-block; width: 9px; height: 9px; border-radius: 2px; margin-right: 5px; vertical-align: middle; }

.tower { display: grid; }
.floor { display: grid; grid-template-columns: 120px 1fr; border: 1px solid var(--border-color); background: var(--bg-secondary); margin-top: -1px; }
.floor.current { border-color: var(--text-accent); background: #141208; }
.floor.mk { background: var(--bg-primary); border-style: dashed; }
.floor-label { padding: 14px; border-right: 1px solid var(--border-color); display: grid; align-content: start; gap: 4px; }
.floor-label .n { font-family: var(--font-heading); font-weight: 700; font-size: 22px; line-height: 1; }
.floor.current .n { color: var(--text-accent); }
.floor-label .name { font-size: 12px; font-weight: 600; }
.floor-label .needs, .floor-label .status { font-size: 11px; color: var(--text-secondary); opacity: .75; font-family: var(--font-mono); }
.connector { color: var(--text-secondary); opacity: .6; font-size: 11px; padding: 6px 0 6px 120px; font-family: var(--font-mono); text-align: center; }
.connector::before { content: "\25BC  "; }

.cards { padding: 12px; display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 8px; align-content: start; }
.tcard { background: var(--bg-tertiary); border: 1px solid var(--border-color); border-left-width: 3px; border-radius: var(--radius); padding: 8px 10px; display: grid; gap: 4px; cursor: pointer; text-align: left; color: var(--text-primary); font-family: var(--font-main); }
.tcard:hover { background: var(--bg-hover); }
.tcard.open { outline: 1px solid var(--text-accent); }
.tcard:focus-visible { outline: 2px solid var(--text-accent); }
.tcard .row { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.tcard .tid { font-family: var(--font-mono); font-size: 11px; color: var(--text-secondary); opacity: .8; }
.tcard .ttitle { font-size: 13px; font-weight: 500; line-height: 1.3; }
.tcard .dep { font-size: 10px; color: var(--text-secondary); opacity: .75; font-family: var(--font-mono); }
.tghost { border: 1px dashed var(--border-color); border-radius: var(--radius); padding: 10px; font-size: 12px; color: var(--text-secondary); opacity: .7; text-align: center; }

.pill { font-size: 9px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; padding: 2px 6px; border-radius: 999px; color: #fff; white-space: nowrap; }
.pill.st-proposed { background: #3a3a3a; color: var(--text-secondary); }
.pill.st-approved { background: var(--color-warning); color: #111; }
.pill.st-in-progress { background: var(--color-progress); }
.pill.st-blocked { background: var(--color-overdue); }
.pill.st-done { background: var(--color-done); }

.cat-words { border-left-color: #7a5c9e; } .sw.cat-words { background: #7a5c9e; }
.cat-look { border-left-color: #b0563a; } .sw.cat-look { background: #b0563a; }
.cat-formats { border-left-color: #3f7f8a; } .sw.cat-formats { background: #3f7f8a; }
.cat-machine { border-left-color: #6d7f5a; } .sw.cat-machine { background: #6d7f5a; }
.cat-measure { border-left-color: #8a7f3f; } .sw.cat-measure { background: #8a7f3f; }
.cat-mkt { border-left-color: #555; } .sw.cat-mkt { background: #555; }

.tdetail { background: var(--bg-secondary); border: 1px solid var(--text-accent); border-radius: var(--radius-lg); padding: 16px 18px; display: grid; gap: 10px; }
.tdetail .head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap; }
.tdetail h2 { font-family: var(--font-heading); font-size: 17px; margin: 0; }
.tdetail .lanechip { font-size: 11px; color: var(--text-accent); font-family: var(--font-mono); }
.tdetail .field { display: grid; grid-template-columns: 90px 1fr; gap: 10px; font-size: 13px; }
.tdetail .field .k { font-size: 10px; letter-spacing: .06em; text-transform: uppercase; color: var(--text-secondary); opacity: .7; padding-top: 3px; }
.tdetail .field .v { color: var(--text-secondary); max-width: 72ch; }
.tdetail .field .v ul { margin: 0; padding-left: 18px; }

@media (max-width: 820px) {
    .floor { grid-template-columns: 1fr; }
    .floor-label { border-right: 0; border-bottom: 1px solid var(--border-color); }
    .connector { padding-left: 0; }
    .tdetail .field { grid-template-columns: 1fr; gap: 2px; }
}
```

- [ ] **Step 7: Run the tests to verify they pass**

Run: `python3 -m pytest tests/test_board.py -q`
Expected: 23 passed.

- [ ] **Step 8: Look at it once**

Run the RM (`python3 -m release_manager.webapp` from `Inchofshadowcode/`, or however it is normally started), open `http://127.0.0.1:5000/board` in the Browser pane, click a card, toggle "Hide done" and "Waiting on Amir". Fix only what is visibly broken.

- [ ] **Step 9: Commit**

```bash
git add release_manager/webapp.py release_manager/templates/base.html release_manager/templates/board.html release_manager/static/style.css tests/test_board.py
git commit -m "board: read-only /board tower page in the Release Manager

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: Pointers from the old docs

**Files:**
- Modify: `TICKETS.md` (the B-01 row and the Log)
- Modify: `docs/brand/CONTROL-PANEL-SETUP-ROADMAP.md` (line 1 area)
- Modify: `docs/brand/VIDEO-BRAND-SESSION-KIT.md` (line 1 area)

**Interfaces:** none (docs only).

- [ ] **Step 1: TICKETS.md**

Replace the B-01 row's title cell text with:
`Brand for the song era: see the Control Panel Board (plans/control-panel/tickets.json, RM /board). Floors 1-2 due 2026-09-20`
and keep its status cell. Append to the Log:

`- 2026-09-13 BOARD LIVE: plans/control-panel/tickets.json + RM /board (read-only tower). 23 seed tickets, floors 1-4 + Mkt-01 parked. Roadmap and session-kit files now point to the board and are frozen.`

- [ ] **Step 2: Roadmap and session kit**

Insert as the second line of each file (right after the H1):

`> Superseded 2026-09-13 by the Control Panel Board: plans/control-panel/tickets.json, viewed at RM /board. This file is frozen as reference; its questions live in the board's tickets.`

- [ ] **Step 3: Run the full board test file once more**

Run: `python3 -m pytest tests/test_board.py -q`
Expected: 23 passed.

- [ ] **Step 4: Commit**

```bash
git add TICKETS.md docs/brand/CONTROL-PANEL-SETUP-ROADMAP.md docs/brand/VIDEO-BRAND-SESSION-KIT.md
git commit -m "docs: point the roadmap, session kit and TICKETS.md at the board

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Self-review

- Spec coverage: schema (Task 1, 3), validator cases (Task 1 tests), derived blocked (Task 2), page with header numbers, filters, legend, tower, cards, detail panel, RM styling, sidebar (Task 4), seed of 23 (Task 3), pointers and B-01 (Task 5), read-only (no POST anywhere), tests as listed. Working rules and "out of scope" are process, not code.
- Placeholders: none; every code step has its content.
- Names: `load_board`, `validate`, `BoardError`, `effective_status`, `build_view`, `category_slug`, `board_page`, `cards_json`, `view` are used consistently across tasks. Test count: 12 + 6 + 2 + 3 = 23.
