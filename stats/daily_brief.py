#!/usr/bin/env python3
"""System 72: one daily brief at 20:00 (spec: plans/strategy/drafts/daily-brief-spec.draft.md, D13 2026-11-05).

Read-only over the files the day's automation already writes. Default prints only; --write also saves
the brief, the red-repeat state and (when a red line repeats) a proposed ticket line in the System handover.

  python3 stats/daily_brief.py              # today, print only
  python3 stats/daily_brief.py 2026-11-04   # another day
  python3 stats/daily_brief.py --write      # also docs/reports/daily-brief-DATE.md + state + handover

Shape (max about 12 lines; a block with nothing to say is left out):
  Inch of Shadow · Thu 11-05
  🔴 Problems            only when there is one
     <line> [→ ticket]   "→ ticket" when the same line was red yesterday too (red repeats rule)
  🔥 Now                 bucket == now on both boards, grouped per area, areas with nothing left out
  🎯 Nov 30   IG 971 → 996 · SC 473 → 510 · Spotify listeners 115 (rung 90 ✅)
  🤖 Ran today   IG ✅ 10/10 · SC ✅ 10/10 · sweep ✅ · dispatch ✅ · stats ✅ · spend ✅
  🙋 Waiting on you today: 4 · HTN cover · ...
  💶 Spend ⚠️ ...        only when stats/spend.py warns

Sources: docs/reports/loop-close-{ig,sc}-DATE.md, scene_intelligence/sc_session_report_DATE.md,
docs/reports/sc-weekly-DATE.md, docs/reports/dispatch-log.md, stats_snapshots/snapshot_*.json,
stats_snapshots/spotify_s4a.json, stats_snapshots/spend_latest.json (fallback) or stats/spend.py,
stats/ig_token_state.json, plans/targets.json (never written), both ticket boards (never written).
The 🎬 Socials digest (stats/socials_digest.py) stays untouched; its pure helpers are imported.
Nothing here touches engagement code or state.
"""
from __future__ import annotations

import glob
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:  # run as python3 stats/daily_brief.py from Inchofshadowcode
    sys.path.insert(0, str(ROOT))
REPORTS = ROOT / "docs" / "reports"
SI = ROOT / "scene_intelligence"
SNAPS = ROOT / "stats_snapshots"
TARGETS = ROOT / "plans" / "targets.json"
BOARDS = (ROOT / "plans" / "tickets.json", ROOT / "plans" / "control-panel" / "tickets.json")
STATE_FILE = ROOT / "stats_snapshots" / "daily_brief_state.json"
HANDOVER = ROOT / "plans" / "handovers" / "system" / "system.md"
S4A_FILE = ROOT / "stats_snapshots" / "spotify_s4a.json"
SPEND_LATEST = ROOT / "stats_snapshots" / "spend_latest.json"
IG_TOKEN_STATE = ROOT / "stats" / "ig_token_state.json"
DISPATCH_LOG = ROOT / "docs" / "reports" / "dispatch-log.md"

from stats import registry  # noqa: E402  (metric labels, cadences and the freshness rule, M11)
from stats.socials_digest import IG_SESSION_DAYS, _counts, _mark, _read, _score  # noqa: E402

AREA_ORDER = ("Release", "Socials", "Booking", "Income", "Studio", "System")
AREA_EMOJI = {"Release": "🎵", "Socials": "🎬", "Booking": "🎧", "Income": "💶", "Studio": "🎸", "System": "⚙️"}
WHO_MARK = {"amir": "🙋", "claude": "🎃", "auto": "🤖"}
OPEN_STATUSES_EXCLUDED = ("done", "closed")
BRIEF_HOUR = 20   # the brief runs at 20:00; freshness is judged at that hour of the brief's day
DETECTION_WORDS = ("CAPTCHA", "challenge", "detection event written", "CHURN ALERT", "takeover")
TOKEN_WARN_DAYS = 7
STATE_KEEP_DAYS = 7
HANDOVER_SECTION = "## Proposed from the brief"


# ---------------------------------------------------------------- helpers

def _clean(s: str) -> str:
    """No em-dashes in anything we print or write; collapse the log's ' \u2014 ' separators."""
    return re.sub(r"\s*[\u2014\u2013]\s*", " · ", s).strip()


def _load_json(p: Path) -> Optional[dict]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _tickets() -> list:
    out = []
    for board in BOARDS:
        data = _load_json(board) or {}
        for t in data.get("tickets") or []:
            if t.get("status") not in OPEN_STATUSES_EXCLUDED:
                out.append(t)
    return out


def _ticket_name(t: dict) -> str:
    area = t.get("area") or "System"
    return f"{AREA_EMOJI.get(area, '')} {area} {t.get('area_no')}".strip()


def _label(t: dict) -> str:
    return t.get("label") or (t.get("title") or "")[:30]


def _flagged(text: str) -> list:
    """Detection words that appear without a 'no' earlier in the same sentence."""
    hits = []
    for line in text.splitlines():
        for word in DETECTION_WORDS:
            for m in re.finditer(re.escape(word), line, re.I):
                sentence = re.split(r"[.;:]\s", line[:m.start()])[-1]
                if not re.search(r"\bno\b", sentence, re.I) and word not in hits:
                    hits.append(word)
    return hits


def _dispatch_lines(d: date) -> list:
    text = _read(DISPATCH_LOG) or ""
    return [ln for ln in text.splitlines() if ln.startswith(f"- {d.isoformat()}T")]


# ---------------------------------------------------------------- sessions

def ig_status(d: date) -> dict:
    """{'mark': '✅ 10/10' | '⏸' | '❌', 'problems': [...]}"""
    text = _read(REPORTS / f"loop-close-ig-{d.isoformat()}.md")
    if text is None:
        if d.weekday() in IG_SESSION_DAYS:
            return {"mark": "❌", "problems": ["IG session day, nothing logged · check the 15:00 session"]}
        return {"mark": "⏸", "problems": []}
    s = _score(text)
    problems = []
    if s is None:
        problems.append(f"IG session has no score · docs/reports/loop-close-ig-{d.isoformat()}.md")
    elif s < 8:
        problems.append(f"IG session scored {s}/10 · docs/reports/loop-close-ig-{d.isoformat()}.md")
    c = _counts(text, "Actions:")
    if c.get("session_halt"):
        problems.append(f"IG session halted (popup or safety stop) · docs/reports/loop-close-ig-{d.isoformat()}.md")
    for word in _flagged(text):
        problems.append(f"IG {word} · docs/reports/loop-close-ig-{d.isoformat()}.md")
    mark = f"{_mark(s)} {s}/10" if s is not None else "❔"
    return {"mark": mark, "problems": problems}


def sc_status(d: date) -> dict:
    """{'mark': ..., 'sweep': '✅' | '⚠️' | None, 'problems': [...]}"""
    text = _read(REPORTS / f"loop-close-sc-{d.isoformat()}.md")
    report_name = f"sc_session_report_{d.strftime('%Y%m%d')}.md"
    report = _read(SI / report_name) or ""
    problems = []
    if text is None:
        mark = "❌"
        problems.append(f"SC: no session logged · scene_intelligence/{report_name}")
    else:
        s = _score(text)
        if s is None:
            problems.append(f"SC session has no score · docs/reports/loop-close-sc-{d.isoformat()}.md")
        elif s < 8:
            problems.append(f"SC session scored {s}/10 · docs/reports/loop-close-sc-{d.isoformat()}.md")
        mark = f"{_mark(s)} {s}/10" if s is not None else "❔"
    for word in _flagged(report):
        problems.append(f"SC {word} · scene_intelligence/{report_name}")
    sweep = None
    m = re.search(r"^## 16:15 sweep run[^\n]*", report, re.M)
    if m:
        body = report[m.end():]
        bad = re.search(r"STOP|SESSION_INCOMPLETE|not connected", body[:600], re.I)
        sweep = "⚠️" if bad else "✅"
        if bad:
            problems.append(f"SC sweep stopped early · scene_intelligence/{report_name}")
    health = _read(REPORTS / f"sc-weekly-{d.strftime('%Y%m%d')}.md") or ""
    m = re.search(r"## Drift detected[^\n]*\n(.*?)(\n## |\Z)", health, re.S)
    if m and m.group(1).strip() and "_None_" not in m.group(1):
        problems.append(f"SC tracker drift · docs/reports/sc-weekly-{d.strftime('%Y%m%d')}.md")
    return {"mark": mark, "sweep": sweep, "problems": problems}


# ---------------------------------------------------------------- problems

def dispatch_problems(d: date) -> list:
    out = []
    for ln in _dispatch_lines(d):
        m = re.search(r"\*\*notify-amir\*\*\s*[\u2014-]\s*(.+)", ln)
        if m:
            out.append(_clean(m.group(1)))
    # a red test suite counts when the watchdog said so on two of the last three nights
    text = _read(DISPATCH_LOG) or ""
    window = {(d - timedelta(days=n)).isoformat() for n in range(3)}
    reds = {}
    for ln in text.splitlines():
        if "**watchdog**" in ln and "TEST SUITE RED" in ln and ln[2:12] in window:
            reds[ln[2:12]] = _clean(ln.split("TEST SUITE RED", 1)[1].strip(": "))
    if len(reds) >= 2:
        last = sorted(reds)[-1]
        out.append(f"Test suite red {len(reds)} nights ({last[5:]}: {reds[last]}) · "
                   "python3 -m pytest -q tests/ -p no:cacheprovider")
    return out


def token_problems(d: date) -> list:
    out = []
    state = _load_json(IG_TOKEN_STATE) or {}
    try:
        exp = date.fromisoformat(str(state.get("expires"))[:10])
    except ValueError:
        return out
    left = (exp - d).days
    if left < 0:
        out.append(f"IG Graph token expired {exp.isoformat()} · renew, then --mark-issued")
    elif left <= TOKEN_WARN_DAYS:
        out.append(f"IG Graph token expires in {left} days ({exp.isoformat()}) · refresh runs at day 50")
    return out


def ticket_problems() -> list:
    """Open tickets whose blocked_on says something expired (a login, a token)."""
    out = []
    for t in _tickets():
        blocked = str(t.get("blocked_on") or "")
        if re.search(r"\bexpired\b", blocked, re.I):
            first = re.split(r"\.\s|\s\(", blocked, 1)[0].strip()
            out.append(f"{_ticket_name(t)} · {_label(t)} · {_clean(first)}")
    return out


def problems(d: date, ig: dict, sc: dict) -> list:
    reds = ig["problems"] + sc["problems"] + ticket_problems() + token_problems(d) + dispatch_problems(d)
    seen, out = set(), []
    for r in reds:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


# ---------------------------------------------------------------- red repeats

def _red_key(line: str) -> str:
    """Same problem on two days even when a number inside it moved (1609KB vs 1637KB)."""
    return re.sub(r"\d+", "#", line.replace(" → ticket", "")).strip()


def load_state() -> dict:
    state = _load_json(STATE_FILE) or {}
    state.setdefault("reds", {})
    state.setdefault("proposed", {})
    return state


def apply_red_repeats(reds: list, state: dict, d: date) -> tuple:
    """Mark lines that were red yesterday too; return (marked lines, new proposals)."""
    yesterday = {_red_key(r) for r in state["reds"].get((d - timedelta(days=1)).isoformat(), [])}
    marked, proposals = [], []
    for r in reds:
        key = _red_key(r)
        if key in yesterday:
            marked.append(r + " → ticket")
            if key not in state["proposed"]:
                proposals.append((key, r))
        else:
            marked.append(r)
    return marked, proposals


def save_state(state: dict, reds: list, d: date, proposals: list) -> None:
    state["reds"][d.isoformat()] = reds
    cutoff = (d - timedelta(days=STATE_KEEP_DAYS)).isoformat()
    state["reds"] = {k: v for k, v in state["reds"].items() if k >= cutoff}
    for key, _ in proposals:
        state["proposed"][key] = d.isoformat()
    state["updated"] = d.isoformat()
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_proposals(proposals: list, d: date) -> int:
    """Append one proposed ticket line per repeated red under 'Proposed from the brief' in the System handover."""
    if not proposals:
        return 0
    text = _read(HANDOVER) or ""
    if HANDOVER_SECTION not in text:
        text = text.rstrip("\n") + f"\n\n{HANDOVER_SECTION}\n" \
            "Written by stats/daily_brief.py when the same 🔴 line shows two days running. " \
            "Each line is a proposal for the System chat to turn into a ticket (or to dismiss).\n"
    lines = [f"- {d.isoformat()} · proposed ⚙️ System ticket · {_clean(line)} · "
             f"red on {(d - timedelta(days=1)).strftime('%m-%d')} and {d.strftime('%m-%d')}"
             for _, line in proposals]
    # insert at the end of that section (before the next '## ' heading), so later sections stay intact
    start = text.index(HANDOVER_SECTION)
    nxt = re.search(r"^## ", text[start + len(HANDOVER_SECTION):], re.M)
    cut = start + len(HANDOVER_SECTION) + nxt.start() if nxt else len(text)
    head, tail = text[:cut].rstrip("\n"), text[cut:]
    text = head + "\n" + "\n".join(lines) + "\n" + ("\n" + tail if tail.strip() else "")
    HANDOVER.write_text(text.rstrip("\n") + "\n", encoding="utf-8")
    return len(lines)


# ---------------------------------------------------------------- blocks

def now_block() -> list:
    """One line per area with 🔥 now tickets; the first item carries the area name."""
    per_area = {}
    for t in _tickets():
        if t.get("bucket") == "now":
            per_area.setdefault(t.get("area") or "System", []).append(t)
    lines = []
    for area in AREA_ORDER:
        items = sorted(per_area.get(area, []), key=lambda t: (t.get("area_no") or 0))
        if not items:
            continue
        parts = []
        for n, t in enumerate(items):
            head = _ticket_name(t) if n == 0 else str(t.get("area_no"))
            tail = (WHO_MARK.get(t.get("who"), "") + ("🌐" if t.get("chrome") else "")).strip()
            parts.append(f"{head} · {_label(t)} {tail}".rstrip())
        lines.append(" · ".join(parts))
    return lines


def _snapshot_value(platform: str, field: str, upto: date):
    for f in sorted(glob.glob(str(SNAPS / "snapshot_*.json")), reverse=True):
        day = Path(f).stem[len("snapshot_"):][:10]
        if day > upto.isoformat():
            continue
        data = _load_json(Path(f)) or {}
        p = (data.get("platforms") or {}).get(platform) or {}
        if registry.is_skipped(p):          # not collected, never a 0: the older reading stands
            continue
        if p.get(field) is not None:
            return p[field], (p.get("as_of") or data.get("timestamp") or day)
    return None, None


def _s4a_value(field: str, upto: date):
    weeks = (_load_json(S4A_FILE) or {}).get("weeks") or {}
    for key in sorted(weeks, reverse=True):
        if key > upto.isoformat():
            continue
        v = weeks[key].get(field)
        if v is not None:
            return v, key
    return None, None


def resolve_source(source: str, d: date):
    """'snapshot:instagram.followers' / 's4a:weeks.monthly_active' / alternatives joined by '|'."""
    for src in str(source).split("|"):
        src = src.strip()
        if src.startswith("snapshot:") and "." in src:
            platform, field = src[len("snapshot:"):].split(".", 1)
            v, day = _snapshot_value(platform, field, d)
        elif src.startswith("s4a:weeks."):
            v, day = _s4a_value(src[len("s4a:weeks."):], d)
        else:
            continue
        if v is not None:
            return v, day, src.split(":", 1)[0]
    return None, None, None


def targets_line(d: date, now: Optional[datetime] = None) -> Optional[str]:
    """The 🎯 line over the registry's ladder rows; a reading older than its cadence window
    (the one freshness rule) says so: 'IG 971 → 996 (stale, read 11-02)'."""
    now = now or datetime.combine(d, datetime.min.time().replace(hour=BRIEF_HOUR))
    metrics = registry.from_targets(_load_json(TARGETS) or {})
    parts, rung_label = [], None
    for key, m in metrics.items():
        if m.get("kind") != "ladder":
            continue
        rungs = sorted((m.get("rungs") or {}).items())
        nxt = next(((k, v) for k, v in rungs if k >= d.isoformat()), rungs[-1] if rungs else None)
        if nxt is None:
            continue
        value, as_of, kind = resolve_source(m.get("source", ""), d)
        if value is None:
            continue
        rung_label = rung_label or datetime.fromisoformat(nxt[0]).strftime("%b %-d")
        short = m["short"]
        fresh = registry.freshness(as_of, m["cadence"], now)
        stale = f" (stale, read {str(as_of)[5:10]})" if fresh["stale"] else ""
        if value >= nxt[1]:
            parts.append(f"{short} {value} (rung {nxt[1]} ✅){stale}")
        else:
            parts.append(f"{short} {value} → {nxt[1]}{stale}")
    if not parts:
        return None
    return f"🎯 {rung_label}   " + " · ".join(parts)


def ran_line(d: date, ig: dict, sc: dict) -> str:
    parts = [f"IG {ig['mark']}", f"SC {sc['mark']}"]
    if sc.get("sweep"):
        parts.append(f"sweep {sc['sweep']}")
    if _dispatch_lines(d):
        parts.append("dispatch ✅")
    if glob.glob(str(SNAPS / f"snapshot_{d.isoformat()}*.json")):
        parts.append("stats ✅")
    spend = _load_json(SPEND_LATEST) or {}
    if str(spend.get("made", ""))[:10] == d.isoformat():
        parts.append("spend ✅")
    return "🤖 Ran today   " + " · ".join(parts)


def waiting_line() -> str:
    mine = [t for t in _tickets() if t.get("who") == "amir" and t.get("bucket") == "now"]
    mine.sort(key=lambda t: (AREA_ORDER.index(t.get("area")) if t.get("area") in AREA_ORDER else 9,
                             t.get("area_no") or 0))
    line = f"🙋 Waiting on you today: {len(mine)}"
    if mine:
        line += " · " + " · ".join(_label(t) for t in mine)
    return line


def spend_warnings(d: date) -> list:
    """Live from stats/spend.py when importable, else the last written spend_latest.json."""
    try:
        from stats import spend
        return list(spend.build(datetime.combine(d, datetime.now().time()))["warnings"])
    except Exception:  # noqa: BLE001 - a broken spend page must not kill the brief
        return list((_load_json(SPEND_LATEST) or {}).get("warnings") or [])


def spend_line(d: date) -> Optional[str]:
    warns = [_clean(w) for w in spend_warnings(d)]
    if not warns:
        return None
    return "💶 Spend ⚠️ " + " · ".join(warns) + " · python3 stats/spend.py"


# ---------------------------------------------------------------- build

def build(d: date, write: bool = False) -> str:
    ig, sc = ig_status(d), sc_status(d)
    reds = problems(d, ig, sc)
    state = load_state()
    marked, proposals = apply_red_repeats(reds, state, d)

    blocks = [f"Inch of Shadow · {d.strftime('%a %m-%d')}"]
    if marked:
        blocks.append("🔴 Problems\n" + "\n".join(f"   {r}" for r in marked))
    now = now_block()
    if now:
        blocks.append("🔥 Now\n" + "\n".join(f"   {ln}" for ln in now))
    t = targets_line(d)
    if t:
        blocks.append(t)
    blocks.append(ran_line(d, ig, sc))
    blocks.append(waiting_line())
    s = spend_line(d)
    if s:
        blocks.append(s)
    text = "\n\n".join(blocks)

    if write:
        REPORTS.mkdir(parents=True, exist_ok=True)
        (REPORTS / f"daily-brief-{d.isoformat()}.md").write_text(text + "\n", encoding="utf-8")
        save_state(state, reds, d, proposals)
        write_proposals(proposals, d)
    return text


def main(argv: list) -> int:
    args = [a for a in argv if not a.startswith("--")]
    d = date.fromisoformat(args[0]) if args else date.today()
    print(build(d, write="--write" in argv))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
