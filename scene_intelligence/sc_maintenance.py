"""
scene_intelligence/sc_maintenance.py
-------------------------------------
SC maintenance audit (SC-08, live 2026-09-01). READ-ONLY.

Runs monthly on the 1st (scheduled reminder; Amir triggers it in a session),
and any time on demand. In Jan/Apr/Jul/Oct the report appends the quarterly
review checklist (seeds, law diff, goal renegotiation).

Checks — each is a lesson the 08-31 twin audit paid for:
  1. Counter drift        stored stats vs recomputed-from-lists (IG was off 22)
  2. Protected integrity  reciprocators in the never-refollow list / churned
  3. Estate ages          every SC state file vs its expected write cadence
                          (the IG paid-audience file froze 3 months unseen)
  4. Backlog + ratio      overdue U2 candidates, ratio vs the goal ladder
  5. U2 throughput        logged unfollows last 30d vs what steady-state needs

Output: docs/reports/sc-maintenance-<YYYYMMDD>.md + terminal verdict.
RED findings fire a macOS notification. Exit codes: 0 green, 1 amber, 2 red.

Usage:
    python3 scene_intelligence/sc_maintenance.py
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

SI_DIR = Path(__file__).parent
BASE = SI_DIR.parent
REPORTS_DIR = BASE / "docs" / "reports"

TRACKER = SI_DIR / "sc_follow_tracker.json"
ENG_LOG = SI_DIR / "engagement_log.json"
AUDIT = SI_DIR / "sc_following_audit.json"
PROMO = SI_DIR / "promotion_log.json"
ENRICHED = SI_DIR / "enriched_contacts.json"

# Goal ladder — OFFICIAL (SC-07, Amir confirmed 2026-09-01). Read from the
# config (THE LAW); fallback mirrors it.
try:
    from scene_intelligence.sc_engagement_config import GOAL_RATIO_FLOOR, GOAL_FOLLOWERS
except ImportError:
    try:
        from sc_engagement_config import GOAL_RATIO_FLOOR, GOAL_FOLLOWERS
    except ImportError:
        GOAL_RATIO_FLOOR = 1.0
        GOAL_FOLLOWERS = {"2026-09-30": 285, "2026-10-31": 420, "2026-11-30": 510, "2026-12-31": 600}

# file -> max age in days before it counts as frozen/stale
ESTATE_CADENCE = {
    "sc_follow_tracker.json": 8,       # every health run + sessions
    "engagement_log.json": 5,          # every session
    "sc_following_audit.json": 8,      # every health run
    "promotion_log.json": 60,          # campaign updates
    "enriched_contacts.json": 60,      # enrichment passes
}

STEADY_STATE_UNFOLLOW_FACTOR = 0.85    # ~85% of follows never reciprocate


def _age_days(p: Path) -> int | None:
    try:
        return (datetime.now() - datetime.fromtimestamp(p.stat().st_mtime)).days
    except OSError:
        return None


def _load(p: Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def check_counters(tracker: dict) -> list[tuple[str, str]]:
    """[(severity, message)] — severity in GREEN/AMBER/RED."""
    out = []
    follows = tracker.get("follows", [])
    stats = tracker.get("stats", {})
    perm = tracker.get("permanently_unfollowed", [])
    fb = sum(1 for e in follows if e.get("followed_back"))
    nlf = sum(1 for e in follows if e.get("no_longer_following"))
    checks = [
        ("total_followed", stats.get("total_followed"), len(follows)),
        ("follow_backs", stats.get("follow_backs"), fb),
        ("no_longer_following", stats.get("no_longer_following"), nlf),
        ("active_follows", stats.get("active_follows"), len(follows) - nlf),
    ]
    for name, stored, real in checks:
        if stored != real:
            out.append(("RED", f"counter drift: stats.{name}={stored} but lists say {real}"))
    diff = abs((stats.get("total_unfollowed") or 0) - len(perm))
    if diff > 1:
        out.append(("AMBER", f"total_unfollowed={stats.get('total_unfollowed')} vs "
                             f"permanently_unfollowed={len(perm)} (drift {diff})"))
    if not out:
        out.append(("GREEN", "counters match the lists"))
    return out


def check_protected(tracker: dict) -> list[tuple[str, str]]:
    out = []
    follows = tracker.get("follows", [])
    perm = set(str(x) for x in tracker.get("permanently_unfollowed", []))
    banned_recips = [e.get("name") for e in follows
                     if e.get("followed_back") and str(e.get("user_id")) in perm]
    churned = [e.get("name") for e in follows
               if e.get("followed_back") and e.get("no_longer_following")]
    keeps = sum(1 for e in follows if e.get("keep_following"))
    if banned_recips:
        out.append(("AMBER", f"reciprocators stuck in the never-refollow list: {banned_recips}"))
    if churned:
        out.append(("AMBER", f"churn record (followed_back + no_longer_following): {len(churned)} — {churned[:5]}"))
    out.append(("GREEN", f"explicit keeps: {keeps}"))
    return out


def check_estate() -> list[tuple[str, str]]:
    out = []
    for fname, max_age in ESTATE_CADENCE.items():
        age = _age_days(SI_DIR / fname)
        if age is None:
            out.append(("RED", f"{fname}: MISSING"))
        elif age > max_age:
            out.append(("AMBER", f"{fname}: {age}d old (cadence expects ≤{max_age}d) — frozen?"))
        else:
            out.append(("GREEN", f"{fname}: {age}d"))
    cands = sorted(SI_DIR.glob("discovery_candidates_*.json"))
    if not cands:
        out.append(("RED", "no discovery_candidates file at all"))
    else:
        age = _age_days(cands[-1])
        sev = "AMBER" if (age or 99) > 8 else "GREEN"
        out.append((sev, f"newest discovery candidates: {cands[-1].name} ({age}d)"))
    promo = _load(PROMO, {})
    for cid, c in (promo.get("campaigns") or {}).items():
        if isinstance(c, dict):
            ns = sum(1 for t in c.get("targets", []) if t.get("status") == "not_sent")
            if ns:
                out.append(("AMBER", f"campaign '{cid}': {ns} not_sent targets still "
                                     f"active (pre-warm keeps firing; close or send)"))
    return out


def check_goals(tracker: dict) -> list[tuple[str, str]]:
    out = []
    audit = _load(AUDIT, {})
    followers = audit.get("total_followers")
    following = audit.get("total_following")
    if not followers or not following:
        out.append(("AMBER", "sc_following_audit.json has no counts — run the health pass"))
        return out
    ratio = followers / following
    sev = "RED" if ratio < 0.8 else ("AMBER" if ratio < GOAL_RATIO_FLOOR else "GREEN")
    out.append((sev, f"ratio {followers}/{following} = {ratio:.2f} (floor {GOAL_RATIO_FLOOR})"))
    today = date.today().isoformat()
    next_goal = next(((d, n) for d, n in sorted(GOAL_FOLLOWERS.items()) if d >= today), None)
    if next_goal:
        d, n = next_goal
        gap = n - followers
        out.append(("GREEN" if gap <= 0 else "AMBER" if gap < 40 else "RED",
                    f"next camp: {n} followers by {d} — now {followers}, gap {gap}"))
    overdue = sum(1 for e in tracker.get("follows", [])
                  if not e.get("followed_back") and not e.get("no_longer_following")
                  and not e.get("keep_following") and not e.get("no_longer_engage")
                  and (e.get("unfollow_after") or "9999") <= today)
    out.append(("AMBER" if overdue > 60 else "GREEN", f"U2 backlog: {overdue} overdue"))
    return out


def check_u2_throughput(eng: dict) -> list[tuple[str, str]]:
    cutoff = (date.today() - timedelta(days=30)).isoformat()
    unf = fol = 0
    for es in (eng.get("log") or {}).values():
        if not isinstance(es, list):
            continue
        for e in es:
            if e.get("platform") != "soundcloud" or (e.get("date") or "") < cutoff:
                continue
            a = e.get("action", "")
            if a.startswith("sc_unfollow"):
                unf += 1
            elif a == "sc_follow":
                fol += 1
    need = round(fol * STEADY_STATE_UNFOLLOW_FACTOR)
    sev = "GREEN" if unf >= need or fol == 0 else ("AMBER" if unf >= need // 2 else "RED")
    return [(sev, f"last 30d: {fol} follows vs {unf} logged unfollows "
                  f"(steady state needs ≈{need}) — ratio "
                  f"{'holds' if sev == 'GREEN' else 'is slipping'}")]


QUARTERLY_CHECKLIST = [
    "Seed review: per-source yield + the reciprocator-vs-label seed split (labels crawl 0x since 07-24)",
    "Law diff: config SESSION_* vs SOP §4.1 vs close_loops — one law, prose mirrors",
    "Experiments: every pre-committed decision rule gets its verdict (band table is in the weekly now)",
    "Goal renegotiation: camps vs actual trajectory, with the growth math",
]


def main() -> int:
    today = date.today()
    sections = [
        ("Counter drift", check_counters),
        ("Protected-account integrity", check_protected),
    ]
    tracker = _load(TRACKER, {"follows": []})
    eng = _load(ENG_LOG, {"log": {}})

    results: list[tuple[str, list[tuple[str, str]]]] = [
        ("Counter drift", check_counters(tracker)),
        ("Protected-account integrity", check_protected(tracker)),
        ("Estate ages", check_estate()),
        ("Goals & ratio", check_goals(tracker)),
        ("U2 throughput", check_u2_throughput(eng)),
    ]

    worst = "GREEN"
    md = [f"# SC Maintenance — {today.isoformat()}", ""]
    for title, findings in results:
        md.append(f"## {title}")
        print(f"\n== {title} ==")
        for sev, msg in findings:
            mark = {"GREEN": "OK", "AMBER": "WARN", "RED": "RED"}[sev]
            md.append(f"- **{mark}** {msg}")
            print(f"  [{mark}] {msg}")
            if sev == "RED":
                worst = "RED"
            elif sev == "AMBER" and worst != "RED":
                worst = "AMBER"
        md.append("")

    if today.month in (1, 4, 7, 10):
        md.append("## Quarterly review (due this month)")
        for item in QUARTERLY_CHECKLIST:
            md.append(f"- [ ] {item}")
        md.append("")
        print("\n== Quarterly review due this month — checklist in the report ==")

    md.append(f"**Verdict: {worst}**")
    md.append("")
    md.append("Generated by `scene_intelligence/sc_maintenance.py` (SC-08). Read-only.")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / f"sc-maintenance-{today.strftime('%Y%m%d')}.md"
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"\nVerdict: {worst}  ->  {out.relative_to(BASE)}")

    if worst == "RED":
        try:
            import subprocess
            subprocess.run(["osascript", "-e",
                            'display notification "SC maintenance found RED findings" '
                            'with title "SC maintenance — NEEDS AMIR" sound name "Basso"'],
                           capture_output=True, timeout=10)
        except Exception:
            pass
    return {"GREEN": 0, "AMBER": 1, "RED": 2}[worst]


if __name__ == "__main__":
    sys.exit(main())
