# SC Expert Agent — Design Spec

**Date:** 2026-06-03
**Status:** Approved (brainstorming), pending implementation plan

## Goal

A `/sc` skill + `sc-expert` subagent — the SoundCloud "Brain" for Inch of Shadow. It owns
own-profile growth: interprets follow-back/targeting data, proposes the unfollow sweep, and
hands a next-session brief to CC (the live operator). The twin of `ig-expert`, minus
content/Canva and minus premieres.

## Why

SoundCloud already has the full Hands-side infrastructure (a CC briefing, an SOP, a
follow-tracker, weekly health reports) but no strategist interpreting it. The latest weekly
report shows an unaddressed problem — follow-back is 4-7% from discovery/release_boost
sources vs 24% from fans — exactly the kind of signal a Brain agent should catch and act on.

## Architecture (approach A: pure markdown, no new code)

```
/sc <request>  ->  sc-expert subagent (the SC Brain)
   reads:  docs/sc-agent-context.md, docs/sc-engagement-sop.md   (strategy + rules)
           scene_intelligence/sc_follow_tracker.json             (201 follows)
           latest docs/reports/sc-weekly-*.md                     (context)
           scene_intelligence/release_context.json                (active release vibe)
   computes follow-back-by-source live from the tracker (no API, no code)
   ->  returns analysis + proposals
   ->  writes scene_intelligence/sc_next_session_brief.md (CC reads after Amir approves)
```

The agent computes the follow-back breakdown itself from the tracker (each entry has
`source` + `followed_back`), so the analysis is always fresh with zero SC API calls and no
new Python. It may also read the latest weekly report for context.

## Capabilities (own-profile growth only)

1. **Follow-back + targeting analysis** — compute follow-back rate by source and month from
   `sc_follow_tracker.json`, flag underperforming sources (e.g. discovery 4-7% vs fan 24%),
   recommend concrete targeting shifts.
2. **Unfollow-sweep proposal** — list follows past their `unfollow_after` that never followed
   back, EXCLUDING own-release labels (MM Discos, Stereo Society, NaNa Disc), personal
   friends, and anything marked `no_longer_engage`/`no_longer_following`. Proposes only.
3. **Next-session brief** — write who to follow next + who to unfollow into
   `scene_intelligence/sc_next_session_brief.md` for CC to act on after Amir approves.

## Brain to Hands loop (asymmetric)

- Reads the tracker + docs freely (read-only).
- Never edits `sc_follow_tracker.json` or other state files.
- Proposes via `sc_next_session_brief.md`; CC acts only after Amir approves. Same model as
  `ig-expert`.

## Boundaries

- No live clicks (follow/unfollow/like) — CC only.
- Approach A makes zero SC API calls. If any future call is needed, pre-announce the count
  and wait (SC API hard rule).
- Never engage or sweep own-release labels or personal friends; never include them in the
  unfollow list.
- Does not own premieres (Promotion agent), bios (`/bio`), or track SEO/descriptions
  (`release-prep`).
- Inherits all standing rules (no double-dash, no Software Zero, genre "Synthwave").

## Components to build

1. `.claude/agents/sc-expert.md` — the subagent definition (gitignored, local-only).
2. `.claude/skills/sc/SKILL.md` — the `/sc` front-door skill (gitignored, local-only).

No new Python, no tests (no code to test — the agent reads existing JSON and computes
simple counts). Verification is functional: dispatch `sc-expert` and confirm it reads the
tracker, produces a correct by-source breakdown, and respects the exclusions.

## Out of scope

- Premiere pitching (Promotion agent).
- Live engagement / clicks (CC).
- Any new analysis script (the agent computes from the tracker directly).
