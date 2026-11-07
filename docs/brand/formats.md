# Inch of Shadow - Formats: the fixed set per single (Formats-01, decided 2026-09-20)

What always gets made for a release, so each single is a checklist and not a debate.
Approved by Amir 2026-09-20 ("for now, keep everything"). How each object looks: `frame.md`.
How it moves: `motion-library.md`. The same list lives in the Release Manager checklist
(category "formats"), driven by the release's `lane`.

## Two lanes (bridge plan v2)

- **LIGHT** = electronic drops (Half the Night EP, date open). Objects 1 to 6.
- **FULL** = songs. Objects 1 to 11.

## The set

| # | Object | Canvas | Made with | When | Lane |
|---|---|---|---|---|---|
| 1 | Cover | 4000x4000 JPEG sRGB | design, then `artwork_resizer.py` for every platform size | final before the first submission | light |
| 2 | Spotify Canvas | 1080x1920, 3 to 8 s seamless loop, no audio | HyperFrames, then `video_resizer.py --only spotify` | with the release | light |
| 3 | Process reel | 1080x1920 | footage + HyperFrames | about T-4 days | light |
| 4 | Release reel with 2 to 3 tested hooks | 1080x1920 | HyperFrames, the first 2 seconds as a variable, batch render; run as trial reels, the winner goes out | trial from T-14, winner on release day | light |
| 5 | YouTube Shorts of 3 and 4 | the same files, passed through, no re-encode | `video_resizer.py --only youtube` | same days | light |
| 6 | Release-day story set | 1080x1920, 3 frames, link sticker | image tool / Canva / HyperFrames | release day | light |
| 7 | Reveal carousel, face on slide 3 | 1080x1440 (3:4 fills the grid tile) | photos + `artwork_resizer.py` | about T-2 days | full |
| 8 | Face or performance reel (singing or playing, no talking) | 1080x1920 | footage + HyperFrames | release week | full |
| 9 | Lyric reel | 1080x1920 | HyperFrames (`music-to-video`), title arrivals T1 to T4 line by line | release +2 days | full |
| 10 | YouTube visualizer, full song | 3840x2160, thumbnail = the plain cover like the 11 (Amir, 2026-09-21; title only is parked) | HyperFrames `-q delivery --resolution landscape-4k` | release day | full |
| 11 | Pre-save image | story 1080x1920 + post 1080x1440 | image tool / Canva | T-14 days | full |

TikTok is not an object of its own: it takes the files of 3, 4, 8 and 9 as they are. See
"TikTok" below (Formats-04).

## Why these (Amir's own numbers, not theory)

Baseline only (Amir, 2026-09-20): these numbers are from the electronic era, when he shared
little, with content made before the AI tools. They explain why the set starts this way.
The set gets reviewed after the first song is released, on real songs-era data.

- **Reels find new people, carousels feed the base.** Deceiver reels reached 55 to 62%
  non-followers; the reveal carousel reached 98% followers but drew 21 comments on 162 reach.
- **Process beats announcement.** The mixing reel reached 455, the release reel 341.
- **The face beats the art.** His portrait slide out-liked both statues.
- **The ceiling is the first 2 seconds.** About 65% of viewers gone by 0:02, skip rate 75%,
  on all three Deceiver pieces. Hence one build with swapped hooks, tested before release.
- **0 follows from 336 and 140 reached.** Formats alone do not fix that; the profile's first
  impression is its own job.
- **Farewell had no pre-save.** Hence object 11.
- **No own data yet** for Canvas, visualizers, Shorts or TikTok. Objects 2, 5 and 10 start it.
  Until then, the Shorts reference numbers (added 2026-10-06, from the Social Media Skills
  research in `research/social-media-skills-mined-2026-10-06.md`): aim for 70-75% average
  viewed; lengths work at two sizes, under 30 s for completion or 50-60 s for total views;
  3-7 a week; the first 30-60 minutes after posting decide the spread; a Short is
  deprioritised after about 28-30 days; an AI-made Short needs YouTube's "Altered Content"
  disclosure; over 1 minute carries Content ID risk. Replace with our own numbers once
  object 5 has data.

## A system, not twenty designs (from Amir's reference 33, 2026-09-21)

He sent Sacred Bones Records, and it is not a cover, it is a **template the whole label runs
on**: one typeface (Sabon), a fixed slot order (artist name bold, "an LP recorded in 20XX",
title in italics, then the track listing), and the variation comes only from ink colour,
illustration and background. Where the template does not fit, a small coloured frame carries
just the artist name and the catalogue number. The label names its own sources as Factory,
4AD, Penguin Books and classical music layouts.

That answers a question this file did not: **how twenty releases look like one artist.**
The set above says WHAT gets made each time; a template of this kind would fix WHERE the
words sit on the cover, so the art can change completely and the shelf still reads as one
body of work.

**A second one, reference 37 (2026-09-21): Rizohm Events**, an electronic series in Treviso.
Same structure, one plain face (Neue Haas Grotesk) for all the information and the imagery
changing per edition, plus two things Sacred Bones does not have: a HAND-MADE wordmark next
to the bought face, and a symbol kept separate from the wordmark so either works alone. That
is close to what is already planned here: his hand-drawn mark (Look-02) beside a bought face.
https://fontsinuse.com/uses/79673

Not decided, and not Claude's to decide: whether Inch of Shadow wants a fixed cover template
at all. It is a real choice with a cost, because it rules out a cover that wants its own
layout. Raised here so it is not lost. Reference:
https://fontsinuse.com/uses/15851

## TikTok (Formats-04, Amir 2026-09-21)

**Decided**
- **One rhythm for all three.** 2 to 3 pieces a week, in parallel with Instagram and with
  some of them as YouTube Shorts. His words: "everything should sync and align". So a piece
  is made once and goes out on Instagram Reels, TikTok and Shorts together, as clean files
  with no other app's watermark (a watermark makes a clip ineligible for TikTok's For You feed).
- **The sound:** on TikTok always his track picked from the sound library in the app, 60
  seconds at most. Music baked into the file earns nothing and gives no link to the song.
  How a beat-cut render stays in sync with the in-app sound is still open (Machine-04).
- **Never:** dances, trend challenges, lip-sync to other people's sounds, talking about what
  a song means, reposts that show another app's watermark. Same person as on Instagram.

**Not decided: formats made only for TikTok.** Amir: "I don't know yet." The menu that was
put to him, all wordless, kept here so it is not invented again:
1. Performance at one strong spot, one take (TikTok's own artist page suggests this).
2. Process, no talking, text for muted viewers; tagged #BehindTheSong it can sit on the
   song's sound page.
3. Lyric clip: a line or two on screen (about 30% watch muted, TikTok's own figure).
4. Photo carousel from the shoot with the song playing (how carousels rank is unknown).
He raises this when he wants to; until then TikTok gets the shared pieces only.

Source for every fact: `plans/platform-algorithm-research-tiktok.md`.

## Decided per release, not once (Amir, 2026-09-21)

Two questions from the rehearsal (`plans/control-panel/rehearsal-2026-09-21.md`) are his
call for EACH release, not a rule. Ask him at the start of every release; do not assume.

- **Cover art without text.** Whether the release gets a second cover file with no type in
  the picture, so the reel's first frame and the Spotify Canvas show only the image. When he
  wants it, the file is saved from the cover's design BEFORE the type goes on, not painted
  out afterwards. Picture of the difference: `references/formats/cover-art-with-and-without-type.jpg`.
- **The story set (object 6).** Which three frames. Two starting points, both shown on
  `references/formats/story-sets-a-and-b.jpg`:
  - **A, the cover leads:** cover + "Out now", him + the title, cover + the link sticker.
  - **B, he leads:** him and nothing else, cover + the title, a plain card + the link sticker.
  Mixing them is allowed. On any frame with one of her photos: `📸@shirzilber.art` (Instagram).
  Type never on his face.

## Left out on purpose

- "Story behind the track" talking reels. He does not explain the songs and rarely talks
  on camera.
- A logo or title opening any video. The hook opens, the name closes (the sting).
- More than one text effect per video.

## Rules every object follows

- Sizes, type, colour mood, safe zones, face rules: `frame.md`. A release may bring its own
  title face; the name "Inch of Shadow" follows the brand face, Albertus Nova (Amir,
  2026-09-21).
- Render at delivery quality; a file that already fits a platform is uploaded as is;
  everything else goes through the resizers (frame.md, Render & Export).
- Every fact on screen comes from `proof.md`. Nothing is claimed as released before its date.
- Publish checklist on Instagram: location, tag or collab users, rename the audio.

## Open

- **Between singles:** what gets made when no release is near (studio, gigs, the city).
  Not decided here.
- **The album wrap:** what an EP or album adds on top of its singles. First piece of it,
  Amir's idea (2026-09-20): **A Letter for Listeners**. A piece of poetry reflecting the
  period of his life the record comes from, maybe a "playbook" of feelings, moods and
  colours. A carousel, for an EP or an album, never per single. NOT a thank-you and NOT a
  making-of. **The object is now specified: `letter-for-listeners.md`, built by
  `letter_slides.py`.** He writes the words. What the album wrap adds BESIDES the Letter is
  still open.
- **YouTube details: DECIDED 2026-09-21 (Formats-03)**, written in `youtube/PLAYBOOK.md` section 6.
  Drops get the cover video, songs the visualizer; the thumbnail is always the plain cover;
  **Premiere yes** (YouTube recommends it; his clicks in Studio, no hosted chat; 4K to be tried on Pinocchio); no cards; end screens from the template; Shorts carry a
  related-video link. The 11 catalogue videos are not a measurement of a release.
- **Which reel rules survive** (hooks, pacing, lyric reveals): Formats-02.
