# Video Brand Session Kit — the 5 questions, pre-loaded

> Superseded 2026-09-13 by the Control Panel Board: plans/control-panel/tickets.json, viewed at RM /board. This file is frozen as reference; its questions live in the board's tickets.

Prepared 2026-08-15 by the video side (HyperFrames). When Amir says "let's set up the
video brand" (here or in the control-panel chat), ask THESE questions in THIS order,
with these prepared options. Every answer is decided BY EYE on rendered samples,
same method as the locked palette work. After Q1-Q5 are answered, write
`docs/brand/frame.md` (the video brand spec) and render the logo sting once.

---

## Q1 — Typography (decided on 4 rendered specimen videos)

Render the same 5s clip in 4 type systems (all free, self-hostable, scene-grounded
via typewolf/current club-poster usage), Amir picks:

| # | Display | Mono/support | Feel |
|---|---|---|---|
| A | Barlow 800/900 | IBM Plex Mono | industrial grotesque, the look of the 2 test reels |
| B | Archivo Black / Expanded | Space Mono | wide brutalist poster, heavier presence |
| C | Anton or Oswald (condensed) | JetBrains Mono | tall club-flyer, classic techno poster |
| D | Syne or Unbounded | IBM Plex Mono | electronic-native, weirder, carries the "not only dark" side |

The chosen display face lowercase = the **wordmark lockup** ("inch of shadow" +
accent rule), since no standalone logo file exists (checked Brand Assets 2026-08-15:
only release-specific transparents). One decision closes fonts + wordmark + sting.

## Q2 — Palette hexes (approve swatches, not prose)

Core stays constant, palette flexes per release. Candidates already sampled from
the actual artwork (medium-cut quantization):

- **oxblood (default, A60/B40 warm/cold)** — derive from the "room" reference +
  Farewell art: ground `#180C19`, surface `#341327`..`#381933`, accent `#7A2E2A`
  family (tune by eye), cold counter `#3E5C5F`-ish steel-teal, text bone `#EDE6DA`
- **cold** — from Deceiver art: `#070B0F` ground, `#131C28`/`#1F2E41` surfaces,
  `#25384C` accent zone, `#687886` muted text-blue
- **neutral-ink** — from Tour art: `#0D0D0D`..`#181718` + `#5F5969` violet-grey
Ask: approve/adjust 5-6 swatches per palette (show as rendered swatch cards).

## Q3 — Anti-brand line (approve or edit, 1 minute)

Draft to approve: "Never: bright/poppy candy colors, clean corporate SaaS look,
cartoonish/playful illustration, glossy stock-photo sheen, gradient-tech-startup
purple. IoS is grain, shadow, one light source, matte."

## Q4 — Motion identity (A/B rendered samples)

The dimension the control panel doesn't cover. Two proposals, pick or mix:
- **A "hard industrial"**: 0ms hits, glitch/chromatic on surges, ridged-burn on
  drops, shakes; fast 0.15-0.3s transitions
- **B "cinematic slow-burn"**: slow pushes, light-leak/blur transitions, fewer
  harder hits saved for real drops
Likely answer: A for dark releases, B for warm/daylight content; both live in the
spec keyed to content register.

## Q5 — Caption identity defaults (needs one talking clip first)

Render the same clip with `anchor` (safe default), `ink` (bright scenes) and one
themed dark identity (`glitch` or `neonsign`); Amir picks the default pair.

---

## Standing facts the session should know

- Video brand spec target file: `docs/brand/frame.md` (single source of truth;
  every HyperFrames project copies it). Update CONTROL-PANEL.md to point here.
- Locked already: core visual DNA, per-release palette philosophy, safe-face rules,
  no-text-in-artwork (type lives in the video layer), anti "monolithically dark".
- Video-side rules already in force: no branding in first 3s, sting/handle/credit
  per menu row, no text over Amir's face (check per shot), no em-dashes in copy,
  copy quoted verbatim.
- Open image-side dimensions (subject mix, real-vs-abstract, medium/texture,
  faces-in-art) do NOT block video; resume separately.
