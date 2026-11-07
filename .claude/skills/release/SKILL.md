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

**plan** - Read `plans/release-lessons.md` (apply last release's lessons) and
`plans/release-platform-deadlines.md`. Surface the dated to-dos (Spotify pitch T-31/40,
pre-saves at T-14, r/EBM cooldown, grid image prep). Output a tailored plan; don't execute.
Every Instagram part of the plan is checked against `docs/brand/mosseri-guide.md` (before-post
checklist + stop flags) before it is shown (Amir, 2026-11-05).

**prep** - Hand off to the `release-prep` skill for SEO copy, premiere contacts, checklist.
Do not duplicate it.

**YouTube, in every stage (Machine-03, 2026-09-21).** You are his YouTube agent: read
`../youtube/PLAYBOOK.md` sections 5 and 6 first. Then run
`python3 ../youtube/tools/yt_release.py <slug>` (no API calls): it prints the eight YouTube
steps in order, who does each (SCRIPT = you, AMIR = his clicks in Studio) and what is already
on disk. The same eight steps are the "YouTube" group of the release's checklist in the
Release Manager; tick them there as they get done.
- prep: `yt_release.py <slug> --draft` writes the metadata file from the release record with
  `PREMIERE: yes`. Replace its [TODO lines yourself (one sentence on how the track SOUNDS,
  the lead link); `yt_apply.py` refuses a file that still has one. Render the main video.
- after Amir's upload: `yt_apply.py N` dry run, show him the output, then `--apply N` on his
  go; the cover thumbnail the same way. These are API calls: announce them first.
- release_day: read him his own clicks from the step list (Premiere tick, end screen import,
  featured video, playlist row, community post, banner, related video on each Short).
- Decided and not reopened per release: plain cover thumbnail, Premiere yes with no hosted
  chat, no cards. Never upload a video file through the API.

**release_day** - Walk `plans/release-day-playbook.md` Part A in order. Offer the
`ig-expert` agent for the reel/caption + Canva art (on confirm). Track which steps are done.

**capture** - Auto-pull IG stats: pre-announce, then run
`python3 scene_intelligence/ig_fetch_insights.py` (1 + N calls).
HARD RULE first (added 2026-07-05, audit item 21): never two IG scripts on the same day.
Before running the fetch, check whether ANY IG automation ran today (an
`ig_session_<today>.jsonl` exists, or the tracker's `stats.last_session` /
`session_reports.json` shows today, or CC had a session). If yes, defer the fetch to the
next IG-free day - stats can wait, the account cannot. Then ask the artist for
human outcomes in plain words ("Mechatronica replied interested; DJ X played it on SC") and
write them to `releases/<slug>.json` under `outcomes.human` as structured entries
(`who`, `type`, `event`, `sentiment`, `note`, `logged`). Also write pulled stats under
`outcomes.stats`.

**post_mortem** - Run `python3 scene_intelligence/release_status.py <slug> --aggregate`,
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
