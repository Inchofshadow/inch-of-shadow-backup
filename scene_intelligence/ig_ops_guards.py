"""Shared hard gates for every IG entrypoint (2.0 law, Amir-approved 2026-08-30).

Closes review finding L1 (docs/reports/ig-automation-review-2026-08-25.md):
`autonomy_state.json` pauses and `detection_events.json` cooldowns were read
by no script — a CLOSED sign taped to the door while the machines kept their
own schedule. Every IG entrypoint now calls, in order, BEFORE anything else:

    require_not_paused()      # Amir's pause is absolute; resume is his alone
    require_no_cooldown()     # detection events impose a rest window
    (then the daily ledger claim, which enforces budgets + daytime hours)

Law summary (TICKETS.md T-003/T-004; findings doc addendum):
- pauses hard-block, never advisory
- a detection event blocks all IG API work for its cooldown window (72h
  default; per-type override via config DETECTION_COOLDOWN_HOURS)
- API work runs in daytime only (09:00-21:00 local/Berlin) — 8 of the last
  23 ledger runs had fired 23:00-06:00, a bot-timing signal, that stops
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

SI_DIR = Path(__file__).parent
AUTONOMY_PATH = SI_DIR / "autonomy_state.json"
DETECTION_PATH = SI_DIR / "detection_events.json"

EXIT_PAUSED = 6
EXIT_NIGHT = 7
EXIT_COOLDOWN = 8

DAY_START_HOUR = 9   # inclusive
DAY_END_HOUR = 21    # exclusive
DEFAULT_COOLDOWN_HOURS = 72


class OpsGate(SystemExit):
    """Hard-gate refusal. Prints its reason (SystemExit(int) is silent)."""

    def __init__(self, message: str, code: int):
        self.message = message
        print(message)
        super().__init__(code)


def _config():
    """Best-effort import of ig_engagement_config for law constants."""
    try:
        from scene_intelligence import ig_engagement_config as cfg
    except ImportError:
        try:
            import ig_engagement_config as cfg  # script-dir invocation
        except ImportError:
            return None
    return cfg


def load_autonomy_state(path: Path = AUTONOMY_PATH) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        # Fail CLOSED: an unreadable pause file cannot prove "not paused".
        raise OpsGate(
            f"[PAUSE GATE] {path.name} exists but is unreadable — refusing to "
            f"run (fail closed). Restore it from git/.bak, then retry.",
            EXIT_PAUSED,
        )


def get_pause(platform: str = "ig", path: Path = AUTONOMY_PATH):
    """Return the platform's pause dict, or None. Understands the legacy
    top-level `paused` flag (pre-2026-07-24) as a pause on EVERY platform —
    the 08-29 incident came from a caller reading only the dead legacy key."""
    state = load_autonomy_state(path)
    pause = (state.get("pauses") or {}).get(platform)
    if pause:
        return pause
    if state.get("paused"):
        return {"reason": state.get("paused_reason") or "legacy global pause",
                "at": state.get("paused_at"), "paused_by": "legacy"}
    return None


def pause_scope(pause) -> str:
    """A pause dict may carry scope: "sessions" (engagement sessions only —
    API maintenance continues) or "all" (everything stops; the default).
    Added 2026-09-01: Amir paused SESSIONS for the attribution review and
    the dispatcher wrongly stopped all maintenance with them."""
    if not pause:
        return "none"
    return str(pause.get("scope") or "all").lower()


def blocks_api_jobs(pause) -> bool:
    return pause_scope(pause) == "all"


def blocks_sessions(pause) -> bool:
    return pause_scope(pause) in ("all", "sessions")
    return None


def require_not_paused(platform: str = "ig", path: Path = AUTONOMY_PATH) -> None:
    pause = get_pause(platform, path)
    if pause:
        raise OpsGate(
            f"[PAUSE GATE] {platform.upper()} automation is PAUSED "
            f"(set {pause.get('at', '?')} by {pause.get('paused_by', '?')}): "
            f"{pause.get('reason', 'no reason recorded')}\n"
            f"Nothing runs until Amir clears it: "
            f"python3 scene_intelligence/close_loops.py --resume --platform {platform}",
            EXIT_PAUSED,
        )


def record_detection(platform: str, event_type: str, detail: str, *,
                     path: Path = DETECTION_PATH, today: str | None = None,
                     count: int = 1) -> dict:
    """Append a detection event so the cooldown gate blocks the next run.

    2026-09-11: until now a 429 inside the audit/builder just exited; nothing
    was recorded, so the dispatcher retried the next morning and restarted
    Instagram's clock (that is what happened on 09-05). Scripts call this
    BEFORE raising on a 429/soft-throttle.
    """
    from datetime import date as _date
    try:
        data = json.load(open(path, encoding="utf-8")) if path.exists() else {"events": []}
    except (ValueError, OSError):
        data = {"events": []}
    if isinstance(data, list):
        data = {"events": data}
    ev = {
        "date": today or _date.today().isoformat(),
        "platform": platform, "type": event_type, "count": count,
        "detail": detail,
        "recorded_by": "auto",
        "action_taken": (f"recorded automatically by the script that hit it; "
                         f"cooldown per DETECTION_COOLDOWN_HOURS[{event_type!r}] "
                         f"blocks the next API run"),
    }
    data.setdefault("events", []).append(ev)
    try:
        from scene_intelligence.json_io import atomic_write_json
    except ImportError:
        from json_io import atomic_write_json
    atomic_write_json(path, data)
    return ev


def _cooldown_hours_for(event_type: str) -> float:
    cfg = _config()
    table = getattr(cfg, "DETECTION_COOLDOWN_HOURS", None) if cfg else None
    if isinstance(table, dict) and event_type in table:
        return float(table[event_type])
    if isinstance(table, dict) and "default" in table:
        return float(table["default"])
    return float(DEFAULT_COOLDOWN_HOURS)


def _event_cooldown_hours(ev: dict, platform: str) -> float:
    """Hours this event blocks work for.

    SC LAW (Amir, 2026-09-09): a SoundCloud challenge he clears himself in
    seconds is not a platform block, and no multi-day freeze is imposed on his
    behalf. An SC event therefore blocks NOTHING unless it carries an explicit
    `cooldown_hours` that Amir approved (`cooldown_approved_by`). The event is
    still recorded, and the session still stops in the moment it appears.
    The 09-08 slider — solved, test action succeeded, session resumed and
    landed 7 more follows — auto-froze four days under the old default.

    IG is unchanged: its table-driven cooldowns still apply automatically.
    """
    if platform == "sc":
        hours = ev.get("cooldown_hours")
        if hours is None or not str(ev.get("cooldown_approved_by", "")).strip():
            return 0.0
        try:
            return float(hours)
        except (TypeError, ValueError):
            return 0.0
    return _cooldown_hours_for(str(ev.get("type", "")))


def _api_surface_types() -> frozenset:
    cfg = _config()
    types = getattr(cfg, "API_SURFACE_DETECTION_TYPES", None) if cfg else None
    return frozenset(types) if types else frozenset()


def active_detection_cooldown(now: datetime | None = None,
                              platform: str = "ig",
                              path: Path = DETECTION_PATH,
                              kind: str = "api"):
    """Return (event, until_dt) when the newest matching detection event is
    still inside its cooldown window, else None. Events carry only a date in
    the durable record, so the window is counted from that date's END of day
    (conservative: a same-day event always blocks the whole next window).

    kind="api": every event counts. kind="session": events whose type is in
    config API_SURFACE_DETECTION_TYPES are ignored -- a throttled read
    endpoint says nothing about clicking in the real browser (2026-09-06)."""
    now = now or datetime.now()
    skip = _api_surface_types() if kind == "session" else frozenset()
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            events = json.load(f).get("events", [])
    except (ValueError, OSError):
        raise OpsGate(
            f"[COOLDOWN GATE] {path.name} exists but is unreadable — refusing "
            f"to run (fail closed). Restore it, then retry.",
            EXIT_COOLDOWN,
        )
    aliases = {"ig": ("ig", "instagram"), "sc": ("sc", "soundcloud")}
    wanted = aliases.get(platform, (platform,))
    best = None
    for ev in events:
        ev_platform = str(ev.get("platform", "")).lower()
        if not any(a == ev_platform or a in ev_platform for a in wanted):
            continue
        if str(ev.get("type", "")) in skip:
            continue
        try:
            day_end = datetime.fromisoformat(str(ev.get("date"))) + timedelta(days=1)
        except ValueError:
            continue
        hours = _event_cooldown_hours(ev, platform)
        if hours <= 0:
            continue          # recorded, but imposes no freeze (SC law)
        until = day_end + timedelta(hours=hours)
        if until > now and (best is None or until > best[1]):
            best = (ev, until)
    return best


def require_no_cooldown(now: datetime | None = None, platform: str = "ig",
                        path: Path = DETECTION_PATH, kind: str = "api") -> None:
    hit = active_detection_cooldown(now, platform, path, kind=kind)
    if hit:
        ev, until = hit
        # Name the platform being blocked: this module gates SC too since
        # SC-01, and an SC block that read "No IG API work" was misread as a
        # malfunction (2026-09-09).
        plat = platform.upper()
        what = f"{plat} API work" if kind == "api" else f"{plat} sessions"
        raise OpsGate(
            f"[COOLDOWN GATE] Detection event on {ev.get('date')} "
            f"({ev.get('type', '?')}) imposes a rest window until "
            f"{until:%Y-%m-%d %H:%M}. No {what} before then.",
            EXIT_COOLDOWN,
        )


def is_daytime(now: datetime | None = None) -> bool:
    now = now or datetime.now()
    return DAY_START_HOUR <= now.hour < DAY_END_HOUR


def require_daytime(now: datetime | None = None, *, override: bool = False) -> None:
    """Daytime-only law for API work. `override` is the deliberate escape
    hatch (wired to --override-ledger — one escape flag for the whole law)."""
    if override or is_daytime(now):
        return
    raise OpsGate(
        f"[HOURS GATE] IG API work runs {DAY_START_HOUR:02d}:00-"
        f"{DAY_END_HOUR:02d}:00 local only (night runs are a bot-timing "
        f"signal). It is {datetime.now() if now is None else now:%H:%M}. "
        f"Re-run in the daytime window, or --override-ledger if Amir "
        f"deliberately wants it now.",
        EXIT_NIGHT,
    )


def standard_gates(platform: str = "ig", *, kind: str = "api") -> None:
    """The gate pair every IG entrypoint runs first (ledger handles hours).

    kind="api" (scripts: audit, builder, re-enrichment) or kind="session"
    (the engine's --live path). A pause with scope "sessions" blocks only
    session-kind callers; scope "all" (the default) blocks everyone.
    2026-09-02: under Amir's sessions-scoped pause the dispatcher correctly
    launched the audit and the audit refused itself here — maintenance was
    dead under exactly the pause meant to let it run.
    """
    pause = get_pause(platform)
    if pause:
        blocked = blocks_sessions(pause) if kind == "session" else blocks_api_jobs(pause)
        if blocked:
            require_not_paused(platform)
    require_no_cooldown(platform=platform, kind=kind)
