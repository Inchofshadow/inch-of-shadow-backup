"""
scene_intelligence/release_weekly_health.py
--------------------------------------------
Weekly release health pass for Inch of Shadow.

Closes the capture gap (Farewell's outcomes were never logged) and flags
overdue critical-path items before they cost a deadline (the stale-checklist
problem caught 2026-06-08 on The Deceiver).

What it does, per release in releases/*.json:
  1. Reports stage (via release_status.py) and days to/since release.
  2. Flags OVERDUE checklist items (undone, due_date in the past).
  3. Lists items due in the next 7 days.
  4. Flags drift: release date passed but stage still plan/prep,
     or outcomes empty at T+3 or later (capture overdue).
  5. Ingests promotion campaign status counts from promotion_log.json
     into the release JSON under outcomes.stats.promo (merge-only;
     never touches outcomes.human).
  6. Generates docs/reports/release-health-<YYYYMMDD>.md.

Hard rules (engagement-safety):
  - ZERO API calls. No IG, no SC, no network.
  - READ-ONLY on every engagement-adjacent file: promotion_log.json,
    dj_promo_targets.json, playlist_curator_targets.json,
    enriched_contacts.json, release_context.json, ig_* / sc_* files.
  - Writes ONLY to releases/<slug>.json (outcomes.stats merge) and
    docs/reports/. Nothing the engagement automations read is modified.
  - The human side of capture (replies, plays, support) is NOT automated:
    the report nags for it; the artist logs it via the /release capture stage.

Usage:
    python3 scene_intelligence/release_weekly_health.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RELEASES_DIR = BASE / "releases"
REPORTS_DIR = BASE / "docs" / "reports"
PROMOTION_LOG = BASE / "scene_intelligence" / "promotion_log.json"
DJ_TARGETS = BASE / "scene_intelligence" / "dj_promo_targets.json"
CURATOR_TARGETS = BASE / "scene_intelligence" / "playlist_curator_targets.json"

CAPTURE_GRACE_DAYS = 3  # outcomes expected from T+3 onward


def _load_json(path: Path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _stage(slug: str) -> str:
    try:
        out = subprocess.run(
            [sys.executable, str(BASE / "scene_intelligence" / "release_status.py"), slug, "--stage"],
            capture_output=True, text=True, timeout=30,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _parse(d: str):
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def analyse_release(path: Path, today: date, promo_log: dict) -> dict:
    rel = _load_json(path, {})
    slug = rel.get("slug", path.stem)
    rd = _parse(rel.get("release_date", ""))
    checklist = rel.get("checklist", [])

    overdue, upcoming = [], []
    for item in checklist:
        if item.get("done"):
            continue
        due = _parse(item.get("due_date", ""))
        if not due:
            continue
        if due < today:
            overdue.append((due, item["label"]))
        elif (due - today).days <= 7:
            upcoming.append((due, item["label"]))
    overdue.sort()
    upcoming.sort()

    flags = []
    stage = _stage(slug)
    if rd and rd < today and stage in ("plan", "prep"):
        flags.append(f"release date {rd} has passed but stage is still '{stage}'")
    if rd is None and any(not c.get("done") for c in checklist):
        flags.append("no release date set; checklist dates cannot be trusted")

    # Capture check + promo ingest (post-release only)
    outcomes = rel.get("outcomes", {})
    campaign = (promo_log.get("campaigns") or {}).get(slug) or {}
    promo_counts = Counter(t.get("status", "unknown") for t in campaign.get("targets", []))
    capture_overdue = False
    if rd and (today - rd).days >= CAPTURE_GRACE_DAYS:
        if not outcomes.get("human"):
            capture_overdue = True
            flags.append(
                f"T+{(today - rd).days} and outcomes.human is empty: "
                "run /release capture while wins are still fresh"
            )
        # Spotify is S4A-only (no API) - must be screenshotted manually
        sp = (outcomes.get("stats") or {}).get("spotify") or {}
        if sp.get("streams_all_time") is None and sp.get("streams") is None:
            flags.append(
                f"T+{(today - rd).days}: no Spotify stats captured. "
                "Screenshot Spotify for Artists (S4A) - streams/listeners/saves/playlist adds. "
                "No API for this; it stays invisible until you grab it."
            )

    return {
        "slug": slug, "title": rel.get("metadata", {}).get("title", slug),
        "release_date": rd, "stage": stage, "path": path, "rel": rel,
        "overdue": overdue, "upcoming": upcoming, "flags": flags,
        "promo_counts": dict(promo_counts), "capture_overdue": capture_overdue,
    }


def ingest_promo_stats(info: dict, today: date, dry_run: bool) -> bool:
    """Merge promotion_log status counts into outcomes.stats.promo.
    Writes only the release JSON. Never touches outcomes.human."""
    if not info["promo_counts"]:
        return False
    rel = info["rel"]
    outcomes = rel.setdefault("outcomes", {})
    stats = outcomes.setdefault("stats", {})
    existing = stats.get("promo", {})
    new_block = {"counts": info["promo_counts"], "as_of": today.isoformat()}
    if existing.get("counts") == new_block["counts"]:
        return False
    stats["promo"] = new_block
    rel["updated_at"] = datetime.now().isoformat(timespec="seconds")
    if not dry_run:
        with open(info["path"], "w") as f:
            json.dump(rel, f, indent=2, ensure_ascii=False)
    return True


def generate_report(results: list, today: date, ingested: list) -> str:
    lines = [f"# Release Health Report -- {today.isoformat()}", ""]
    dj = _load_json(DJ_TARGETS, {})
    cur = _load_json(CURATOR_TARGETS, {})

    for r in sorted(results, key=lambda x: (x["release_date"] is None, x["release_date"] or today)):
        rd = r["release_date"]
        when = "no date set"
        if rd:
            delta = (today - rd).days  # positive = post-release
            when = f"T{delta:+d} ({rd})" if delta else f"RELEASE DAY ({rd})"
        lines.append(f"## {r['title']} (`{r['slug']}`)")
        lines.append(f"- Stage: **{r['stage']}** | {when}")
        if r["flags"]:
            lines.append("- **FLAGS:**")
            for fl in r["flags"]:
                lines.append(f"  - {fl}")
        if r["overdue"]:
            lines.append(f"- **Overdue ({len(r['overdue'])}):**")
            for due, label in r["overdue"]:
                lines.append(f"  - {due} {label}")
        if r["upcoming"]:
            lines.append("- Due next 7 days:")
            for due, label in r["upcoming"]:
                lines.append(f"  - {due} {label}")
        if r["promo_counts"]:
            counts = ", ".join(f"{k}: {v}" for k, v in sorted(r["promo_counts"].items()))
            lines.append(f"- Promo campaign (from promotion_log, read-only): {counts}")
        if not (r["flags"] or r["overdue"] or r["upcoming"]):
            lines.append("- On track. Nothing due this week.")
        lines.append("")

    if ingested:
        lines.append(f"_Ingested promo stats into: {', '.join(ingested)}_")
    djs = dj.get("targets", dj if isinstance(dj, list) else [])
    n_dj = sum(
        1 for t in djs if isinstance(t, dict)
        and any(r.get("send") for r in t.get("releases", {}).values())
    )
    n_cur = len(cur.get("targets", []))
    lines.append("")
    lines.append(f"Channel inventories (read-only): DJ targets flagged send: {n_dj} | curator playlists tracked: {n_cur}")
    lines.append("")
    lines.append("---")
    lines.append("Generated by `scene_intelligence/release_weekly_health.py`. "
                 "Zero API calls; engagement files read-only.")
    return "\n".join(lines)


def iter_release_paths(releases_dir=None):
    """Real release files only. Stats-capture backups live in the same dir and
    end in .json (e.g. farewell-single.bak.20260711_220111_sc_stats.json), so a
    bare *.json glob double-counts: the 2026-07-15 report listed Farewell twice
    and The Deceiver three times, and each duplicate went through the promo
    ingest path."""
    d = releases_dir if releases_dir is not None else RELEASES_DIR
    return [p for p in sorted(d.glob("*.json")) if ".bak" not in p.name]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="no writes at all")
    args = ap.parse_args()

    today = date.today()
    promo_log = _load_json(PROMOTION_LOG, {})

    results = []
    for path in iter_release_paths():
        results.append(analyse_release(path, today, promo_log))

    ingested = []
    for r in results:
        if ingest_promo_stats(r, today, args.dry_run):
            ingested.append(r["slug"])

    report = generate_report(results, today, ingested)
    if args.dry_run:
        print(report)
        print("\n[dry-run] no files written")
        return
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / f"release-health-{today.strftime('%Y%m%d')}.md"
    out.write_text(report)
    print(report)
    print(f"\nReport saved: {out}")


if __name__ == "__main__":
    main()
