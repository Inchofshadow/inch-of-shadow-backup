# 🎵 Release: Half the Night EP handover

Chat: main Release chat for the Half the Night EP (lead Half the Night, track 2 Pinocchio; release slug `pinocchio-single`). Written 2026-11-05.
Role (Amir, 2026-11-05): this chat is the master of the EP and talks only about the main release things (decisions, release file, export, Symphonic, dates, pitch). Cover detail lives in the noir chat; its news is not relayed here.
Side chat that stays open: **HTN cover: 90s noir direction** (local_e995e310), the ONE working chat for the cover. Cut-paper, Polish and Burton chats are finished; their results are in their direction notes (below) and on noir's summary boards.

## Where things stand

- Tags: done and locked (2026-11-03) in `releases/pinocchio-single.json`. Symphonic genre Electronic / subgenre Dark Disco on both tracks, both instrumental. Spotify moods ominous, nocturnal, hypnotic, psychedelic, driving. SoundCloud genre Dark Disco + tags electro, dark disco, acid, EBM, italo disco, Berlin. Bandcamp tags lead with darkwave (the bridge to the future songs). Never-list in `tag_rules`.
- Cover: the language is found (90s noir / dark deco, poster-like, minimal, 3 colours). The work goes on in the noir chat:
  - effects wall at RM `/playground/pinocchio-single/wall` (port 5001, checked 200 on 11-05)
  - 14 covers (1a / 1c, with and without the tree), colour switch (original, Moonlit wall, two old R. Missing)
  - title size slider, his kept pick S21 Pixel sort on 1a owl moon + stars
  - searchlight-moon idea also logged in noir
- 2026-11-06 late (noir, commit 081126b): the lead direction is ivory trees (#25 / #33 family), with #13 as the fallback. The cover is PAUSED until the font is solved. The purple's exact shade is still open.
- 2026-11-05 Amir: **1a is the main artwork**; 1c is kept for the campaign later.
- Noir's next step (waiting for Amir): pick 1-2 covers with Wet at 0% first, then effects on those only.
- Symphonic: Amir logged in on 11-03, form read, nothing saved (no draft, no UPC). Submit this week once the cover is final.

## Decisions made

- One EP, both tracks for every platform; Beatport not used.
- Darkwave goes in the free-text tag fields only (Symphonic has no Darkwave); dark electro, alternative dance and indie dance are out.
- Cover: no photo of him, no face, mostly graphic; R. Missing palette (dark purple + ivory/blonde), coloured by role, applied last and locally; both names on the cover; record/vinyl concept out.
- Workflow: talk design first, then short raw prompts (`artwork/edits/half-the-night-build/raw_render.py`, medium quality, unique filenames), then he picks elements, then Canva, then I suggest effects, then colour/type/export.

## Open decisions (Amir)

- Pick the cover (noir chat).
- Commit noir's playground + wall files (noir asked). See "Not committed yet".
- Release date on Symphonic: about 3-4 weeks out so the Spotify pitch fits; Holiday banner: submit by Nov 6 to go live Nov 27 to Dec 4.
- Spotify pitch dropdown: read it on the day after delivery (want darkwave / cold wave if offered).

## Pre-warm (note from ⚙️ System, 2026-11-06)

- When the pre-warm starts, set `slug` by hand in `scene_intelligence/release_context.json` (null since 2026-08-15). Also add the campaign to `promotion_log.json`, or the IG promo lane stays off. The RM page that used to set it is gone until RM 2.0 slice 1.

## After the cover is final (back in this chat)

1. Fable second-opinion reminder.
2. 4000 px master via `artwork_resizer.py --cover`; type set by us.
3. Release file brand block + artwork path.
4. Symphonic submission (Amir clicks submit).
5. End-of-artwork summary with Amir (OPEN in `plans/half-the-night-cover-v2.md`).

## Key files

- `releases/pinocchio-single.json` (backup `releases/pinocchio-single.bak.20261103_tags.json`)
- `plans/symphonic-genre-list-2026-11-03.md`
- `plans/half-the-night-cover-v2.md`: the 11-03 history, lessons, process (main chat)
- `plans/half-the-night-cover-direction-noir.md`: the live log (to 11-04 ~20:16), plus `-cutpaper.md`, `-polish.md`, `-burton.md`
- `plans/genre-cover-board-2026-11-03.md` + `artwork/edits/half-the-night-board-genre-kept.jpg`
- `artwork/edits/htn-noir/` (`playground-covers/pinocchio-single/` has 104 files, plus `reference/`, `rmissing-roles/`), `htn-cutpaper/summary-board.jpg`, `htn-polish/htn-polish-summary-board.jpg`
- `artwork/edits/half-the-night-build/` (42 build scripts and prompts), `refs-amir/`
- RM: `release_manager/playground.py` (WALL_PICKS), `templates/playground_wall.html`, `plans/playground-wall/pinocchio-single.json` (kept picks)
- Shadow Archive R-020 (R. Missing study), R-012 (Chateau Royal)
- Side pages: noir picks https://claude.ai/artifact/ApLxqSzWFAz8Renc7iMbi9, sketch pad https://claude.ai/artifact/Aa1kPEqPHy75KpLPAFoKdX

## Not committed yet (checked 2026-11-05, git status)

- `plans/half-the-night-cover-direction-noir.md`, `release_manager/templates/playground_wall.html`, `plans/playground-wall/` (new), `releases/pinocchio-single.json` (the tags), its `.bak.20261103_tags.json`.
- The RM chat already committed 2 of noir's small changes. The files are all on disk and the RM wall runs, so nothing is lost. Committing them is Amir's yes (noir is asking).

## Side chats: merged back?

- Cut-paper, Polish: yes. Each has a full direction note with Amir's sum-up, and both summary boards are in noir.
- Cut-paper chat deleted by Amir 2026-11-05; its files stay. Kept in mind (Amir): some cut-paper elements may be used for a side thing for posting, not decided ("let's see"). Source: `artwork/edits/htn-cutpaper/` (53 files incl. summary-board.jpg) + `plans/half-the-night-cover-direction-cutpaper.md`.
- Burton: yes, low priority (note + 11 files).
- Noir: its note is current to 11-04 ~20:16. Its latest round plan ("pick the cover at Wet 0% first, then effects") and its commit question live only in the noir chat for now. Noir keeps its own note; it stays open.

## Tickets touched

- 🎵 Release 1: metadata + artwork brief (approved)
- 🎵 Release 2: artwork FINAL before Symphonic submit (proposed, the live one)
- 📱 Socials 14: Bandcamp Friday Nov 6 / Half the Night (`plans/bc06-nov6-half-the-night.md`), related only

## Ticket updates (for the System chat to merge)

- 🎵 Release 1: note "tags done and locked 2026-11-03 (Electronic / Dark Disco, darkwave in free-text fields, instrumental); see releases/pinocchio-single.json platform_tags".
- 🎵 Release 2: status in-progress; note "language = 90s noir / dark deco; working chat = HTN cover: 90s noir direction; effects wall live in RM; next = Amir picks 1-2 covers at Wet 0%".
### Priority fields (board rule 2026-11-05)

- 1 next/claude · chrome false · EP metadata · next: add final artwork path + brand block to the release file once the cover is final (tags done).
- 2 now/amir · chrome false · HTN cover · next: Amir picks effects on 1a (main) on the RM wall in the noir chat; then type + 4000 px export.
- 9 now/amir · chrome true · Symphonic submit · next: Amir picks the release date (3-4 weeks out), then submit in Symphonic once 🎵 Release 2 is final.
- 3 parked/amir · chrome false · Spotify curator list · next: Amir sends seed artists (3 sizes x 2 lanes), then one refresh pass.
- 4 parked/claude · chrome false · Cover-song licensing · next: check Symphonic Starter cover-licensing route before the 2027 plan.
- 5 parked/amir · chrome false · Downtempo grouping · next: Amir decides how The Piper, In My Dream and others group.
- 6 parked/claude · chrome false · Song-era label list · next: draft the label list + demo spec when the songs lane opens.

- (Merged as 🎵 Release 9) New 🎵 Release ticket: "Half the Night EP: Symphonic submit + release date + Spotify pitch dropdown read", waiting on 🎵 Release 2.

## Inbox from Amir via ⚙️ System (2026-11-05)
Playground wall UI feedback, pasted into the wrong chat; screenshots saved here so he does not retake them:
- `plans/handovers/release/inbox/htn-playground-ui-2026-11-05-1.webp`: the wall. The thumbnail strip hugs the left edge; the whole right side is empty ("why is the UI not using all this space?").
- `plans/handovers/release/inbox/htn-playground-ui-2026-11-05-2.webp`: the Title / Name / Elements panel is too wide (font chips overflow, horizontal scrollbar).
His words: "why ui not using all this space!? image 2 is too wide".
- Handled 2026-11-05 by the noir cover session, on the Layout page (/playground/pinocchio-single/layout):
  - no width cap; the colour saves fill all the free space beside the picture (column count picked for the biggest thumbnails)
  - the font cards wrap into rows instead of scrolling sideways; no panel overflows at 1280, 1800 or 2400 px
