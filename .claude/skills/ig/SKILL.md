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
For any post, post plan or campaign: the subagent runs the before-post checklist in
`docs/brand/mosseri-guide.md` and shows the result (Amir, 2026-11-05).

## Step 4: Return the result

Relay the subagent's finished work to Amir. If it wrote
`scene_intelligence/ig_next_session_brief.md`, tell Amir it is ready for his review and
that CC should only use it after he approves.

## Boundaries (enforced by the subagent too)
- Never triggers a live engagement session (that is CC).
- Never sends DMs, never runs IG-API scripts, never edits CC's state files.
- Obeys all copy/voice/targeting rules in docs/ig-agent-context.md and the SOP.
