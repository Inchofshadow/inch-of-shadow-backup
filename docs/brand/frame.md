---
version: v1
name: Inch of Shadow, Frame (video / image / text layer)
description: >
  The visual spec for everything Inch of Shadow puts on a screen: reels, stories, feed
  posts, thumbnails, covers, stings. Written in the HyperFrames frame.md format, so a video
  project that copies this file starts on brand. Assembled 2026-09-20 from the control
  panel decisions Look-01 (type), Look-02 (mark), Look-03 (colour), Look-04 (image),
  Look-05 (face), Look-06 (motion). Nothing here is invented: every value comes from a
  decision Amir made on a render. What is not decided is listed under Known Gaps.
unit: the frame. 1080x1920 (9:16) primary; 1080x1350 feed, 1280x720 thumbnail, 3000x3000 cover documented
principle: the core is constant, each release brings its own colour and may bring its own title face. One whole, one light idea, one text effect.

# Default mood M2. A release swaps `ground` and `ink` for its own mood (see `moods`) and adds accents sampled from its artwork.
colors:
  ground: "#0F0D0C"        # warm black, default dark
  ink: "#D6D1C8"           # platinum, default light
  flash: "#F4F1EC"         # the flash frame of T4 and the sting: color-mix(ink 27%, white)
  text-shadow: "rgba(15,13,12,0.55)"   # the only shadow allowed under light text on a photo: 0 2px 24px on a 1080px-wide canvas, scale it with the canvas
  # every mood hex is listed so no tool flags a mood colour as invented
  bone: "#EDE6DA"
  bone-ink: "#1F1D20"
  cream: "#F3EAD3"
  espresso: "#2A1F1A"
  champagne: "#D8C39A"
  oxblood-black: "#1C0F12"
  blush: "#E8D6D2"
  plum-black: "#1B1119"
  moon-violet: "#C9C2D6"
  midnight: "#110D19"
  pale-sage: "#C8CFC2"
  forest-black: "#0C120F"
  pewter: "#9E9A93"
  black: "#0A0A0A"

# The mood library (Look-03). One mood per release, chosen by what the song conveys,
# then checked against the artwork. light = text on dark, dark = ground or text on light.
moods:
  M2: { light: "#D6D1C8", dark: "#0F0D0C", name: "platinum + warm black", use: "DEFAULT. Non-release content: gigs, studio posts, story cards, the sting" }
  A:  { light: "#EDE6DA", dark: "#1F1D20", name: "bone + ink", use: "kept from the 2025 brand deck" }
  C:  { light: "#F3EAD3", dark: "#2A1F1A", name: "cream + espresso", use: "warm vintage" }
  E:  { light: "#D8C39A", dark: "#1C0F12", name: "champagne + oxblood black", use: "warm luxury" }
  F:  { light: "#E8D6D2", dark: "#1B1119", name: "blush + plum black", use: "romance" }
  M3: { light: "#C9C2D6", dark: "#110D19", name: "moon violet + midnight", use: "night mystery" }
  M4: { light: "#C8CFC2", dark: "#0C120F", name: "pale sage + forest black", use: "misty forest" }
  M6: { light: "#9E9A93", dark: "#0A0A0A", name: "pewter + black", use: "almost invisible. Story cards only, it fades on photo posts" }

# THE BRAND FACE. Every tool reads the family and the font file from here, nothing is typed
# anywhere else. Changing the face = changing this block.
face:
  family: "Albertus Nova"
  file: "fonts/AlbertusNova-Regular.otf"   # relative to docs/brand/. NOT ON DISK YET: put the bought file here under this name
  foundry: "Monotype (Berthold Wolpe's Albertus, revived 2017), https://www.myfonts.com/collections/albertus-nova-font-monotype-imaging , $104.99 for the 5-weight family"
  status: "DEFAULT FOR NOW (Amir, 2026-09-21), CANVA ONLY. It is in Canva's library and set on the Brand Kit, so Canva work uses it today. No file is owned yet, so every local tool (HyperFrames, image_generator, letter_slides) draws the fallback until the licence is bought and the file is saved at the path above. Read the logo clause before it becomes the wordmark."
  limits: "None known in the full family. Until the file exists the tools cannot use it at all."
  fallback: { family: "Marcellus", file: "fonts/Marcellus-Regular.ttf" }

typography:
  # Albertus Nova is the brand face for now (2026-09-21); Marcellus is its fallback and is what the local tools draw until the Albertus Nova file is bought. A release may bring its own title face (see Typography);
  # the sizes, spacing and placement below still apply to it. Within one piece: one face,
  # hierarchy from size, spacing and colour, never from bold.
  # Font file: docs/brand/fonts/Marcellus-Regular.ttf (SIL OFL). Declare it with a local
  # @font-face in every project; it is NOT one of HyperFrames' bundled fonts.
  # 1080x1920 reel / story
  title:        { fontFamily: "Albertus Nova", px: 104, weight: 400, tracking: "0.03em", case: "mixed" }
  name:         { fontFamily: "Albertus Nova", px: 60,  weight: 400, tracking: "0.05em", case: "mixed" }
  small:        { fontFamily: "Albertus Nova", px: 36,  weight: 400, tracking: "0.24em" }
  sting-name:   { fontFamily: "Albertus Nova", px: 96,  weight: 400, tracking: "0.05em", case: "mixed" }
  handle:       { fontFamily: "Albertus Nova", px: 34,  weight: 400, tracking: "0.24em", opacity: 0.6 }
  # 1080x1350 feed post
  post-title:   { fontFamily: "Albertus Nova", px: 96,  weight: 400, tracking: "0.03em" }
  post-name:    { fontFamily: "Albertus Nova", px: 56,  weight: 400, tracking: "0.05em" }
  post-small:   { fontFamily: "Albertus Nova", px: 34,  weight: 400, tracking: "0.24em" }
  # 1280x720 YouTube thumbnail: title only, NO artist name (YouTube prints the channel name)
  # PARKED 2026-09-21: live thumbnails are the plain cover, songs included (youtube/PLAYBOOK.md section 6).
  # This size stays for a Test & Compare, only with Amir's OK.
  thumb-title:  { fontFamily: "Albertus Nova", px: 150, weight: 400, tracking: "0.03em" }
  # 3000x3000 cover
  cover-title:  { fontFamily: "Albertus Nova", px: 220, weight: 400, tracking: "0.03em" }
  cover-name:   { fontFamily: "Albertus Nova", px: 140, weight: 400, tracking: "0.05em" }
  cover-small:  { fontFamily: "Albertus Nova", px: 110, weight: 400, tracking: "0.24em" }

spacing:
  # Meta 9:16 safe zone on 1080x1920. Nothing readable goes into these strips.
  safe-top: "270px"
  safe-bottom: "672px"
  safe-sides: "65px"
  name-under-title: "40px"
  handle-under-name: "56px"
  min-display-size: "11pt at real display size (render-and-shrink check)"

components:
  title-lockup:
    typography: "{typography.title} over {typography.name}"
    textColor: "{colors.ink}"
    shadow: "0 2px 24px {colors.text-shadow}, only on photos, never heavier"
    description: "Track title with the artist name under it. Sits on a calm area of the picture: sky, wall, shadow, floor. Never over a face, a head, gear or detail."
  dark-band:
    backgroundColor: "{colors.ground}, soft edged, low opacity"
    description: "Only when the safe zone has no calm area: a soft dark band behind light text. Dark ink is used only on plain light areas."
  sting:
    typography: "{typography.sting-name}"
    textColor: "{colors.ink}"
    backgroundColor: "{colors.ground}"
    flash: "{colors.flash} at 0.55 opacity, decays over 3 frames"
    source: "videos/ios-sting/ (variables: handle, ground, ink)"
    description: "The ending. Ground, one flash, the name is there, rest, fade to ground. 3 seconds. Type only until the hand-drawn mark exists. No handle."
  handle:
    typography: "{typography.handle}"
    text: "@inch_of_shadow"
    description: "OFF by default. Appears only when a piece really needs it. The underscores are part of the handle."
  mark:
    status: "working set, final art to be hand drawn by Amir (Look-02)"
    drafts: "docs/brand/mark/mark-drafts-v4.html"
    description: "Thorn ring, used alone where the name does not fit. Wordmark: mixed case with an obelisk as the I, or capitals with the ring as the O, never both in one lockup. No file to place yet: do not draw or generate one."
---

# Inch of Shadow, frame.md v1

## Overview

Inch of Shadow is Amir Miller, a Berlin artist. The name comes from "one inch of love is one
inch of shadow": light and shadow as one thing. The look carries **love and shadow, romance,
mystery, luxury**, with a person who is confident and out of reach. It is made for the big
crowd, not for a niche.

The system is small on purpose. **A few things never change** (the sizes, the
safe zones, the face rules, one light idea per image, one text effect per video). **Everything
else is chosen per release or per piece** from open libraries: a colour mood, sometimes a title face, a light, a
medium, a title arrival, and the motion borrowed from a reference Amir sends at that time.

**Key characteristics:**

- **Albertus Nova** (Monotype), mixed case, is the brand face FOR NOW (Amir, 2026-09-21): the name, the sting, non-release content. It lives in Canva today; the local tools draw **Marcellus**, the fallback, until the file is bought. A release may bring its own title face. No bold.
- **One light/dark colour pair per release** from the mood library. Default: platinum on warm black.
- **Text lives on a calm area of the picture** and never touches the face.
- **The name closes a video, it never opens one.** The ending is a flash and the name.
- **The pop rule:** would a stranger feel something in one second, without an explanation. Clear and charged beats clever and academic. Never only dark.

## The Frame

- **Primary:** 1080x1920 (9:16). Reels, stories, TikTok, Shorts. (30 fps in the renders so far.)
- **Also:** 1080x1350 feed post, 1280x720 YouTube thumbnail, 3000x3000 cover.
- **Safe zone (9:16):** top 270px, bottom 672px, sides 65px stay free of anything readable.
- **Render-and-shrink check (standing rule):** every new format is rendered at its native
  canvas, scaled down to its real display size (phone 390pt wide, YouTube sidebar 168px,
  mobile search 120px) and must still read at 11pt or more. Sizes are never trusted from
  numbers alone.

## Colors

There is no single palette. The frontmatter `colors.ground` and `colors.ink` are the default
mood M2; a release replaces them with its own pair from `moods`.

- The mood is chosen by **what the song conveys**, then checked against the artwork.
- **Accents come from the release artwork**, sampled exactly with a script, never guessed by
  eye. Examples already sampled: Farewell gold lettering #D4B955, The Deceiver ice lettering #D5EAF9.
- Rejected as MOOD pairs for type and graphics from now on: white + black, silver +
  blue-black, smoke + graphite. This does not touch artwork already released: The Deceiver
  cover (ice on blue-black) and its sampled colours stay valid for Deceiver objects.
- A release's choices are recorded in its release file, block `brand`: `mood`, `accents`,
  `title_font`, `artwork`.
- Internal north star: "everything runs in cycle but love returns in colours." The core is
  constant, each release brings its own colour.

## Typography

- **Albertus Nova** (Monotype, Berthold Wolpe's carved Albertus) is the brand face for now,
  chosen by Amir on 2026-09-21 out of four he named (Clarendon, Bookmania, Albertus Nova,
  Viking), after seeing them set as The Deceiver over Inch of Shadow in platinum on warm
  black (`references/fonts-look12/canva-default-candidates.png`). It carries the wordmark,
  the sting, gigs, studio posts, story cards, and any release that does not choose
  otherwise. Hierarchy by size, letter-spacing and colour.
  **It is in Canva and nowhere else yet.** The Brand Kit is set to it, so Canva work uses it
  today. The local tools need a bought file ($104.99 for five weights, MyFonts), saved as
  `docs/brand/fonts/AlbertusNova-Regular.otf`; until then they draw Marcellus. Read the logo
  clause before it becomes the wordmark.
- **Marcellus** is the fallback face and was the default until 2026-09-20. The sizes below
  were approved on Marcellus; Albertus Nova is heavier and a little wider, so the
  render-and-shrink check has to be run again on the first real piece once the file exists.
- **Ogg** (Sharp Type) was the default for one day, 2026-09-20 to 09-21. It stays in the
  library as a guest face; its trial file is still on disk for looking at.
- **Fonts can change per release** (Amir, 2026-09-20; Look-01 already said each release may
  vary). A release may choose its own title face, the same way it chooses its colour mood,
  picked by eye on renders. The sizes, spacing, safe zones and placement rules stay. The message
  the type carries stays: love and shadow, romance, mystery, luxury. Every new face passes the
  render-and-shrink check and ships as a local font file in `fonts/`.
- **Case is flexible by context:** mixed case is the default ("Inch of Shadow", "The Deceiver");
  the name, titles and small text (label, credits) may go in capitals when the context asks.
- Kept on the shortlist for later: Cormorant Garamond, Forum. Jost light is kept in mind for
  the electronic lane. Out: Cinzel, the electronic-era grotesque and mono faces, the Farewell title font.
- **Never abbreviate the name as IOS or IoS.** Write it in full, or stack it INCH / OF / SHADOW.
- Readable text says **Inch of Shadow**. Credit boxes say **Amir Miller**.

## Text Placement

- Text goes on a **calm area**: sky, wall, shadow, floor. Never over gear, faces, heads or detail.
  Check where the subject is in every shot before placing type, and look at the rendered frame.
- No calm area inside the safe zone: use the soft `dark-band` behind light text.
- Dark ink only on plain light areas.
- Thumbnails need a calm photo or a tight crop; a busy photo stays weak at 120px.
- **No artist name on YouTube thumbnails.**

## The Mark

Working set only (Look-02). Direction: **the ring**, a thorn ring that reads as halo, cycle and
crown of thorns. Used alone where the name does not fit: profile picture, stamp, the corner of a
photo. Final art will be hand drawn by Amir, so **no tool draws, generates or places a mark
yet**. Until then the brand signs with the wordmark in the brand face (Albertus Nova; drawn in Marcellus by the local tools until the Albertus Nova file is owned).

## Image

The image prompt is three layers, handled by `image_generator.py`:

1. **Core** (`inch_of_shadow_style.txt`), always added: love and shadow, light and dark;
   romantic, melancholic, mysterious, refined; **everything completes as one whole**; **one
   clear light idea, never flat, even, commercial light**; no people unless the subject asks;
   a person is distant and self-possessed, confident, out of reach, sexy in a tasteful way,
   never explicit; real faces kept exactly; no logos or text in the image.
2. **Options** (`options/<kind>/`), chosen per image, open lists: light L1 to L9, medium,
   texture, faces, concept (duality, reflection, shadow copy), symbols, motifs (sunglasses,
   flowers and roses, cast shadows, angels and statues, moon, sun, stars, streetlight).
3. **Palette**, optional colour line, default none.

Cinematic is an option, not the core. Direct flash is in. Styling comes from the shoots
(leather, or a fancy luxury suit; Gesaffelstein as an influence: sharp, monochrome, tailored).

## Borrowed Looks

A release may borrow ONE named look on top of the constant brand: S1 Xerox, S2 Halftone,
S3 Riso, S4 Engraving, S5 Cyanotype, S6 Solarisation, S7 Pictorialism. History, rules and
when to use each: `style-library.md`. Made locally with `print_looks.py` (no AI, the photo is
never redrawn). Flat-colour screenprint is rejected for portraits.

## The Face

- **Sunglasses:** the feeling of the song or post decides. On is the natural state. Off is the
  deliberate move for open, direct or vulnerable moments, and it carries weight because it is rare.
- **Never:** distorted, cartooned, comic or warped versions of his face.
- **AI never changes his face.** The only exception is surgical work Amir asks for explicitly
  (remove one object or blemish). Photos of him go through grade or composite, never restyle.
- Everything else about faces is decided case by case with Amir.

## Motion

Full detail: `motion-library.md`. In short:

- **No fixed motion register.** Pace, camera, transitions and effects are chosen per video from
  the reel Amir sends at that time, and each liked reference is saved as M1, M2...
- **Title arrivals, one per video:** T1 soft fade, T2 letter by letter, T3 out of shadow (the
  light brings the letters, the shadow takes them away), T4 on the flash.
- **The ending:** the `sting` component. For short videos, maybe: out of shadow on black, or
  over the picture itself.
- **No default caption look.** Amir very rarely talks on camera.

## Render & Export (standing rule, Amir 2026-09-20)

Always render in high quality, and deliver each platform its own best file. Never upload a
draft render, never stretch one aspect ratio into another.

1. **Compose per aspect ratio.** A 9:16 reel, a 4:5 post, a 16:9 YouTube video and a 1:1 cover
   are separate compositions with their own sizes from this file, not crops of each other.
2. **Render the master from HyperFrames at delivery quality:**
   `npx hyperframes render . -q delivery` (the default `looks` is for checking, `draft` is
   never delivered). For YouTube and for the archive also render 4K:
   `--resolution portrait-4k` (2160x3840) or `landscape-4k` (3840x2160). Tested on the sting
   2026-09-20, both work. Use full-resolution source photos and footage, not downscaled
   working copies, or the 4K render gains nothing.
3. **If the render already has the platform's exact size, upload that file.** Every extra
   encode loses quality, and the platform re-encodes once more anyway.
4. **Use our resizer for everything else:** `video_resizer.py` (10 presets: Instagram reel,
   story, square and portrait post; YouTube 1080p, 1440p, 4K and Shorts; Spotify Canvas
   vertical, no audio; TikTok), with trim, focal-point crop, metadata from the release file,
   and stripping of source metadata. Straight from a project:
   `python3 video_resizer.py --from-hyperframes <project folder>`. Still images and covers
   go through `artwork_resizer.py` (24 specs: cover, profile images, thumbnails including
   3840x2160 and Shorts, Instagram 1:1, 4:5, 3:4, story and reel cover).
5. **What the resizer does since the 2026-09-20 upgrade (Machine-07, covered by tests):** a
   file that already fits a preset (same size, H.264, same frame rate, nothing to trim) is
   passed through with the picture untouched, only the metadata is stripped; the 1440p and
   4K YouTube files are written only from a source that large, never upscaled; a frame rate
   that has to be converted (for example 25 to 30) is reported; the release cover comes out
   at 4000x4000 from a master that large and falls back to 3000x3000 without upscaling.
6. **Platform specs checked against the official pages on 2026-09-20** (full table on board
   ticket Machine-07). What changes our files:
   - **Cover master: 4000x4000**, JPEG, sRGB. Apple now asks for at least 4000x4000; Spotify
     takes up to 10000, Bandcamp needs 1400 or more, Beatport prefers 3000, Symphonic takes
     JPEG only, 1000 to 10000, up to 50 MB. The Look-01 cover sizes were approved on
     3000x3000, so on a 4000 canvas scale them by 4/3 (title 293, name 187, small 147) and
     confirm with the render-and-shrink check.
   - **YouTube thumbnail: 3840x2160** is now the recommended size (2160x3840 for Shorts),
     up to 50 MB when uploaded from a computer, 2 MB from a phone. The approved 150px title
     on 1280x720 becomes 450px on 3840x2160.
   - **YouTube video: upload 4K or 1440p when the source allows.** YouTube's recommended
     bitrates: 1080p 8 Mbps, 1440p 16, 2160p 35 to 45. One outside test (FilmDaft, 2025)
     found 1440p and 4K uploads get the better VP9 codec at every playback size and 1080p
     uploads do not; YouTube itself states no such rule, so treat it as likely, not certain.
   - **Spotify Canvas is vertical 9:16 only**, 3 to 8 seconds, 720 to 1080 px tall. There is
     no square Canvas: do not use the resizer's square Canvas preset.
   - **Instagram:** a story clip can now be 60 s (our preset cuts at 15); reels can be up to
     20 minutes and are recommended to new people up to 3 minutes; the old 60 s caps on feed
     video are gone. Photos keep quality from 1.91:1 to 3:4, and the profile grid shows 3:4
     tiles, so 1080x1440 is the still size that fills a tile.
   - **TikTok:** uploads up to 60 minutes; 3 minutes is what every account can post.
   - Still unconfirmed officially: Bandcamp avatar and header height, SoundCloud track
     artwork page (it would not load; 800x800 minimum comes from a search snippet).

## Composition Rules

### Do

- Set type in the **brand face** (the `face` block above: Albertus Nova, fallback Marcellus 400), or in the release's own title face when it has one, in the release's mood colours.
- Keep all text **inside the safe zone** and **off the face and head**.
- Give every image **one light idea** and every video **one text effect**.
- Open with the hook. **Close with the name.**
- Run the **render-and-shrink check** on every new format.
- Use symbols a stranger already knows, handled with taste.

### Don't

- Don't place text over the face or head, or outside the safe zone.
- Don't distort, cartoon or AI-change the face.
- Don't use flat, even, commercial light.
- Don't write IOS or IoS.
- Don't open a video with a title, a name or a logo.
- Don't use more than one text effect in the same video.
- Don't let one influence become the whole look (no house style of sacred geometry).
- Don't make anything that needs an explanation to work on a stranger.
- Don't go only dark. Sunny, warm and daylight are on brand too.
- Don't use Cinzel or the electronic-era grotesque and mono faces.
- Don't show the handle by default.

Allowed per video, by Amir's word: glitch, RGB split and shake; typewriter or terminal-style
text; fast cuts and zoom punches; emoji or sticker text; bouncy or playful text.

## Aspect-Ratio Behavior

| Object | 9:16 (1080x1920) | 4:5 (1080x1350) | 16:9 thumbnail (1280x720) | 1:1 cover (3000x3000) |
| --- | --- | --- | --- | --- |
| Title | 104px | 96px | 150px | 220px |
| Artist name | 60px | 56px | none | 140px |
| Small text | 36px | 34px | none | 110px |
| Safe zone | 270 / 672 / 65 | not decided | not decided | not decided |

## Approved Entities

- Artist: **Inch of Shadow**. Real name Amir Miller, in credit boxes only.
- Handle: **@inch_of_shadow** (underscores). Studio: Ambertone Studios, @ambertone.studios.
- Label: Indigo Children Records. Credit line: "Written, produced, mixed and mastered by Inch
  of Shadow at Ambertone Studios, Berlin." (Eastern Stars: mastered at Riverside Studios.)
- No other logos, venues, labels or people appear on screen unless `proof.md` lists them.

## Numerals & Claims (hard rule)

Every fact, date, number and credit on screen comes from `proof.md`. Nothing is invented or
rounded. The Half the Night EP (Half the Night + Pinocchio, date open) is never shown as released
before its date. The songs era
is not public yet: see the PUBLIC STATUS block in `positioning.md`.

## Pre-Render Self-Audit

- **Type:** the brand face (the `face` block: Albertus Nova, fallback Marcellus 400), or the release's chosen title face, from a local font file; sizes match the canvas row above.
- **Colour:** only the release's mood pair plus accents sampled from its artwork.
- **Safe zone:** nothing readable in the top 270, bottom 672 or side 65 strips (9:16).
- **Face:** no text on the face or head, in any frame of the move, checked on rendered frames.
- **Light:** one clear light idea; nothing flat or commercial.
- **Effects:** one text effect in the whole video.
- **Order:** hook first, name last; no handle unless the piece needs it.
- **Shrink:** readable at real display size, 11pt minimum.
- **Stranger test:** one second, no explanation.
- **Facts:** every claim traces to `proof.md`.

## Known Gaps

- **The mark has no final art.** Hand drawn by Amir, then `mark.svg`, then a sting version with it.
- **Feed post and thumbnail safe zones** were never measured; only the 9:16 zone is decided.
- **A 3:4 still (1080x1440)** has no approved type sizes yet; Look-01 covered 1080x1350.
- **Dark band opacity** is set by eye per render, no fixed number.
- **Styling and the shoot** (Look-08) and **the edit recipe / grade** (Look-09) are open
  tickets and will add sections here.
- **Voice** lives in `voice.md` (v2, 2026-09-20).
- **Canva Brand Kit** (fonts, colours, logo) and the tool wiring are Machine-02.
- **Lyric look** (how sung lines appear) is not decided; it comes with the first song video.
- **Title colour:** the mood's light colour, or an accent sampled from the artwork (as on
  the Farewell and Deceiver covers)? Not decided as a rule.
- **Long titles:** the approved sizes were checked on short titles. A title wider than
  about three quarters of the canvas, or set on two lines, has no approved treatment.
- **Logos inside a photo** (for example the brand mark on his sunglasses): no rule. His
  photos are never AI-changed, so it stays unless he asks for a surgical removal.
- **There will not be one font for everything** (Amir, 2026-09-20). A release picks its
  face from `font-library.md` (his own research, categorised, all potentials) or from a new
  find. What follows about the search for the brand's own face still stands (Look-12).
- **The brand's own face is still being searched** (board ticket Look-12). Albertus Nova is
  the default FOR NOW (2026-09-21, after Ogg for one day), not the final answer; he is collecting references (first two: The Cure
  "Lovesong", set in Thor, and The Doors "L.A. Woman", set in Cooper Black in tight capitals:
  both warm, heavy, drawn-by-hand display faces, far from thin fashion serifs). Already known: wide-spaced
  serif CAPITALS read as fantasy ("Lord of the Rings") to him, in any face, so do not set
  the name that way. Guest faces he likes for titles and posters: Editorial New, Apoc,
  Saol Display, Reckless (kept, he likes it "in a certain way"); Matthews Thin and Gloria
  (tall deco capitals).
- **Per-release fonts:** allowed, no release has chosen one yet. For now the artist name
  "Inch of Shadow" follows the BRAND FACE, Albertus Nova, even next to a release title in
  another face (Amir, 2026-09-21: "it follows Albertus Nova"; on 09-20 the same rule named
  Marcellus, the brand face of that day). Revisit on the first release that brings its own font.
- **Export gaps in our resizer:** see Render & Export.
