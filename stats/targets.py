"""Score board targets: file loading and ladder maths (pure functions)."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Optional, Tuple

TARGETS_PATH = Path(__file__).parent.parent / "plans" / "targets.json"
KINDS = {"ladder", "floor", "collecting"}


def load_targets(path: Path = TARGETS_PATH) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "period" not in data or "metrics" not in data:
        raise ValueError("targets file needs 'period' and 'metrics'")
    for key, m in data["metrics"].items():
        if m.get("kind") not in KINDS:
            raise ValueError("metric %s: kind must be one of %s" % (key, sorted(KINDS)))
        if not m.get("label"):
            raise ValueError("metric %s: missing label" % key)
        need = {"ladder": ("baseline", "rungs", "target"), "floor": ("floor", "baseline")}.get(m["kind"], ())
        for field in need:
            if field not in m:
                raise ValueError("metric %s: %s metric needs '%s'" % (key, m["kind"], field))
        if m.get("proposed_by") and not isinstance(m.get("confirmed"), bool):
            raise ValueError("metric %s: a proposed metric needs 'confirmed': true or false" % key)
    return data


def _d(s: str) -> date:
    return date.fromisoformat(s)


def ladder_value(metric: dict, period: dict, on: date) -> Optional[float]:
    if metric.get("kind") != "ladder":
        return None
    base = (metric.get("baseline") or {}).get("value")
    if base is None:
        return None
    anchor = _d(period["start"])
    base_day = (metric.get("baseline") or {}).get("date")
    if base_day:
        anchor = max(anchor, _d(base_day))   # the ladder starts where the baseline was read
    points = [(anchor, float(base))]
    points += sorted((_d(k), float(v)) for k, v in (metric.get("rungs") or {}).items())
    if on <= points[0][0]:
        return float(base)
    if on >= points[-1][0]:
        return points[-1][1]
    for (d0, v0), (d1, v1) in zip(points, points[1:]):
        if d0 <= on <= d1:
            span = (d1 - d0).days
            if span <= 0:
                return v1
            return v0 + (v1 - v0) * (on - d0).days / span
    return points[-1][1]


def light_for_ladder(value: Optional[float], ladder_today: Optional[float]) -> Tuple[str, str]:
    if value is None or ladder_today is None:
        return ("none", "collecting")
    delta = int(round(value - ladder_today))
    text = "%+d %s" % (delta, "past rung" if delta >= 0 else "to rung")
    if ladder_today <= 0:
        return ("green", text)
    ratio = value / ladder_today
    light = "green" if ratio >= 0.95 else "amber" if ratio >= 0.85 else "red"
    return (light, text)


def light_for_floor(value: Optional[float], floor: float) -> Tuple[str, str]:
    if value is None:
        return ("none", "collecting")
    delta = int(round(value - floor))
    text = "%+d vs floor" % delta
    light = "green" if value >= floor else "amber" if value >= floor - 5 else "red"
    return (light, text)


def progress_pct(baseline: float, target: float, value: float) -> Optional[int]:
    if target == baseline:
        return None
    pct = (value - baseline) / (target - baseline) * 100
    return int(max(0, min(100, round(pct))))


def current_rung(metric: dict, on: date) -> Optional[Tuple[str, float]]:
    for k, v in sorted((metric.get("rungs") or {}).items()):
        if _d(k) >= on:
            return (k, v)
    return None
