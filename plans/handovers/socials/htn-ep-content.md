# 🎬 Socials: Half the Night EP content run-up

Chat: HTN EP content (side chat of the main EP chat). Started 2026-11-10.

## Where things stand

- 2026-11-11: **EP SUBMITTED to Symphonic** (Uploads chat): UPC 708208624645, release Fri 2026-12-11. Store/TikTok clip starts: Half the Night 2:59, Pinocchio 4:48. These match our `htn-drop` (2:59.6, bar 95) and `pin-drop` (4:48.6, bar 151) clips, so the release reel (D) can reuse the same moment people hear in the stores. Canvas upload opens once the release shows in Spotify for Artists.

- 2026-11-11: **release moved to Fri 2026-12-11** (Amir, Symphonic chat). Plan dates from trial round 1 on moved +7 days (main EP chat asked): round 1 Wed 11-25 to Fri 11-27, read Mon 11-30, round 2 Tue 12-01 to Wed 12-02, grid share Fri 12-04 (only if a trial beat the bar), release reel Fri 12-11, Pinocchio Sun 12-13, final read Mon 12-21. Grid option A dates follow: cover once on 12-11. No video or draft shows a date on screen.

- 2026-11-10: plan `plans/half-the-night-content-plan.md` approved by Amir ("Yes, build it").
- 2026-11-10: **first build done, waiting on Amir's V/X ticks** on https://claude.ai/artifact/WyaAqzsH5oNjpebKhZ92bo (db collection `ticks`, one doc per item id, `{pick: "v"|"x"|null, note}`).
  - 4 trial-reel styles + 1 Canvas, 1080x1920, `-q delivery`: `../videos/htn-ep/renders/` (s1-moon-pulse, s2-through-trees, s3-cover-builds, s4-acid-line, canvas-half-the-night + `_spotify.mp4` 5.8 MB copy).
  - 2026-11-10 Amir "we need to add pinocchio as well": Pinocchio Canvas added (`canvas-pinocchio` + `_spotify.mp4` 6.1 MB), local, style `canvas2` in build.py (acid line breathing, moon pulse at 126 BPM, all periodic so the loop is seamless). On the picks page.
  - 6 clips, 6 bars each, on the draft WAVs: `../videos/htn-ep/clips/` (+ `clips.json` with bar, start, snap offset).
- The platform-slots chat (🎵 Release 16) made its own Canvas: `Releases/Half the Night EP/Artwork & Designs/Platform sizes/Banners/Spotify_1080x1920_Canvas_8s-loop_Half the Night EP.mp4`, ticked on its own page. Only one goes to Spotify; Amir's tick decides.

- 2026-11-10 grid question (Amir): the grid must not show the same cover several times. Option B (three different paintings: b1/b2/c1 from `artwork/edits/htn-noir/campaign/`) previewed on his real grid: `../videos/htn-ep/analysis/grid-option-B.jpg` (script `scripts/grid_preview.py`). Amir: "still don't know, need to finish the other artworks first, at the moment it feels too much". **ON HOLD: nothing built for B, no new artwork work started.** Fallback that needs no new art: option A (cover on the grid once, on 12-11; trials stay trial-only).

## How it is built (all local, no AI)

Project: `videos/htn-ep/` (outside the git repo).
1. `scripts/analyse.py`: per-bar librosa analysis -> `analysis/*.json|png`. Phrases sit on 8-bar lines in both tracks.
2. `scripts/cut_clips.py [--src half-the-night=PATH pinocchio=PATH]`: 6 clips, start snapped to the kick. **On 11-11 re-run with the masters** (check the snap offsets; same arrangement assumed), then `scripts/features.py`, `scripts/build.py`, re-render.
3. `scripts/layers.py`: splits the FINAL 3000 px cover into sky/back/stars/moon/owl/hill/trees/type by colour keys + OpenCV inpaint (hill under the trees). Recomposite error 1.4/255.
4. `scripts/features.py`: per-frame kick/acid/hats envelopes + 303 scope, inlined in each page.
5. `scripts/build.py`: writes `pieces/<id>/index.html` (HyperFrames 0.9.27). Render: `cd pieces/<id> && npx hyperframes@0.9.27 render -q delivery -o ../../renders/<id>.mp4`.
Python deps run via `uv run --no-project --with librosa|opencv-python-headless|scipy|soundfile` (nothing installed into .venv or system).

## Open

- Hook text: none on the reels yet (motion opens). Any hook text = draft, approved by Amir in the main EP chat.
- "PINOCCHIO" credit line under the cover type on s3/s4: needs Amir's OK like any on-screen text.
- Clip labels (acid hook / arp) come from band analysis, not listening.

## Rules for this chat

- Captions and hook text are drafts only. Amir approves them in the main EP chat.
- Never post or schedule anything. No posting reminders.
- No AI on images without his go; show the exact prompt first.
- No paid promotion.

## Ticket updates (for the System chat to merge)

- New 🎬 Socials ticket: "Half the Night EP content run-up (Instagram trial reels + Canvas)". Fields: now/amir · chrome false · next: Amir ticks V/X on the reel picks page; then re-cut on the masters (11-11) and final renders for trial round 1 (11-25).
