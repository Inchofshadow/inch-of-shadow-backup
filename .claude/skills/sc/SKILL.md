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
