---
name: promo
description: Promotion helper for Inch of Shadow - DJ, label, playlist-curator, and press/premiere/radio channels. DJs: DM drafts. Labels: demo-safe hooks as drafts Amir sends himself. Curators: free IG-DM + Groover pitches off the curator DB. Press: feature/review/play pitches + the premiere ladder. Use when the user wants to promote a release to DJs, labels, playlist curators, or press, or types /promo.
argument-hint: [release slug, e.g. "the-deciver-single"]
---

# Promotion (DJ + label + curator + press channels)

Front door to the `promotion-expert` subagent (the Promotion Brain). Four channels; the
subagent picks the channel from the request:
- **DJs** - DM drafts (Amir sends).
- **Labels** - no demo waves for electronic tracks. Song-era label list only, on Amir's call.
- **Curators** - free IG-DM + Groover pitches from the curator DB (category:"curator"); tracks
  adds via curator_check_adds.py. Amir sends/submits manually.
- **Press / Premiere / Radio** - feature/review pitches (press), play/mix requests (radio),
  and the one-at-a-time premiere ladder. Email drafts go to the RM /outreach page and Amir sends each from his own mail (the RM
  Promotion page and its email tool were dropped 2026-11-06), website-only via manual form.
  Shortlist: `promo_press_shortlist.py`.

## Step 1: Resolve the release

Find the release slug from `$ARGUMENTS` (match a file in `releases/`). If none matches, ask
which release.

## Step 1b: Ask Amir first (before any draft)

Ask Amir up to 3 short questions, in one message:
1. Which of these people does he actually know, and how (met at a gig, they played his track,
   a mutual friend)?
2. What does he want from this send (a play, an add, a reply, a first contact)?
3. Anything to avoid or mention?

Pass his answers word for word to the subagent. Never invent a connection he did not name. If he
says "skip", go on without them.

## Step 2: Dispatch the promotion-expert subagent

Use the Agent tool with subagent_type "promotion-expert". Pass the slug and the request. Let
the subagent read its own data (pool, template, voice, contacts); do not paste those into the
main chat.

## Step 3: Return the result

Relay the target list, drafted DMs, and send plan. Remind Amir: the agent does not send -
Amir sends the DMs manually, across 2-3 days, warm contacts first.

## Boundaries (enforced by the subagent too)
- Never sends DMs / emails / submissions (Amir does); never auto-sends; never during a CC
  engagement session.
- Premiere lane is one channel at a time (ladder), never a blast. The only API use is the
  curator add-check (read-only, pre-announced); no SC/IG API calls.
- Never pitches personal friends or own-release labels via the DJ/engagement channels.
- Copy stays genuine/peer-to-peer; no double dash or em dash anywhere.
