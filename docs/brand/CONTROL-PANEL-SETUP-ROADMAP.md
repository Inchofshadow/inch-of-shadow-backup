# Control Panel Setup Roadmap — the complete remaining setup, led question by question

> Superseded 2026-09-13 by the Control Panel Board: plans/control-panel/tickets.json, viewed at RM /board. This file is frozen as reference; its questions live in the board's tickets.

Written 2026-08-15. This is the master checklist so nothing gets missed. Each phase is
one sitting (30-60 min). Claude leads: asks the phase's questions with prepared options,
renders samples where visual, records the answer, moves on. Everything decided BY EYE.
Resume from any phase; status lines get updated in place.

**Already DONE, never re-ask:** positioning.md, voice.md, proof.md (verbal layer) ·
core visual DNA (`inch_of_shadow_style.txt`) · palette philosophy (per-release, A60/B40
default) · safe-face image rules · video craft system (videos/ playbook files).

---

## Phase 1 — Type & Mark  [OPEN, do first]
The single highest-leverage sitting. Fonts and wordmark are one decision.
1. **Fonts by eye:** 4 rendered specimen videos (same 5s clip):
   A Barlow 900 + IBM Plex Mono (industrial, the test-reel look) ·
   B Archivo Black + Space Mono (wide brutalist) ·
   C Anton/Oswald + JetBrains Mono (condensed club flyer) ·
   D Syne/Unbounded + IBM Plex Mono (electronic-native, carries the warm side)
2. **Wordmark, no logo needed** — pick a direction (rendered on the winning font):
   - pure type lockup: lowercase "inch of shadow"
   - type + the accent rule (the short bar under/beside, already a motif in the reels)
   - **the inch mark**: a ruler tick / one-inch notch glyph next to the name. Literal,
     minimal, ownable, no illustration skill needed
   - shadow-cast type: the lockup throwing a long hard shadow (the duality IN the mark)
   - mono/terminal mark: `inch_of_shadow` styled as the handle itself, IBM Plex Mono
3. Output: locked type system + wordmark lockup file (transparent PNG/SVG).

## Phase 2 — Color numbers  [OPEN]
Prose palettes become approved hex swatches (rendered as cards):
- oxblood (default): grounds `#180C19`/`#341327`, oxblood accent ~`#7A2E2A` family,
  steel-teal counter, bone text `#EDE6DA` — tune by eye vs the "room" reference
- cold: from Deceiver art (`#070B0F`, `#131C28`, `#25384C`, `#687886`)
- sepia + neutral-ink: same treatment
- Rule to confirm: every future release gets its hexes sampled from its artwork,
  core stays constant.

## Phase 3 — Motion + anti-brand → THE SPEC  [OPEN]
1. Motion identity A/B renders: hard-industrial (0ms hits, glitch, shakes) vs
   cinematic slow-burn (pushes, light-leak) — likely both, keyed to content register.
2. Anti-brand one-liner: approve/edit the draft ("Never: bright/poppy candy, clean
   corporate, cartoonish, glossy stock, startup-gradient. IoS is grain, shadow, one
   light source, matte.") — governs images AND video.
3. **Output: `docs/brand/frame.md` v1 (the video brand spec) + the logo sting rendered
   + the watermark. MASS PRODUCTION UNLOCKS HERE.**

## Phase 4 — Image-side dimensions  [OPEN, from CONTROL-PANEL.md, doesn't block video]
The four paused questions, one at a time, options generated per question:
faces in generated art (always obscured?) · subject mix (figures/places/objects/symbols)
· real vs abstract · medium/texture dial. Output: updates to `inch_of_shadow_style.txt`
and the image studio defaults.

## Phase 5 — Footage & captions  [OPEN, needs one talking clip from Amir]
First real talking clip: verify matting on sunglasses/night light, then pick caption
defaults from 3 rendered identities (`anchor` safe / `ink` bright / one dark themed).
Output: caption identity defaults into frame.md; the captioned-clip pipeline certified.

## Phase 6 — Convergence (the BIG project)  [LATER, design only for now]
Control panel + HyperFrames + image studio + IG agent as one machine: release skill
triggers video menu rows · brand spec feeds image AND video generation · IG stats loop
feeds back into what gets made. No building here until 1-5 are locked; every earlier
phase is built to slot in.

---

**How to run a phase:** Amir says "phase N" (here or any chat that reads this repo).
Claude prepares the renders/options FIRST, then asks the questions one at a time,
records answers in this file + the target artifact, and names what unlocked.
