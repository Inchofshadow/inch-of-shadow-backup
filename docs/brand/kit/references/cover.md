# Recipe: release cover and profile images

**Canvas:** 4000x4000, JPEG, sRGB. Apple asks for at least 4000; Symphonic takes JPEG only,
1000 to 10000 px, up to 50 MB. Beatport is not used for new releases; its write-once rule
(artwork and metadata 100% final before the FIRST submission, this burned The Deceiver)
applies only if it is added back.

**Type on a cover** (approved on 3000, scale by 4/3 on 4000 and confirm by render):
title 293px, name 187px, small 147px. Tracking: title 0.03em, name 0.05em, small 0.24em.
The brand face from `frame.md` (Albertus Nova), or the release's own title face; the name
"Inch of Shadow" follows the brand face (Amir, 2026-09-21).
The image generator never puts text in the artwork: type is a separate layer.

**Steps**
1. Mood: pick the release's colour pair from the mood library by what the song conveys
   (`frame_tokens.py --moods`), then sample accents from the artwork with a script
   (Pillow, exact values), never by eye from a preview.
2. Image: `Inchofshadowcode/image_generator.py` builds the prompt from the core plus
   options chosen per image (`--light L1..L9 --medium --texture --faces --concept
   --symbols --motif`). `--print-prompt` first, it costs nothing. A paid render needs
   Amir's go. Photos of him go through `grade` or `composite`, never `restyle`.
3. Check: `shrink_check.py cover.png --format cover --text-px <smallest>`. A cover has to
   work at 64px in a playlist row.
4. Export every platform size: `python3 Inchofshadowcode/artwork_resizer.py <master>`. It
   writes the 4000 cover when the master allows it and falls back to 3000 without
   upscaling, plus Beatport 3000, SoundCloud, profile images and thumbnails. It strips GPS
   and camera data and embeds sRGB.

**The release's look:** one borrowed look from `style-library.md` (S1 to S7), shown to Amir
on his own photo first (`print_looks.py <photo> --sheet`), then recorded in the release
file's `brand` block.

**Not decided:** the final mark art (Look-02). Do not draw or place a mark.
