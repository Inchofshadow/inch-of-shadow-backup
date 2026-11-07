# Inch of Shadow Control Panel - Visual Brand (status + handoff)

Read this first to continue the visual-brand / palette / image work in a fresh
Claude chat. Everything below is committed in this repo.

**To resume in a new chat:** open this repo and say
"continue the Inch of Shadow visual brand tuning - read docs/brand/CONTROL-PANEL.md".
The open work is on the control panel board (`plans/control-panel/tickets.json`), not in this file.

---

## What this is
The Inch of Shadow Control Panel = IoS's own creative/marketing tools (Python,
local-first; concepts borrowed read-only from a partner's repo, never his code/data).
This file covers the VISUAL brand + the image studio.

## The image studio - `image_generator.py`
Runs on Amir's own OpenAI key (`OPENAI_API_KEY` in `.env`). Output goes to
`generated_images/<project>/` (gitignored, local). Finder opens after each run.

Five modes:
- `art "<subject>"` - text to image in the IoS look
- `restyle <photo> "<instruction>"` - AI restyles a photo (uploads to OpenAI; can drift the face)
- `card "<subject>" --title "<TEXT>"` - AI background + Pillow text/wordmark overlay
- `grade <photo>` - local palette recolor, no AI, face untouched
- `composite <photo> "<background>" --blend 0..1` - THE SAFE FACE PATH: rembg cuts
  you out locally (face never sent to OpenAI), generate an IoS background, composite
  locally. Use a NEUTRAL photo for `--blend 0`; a pre-tinted photo needs ~0.85.

Style is THREE layers (rebuilt 2026-09-14, Look-04):
1. **Core** (`inch_of_shadow_style.txt`) - always added, short, only what is true for
   every image.
2. **Options** (`options/<kind>/`) - chosen per image, nothing is forced:
   `--light L1..L9 --medium --texture --faces --concept --symbols --motif` (repeatable).
   `python3 image_generator.py options` lists them; `--print-prompt` shows the exact
   prompt with no API call and no cost.
3. **Palette** (`palettes/`) - optional colour line, default is none.

## Visual identity - replaced 2026-09-14 (see the control panel board)
- **Core** (`../../inch_of_shadow_style.txt` v2): love and shadow, light and dark; mood
  romantic, melancholic, mysterious, refined; everything in the image completes as one
  whole; one clear light idea, never flat commercial light; real faces kept exactly; no
  text in the image. Grain, noir, hidden faces, occult and cinematic are now OPTIONS,
  not the core. The old core is kept as `inch_of_shadow_style.v1.txt`.
- **Default palette:** none. Colour is chosen per image, or per release from the Look-03
  mood library (default mood M2: platinum #D6D1C8 + warm black #0F0D0C).
- **Per-release palettes** (`../../palettes/`): `oxblood`, `cold`, `sepia` are
  electronic-era prompt text, still callable with `--palette NAME`, no longer automatic.
- **Signature descriptor:** "dark dance wave" (bio prose only, never a tag).
  Genre/discovery tags: dark disco, EBM, coldwave, acid, electro.

## Brand tuning - DONE vs OPEN (resume here)
Method: one dimension at a time, decided BY EYE (generate options, Amir picks).
All five OPEN dimensions were decided on 2026-09-14 in Look-04 (board ticket):
- **Faces:** both. More images WITH the face from now on; hidden by pose, crop or
  shadow is an option (`--faces`). Full face rules come in Look-05.
- **Subject mix, real vs abstract, medium / texture:** open lists in `options/medium/`
  and `options/texture/`, chosen per image (photo, B&W flash film, painting, engraving,
  noir comic, 8-bit, digital effects).
- **Anti-brand:** the one line that stayed in the core is "never flat, even, commercial
  light". The rest of the anti-brand list belongs to Look-06.

## Context Amir gave (keep in mind)
- Palette is DYNAMIC: each album/release tends to a different colour. That is why the
  core is constant and the palette is per-release. Do not force one colour.
- Songs are the main line (bridge plan v2, 2026-09-13), not public yet; the electronic
  lane continues under the same name. The brand rides on mood/identity, not genre.
- It has to be pop (Amir, 2026-09-19): made for the big crowd, familiar symbols handled
  with taste. Test: would a stranger feel something in one second, no explanation.
- Never AI-redraw Amir's face. Use `grade` or `composite` for photos of him.

## File map
- `image_generator.py` - the tool (5 modes)
- `inch_of_shadow_style.txt` - the core (constant DNA)
- `options/` - per-image options (light, medium, texture, faces, concept, symbols, motif)
- `palettes/` - oxblood, cold, sepia (electronic-era, optional; no default palette)
- `references/` - reference images for `--reference`
- `generated_images/` - output (gitignored, local)
- `description_scorer.py` - pre-publish bio/description scorer
- `docs/brand/` - positioning, voice, proof, README, and this file

## Setup roadmap - superseded by the board (2026-09-14)
The plan now lives as tickets in `plans/control-panel/tickets.json`, rendered at
Release Manager `/board`. `CONTROL-PANEL-SETUP-ROADMAP.md` is frozen history.
The board is the only status list; do not keep a second one here. Name a ticket to run it.
