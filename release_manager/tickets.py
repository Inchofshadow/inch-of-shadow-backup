"""Tickets page: load, validate and shape plans/tickets.json.

This is the work queue for everything that is NOT the Control Panel (that board
lives in plans/control-panel/tickets.json and release_manager/board.py). The JSON
file is the only source of truth; the webapp renders it and never writes it.
Done tickets before 2026-09-14 stay in TICKETS.md as history.

Ticket shape (System 78, 2026-11-06, from the Gero study): one priority axis.
`bucket` (now / next / parked / routine) is the priority; the old `priority`
P1-P3 is no longer stored and is derived from the bucket for the /tickets page
only (now = P1, next = P2, parked and routine = P3). Every ticket carries
`metric`, `updated` and `done_means`; every open ticket also carries `bucket`,
`who`, `label` and `next_step`. The same checks (`_check_loop_fields`,
`check_now_cap`) run on the Control Panel board from the tests.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Optional

STATUSES = ("proposed", "approved", "in-progress", "blocked", "waiting", "done")
SECTIONS = ("General", "Release", "Maintenance", "Gap Radar")
PRIORITIES = ("P1", "P2", "P3")                     # derived view only, never stored
PRIORITY_LABEL = {"P1": "now", "P2": "next", "P3": "later"}
BUCKETS = ("now", "next", "parked", "routine")
BUCKET_PRIORITY = {"now": "P1", "next": "P2", "parked": "P3", "routine": "P3"}
WHO = ("amir", "claude", "auto")
DONE_MEANS_BY = ("amir", "claude")
NOW_CAP = 3                                          # max bucket=now per area, a cap not a quota
SIZES = ("XS", "S", "M", "L")

REQUIRED_FIELDS = ("id", "section", "title", "why", "helps", "status")
SHAPE_FIELDS_ALL = ("metric", "updated", "done_means")          # every ticket, done ones too
SHAPE_FIELDS_OPEN = ("bucket", "who", "label", "next_step")     # every ticket that is not done
NO_METRIC = "none"           # a ticket that moves no number carries metric "none" + metric_note
ISO_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EM_DASH = "—"
TARGETS_FILE = Path(__file__).resolve().parent.parent / "plans" / "targets.json"


class TicketsError(ValueError):
    """Raised when the ticket file is unreadable or fails validation."""


def metric_keys(path: Path = TARGETS_FILE) -> Optional[set]:
    """The metric keys of plans/targets.json, or None when the file cannot be read."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        keys = set(data.get("metrics") or {})
    except (OSError, ValueError, AttributeError):
        return None
    return keys or None


def validate(data: dict, keys: Optional[set] = None) -> list[str]:
    """Return a list of error strings. Empty list means the file is valid.

    keys: the allowed metric keys; None reads plans/targets.json (and skips the
    key check when that file is unreadable, so the page still renders).
    """
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["top-level must be an object"]
    tickets = data.get("tickets")
    if not isinstance(tickets, list):
        return ["top-level 'tickets' must be a list"]
    if keys is None:
        keys = metric_keys()

    seen: set[str] = set()
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
        if t.get("section") not in SECTIONS:
            errors.append(f"{tid}: bad section {t.get('section')!r}")
        if "size" in t and t["size"] not in ("",) + SIZES:
            errors.append(f"{tid}: bad size {t['size']!r}")
        if "notes" in t and not isinstance(t["notes"], list):
            errors.append(f"{tid}: notes must be a list")
        errors.extend(_check_loop_fields(tid, t, keys))
    errors.extend(check_now_cap(tickets))
    return errors


def _missing(t: dict, field: str) -> bool:
    v = t.get(field)
    return v is None or (isinstance(v, str) and not v.strip())


def _check_loop_fields(tid: str, t: dict, keys: Optional[set] = None) -> list[str]:
    """The ticket shape, one ticket at a time (both boards use it).

    Every ticket: metric (a targets key or 'none' with a metric_note), updated (ISO
    day), done_means (one line, done_means_by amir|claude). Open tickets also:
    bucket, who, label, next_step. No stored priority. No em-dash in any text.
    """
    errors: list[str] = []
    is_open = t.get("status") != "done"

    if "priority" in t:
        errors.append(f"{tid}: priority is derived from bucket since 2026-11-06, remove it")
    for f in SHAPE_FIELDS_ALL:
        if _missing(t, f):
            errors.append(f"{tid}: missing {f}")
    if is_open:
        for f in SHAPE_FIELDS_OPEN:
            if _missing(t, f):
                errors.append(f"{tid}: open ticket missing {f}")

    if "bucket" in t and t["bucket"] not in BUCKETS:
        errors.append(f"{tid}: bad bucket {t['bucket']!r} (now | next | parked | routine)")
    if "who" in t and t["who"] not in WHO:
        errors.append(f"{tid}: bad who {t['who']!r} (amir | claude | auto)")

    if "metric" in t:
        metric = t["metric"]
        if not isinstance(metric, str) or not metric.strip():
            errors.append(f"{tid}: metric must be a targets key or {NO_METRIC!r}")
        elif metric == NO_METRIC:
            if not str(t.get("metric_note", "")).strip():
                errors.append(f"{tid}: metric {NO_METRIC!r} needs a metric_note")
        elif keys is not None and metric not in keys:
            errors.append(f"{tid}: metric {metric!r} is not a plans/targets.json key")
    if "updated" in t and not (isinstance(t["updated"], str) and ISO_DAY.match(t["updated"])):
        errors.append(f"{tid}: updated must be YYYY-MM-DD")

    dm = t.get("done_means")
    if dm is not None and (not isinstance(dm, str) or "\n" in dm):
        errors.append(f"{tid}: done_means must be one line of text")
    if "done_means_by" in t and t["done_means_by"] not in DONE_MEANS_BY:
        errors.append(f"{tid}: bad done_means_by {t['done_means_by']!r} (amir | claude)")

    for field in _em_dash_fields(t):
        errors.append(f"{tid}: em-dash in {field}")
    return errors


def _em_dash_fields(t: dict) -> list[str]:
    """Names of the text fields (notes entries included) that contain an em-dash."""
    hits = []
    for k, v in t.items():
        if isinstance(v, str) and EM_DASH in v:
            hits.append(k)
        elif isinstance(v, list):
            if any(isinstance(x, str) and EM_DASH in x for x in v):
                hits.append(k)
    return hits


def check_now_cap(tickets: list, cap: int = NOW_CAP) -> list[str]:
    """Max `cap` open tickets in bucket 'now' per area; the error names the area."""
    per_area: dict = {}
    for t in tickets:
        if not isinstance(t, dict) or t.get("status") == "done" or t.get("bucket") != "now":
            continue
        area = t.get("area") or "(no area)"
        per_area[area] = per_area.get(area, 0) + 1
    return [f"area {area}: {n} open tickets in bucket 'now', cap is {cap}"
            for area, n in sorted(per_area.items()) if n > cap]


def load_tickets(path: Path) -> dict:
    """Read and validate the ticket file. Raises TicketsError on any problem."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise TicketsError(f"cannot read {path}: {e}") from e
    errors = validate(data)
    if errors:
        raise TicketsError("\n".join(errors))
    return data


def priority_of(t: dict) -> str:
    """The derived P1-P3 view of a ticket's bucket (no bucket, e.g. a done ticket: P3)."""
    return BUCKET_PRIORITY.get(t.get("bucket") or "", "P3")


def _card(t: dict) -> dict:
    priority = priority_of(t)
    return {
        "id": t["id"],
        "title": t["title"],
        "why": t["why"],
        "helps": t["helps"],
        "section": t["section"],
        "lane": t.get("lane", "") or "",
        "priority": priority,
        "priority_label": PRIORITY_LABEL[priority],
        "status": t["status"],
        "blocked_on": t.get("blocked_on", "") or "",
        "due": t.get("due", "") or "",
        "size": t.get("size", "") or "",
        "notes": t.get("notes", []) or [],
        "area": t.get("area", "") or "",
        "area_no": t.get("area_no", ""),
        "bucket": t.get("bucket", "") or "",
        "who": t.get("who", "") or "",
        "label": t.get("label", "") or "",
        "next_step": t.get("next_step", "") or "",
        "chrome": bool(t.get("chrome", False)),
        "metric": t.get("metric", "") or "",
        "metric_note": t.get("metric_note", "") or "",
        "updated": t.get("updated", "") or "",
        "done_means": t.get("done_means", "") or "",
        "done_means_by": t.get("done_means_by", "") or "",
    }


def area_label(card: dict, areas: dict) -> str:
    """'\U0001F3AC Socials 14': how a ticket is shown to Amir (area_rule). Falls back to the id."""
    if card.get("area") and card.get("area_no") not in ("", None):
        return "%s %s" % (areas.get(card["area"], card["area"]), card["area_no"])
    return card["id"]


def _sort_key(c: dict):
    # bucket (as derived priority) first, then dated before undated, then date, then id
    return (PRIORITIES.index(c["priority"]), c["due"] == "", c["due"], c["id"])


def build_view(data: dict) -> dict:
    """Shape a validated file into what the template renders."""
    cards = sorted((_card(t) for t in data.get("tickets", [])), key=_sort_key)
    open_cards = [c for c in cards if c["status"] != "done"]

    sections = []
    for name in SECTIONS:
        mine = [c for c in cards if c["section"] == name]
        sections.append({
            "name": name,
            "tickets": mine,
            "open_count": sum(1 for c in mine if c["status"] != "done"),
        })

    dated = [c for c in open_cards if c["due"]]
    nxt = min(dated, key=lambda c: c["due"]) if dated else None
    now_count = sum(1 for c in open_cards if c["bucket"] == "now")

    return {
        "sections": sections,
        "open_count": len(open_cards),
        "now_count": now_count,
        "p1_count": now_count,          # old name kept for the template: P1 is the derived view of 'now'
        "next_due": {"date": nxt["due"], "id": nxt["id"]} if nxt else None,
        "updated": data.get("updated", "") or "",
    }


# ------------------------------------------------------------ by number

BUCKET_ORDER = ("now", "next", "", "routine", "parked")


def metric_readings(targets: dict, today: Optional[date] = None) -> dict:
    """Per targets key: label, unit, latest value and the rung in force (from the stats sources).

    Reads through the score board's series resolver; a missing source gives an
    empty value, never an error, so the tickets page keeps rendering.
    """
    from release_manager.score_board import _fmt, series_for   # lazy: pulls the stats stack
    from stats.targets import current_rung
    today = today or date.today()
    out = {}
    for key, m in (targets.get("metrics") or {}).items():
        try:
            series = series_for(m.get("source", ""))
        except Exception:
            series = []
        last = series[-1] if series else None
        try:
            rung = current_rung(m, today) if m.get("kind") == "ladder" else None
        except (TypeError, ValueError):
            rung = None
        out[key] = {
            "label": m.get("label", key),
            "unit": m.get("unit", ""),
            "kind": m.get("kind", ""),
            "value": _fmt(last["value"]) if last else "",
            "as_of": last["date"] if last else "",
            "rung": _fmt(rung[1]) if rung else "",
            "rung_date": rung[0] if rung else "",
            "floor": _fmt(m["floor"]) if m.get("kind") == "floor" and "floor" in m else "",
            "proposed": bool(m.get("proposed_by")) and not m.get("confirmed", False),
        }
    return out


def control_panel_cards(cp_data: dict) -> list:
    """Control Panel tickets in the card shape build_metric_view takes (open ones only)."""
    out = []
    for t in cp_data.get("tickets", []):
        if not isinstance(t, dict) or t.get("status") == "done":
            continue
        priority = priority_of(t)
        out.append({
            "id": t.get("id", "?"), "title": t.get("title", ""), "why": t.get("why", ""),
            "helps": t.get("serves", ""), "section": "Control Panel", "lane": t.get("lane", "") or "",
            "priority": priority, "priority_label": PRIORITY_LABEL[priority], "status": t.get("status", ""),
            "blocked_on": ", ".join(t.get("blocked_on") or []), "due": "", "size": t.get("size", "") or "",
            "notes": t.get("notes", []) or [], "area": t.get("area", "") or "", "area_no": t.get("area_no", ""),
            "bucket": t.get("bucket", "") or "", "who": t.get("who", "") or "", "label": t.get("label", "") or "",
            "next_step": t.get("next_step", "") or "", "chrome": bool(t.get("chrome", False)),
            "metric": t.get("metric", "") or "", "metric_note": t.get("metric_note", "") or "",
            "updated": t.get("updated", "") or "",
            "done_means": t.get("done_means", "") or "", "done_means_by": t.get("done_means_by", "") or "",
            "board": "control-panel",
        })
    return out


def _metric_sort_key(c: dict):
    bucket = c.get("bucket", "")
    return (BUCKET_ORDER.index(bucket) if bucket in BUCKET_ORDER else len(BUCKET_ORDER), c["id"])


def build_metric_view(data: dict, readings: dict, extra_cards: Optional[list] = None) -> dict:
    """Open tickets grouped under the number they move, in targets order; 'none' last.

    readings: metric_readings() output (or any {key: {label, value, rung, ...}}).
    extra_cards: open cards from another board (the Control Panel) in the same card shape.
    """
    areas = data.get("areas") or {}
    cards = [_card(t) for t in data.get("tickets", [])]
    for c in cards:
        c["board"] = "tickets"
    cards.extend(extra_cards or [])
    open_cards = [c for c in cards if c["status"] != "done"]
    for c in open_cards:
        c["shown_as"] = area_label(c, areas)

    by_key: dict = {}
    for c in open_cards:
        by_key.setdefault(c["metric"] or NO_METRIC, []).append(c)

    groups = []
    order = list(readings.keys()) + [k for k in by_key if k not in readings and k != NO_METRIC] + [NO_METRIC]
    for key in order:
        mine = sorted(by_key.get(key, []), key=_metric_sort_key)
        if key == NO_METRIC:
            head = {"label": "No number", "value": "", "rung": "", "rung_date": "", "unit": "", "floor": "",
                    "kind": "", "proposed": False, "as_of": ""}
        else:
            head = readings.get(key) or {"label": key + " (not in targets)", "value": "", "rung": "",
                                         "rung_date": "", "unit": "", "floor": "", "kind": "",
                                         "proposed": False, "as_of": ""}
        groups.append({"key": key, "tickets": mine, "open_count": len(mine), **head})

    return {
        "groups": groups,
        "open_count": len(open_cards),
        "none_count": len(by_key.get(NO_METRIC, [])),
        "updated": data.get("updated", "") or "",
    }
