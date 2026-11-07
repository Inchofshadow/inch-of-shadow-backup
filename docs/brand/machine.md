# Inch of Shadow - The machine: who makes what (Machine-01, 2026-09-20)

One owner per object, so nothing gets made twice and every session reaches for the same
tool. Objects are the fixed set in `formats.md`. Rules for how things look: `frame.md`.
Every session starts from the `brand` skill, which points here.

## Object to tool

| Object | Made with | Checked with | Exported with | By hand (Amir) |
|---|---|---|---|---|
| Cover 4000x4000 | design in Canva or an image from `image_generator.py` (`art`, options per image); photos of him only through `grade`, `composite` or `print_looks.py`, never `restyle` | `shrink_check.py --format cover` | `artwork_resizer.py --cover` (release sizes only; the whole cover kept on every size that is not square; never upscaled) | the final say, the hand-drawn mark, submitting to Symphonic |
| A borrowed look on a photo (S1 to S7) | `print_looks.py` (local, no AI) | by eye on `--sheet` | same file, then `artwork_resizer.py` | picks the look |
| Feed post, carousel, pre-save image | photo from the shoot catalogue (`contact_sheet.py`), type with `pillow_type.py`, or `image_generator.py card --mood` | `shrink_check.py --format post` | `artwork_resizer.py --only instagram` | posting, location, tags |
| Story set | same as a post, 1080x1920 | `shrink_check.py --format reel` (safe zone) | `artwork_resizer.py` | posting, link sticker |
| Reel, Shorts, TikTok file | HyperFrames, started with `start_video_project.py --mood` (writes a 1080x1920 on-brand first page; `--canvas wide` for YouTube); footage pre-cut with `/video-editing`; a reference reel read with `/video-analyze` | `adherence.py`, snapshots looked at frame by frame, `shrink_check.py` | `hyperframes render -q delivery`, then `video_resizer.py --reel` (the three files for Reels, Shorts and TikTok, picture untouched) | filming, choosing the reference, posting, renaming the audio |
| Hook variants for trial reels | the same HyperFrames project, the first 2 seconds as a variable, `--batch` | as above | as above | running the trial reels in the app |
| Lyric reel | HyperFrames `/music-to-video` | as above | as above | the lyrics as text |
| Spotify Canvas | HyperFrames, a seamless 3 to 8 s loop | loop seam by eye | `video_resizer.py --only spotify` | upload in Spotify for Artists |
| The sting | `videos/ios-sting/` (variables: handle, ground, ink). Reused, never rebuilt | done once | `-q delivery`, 1080 and 4K | nothing |
| YouTube visualizer + thumbnail | HyperFrames at 16:9, 4K render; thumbnail by the `brand` skill's thumbnail recipe | `shrink_check.py --format thumb` | `video_resizer.py --only youtube`, `artwork_resizer.py --only youtube` | the upload click |
| YouTube titles, descriptions, tags, schedule, playlists | `youtube/tools/gen_metadata.py` then `yt_apply.py` (read `youtube/PLAYBOOK.md` first) | dry run first | the API | approving the dry run |
| Captions and post text | the `ig` skill, from `voice.md` | copy rules in `voice.md` | none | final wording, posting |
| Bios | the `bio` skill, from `positioning.md` + `proof.md` (PUBLIC STATUS first) | `description_scorer.py` | none | pasting into each platform |
| Release copy, SEO, checklist, timeline | the `release` and `release-prep` skills + Release Manager (`/` and `/board`) | the checklist (category formats, by lane) | none | ticking, deciding |
| Pitches to DJs, curators, press | the `promo` skill | `proof.md` | none | sending every message himself |

## AI image generation or local: the rule

Claude says which one BEFORE every image job, in one line: "local" or "AI, costs money,
needs your go".

| Use | When | Examples |
|---|---|---|
| **Local** (free, nothing leaves the Mac) | the picture already exists, or it is type, colour, a look, a size | any photo of Amir (`grade`, `print_looks.py` S1 to S7, `composite` cuts him out locally), titles and cards, thumbnails from a photo, every resize, every video |
| **AI** (`image_generator.py`, his OpenAI key, paid per image) | the picture does NOT exist and cannot be shot | cover art subjects (roses, statues, a moon), a background to put his cut-out photo on, a texture, concept and mood images, the "subjects" of the style library (Art Nouveau botanical, memento mori, collage) |
| **Never AI** | his face | `restyle` uploads the photo and can drift the face: not for photos of him. AI changes nothing on his face except a surgical removal he asks for |

How to write the prompt, keep it consistent, what it costs and the checklist before each
render: `ai-image-prompting.md` (2026 research). Note: gpt-image-1.5, the tool's current
default, shuts down 2026-12-01; move to gpt-image-2.5 (Flare drafts, Sunburst finals).

How an AI job runs: options chosen per image, `--print-prompt` first (free, shows the exact
prompt), Amir's go, then the render. A generated image can then go through a local look
(`print_looks.py`) so it matches a photo treated the same way.

The ChatGPT app itself stays useful for playing with ideas. To keep those on brand too,
paste the text from `--print-prompt` into ChatGPT: it carries the same core and options.
What comes out is a reference to show, not a final asset, until it has been checked against
`frame.md` (no text in the image, one light idea, no invented people).

## What Canva is for

Amir's own hands: drawing the mark, quick one-off designs, things he wants to make himself.
The connector can read his Brand Kit and create designs from it, but it CANNOT edit the
Brand Kit (checked 2026-09-20: no such tool). The kit is set by hand once, from
`canva-setup.md`. Nothing in the pipeline above depends on Canva.

## What always stays by hand

Filming and photos. Choosing references. The mark's final art. Writing A Letter for
Listeners. Every upload, post and send. Every paid render (AI image generation) needs his
go first. Anything that moves, renames or deletes his files.

## YouTube, wired into a release (Machine-03, 2026-09-21)

`python3 ../youtube/tools/yt_release.py <slug>` prints the eight YouTube steps of a release in
order, who does each, and what is already on disk; `--draft` writes the metadata file from
the release record. No API calls. The same eight steps are the "YouTube" group in the
Release Manager checklist of every release that has a lane.

| Step | Who |
|---|---|
| Main video rendered in 4K (drop: cover video; song: visualizer) | script |
| File dragged into Studio, no metadata, not published | **Amir** (the API would lock it private) |
| Title, description, tags, playlists (`yt_apply.py`, dry run first) | script, announced first |
| Plain cover thumbnail (`yt_thumbnails.py`, dry run first) | script, announced first |
| Schedule + "Set as Premiere" | **Amir** (the API has no Premiere setting) |
| End screen: Import from video | **Amir** (not part of any API) |
| Release day on the channel: featured video, playlist row, community post, banner | **Amir** |
| Related video on each Short | **Amir** |

## Tools that are out of date (do not use as they are)

- `youtube/tools/make_thumbnails.py`: still Cinzel capitals with Cormorant artist lines at
  1280x720. Since 2026-09-21 the thumbnail is the PLAIN COVER on every video, songs included
  (Formats-03, `youtube/PLAYBOOK.md` section 6), so nothing needs this script. The title-only
  design is parked for a Test & Compare with Amir's OK; rebuild the script only then.
- `image_generator.py grade`: its colour ramp is the electronic-era oxblood grade. The grade
  for the songs is board ticket Look-09. `print_looks.py` is the decided path for looks.
- `palettes/oxblood|cold|sepia`: electronic-era prompt colours, optional, never automatic.
- `videos/IOS-*.md`: electronic-era video rules, replaced by `motion-library.md`,
  `formats.md` and `reel-craft.md` (the old files are untouched, Formats-02 is parked).
