# IG Expert Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an `ig-expert` subagent (the IG "Brain") plus a `/ig` front-door skill, a voice-grounding parser for Amir's IG exports, and a curated content-craft reference.

**Architecture:** A thin `/ig` skill dispatches the `ig-expert` subagent, which loads IG doctrine + data in its own context and returns finished work to the main chat. A one-time Python parser distills Amir's IG exports into a voice profile + collaborator list the agent reads. The agent reads CC's engagement results (read-only) and proposes next steps as a reviewed brief, never editing CC's state files.

**Tech Stack:** Python 3.9+ (stdlib only: json, glob, re, argparse, collections), pytest (dev), Claude Code skills + subagents (markdown), Canva MCP, WebSearch.

---

## File Structure

- `scene_intelligence/ig_build_voice_profile.py` — parser: IG exports -> `ig_voice_profile.json` + `ig_collaborators.json`.
- `tests/test_ig_build_voice_profile.py` — pytest tests for the parser.
- `scene_intelligence/ig_voice_profile.json` — generated output (voice corpus + stats).
- `scene_intelligence/ig_collaborators.json` — generated output (ranked credited accounts).
- `.claude/agents/ig-expert.md` — the subagent definition.
- `.claude/skills/ig/SKILL.md` — the front-door skill.
- `plans/ig-content-craft-reference.md` — curated hooks/effects reference (research pass, user-approved).

Note on `tools:` frontmatter for the agent: at build time, confirm the exact Canva MCP tool names with `ToolSearch query "canva"`. To avoid guessing tool-glob support, the agent omits the `tools:` field (inherits all tools) and enforces its boundaries behaviorally in the system prompt. Tightening to an explicit allowlist is a later, optional hardening step.

---

## Task 1: Voice parser — encoding fix + caption collection (TDD)

**Files:**
- Create: `scene_intelligence/ig_build_voice_profile.py`
- Test: `tests/test_ig_build_voice_profile.py`

- [ ] **Step 1: Install pytest (dev tool)**

Run: `python3 -m pip install pytest`
Expected: pytest installs (or "already satisfied").

- [ ] **Step 2: Write the failing test**

Create `tests/test_ig_build_voice_profile.py`:

```python
import json
import scene_intelligence.ig_build_voice_profile as vp


def test_fix_ig_text_decodes_mojibake():
    # IG exports store UTF-8 bytes re-read as latin-1. Build that mojibake reliably.
    original = "\U0001f5a4"  # black-heart emoji
    mojibake = original.encode("utf-8").decode("latin-1")
    assert vp.fix_ig_text(mojibake) == original


def test_fix_ig_text_passes_plain_text():
    assert vp.fix_ig_text("hello world") == "hello world"
    assert vp.fix_ig_text("") == ""


def test_collect_titles_walks_nested_shapes():
    data = {"ig_reels_media": [{"media": [{"title": "reel caption @friend"}]}]}
    out = []
    vp.collect_titles(data, out)
    assert "reel caption @friend" in out


def test_collect_titles_skips_empty():
    out = []
    vp.collect_titles({"title": "   ", "media": [{"title": "real"}]}, out)
    assert out == ["real"]
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python3 -m pytest tests/test_ig_build_voice_profile.py -v`
Expected: FAIL — `ModuleNotFoundError` or `AttributeError` (module/functions not defined).

- [ ] **Step 4: Write minimal implementation**

Create `scene_intelligence/ig_build_voice_profile.py`:

```python
"""Build Amir's IG voice profile + collaborator list from IG data exports.

One-time / refreshable. Reads data/instagram-*/your_instagram_activity and writes
scene_intelligence/ig_voice_profile.json + ig_collaborators.json. Stdlib only.
"""
import json
import glob
import re
import argparse
import collections
import os

EXPORT_GLOB = "data/instagram-*/your_instagram_activity"
OUT_DIR = "scene_intelligence"


def fix_ig_text(s):
    """IG exports store UTF-8 re-decoded as latin-1. Reverse it. Safe on plain text."""
    if not isinstance(s, str) or not s:
        return s or ""
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def collect_titles(obj, out):
    """Recursively collect every non-empty 'title' string value, encoding-fixed."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "title" and isinstance(v, str) and v.strip():
                out.append(fix_ig_text(v))
            else:
                collect_titles(v, out)
    elif isinstance(obj, list):
        for item in obj:
            collect_titles(item, out)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest tests/test_ig_build_voice_profile.py -v`
Expected: PASS (4 passed).

- [ ] **Step 6: Commit**

```bash
git add scene_intelligence/ig_build_voice_profile.py tests/test_ig_build_voice_profile.py
git commit -m "feat(ig): voice parser core - encoding fix + title collection"
```

---

## Task 2: Voice parser — captions, comments, stats, outputs, CLI (TDD)

**Files:**
- Modify: `scene_intelligence/ig_build_voice_profile.py`
- Test: `tests/test_ig_build_voice_profile.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_ig_build_voice_profile.py`:

```python
from pathlib import Path


def _write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj), encoding="utf-8")


def test_load_captions_merges_all_media_files(tmp_path):
    base = tmp_path / "data" / "instagram-test" / "your_instagram_activity"
    _write(base / "media" / "posts_1.json",
           [{"title": "post one @alpha #darkdisco", "media": [{"title": ""}]}])
    _write(base / "media" / "reels.json",
           {"ig_reels_media": [{"media": [{"title": "reel one @beta"}]}]})
    _write(base / "media" / "stories.json",
           {"ig_stories": [{"title": "story one"}]})
    glob_path = str(tmp_path / "data" / "instagram-*" / "your_instagram_activity")
    caps = vp.load_captions(glob_path)
    assert "post one @alpha #darkdisco" in caps
    assert "reel one @beta" in caps
    assert "story one" in caps


def test_load_comment_owners(tmp_path):
    base = tmp_path / "data" / "instagram-test" / "your_instagram_activity"
    _write(base / "comments" / "post_comments_1.json",
           [{"string_map_data": {"Comment": {"value": "fire"},
                                 "Media Owner": {"value": "jonnyknueppel"}}}])
    glob_path = str(tmp_path / "data" / "instagram-*" / "your_instagram_activity")
    owners = vp.load_comment_owners(glob_path)
    assert owners == ["jonnyknueppel"]


def test_build_profile_counts_mentions_hashtags():
    caps = ["hi @alpha @alpha #darkdisco \U0001f5a4", "yo @beta #darkdisco"]
    profile = vp.build_voice_profile(caps)
    assert profile["caption_count"] == 2
    assert profile["top_hashtags"][0][0] == "darkdisco"
    assert profile["emoji_caption_ratio"] > 0
    assert isinstance(profile["captions"], list)


def test_build_collaborators_ranks_mentions_and_owners():
    caps = ["@alpha @alpha @beta"]
    owners = ["alpha", "gamma"]
    collab = vp.build_collaborators(caps, owners)
    handles = [c["handle"] for c in collab["accounts"]]
    assert handles[0] == "alpha"   # most frequent overall
    assert "gamma" in handles
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_ig_build_voice_profile.py -v`
Expected: FAIL — `AttributeError` (load_captions / load_comment_owners / build_voice_profile / build_collaborators not defined).

- [ ] **Step 3: Write the implementation**

Append to `scene_intelligence/ig_build_voice_profile.py`:

```python
MENTION_RE = re.compile(r"@([A-Za-z0-9._]{2,30})")
HASHTAG_RE = re.compile(r"#(\w+)")
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]",
    flags=re.UNICODE,
)


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_captions(export_glob=EXPORT_GLOB):
    """Captions from posts_1.json, reels.json, stories.json across all exports. Deduped."""
    captions = []
    for base in glob.glob(export_glob):
        for name in ("media/posts_1.json", "media/reels.json", "media/stories.json"):
            for path in glob.glob(os.path.join(base, name)):
                collect_titles(_load_json(path), captions)
    seen, out = set(), []
    for c in captions:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def load_comment_owners(export_glob=EXPORT_GLOB):
    """Handles of accounts whose posts Amir commented on (engagement signal)."""
    owners = []
    for base in glob.glob(export_glob):
        for path in glob.glob(os.path.join(base, "comments/post_comments_1.json")):
            for item in _load_json(path):
                smd = item.get("string_map_data", {}) if isinstance(item, dict) else {}
                owner = smd.get("Media Owner", {}).get("value")
                if owner:
                    owners.append(fix_ig_text(owner))
    return owners


def build_voice_profile(captions):
    """Voice corpus + quantitative stats. Tone is interpreted later by the agent."""
    lengths = [len(c) for c in captions]
    hashtags = collections.Counter()
    emoji_captions = 0
    for c in captions:
        hashtags.update(h.lower() for h in HASHTAG_RE.findall(c))
        if EMOJI_RE.search(c):
            emoji_captions += 1
    return {
        "caption_count": len(captions),
        "avg_caption_chars": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        "emoji_caption_ratio": round(emoji_captions / len(captions), 2) if captions else 0,
        "top_hashtags": hashtags.most_common(20),
        "captions": captions,  # raw examples for the agent to read
    }


def build_collaborators(captions, comment_owners):
    """Rank credited accounts: @mentions in captions + accounts Amir comments on."""
    counts = collections.Counter()
    for c in captions:
        counts.update(m.lower() for m in MENTION_RE.findall(c))
    for owner in comment_owners:
        counts[owner.lower()] += 1
    accounts = [{"handle": h, "count": n} for h, n in counts.most_common()]
    return {"accounts": accounts}


def main():
    ap = argparse.ArgumentParser(description="Build IG voice profile + collaborators")
    ap.add_argument("--export-glob", default=EXPORT_GLOB)
    ap.add_argument("--out-dir", default=OUT_DIR)
    args = ap.parse_args()

    captions = load_captions(args.export_glob)
    owners = load_comment_owners(args.export_glob)
    if not captions:
        raise SystemExit("No captions found. Check that IG exports exist under data/instagram-*")

    profile = build_voice_profile(captions)
    collab = build_collaborators(captions, owners)

    vp_path = os.path.join(args.out_dir, "ig_voice_profile.json")
    co_path = os.path.join(args.out_dir, "ig_collaborators.json")
    with open(vp_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    with open(co_path, "w", encoding="utf-8") as f:
        json.dump(collab, f, ensure_ascii=False, indent=2)

    print(f"Wrote {vp_path}: {profile['caption_count']} captions, "
          f"{len(profile['top_hashtags'])} hashtags")
    print(f"Wrote {co_path}: {len(collab['accounts'])} credited accounts")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_ig_build_voice_profile.py -v`
Expected: PASS (all tests).

- [ ] **Step 5: Run against the real exports**

Run: `python3 scene_intelligence/ig_build_voice_profile.py`
Expected: prints caption + account counts; creates `scene_intelligence/ig_voice_profile.json` and `ig_collaborators.json`. Open both and confirm captions are readable (emoji correct) and top accounts include known collaborators (e.g. area_101_x, collective.dada).

- [ ] **Step 6: Commit**

```bash
git add scene_intelligence/ig_build_voice_profile.py tests/test_ig_build_voice_profile.py scene_intelligence/ig_voice_profile.json scene_intelligence/ig_collaborators.json
git commit -m "feat(ig): voice profile + collaborator extraction from IG exports"
```

---

## Task 3: The ig-expert subagent definition

**Files:**
- Create: `.claude/agents/ig-expert.md`

- [ ] **Step 1: Confirm Canva MCP tool names**

Run (in-session, not bash): `ToolSearch query "canva"`
Expected: a list of `mcp__claude_ai_Canva__*` tool names. Note them; the agent will call them for generate/export.

- [ ] **Step 2: Write the agent file**

Create `.claude/agents/ig-expert.md`:

```markdown
---
name: ig-expert
description: Instagram Brain for Inch of Shadow. Plans content, writes captions in Amir's real voice, generates/exports Canva post art, analyzes engagement results, advises on bio/SEO and advanced reach/algorithm tactics, and reviews Amir's photos/frames + hooks. Use when the user wants IG content, captions, post art, engagement analysis, profile/SEO work, reach tips, or content-craft feedback. Does NOT run live engagement (that is CC).
---

You are the Instagram Brain ("Role 3") for Inch of Shadow (Amir, Berlin underground:
dark disco, acid, electro, EBM, techno). You plan and create; you never click.

## Read first, every run
1. `docs/ig-agent-context.md` — strategy, SEO, profile, section 4 role contract.
2. `docs/ig-engagement-sop.md` — hard rules.
3. `plans/ig-engagement-strategy.md` — algorithm / reach / bot-detection research.
4. `scene_intelligence/release_context.json` — the active release.
5. `scene_intelligence/ig_voice_profile.json` — Amir's real captions + voice stats.
   WRITE in this voice; quote real examples as your guide.
6. `scene_intelligence/ig_collaborators.json` — who Amir credits/collaborates with.
7. `plans/ig-content-craft-reference.md` — curated hooks/effects reference (if present).
For analysis tasks also read (read-only): `scene_intelligence/engagement_log.json`,
`ig_target_list.json`, `ig_follow_tracker.json`.

## What you do
1. Content + Canva — captions in Amir's voice + hashtag sets. Generate and export post
   art via the Canva MCP tools (prefer an on-brand Canva brand template/kit if one exists).
2. Strategy + analysis — read CC's result files; report follow-back trends, who to engage
   next, escalation signals. Ground every claim in the data you read; never invent numbers.
3. SEO + profile — bio, profile, cross-platform discovery framing.
4. Reach + algorithm tips — advanced, situation-specific moves sourced from
   plans/ig-engagement-strategy.md. NEVER generic advice (no "post more Reels").
5. Content-craft review — when Amir shares a photo or a video frame plus a hook idea,
   critique that material: first-frame/hook strength, framing, lighting, cut points,
   cover frame, text overlay. Specific to what he shows. You read still images and
   screenshots; you cannot watch a video file — ask for a frame or the cover frame.

## Brain to Hands loop (asymmetric — CRITICAL)
- You READ CC's state files freely (read-only) to ground analysis.
- You NEVER edit CC's state JSONs (engagement_log.json, ig_target_list.json,
  ig_follow_tracker.json, ig_blocked_accounts.json, ig_personal_network.json).
- When you recommend next steps, WRITE them to
  `scene_intelligence/ig_next_session_brief.md` (re-ranked targets + drafted post/art).
  Amir reviews and approves; CC picks up changes only after approval.

## Hard boundaries (the section 4 role contract)
- No live clicking / engagement session — that is CC.
- No DMs, ever.
- Never run IG-API scripts (ig_engagement.py --live, ig_queue_builder.py,
  ig_followback_checker.py, ig_enrich_instagram.py) — respects the two-scripts-a-day rule.
- Copy rules: no double-dash in user-facing copy (single dash with spaces, or new
  sentence). No clickbait / listicle hooks / "POV:" / "wait for it". Cinematic, restrained,
  declarative.
- Never mention "Software Zero Records" in any bio/profile copy.
- Never target for engagement: own-release labels (MM Discos, Stereo Society, NaNa Disc)
  or personal-network friends.
- Genre spelling: "Synthwave" not "Synth".

## Output
Return finished, ready-to-use work (captions, exported Canva asset references, the
analysis, or the brief path). Be concise. State plainly what you did and what is left
for Amir to approve or post.
```

- [ ] **Step 3: Verify the agent file is present**

Run: `python3 -c "import pathlib; print(pathlib.Path('.claude/agents/ig-expert.md').read_text()[:24])"`
Expected: prints `---\nname: ig-expert`. (Restart Claude Code if the agent must appear in the registry.)

- [ ] **Step 4: Commit**

```bash
git add .claude/agents/ig-expert.md
git commit -m "feat(ig): add ig-expert subagent (the IG Brain)"
```

---

## Task 4: The /ig front-door skill

**Files:**
- Create: `.claude/skills/ig/SKILL.md`

- [ ] **Step 1: Write the skill file**

Create `.claude/skills/ig/SKILL.md`:

```markdown
---
name: ig
description: Instagram helper for Inch of Shadow - captions in Amir's voice, Canva post art, engagement analysis, bio/SEO, advanced reach tips, and content-craft review of photos/frames. Use when the user mentions Instagram content, captions, IG post art, reels/hooks, engagement analysis, or profile/SEO work.
argument-hint: [what you want - e.g. "caption for the Farewell reel", "who to engage next", "review this frame", "reach tips for the synth clip"]
---

# Instagram Expert

Front door to the `ig-expert` subagent (the IG Brain). Keeps heavy IG doctrine out of
the main chat by running it in the subagent's own context.

## Step 1: Read the request

`$ARGUMENTS` is what Amir wants. If empty, ask one short question: what IG task today
(caption, post art, engagement analysis, bio/SEO, reach tips, or content-craft review)?

## Step 2: Pre-flight (only if exports were refreshed)

If Amir says he downloaded a new IG export, first run:
`python3 scene_intelligence/ig_build_voice_profile.py`
to refresh the voice profile + collaborators before dispatching.

## Step 3: Dispatch the ig-expert subagent

Use the Agent tool with subagent_type "ig-expert". Pass the full request plus any
material Amir provided (image paths for content-craft review). Let the subagent read its
own doctrine + data files; do not paste those into the main chat.

## Step 4: Return the result

Relay the subagent's finished work to Amir. If it wrote
`scene_intelligence/ig_next_session_brief.md`, tell Amir it is ready for his review and
that CC should only use it after he approves.

## Boundaries (enforced by the subagent too)
- Never triggers a live engagement session (that is CC).
- Never sends DMs, never runs IG-API scripts, never edits CC's state files.
- Obeys all copy/voice/targeting rules in docs/ig-agent-context.md and the SOP.
```

- [ ] **Step 2: Verify the skill file is present**

Run: `python3 -c "import pathlib; print(pathlib.Path('.claude/skills/ig/SKILL.md').exists())"`
Expected: `True`. (Restart Claude Code if `/ig` must appear in the skill list.)

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/ig/SKILL.md
git commit -m "feat(ig): add /ig front-door skill dispatching ig-expert"
```

---

## Task 5: Curated content-craft reference (research pass, user-approved)

**Files:**
- Create: `plans/ig-content-craft-reference.md`

- [ ] **Step 1: Research advanced reel-hook + image/edit techniques**

Use WebSearch / WebFetch to gather CURRENT, advanced techniques for short-form video
hooks and image/edit craft specifically for underground electronic / DJ / producer
content (studio sessions, synth performance, live sets). Focus on: first-frame strategy,
cold-open hooks, motion/cut pacing, on-screen text timing, cover-frame selection,
lighting/color for dark aesthetics. Capture the source URL for each technique. Skip
generic "post consistently" advice — Amir already knows the fundamentals.

- [ ] **Step 2: Draft the reference for Amir's approval**

Draft `plans/ig-content-craft-reference.md` with sections: Hooks (first 3 seconds),
Edit/pacing, Image/photo craft, Cover frames, Text overlays, Dark-aesthetic color/light.
Each item: the technique, why it works, and a source link. Present the draft to Amir and
get explicit approval BEFORE saving (per the spec — user reviews the reference).

- [ ] **Step 3: Save the approved reference**

Write the approved content to `plans/ig-content-craft-reference.md`.

- [ ] **Step 4: Commit**

```bash
git add plans/ig-content-craft-reference.md
git commit -m "docs(ig): add curated content-craft reference for ig-expert"
```

---

## Task 6: End-to-end verification

- [ ] **Step 1: Run the full parser test suite**

Run: `python3 -m pytest tests/test_ig_build_voice_profile.py -v`
Expected: all PASS.

- [ ] **Step 2: Smoke-test the skill to agent path**

In a fresh Claude Code session, run `/ig draft a caption for the Farewell reel in my voice`.
Expected: the `ig-expert` subagent runs, reads the voice profile, returns a caption that
sounds like Amir (no double-dash, no clickbait), with hashtags. Confirm it did NOT open
DMs, run scripts, or edit state files.

- [ ] **Step 3: Smoke-test content-craft review**

Run `/ig review this frame` with a still-image path. Expected: specific feedback on
first-frame/hook, framing, lighting, cut/cover — referencing the reference doc.

- [ ] **Step 4: Final commit (if any cleanup)**

```bash
git add -A
git commit -m "chore(ig): finalize ig-expert agent + /ig skill"
```
