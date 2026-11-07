"""Control Panel Board: load, validate and shape plans/control-panel/tickets.json.

The JSON file is the only source of truth. The webapp renders it and never writes it.
Spec: docs/superpowers/specs/2026-09-13-control-panel-board-design.md
"""
from __future__ import annotations

import json
import re
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
    if not isinstance(data, dict):
        return ["top-level must be an object"]
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
            prefix = ID_PREFIX[cat]
            if not re.fullmatch(re.escape(prefix) + r"-\d{2}", tid):
                errors.append(f"{tid}: id must be {prefix}-NN")
        if t.get("floor") not in FLOORS:
            errors.append(f"{tid}: floor must be 1..6")
        if "size" in t and t["size"] not in ("",) + SIZES:
            errors.append(f"{tid}: bad size {t['size']!r}")
        deps = t.get("blocked_on") or []
        if not isinstance(deps, list):
            errors.append(f"{tid}: blocked_on must be a list")
        else:
            for dep in deps:
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
        "model": t.get("model", ""),
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

    present = {c["category"] for c in cards}
    categories = [{"name": cat, "slug": category_slug(cat)}
                  for cat in LANE_OF if cat in present]

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
        "categories": categories,
        "deadline": data.get("deadline", {}) or {},
        "updated": data.get("updated", "") or "",
    }
