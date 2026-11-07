# Per-release palettes

The Inch of Shadow image prompt is three layers (core, options, palette). See ../options/README.md.

- **Core** (`../inch_of_shadow_style.txt`): only what is true for every image. Always added.
  Grain, noir, cinematic and hidden faces are options now, not the core (Look-04, 2026-09-14).
- **Options** (`../options/`): chosen per image.
- **Palette** (this folder): an optional colour line. **The default is none.**

The three files here, `oxblood.txt`, `cold.txt`, `sepia.txt`, are electronic-era prompt
text. They still work when called by name, nothing adds them automatically.

```
python3 image_generator.py art "rain on black glass"                       # no palette line
python3 image_generator.py art "a frozen lake at night" --palette cold
python3 image_generator.py art "a faded portrait" --palette sepia
```

`--palette` also accepts an inline description for a one-off release palette:

```
python3 image_generator.py art "..." --palette "deep violet and silver, cold moonlight"
```

An unknown palette name stops with the list of available ones.

Not the same thing as the Look-03 mood library: the moods (M2 platinum + warm black as
the default, bone + ink, cream + espresso and the others) are hex pairs for TEXT AND
GRAPHICS on top of images. They live in the Look-03 ticket and go into `docs/brand/frame.md`
(Look-07). The files in this folder are colour words for the image model.

To add a release palette permanently, drop a new `<name>.txt` here (one short
"Palette: ..." line) and call it by name.
