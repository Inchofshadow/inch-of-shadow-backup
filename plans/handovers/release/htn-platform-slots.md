# 🎵 Release 16: Half the Night EP platform slots (side chat)

Written 2026-11-10. Started from the main EP chat ("Half the Night EP"). Ticket: 🎵 Release 16 "Squeeze the lemon", un-parked for this EP (Amir 11-09: "R16 also add the research there").

## Where things stand

- Verdict table shown to Amir on 11-10. **He picked all four:** SoundCloud header, YouTube channel banner, Spotify artist header (no text), Spotify Canvas.
- Skipped (verdict): Bandcamp header (the BC-11 brand header from 10-21 stays, ~20 visits a month), Facebook / X (not used), Apple artist image (a photo slot) and Apple motion art (editorial only).
- All built locally from the final cover `Releases/Half the Night EP/Artwork & Designs/Half the ngiht EP.jpg`. No AI. The cover was not re-rendered.
- Output: `Releases/Half the Night EP/Artwork & Designs/Platform sizes/Banners/` (7 files)
  - SoundCloud_2480x520_Header A-title / B-art-only
  - YouTube_2560x1440_ChannelBanner A-title / B-art-only (readable content inside the 1546x423 centre)
  - Spotify_2660x1140_ArtistHeader_no-text
  - Spotify_1080x1920_Canvas_8s-loop (H.264, 24 fps, no audio, 4.8 MB) + poster frame
- Round 2 (Amir 11-10 "show me more versions"): 10 more files in the same folder. SC C-moonrise / D-tree / E-minimal, YT C-moonrise / D-framed / E-minimal, Spotify header B-moonrise / C-open-sky, Canvas B-moonrise / C-close (+ poster frames). Script flags `--more` and `--more-canvas`.
- Round 3 (Amir 11-10: "SC is working, Spotify and YouTube working less"; ticks before it: SC A B D E, YT D E, Spotify A C, Canvas A). Hypothesis: the big flat hill fails on the taller formats. Added YT F-sc-look + G-painting, Spotify D-painting + E-sc-look (`--round3`). "Painting" = the final cover with the title painted out using the cover's own sky (copied from right of the title).
- Sky fix 11-10: the first grain measurement caught a star (std 18); the cover's real black is std ~1.4 with sparse specks. `sky()` corrected and ALL files re-rendered, so every version matches the cover's black.
- Pick page (V ticks + notes in page db `ticks`, doc id = card id): https://claude.ai/artifact/VRxmt6BWN62opHfbyxg31h
  - Source: `plans/htn-platform-slots-page/index.html` + `img/` (previews, rebuilt by hand from the outputs)
- Build script: `artwork/edits/htn-noir/build/platform_slots.py` (`--guides` writes safe-zone copies to `artwork/edits/htn-noir/slots/`, `--canvas` renders the loop). Fixed seed, so the same files every run.

## How it is built (for the next release)

- Pieces cut from the final cover: moon + owl (circle mask), title block, the big ivory tree, the two thin trees, one gold star. Lit pixels kept, the black surround fades into a new sky.
- Sky = the cover's warm black (12,11,9) + grain matched to the cover's std. Hill = a new curve filled with the cover's own plum pixels, resampled (no tile seams).
- Specs used:
  - SoundCloud: help centre min 2480x520, 2 MB. No official safe zone, so the art sits right of centre (avatar + name boxes on the left).
  - YouTube: 2560x1440, 1546x423 centre (third-party guides agree; not checked on YouTube's own page).
  - Spotify header: min 2660x1140. Official rules: no text, no release promo, no busy background. Bottom third kept calm (name + buttons).
  - Canvas: 1080x1920, 3-8 s, no audio, under 8 MB (our playbook + formats.md).
- Canvas made with Pillow frames + ffmpeg, not HyperFrames (formats.md names HyperFrames). It's a still-based loop, so a frame script was the shorter path.

## Amir's picks (2026-11-10, "done"; read from page db `ticks`)

- SoundCloud header: A-title, B-art-only, D-tree, E-minimal
- YouTube banner: A-title, B-art-only, D-framed, E-minimal, G-painting (A was missing here until 11-13; page db has it ticked)
- Spotify header: A (no-text), C-open-sky, D-painting, E-sc-look
- Spotify Canvas: A (8s-loop). B moonrise and C close not kept.
- 11-11 (from ⬆ UPLOADS · HTN Symphonic): EP submitted, UPC 708208624645, release Fri 2026-12-11. Spotify header (and the Canvas, which attaches per track) go up once the release shows in Spotify for Artists. The banners carry no date, so nothing changes for the move from 12-04.
- 11-13 (Amir: see picks together; Canvas light + star shine on the BPM, must loop): page v6: "Final round" (his ticks + new loops, a Choose button per card, one per slot, saved in db `final`, doc id = slot g-sc/g-yt/g-sp/g-cv) and "All" (V ticks). New Canvas D-beat-pulse (5.1 MB) and E-beat-shimmer (5.4 MB), `--beat-canvas`: same scene as A, 127 BPM from releases/pinocchio-single.json, 16 beats = 181 frames at 24 fps (plays at 127.3), every motion a function of loop phase so it's seamless. D: moon halo hits every beat (bar 1 strongest), moonlight wash on the trees, one star glints with a gold cross-flare on each off-beat. E: halo swells once per bar, stars sparkle on the sixteenths. Canvas A untouched. Waits on his ticks.
- 11-13 final round so far (db `final`): SoundCloud A, YouTube E, Canvas E. Amir on Canvas: "E but less shimmer stars and flash" -> new F-beat-calm (8 soft sparkles a loop instead of 32, half the flare, `--canvas-f`). Spotify header: "I don't like all, maybe a different direction. D is fine" + a screenshot of a cut-off twig at D's top edge -> fixed in D (patched with the band's own sky, `--spotify-d`). New Spotify directions (Amir: "Yes, show options"): F-wide-moon (moon 1.8x cut by the right edge), G-tree-line (no moon, thin trees as a dim low band, starry sky), H-grain-field (black + grain, one star with flare, red haze below); `--spotify-new`, page ids sp-nf/sp-ng/sp-nh.
- **FINAL (Amir 11-13 "chosen", page db `final`):** SoundCloud header A-title, YouTube banner E-minimal, Spotify header D-painting (twig fixed), Canvas E-beat-shimmer (F not taken). No notes. Spotify header + Canvas go up once the EP shows in Spotify for Artists (release Fri 2026-12-11).
- Several kept per slot = a rotation set; he uploads himself. Nothing live was touched; SoundCloud profile picture unchanged. Unpicked files stay in the folder (no moves without his yes).

## Ticket updates (for the System chat to merge)

- 🎵 Release 16: done (Amir 11-10). Final one-per-slot 11-13: SC A, YT E, Spotify header D, Canvas E-beat-shimmer. Picks: SC A B D E, YT B D E G, Spotify header A C D E, Canvas A. Note: "2026-11-10: verdict done (build SC header, YT banner, Spotify header no-text, Spotify Canvas; skip Bandcamp header, FB/X, Apple). Files in Platform sizes/Banners, pick page VRxmt6BWN62opHfbyxg31h, script artwork/edits/htn-noir/build/platform_slots.py. Amir uploads himself."
- Not done from the original R16 brief (still open there if wanted): the general "world kit" leftovers check as a cover-pipeline step, and back cover / merch / press kit slots.

## Lessons + mistakes (before this chat is deleted, 11-13)

- Mistake: sky grain measured on a patch that held a star (std 18 vs the real ~1.4), so every file came out ~7x grainier and all had to be re-rendered. Measure noise only on a patch checked to be empty.
- Mistake: Spotify D shipped with a cut-off twig at the top edge; Amir caught it. Check all four crop edges for cut-off pieces before showing any crop of the painting.
- Mistake: the handover picks were retyped and missed YouTube A. Copy picks straight from the page db, never from memory.
- Pick page: a "picks only" view where every card is gold makes choosing hard. Once picks pass one per slot, go straight to a final round (one Choose per slot, nothing pre-selected) with notes on every card.
- Pick page: Canvas loops in a 3-column grid are too small to judge. Give every pick page click-to-zoom from the start.
- Canvas: uncapped H.264 came out at 21.6 MB; `-b:v 6500k -maxrate 7000k -bufsize 7000k` keeps 8 s at 1080x1920 around 5 MB. Upscaling cover pieces past ~1.8x goes soft.
- Beat-locked loop recipe (reusable): loop = whole bars (16 beats), frames = round(16 x 60 / BPM x fps), every motion a function of loop phase (kick = instant attack + exp decay, wrapped modulo the loop). Seam check: last frame vs first differs no more than a normal beat hit.
- What worked: building only from the final cover's own pieces (no AI), fixed seed for repeatable files, and new versions that differ in one bold idea each.
