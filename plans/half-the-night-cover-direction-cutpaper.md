# Half the Night cover, direction: 1950s cut-paper movie poster (started 2026-11-04)

One direction only. History and lessons: plans/half-the-night-cover-v2.md (read-only from here).
Files for this direction: artwork/edits/htn-cutpaper/.

## Language

Flat torn and cut paper shapes, 3 colours, visible paper edges, hand-cut title. 1950s B-movie / thriller poster.

## Fixed by Amir

- "Very interesting" direction.
- NO woman / person. NO river.
- Colour comes last, locally (R. Missing ramp); concept renders carry whatever colours the model gives.
- Room for "Half the Night" + "Inch of Shadow"; movie poster, minimal, reads as a music cover.

## Starting points (renders so far)

- v6-languages #3 (generated_images/pinocchio-single/...20261103_234226): woman + river = rejected elements;
  kept: the red ground, small moon, hand-cut slanted title.
- v7 #1 (...235736): bare trees + moon, torn black/blue layers.
- v7 #2 (...235755): night torn diagonally, half moon, stars. Closest to his sketch 1 and to the
  Frigio Ecdisis 4 diagonal division he likes.

## Our effects that could fit later (pick after the image is chosen)

- print-linocut-reduction-print (stacked carved colour blocks), look-riso S3 (two inks, off register),
  look-xerox S1, look-halftone S2, print-scrapbook-archive-collage (torn edges), kill-the-polish (texture baked in).

## Design talk (2026-11-04)

(answers go here)
- Base: v7 #2 torn sky (Amir, 2026-11-04). Other questions (light half, red, title, tear, moon) left open;
  answered by the renders instead: 4 short prompts in artwork/edits/htn-cutpaper/prompt-1..4.txt, waiting for his go.
- Round 1 rendered (2026-11-04 00:05): r1-trees.png, r2-torn-open.png, sheet round-1.jpg.
  Prompts 3 (moon torn) and 4 (red ground) were LOST: run in parallel, raw_render.py names files by
  prompt[:40] + second, so 2, 3 and 4 wrote the same file (2 survived). Render one at a time from now on.
- 11-04: raw_render.py fixed by the main session (unique file names; drafts default to medium, ~$0.05;
  --quality high only for a final Amir asks for). Re-render of 3 + 4 still waits for Amir's go.
- 11-04: sheet from-main-chat.jpg (the 3 earlier renders) made for Amir next to round-1.jpg.
- Round 2 (11-04 00:20, medium): r3-moon-torn.png, r4-red.png, sheet round-2.jpg (prompts 3 + 4 re-run on Amir's 'show me 2 new options').

## Picks after main-chat sheet + round 1/2 (Amir, 2026-11-04 by voice; quick answers, not taste rules)

From the main chat (from-main-chat.jpg):
- MC1 (red, first cut-paper, 234226): "beautiful" but WITHOUT the character; find something to replace her.
- MC2 (trees + moon, black/blue torn layers, 235736): composition, paper cut, the middle. "Can be our main one."
- MC3 (torn sky, 235755): pass. Its font stays an option.
From this chat:
- Round 1 #1 (r1-trees.png): the black trees. Font liked.
- Round 1 #2 (r2-torn-open.png): font liked.
- The moon shape and the star shapes from "the second generation": which file is still being confirmed.
Open: what replaces the woman in MC1.
- Moon + stars confirmed by his screenshot: the gold CRESCENT and the gold 4-point star from round 1 #1 (r1-trees.png).
  Cut out locally (no AI): elements/moon-crescent-r1.png, elements/star-r1.png.
- MC1 replacement for the woman (Amir 11-04): a big black tree, c blank motel sign, d birds across the moon, plus his idea:
  an unknown figure that hints at Pinocchio but is not clearly him. Prompts prompt-mc1-a/c/d/e.txt, waiting for his go.
- Round 3 (11-04, medium): mc1-a-tree/c-motel/d-birds/e-figure.png, sheet round-3-mc1.jpg.
- Round 3 MC1 (tree / motel / birds / figure): Amir "none of them feels like the evolution of number 2" (MC2). Do NOT use blue.
- Next: 4 evolutions of MC2 (prompt-mc2-1..4.txt): red band / cream band + gold crescent + stars (his liked elements) /
  big moon in a purple band / minimal grey band. Waiting for his go.
- Round 4 (11-04, medium): mc2-1-red / 2-cream-gold / 3-big-moon / 4-minimal.png, sheet round-4-mc2.jpg.
- Round 4 (11-04, medium): mc2-1-red / 2-cream-gold / 3-big-moon / 4-minimal.png, sheet round-4-mc2.jpg (first batch try failed on a shell loop, empty prompt refused by the API with a 400, not billed).
- Amir 11-04 asked: MC2 in red + purple; A tree (MC1 batch) in purple; D with the OWL from the Polish chat
  (htn-polish/p8-owl-moon.png) instead of the birds, on purple; round 4 #1 (red band) in purple.
- Round 5 done LOCALLY, no AI, no cost: recolour.py (one saturated paper colour -> target, texture kept;
  red 180,30,20 / purple 69,33,76 = sampled from mc2-3-big-moon band) and owl_d.py (birds covered with
  purple paper, clean cream paper moon, owl silhouette from p8). Files in purple/, sheet round-5-colours.jpg,
  owl element elements/owl-silhouette-p8.png. Note: owl is brush-drawn (Polish gouache), not cut paper.

## SUMMARY of this chat (Amir, 2026-11-04; quick answers, not 📌 taste rules). Board: artwork/edits/htn-cutpaper/summary-board.jpg

Main composition: MC2 (main-chat trees + moon, 235736): torn black layer top left holding the title, a torn band of
sky across the middle, two bare black trees rising from a black torn hill, a cream paper moon. In RED or PURPLE
(purple/mc2-orig-red.png, purple/mc2-orig-purple.png). Never blue.
Elements kept:
- Gold crescent moon + gold 4-point star (round 1 #1): elements/moon-crescent-r1.png, elements/star-r1.png.
- Owl in the moon (owl from the Polish chat p8): elements/owl-silhouette-p8.png; seen in purple/mc1-d-owl-purple.png.
- Black trees (round 1 #1). Next: make them gothic, Tim Burton (twisted, spiral branches).
- Fonts: ALL liked (MC2, round 1 #1 + #2, MC3, A tree, band #1); crops in summary/font-*.png.
Out: any woman / person (puppet figure included), river / water, blue, MC3 composition, the MC1 swaps
(big tree, motel sign, birds, figure: "none feel like the evolution of number 2").
Last render: MC2 with gothic Tim Burton trees, red (prompt-final-gothic-trees.txt), purple made locally after.
Then: Canva compose, our effects, colour ramp, type, export.
- Last render done (11-04 00:58, medium): final-gothic-red.png (src ...20261104_005842-fd98ac.png), purple made locally
  final-gothic-purple.png; sheet round-6-final.jpg. Spiral Burton trees, MC2 layout kept (title in the black top left, band, moon).
  Small known flaw: a few faint red edge specks stay on the purple tree edges (local recolour); clean in Canva/colour step.
- Amir on round 6 (gothic spiral trees, red + purple): "none". PAUSED here 11-04 ~01:00.
  Standing picks = the SUMMARY above (MC2 composition in red/purple with its ORIGINAL trees, crescent + star, owl in the moon, all fonts).
