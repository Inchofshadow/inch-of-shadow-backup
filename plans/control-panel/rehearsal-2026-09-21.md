# Rehearsal: the whole chain, run once (Machine-09, 2026-09-21)

Test material: The Deceiver, store-verified cover (`youtube/assets/art/the-deceiver.png`,
3000x3000), 9 seconds of the master from 1:02. Light lane. Everything local and free, no AI,
nothing published. Draft render quality. The work files (the test project
`videos/rehearsal-deceiver/` and the test exports named `*the-deceiver*`) were moved to the
Trash on Amir's word the same day.

## What ran, in order

| # | Object | Tool | Result |
|---|---|---|---|
| 1 | Cover exports | `artwork_resizer.py` | worked, two faults found and fixed (below) |
| 2 | Spotify Canvas, 6 s loop | HyperFrames `-c compositions/canvas.html`, then `video_resizer.py --only spotify` | worked: 1080x1920, 30 fps, no audio, 6.0 s, passed through untouched |
| 3 | Process reel | needs filmed footage | NOT rehearsed, nothing to test without footage |
| 4 | Release reel, two hooks | one HyperFrames project, the first 2 seconds as a variable, `render --batch` | worked: both versions in 25 s; `check` clean, `adherence.py` clean, 5 frames looked at |
| 5 | Reels + Shorts + TikTok files | `video_resizer.py --reel` (new) | worked: three files, picture not re-encoded |
| 6 | Story set | no tool | the pieces fit (one frame made, 36 px = 13 pt, passes), but nobody has designed the three frames |
| 7 | YouTube | `yt_release.py the-deceiver-single` | worked: the step list prints and sees the render and the metadata file on disk |

## Faults found and FIXED in this run

1. **A cover lost its artist name on YouTube sizes.** `artwork_resizer.py` cropped the square
   cover to 16:9, which cut "Inch of Shadow" off the top. It also made twelve profile pictures
   and banners nobody wants from a cover. NEW `--cover`: skips every profile size and keeps
   the WHOLE cover on a blurred, darkened copy of itself for every size that is not square.
   Measured against the live thumbnail of The Deceiver: within 3 levels of 255 per channel, so
   the plain-cover thumbnail can now be made from the cover alone, without a render. Test added.
2. **One reel became seven files.** `video_resizer.py` turned a finished vertical reel into a
   square, a 4:5, a story and a LANDSCAPE crop as well. NEW `--reel`: only the three files of
   "one piece, three platforms" (Formats-04).
3. **Every new video started on the wrong canvas.** `start_video_project.py` left the page
   `hyperframes init` makes: 1920x1080, set in Inter, with brand.css to be pasted in by hand.
   It now writes the first page itself: `--canvas reel` (default 1080x1920), `wide` or
   `square`, brand colours, sizes, safe zone and font already inside. Two tests added; both
   copies of the brand kit carry the same file.
4. **Batch renders failed under the strict flag** because the row's `name` (the output file
   name) was not a declared variable. Rule for every hook project: declare `name` too.
5. **Asset paths inside `compositions/`** must be written from the project root
   (`assets/x.png`), not `../assets/x.png`. It renders either way, but the linter calls it an
   error and the Studio preview would show nothing.
6. `artwork_resizer.py --delete NAME` waits for a typed yes, so it hangs when Claude runs it.
   Not changed: deleting is Amir's. Claude passes no delete commands.

## Gaps that need Amir, not code

**Answered the same day: A and B are decided PER RELEASE** ("I will decide each release"),
both shown to him on sheets now kept in `references/formats/`. Recorded in `docs/brand/formats.md`.

- **A. The cover art WITHOUT type.** The Deceiver's cover has the name and the title inside
  the picture. So the reel showed branding in the first frame (our rule: no branding in the
  first 3 seconds), and a Spotify Canvas is not supposed to carry text either. frame.md already
  says type is a separate layer; the chain needs that layer as a FILE. Proposal: the fixed set
  lists "cover art, no type, 4000x4000" beside the cover. His yes or no.
- **B. The story set has no design.** formats.md says "3 frames, link sticker" and nothing
  more. What the three frames show is a look decision, best made on renders, his eye.
- **C. The process reel** cannot be rehearsed without footage. First real one is the test.
- **D. TikTok's sound.** The three files carry the music. TikTok replaces it with the library
  sound picked in the app; whether the cut stays in sync is still the open question (Machine-04).

## Not rehearsed

Full lane objects 7 to 11 (reveal carousel, face reel, lyric reel, visualizer, pre-save
image), `-q delivery` and 4K renders (draft only here), anything that talks to a platform.
