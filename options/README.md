# Per-image options

The image tool builds every prompt from three layers:

1. **Core** (`../inch_of_shadow_style.txt`): only what is true for every image. Always added.
2. **Options** (this folder): chosen per image. Nothing here is added unless you ask for it.
3. **Palette** (`../palettes/`): optional colour line. Default is none.

Each option is one short text file: `options/<kind>/<name>.txt`.

| Kind | Flag | Examples |
|---|---|---|
| light | `--light` | `L1` to `L9` (the light library) |
| medium | `--medium` | `cinematic`, `bw-flash-film`, `engraving`, `8-bit` |
| texture | `--texture` | `clean`, `film-grain`, `flash-overexposure` |
| faces | `--faces` | `shown`, `hidden-by-pose`, `hidden-by-crop` |
| concept | `--concept` | `duality`, `reflection`, `shadow-copy` |
| symbols | `--symbols` | `cycle-circle`, `ritual` |
| setting | `--setting` | empty for now (Amir removed the draft list); inline text works |
| motif | `--motif` (repeatable) | `moon`, `sun`, `stars`, `flowers-roses` |

A flag matches a file name or its id prefix (`--light L9` finds `l9-direct-flash-night`).
Quoted multi-word text works as a one-off: `--medium "watercolour on rough paper"`.

```
python3 image_generator.py options
python3 image_generator.py art "a woman on a sidewalk" --light L9 --medium bw-flash-film --print-prompt
```

`--print-prompt` shows the exact prompt and stops: no API call, no cost.

The lists are open. To add an option, drop a new `.txt` file with one sentence
into the right folder. New references from Amir get sorted here (Look-04, 2026-09-14).
Settings: the draft list was removed by Amir on 2026-09-14; add settings only from his references.
