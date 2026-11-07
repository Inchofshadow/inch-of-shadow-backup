# Half the Night EP cover: 1970s Polish film-poster direction

Started 2026-11-04. This session's notes ONLY. Files go in `artwork/edits/htn-polish/`.
History before this: `plans/half-the-night-cover-v2.md` (read-only here).

## The language

1970s Polish film poster (Polska Szkoła Plakatu): one surreal painted idea, a visual metaphor instead of a
scene; three flat colours; the title hand-lettered, part of the picture. Poster feel, minimal, must read
as music artwork, not as an AI illustration.

## What we know (from the v2 log)

- Liked: the concept. Rejected: v6-languages #4 (woman's face with the moon in her head, "Nina Simone vibe").
- No people. No rivers. No familiar religious symbols.
- v7 #3: moon split light / black / red (river = out). v7 #4: moon cut in half above water.
- Kept board: Dark Entries / Wolfsheim, the red moon with silhouettes inside (birds); inside could be stars,
  trees, an animal or birds.
- Colour is LAST and local (R. Missing ramp + shares). Concept renders carry no palette.
- Room for "Half the Night" + "Inch of Shadow".

## Our effects that may fit later (to suggest after he picks an image)

- print-screenprint-split-fountain, print-risograph-overprint, look-riso (S3), look-halftone (S2),
  print-dithered-halftone, balanced-opposition, kill-the-polish. Local looks: `print_looks.py --look riso`.

## Round 1: single surreal ideas (proposed to Amir 2026-11-04, waiting for his picks)

Prompts as they would be sent raw (`raw_render.py`), one each:

1. Candle: "Make an album artwork cover in the style of a 1970s Polish film poster: a candle burned exactly halfway, its flame is a thin crescent moon. Three flat colours, painted, surreal, lots of empty space. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
2. Moon with a forest inside: "Make an album artwork cover in the style of a 1970s Polish film poster: a big moon, and inside it a dark forest of bare trees and a few birds, like a window. Three flat colours, painted, surreal, lots of empty space. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
3. Peeled moon: "Make an album artwork cover in the style of a 1970s Polish film poster: the moon peeled like an orange, the peel hanging down in a long spiral, black night inside it with stars. Three flat colours, painted, surreal, lots of empty space. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
4. Night bird: "Make an album artwork cover in the style of a 1970s Polish film poster: a large bird in flight whose wings are made of night sky with stars, the moon as its eye. Three flat colours, painted, surreal, lots of empty space. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
5. Tree holding the moon: "Make an album artwork cover in the style of a 1970s Polish film poster: one bare tree whose branches hold the moon like a fruit, half the moon bitten off. Three flat colours, painted, surreal, lots of empty space. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
6. Hourglass night: "Make an album artwork cover in the style of a 1970s Polish film poster: an hourglass, the top half is night sky with stars, the stars fall through as sand and pile up below. Three flat colours, painted, surreal, lots of empty space. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."

Open questions to him: which 2-3 to render; is red allowed as the third colour (Wolfsheim moon) or is
it the R. Missing ramp only, like the brief.

## Round 1 renders (2026-11-04 ~00:05, Amir's go: "Render 1, 2, 4")

Sheet: `artwork/edits/htn-polish/htn-polish-round1.jpg`. Files: p1-candle.png, p2-moon-forest.png, p4-night-bird.png
(sources generated_images/pinocchio-single/...20261104_000404 / _000440 / _000405).
- Note: 1 and 2 first ran in parallel and saved to the same filename (same second); 2 was overwritten and re-run
  once with the same approved prompt. Fixed 11-04 in raw_render.py (unique names, parallel is safe again);
  drafts now default to MEDIUM quality (~$0.05); --quality high only for a final Amir asks for.
- My read: all three are cleaner and more "modern flat vector" than real 1970s Polish posters (those are
  rougher, stranger, more painted). Hand-lettering came out as brush script on all three.
- Waiting for his picks.

## Start sheet (2026-11-04)

`artwork/edits/htn-polish/htn-polish-from-main-chat.jpg`: what the main chat showed for this direction.
1 woman + moon (rejected), 2 split moon (red river out), 3 moon cut in half over water, 4 Wolfsheim (crop of
the kept board #12, soft, looking only). Sent with round 1 next to it.

## Round 2 ideas (2026-11-04, after Amir: "None, new ideas" on round 1)

Round 1 read as too clean/modern, so every prompt now asks for rough gouache. Exact prompts (raw_render.py, medium):

3. Peeled moon: "Make an album artwork cover in the style of a 1970s Polish film poster, rough gouache, visible brush, strange: the moon peeled like an orange, the peel hanging down in a long spiral, black night inside it with stars. Three flat colours, lots of empty space. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
5. Bitten moon tree: "Make an album artwork cover in the style of a 1970s Polish film poster, rough gouache, visible brush, strange: one bare tree whose branches hold the moon like a fruit, half the moon bitten off. Three flat colours, lots of empty space. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
6. Hourglass: "Make an album artwork cover in the style of a 1970s Polish film poster, rough gouache, visible brush, strange: an hourglass, the top half is night sky with stars, the stars fall through as sand and pile up below. Three flat colours, lots of empty space. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
7. Disco-ball moon: "Make an album artwork cover in the style of a 1970s Polish film poster, rough gouache, visible brush, strange: the moon is a mirror ball, one half lit and sparkling, the other half swallowed by black night. Three flat colours, lots of empty space. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
8. Owl in the moon: "Make an album artwork cover in the style of a 1970s Polish film poster, rough gouache, visible brush, strange: a red moon with the black silhouette of an owl inside it, wings open, a few stars around. Three flat colours, lots of empty space. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
9. Keyhole moon: "Make an album artwork cover in the style of a 1970s Polish film poster, rough gouache, visible brush, strange: the moon has a keyhole in it, and through the keyhole you see a second night with stars. Three flat colours, lots of empty space. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."

## Round 2 renders (2026-11-04 ~00:21, Amir's go: "Render 7, 8, 5", medium)

Sheet: `artwork/edits/htn-polish/htn-polish-round2.jpg`. Files: p7-discoball-moon.png, p8-owl-moon.png,
p5-bitten-moon.png (sources ...20261104_002045-467fa0 / _002045-f973d6 / _002044-b3d9e0; matched to prompts by eye).
- Rougher than round 1; the "rough gouache" line worked.
- 7 added a standing figure unasked (no people rule): it would need removing or a re-render with "no people".
- Title lettering is still the same brush script on all three; the type is ours later anyway.
- Waiting for his picks.

## Amir's picks after rounds 1 + 2 (2026-11-04 ~00:30, by voice; quick answers, not 📌 taste rules)

- Move away from the moon / a big circle as the MAIN element: the tour artwork already has that motif.
- Round 1 #1 candle (half burned, crescent flame): liked, "nice that way". Develop it; wants more "half"
  ideas like it, preferably without a moon.
- Round 1 #2 moon forest: likes the trees + birds inside the yellow moon, and its FONT. He asks to combine it
  with the Burton tree style (v6-languages #1, curly spiral bare trees).
- Round 1 #4 night bird: pass.
- Round 2: only #8 owl in the red moon; and the FONT of #5 (bitten moon tree).

## Round 3 ideas (proposed 2026-11-04, waiting for his go). Exact prompts:

A. Match: "Make an album artwork cover in the style of a 1970s Polish film poster, rough gouache, visible brush, strange: a single match burned exactly halfway, the burnt half turns into a bare twisted tree. Three flat colours, lots of empty space, no people. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
B. Glass of night: "Make an album artwork cover in the style of a 1970s Polish film poster, rough gouache, visible brush, strange: a cocktail glass filled exactly halfway with night sky and stars. Three flat colours, lots of empty space, no people. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
C. Half-open door: "Make an album artwork cover in the style of a 1970s Polish film poster, rough gouache, visible brush, strange: a door standing alone in an empty field, half open, behind it is night with stars while around it is day. Three flat colours, lots of empty space, no people. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
D. Street lamp: "Make an album artwork cover in the style of a 1970s Polish film poster, rough gouache, visible brush, strange: one street lamp, its cone of light falls on only half of the picture, the other half is deep night with stars. Three flat colours, lots of empty space, no people. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
E. Candle with a star flame: "Make an album artwork cover in the style of a 1970s Polish film poster, rough gouache, visible brush, strange: a candle burned exactly halfway, its flame is a small four-pointed star. Three flat colours, lots of empty space, no people. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
F. Moon forest with Burton trees (his combine): "Make an album artwork cover in the style of a 1970s Polish film poster: a big yellow moon, and inside it a dark forest of curly Tim Burton style bare trees with spiral branches, and a few birds, like a window. Three flat colours, painted, surreal, lots of empty space. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."

## Round 3 renders (2026-11-04 ~00:28, Amir's go: "Render all six", medium)

Sheet: `artwork/edits/htn-polish/htn-polish-round3.jpg`. Files p3A..p3F in htn-polish/ (sources ...20261104_:
A 002822-cda65d, B 002822-04a7fd, C 002823-9e773d, D 002820-828a43, E 002822-92ffff, F 002820-f84afe; each
mapped from its own log, labels checked by eye).
- A match: added a red sun disc unasked (circle again). C door: all daylight yellow, the night only inside the door.
- E candle: the whole candle came out black; the "burned halfway" read is lost (round 1 #1 kept it).
- F: curly Burton trees + birds inside the yellow moon, its own font (thinner, gothic).
- Waiting for his picks.

## Amir's picks after round 3 (2026-11-04 ~00:35, by voice; quick answers, not 📌 taste rules)

KEPT: round 1 #1 candle with the crescent flame (NOT E); round 3 B glass; round 3 D street lamp.
- B: "really cool", the HALF idea is right, but a glass is not the vibe of the track. Find another object in
  that direction.
- D: "perfect": the composition, the diagonal cut line, the blue + yellow. Subject can change (the lamp is
  also fine). Move forward with D first.

## Round 4 ideas (proposed, waiting for his go). Exact prompts:

D-cut base used in D1-D3: "Make an album artwork cover in the style of a 1970s Polish film poster, rough gouache, visible brush, strange: <subject>. A straight diagonal cone of light cuts the picture: the left part flat warm yellow light, the right part deep blue night with small stars. Three flat colours, lots of empty space, no people. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
D1 subject: "car headlights coming in from the left edge on an empty road"
D2 subject: "the open door of a nightclub at the left edge, its light spilling out onto the empty street"
D3 subject: "one bare twisted tree standing exactly on the line between the light and the night, half lit, half dark"
B-half base: "Make an album artwork cover in the style of a 1970s Polish film poster, rough gouache, visible brush, strange: <subject>. Three flat colours, lots of empty space, no people. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."
B1 subject: "an hourglass, the top half is night sky with stars, the stars fall through as sand and pile up below"
B2 subject: "a window in a plain wall, the night with stars fills the window halfway like rising water"
B3 subject: "a hanging light bulb filled exactly halfway with night sky and stars"

## Round 4 renders (2026-11-04 ~00:37, Amir's go: "Render all six", medium)

Sheet: `artwork/edits/htn-polish/htn-polish-round4.jpg`. Files p4D1..p4B3 in htn-polish/ (sources ...20261104_:
D1 003718-629508, D2 003717-44dad9, D3 003717-a79194, B1 003716-e8a9f9, B2 003717-719aab, B3 003715-029705;
each mapped from its own log, labels checked by eye).
- D3 keeps round 3 D's cut best (straight cone edge, tree on the line, half lit).
- D1: the cut became the road edge, not a light cone. D2: painted "KLUB" sign text (would need removing).
- B2 painted a sea in the window, not night rising. B3 has a tiny crescent inside the bulb.
- Waiting for his picks.

## B1 as engraving (2026-11-04 ~00:45, Amir: "try and make B1 engraving")

Local, no AI: print_looks.py S4 engraving on p4B1-hourglass.png. Sheet `htn-polish/htn-polish-b1-engraving.jpg`
(1 original, 2 S4 default pitch, 3 S4 fine pitch 3.0). Files p4B1-hourglass-engraving(.png / -fine.png).
- My read: 2 works on the hourglass itself, but the flat cream paper fills with line noise; 3 (fine) breaks into
  moire, worse. The filter turns tone into lines everywhere; a true engraving keeps the paper clean.
- Offered option: an AI re-render drawn as an engraving (prompt below), waiting for his go:
  "Make an album artwork cover in the style of a 19th century copper engraving printed as a 1970s Polish film poster: an hourglass, the top half is night sky with stars, the stars fall through as sand and pile up below. Fine engraved line hatching on the hourglass only, clean empty paper around it, two inks, no people. Hand-lettered title \"Half the Night\", small \"Inch of Shadow\"."

## Summary of what Amir liked (2026-11-04 ~00:50, he asked for it)

Sheet: `artwork/edits/htn-polish/htn-polish-liked-summary.jpg`.
1 candle with crescent flame (R1, keep) / 2 street lamp R3 D ("perfect" cut, blue + yellow) / 3 glass R3 B (the
half idea only) / 4 moon forest R1 (trees + birds inside, font) / 5 owl in red moon R2 / 6 bitten moon tree R2
(font only) / 7 hourglass R4 B1 (asked for engraving) / 8 Wolfsheim (red moon, silhouettes inside).
Rules he said: no big moon/circle as the MAIN element (tour artwork has it); no people; no rivers; glass is
not the track's vibe; Burton curly trees welcome (combine asked for moon forest).

## Amir's sum-up of this chat (2026-11-04 ~00:55, by voice)

- Street lamp (R3 D): really likes the COMPOSITION.
- Fonts of #5 (sheet numbering = the owl render): likes. The owl in the red moon: "beautiful".
- Hourglass: nice. Candle: obviously. Moon forest: the moon with the forest.
- Next: "the less generate": try the moon forest with GOTHIC trees, in the style of the Tim Burton, Noir or
  Cut-paper chats.

## Moon forest + gothic trees (proposed 2026-11-04 ~01:00, waiting for his go)

Ref sheet: `htn-polish/htn-polish-moon-forest-refs.jpg` (1 moon forest R1, 2 R3 F moon forest + Burton spirals,
3 Burton chat r1-1 black trees, 4 Noir chat v-1a, 5 Cut-paper chat final-gothic-red). Same layout in all three:
yellow moon as a window with the forest + birds, black around, title below in brush lettering.
M1 Burton-chat trees: "Make an album artwork cover in the style of a 1970s Polish film poster: a big yellow moon on black, and inside it, like a window, a forest of crooked gnarled black trees hand-inked like an old gothic picture book, and a few birds. Three flat colours, painted, surreal, lots of empty space, no people. Hand-lettered title \"Half the Night\" below the moon, small \"Inch of Shadow\"."
M2 Noir-chat trees: "Make an album artwork cover in the style of a 1990s noir animation poster: a big yellow moon on flat black, and inside it, like a window, a forest of crooked angular black dead trees and a few birds. Bold flat shapes, almost no detail, three flat colours, no people. Hand-lettered title \"Half the Night\" below the moon, small \"Inch of Shadow\"."
M3 Cut-paper-chat trees: "Make an album artwork cover as a 1950s cut-paper movie poster: a big torn yellow paper moon on black paper, and inside it, like a window, a forest of black paper trees in gothic Tim Burton style, twisted trunks and curling spiral branches, and a few birds. Rough torn paper edges, three flat colours, no people. Hand-cut title \"Half the Night\" below the moon, small \"Inch of Shadow\"."

## Moon forest M1-M3 renders (2026-11-04 ~01:02, Amir's go: "Render all three", medium)

Sheet `htn-polish/htn-polish-moon-forest-m.jpg`. Files pM1-moon-forest-burton-ink.png (src ...20261104_010200-6a3e05),
pM2-moon-forest-noir.png (010157-d0c7ee), pM3-moon-forest-cutpaper.png (as-a-1950s-c-...010201-68323f). Labels checked by eye.
- All three came out 2 colours (yellow + black), no third ink.
- M1: detailed hand-inked gnarled trees, most "gothic picture book"; a small pool of water at the bottom (water = out, remove if picked).
- M2: cleanest poster read, flat angular trees, sharp brush title.
- M3: torn paper moon, spiral Burton trees, hand-cut title.
- Waiting for his picks.

- Moon forest M1-M3: Amir "none" (2026-11-04 ~01:05).

## SUMMARY of this chat (Amir, 2026-11-04; quick answers, not 📌 taste rules). Board: artwork/edits/htn-polish/htn-polish-summary-board.jpg

Main composition: street lamp R3 D (p3D-street-lamp.png): one diagonal light cone splits the cover, flat warm yellow
light on the left holding the title, deep blue night with small stars on the right. "Perfect": the cut line, the
composition, the blue + yellow. The subject may change; the lamp itself is also fine. (Round 4 D3, tree on the line,
kept the cut best of the new subjects; no verdict from him.)
Ideas kept:
- Candle burned halfway with a crescent moon as its flame (p1-candle.png, round 1). "Obviously".
- Owl in the red moon (p8-owl-moon.png, round 2): "beautiful".
- Hourglass of stars (p4B1-hourglass.png, round 4): nice; asked to try it as an engraving (local S4 done, AI
  engraving prompt written, not rendered).
- Moon forest, the original (p2-moon-forest.png, round 1): trees + birds inside the yellow moon.
- The HALF idea (half-burned candle, half-full glass p3B); a glass is not the track's vibe.
Elements (cut out locally, no AI): elements/candle-crescent-r1.png, owl-red-moon-r2.png, moon-forest-birds-r1.png,
hourglass-stars-r4.png.
Fonts liked: owl (R2), bitten moon tree (R2 #5), moon forest (R1); crops in summary/font-*.png. All the same family:
dry-brush hand script.
Out: moon / big circle as the MAIN element (tour artwork has it), any person, river / water, the glass object, night
bird, E star candle, moon forest with gothic trees M1-M3.
Open: what goes into the street-lamp composition (lamp, or another subject on the cut); then Canva compose, our
effects, colour ramp, type, export.
