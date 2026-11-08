# Half the Night cover, direction: 90s noir animation / dark deco

Session started 2026-11-04 (side session of the cover work). Files: `artwork/edits/htn-noir/`.
History and rules: `plans/half-the-night-cover-v2.md` (not edited here).

## Starting point

- His favourites (short raw prompts, 2026-11-03):
  - A `generated_images/pinocchio-single/make-an-album-artwork-cover-in-a-90s-noi-20261103_233807.png`
    three crooked cream trees, big cream moon, red slashed hill, flat black.
  - B `...-20261103_233827.png` star sky, left half lit, right half switched off (blue dots), figure + city low.
  - C `make-an-album-artwork-cover--noir-sonic-20261103_233847.png` bold condensed title top-left, red moon, figure.
    He likes the FONT and maybe the red moon.
- His refs: BTAS title card (low angle, deco towers, red sky), comic skyline + moon (B/W, flat), villain skyline poster
  (red flat sky, white moon disc, towers).
- Common language: flat shapes, 2 or 3 inks (black, cream, one red), one big disc, low angle, almost no detail.

## Open design questions (asked 2026-11-04)

See chat log below.

## Log
### 2026-11-04 design talk, round 1 (proposed, waiting for Amir)

Questions: 1 which scene leads (A trees / B half the stars / low-angle BTAS), 2 moon size + colour, 3 inks
(black + cream + red, or black + cream only), 4 title place (top-left like C, or bottom band).
Proposed raw prompts (1024, need his go before sending):
- P1 "Album cover in a 90s noir animation style. Flat black night. Three crooked white trees on the right side, a small cream moon high on the left. Lots of empty black for a title. Bold flat shapes, almost no detail."
- P2 "Album cover in a 90s noir animation style. A flat black night sky full of stars, and exactly half of the stars are switched off. A low dark horizon line. No people. Bold flat shapes, empty space for a title."
- P3 "Album cover in a 90s noir animation style, low angle looking up at tall bare dead trees like dark towers, one big moon disc, flat red sky. Bold flat shapes, almost no detail, space for a title."

### 2026-11-04 round 1 renders (Amir: "Render 1 and 3")

- P1 -> artwork/edits/htn-noir/p1-trees-small-moon.png (3 cream trees bottom-right, tiny moon top-left, big empty black).
- P3 -> artwork/edits/htn-noir/p3-low-angle-red-sky.png (low angle, black dead trees on flat red, cream moon top-right).
- Sheet: artwork/edits/htn-noir/htn-noir-round1.jpg
- Note: raw_render.py names files by prompt start + second; two parallel renders with the same start overwrote each
  other, so P3 was sent twice (3 paid renders for 2 images). Run renders one after another from now on.
- 2026-11-04 update from the main session: raw_render.py now defaults to MEDIUM quality (~$0.05 per draft, was ~$0.21 at high)
  and gives every file a unique name, so parallel renders are safe again. --quality high only for a final Amir asks for.
- Sheets sent 2026-11-04: artwork/edits/htn-noir/htn-noir-from-main-chat.jpg (1-8: v6 short prompts 1-3, dark deco 4,
  B/W comic ink 5, his refs 6-8) and htn-noir-round1-labelled.jpg (this chat's P1 + P3). No new renders.

### 2026-11-04 round 2 proposed ("show me more"), waiting for his go
- R2-1 "Album cover in a 90s noir animation style. Two thin white dead trees far apart on a black hill, a huge flat cream moon low behind them. Bold flat shapes, empty sky for a title."
- R2-2 "Album cover in a 90s noir animation style. Night sky, the left half full of bright stars, the right half dark and empty. One small crooked tree at the bottom. No people. Bold flat shapes."
- R2-3 "Album cover in a 90s noir animation style. A lonely road at night bending into black dead trees, one red moon. Bold flat shapes, almost no detail, space for a title."
- R2-4 "Album cover in a 90s noir animation style. Black dead trees rising like tall towers from below, a cream moon between them, flat dark blue sky. Bold flat shapes, almost no detail."
- R2-5 "Black and white comic ink album cover, Sin City style. White bare trees on pure black, one hard white moon. High contrast, no grey, minimal, space for a title."
- R2-6 "Album cover in a 90s noir animation style. A red hill cuts the picture diagonally, three white crooked trees on it, a small cream moon, black sky. Bold flat shapes, poster feel."
- Round 2 above STOPPED by Amir before anything rendered (no cost). He meant: more options LIKE tiles 1 and 2 of the
  main-chat sheet (trees + cream moon + red hill; half the stars off). Round 2 rewritten as variations of those:
- V1a "Make an album artwork cover in a 90s noir animation style: crooked white trees, a cream moon, a red hill. Black night."
- V1b "Make an album artwork cover in a 90s noir animation style: two crooked white trees on a red hill, a small cream moon, lots of black night."
- V1c "Make an album artwork cover in a 90s noir animation style: crooked white trees on the right, a red hill, a cream moon behind them."
- V2a "Make an album artwork cover in a 90s noir animation style: a night sky where half of the stars are switched off. No people."
- V2b "Make an album artwork cover in a 90s noir animation style: a night sky, half the stars bright, half switched off, a low black hill. No people."
- V2c "Make an album artwork cover in a 90s noir animation style: a night sky split down the middle, stars on one side switched off, a few crooked trees below. No people."
- Rendered 2026-11-04 (medium, 6 x ~$0.05): artwork/edits/htn-noir/v-1a..v-2c.png, sheet htn-noir-round2-variations.jpg.
  1a-1c kept the flat 2-ink language (cream trees, red hill). 2a-2c drifted to anime night-scene look (blue gradients,
  detail; 2a has a city + Parental Advisory stamp, 1c also has a stamp). Stamps are model junk, remove if picked.

## Picks 2026-11-04 (Amir, voice; quick answers, not taste rules)

Main-chat sheet (htn-noir-from-main-chat.jpg):
- 1 (trees, cream moon, red hill): the base from now on. He likes the trees.
- 2 (half the stars off): the colours and the half-side split are "really cool". Without the figure, but he notes the
  figure carries the language; open, keep in mind.
- 3: the red moonlight, the FONT, and the moon's reflection on the water ("super cool").
- 5 (B/W comic ink): the moon SIZE is right, and its stars = what he means by "minimum stars".
Round 2 (htn-noir-round2-variations.jpg):
- 1a and 1c: "wow, really, really good". Both need a smaller moon (target: tile 5's moon size).
- 1b, 2a, 2b, 2c: removed.
- Smaller moon done LOCALLY (no AI, no cost), diameter 126 px = 12% of the frame, same as tile 5's moon:
  artwork/edits/htn-noir/v-1a-small-moon.png, v-1c-small-moon.png (1c: fake Parental Advisory stamp removed too;
  with-stamp copy in build/). Scripts: build/shrink_moon.py (keeps branches crossing the moon, rebuilds the old edge),
  build/patch_1c_branch.py (one hand bridge), build/remove_stamp.py. Sheet: htn-noir-round3-small-moon.jpg.
- 1b, 2a, 2b, 2c moved to artwork/edits/htn-noir/dropped/ (originals still in generated_images).

## Picks 2026-11-04 (Amir): "1a after, 1c before"
- 1a WITH the smaller moon (v-1a-small-moon.png) and 1c ORIGINAL with the big moon (v-1c.png; stamp still to remove).
- 1c clean copy (stamp removed, big moon kept): artwork/edits/htn-noir/v-1c-clean.png.
- Effects step (local, no cost): print_looks.py S1 xerox, S2 halftone, S3 riso, S9 scanlines, S11 halation on 1a + 1c
  -> artwork/edits/htn-noir/looks/, sheet htn-noir-looks-sheet.jpg. Note: S1/S2/S9 turn the red hill white (they are
  1-ink looks), so they lose the red; S11 keeps the colours and adds a red glow; S3 riso goes plum. Colour comes later
  (ramp), so these are about TEXTURE, not colour. For the Canvas later: Blackout Strobe / Negative Flash (effects
  library, rhythm) = trees and stars flashing on the kick.
- "show more looks": all 26 print_looks on both -> looks/htn-noir-1a-all-looks.jpg, looks/htn-noir-1c-all-looks.jpg.
  Worth a look for this direction: S12 dirty window (keeps red, adds dust/stars), S22 blowout (violet, near the ramp),
  S23 monotint (periwinkle = ramp family), S10 pixel, S24 night flash.

## Side page for picks (Amir 2026-11-04: "open it on the side, I tick V")
- https://claude.ai/artifact/ApLxqSzWFAz8Renc7iMbi9 (Half the Night Noir Picks). Build: artwork/edits/htn-noir/page/
  (rounds.json + template.html -> gen.py -> index.html, img/). Ticks in db collection `ticks`,
  doc id <round>--<option>, {round, option, label, v, at}. Read back with ArtifactData list before moving on.
- Round looks-1: 27 looks x 2 (1a small moon, 1c big moon) = 54 cards. Waiting for his V ticks.
- Ticks read 2026-11-04 (15 V). He stopped ticking 1c looks early: "the same" as 1a.
  1a (small moon): As is, S1 Xerox, S2 Halftone, S6 Solarisation, S8 Dither, S9 Scanlines, S11 Halation,
  S12 Dirty window, S20 Night vision, S21 Pixel sort, S23 Monotint.
  1c (big moon): As is, S1 Xerox, S2 Halftone, S4 Engraving.
  Shared by both: As is, Xerox, Halftone.
- 2026-11-04 Amir skipped narrowing ("I wanna see all with text"). Round looks-3 on the side page: his 15 looks with
  type, look first + type last. Title = DIN Condensed Bold (macOS system font, stand-in for the condensed title in the
  'noir sonic' render), stacked HALF / THE / NIGHT, cream. Name = brand face, small, right under the title on the black
  sky (on the hill it vanished in looks that turn the hill pale). 1a title in the gap between the trees, 1c top-left.
  Script: artwork/edits/htn-noir/build/compose_text.py. Final type gets set in Canva.
- 2026-11-04 Amir expected a different font per card. Round fonts-1 on the side page: 1a + 1c as is, 8 title faces
  (all free or macOS system, nothing to buy to test): F1 DIN Condensed Bold, F2 Futura Condensed ExtraBold (liked 09-21),
  F3 Impact (liked 09-21), F4 Mohave Bold, F5 Viking (deco), F6 Gloock, F7 Bodoni 72 Bold, F8 Rockwell Bold.
  My view: F2 / F3 for the bold condensed 90s poster feel; F7 / F6 if it should read as an old noir film title.
  System fonts (Futura, Impact, Bodoni, Rockwell, DIN) need a licence check before release.
- Font ticks (fonts-1, 2026-11-04): F2 Futura Condensed ExtraBold, F3 Impact, F4 Mohave Bold, F7 Bodoni 72 Bold on
  both 1a and 1c; F6 Gloock on 1c only. Not ticked: DIN, Viking, Rockwell. Round looks-3 (looks with text) has no
  ticks yet. Name stays in the brand face (asked, explained; he can ask to vary it).
- Round fonts-looks-1 (27 cards): picked fonts x looks As is / S1 Xerox / S2 Halftone; 1a = 4 fonts, 1c = 5 (+Gloock).
  Files artwork/edits/htn-noir/page/img/fl-*.jpg. Waiting for ticks.

## Noir is THE direction (main chat, 2026-11-04)
- Cut-paper and Polish finished; this chat is the one working chat for the cover. Order: look + font (fonts-looks-1)
  -> elements from the cut-paper + Polish boards -> Canva -> R. Missing colours -> final to the main chat for export.
- Their elements copied (read-only source) into artwork/edits/htn-noir/borrowed/{cutpaper,polish}/.
- Side page now shows several open rounds at once: elements-1 (N1-N2 noir base, C1-C12 cut-paper, P1-P8 Polish) and
  fonts-looks-1. Nothing combined until he names it. Polish rule to keep in mind: no big moon as the MAIN element
  (tour artwork has it), which touches 1c.
- 2026-11-04 Amir: "try the fonts from the other chats". Those are hand lettering in AI renders, not font files, so the
  9 crops were cut out locally (build/extract_lettering.py -> htn-noir/lettering/*.png, cream alpha) and placed on 1a
  and 1c (compose_text.compose_lettering). Round lettering-1 on the side page (L1-L9 x 2). MC2's crop lost part of the
  f ("Halt"); recover from the full MC2 render if picked. For a final at 3000 px the lettering needs a clean redraw or
  vector trace in Canva (crops are ~450 px).
- lettering-1 ticks: all 9 liked ("I liked all the fonts"; L5 ticked on 1c only). Title candidates now = typed F2 Futura,
  F3 Impact, F4 Mohave, F7 Bodoni, F6 Gloock (1c) + lettering L1-L9. elements-1 and fonts-looks-1: no ticks yet.
- Amir 2026-11-04: fonts PAUSED for now (14 candidates kept). Next: elements-1 (which cut-paper / Polish elements come in).

## New idea: searchlight moon over a noir street (Amir by voice in the main chat, 2026-11-04)
"The moon is like a searchlight; a tall building along the frame with windows like the Batman ones; inside the
searchlight/moon it says Inch of Shadow and Half the Night; a noir street." Refs: comic-skyline-moon-bw.png,
batman-villain-skyline-poster.png. Rules: no bat symbol / Batman marks; the moon/beam is rendered BLANK and both names
are our own type layer, in his picked fonts. Proposed raw prompts (medium, ~$0.05 each), waiting for his go:
- S1 "Album cover in a 90s noir animation style. Looking up a dark noir street at one tall building with rows of lit windows running up the side. A huge pale moon glows like a searchlight, a blank empty circle of light. Bold flat shapes, no text, no people, no logos."
- S2 "Album cover in a 90s noir animation style. A noir city street at night, a tall building with rows of lit windows on one side. A searchlight beam shines up from the street and ends in a blank pale moon. Bold flat shapes, no text, no people, no logos."
- S3 "Black and white comic ink album cover. Low angle up a tall building with many lit windows, a big blank white moon behind it like a searchlight. Screen tone sky, flat shapes, no text, no people, no logos."
- S4 "Album cover in a 90s noir animation style. Flat red sky, tall dark buildings with yellow windows rising from below, a big blank cream moon disc. Bold flat shapes, no text, no people, no logos."
- Rendered S1-S4 (Amir: "Render all 4"; medium, 4 x ~$0.05): artwork/edits/htn-noir/searchlight/s1-s4.png
  (sources generated_images/pinocchio-single/*20261104_01564[89]*). No logos or bat marks came out.
  Names inside the moon (our type, Futura Condensed ExtraBold + brand-face name, warm black): s1/s2/s4-names.jpg
  (build/names_in_moon.py). S3's tower covers most of its moon, so no names version. Side page round searchlight-1
  (elements-1 still open; lettering + fonts-looks closed, fonts paused).

### Last try, even more minimal (Amir, Hebrew voice, 2026-11-04)
His words (translated): "Even more minimal. On the right a building lying down, not tall, lying lengthwise; then the
street; and a searchlight that is actually the moon. The street just a colour, say ivory. The text maybe there, or on
the moon / searchlight, not sure. Let's give it one last try."
Proposed raw prompts (medium, ~$0.05 each), waiting for his go:
- M1 "Minimal album cover in a 90s noir animation style. A long low dark building lying along the right side with one row of lit windows, a flat ivory street, and a pale moon shining down like a searchlight. Very few flat shapes, lots of empty space, no text, no people, no logos."
- M2 "Minimal album cover in a 90s noir animation style. A long low dark building lying on the right, a flat ivory street, and a searchlight beam rising from the street that becomes the moon. Very few flat shapes, lots of empty space, no text, no people, no logos."
- M3 "Minimal noir poster, flat graphic shapes only: a long black building lying horizontally on the right, an empty ivory street, one round moon as a searchlight casting a cone of light. Black, ivory and one muted colour. No text, no people, no logos."
- Rendered M1-M3 (Amir: "Render all 3"; medium, 3 x ~$0.05): artwork/edits/htn-noir/searchlight/m1-m3.png
  (sources generated_images/pinocchio-single/*20261104_02001[01]*). Names on the ivory street (Futura Condensed
  ExtraBold one line + brand-face name, warm black): m1/m2/m3-street.jpg (build/names_on_street.py).
  Side page: only round searchlight-2 open now (older rounds hidden, ticks kept).
- Amir on M1-M3: "none. The idea is good, the execution is bad, you lost the Batman language."
  Why: "minimal" + "flat graphic poster" in the prompts pulled it to modern flat vector (navy, khaki), and dropped
  "dark deco", the red sky, the painted-on-black-paper look, the hard shadows and the art deco windows.
  Next prompts keep his idea (long low building on the right, ivory street, moon = searchlight) but put the language
  back. Proposed (medium), waiting for his go:
- B1 "Album cover in a 1990s dark deco animation style, painted on black paper. A long low art deco building lying along the right side with rows of yellow lit windows, an empty ivory street, and a big pale moon shining down like a searchlight. Flat red sky, hard black shadows, no text, no people, no logos."
- B2 "Album cover in a 1990s dark deco animation style, painted on black paper. Low angle from the street: a long art deco building stretching along the right, a searchlight beam rising into a flat red sky and ending in a pale moon, an empty ivory street. Hard black shadows, no text, no people, no logos."
- B3 "Black and white noir comic ink, dark deco. A long art deco building along the right with lit windows, an empty pale street, one big white moon like a searchlight. Heavy black shadows, screen tone, no text, no people, no logos."
- Rendered B1-B3 (Amir: "Render all 3"; medium, 3 x ~$0.05): artwork/edits/htn-noir/searchlight/b1-b3.png
  (sources generated_images/pinocchio-single/*20261104_02023[01]*, *_020229*). Dark deco, red sky, hard shadows came
  back. Names set by us in the calm sky (street text crossed shadows): b1/b2/b3-street.jpg (build/names_on_street.py,
  now takes ink/stack/size). Side page round searchlight-3.
- Amir on searchlight-3: "the fonts you used are nice" (Futura Condensed ExtraBold title + brand-face name).
  "Never mind, let's go back to the tree option and focus on that." Searchlight idea parked (files kept in searchlight/).
  Side page: reopened the tree rounds fonts-looks-1 and elements-1.

## Trees, two paths (Amir, 2026-11-04)
His ask: path 1 = cut-paper torn cuts (C1/MC2/C2 vibe, a little), a few small C4 gold stars, the red owl moon (P3);
never all combined everywhere, mixed per card. Path 2 = minimal base: red moon with changed hill colours, a purple
option, and the C3 gold crescent in place of the round moon. All local, no AI, no cost.
- Tools: build/variants.py (torn band, stars, owl moon, crescent, moon/hill recolour). Owl disc cut clean from the full
  Polish render: borrowed/polish/owl-red-moon-disc.png. Purple = #44214C sampled from MC2 purple.
- A torn BLACK corner (MC2) is invisible on our black sky (only the cream edge shows), so path 1 uses a torn COLOUR
  band behind the trees instead.
- Files: artwork/edits/htn-noir/variants/trees-path1-*.jpg (1a A1-A5, 1c C1-C5), trees-minimal-*.jpg (M1-M6 x 1a/1c).
  Side page rounds trees-path1 + trees-minimal (no titles on them).
- Ticks 2026-11-04 (16 V; more instructions coming by voice):
  path 1: 1a A2 owl moon, A3 owl + stars, A5 red band + owl + stars; 1c C2 owl + stars, C4 stars only.
  minimal: 1a M1-M6 all (red moon purple/black/ivory hill, purple hill, crescent red/purple hill);
  1c M2, M3, M4, M5, M6 (not M1). Not ticked: torn band alone (A1, A4, C1, C3, C5).
- Amir (Hebrew voice, 2026-11-04), translated: "By cut-paper I did not mean the fill, the red and purple you filled; I
  meant only the cuts, that white-ivory line. I thought it might trace the trees, or trace the hill, minimal, on the
  side, as a texture. That's why I barely ticked those. The half moon: you made it only yellow; in some it's really
  nice, but in M5 and M6 maybe see it in the colours you chose too. We're progressing, good."
  -> Next: torn ivory paper EDGE only (no colour fill) along the hill top and/or around the trees; crescent in cream
  and red as well as gold.
- Built (local, no cost): variants.torn_edge (crisp ivory torn-paper line on the hill top where it meets open sky, or a
  thin offset outline around the trees) and variants.crescent_col (crescent in cream / red, paper texture kept).
  Rounds on the side page: trees-torn-edge (E1 hill, E2 trees, E3 both, E4 hill + owl moon + stars; 1a + 1c) and
  trees-crescent (K1 cream/red hill, K2 red/red, K3 cream/purple, K4 red/purple, K5 cream/black; 1a + 1c).
  Files artwork/edits/htn-noir/variants/trees-torn-edge-*, trees-crescent-*. Note: recolour the hill BEFORE adding a
  red element, or the hill recolour catches it (K4 fixed).
- Ticks: torn edge 1c E1 hill, E2 tree outline, E4 hill + owl + stars; crescent 1a K1 cream/red, K3 cream/purple,
  K4 red/purple. Amir: "the previous batch was better in general. The paper cut even less in all of them, and never
  on the moon." -> next: his previous-batch ticks, each with a much lighter torn edge (thinner, only part of the hill
  top), never touching the moon.
- Round trees-light-edge: his 16 previous-batch picks, each with a thin torn ivory line on PART of the hill top only
  (1a x 0.50-0.92, 1c x 0.02-0.48, width 2.6), masked off the moon (rule: never on the moon). M3 (ivory hill) has no
  edge since ivory on ivory would not show. Files variants/trees-light-*.jpg.
- FINALISTS (trees-light-edge ticks, 2026-11-04): 1a A2e owl moon, A3e owl + stars, M1e red moon purple hill,
  M3e red moon ivory hill, M4e purple hill cream moon; 1c C4e stars only, M3e red moon ivory hill, M4e purple hill
  cream moon. Files artwork/edits/htn-noir/variants/trees-light-<base>-<code>.jpg.
- Amir: "show me them in the R. Missing palette". build/rmissing.py maps a cover into the ramp, two ways:
  'shares' (re-spread to darks 17 / low-mids 35 / mids 36 / lights 12; ranked on a smoothed coarse luminance so the
  flat night stays one tone, first try spread the paper grain into blotches) and 'straight' (luminance as is, keeps
  the black night). Red/purple/cream all become tones of the one ramp. Files variants/rmiss-{shares,straight}-*.jpg,
  side page round rmissing-1.
- rmissing-1 ticks (10 V): shares 1a M1, 1a M3, 1c C4, 1c M4; straight 1a A2, 1a A3, 1a M3, 1a M4, 1c C4, 1c M3.
  Next: the same 10 with the title (Futura Condensed ExtraBold + brand-face name, ink = lightest ramp tone #B4C2F8).
- Round rmissing-title-1 on the side page: the 10 with title (compose_text.title_on), files variants/rmiss-title-*.jpg. On 1a the name sits near the hill top; final spacing gets set in Canva.

## Effects step (Amir, 2026-11-04)
"Now add our effects tools. I don't want to work by ticking, it must be broader, and I need to see the effects not
100% wet all the time." -> Effects mixer on the side page: his 10 R. Missing picks as bases; every print_looks look
pre-rendered as base -> look -> ramp (pipeline order, so all stays in the palette); in the page he picks a base, an
effect, a wet/dry slider, an optional second effect, title on/off, and saves the setting (db collection `mixes`).
- EFFECTS MIXER live: https://claude.ai/artifact/BeciA7jyQNGxJSZepHCp84 (Half the Night Mixer). Build:
  artwork/edits/htn-noir/build/mix_prerender.py (all 26 looks x his 10 picks, coloured cover -> look -> ramp) ->
  page/img/mix/ -> packed into one sheet per cover page/img/sheets/<pick>.jpg (6 x 5 tiles of 720) + title-1a/1c.png;
  page source page/mixer_template.html + mix.json -> mixer.html. In the page: cover, effect 1 + strength, effect 2 +
  strength, title on/off, hold to compare, Save (db collection `mixes`: base, e1, m1, e2, m2, title, note, at).
  Read his saved mixes with ArtifactData list mixes. Checked: sheets line up with the looks; I could not open the live
  page (built-in browser not signed in to claude.ai), so the in-page blending is untested by me.
- Amir: "can you do it on the playground? I think it's the right time. When we built it we said it can be adapted.
  Keep some of the features we already have." Checked RM /playground/<slug> (Machine-21, release_manager/playground.py
  + templates/playground.html): it already has look + strength (wet/dry) + size + blend, moods, brightness/contrast/
  grain, hue/sat/tint/duotone, accent, title + name fonts/size/spacing, Spotify/record/IG previews, downloads, saved
  versions (into releases/pinocchio-single.json brand.playground.versions). Missing vs the mixer: a 2nd look layer,
  the R. Missing ramp, switching between our 10 covers (base is ONE image from the release file, which this chat may
  not edit). Proposed plan sent to Amir, waiting for his go; webapp.py changes need an RM server restart (his call).
- PLAYGROUND ADAPTED (Amir: "Yes, go ahead", 2026-11-04). Release Manager /playground/pinocchio-single now has:
  cover picker (any images in artwork/**/playground-covers/<slug>/; ours: artwork/edits/htn-noir/playground-covers/
  pinocchio-single/, the 8 coloured finalists, so no release-file edit), a second look layer (strength, size, blend),
  the release palette (R. Missing ramp, off / straight / middle-tone shares + amount, after the looks), text colour
  (mood ink / palette lightest / darkest / custom), and "Hold: without effects". Files: release_manager/playground.py
  (cover_dirs/covers/cover_path, RAMPS), webapp.py (covers + ramp passed, image route takes ?cover=name),
  templates/playground.html, static/style.css (.pg-ramp), tests/test_playground.py (+2 tests, 8 pass). JS syntax
  checked. NOT browser-tested: needs an RM restart (Amir's call); my test server could not read the Desktop folder.
  Backups of the 3 files before the change: scratchpad (*.bak).
- 2026-11-04 03:10: RM restarted on Amir's "Yes, restart it" (old PID 20059 stopped; new server in the app's terminal
  tab "Release Manager"). Checked live: 9 covers in the picker, second look + palette render, no console errors.
  Amir is also working on RM in another chat: the restart loaded every RM file on disk, theirs included.
- Amir (voice): the detailed playground is too much for this step; he wants to SEE all effects at once on our art,
  one wet knob for all, easy and clickable; Instagram/record later. Built the EFFECTS WALL (his "y"):
  RM /playground/pinocchio-single/wall (template playground_wall.html; routes in webapp.py: wall, overlay,
  wall-kept API, image ?w= for small tiles). Top: the 8 covers + release base as thumbnails, one big Wet knob (all
  tiles), palette colour / R. Missing / R. Missing mid tones, title on/off, only kept. Grid: Original + all 26 looks.
  Click a tile: big view with its own knob, Instagram + record preview, Keep, "Open in the detailed playground"
  (writes cover/look/strength/palette into that page's saved state). Kept list: plans/playground-wall/<slug>.json.
  Title overlays: playground-covers/pinocchio-single/<cover>.title.png (white, tinted in the page). Link to the wall
  at the top of the detailed playground. Tests 10 pass, JS syntax ok. Needs an RM restart (asked Amir).
- 2026-11-04 ~03:25: RM restarted on Amir's word ("both chats need to restart now"); server in terminal tab c2. Wall checked live: covers strip, knob, 27/27 tiles drawn, no console errors.
- Amir: "are those the effects I chose? also very zoomed in, I want to see more in one scroll". Wall now opens on HIS PICKS (WALL_PICKS in playground.py: the 11 looks he ticked in round looks-1 + Original), with an 'all 26' switch, smaller tiles by default (220 px) and a tile-size slider. Tests 10 pass. Needs one more RM restart.
- RM restarted again (his "Yes, restart"), terminal tab c3. Wall checked: opens on his picks, 12/12 tiles drawn, no console errors.

## R. Missing done properly (Amir 2026-11-04: "you didn't make quality samples and decisions from the R. Missing reference")
- Reference downloaded on his go and KEPT on his word: Shadow Archive R-020 (docs/brand/shadow-archive/examples/R-020/01.jpg,
  refs/R-020.md with the study), copy in artwork/edits/htn-noir/reference/.
- Study in one line: one blue-violet hue, LIGHT and airy (median mid-light), textured crumpled big field, darks only as
  thin branch lines + the bottom corner, one lightest subject, light falling off downward. Our first pass (luminance
  map of a black night) kept the night dark = the opposite. New approach: colour by ROLE (sky / trees / hill / ground /
  moon / stars / torn edge / title), build/rmissing_roles.py.
- Samples (local, no cost): 3 recipes x 2 covers (1a owl moon + stars, 1c stars), with title in a role ink.
  Moonlit wall (closest: light textured sky t .72-.84, dark trees .11, hill .33 falling to the dark bottom, moon 1.0
  with soft glow, title dark), Night wall (mid-dark textured sky .40, light trees .90, dark hill, glowing moon, title
  light), Flat ink (the same roles, flat, our noir graphics). Files artwork/edits/htn-noir/rmissing-roles/
  (<key>-<code>-<recipe>.png + -title.jpg). Side page round rmissing-roles, the reference first.
  Fixes on the way: moon was lost in the light sky (capped the sky below the moon tone); the black ground turned light
  where it touched the sky (sky now = only above the hill line).
- rmissing-roles ticks: 1a Moonlit, Night wall, Flat ink (all three); 1c Moonlit, Night wall. Role colouring approved; next: into the effects wall (colour switch = original / Moonlit / Night wall / Flat ink).
- Role colourings rendered for all 8 covers as playground-covers/pinocchio-single/<cover>--{moonlit,nightwall,flatink}.jpg
  (+ title overlays). Note: in one hue, red / purple / ivory hill versions become the same picture; what still differs
  is owl or not, stars, 1a vs 1c. Wall: colour switch = original colour / Moonlit wall / Night wall / Flat ink (role
  version as the base, the look on top, then the ramp straight to pull the look's colours back into the palette; title
  ink per recipe). Amir asked mid-way: a title size slider -> "title size" 50-170% (scales the title around its own
  top-left). Server accepts any recipe name for kept picks. Tests 10 pass, JS ok. Needs an RM restart.
- RM restarted (his "Yes, restart"), terminal tab c4. Checked live: colour switch original/Moonlit/Night wall/Flat ink, title size slider, 12/12 tiles, no console errors. His first kept pick on the wall: S21 Pixel sort 100% on 1a owl moon + stars (old brightness palette). Not committed yet.
- Amir: "keep the old R. Missing" -> the wall's colour switch keeps the old brightness mappings too: 'R. Missing (old, by brightness)' and 'R. Missing mid tones (old)', next to the role versions. Needs an RM restart.
- RM restarted (his "Yes, restart"), tab c5. Checked: 6 colour options incl. the two old ones, 12/12 tiles, no errors. Not committed yet.
- Amir: "in these images this tree blocks the text, twist it or remove it so the text can breathe". REMOVED the third
  tree on 1a (the one at x 355-497 with its twigs) by local inpaint: build/remove_title_tree.py ->
  v-1a-small-moon-clear.png (original kept). variants.BASE["1a"] now points to the cleared art; the 5 1a covers and
  their 15 R. Missing versions in playground-covers were rebuilt from it (old 1a covers still in variants/
  trees-light-1a-*.jpg). Wall URLs now carry each cover's file version so the browser never shows the old tree.
  Needs an RM restart.
- Amir: "keep without the tree as an option, don't remove all the others yet". The 5 1a covers are back WITH the tree
  (same names, variants.BASE["1a"] back to v-1a-small-moon.png), and the cleared versions are extra covers named
  <cover>-no-tree (+ their --moonlit/--nightwall/--flatink and title overlays). Wall now shows 13 covers. Needs an RM restart.
- RM restarted (his "restart rm"), tab c6. Checked: wall cover strip shows the 1a covers with and without the tree side by side, 13 of ours + the original single cover, no console errors. Not committed yet.
- Amir: "night wall and flat ink not needed" -> hidden from the wall's colour switch (files kept). RM restarted (his "Yes, restart"), tab c7. Checked: 4 colour options (original, Moonlit wall, two old R. Missing), 14 covers in the strip, no errors. Not committed yet.

## Round plan from here (proposed 2026-11-04, Amir asked "how do you suggest we work from here")
1. Cover first, no effects: wall at Wet 0%, Amir picks 1-2 covers (tree or no tree, owl or not, 1a or 1c, colour).
2. Effects only on those covers: Wet knob, Keep 3-5 at most, he says "Kept are in".
3. Claude renders each kept pick full size with the title, side page with V ticks, Instagram + record size.
4. Type: unpause fonts, test only Futura Condensed + 2-3 of the 14 saved, on the winning cover.
5. Second opinion from the other model (Fable) once, when nearly final.
6. Canva final assembly (art, title, name as layers), R. Missing colours, export, final to the main chat.
Rule: no new directions while narrowing; new ideas go on a later list.

## DECISION 2026-11-05: 1a = main artwork, 1c = campaign (later)
Amir in the main chat: "main artwork will be 1a"; 1c stays for the campaign. He wants to compare them in a friendly way
on the RM page, not on a sheet -> wall got a "Compare two covers" view (button at the top): A and B big side by side,
or "One at a time" (click the picture / arrow keys / space flips A and B), own effect + Wet, same colour and title as
the wall; defaults A = first 1a cover, B = first 1c cover, saved per browser. Tested on a temporary copy (port 5099),
no console errors; tests 10 pass. Needs an RM restart (asked Amir).
- RM restarted (his "Yes, restart"), tab c10. Compare button live on the wall, no errors. Not committed yet.
- Amir: "I need a slider so I can go back and forth under each image like a gallery" + "an option for adding and
  removing text each time". Compare view: under each picture ‹ slider › and "n / N"; "main artwork only (1a)" on by
  default; "text" checkbox (same switch as the wall's title). Tested on temp copy :5099, no errors. Needs an RM restart.

## WORKFLOW TO THE FINAL (proposed 2026-11-05, main artwork 1a only; Amir: "elements first, then colours, guide me")
1. ELEMENTS, in the original colours (black sky, cream trees, red hill) so only the elements differ. Element builder
   on the compare page, local renders, no AI, no cost: moon cream / red / red owl; stars none / few; middle tree
   keep / remove; cut-paper ivory line on / off (24 combinations). Amir slides and keeps 1-2.
2. COLOURS on the chosen elements: hill colour (red / purple / ivory) x palette (original / Moonlit / R. Missing old).
   Keep 1.
3. TEXT: title face (Futura Condensed + 2-3 of the 14 saved), size, place; the name line. Keep 1.
4. EFFECTS: the wall at Wet 0 up; "none" is a fair answer. Keep 1.
5. CHECK: small sizes (Instagram, Spotify thumb, record), second opinion from Fable once.
6. CANVA: assemble as layers (art / title / name), final nudges, export, final to the main chat.
Rule: one stage at a time, no going back unless Amir says so; ideas for later go on a list.
- Amir 11-05: no more asking before RM restarts; I restart myself after changes, his saved work kept (memory updated). Restarted, tab c12: compare slider + text switch live, no errors.
- STAGE 1 ELEMENT BUILDER BUILT (Amir "Yes, build it", 2026-11-05): RM /playground/pinocchio-single/elements (link
  "Elements (stage 1)" at the top of the wall). 24 local renders, build/elements.py ->
  artwork/edits/htn-noir/playground-elements/pinocchio-single/el-<moon>-<stars>-<tree>-<line>.jpg (+ el.title.png).
  Page: A and B side by side or one at a time, per picture switches Moon cream/red/red owl, Stars none/a few, Middle
  tree keep/remove, Cut-paper line off/on, a slider + ‹ › through all 24, Keep (saved to
  plans/playground-wall/pinocchio-single-elements.json), text on/off + title size. Code: playground.py
  (element_path, elements_kept, elements_toggle), webapp.py (3 routes), templates/playground_elements.html,
  2 new tests (12 pass). RM restarted by me (standing OK), tab c14, checked: switches, slider, keep/unkeep, no errors.
- Amir: "owl is an element, not only red by default" -> Owl is its own switch (none / on the moon), on a cream OR red
  moon (owl disc recoloured to the art's moon cream locally). Now 32 combinations: el-<moon>-<owl>-<stars>-<tree>-<line>.jpg.
  Amir: "paper cut slider changes elements in the image" -> checked by pixel diff: line on vs off changes ONLY the
  ivory line (top of the hill + a short piece low right); asked him what he saw. RM restarted (tab c15), no errors.
- Amir: switching the line showed the owl + the middle tree he had removed -> the page STARTED with owl on + tree kept. Now both pictures start from his decisions: tree removed, no owl, no stars, line off (A cream moon, B red moon); old saved page state reset. Turning the line on now changes only the line (checked). RM restarted, tab c16.
- Amir: the slider under each picture walked through all combinations, so moving it changed elements. He wants that slider ONLY for the paper-cut vibe. Gallery slider removed; under each picture now 'Cut-paper' 0-4 (0 none, 1 thin/short ... 4 strongest, kept off the messy left grass area and never on the moon), the cut-paper on/off switch is gone. 80 renders el-<moon>-<owl>-<stars>-<tree>-<0-4>.jpg. Checked: slider moves only the line, switches stay; no errors. RM restarted, tab c17.
- Amir kept 2 element picks (12:53): el-red-none-few-remove-0 (red moon, stars, no middle tree, no line) and
  el-red-on-few-remove-3 (same + owl + cut-paper 3).
- STAGE 2 COLOURS BUILT (Amir "do it", 2026-11-05): RM /playground/pinocchio-single/colours (links from Elements).
  build/colour_layers.py cuts each kept pick into soft masks (hill, trees, moon, owl, stars, line + paper-texture
  shade) in artwork/edits/htn-noir/playground-colours/pinocchio-single/<pick>/; the page paints every element live,
  so any mix works without a render per combination. Per element colour swatches: hill (hill red / red / purple /
  ivory / black), moon (cream / red / purple / ivory), owl (black / purple / red / cream), trees (cream / ivory / red /
  purple), stars (gold / cream / red / purple), cut-paper line (ivory / cream / red / purple). Purple = the earlier
  cut-paper purple #44214C. Shuffle = random colours for unlocked elements; lock per element; Original colours;
  Keep -> plans/playground-wall/pinocchio-single-colours.json. A/B side by side or one at a time, text + title size.
  Code: playground.py (colour_* helpers), webapp.py (3 routes), templates/playground_colours.html, 1 new test (13 pass).
  New element picks need `python3 artwork/edits/htn-noir/build/colour_layers.py` to appear here. RM restarted, tab c18,
  checked: rows per element, lock + shuffle, no errors.
- Amir: "I can't see it" (his browser had only reloaded /elements, the colour link was small in the header). Added a big 'Next: colour your kept picks (stage 2)' button under Kept on the Elements page and a 'Colours (stage 2)' button at the top of the wall. RM restarted, tab c19.
- Amir: "I still want the basic option to change elements in the image" -> the colour page now has, per picture: Elements (Owl, Stars, Middle tree switches + Cut-paper slider 0-4) AND Colours (per element + Shuffle + locks). Masks cut for all 40 element combinations (moon colour is painted, so moon is no dimension), ~19 s local. Starts from his 2 kept element picks. RM restarted, tab c21, checked: switches, slider, shuffle, no errors.
- Amir: "make this section look nicer, it's hard to pick" + "a button A to B". Colour rows now one card per element: label + current colour name, big round swatches (name on hover), a lock icon at the end (locked card gets a gold border). Top bar: Copy A -> B and Copy B -> A (copies elements, colours and locks). His first kept colour version is safe in plans/playground-wall/pinocchio-single-colours.json. RM restarted, tab c22, checked, no errors.
- Amir: "is shuffle based on our rules? 60-30-10, golden ratio, all those" -> it was pure random. Found our collected rules in docs/brand/effects/effects.json (colour-60-30-10 from R-013, value-70-20-10, comp-rule-of-thirds, comp-golden-ratio, comp-rule-of-odds). Added 'Smart shuffle' next to Shuffle: tries 600 mixes (locks kept), drops unreadable ones (moon = hill colour, moon too dark on the sky, owl not standing out, trees vs hill), scores 60-30-10 colour shares + 70/20/10 light/dark + accent on the moon, picks one of the best 8. Under each picture a readout of the measured shares. Thirds / golden ratio are placement rules -> text stage. Note: the black sky alone is ~67% of the picture, so the colour split lands near 67/23/10. RM restarted, tab c23, checked, no errors.
- Amir: "add undo button for A and B" -> '↶ Undo A' / '↶ Undo B' under each picture; each picture has its own history (60 steps, this page load): colour clicks, element switches, cut-paper slider, both shuffles, Original colours, copy into it, loading a kept one, locks. His kept colour versions stay in the file. RM restarted, tab c24, checked: shuffle then undo restores exactly, no errors.
- Amir kept 7 colour versions by 13:22 (plans/playground-wall/pinocchio-single-colours.json); newest = red hill, ivory
  moon, black owl, purple trees, purple stars, ivory cut-paper line (owl, stars, no middle tree, cut-paper 2).
- STAGE 3 TEXT, round text-1 (Amir: "before effects, do you have a newer way to present the text? show me a few"):
  build/text_layouts.py paints his newest save from the masks and sets 6 layouts (Futura Condensed ExtraBold + brand
  face, local, no AI): T1 today's stacked block, T2 one big line with the trees IN FRONT of the letters, T3 a huge
  NIGHT half sunk behind the hill, T4 a torn ivory paper label with black letters, T5 small wide-tracked film credit at
  the top, T6 the title along the hill's curve in black. Files text-layouts/T*.jpg (2048) + thumb-check-300.jpg
  (all read at 300 px; T5 is the weakest small). Side page round text-1, V ticks (artifact ApLxqSzWFAz8Renc7iMbi9 v19).
- Amir: not those, he wanted something basic: the text in different positions, different fonts where they fit better, me as the designer. Round text-2 (replaces text-1 as the open round, text-1 closed and kept): build/text_positions.py, 8 options on his newest save: P1 today (centre, Futura Cond), P2 top line Bodoni 72, P3 right column under the moon Gloock, P4 one line on the horizon Mohave, P5 black on the hill Futura Cond, P6 bottom right stacked Rockwell black, P7 centre deco Viking, P8 top two lines Impact. Checked at 300 px; fixed overlaps with the moon, the trunk, the edges and the hill shadows. Side page v20.
- DECISION 2026-11-05 (Amir): text stays as we worked it so far = P1 (centre of the sky, Futura Condensed ExtraBold,
  name in the brand face) is the main. SIDE OPTION kept: P8 (two heavy Impact lines at the top) with the title layer
  masked UNDER the trees, a blurry vibe. Rendered sharp + soft (5 px blur at 2048) as
  text-positions/P8-under-trees-{sharp,soft}.jpg. Next per plan: effects (stage 4).
- Amir: side page with his saves in medium thumbnails, look-alikes next to each other, to choose. Round kept-colours (side page v21): all 7 colour saves with the P1 title (kept-colours/K1-7.jpg), grouped by measured likeness (64 px mean difference): pair 2+3 (ivory hill, differ only in the line), pair 4+5 (red hill cream trees, stars + line), pair 6+7 (red hill purple trees, stars only), save 1 alone (black hill). Waiting for his ticks.
- Amir: "I still like them all, move to the effects". STAGE 4 EFFECTS: his 7 colour saves exported as wall covers playground-covers/pinocchio-single/1a-save-1..7.jpg (2048, painted from the masks) + .title.png (today's P1 title, white, tinted by the wall). Wall strip: the 7 saves first, a gold divider, then the older covers; first visit opens on save 1 with original colour. RM restarted, tab c25, checked: 12 tiles draw, no errors.
- Amir: still too many options, page not presented well (to improve later); first remove effects he is sure don't fit. Wall: every effect tile has '✕ doesn't fit' (removes it from the wall, saved in plans/playground-wall/pinocchio-single-hidden.json), 'show removed (n)' checkbox, '↺ bring back' on removed tiles. Test hide/bring-back round trip left the list empty. RM restarted, tab c26, no errors. Open: improve the wall's presentation.

## 2026-11-05: IG grid preview
- One Graph API read of his own feed (1 call + 12 thumbnails, approved by Amir). The newest post on the feed is 2026-07-10.
- `build/ig_grid.py` puts each of the 7 colour saves (with the P1 title) as the newest post above his real last 11 posts. Tiles are 3:4, as the IG profile grid shows them, so a square cover loses 12.5% on each side. The title and the moon still fit.
- RM: /playground/pinocchio-single/ig-grid, opened with the "On my IG grid" button on the wall.

## 2026-11-05: effects cut (stage 4)
- Amir removed 15 of 26 effects: Engraving, Cyanotype, CRT, Halation, Pixel, Softclub, Emboss, ASCII, Blowout, Camcorder, Monotint, Monotint night, Pictorialism, Riso, VHS.
- 11 left: Xerox, Halftone, Solarisation, Dither, Scanlines, Dirty window, Anaglyph 3D, Thermal, Night vision, Pixel sort, Night flash.
- Starred on Save 2 at 50%: Thermal, Night vision, Night flash. Side-by-side sheet: ig-grid/effect-picks-save2.jpg.
- Amir 11-05: pause the effects stage here and keep the 11 effects as the options. Back to the compare view, where each pane (A, B) now has its own effect and Wet. The effect list holds only the effects not removed from the wall.

## 2026-11-05: stage 3b Layout page + effect mixer
- Layout page: /playground/pinocchio-single/layout (buttons on the Colours page and the wall). It builds one of the 7 colour saves live from its layers.
  - Title: 8 faces (Futura Cond ExtraBold, Impact, DIN Cond, Bodoni 72, Rockwell, Gloock, Mohave, Viking), 1/2/3 lines, left/centre/right, size, line spacing, letter spacing, 6 colours.
  - Name: Marcellus, under the title / top / bottom.
  - Guides: thirds, golden ratio, golden spiral (turnable), centre. Magnet and snap.
  - Moon + owl can be dragged and resized, and the old place is cleared to the sky. Owl and stars on/off.
  - Keep goes to plans/playground-wall/pinocchio-single-layouts.json. Live IG grid.
  - Known limit: the moon is always drawn in front of the hill, so it can't set behind the horizon. Drag range is kept to the sky.
- Compare: each pane mixes up to 3 effects, each with its own amount. Shares over 100% are scaled to 100%, and the original keeps whatever is left.

## 2026-11-05: step back on the elements (Amir)
- Amir isn't sure about the two stars by the NIGHT text. He wants to flip or change some trees, maybe new trees in a similar style to continue the story and give more continuity. Depth is for a later step.
- Done locally on the Layout page:
  - each star on/off or dragged on its own (6 stars; 2 are marked "by the title")
  - flip the whole picture
  - middle tree removed/kept
  - cut-paper 0-4
  - the moon's old place is now cleared a bit wider (the faint red rim is gone)
- Fonts:
  - Title: 8 faces in the condensed poster world of today's Futura (Futura Cond, Futura Cond Med, Avenir Cond, Helvetica Cond, DIN Cond, Impact, Mohave, Gill Ultra) plus 4 others.
  - Name: own font (10 options), size, letter spacing, colour. Brand face = Albertus Nova (Canva only), Marcellus is only the local stand-in.
- Compare: the effect menu is now a thumbnail picker by family (Print, Photo chemistry, Screen and video, Light and night), with the removed effects left out. Fixed: removed effects showed when compare opened before the removed list had loaded.
- Emojis on the magic buttons (colours, wall, layout).
- Open: new-style trees. Any new tree drawing is either AI (needs his go per image) or hand-drawn by him; local options are flip, keep/remove the middle tree, and moving existing pieces.
- Amir 11-05, revert: per-tree tools went too deep ("too complex, more decisions for nothing"). Removed from the Layout page: per-tree hide/flip/copy/move/size, the middle-tree switch and the cut-paper slider. Each save keeps its own trees and line. Kept: fonts, name controls, moon move, star hide/move.
- What he meant: generate ONE new tree, just for fun, and add it. AI render, his go first, exact prompt shown before the render.
- New tree: one AI render (gpt-image-2.5-flare, medium, about $0.05) with the prompt Amir approved, cut out locally into playground-extras/pinocchio-single/tree1.png (source render kept next to it as tree1-source.png). On the Layout page it's one element: on/off, mirror, size, "Drag: new tree". It takes the save's tree colour and sits behind the stars and the line.
- Layout page redesign (Amir 11-05: "make it more user friendly, intuitive"). Same tools, new layout:
  - picture on the left, staying in view, with Drag and Guides pills above it and Keep / Undo / Today's text under it
  - on the right: the colour saves as big thumbnails, then 4 tabs: Title, Name, Elements, Grid
  - font cards show the real words in each face ("HALF THE NIGHT", "Inch of Shadow"); "other worlds" folded away
- Name fonts (Amir 11-05: "the one we made with the swans and the ravens"). His saved playground versions on pinocchio-single say the name was UnifrakturCook (versions 4, 5 "last work Oct 17", "last no charter"), written lowercase "inch of shadow" at size 49 and track 13; versions 1-2 used CAT Eckmann; the title was Impact. Added to the Name row: UnifrakturCook, CAT Eckmann, UnifrakturMaguntia, Pirata One (all OFL, already on disk). My first wrong guess (Cinzel from the Farewell cover, plus Ogg, Viking, Cormorant and Forum) is removed; the Cinzel, Cormorant and Forum downloads are in the Trash.
- Inbox fix (11-05, his two screenshots): the Layout page uses the full width (no max-width), the saves grid fills the space beside the picture, and the font rows wrap instead of scrolling. Checked at 1280, 1800 and 2400 px wide: nothing overflows.
- Layout page, 11-05 late: save thumbnails capped at 118px (2 columns). On screens wider than 1400px the controls (text group + tabs) now sit to the right of picture + saves, so there's no dead space; on narrower screens they drop under the picture. Checked at 1800px: no overflow.
- 11-06: every font card on the Layout page (title and name) has a ✕ to remove it. Removed fonts are saved in plans/playground-wall/pinocchio-single-fonts-hidden.json; "Show removed fonts" brings them back faded with ↺. The list starts empty; Amir does the removing.
- 11-06: the new tree now REPLACES a tree instead of being added (Amir). Options on the Layout page, Elements tab: instead of the left thin tree (the one right of the big trunk) / instead of the right small tree / off. The chosen tree is lifted off (its place filled from the pixels beside it), and the new tree stands at its foot at about its height. Still draggable, with mirror and size.

- 11-06: Amir removed colour save 7 from the saves ("remove 7"). It was: {"pick": "el-red-on-few-remove-2", "cols": {"hill": "red", "moon": "ivory", "owl": "black", "trees": "purple", "stars": "purple", "line": "ivory"}, "saved": "2026-11-05 13:22"} . To bring it back, add this entry back to plans/playground-wall/pinocchio-single-colours.json.
- 11-06: Amir removed colour saves 2 and 3 ("remove 2/3", the two ivory-hill saves). They were: [{"pick": "el-red-on-few-remove-2", "cols": {"hill": "ivory", "moon": "red", "owl": "black", "trees": "purple", "stars": "gold", "line": "purple"}, "saved": "2026-11-05 13:13"}, {"pick": "el-red-on-few-remove-2", "cols": {"hill": "ivory", "moon": "red", "owl": "black", "trees": "purple", "stars": "gold", "line": "ivory"}, "saved": "2026-11-05 13:17"}] . 4 saves remain. Layout page also got a 🎨 Colours tab: any element's colour on top of the save (e.g. purple hill), with 🔄 back to the save's colours and 🎲 shuffle; kept layouts store the colours.
- 11-06 font licence check (Layout page fonts after his removals):
  - Free, fine for the cover: Mohave, Gloock, Pirata One, Jost (all OFL); Viking (1001Fonts Free For Commercial Use).
  - Mac system fonts: Apple's licence lets you display and print with them, and doesn't speak to album covers. Brand rule: buy the licence before anything public.
    - Futura Condensed ExtraBold: Futura PT $39, Futura ND $45.25, Futura Now $53.99 a style (MyFonts, 11-06)
    - Impact: Impact Std $40.99 (MyFonts) / $49 (fonts.com)
    - Gill Sans: $61.99 a style (fonts.json)
    - Not priced yet: Avenir Next Cond, Helvetica Neue Cond, DIN Cond, Rockwell, Bodoni 72, Copperplate, Futura Medium, Avenir Next
- 11-06: magic buttons on the Layout page (above the picture): 🎲 Colours, ✨ Smart colours (readability rules: moon not the hill colour and clear of the sky, owl clear of the moon, trees clear of the hill), 🎲 Effect (a random one of the 11 kept, Wet 30-70%), ✕ No effect. The Colours tab now also has "Effect on top" with all 11 and a Wet slider. The effect runs locally on the server (print_looks), on the picture without text; the text sits on top. Kept layouts store colours + effect.
- Fonts: Avenir is a Mac/Monotype font, not free (buy before release).
- 11-06: Layout page: a lock (🔓/🔒) on every colour row, and one on the effect; all shuffles keep locked colours and 🎲 Effect keeps a locked effect. The Colours tab's 🎲 Shuffle now uses the smart rules. Ctrl+Z / Cmd+Z = Undo.
- 11-06: ✨ Smart colours reworked (Amir: "repeats itself, hills always dark"): the hill is picked first from all 6 hill colours (a different one each time unless locked), any mix passing the readability rules can win, and the last 8 results never come back. Test: 12 presses gave all 6 hill colours.
- 11-06: effect no longer blocks the Layout page (Amir: "heavy and buggy"). Every change draws at once (about 0.1 s) with the last picture of the same effect, the server is asked only after 300 ms of calm, and the real effect drops in when it's ready (about 1-3 s). Up to 12 pictures are cached, so kept thumbnails no longer push out the main one.
- 11-06: Amir removed S12 Dirty window; 10 effects left.
- 11-06: fixed "the new tree moves when I play with the effect": the page reused an effect picture made from the previous state, so the tree showed at its old place under the effect. Now it shows the plain picture with a small "adding the effect…" note until the right effect is ready.
- 11-06: Layout page, Elements tab: 🦉 Owl size slider (40-180%), on top of the moon size; Moon back resets it too.
- 11-06: Amir removed S2 Halftone ("not working"); 9 effects left.
- 11-06: Layout page effects now mix up to 3 at once, each with its own Wet (Colours & effect tab: pick from the 9, slider, ✕, ➕ add). Shares over 100% are scaled to 100%; a line shows effects % vs picture %. 🎲 Effect gives one main effect (30-70%) and sometimes a second for texture (10-30%); the effect lock keeps the whole mix. Kept layouts store the mix (fxmix).
- 11-06 (Fable): bug pass. Fixed: the 4 save thumbnails were drawn with the current colour changes (so they all changed colour after a shuffle); a kept layout missing a newer field (effect mix, owl size) borrowed it from the current state when loaded or drawn; two effect requests at once could read a half-written cache file (500). Added ✕ None in the effect rows.
- 11-06: Layout page: ⇄ Compare A / B of the kept layouts (side by side or one at a time, ‹ slider › under each, click or space to flip, Esc to close, "Open in the editor" loads that layout). Effects are waited for, so both sides show the full result.
- 11-06: A / B now opens on the main page in place of the editor picture, across the full width (about 714 px per picture at 1800 px), with the editing controls hidden; "Back to editing" or Esc returns.
- 11-06: fixed the squeezed controls on wide screens (his screenshot): the kept-layouts row (16 keeps) and the toolbar stretched the picture column to about 1470 px, so the controls got about 140 px. Both now fit the picture width; at 2300 px: picture 720 + saves 118, controls 1072.
- 11-06: Layout page: 🏆 Tournament (last 10 kept layouts). Play-in for the 4 oldest (2 matches), then quarter-finals (4), semi-finals (2), final: 9 picks. Click the picture, the button or ← →; undo a pick; a bracket with thumbnails under it; the champion opens in the editor. Nothing is saved by the tournament itself.
- 11-06 02:4x: the tournament code was lost from the working tree when a ⚙️ System session rewrote git history (its commit 08c57d2, which had swept in the tournament, was dropped). Restored from 08c57d2 and committed on its own. Amir's data (16 keeps, effects, saves) was never touched.
- 11-06: the tournament leaves out near-twins (same layout and colours, effects within about 7%; the newest plays). Today: #8 is a twin of #9 (Anaglyph 7% vs 3%), so the 10 are #6, #7, #9-#16.
- 11-06 tournament note (Amir): picks A (#9: hill red, red moon, purple trees, Anaglyph 3% + Xerox 25%) over B (#11: cream hill, red moon, black trees, cream stars, purple line) in the semi-final, BUT he really likes the trees and shades in B: black trees, which the Xerox turns into a grey sketchy texture. Idea to try: #9 with black trees (close to #12, which has the bright red hill).
- 11-06: Amir's colour rule (he had it from the start): fewer colours. Black (sky + trees) 60, purple hill 30 for the psychedelic acid feel, red ONLY on the moon 10. Made 3 keeps from #16 (same text, tree, effect): #17 purple hill + red moon + black trees + red stars, #18 the same with cream stars, #19 reference with hill red.
- 11-06: A / B can be opened by link: /playground/pinocchio-single/layout?ab=9,17 (keep numbers as shown).
- 11-06: effects per element (Amir's 5 notes: deep red moon #1, moving trees from Anaglyph #2, tree lines from Xerox #3, dark halo round the owl #4, #17 colours #5). Each effect row now has a "where": whole picture / trees / moon + owl / hill / all but the moon. With any "where" set, effects are layered over their part at their Wet (top row first); masks come from the colour layers (trees + new tree, moon + owl, hill minus trees and moon). Tested on #17: Xerox 60% on the trees only gives grey sketch trees, a clean deep red moon and a flat purple hill.
- 11-06: Layout page: up to 5 effect rows; 🖼 All my keeps gallery (21 keeps now) with a switch: each with its own effect, or all with the effect on screen now; click one to open it in the editor.
- 11-06: Layout page, effect rows: "Show all 26 effects" switch brings the 17 removed effects back into the menus, marked (removed). The wall's removed list is not changed.
- 11-06: colour-save column hidden on the Layout page (Amir: not needed any more). RM now reloads page templates by itself (TEMPLATES_AUTO_RELOAD), so page-only changes need no restart and no approval prompt.

## Where we stopped (2026-11-06, ~03:40, Amir going to sleep)
- 22 kept layouts. His LAST picks (the ones to start from next time):
  - #22 (03:36): save 4 + red moon, cream stars, ivory line. Effects: Anaglyph 64% on trees + Thermal 30% (whole) + Xerox 24% on all but the moon + Dither 6% + Night flash 87%.
  - #21 (03:22): save 4 + red moon. Anaglyph 64% on trees + Thermal 30% on hill + Xerox 24% on all but the moon.
  - #20 (03:21): save 4 + red moon. Anaglyph 64% on trees + Night flash 78% on hill + Xerox 24% on all but the moon.
  - Before those, the colour-rule set: #17 (purple hill, red moon, black trees, red stars), #18 (same, cream stars), #19 (hill red reference).
- His direction: few colours (black 60 / purple hill 30 / red moon only 10); the red moon is the strongest element; trees with Anaglyph (movement) + Xerox lines; the moon kept clean (deep red) or a touch of Xerox for the dark halo round the owl; Batman TAS = flat black silhouettes.
- All 22 still use Avenir Cond (title, paid Mac font) + Pirata One (name, free).
- Next: clean the older picks (Amir 11-06: "we can start clean older picks"), e.g. #1-#8 (the first save-4 rounds). Not done yet: show him the list and get his yes, archive them rather than delete. Then the final pick (step 6).
- 11-06 (Amir: "Yes, #1-#8"): archived keeps #1-#8 (the first save-4 rounds, 01:35-02:02) to plans/playground-wall/pinocchio-single-layouts-archive.json, each with its old number. 16 keeps left (he had kept 2 more, now #15-#16); the numbers moved up by 8: old #20-#22 are now #12-#14, the colour-rule set #17-#19 is now #9-#11. Undo: copy the entries back from the archive file.
- 11-06: the new tree is now drawn BEHIND the other trees (in front, its branch looked glued onto the big trunk). Open from Amir: "certain combinations of effects showed it clearly buggy". He'll send a screenshot of one.
- 11-06: Layout page, Elements tab: ✂️ Cut-paper lines on/off (off = the save's layers with line level 0). Kept layouts remember it.
- 11-06: why the new tree still looks glued: its foot sits where the old thin tree stood, right behind the big trunk, so its own trunk is hidden and its branches read as limbs of the big tree. The draw order fix only changes the overlap. Fix is placement (drag it right so its trunk shows, or mirror it). Also fixed: the old tree's loose foot piece (a separate small piece of the trees layer) is now lifted with it.
- 11-06 (Amir: "Yes, move it"): the new tree's spot moved right of the big trunk: foot x 0.227 -> 0.335, y 0.64, height 0.42, so its own trunk shows and it reads as a separate tree further back. Applied as the default for "instead of the left thin tree" and to every keep that had it at the old spot (old values in git).

## Amir's notes per row (main chat, 2026-11-06 evening, voice; quick answers, not taste rules)
Rows as on the picks page (picks.html ROWS):
- Row 5 (#2, cream hill): likes the ivory; we barely use it beyond the text. Prefers purple anyway. Likes the lines in the trees (more real), the grass, the shades; "the quality looks good".
- Row 4 (#9, #7, glow): "we should use the glow", much less, maybe not on the text, in other areas.
- NEW POINT: the text still doesn't feel embedded; it sits a little above the image. Next step after the pick = solve this, then almost done.
- Row 3 (#12, #11, #10, #8, #1): #12 and #11 have a pinkish earth he really likes (Dragon Ball Z Frieza vs Goku / Looney Tunes Marvin the Martian vibe). Really likes the red moon colour in #8 and #10.
- Row 2 (#6, #3): the trees' movement and feel make it real; same Looney Tunes vibe as #8 / #10.
- Row 1 (#13, #5, #4, fits all decisions): likes the trees and shades.
- Stars: wants them yellow. Small, but they give density. Open: same colour as the text or as the moon? Agreed for sure: move/remove the first star hiding behind the F of "Inch of Shadow".
- New batch (#15, #14 moon in branches): very interesting with the moon there; no owl in that version.
- Thermal: unique, a brave choice, maybe not used; nice in yellow-gold. Open what to do with it.
- #18: trees, tree shades, hill and mainly the CORNERS ("more vibe, less computer").
- #16: likes the pixel effect; all effects need fine-tuning.
- Wants the new batch (#14-#18 composition) shown in the colours chosen now.
- Asked which version we are on: #13 is the strongest so far (row 1).

## Final round, 2026-11-06 evening (Amir)
- Default artwork until the final pick: #13 (moon top right, black trees, plum hill, red moon). Versions made from it:
  #19-#24 (subtle: ivory cut-paper edges, star colour, light Thermal / Night flash / Xerox / Pixel sort) and
  #25-#30 (bolder: ivory trees, ivory hill, rough, pink earth, ivory owl, dark glow + red stars),
  #31-#35 (#25 ivory trees + one stronger effect each). Picks page rows: "#13 with the same colours", "Ivory trees (#25) + more effects".
- His short list: #13, #21, #24 / #25, #33, #35. Claude's call: #13 cover, #33 runner-up. Amir: "you were right".
- DIRECTION (Amir): he intends to go with the IVORY TREES (#25 / #33 family): "it got the movement, it got magic".
- Still open, hard to describe: the "timbre" of the purple, i.e. which effect sits on the plum hill.
- Stars: asked for one suggestion only, no renders ("a waste of time"). Claude's suggestion: warm gold/yellow stars.
- Lessons (memory visual-versions-must-differ): versions must differ at a glance; zoom view slides between pictures; picks page has Undo.
- PAUSED the cover here. Next: solve the title font (licence), then back to the final pick (#33 family vs #13).
- Font (Amir 11-06 19:15): "the free font is nice, keep it as an option" (Barlow Condensed ExtraBold, OFL, on the Layout page).
  Avenir Next Condensed Heavy: MyFonts sells single styles (from $97.99), no need for the whole family, but $40-100 is too much for him.
  Open question he raised: Pirata One (blackletter) for "Inch of Shadow" long term? Claude: the name belongs to the brand face (frame.md: Albertus Nova, constant core); Pirata is fine as this release's choice; a long-term goth name = the logo round (Look-02), not this cover.
- TICKET (Amir 11-07): "Name font for Half the Night" parked for later. Candidates on the picks page step 2 · Fonts (cover #36, Barlow title vs Avenir title): Pirata One, CAT Eckmann (OFL, checked 11-07), UnifrakturCook, Albertus Nova (Marcellus stand-in). Title = Barlow Cond (free). Claude's pick: Eckmann.
- NOW (11-07): making the text blend into the picture (embedded, not on top).
- Text blend round 1 (11-07, on #36, Barlow title + Pirata name): Amir: text must NOT move; 2 (Xerox grain on the letters) = CHOSEN, keep as is (colour shift from the effect: unsure but keep); from 3 he likes the dark shadow behind the title (Canva calls it Effects > Shadows); 4 name colour = an option later; 5 only if the name sits ON the hill line, not behind it.
- Round 2 on the picks page: 2+shadow, 2+shadow+red edge, 1+3 combined, 5 redone on the hill line (normal and bigger). All made locally in the RM page (no Canva).
