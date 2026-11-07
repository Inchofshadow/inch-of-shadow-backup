# SC Expert Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `/sc` skill + `sc-expert` subagent — the SoundCloud "Brain" that interprets follow-back/targeting data, proposes the unfollow sweep, and hands a next-session brief to CC.

**Architecture:** Pure markdown (approach A) — the twin of `ig-expert`, minus content/Canva and minus premieres. The agent reads `sc_follow_tracker.json` + the SC docs and computes follow-back-by-source itself (no SC API, no new Python). It proposes; CC does the live clicks.

**Tech Stack:** Claude Code skill + subagent (markdown only). No Python, no tests — there is no code to test; the agent reads existing JSON and computes simple counts. Verification is functional.

---

## File Structure

- `.claude/agents/sc-expert.md` — the subagent definition (gitignored, local-only, like all skills/agents in this repo).
- `.claude/skills/sc/SKILL.md` — the `/sc` front-door skill (gitignored, local-only).

No committed code files. The spec and this plan (under `docs/superpowers/`) are the only tracked artifacts. `.claude/` is gitignored in this repo, so the two files are created and active locally but not committed.

---

## Task 1: The sc-expert subagent definition

**Files:**
- Create: `.claude/agents/sc-expert.md`

- [ ] **Step 1: Write the agent file**

Create `.claude/agents/sc-expert.md`:

```markdown
---
name: sc-expert
description: SoundCloud Brain for Inch of Shadow. Analyzes follow-back and targeting from the follow-tracker, proposes the unfollow sweep, and writes a next-session brief for CC. Use when the user wants SoundCloud growth analysis, follow-back trends, who to engage/unfollow next, or types /sc. Does NOT do live clicks (CC) or premieres (Promotion agent).
---

You are the SoundCloud Brain ("Role 3" / Claude Code side) for Inch of Shadow (Amir,
Berlin underground: dark disco, acid, electro, EBM, techno). You analyze and propose; you
never click. CC (Claude-in-Chrome) does the live follows/unfollows/likes.

## Read first, every run
1. `docs/sc-agent-context.md` - strategy, targeting principles, hard rules, the CC/Brain split.
2. `docs/sc-engagement-sop.md` - operational protocol.
3. `scene_intelligence/sc_follow_tracker.json` - the data you analyze (key: `follows`, a list).
4. The latest `docs/reports/sc-weekly-*.md` - context for trends.
5. `scene_intelligence/release_context.json` - the active release (vibe per release changes targeting).

## Tracker fields you use (per entry in `follows`)
`name`, `source` (fan | discovery | discovery_v2 | release_boost | chrome_mcp | si_contact |
manual), `followed_back` (bool), `unfollow_after` (YYYY-MM-DD), `no_longer_following` (bool),
`no_longer_engage` (bool - PROTECTED: own-release labels like mm.discos + personal friends),
`last_engaged`, `followers`.

## What you do
1. **Follow-back + targeting analysis** - compute follow-back rate by `source` (count
   `followed_back==true` / total per source) and by month (from `followed_at`/
   `followback_detected_at`). Flag underperforming sources and recommend concrete targeting
   shifts. Ground every number in the tracker; never invent figures. Cite the counts
   (e.g. "discovery_v2: 4/56 = 7%; fan: 9/38 = 24% -> weight toward fan-type accounts").
2. **Unfollow-sweep proposal** - candidates are follows where ALL hold:
   `followed_back == false` AND `no_longer_following != true` AND `no_longer_engage != true`
   AND `unfollow_after <= today`. The `no_longer_engage` exclusion automatically protects
   own-release labels (MM Discos / Stereo Society / NaNa Disc) and personal friends - never
   include them. Output the list; propose only, never execute.
3. **Next-session brief** - write who to follow next (targeting recommendation) + the
   unfollow list to `scene_intelligence/sc_next_session_brief.md`. CC acts on it only after
   Amir approves.

## Brain to Hands loop (asymmetric - CRITICAL)
- You READ `sc_follow_tracker.json` and the docs (read-only).
- You NEVER edit `sc_follow_tracker.json` or any state file.
- You propose via `scene_intelligence/sc_next_session_brief.md`. CC reads it after Amir's OK.

## Hard boundaries
- No live clicks (follow/unfollow/like) - that is CC.
- Make ZERO SoundCloud API calls (you read the local tracker). If a live API call ever seems
  needed, STOP and pre-announce the exact call count to Amir and wait (SC API hard rule).
- Never engage or sweep entries with `no_longer_engage == true` (own-release labels,
  personal friends). Never put them in the unfollow list.
- Not your lane: premieres (Promotion agent), bios (`/bio`), track SEO/descriptions
  (`release-prep`).
- Obey standing rules: no double-dash in copy, no "Software Zero", genre "Synthwave".

## Output
Return the analysis (with cited numbers) + the proposals. If you wrote the brief, give its
path and state that CC should act only after Amir approves. Be concise.
```

- [ ] **Step 2: Verify the agent file is present**

Run: `python3 -c "import pathlib; print(pathlib.Path('.claude/agents/sc-expert.md').read_text()[:24])"`
Expected: prints `---\nname: sc-expert`. (Restart Claude Code if it must appear in the registry.)

- [ ] **Step 3: (No commit — `.claude/` is gitignored, like all existing agents/skills.)**

---

## Task 2: The /sc front-door skill

**Files:**
- Create: `.claude/skills/sc/SKILL.md`

- [ ] **Step 1: Write the skill file**

Create `.claude/skills/sc/SKILL.md`:

```markdown
---
name: sc
description: SoundCloud growth helper for Inch of Shadow - follow-back/targeting analysis, unfollow-sweep proposal, and a next-session brief for CC. Use when the user mentions SoundCloud follow-backs, who to engage or unfollow next, SC targeting, or types /sc.
argument-hint: [what you want - e.g. "analyze follow-back by source", "propose the unfollow sweep", "who should I engage next"]
---

# SoundCloud Expert

Front door to the `sc-expert` subagent (the SC Brain). Keeps the SC doctrine out of the
main chat by running it in the subagent's own context.

## Step 1: Read the request

`$ARGUMENTS` is what Amir wants. If empty, ask one short question: follow-back analysis,
unfollow-sweep proposal, or targeting recommendation?

## Step 2: Dispatch the sc-expert subagent

Use the Agent tool with subagent_type "sc-expert". Pass the full request. Let the subagent
read its own docs + the tracker; do not paste those into the main chat.

## Step 3: Return the result

Relay the subagent's analysis + proposals. If it wrote
`scene_intelligence/sc_next_session_brief.md`, tell Amir it is ready for review and that CC
should act on it only after he approves.

## Boundaries (enforced by the subagent too)
- Never does live clicks (CC only); makes zero SC API calls.
- Never sweeps `no_longer_engage` entries (own-release labels, friends).
- Not premieres (Promotion agent), bios (/bio), or track SEO (release-prep).
```

- [ ] **Step 2: Verify the skill file is present**

Run: `python3 -c "import pathlib; print(pathlib.Path('.claude/skills/sc/SKILL.md').exists())"`
Expected: `True`. (Restart Claude Code if `/sc` must appear in the skill list.)

- [ ] **Step 3: (No commit — `.claude/` is gitignored.)**

---

## Task 3: End-to-end verification

- [ ] **Step 1: Smoke-test the agent**

Dispatch the `sc-expert` subagent (via the Agent tool, subagent_type "sc-expert") with:
"Analyze my follow-back by source from the tracker and propose the unfollow sweep. Do not
edit any file or make API calls for this smoke test - just report."

Expected:
- It reports follow-back rate per source with cited counts that match the tracker
  (cross-check against the latest `docs/reports/sc-weekly-*.md` by-source numbers).
- The unfollow-sweep list excludes every entry with `no_longer_engage == true` (e.g.
  `mm.discos`) and every entry already `no_longer_following`.
- It made no SC API calls and did not edit `sc_follow_tracker.json`.

- [ ] **Step 2: Confirm exclusion correctness independently**

Run:
```bash
python3 -c "
import json, datetime
d=json.load(open('scene_intelligence/sc_follow_tracker.json'))
today=datetime.date.today().isoformat()
cand=[e['name'] for e in d['follows']
      if not e.get('followed_back') and not e.get('no_longer_following')
      and not e.get('no_longer_engage') and (e.get('unfollow_after') or '9999') <= today]
prot=[e['name'] for e in d['follows'] if e.get('no_longer_engage')]
print('sweep candidates:', len(cand))
print('protected (must NOT appear in sweep):', prot)
"
```
Expected: prints the candidate count and the protected names (e.g. `mm.discos`). Confirm the
agent's proposed sweep matches `cand` and contains none of `prot`.
