# The photographer's full Lightroom settings, one file per edit

Each `out-NNN.xmp` is the COMPLETE XMP block copied out of the edited JPEG on the drive,
byte for byte, on 2026-09-21. Nothing was filtered, so no setting can be missing: 290 kinds of simple
setting and 28 kinds of structured setting across the 204 files (tone curves per channel,
point colours, the profile or look, AI remove areas with their brush dabs, masks, AI denoise).

They are standard Adobe XMP. Lightroom and Camera Raw can read them as a sidecar next to the
matching raw (same base name, `.xmp`), which applies her exact edit to that raw.

Index with the values pulled out: `../shoot-lightroom-settings.json`. Summary in words:
`docs/brand/recipes/her-lightroom-settings.md`. The ids match `../shoot-catalogue.json`.
