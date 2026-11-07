# Splice Creative Racks — plan

Source: `~/Splice/sounds/packs` (892 packs, 1,416 files, 3.2 GB)
**One-shots only.** Excluded: filename containing loop / groove / beat / bpm, AND anything living in a `loops/` folder.
Max 32 pads per rack (two pages of 16). Output: `~/Desktop/SAMPLES MAC/Drum Machine Tune/racks/`

## Decided racks

| # | Rack | Pads | Status |
|---|------|------|--------|
| 1 | **Tambourines** | 17 | **BUILT 2 Sep** |
| 2 | **Rides** | 22 | **BUILT 2 Sep** |
| 3 | Shakers | 22 | pending |
| 4 | Bells (church + glocken + chimes + synth) | 21 | pending |
| 5 | Hand Perc + Timpani + Cowbell | 21 | pending |
| 6 | Risers & Sweeps | 18 | pending |
| 7 | Wood & Clicks | 18 | pending |
| 8 | Impacts, Booms & Downlifters | 28 | pending, over 25 |
| 9 | Foley & Lasers | 32 | pending, over 25 |

Optional, not decided: Vox (25), Horror (34).

## Full Splice inventory (audited 2 Sep) — 1,416 files

**Drum basics, not covered yet** (one-shots): Kicks 162 · Snares 144 · **Crashes 31** · **Rides 22 (BUILT)** · Hats 43 · Claps 19 · other cymbals 5.

**Racks found inside the 114 "unclassified"** — filenames use no standard drum words, but the material is good. **Remember these, Amir wants them later:**

| Rack | Count | Contents |
|---|---|---|
| Nature | 15 | raven screech, seagulls, ocean waves, wind gusts, street rain, twig snaps, leaf rustle |
| World Perc | 12 | Taiko, Surdo x2, cajon, cuica, vibraslap, didgeridoo x2, African drumset, tribal drum |
| Urban / Machine | 11 | ambulance + police sirens, motorcycle drive-by, drill ratchet, fluorescent light ballast + flicker, hotel room light |
| Metal | 10 | rust2 bunker door slam, tower rail strike, rust3 pipe strike, metal taps, chain rattle, metal pole on concrete |
| Snaps | 7 | finger snaps, verb snaps, brake snap |
| Fills | 6 | Sullivan King fills, timbale roll w/ dub echo |
| Fire | 5 | blaze, fireplace, flame crackle, firework crackle, sparklers |

Plus 4 game/sci-fi and 4 explosions (too thin alone, fold into Metal or Urban).
40 files stay genuinely miscellaneous (cryptic pack codes, need listening).

**Dropped by Amir, do not raise again:** melodic, bass, pads/atmos, stabs.
**501 loops** excluded by the one-shot rule (373 in `loops/` folders, 128 named as loops).

## Amir's decisions
- **Toms: removed.** Not wanted.
- **Downlifters & Reverse** merged into Impacts & Booms.
- **Lasers & Zaps** merged into Foley FX.
- **Timpani (9) and Cowbell (4) are NOT bells** — they belong in Percussion.
- max 32 samples per rack.
- One-shots only, no loops.
- Digitakt and MPC on hold. Mac first.

## Trimming the two oversized racks
No decision yet. Options given:
1. Delete near-duplicates, then keep the 25 that measure most different (length, brightness, punch, low-end weight). Finds the most *varied* 25, not the *best* 25.
2. Build at full size and delete pads inside Live while hearing them.

## Lessons from the Tambourine build
- Filename filtering alone is not enough: 3 files had no loop marker in the name but sat in a `loops/` folder. **Always filter on the path too.**
- One false positive found in Shakers: `RO_060_..._104bpm_..._CaxixisMedBigOneHitShaker.wav` is a genuine one-shot caught by the bpm rule. Shakers is therefore 22, not 21.
- These racks span 892 packs, so the tool needed a new `--from-list` mode (build a rack from a text file of paths). Added 2 Sep.

## Command
```
python3 drumrack_tool_v2.py build --from-list <list.txt> --name <RackName> \
  --all --peak-db -6 --out ~/Desktop/"SAMPLES MAC/Drum Machine Tune"
```
