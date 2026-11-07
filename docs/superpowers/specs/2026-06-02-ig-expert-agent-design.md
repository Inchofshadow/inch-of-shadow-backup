# IG Expert Agent — Design Spec

**Date:** 2026-06-02
**Status:** Approved (brainstorming), pending implementation plan

## Goal

A single Instagram helper for Inch of Shadow that plans content, writes captions in
Amir's real voice, makes and exports post art via Canva, analyzes engagement results,
and gives advanced reach/algorithm tips. It is the "Brain" (Role 3 in
`docs/ig-agent-context.md` §4); it never does the live clicking (that stays with CC,
the "Hands").

## Architecture

Hybrid: a thin skill is the front door, a subagent does the heavy work.

```
You type  /ig <request>
              │
              ▼
   thin /ig skill (front door, ~40 lines, lives in main chat)
              │ dispatches
              ▼
   ig-expert subagent  (.claude/agents/ig-expert.md)
     loads in ITS OWN context (keeps main chat clean):
       • docs/ig-agent-context.md          (strategy / SEO / profile)
       • docs/ig-engagement-sop.md         (hard rules)
       • plans/ig-engagement-strategy.md   (algorithm / reach research)
       • scene_intelligence/release_context.json
       • scene_intelligence/ig_voice_profile.json   (built once, see below)
       • scene_intelligence/ig_collaborators.json    (built once, see below)
       • engagement_log.json / ig_target_list.json / ig_follow_tracker.json (read-only)
       • Canva MCP (generate + export designs)
              │
              ▼
   returns finished work to you in the main chat
```

Why hybrid: you get a named trigger (`/ig`) AND the 2,400 lines of IG doctrine load in
the subagent's own context, so they never crowd the main conversation. Matches how
`/discover` and `/enrich` already work.

## Voice grounding (one-time, refreshable)

A grounding pass parses both IG exports in `data/instagram-*` into two small files the
agent reads on every run:

- `scene_intelligence/ig_voice_profile.json` — voice fingerprint distilled from Amir's
  real captions (tone, sentence shapes, emoji habits, sign-offs, hashtag patterns).
- `scene_intelligence/ig_collaborators.json` — accounts Amir credits/tags + venues,
  ranked by frequency, from his own captions and comments.

Honest limit: the export reliably shows Amir's own posts, comments, follows/unfollows,
and who he tags. It does NOT contain a clean "who tagged me" list (that is other
people's data). Collaboration is approximated from outgoing mentions + comments
received; we will not invent reciprocal tags the export lacks.

Refresh: re-run the grounding pass when a new quarterly export is downloaded
(Jan/Apr/Jul/Oct 23rd).

## Capabilities

1. **Content + Canva** — captions in Amir's voice, hashtag sets, and generated/exported
   post artwork via Canva (prefers an on-brand Canva brand template/kit if one exists).
2. **Strategy + analysis** — read engagement results, report follow-back trends, who to
   engage next, when to escalate.
3. **SEO + profile** — bio, profile, cross-platform discovery framing.
4. **Reach + algorithm tips** — advanced, situation-specific exposure moves sourced from
   `plans/ig-engagement-strategy.md`. Never generic ("post more Reels" is banned).
5. **Voice & relationship grounding** — builds/refreshes the two files above.
6. **Content-craft review** — critiques Amir's actual photos / video frames + hook
   ideas: first-frame/hook strength, framing, lighting, cut points, cover frame, text
   overlay. Specific to the material shown, never generic. Backed by a curated reference
   (below). Limit: a text agent reads still images and screenshots but cannot watch a
   video file — Amir supplies a frame or two (or the cover frame) plus the hook idea.

## Brain ↔ Hands loop (asymmetric)

- **Reads freely:** the agent reads CC's result files (`engagement_log.json`,
  `ig_follow_tracker.json`, `ig_target_list.json`) so its advice is grounded in real
  outcomes, not guesses. Read-only file inspection, permitted by §4.
- **Writes only as a reviewed proposal:** the agent does NOT silently edit CC's state
  files. It emits `scene_intelligence/ig_next_session_brief.md` (re-ranked targets +
  the drafted post/Canva art). Amir reviews and approves; CC picks up changes only after
  approval.

This keeps the feedback value while avoiding silent state-file mutation (which has caused
past incidents).

## Boundaries (the §4 role contract — what it will NOT do)

- No live clicking / engagement session — that is CC's job.
- No DMs, ever.
- Never runs IG-API scripts (respects the two-scripts-a-day rule).
- Never directly edits CC's state JSONs — proposal only.
- Obeys all standing rules: no double-dash in copy, no clickbait/listicle hooks, no
  mention of Software Zero, never engage own-release labels (MM Discos, Stereo Society,
  NaNa Disc) or personal-network friends, IG risk caps.

## Components to build

1. `.claude/skills/ig/SKILL.md` — thin front-door skill that dispatches the subagent.
2. `.claude/agents/ig-expert.md` — the subagent definition (doctrine references,
   capabilities, boundaries, output format).
3. Voice-grounding script (e.g. `scene_intelligence/ig_build_voice_profile.py`) — parses
   the IG exports into `ig_voice_profile.json` + `ig_collaborators.json`.
4. Curated content-craft reference (e.g. `plans/ig-content-craft-reference.md`) — built
   ONCE via a web research pass into advanced reel-hook and edit/image techniques for
   underground electronic artists. Amir reviews and approves before it is saved; the
   agent then draws on it for content-craft review. Uses web search only (no data of
   Amir's leaves the machine).

## Out of scope

- Live engagement automation (CC owns it).
- Email outreach, Stats Dashboard, other tools.
