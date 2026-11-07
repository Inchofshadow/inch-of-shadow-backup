# What the photographer actually did (read from her own files, 2026-09-21)

Every one of the 204 outdoor edits carries her complete develop settings in its XMP block.
Software: **Adobe Photoshop Lightroom Classic 15.5 (Macintosh)**, camera profile Adobe
Standard. Extracted to `plans/control-panel/shoot-lightroom-settings.json`, one entry per
catalogue id. This is ground truth; it replaces guessing from pixels wherever the two differ.

## The built-in filters Amir watched her use

Lightroom calls them profiles. 125 photos use plain **Adobe Color**, 37 **Adobe Monochrome**,
and 36 use a creative profile: **Modern 01** (13), **B&W 09** (9), **Modern 10** (7),
**Modern 04** (3), **Artistic 01** (2), **Artistic 04** (2). 6 have none. No named preset on
any photo: she works the sliders by hand on top of a profile.

## Her style in numbers (median, range, how often she touched it)

| Control | Median | Range | Touched on |
|---|---|---|---|
| Exposure (stops) | +0.2 | -3.7 to +4.8 | 80% |
| Contrast | +6 | -100 to +55 | 64% |
| **Highlights** | **-46** | -100 to +29 | 76% |
| **Shadows** | **+38** | -18 to +100 | 75% |
| Whites | +7 | -99 to +57 | 95% |
| Blacks | 0 | -66 to +69 | 94% |
| White balance | 6350 K | 3450 to 8000 K | 100% |
| Tint | +4 | -17 to +40 | 97% |
| Texture | 0 | -15 to +30 | 44% |
| Clarity | +8 | -14 to +36 | 69% |
| Dehaze | 0 | -14 to +38 | 31% |
| Vibrance | +5 | -11 to +30 | 81% |
| Saturation | 0 | -40 to +6 | 82% |
| Sharpening | 40, radius 1.0 | 13 to 58 | 100% |
| Noise reduction, luminance | 0 | 0 to 25 | 2% |
| Noise reduction, colour | 25 | 0 to 30 | 98% |
| **Grain added** | 0 | 0 to 27 | **7%** |
| **Vignette added** | 0 | 0 to 9 | **2%** |
| Lens profile correction | off | | 0% |

Her habit: pull the highlights far down, lift the shadows, then set whites and blacks per
photo. Colour mixer: she moves the hue or saturation of single colours on 56 to 86% of
photos, each photo differently (greens lean a median +9 toward aqua, oranges a median -6 in
saturation). Colour grading: shadows tinted on 76% of photos (median amount 10), midtones and
highlights warm (hue about 46 to 49). 71 different tone curves; the most common pulls the
midtones slightly down (136 to 129). Cropped on 102 of 204, keeping a median 77% of the frame;
rotated on 26%, up to 14 degrees.

## What this settles

- **Why no recipe copies a specific edit of hers.** She sets about forty controls by hand on
  every photo: exposure across 8.5 stops, white balance across 4500 K, single colours
  per photo. Claude's four experiments on the pixels had reached the same conclusion blind.
- **The grain and the dark edges are mostly not effects.** See the correction in
  `edit_recipe.py`: two different developers of the same raw, not film grain she added.
- **Retouching, corrected the same day.** The first pass read only the simple slider values
  and reported "no retouching visible". Wrong. Amir said she used Lightroom's AI feature, and
  the full XMP shows it: **17 photos carry `RemoveAreas` with `fill_method="firefly"`**,
  Adobe's generative AI, 19 areas in all. Seen raw against edit
  (`references/look09/ai_remove_before_after.jpg`):
  - about 14 are BACKGROUND cleanup: a door handle above his head (-106, -107), litter and a
    tissue on the ground (-131, -163, -93), a red bag by the tree (-33), a shoe entering the
    frame (-161, -162), people and a cyclist in the park (-2, -3, -5), objects on the horizon
    of the grass slope (-169, -170, -171);
  - **5 are ON HIM:** the jaw and neck line and skin by the ear on the close profile (-19, two
    areas), and the chin or neck on -14, -32 and -5. This is the double chin work he watched.
  Each of these photos is flagged `ai_generated` in the shoot catalogue, with the count on him.
  2 photos also went through Lightroom's AI Denoise (out-072, out-196). Only one photo has
  local masks. No Photoshop step appears in any file's history.

## Nothing is missing: the lossless archive

`plans/control-panel/shoot-xmp/` holds the COMPLETE XMP block of every edit, copied byte for
byte: 290 kinds of simple setting and 28 kinds of structured setting (tone curves per channel,
point colours, the profile, AI remove areas with their brush dabs, masks, AI denoise). The
JSON index is a convenience; the XMP files are the record. They are standard Adobe sidecars,
so Lightroom can apply her exact edit to the matching raw from them.

## What it opens

With Lightroom, her real settings could be reused directly on the unedited raws (copy the
settings of the nearest edited frame, then adjust), at true raw quality, which beats any
pixel recipe. Without Lightroom, `edit_recipe.py` stays the local route.
