# Inch of Shadow - Motion library (Look-06, decided 2026-09-20)

How Inch of Shadow videos move. Built and rendered with HyperFrames. Only what repeats in
every video is fixed; everything else is chosen per video. The list is open and grows.

## Fixed in every video
- Type: Marcellus by default (local file `fonts/Marcellus-Regular.ttf`), or the release's own
  title face when it has one; the Look-01 sizes and spacing,
  the Look-03 colour mood of the release, inside the platform safe zone, never over the
  face or head.
- The name closes a video, it never opens one. The hook comes first.
- One text effect per video, never more (one idea per video, like one light idea per image).
- No handle on screen by default. It appears only when a piece really needs it.

## Title arrivals (open library, pick one per video)
| Id | Arrival | Leaves | Feel |
|---|---|---|---|
| T1 | Soft fade, rising out of a blur | fades out | calm, warm |
| T2 | Letter by letter, like engraved letters being set | letters leave in reverse | careful, classic |
| T3 | Out of shadow: nothing on screen, a light sweeps and the letters exist only where it has passed | the shadow returns and takes the text | slow, romantic, mysterious |
| T4 | On the flash: hard cut onto a 3-frame camera flash, no fade | hard cut | beat hits, flash photos, harder tracks |

New arrivals get the next number (T5...) when a reference or an idea brings one.
Source project: `videos/look06-title-arrivals/`.

## The ending (the sting)
- **The sting is B, on the flash:** warm black, one flash, `Inch of Shadow` is there,
  rests, fades to black. 3 seconds, type only, no handle. Reusable file and project:
  `videos/ios-sting/` (variables: `handle`, `ground`, `ink`, so a release's colour mood
  can be swapped in without rebuilding; commands in that folder's CLAUDE.md).
- For short videos, maybe: A, out of shadow on black, or D, out of shadow over the
  picture itself instead of cutting to black. Source: `videos/look06-sting/`.
- Not picked: C, the cast shadow that grows like a sundial.
- When the hand-drawn ring mark exists (Look-02), the sting gets a version with it.

## Chosen per video, never fixed
Pace, camera movement, transitions, effects. Amir sends a reel or short he likes at the
moment of making; it goes through /video-analyze and HyperFrames builds from it. Every
reference he likes is saved below as M1, M2... so it can be ordered by name later.

| Id | Reference | What was taken from it | Used in |
|---|---|---|---|
| (empty, fills as videos get made) | | | |

## Captions
No default caption look: Amir very rarely talks in a video. If a talking clip happens,
the style is picked on that clip (HyperFrames' quiet `anchor` rail is the safe start).

## Never
- Text over the face or head, or outside the safe zone.
- The face distorted, cartooned, or changed by AI.
- Flat, even, commercial light.
- The name shortened to IOS or IoS.
- A title, name or logo opening a video.
- More than one text effect in the same video.
- One influence becoming the whole look.
- Anything that needs an explanation to work on a stranger (the pop rule).
- Only dark.
- Cinzel, and the electronic-era grotesque and mono faces.

Allowed, by Amir's word (2026-09-20), chosen per video: glitch, RGB split and shake;
typewriter or terminal-style text; fast cuts, zoom punches, emoji or sticker text; bouncy
or playful text.
