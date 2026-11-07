#!/usr/bin/env python3
"""🎬 Socials daily digest (format A, Amir 2026-11-05).

Read-only: builds one short text from the day's automation reports and the
goals board. Nothing is written except the digest file itself.

  python3 stats/socials_digest.py            # today
  python3 stats/socials_digest.py 2026-11-04 # another day
  python3 stats/socials_digest.py --write    # also save docs/reports/socials-digest-DATE.md

Layout:
  🎬 Socials · Thu 11-05
  Instagram   ✅ 10/10 · 16 follows · 7 unfollows · 22 likes
  SoundCloud  ✅ 10/10 · 20 follows · 30 likes · sweep ✅
  (YouTube / Bandcamp lines only when something ran there that day)
  🎯 Nov 30: IG 966 → 996 (-30) · SC 470 → 510 (-40) · SC ratio 1.03 (floor 1.0)
  ⚠️ Needs you: ...   (or ✅ Nothing needs you)
"""
from __future__ import annotations

import glob
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:  # run as python3 stats/socials_digest.py from Inchofshadowcode (stats.registry import)
    sys.path.insert(0, str(ROOT))
REPORTS = ROOT / "docs" / "reports"
SI = ROOT / "scene_intelligence"
SNAPS = ROOT / "stats_snapshots"
TARGETS = ROOT / "plans" / "targets.json"
YT_DIR = ROOT.parent / "youtube"
BC_DIR = ROOT / "data" / "bandcamp"

IG_SESSION_DAYS = {0, 2, 4, 5}  # Mon Wed Fri Sat


def _read(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return None


def _counts(text: str, key: str) -> dict[str, int]:
    """Parse 'key: ig_follow: 16, ig_like: 22' style lines."""
    m = re.search(rf"{key}\s*(.+)", text)
    if not m:
        return {}
    return {k: int(v) for k, v in re.findall(r"(\w+):\s*(\d+)", m.group(1))}


def _score(text: str) -> int | None:
    m = re.search(r"\*\*Score:\s*(\d+)/10", text)
    return int(m.group(1)) if m else None


def _mark(score: int | None) -> str:
    if score is None:
        return "❔"
    return "✅" if score >= 8 else "⚠️"


def ig_line(d: date, needs: list[str]) -> str:
    text = _read(REPORTS / f"loop-close-ig-{d.isoformat()}.md")
    if text is None:
        if d.weekday() in IG_SESSION_DAYS:
            needs.append("IG session day but no session was logged")
            return "Instagram   ❌ no session logged"
        return "Instagram   ⏸ rest day"
    s = _score(text)
    c = _counts(text, "Actions:")
    parts = [f"{_mark(s)} {s}/10" if s is not None else "❔ no score"]
    parts.append(f"{c.get('ig_follow', 0)} follows")
    parts.append(f"{c.get('ig_unfollow', 0)} unfollows")
    parts.append(f"{c.get('ig_like', 0)} likes")
    if s is not None and s < 8:
        needs.append(f"IG session scored {s}/10")
    if "POOL LOW" in text:
        m = re.search(r"POOL LOW:\s*(\d+)", text)
        needs.append(f"IG follow pool low ({m.group(1)} vetted)" if m else "IG follow pool low")
    return "Instagram   " + " · ".join(parts)


def sc_line(d: date, needs: list[str]) -> str:
    text = _read(REPORTS / f"loop-close-sc-{d.isoformat()}.md")
    report = _read(SI / f"sc_session_report_{d.strftime('%Y%m%d')}.md") or ""
    if text is None:
        needs.append("SC: no session logged today")
        line = "SoundCloud  ❌ no session logged"
    else:
        s = _score(text)
        c = _counts(text, "Logged actions:")
        parts = [f"{_mark(s)} {s}/10" if s is not None else "❔ no score"]
        parts.append(f"{c.get('sc_follow', 0)} follows")
        if c.get("sc_unfollow"):
            parts.append(f"{c['sc_unfollow']} unfollows")
        parts.append(f"{c.get('sc_like', 0)} likes")
        if s is not None and s < 8:
            needs.append(f"SC session scored {s}/10")
        line = "SoundCloud  " + " · ".join(parts)
    sweep = re.search(r"^## 16:15 sweep run[^\n]*", report, re.M)
    if sweep:
        body = report[sweep.end():]
        bad = re.search(r"STOP|SESSION_INCOMPLETE|not connected", body[:600], re.I)
        line += " · sweep " + ("⚠️" if bad else "✅")
        if bad:
            needs.append("SC sweep run stopped early")
    health = _read(REPORTS / f"sc-weekly-{d.strftime('%Y%m%d')}.md") or ""
    for title, label in (("Stopped following us back", "SC: someone stopped following back"),
                         ("Drift detected", "SC: tracker drift")):
        m = re.search(rf"## {title}[^\n]*\n(.*?)(\n## |\Z)", health, re.S)
        if m and m.group(1).strip() and "_None_" not in m.group(1):
            needs.append(label)
    return line


def yt_line(d: date) -> str | None:
    hits = [p for p in (YT_DIR / "stats").glob(f"{d.isoformat()}*.json")]
    hits += [p for p in (YT_DIR / "backups").glob("*")
             if datetime.fromtimestamp(p.stat().st_mtime).date() == d]
    if not hits:
        return None
    return f"YouTube     ✅ {len(hits)} file(s) updated (stats/metadata)"


def bc_line(d: date) -> str | None:
    if not BC_DIR.exists():
        return None
    hits = [p for p in BC_DIR.rglob("*")
            if p.is_file() and datetime.fromtimestamp(p.stat().st_mtime).date() == d]
    if not hits:
        return None
    return f"Bandcamp    ✅ {len(hits)} file(s) updated (exports/records)"


def _latest_snapshot_value(platform: str, field: str, upto: date):
    """(value, following, as_of) from the newest snapshot up to `upto` that read the platform;
    a skipped block ({"skipped": reason}) is not a reading, the older one stands."""
    for f in sorted(glob.glob(str(SNAPS / "snapshot_*.json")), reverse=True):
        day = Path(f).stem[len("snapshot_"):][:10]
        if day > upto.isoformat():
            continue
        try:
            data = json.load(open(f))
            p = data["platforms"].get(platform) or {}
        except (OSError, ValueError, KeyError):
            continue
        if isinstance(p, dict) and "skipped" in p:
            continue
        if p.get(field) is not None:
            return p[field], p.get("following"), (p.get("as_of") or data.get("timestamp") or day)
    return None, None, None


def goals_line(d: date, now: datetime | None = None) -> str:
    """The 🎯 line over the registry rows flagged for the digest (stats/registry.py META, M11);
    a reading older than its cadence window says '(stale, read MM-DD)'."""
    from stats import registry
    now = now or datetime.combine(d, datetime.min.time().replace(hour=20))
    try:
        metrics = registry.from_targets(json.load(open(TARGETS)))
    except (OSError, ValueError, KeyError):
        return "🎯 goals board not readable (plans/targets.json)"
    out = []
    rung_label = None
    for key, short, plat in registry.digest_rows(metrics):
        m = metrics.get(key) or {}
        rungs = sorted((m.get("rungs") or {}).items())
        nxt = next(((k, v) for k, v in rungs if k >= d.isoformat()), rungs[-1] if rungs else None)
        value, following, as_of = _latest_snapshot_value(plat, "followers", d)
        if nxt is None or value is None:
            continue
        rung_label = rung_label or datetime.fromisoformat(nxt[0]).strftime("%b %-d")
        gap = nxt[1] - value
        fresh = registry.freshness(as_of, m["cadence"], now)
        stale = f" (stale, read {str(as_of)[5:10]})" if fresh["stale"] else ""
        out.append(f"{short} {value} → {nxt[1]} ({'+' if gap <= 0 else '-'}{abs(gap)}){stale}")
        if plat == "soundcloud" and following:
            out.append(f"SC ratio {value / following:.2f} (floor 1.0, target 1.4-1.6)")
    if not out:
        return "🎯 no goal readings found"
    return f"🎯 {rung_label}: " + " · ".join(out)


def now_line() -> str | None:
    """🔥 Now tickets (bucket == now) with 🙋 Amir decides / 🎃 Claude goes."""
    try:
        tickets = json.load(open(ROOT / "plans" / "tickets.json"))["tickets"]
    except (OSError, ValueError, KeyError):
        return None
    marks = {"amir": "🙋", "claude": "🎃", "auto": "🤖"}
    out = [(f"🎬 Socials {t.get('area_no')} · {t.get('label') or t.get('title', '')[:30]} "
            f"{marks.get(t.get('who'), '')}{' 🌐' if t.get('chrome') else ''}").rstrip()
           for t in tickets
           if t.get("area") == "Socials" and t.get("bucket") == "now"
           and t.get("status") not in ("done", "closed")]
    if not out:
        return None
    return "🔥 Now: " + " · ".join(out) + "  (🙋 your call · 🎃 Claude on it · 🌐 needs Chrome)"


def build(d: date) -> str:
    needs: list[str] = []
    lines = [f"🎬 Socials · {d.strftime('%a %m-%d')}", ig_line(d, needs), sc_line(d, needs)]
    for extra in (yt_line(d), bc_line(d)):
        if extra:
            lines.append(extra)
    lines.append(goals_line(d))
    lines.append("⚠️ Needs you: " + "; ".join(needs) if needs else "✅ Nothing needs you")
    now = now_line()
    if now:
        lines.append(now)
    lines.append("📈 SC ratio graph below")  # cue: the 🎬 Socials chat draws it on arrival (Amir 11-06)
    return "\n\n".join(lines)  # blank line between lines (Amir 11-05: more space)


def main(argv: list[str]) -> None:
    args = [a for a in argv if not a.startswith("--")]
    d = date.fromisoformat(args[0]) if args else date.today()
    text = build(d)
    print(text)
    if "--write" in argv:
        (REPORTS / f"socials-digest-{d.isoformat()}.md").write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
