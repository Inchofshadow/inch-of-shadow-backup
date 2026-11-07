"""Stage detection + post-mortem aggregation for the /release skill.

Pure helpers are unit-tested (no I/O, no network). The CLI loads files and prints
the stage or an aggregated post-mortem summary as JSON. Stdlib only.
"""
import json
import os
import argparse
import datetime
import collections

VALID_STAGES = ["plan", "prep", "release_day", "capture", "post_mortem"]


def detect_stage(release, today):
    """Return the lifecycle stage. An explicit release['stage'] overrides date logic."""
    s = release.get("stage")
    if s in VALID_STAGES:
        return s
    rd = release.get("release_date")
    if not rd:
        return "plan"
    rel = datetime.date.fromisoformat(rd)
    d = (today - rel).days
    if d < -14:
        return "plan"
    if d < 0:
        return "prep"
    if d == 0:
        return "release_day"
    if d <= 25:
        return "capture"
    return "post_mortem"


def match_ig_media(media_list, release_date, before=3, after=30):
    """IG media whose timestamp falls within [release_date - before, + after] days."""
    rel = datetime.date.fromisoformat(release_date)
    out = []
    for m in media_list:
        ts = m.get("timestamp", "")
        if not ts:
            continue
        d = datetime.date.fromisoformat(ts[:10])
        if -before <= (d - rel).days <= after:
            out.append(m)
    return out


def promotion_funnel(campaign):
    """Count outreach targets by status for a promotion_log campaign dict."""
    targets = campaign.get("targets", []) if isinstance(campaign, dict) else []
    counts = collections.Counter(t.get("status", "unknown") for t in targets)
    return {"total": len(targets), "by_status": dict(counts)}


def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return None


def aggregate(slug, base_dir="."):
    """Assemble a post-mortem summary for a release from the data we actually have.

    IG insights (date-matched) and the promotion funnel are real; SC/DSP are left null
    until those data sources exist (honest about current coverage).
    """
    release = _load(os.path.join(base_dir, "releases", f"{slug}.json")) or {}
    rd = release.get("release_date")
    ig = _load(os.path.join(base_dir, "scene_intelligence", "ig_insights.json")) or {}
    ig_media = match_ig_media(ig.get("media", []), rd) if rd else []
    pl = _load(os.path.join(base_dir, "scene_intelligence", "promotion_log.json")) or {}
    campaign = (pl.get("campaigns", {}) or {}).get(slug, {})
    outcomes = release.get("outcomes", {}) or {}
    return {
        "slug": slug,
        "release_date": rd,
        "ig": [{"permalink": m.get("permalink"), "insights": m.get("insights", {})} for m in ig_media],
        "promotion": promotion_funnel(campaign),
        "human_outcomes": outcomes.get("human", []),
        "sc": None,   # no per-release SC play data source yet
        "dsp": None,  # no DSP stats source yet
    }


def main():
    ap = argparse.ArgumentParser(description="Release stage + post-mortem aggregation")
    ap.add_argument("slug", help="Release slug (matches releases/<slug>.json)")
    ap.add_argument("--stage", action="store_true", help="Print the current stage")
    ap.add_argument("--aggregate", action="store_true", help="Print post-mortem summary JSON")
    ap.add_argument("--base-dir", default=".")
    args = ap.parse_args()

    if args.stage or not args.aggregate:
        release = _load(os.path.join(args.base_dir, "releases", f"{args.slug}.json")) or {}
        print(detect_stage(release, datetime.date.today()))
    if args.aggregate:
        print(json.dumps(aggregate(args.slug, args.base_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
