#!/usr/bin/env python3
"""Write Amir's weekly decisions back into targets, tickets and handovers (one loop, step 10).

    python3 plans/decisions_writeback.py 2026-11-09 --dry-run
    python3 plans/decisions_writeback.py 2026-11-09

Reads plans/decisions-<date>.json: a list of
    {"id": "D1", "question": "...", "answer": "...", "answered_at": "2026-11-09",
     "writes": [{"file": "plans/targets.json", "key_or_section": "metrics.spotify_followers.confirmed", "value": true}]}

Every write names a file under the repo root and what to change in it:
  * targets.json: key_or_section is a dotted path under the file, e.g.
      metrics.spotify_followers.confirmed            -> true / false
      metrics.spotify_followers.rungs.2026-11-30     -> 85
      metrics.email_list.target                      -> 60
    The metric must exist; new rung dates are allowed, new metrics are not.
  * tickets.json (any board): key_or_section is "<ticket id>.<field>" with field one of
      bucket (now|next|parked|routine), status (board statuses), who (amir|claude|auto),
      next_step, due, metric (a targets key or "none"), metric_note.
    The ticket's `updated` is set to the decision's answered_at date.
  * *.md (a handover): the decision is appended as one line under "## Decisions <date>"
    (key_or_section is a short context word, value the text; both optional and
    the question and answer are always written).

Each touched file is backed up once per run as <dir>/.<name>.bak-<date>-decisions
before the first write. --dry-run prints the plan and writes nothing.
The decision web page that produces the decisions file is built elsewhere.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent

BUCKETS = ("now", "next", "parked", "routine")
WHO = ("amir", "claude", "auto")
TICKET_FIELDS = ("bucket", "status", "who", "next_step", "due", "metric", "metric_note")
ISO_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class WritebackError(ValueError):
    """A decisions file or one of its writes is not usable."""


# ---------------------------------------------------------------- helpers

def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise WritebackError("cannot read %s: %s" % (path, e)) from e


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _backup_path(path: Path, day: str) -> Path:
    return path.parent / (".%s.bak-%s-decisions" % (path.name, day))


def _day(decision: dict) -> str:
    d = str(decision.get("answered_at", "") or "")[:10]
    return d if ISO_DAY.match(d) else date.today().isoformat()


def load_decisions(path: Path) -> list:
    data = _read_json(path)
    if not isinstance(data, list):
        raise WritebackError("%s: top level must be a list of decisions" % path)
    for i, d in enumerate(data):
        if not isinstance(d, dict) or not d.get("id"):
            raise WritebackError("%s: decision %d has no id" % (path, i))
        for w in d.get("writes") or []:
            if not isinstance(w, dict) or not w.get("file") or not w.get("key_or_section"):
                raise WritebackError("%s: %s has a write without file or key_or_section" % (path, d["id"]))
    return data


def _resolve(root: Path, rel: str) -> Path:
    p = (root / rel).resolve()
    if root.resolve() not in p.parents:
        raise WritebackError("write outside the root: %s" % rel)
    return p


# ---------------------------------------------------------------- planners
# Each planner returns (description, apply) where apply(data_or_text) -> new data_or_text.

def _plan_targets(data: dict, key: str, value: Any) -> tuple:
    parts = key.split(".")
    if len(parts) < 3 or parts[0] != "metrics":
        raise WritebackError("targets key must be metrics.<metric>.<field>[.<sub>]: %s" % key)
    metric = parts[1]
    if metric not in (data.get("metrics") or {}):
        raise WritebackError("targets: unknown metric %s" % metric)
    field = parts[2]
    if field == "confirmed" and not isinstance(value, bool):
        raise WritebackError("targets: %s.confirmed must be true or false" % metric)
    if field == "rungs":
        if len(parts) != 4 or not ISO_DAY.match(parts[3]):
            raise WritebackError("targets: rungs key must be metrics.<metric>.rungs.YYYY-MM-DD: %s" % key)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise WritebackError("targets: rung value must be a number: %s" % key)
    node = data["metrics"][metric]
    for p in parts[2:-1]:
        node = node.setdefault(p, {})
        if not isinstance(node, dict):
            raise WritebackError("targets: %s is not an object" % key)
    old = node.get(parts[-1], "<unset>")

    def apply(d):
        n = d["metrics"][metric]
        for p in parts[2:-1]:
            n = n.setdefault(p, {})
        n[parts[-1]] = value
        return d
    return ("targets %s: %r -> %r" % (key, old, value), apply)


def _plan_ticket(data: dict, key: str, value: Any, day: str) -> tuple:
    tid, _, field = key.partition(".")
    if field not in TICKET_FIELDS:
        raise WritebackError("tickets: field must be one of %s: %s" % (", ".join(TICKET_FIELDS), key))
    tickets = {t.get("id"): t for t in data.get("tickets", []) if isinstance(t, dict)}
    if tid not in tickets:
        raise WritebackError("tickets: unknown ticket %s" % tid)
    statuses = tuple(data.get("statuses") or ("proposed", "approved", "in-progress", "blocked", "waiting", "done"))
    if field == "bucket" and value not in BUCKETS:
        raise WritebackError("tickets: %s bucket must be one of %s" % (tid, "|".join(BUCKETS)))
    if field == "status" and value not in statuses:
        raise WritebackError("tickets: %s status must be one of %s" % (tid, "|".join(statuses)))
    if field == "who" and value not in WHO:
        raise WritebackError("tickets: %s who must be one of %s" % (tid, "|".join(WHO)))
    if field == "due" and value not in ("", None) and not ISO_DAY.match(str(value)):
        raise WritebackError("tickets: %s due must be YYYY-MM-DD or empty" % tid)
    if field == "metric" and value == "none" and not str(tickets[tid].get("metric_note", "")).strip():
        raise WritebackError("tickets: %s metric none needs a metric_note write too" % tid)
    old = tickets[tid].get(field, "<unset>")

    def apply(d):
        for t in d.get("tickets", []):
            if isinstance(t, dict) and t.get("id") == tid:
                t[field] = value
                t["updated"] = day
        d["updated"] = day
        return d
    return ("ticket %s.%s: %r -> %r (updated %s)" % (tid, field, old, value, day), apply)


def _decision_line(decision: dict, key: str, value: Any) -> str:
    bits = ["- %s" % decision.get("id", "?")]
    if key and key != "-":
        bits.append("[%s]" % key)
    q = str(decision.get("question", "") or "").strip()
    a = str(decision.get("answer", "") or "").strip()
    if q:
        bits.append(q)
    if a:
        bits.append("-> %s" % a)
    if value not in ("", None):
        bits.append("(%s)" % (value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)))
    return " ".join(bits)


def _plan_markdown(text: str, decision: dict, key: str, value: Any, day: str) -> tuple:
    heading = "## Decisions %s" % day
    line = _decision_line(decision, key, value)

    def apply(t: str) -> str:
        if not t.endswith("\n") and t:
            t += "\n"
        if heading in t.splitlines():
            # append at the end of that section (before the next "## " heading, or the end of file)
            lines = t.splitlines()
            start = lines.index(heading)
            end = len(lines)
            for i in range(start + 1, len(lines)):
                if lines[i].startswith("## "):
                    end = i
                    break
            while end > start + 1 and not lines[end - 1].strip():
                end -= 1
            lines.insert(end, line)
            return "\n".join(lines) + "\n"
        return t + "\n%s\n%s\n" % (heading, line)
    return ("handover append under %r: %s" % (heading, line), apply)


# ---------------------------------------------------------------- run

def build_plan(decisions: list, root: Path) -> list:
    """One entry per write: {decision, file, path, kind, desc, apply}. Raises on a bad write."""
    plan = []
    for d in decisions:
        day = _day(d)
        for w in d.get("writes") or []:
            rel = str(w["file"])
            path = _resolve(root, rel)
            key = str(w["key_or_section"])
            value = w.get("value")
            if path.name == "targets.json":
                desc, apply = _plan_targets(_read_json(path), key, value)
                kind = "json"
            elif path.name == "tickets.json":
                desc, apply = _plan_ticket(_read_json(path), key, value, day)
                kind = "json"
            elif path.suffix == ".md":
                desc, apply = _plan_markdown(path.read_text(encoding="utf-8") if path.exists() else "", d, key, value, day)
                kind = "md"
            else:
                raise WritebackError("%s: cannot write to %s (targets.json, tickets.json or .md only)" % (d["id"], rel))
            plan.append({"decision": d["id"], "file": rel, "path": path, "kind": kind, "desc": desc,
                         "apply": apply, "day": day})
    return plan


def run(decisions_file: Path, root: Path = ROOT, dry_run: bool = False, out=None) -> dict:
    out = out or sys.stdout
    decisions = load_decisions(decisions_file)
    plan = build_plan(decisions, root)
    print("%s: %d decision(s), %d write(s)%s" % (decisions_file.name, len(decisions), len(plan),
                                                " [dry run]" if dry_run else ""), file=out)
    for step in plan:
        print("  %s  %s  %s" % (step["decision"], step["file"], step["desc"]), file=out)
    if dry_run:
        return {"decisions": len(decisions), "writes": len(plan), "backups": [], "applied": 0}

    backups = []
    done = 0
    for step in plan:
        path = step["path"]
        bak = _backup_path(path, step["day"])
        if path.exists() and bak not in backups:
            shutil.copy2(path, bak)
            backups.append(bak)
        if step["kind"] == "json":
            _write_json(path, step["apply"](_read_json(path)))   # re-read: earlier steps may have changed it
        else:
            text = path.read_text(encoding="utf-8") if path.exists() else ""
            path.write_text(step["apply"](text), encoding="utf-8")
        done += 1
    for b in backups:
        print("  backup %s" % b.relative_to(root), file=out)
    print("applied %d write(s)" % done, file=out)
    return {"decisions": len(decisions), "writes": len(plan), "backups": backups, "applied": done}


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(description="apply plans/decisions-<date>.json to targets, tickets and handovers")
    ap.add_argument("date", help="YYYY-MM-DD, picks plans/decisions-<date>.json (or a path to a decisions file)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    ap.add_argument("--root", default=str(ROOT), help="repo root the write paths are relative to (tests)")
    args = ap.parse_args(argv)
    root = Path(args.root)
    f = Path(args.date)
    if not f.exists():
        f = root / "plans" / ("decisions-%s.json" % args.date)
    try:
        run(f, root=root, dry_run=args.dry_run)
    except WritebackError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
