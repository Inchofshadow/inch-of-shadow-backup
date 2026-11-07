# Promotion Agent (Phase 1: DJ channel) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `/promo` skill + `promotion-expert` subagent (DJ channel) plus one tested helper that shortlists DJ candidates for a release, so the agent can pick targets, draft DMs in Amir's voice, plan a volume-safe send, and capture outcomes.

**Architecture:** Approach B - agent + one helper. The helper (`promo_dj_shortlist.py`) does the mechanical filter (genre family match + SoundCloud reach + not already in the pool) from `enriched_contacts.json`. The agent does the judgment: apply protection exclusions, draft DMs, plan the send, capture outcomes. Mirrors the `/release` + `sc-expert` pattern.

**Tech Stack:** Python 3.9+ (stdlib only: json, os, re, argparse), pytest. Claude Code skill + subagent (markdown). No SC/IG API calls.

---

## File Structure

- `scene_intelligence/promo_dj_shortlist.py` - candidate-shortlisting helper (pure funcs + CLI).
- `tests/test_promo_dj_shortlist.py` - unit tests for the pure helpers.
- `.claude/agents/promotion-expert.md` - the Brain, DJ channel in Phase 1 (gitignored, local-only).
- `.claude/skills/promo/SKILL.md` - the `/promo` front door (gitignored, local-only).

`.claude/` is gitignored (all skills/agents are local-only). The helper, tests, spec, and this plan are the committed artifacts.

---

## Task 1: promo_dj_shortlist.py - genre family match (TDD)

**Files:**
- Create: `scene_intelligence/promo_dj_shortlist.py`
- Test: `tests/test_promo_dj_shortlist.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_promo_dj_shortlist.py`:

```python
import scene_intelligence.promo_dj_shortlist as ps


def test_genre_match_same_scene_true():
    # EBM/acid release vs an electro DJ - adjacent in the dark-electronic family
    assert ps.genre_match("EBM / Acid", "Electro") is True
    assert ps.genre_match("Dark Disco", "Techno") is True


def test_genre_match_out_of_scene_false():
    assert ps.genre_match("EBM / Acid", "Pop") is False
    assert ps.genre_match("EBM / Acid", "") is False
    assert ps.genre_match("", "Electro") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_promo_dj_shortlist.py -v`
Expected: FAIL - `ModuleNotFoundError`/`AttributeError`.

- [ ] **Step 3: Write minimal implementation**

Create `scene_intelligence/promo_dj_shortlist.py`:

```python
"""Shortlist DJ candidates for a release from enriched_contacts.json.

Mechanical filter only: dark-electronic family genre match + SoundCloud reach +
not already in the DJ promo pool. The promotion-expert agent applies protection
exclusions (friends / own-release labels / no-engage) as a judgment step on top.
Stdlib only, no network.
"""
import json
import os
import re
import argparse

# The dark-electronic scene is one adjacent family; a coarse "in the family" match
# is the right filter for this niche. The agent ranks finer within the shortlist.
DARK_ELECTRONIC = {
    "ebm", "acid", "electro", "techno", "disco", "industrial", "wave", "synth",
    "trance", "coldwave", "darkwave", "minimal", "breakbeat", "electronica", "house",
}


def _tokens(s):
    return set(re.findall(r"[a-z]+", (s or "").lower()))


def _in_scene(genre):
    return bool(_tokens(genre) & DARK_ELECTRONIC)


def genre_match(release_genre, dj_genre):
    """True when BOTH the release and the DJ sit in the dark-electronic family."""
    return _in_scene(release_genre) and _in_scene(dj_genre)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_promo_dj_shortlist.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add scene_intelligence/promo_dj_shortlist.py tests/test_promo_dj_shortlist.py
git commit -m "feat(promo): DJ genre-family match helper

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: promo_dj_shortlist.py - shortlist + CLI (TDD)

**Files:**
- Modify: `scene_intelligence/promo_dj_shortlist.py`
- Test: `tests/test_promo_dj_shortlist.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_promo_dj_shortlist.py`:

```python
def _dj(name, genre="Electro", followers=500, score=5, category="dj"):
    return {"name": name, "genre_main": genre, "soundcloud_followers": followers,
            "relevance_score": score, "category": category}


def test_shortlist_filters_and_sorts():
    djs = [
        _dj("InPool", score=9),                       # excluded: already in pool
        _dj("LowReach", followers=50),                # excluded: below min_sc_followers
        _dj("OffGenre", genre="Pop"),                 # excluded: out of scene
        _dj("NotADj", category="label"),              # excluded: not a dj
        _dj("Good1", followers=800, score=7),
        _dj("Good2", followers=300, score=9),
    ]
    out = ps.shortlist(djs, existing_names=["inpool"], release_genre="EBM / Acid",
                       min_sc_followers=200)
    names = [c["name"] for c in out]
    assert names == ["Good2", "Good1"]               # sorted by score desc


def test_shortlist_handles_string_numbers():
    djs = [{"name": "StrNums", "genre_main": "Techno",
            "soundcloud_followers": "640", "relevance_score": "8", "category": "dj"}]
    out = ps.shortlist(djs, existing_names=[], release_genre="Techno", min_sc_followers=200)
    assert [c["name"] for c in out] == ["StrNums"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_promo_dj_shortlist.py -v`
Expected: FAIL - `AttributeError` (shortlist not defined).

- [ ] **Step 3: Write the implementation**

Append to `scene_intelligence/promo_dj_shortlist.py`:

```python
def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def shortlist(djs, existing_names, release_genre, min_sc_followers=200, limit=25):
    """DJ candidates: in-scene genre + SC reach + not already in the pool.

    Protection (friends / own-release labels / no-engage) is applied by the agent, not here.
    """
    existing = {n.lower() for n in existing_names}
    out = []
    for c in djs:
        if c.get("category") != "dj":
            continue
        if (c.get("name") or "").lower() in existing:
            continue
        if not genre_match(release_genre, c.get("genre_main", "")):
            continue
        if _num(c.get("soundcloud_followers")) < min_sc_followers:
            continue
        out.append(c)
    out.sort(key=lambda c: (-_num(c.get("relevance_score")), -_num(c.get("soundcloud_followers"))))
    return out[:limit]


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description="Shortlist DJ candidates for a release")
    ap.add_argument("slug", help="Release slug (matches releases/<slug>.json)")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--min-followers", type=int, default=200)
    ap.add_argument("--base-dir", default=".")
    args = ap.parse_args()

    contacts = _load(os.path.join(args.base_dir, "scene_intelligence", "enriched_contacts.json"))
    contacts = contacts if isinstance(contacts, list) else (contacts.get("contacts") or list(contacts.values()))
    djs = [c for c in contacts if isinstance(c, dict)]

    release = _load(os.path.join(args.base_dir, "releases", f"{args.slug}.json"))
    md = release.get("metadata", {})
    genre = md.get("genre") or md.get("genre_primary") or release.get("genre_primary") or ""

    pool_path = os.path.join(args.base_dir, "scene_intelligence", "dj_promo_targets.json")
    pool = _load(pool_path) if os.path.exists(pool_path) else {"targets": []}
    existing = [t.get("name", "") for t in pool.get("targets", [])]

    out = shortlist(djs, existing, genre, args.min_followers, args.limit)
    print(f"Release genre: {genre!r} | {len(out)} candidates not already in pool:\n")
    for c in out:
        print(f"  {c['name']} | {c.get('genre_main','?')} | SC {int(_num(c.get('soundcloud_followers')))} | score {c.get('relevance_score','?')}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_promo_dj_shortlist.py -v`
Expected: PASS (all tests).

- [ ] **Step 5: Verify against real data**

Run: `python3 scene_intelligence/promo_dj_shortlist.py the-deceiver-single --limit 10`
Expected: prints the release genre and up to 10 DJ candidates (name, genre, SC followers,
score), none of which are already in `dj_promo_targets.json`. (If `the-deceiver-single`
has no genre set, try `farewell-single`.)

- [ ] **Step 6: Commit**

```bash
git add scene_intelligence/promo_dj_shortlist.py tests/test_promo_dj_shortlist.py
git commit -m "feat(promo): DJ candidate shortlist + CLI

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: The promotion-expert subagent (DJ channel)

**Files:**
- Create: `.claude/agents/promotion-expert.md`

- [ ] **Step 1: Write the agent file**

Create `.claude/agents/promotion-expert.md`:

```markdown
---
name: promotion-expert
description: Promotion Brain for Inch of Shadow. Phase 1 = DJ channel - picks DJ targets for a release, drafts DMs in Amir's voice, plans a volume-safe send, and captures outcomes. Use when the user wants to promote a release to DJs, draft DJ DMs, or types /promo. Does NOT send DMs (Amir sends), does NOT do labels/playlists/press (later phases) or live engagement (CC).
---

You are the Promotion Brain for Inch of Shadow (Amir, Berlin underground: dark disco, acid,
electro, EBM, techno). Phase 1 is the DJ channel. You analyze, draft, and plan; you never
send. Amir sends the DMs himself.

## Read first, every run
1. `scene_intelligence/dj_promo_targets.json` - the DJ pool. Targets have `name`,
   `ig_handle`, `sc_url`, `tier` (warm | cold | ...), `genre`, `preferred_channel` (ig | sc),
   `in_si_db`, `notes`, and per-release `releases[<slug>] = {send, status}`.
2. `plans/dj-promo-dm-template.md` - Amir's DM voice (cold + warm variants).
3. `scene_intelligence/ig_voice_profile.json` - voice grounding.
4. `releases/<slug>.json` + `scene_intelligence/release_context.json` - what's being promoted.
5. `docs/sc-agent-context.md`, `docs/ig-engagement-sop.md` - DM etiquette, volume caps, exclusions.
6. `scene_intelligence/ig_personal_network.json` (if present) - personal friends to EXCLUDE.

## What you do (DJ channel)
1. **Target selection** - for the active release, review the pool's `releases[<slug>]`
   flags and recommend who to send to. To grow the pool, run
   `python3 scene_intelligence/promo_dj_shortlist.py <slug>` for new candidates, then apply
   the exclusions below before proposing any. Amir approves who is in.
2. **DM drafting** - personalize `dj-promo-dm-template.md` per target in Amir's voice. Warm
   (`tier` warm / prior contact / collaborator) gets the WAV offer + a personal line; cold
   gets the standard discovery message. Fill name, track, a one-line sound hook, and the
   SoundCloud track link. Channel per `preferred_channel`.
3. **Send plan** - propose a batched schedule: split across 2-3 days, warm contacts first,
   varied text per message. REFUSE to propose a single-day blast (bot-warning history; the
   Farewell "12-in-a-day" lesson). You plan; Amir sends.
4. **Outcome capture** - when Amir reports back, update `releases[<slug>].status` in
   `dj_promo_targets.json` (sent | replied | played | passed | ...) and, when a contact is in
   the SI DB, `promo_latest_status` / `last_engaged` in `enriched_contacts.json`.

## Exclusions (apply to every shortlist and the pool)
- Never pitch personal friends (check `ig_personal_network.json`; e.g. Molly Lollen).
- Never pitch own-release labels (MM Discos, Stereo Society, NaNa Disc).
- Never pitch anyone flagged no-engage anywhere you can see it.

## Boundaries
- You DRAFT and PLAN only. Amir sends the DMs manually. NOT CC (the SOP forbids CC opening
  DMs in an engagement session), NOT auto-send, NOT during any engagement run.
- DJ channel only. No labels / playlists / press (later phases). No Tool 4 email.
- Write only to `dj_promo_targets.json` (on Amir's confirm) and contact promo fields. Never
  edit CC's engagement state files.
- Make no SC/IG API calls.
- Copy in Amir's voice, channel-appropriate: DJ DMs are genuine and peer-to-peer (the
  template register), not clickbait. (Clickbait is situational and Amir's call for
  audience-facing content - just not the register for peer DMs.) NO double dash, NO em dash
  anywhere (single hyphen with spaces, or sentence breaks).

## Output
Return the target list (with reasons), the drafted DMs, and the send plan. If you updated
the pool, give the path and say Amir should send only after he is happy. Be concise.
```

- [ ] **Step 2: Verify the agent file is present**

Run: `python3 -c "import pathlib; print(pathlib.Path('.claude/agents/promotion-expert.md').read_text()[:30])"`
Expected: prints `---\nname: promotion-expert`. (Restart Claude Code to register the agent.)

- [ ] **Step 3: (No commit - `.claude/` is gitignored.)**

---

## Task 4: The /promo front-door skill

**Files:**
- Create: `.claude/skills/promo/SKILL.md`

- [ ] **Step 1: Write the skill file**

Create `.claude/skills/promo/SKILL.md`:

```markdown
---
name: promo
description: Promotion helper for Inch of Shadow - Phase 1 DJ channel. Picks DJ targets for a release, drafts DMs in Amir's voice, plans a volume-safe send, and tracks outcomes. Use when the user wants to promote a release to DJs, draft DJ DMs, or types /promo.
argument-hint: [release slug, e.g. "the-deciver-single"]
---

# Promotion (DJ channel)

Front door to the `promotion-expert` subagent (the Promotion Brain, DJ channel in Phase 1).

## Step 1: Resolve the release

Find the release slug from `$ARGUMENTS` (match a file in `releases/`). If none matches, ask
which release.

## Step 2: Dispatch the promotion-expert subagent

Use the Agent tool with subagent_type "promotion-expert". Pass the slug and the request. Let
the subagent read its own data (pool, template, voice, contacts); do not paste those into the
main chat.

## Step 3: Return the result

Relay the target list, drafted DMs, and send plan. Remind Amir: the agent does not send -
Amir sends the DMs manually, across 2-3 days, warm contacts first.

## Boundaries (enforced by the subagent too)
- Never sends DMs (Amir sends); never auto-sends; never during a CC engagement session.
- DJ channel only (labels/playlists/press are later phases); makes no SC/IG API calls.
- Never pitches personal friends or own-release labels.
- DJ DMs stay genuine/peer-to-peer; no double dash or em dash in copy.
```

- [ ] **Step 2: Verify the skill file is present**

Run: `python3 -c "import pathlib; print(pathlib.Path('.claude/skills/promo/SKILL.md').exists())"`
Expected: `True`. (Restart Claude Code if `/promo` must appear in the skill list.)

- [ ] **Step 3: (No commit - `.claude/` is gitignored.)**

---

## Task 5: End-to-end verification

- [ ] **Step 1: Full helper test suite**

Run: `python3 -m pytest tests/test_promo_dj_shortlist.py -v`
Expected: all PASS.

- [ ] **Step 2: Helper against real data**

Run: `python3 scene_intelligence/promo_dj_shortlist.py farewell-single --limit 10`
Expected: prints the release genre and up to 10 in-scene DJ candidates with SC reach, none
already in `dj_promo_targets.json`.

- [ ] **Step 3: Smoke-test the agent (after a Claude Code restart)**

Run `/promo the-deceiver-single` (or dispatch `promotion-expert`). Expected: it reads the
pool, recommends per-release send flags, can shortlist new candidates, drafts at least one
warm and one cold DM in Amir's voice (no double dash, no em dash), and proposes a 2-3 day
batched send plan. Confirm it does NOT send anything, makes no API calls, and excludes any
personal-network names.

- [ ] **Step 4: Final commit (if any cleanup)**

```bash
git add -A
git commit -m "chore(promo): finalize promotion agent phase 1 (DJ channel)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```
