# Release/Campaign Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a stage-aware `/release` skill that orchestrates a release end-to-end (plan, prep, release day, capture, post-mortem) and closes a learning loop, backed by a small tested helper for stage detection + post-mortem aggregation.

**Architecture:** Approach B — orchestration/voice live in the `/release` skill (prose); the two data-heavy jobs (stage detection, stat aggregation) live in `scene_intelligence/release_status.py` with unit-tested pure helpers. The skill delegates to existing pieces (`release-prep`, `ig-expert`, `ig_fetch_insights.py`) and never duplicates them. Outcomes are stored in `releases/<slug>.json`; lessons accumulate in `plans/release-lessons.md` and are read at the next Plan stage.

**Tech Stack:** Python 3.9+ (stdlib only: json, os, argparse, datetime, collections), pytest, Claude Code skills (markdown).

---

## File Structure

- `scene_intelligence/release_status.py` — stage detection + post-mortem aggregation (pure helpers + CLI).
- `tests/test_release_status.py` — unit tests for the pure helpers.
- `plans/release-lessons.md` — accumulating lessons store, seeded from Farewell Part E.
- `.claude/skills/release/SKILL.md` — the stage-aware orchestrator skill (gitignored, like all skills; local-only).
- `releases/<slug>.json` — gains `stage` + `outcomes` at runtime (backward compatible; absent on old releases).

Note: `.claude/` is gitignored in this repo (all existing skills are local-only), so the skill file is created and active locally but not committed. The Python helper, tests, lessons file, and docs ARE committed.

---

## Task 1: release_status.py — stage detection (TDD)

**Files:**
- Create: `scene_intelligence/release_status.py`
- Test: `tests/test_release_status.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_release_status.py`:

```python
import datetime
import scene_intelligence.release_status as rs


def test_detect_stage_by_date_offset():
    today = datetime.date(2026, 5, 15)
    def rel(date, **kw):
        return {"release_date": date, **kw}
    assert rs.detect_stage(rel("2026-06-30"), today) == "plan"        # >14d before
    assert rs.detect_stage(rel("2026-05-22"), today) == "prep"        # within 14d before
    assert rs.detect_stage(rel("2026-05-15"), today) == "release_day" # release day
    assert rs.detect_stage(rel("2026-05-05"), today) == "capture"     # 10d after
    assert rs.detect_stage(rel("2026-03-01"), today) == "post_mortem" # >25d after


def test_detect_stage_explicit_override_wins():
    today = datetime.date(2026, 5, 15)
    r = {"release_date": "2026-05-15", "stage": "post_mortem"}
    assert rs.detect_stage(r, today) == "post_mortem"


def test_detect_stage_no_date_defaults_plan():
    assert rs.detect_stage({}, datetime.date(2026, 5, 15)) == "plan"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_release_status.py -v`
Expected: FAIL — `ModuleNotFoundError`/`AttributeError` (module/function not defined).

- [ ] **Step 3: Write minimal implementation**

Create `scene_intelligence/release_status.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_release_status.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add scene_intelligence/release_status.py tests/test_release_status.py
git commit -m "feat(release): stage detection for /release skill"
```

---

## Task 2: release_status.py — aggregation helpers + CLI (TDD)

**Files:**
- Modify: `scene_intelligence/release_status.py`
- Test: `tests/test_release_status.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_release_status.py`:

```python
def test_match_ig_media_date_window():
    media = [
        {"permalink": "a", "timestamp": "2026-05-15T17:13:17+0000"},  # release day -> in
        {"permalink": "b", "timestamp": "2026-05-30T10:00:00+0000"},  # +15d -> in
        {"permalink": "c", "timestamp": "2026-01-29T10:00:00+0000"},  # months before -> out
        {"permalink": "d", "timestamp": "2026-07-01T10:00:00+0000"},  # +47d -> out
    ]
    got = [m["permalink"] for m in rs.match_ig_media(media, "2026-05-15")]
    assert got == ["a", "b"]


def test_promotion_funnel_counts_statuses():
    campaign = {"targets": [
        {"status": "sent"}, {"status": "sent"}, {"status": "replied"},
        {"status": "rejected"}, {"status": "bounced"},
    ]}
    f = rs.promotion_funnel(campaign)
    assert f["total"] == 5
    assert f["by_status"]["sent"] == 2
    assert f["by_status"]["replied"] == 1


def test_promotion_funnel_empty():
    assert rs.promotion_funnel({})["total"] == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_release_status.py -v`
Expected: FAIL — `AttributeError` (match_ig_media / promotion_funnel not defined).

- [ ] **Step 3: Write the implementation**

Append to `scene_intelligence/release_status.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_release_status.py -v`
Expected: PASS (all tests).

- [ ] **Step 5: Verify against the real Farewell release**

Run: `python3 scene_intelligence/release_status.py farewell-single --stage`
Expected: prints `post_mortem` (release was 2026-05-15, well over 25 days ago).
Run: `python3 scene_intelligence/release_status.py farewell-single --aggregate`
Expected: JSON with `ig` containing the Farewell reel insights (reach/views) and `promotion.by_status` showing the label-demo funnel (sent/replied/rejected/bounced).

- [ ] **Step 6: Commit**

```bash
git add scene_intelligence/release_status.py tests/test_release_status.py
git commit -m "feat(release): IG/promotion aggregation + CLI for post-mortem"
```

---

## Task 3: Seed the lessons store

**Files:**
- Create: `plans/release-lessons.md`

- [ ] **Step 1: Write the lessons file (seeded from Farewell Part E + post-mortem)**

Create `plans/release-lessons.md`:

```markdown
# Release Lessons (accumulating)

Read at the **Plan** stage of every release; appended to by the **Post-mortem** stage.
Newest first. Each entry tagged with the release it came from.

## From: farewell-single (2026-05-15)
- Set up pre-saves at T-14 days. Farewell had none.
- Prep the grid image in advance; improvising it on release day delayed the reel.
- Time the r/EBM post to land ON release day (r/EBM has a 30-day cooldown and is the best-fit sub; do not burn it early).
- Build the DJ promo list early and SEPARATE from the label/demo campaign (different audiences, different goals).
- Always click through auto-matched DSP links (Apple's first Farewell match was the wrong title).
- Keep IG DM volume low per day (bot-warning history); split promo DMs across days, vary the text.
- Confirm which directory the RM server runs from before a release (worktree data-split bug).
- CAPTURE OUTCOMES as they happen (replies, plays, support) — Farewell's real wins were never logged, so the campaign could not be measured. This is why the /release capture stage exists.
- Promotion was labels-only; the channels that drive plays (DJs, playlists, press) were skipped. Broaden channels next time.
```

- [ ] **Step 2: Commit**

```bash
git add plans/release-lessons.md
git commit -m "docs(release): seed accumulating lessons store from Farewell"
```

---

## Task 4: The /release orchestrator skill

**Files:**
- Create: `.claude/skills/release/SKILL.md`

- [ ] **Step 1: Write the skill file**

Create `.claude/skills/release/SKILL.md`:

```markdown
---
name: release
description: Stage-aware release campaign orchestrator for Inch of Shadow. Runs a release end-to-end - plan, prep, release day, capture outcomes, post-mortem - and learns from each release. Use when the user mentions running, planning, or reviewing a release, or types /release.
argument-hint: [release name/slug, e.g. "the-deciver-single"]
---

# Release / Campaign Orchestrator

Drive a release through its lifecycle. Guide + do-on-confirm: show the stage and the next
actions, and run the safe automatable ones ONLY after the artist confirms each. Never post,
DM, or fire IG-API calls without confirmation; pre-announce IG fetch call counts.

## Step 1: Resolve the release + detect stage

Find the release slug from `$ARGUMENTS` (match a file in `releases/`). If none matches,
ask which release (or offer to create one via the release-prep skill).
Run: `python3 scene_intelligence/release_status.py <slug> --stage`
Report the stage to the artist.

## Step 2: Drive the detected stage

**plan** — Read `plans/release-lessons.md` (apply last release's lessons) and
`plans/release-platform-deadlines.md`. Surface the dated to-dos (Spotify pitch T-31/40,
pre-saves at T-14, r/EBM cooldown, grid image prep). Output a tailored plan; don't execute.

**prep** — Hand off to the `release-prep` skill for SEO copy, premiere contacts, checklist.
Do not duplicate it.

**release_day** — Walk `plans/release-day-playbook.md` Part A in order. Offer the
`ig-expert` agent for the reel/caption + Canva art (on confirm). Track which steps are done.

**capture** — Auto-pull IG stats: pre-announce, then run
`python3 scene_intelligence/ig_fetch_insights.py` (1 + N calls). Then ask the artist for
human outcomes in plain words ("Mechatronica replied interested; DJ X played it on SC") and
write them to `releases/<slug>.json` under `outcomes.human` as structured entries
(`who`, `type`, `event`, `sentiment`, `note`, `logged`). Also write pulled stats under
`outcomes.stats`.

**post_mortem** — Run `python3 scene_intelligence/release_status.py <slug> --aggregate`,
synthesize a report (what we did / what worked / what we could not measure / lessons), then
APPEND the new lessons to `plans/release-lessons.md` under a `## From: <slug>` heading so
the next release's plan stage reads them. This closes the loop.

## Writing to the release JSON
Merge into `releases/<slug>.json` (never overwrite unrelated fields). Add `stage` and
`outcomes` if absent. After writing, tell the artist the file path.

## Boundaries
- No posting, DMs, or live engagement (artist / CC only).
- Nothing fires without confirmation; pre-announce every IG-API call count.
- Don't own outreach detail; the Promotion agent will. For now, capture outcomes into the
  release JSON.
- Obey all standing rules (no double-dash, no Software Zero, IG risk caps, genre "Synthwave").
```

- [ ] **Step 2: Verify the skill is present**

Run: `python3 -c "import pathlib; print(pathlib.Path('.claude/skills/release/SKILL.md').exists())"`
Expected: `True`. (Restart Claude Code if `/release` must appear in the skill list.)

- [ ] **Step 3: (No commit — `.claude/` is gitignored, like all existing skills.)**

---

## Task 5: End-to-end verification

- [ ] **Step 1: Full test suite**

Run: `python3 -m pytest tests/test_release_status.py -v`
Expected: all PASS.

- [ ] **Step 2: Stage + aggregate on the real release**

Run: `python3 scene_intelligence/release_status.py farewell-single --stage`
Expected: `post_mortem`.
Run: `python3 scene_intelligence/release_status.py farewell-single --aggregate`
Expected: JSON showing the Farewell reel IG insights + the label-demo promotion funnel.

- [ ] **Step 3: Smoke-test the skill**

In a fresh Claude Code session, run `/release farewell-single`.
Expected: reports stage `post_mortem`, offers to aggregate + write a post-mortem, and would
append lessons to `plans/release-lessons.md`. Confirm it does NOT post, DM, or fetch without
asking.

- [ ] **Step 4: Final commit (if any cleanup)**

```bash
git add -A
git commit -m "chore(release): finalize /release skill + status helper"
```
