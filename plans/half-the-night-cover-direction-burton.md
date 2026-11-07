# Half the Night cover, Burton storybook direction (backup, low priority)

Started 2026-11-04. Session notes for this one direction only. Main history: plans/half-the-night-cover-v2.md.
Files: artwork/edits/htn-burton/

## Starting point
- Base: artwork/edits/half-the-night-v6-languages.jpg #1
  (generated_images/pinocchio-single/make-an-album-artwork-cover-in-a-gothic-20261103_234142.png):
  3 crooked trees on a hill in front of a huge cream moon, red spiral hill below.
- Amir's own vision (11-03): crooked trees on the SIDE, a much SMALLER moon, room for the title;
  the Spotify Canvas makes trees and stars flash.
- Must change: the spiral hill (too close to The Nightmare Before Christmas).
- Out: #2 half the stars ("seen too many").
- Refs: half-the-night-build/refs-amir/tree-*.png (spiral Burton tree, gothic tree, two plain silhouettes);
  his sketches v2-amir-sketch-1/2 (trees right, small moon top-left, curved line, text bottom-left).
  Contact sheet: htn-burton/00-refs-contact.jpg

## Design talk (round 1, 2026-11-04)
Questions put to Amir, answers below when they come.
- Ground (Amir): 1 low ridge, flat, near the bottom, hand-drawn edge. Spiral hill gone.
- Trees colour + curl: unanswered; renders 1-3 test them by eye (black / white / curly hooks).
- Prompts: htn-burton/prompt-1..3-*.txt (raw_render.py, no core, no palette). Waiting for his go.

## Round 1 renders (2026-11-04 00:05, Amir's go)
- htn-burton/board-r1.jpg: r1-1-black-trees.png, r1-2-white-trees.png
  (sources generated_images/pinocchio-single/gothic-storybook-album-cover--hand-inked-20261104_000504/000503.png)
- Render 3 (curly hooks) was LOST: renders 1 and 3 finished in the same second, image_generator.save_bytes names
  files to the second, so one overwrote the other. Next time run renders one after another.
- 11-04: raw_render.py fixed by the lead session (Amir approved): unique filenames, drafts default to MEDIUM quality
  (~$0.05); --quality high only for a final he asks for.
- Sheet htn-burton/board-from-main-chat.jpg: main-chat Burton renders 1-3 + his tree refs 4-7 + round 1 (R1-1, R1-2). Sent 11-04.
