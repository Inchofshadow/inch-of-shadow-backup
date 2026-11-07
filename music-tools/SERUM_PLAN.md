# Serum presets — organisation plan

Written 2026-10-20. Nothing in this plan has been executed. Each step needs Amir's go.

## 0. The three problems

1. Find a preset fast when you remember the ARTIST, not the song ("Playboi Carti" → the preset).
2. No confusion between Serum 1 and Serum 2.
3. Nothing missing while playing: no empty browser entries, no "missing file" dialogs, no preset that refuses to load.

## 1. Facts checked on disk (2026-10-20)

- Serum 2 reads `/Library/Audio/Presets/Xfer Records/Serum 2 Presets/`. Its browser index (`System/presets.db`) was rescanned 15 Oct:
  2,441 presets, every `User/` folder indexed. Serum 1's tree is shown inside Serum 2 as `S1 Presets` (a link).
- What Serum 2 can search (User Guide, Appendix B): **name**, **category**, **tags**, **rating** (1–5 stars, user-set). Search is limited to the folder selected in the Folders pane.
- What Serum 2 lets you EDIT per preset, from the metadata pane: **Artist, Category (custom allowed), Description, Comments, Tags (new tags allowed)**, rating. Rename/Move goes through a Finder dialog, then "Rescan Database".
- Where that metadata lives: `.SerumPreset` files carry `presetAuthor / presetDescription / tags` in a JSON header; Serum 1 `.fxp` files carry name (28 chars max), author and category inside a compressed block. The index copies these into `presets.db`. Ratings live only in the db (`UserData`).
- The preset name you SEE in Serum is the name INSIDE the file, not the filename (proved with the Petrucci presets and `Devastation_BS` = "octave bass").
- Missing-file dialog: appears when a preset's sample/wavetable isn't in the search path. Fix = copy the file into `Serum 2 Presets/Samples/User/...` (done 12 Sep for 2 files).
- Ableton projects store the whole Serum state inside the `.als`. Moving or renaming preset files never breaks a song. Verified across 2,701 project files; 26 songs use Serum 1, 12 use Serum 2, 7 use both.
- Versions: Serum 1.368, Serum 2 **2.0.16**. Of the 287 loose presets, 60+ were saved in Serum 2.1.x. Those may refuse to load until Serum 2 is updated.

## 2. One home, one tree (problem 2)

**Serum 2 `User/` becomes the only place presets are added.** Serum 2 opens `.fxp` too, so Serum 1 presets go there as well.

Folder scheme = by SOURCE or THEME, flat, no second level except Tonepusher's banks:

```
User/
  Packs:  2Hollis · AoKor Hyperpop · AoKor Witchouse · Crystal Castles · Gesaffelstones · Kraftones ·
          NODE Dark Crystal · Tonepusher/<bank>
  Themes: Track Remakes · Witch House · Angel Core · Chiptune · Cyberpunk · Choirs & Vox · Real Instruments
  Loose:  Presetshare   (one-off downloads, reviewed later; promote to a theme when a group forms)
```

Serum 1 side (`Serum Presets/Presets/User`): today it mirrors 4 folders (Crystal Castles, NODE, Track Remakes, Witch House) and shows up a second time inside Serum 2 under `S1 Presets` = the duplicate listings you see.
Decision needed (D1): do you still build NEW sounds in Serum 1?
- No → Serum 1 User folder emptied (files already exist on the Serum 2 side), the duplicate listings vanish. The 26 old songs keep working, their sound is inside the project.
- Yes → keep the mirror but only for `.fxp`, same folder names, and accept the double listing.
Also: the orphan copy in `~/Music/Xfer/Serum Presets/Presets/User/Witch House` (28 files, read by nothing) goes to the Trash (D2).

## 3. Names you can recognise (problem 1)

Rule: **the name inside the preset carries TYPE + ARTIST + SONG; the metadata carries the rest.**

```
inside name  (what the browser shows; keep under 28 chars so .fxp also fits)
   LD Carti - Long Time          BA Travis - Sicko Mode         PL Radiohead - Right Place
Artist field  = the artist being remade (Playboi Carti), not the preset maker
Description   = song, year, what part (lead/bass/keys), preset maker, source link (presetshare p12345)
Tags          = artist tag (carti, travis, radiohead...), genre (witch house, hyperpop, 80s), role (remake, original)
Category      = Serum's own list (Bass, Lead, Pad, Keys, Pluck, FX...), so the CATEGORIES tab works
Rating        = yours. 5 stars = go-to. The Ratings menu then finds them in one click.
```

Type prefixes stay the two-letter ones most authors already use: BA LD PL PD KY SY AR FX BR ST VOX CH DR.

How you then find things in Serum: select `User` at the top of the Folders pane (so search covers everything), type `carti` → every Carti preset, whichever folder; or open the TAGS tab and click the artist tag; or Ratings → 5 stars for your own picks.

### Where the artist/song info comes from
1. The filename and the inside name (most already say the song: `Travis_Scott_Sicko_Mode`, `YEAT_GET_BUSY_PLUCK`).
2. The presetshare.com page per preset: author, description, tags. Your Chrome-extension list holds the URLs; a scrape of each page fills the gaps (name → artist/song when the file name is cryptic like `Glizy_Gang`, `LD_PLUTO`).
3. You, for the rest: a short CSV review (file · proposed Artist · Song · Type), you correct in the sheet, I apply.

### How the info gets INTO the presets (D3, pick one)
- **A. Inside Serum 2, by hand**: metadata pane per preset. Safe, zero risk, slow (~300 presets ≈ an evening).
- **B. File-level, by script**: `.SerumPreset` → edit the JSON header; `.fxp` → patch the fixed-width name/author fields in the compressed block. Fast; must be proven first: 2 test files (one of each), you load them, check the name and that the sound is unchanged, then batch with an undo script. Unknown: the `hash` field in the `.SerumPreset` header, Serum may check it. The test answers that.
- **C. Database-level**: write into `presets.db` (sqlite). Fastest, but "Erase and Rebuild Database" would wipe it. Not recommended as the only copy.
Recommended: B for names/artist/description (lives in the file, survives rebuilds), A/rating for stars and tags you add while playing. Back up `presets.db` before any of it.

## 4. Nothing missing while playing (problem 3)

| Cause | Seen when | Fix |
|---|---|---|
| Folder changed in Finder, index not rescanned | AoKor packs (Sep), every drop since | After any Finder change: Presets menu → **Rescan Database**. Or add presets through Serum. |
| Preset references a sample/wavetable not installed | PL - BRUISES, VOX - LENI (Sep) | Scan every preset for external refs after each batch; copy the files into `Samples/User/<pack>`. Re-run on the new 287. |
| Preset saved in a newer Serum (2.1.x) on 2.0.16 | 60+ of the new files | Update Serum 2 to the current 2.1.x before relying on them; until then expect refusals. |
| `.SerumPreset` placed under Serum 1 | not yet, by design | Never. Serum 1 can't read them; Serum 2 reads both. |
| Same preset listed twice (User + S1 Presets) | now | D1 above. |
| Project saved with Serum 1, later opened with Serum 2 missing or vice versa | 7 songs use both | Keep both plugins installed. Preset files are irrelevant to saved songs. |

## 5. Order of work

1. D1, D2, D3 answered by Amir.
2. Apply the folder plan for the 287 loose files (`drumrack/serum_sort/plan.txt`), Rescan Database.
3. External-sample scan over all User presets → copy into `Samples/User`.
4. Build the review CSV (file · inside name · author · source URL · proposed Artist/Song/Type/Tags), scrape presetshare where the list has a URL. Amir corrects.
5. Test B on 2 files. Amir loads them. If good: batch, with undo script and a `presets.db` backup first.
6. Serum 1 side per D1; Trash the orphan copy per D2.
7. Update Serum 2 (Amir). Rescan. Check the 2.1.x presets load.
8. STATUS.md updated with the final tree.

## Rules carried over
Propose first, Amir says yes, run, verify, undo script. Count in songs, not files. A rack or preset is verified when Amir loads it, not when the file parses.
