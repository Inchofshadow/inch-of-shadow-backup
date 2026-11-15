# 🎵 Release: Half the Night cover (handover)

Chat: "HTN cover: 90s noir", running 2026-11-04 to 2026-11-09. Written 2026-11-09.

## Where it stands
- Cover FINAL: Amir's Canva version of Layout keep #50 (extra grain). Files: `~/Desktop/Inch of Shadow/Releases/Half the Night EP/Artwork & Designs/` (JPG 3000 px RGB for Symphonic, PNG RGBA, copy of export-902).
- Decisions: `plans/half-the-night-cover-direction-noir.md`. Report: `plans/half-the-night-cover-report/` (artifact https://claude.ai/artifact/JbHFpJ6c6Ptdbf3SSohapG).
- Saved for reuse: Shadow Archive R-022 to R-024 (noir refs, tags 90s-noir / dark-deco / batman-tas); 6 cover elements in Imagine (scope pinocchio-single).
- Not done here: Symphonic upload (🎵 Half the Night EP chat), Fable review (Fable used up this week).

## Ticket updates (for the System chat to merge)

### NEW · 🎸 Studio · "Outside image and video tools: inspect before install" · 🎃 · ⏭️ next
Amir 11-09: before installing anything, understand how each tool would be used, how it connects to the RM, and what we take from it now and for the future. Inspect the repo first.

Status per tool (Claude's read, 11-09):

| Tool | Replaces | Verdict now | Why |
|---|---|---|---|
| HyperFrames | (video) | ✅ have it, use it | Already installed and working; does the HTN campaign videos from the cover layers. |
| darktable | Lightroom | ✅ safe, first candidate | Mature, CLI (`darktable-cli`) for batch grading. Use only if the campaign uses shoot photos: one "Half the Night" style over all of them. |
| Krita | Photoshop (painting) | ✅ safe, not needed now | Mature, PSD layers, frame-by-frame animation. Only for hand-drawn motion (owl wings, stars). |
| GIMP 3 | Photoshop | ✅ safe, fallback | Mature, Python scripting, batch. Fallback for a local cutout of Amir before PhotoCraft is ready. |
| Inkscape | Illustrator | ✅ safe, not needed now | Mature, CLI. For logo / vector type later (Look-02). |
| PhotoCraft (ArtCraft) | Photoshop | ⏸️ wait, re-check in 1-2 months | Early alpha. Best feature mix for us: MCP server + CLI, local Select Subject, layered PSD with editable type. Notes: `plans/research/photocraft-2026-11-09.md`. |
| FilmCraft / EffectCraft (ArtCraft) | Premiere / After Effects | ⏸️ wait | Alpha, not inspected; HyperFrames covers video. |
| Graphite | Photoshop (node graph) | ⏸️ wait | Alpha; closest idea to our live layer pipeline. |

Steps (nothing installed until step 4, and only with Amir's yes; Amir installs apps himself):
1. Inspect each candidate repo (text only, no clone left behind): licence, maintainer, last release, signed Mac build, telemetry, security policy, open issues that matter.
2. Write the job per tool: which pipeline module it serves (cutout, grade, vector, animation), the exact command or MCP call, input/output files.
3. Design the RM connection: one adapter per tool behind a common shape (input file + recipe -> output file), called from the Layout page / Studio pages, results saved back as layers or keeps. Plan for later tools to plug into the same shape.
4. Amir picks what to install; one small trial per tool on real HTN or shoot files.
5. Record what we keep in docs/brand/toolkit.md (few tools, one per job).

### NEW · 🎵 Release · "Squeeze the lemon: use the leftover images" (the world images kit) · 🎃 · 🅿️ parked (Amir 11-09: until it becomes relevant)
Amir 11-09: old generated images can serve the campaign; Claude suggests a leftovers check at the end of every cover, quick picks like the 1c / B round (campaign/ folder, build/campaign_style.py).
Research (text only):
1. Every slot a release image can fill and its size: back cover / inner art, Bandcamp extra images, artist profile images and headers on the streaming platforms, Spotify Canvas, Apple Music motion art, YouTube visual / art track, IG grid and stories, press kit, merch.
2. Which of those slots Amir already uses, and which are empty today.
3. A "world kit" per release: cover + 3-6 leftovers in the cover style, mapped to those slots.
4. How the leftovers check fits the cover pipeline as its last step (and feeds the next release).
5. FIRST, per platform: is it worth it at all? What does each slot actually do for reach or for fans (who sees it, how often, does it move numbers), and which slots to skip. Only slots that earn their place get built.
6. Then, per platform that passes: how to build it smart. Its own composition and safe zones (not a crop of the cover), what moves or not (Canvas loop, motion art), file specs, how it is made from the layers in one pass (one source -> every size, like artwork_resizer / video_resizer), and how it updates when the next release comes.

### NEW · 🎵 Release / 🎸 Studio · follow-ups from the cover report (⏭️ next, 🎃)
- Layout page works for any release and base picture (today HTN only). Own ticket, not during a cover.
- Finish stages: rim light, corners, grain (on early at low, tuned at Finish).
- Studio drawer in the Layout page (Archive, Effects, Fonts, Imagine) + one shared tag list.
- Record new effects (calculated moonlight, grain + shadow on letters, cut line strength, corners) in /effects and new fonts (Barlow, Switzer, Fraunces, CAT Neuzeit Schatten) in /fonts.
- raw_render.py: size option (now fixed 1024 x 1024); check model sizes.
- Fixed keep IDs; Export button on the Layout page; picks page that updates itself.
- ⚙️ LLM system (from the report's LLM section): a cover skill (day-one checks, stages, picks page, honest-opinion step, leftovers step); a structured pick log per round (shown / picked / his words); a fixed self-check before showing any picture (100% zoom, server log, before/after diff); book the Fable review early in the week when a deadline is close.
