# 🎸 Studio: vocal chain research handover

Chat: vocal chain research (side chat of the 🎸 Studio parent). Written 2026-11-12.
Ask (Amir, 11-12): "is there a website or info somewhere on how I can make a vocal chain like famous artists".

## Where it stands

- ✅ Research done, text only: [music-tools/research/vocal-chains.md](../../../music-tools/research/vocal-chains.md)
- 8 kinds of sources rated; 5 chains written up (Depeche Mode, The Cure, IDLES, Protomartyr; Crystal Castles as forum guess only).
- Every documented step is mapped to plug-ins he owns (from `Documents/ableton-plugins-2026-10-12.md` + `/Library/Audio/Plug-Ins/`). Nothing needs buying.
- Nothing installed, bought or built. No Live racks made.
- 11-12 follow-up (Amir: "The Cure?", "look out of my range", "I use autotune, check Lana Del Rey", "create artifact"): added F. Lana Del Rey (SOS 2017 Menzies/Reid + SOS 2020 Laura Sisk) and G. Auto-Tune placement (SOS 'Vocal Fixes' 2003). Private page: https://claude.ai/artifact/KoS6fZ23k1cGGhwHo3CbPd (source `music-tools/research/vocal-chains.html`).
- 11-12 second follow-up (Amir: "check also hip hop artists like the weeknd and travis", "for robert what about compression de esser? distortions?"): added H. The Weeknd (SOS 2015 Illangelo + SOS 2023 Ethan Stevens), I. Travis Scott (tracking chain only, SOS 2023), and the Future/Seth Firkins Auto-Tune tracking method (SOS 2017). Robert Smith: no engineer source names a compressor, de-esser or distortion on his voice; written up as an open ❓. Page republished as v2.
- 11-12 third follow-up (Amir: "im not looking for a specific singer, its a bigger decision which style i want my vocals to be"; then "Yes, build it"): private picker page https://claude.ai/artifact/7REaGbwvsRXXugwrF7TZsV (source `music-tools/research/vocal-style-picker.html`). 4 directions: close-dark, far-haunted, into-effects, modern-treated. Picks are saved in db collection `ticks` (doc id = direction id, {name, pick: yes|maybe|no, note, at}); read them back with ArtifactData list. "Gives/costs" lines are Claude's read (🎃), not facts. A pick becomes a 📌 taste rule only after Amir's read-back.

## Open decision (Amir)

- Vocal style direction: tick on the picker page.

## Sources (best first)

1. Sound On Sound (Inside Track / Classic Tracks / artist features): free, the most genre hits
2. Vintage King "Making Of": free, asks for the vocal chain directly
3. Tape Op interviews: free, method more than settings; no hit for his bands yet
4. Mix magazine, AudioTechnology (live FOH), Pensado's Place, Mix With The Masters (paid)
5. Forum-grade: Gearspace, Equipboard, Reddit

## Open questions (for Amir)

- ✅ Mics answered 11-12: SM7B, AKG "c212" (model ❓), Neumann TLM 103 (confirmed by Amir 11-12).
- 11-12 Amir: "i must admit i looking for more to the vocal chains itself": scope of the next step asked as options (settings sheet / more chains / Live racks).
- 11-12 Amir: "not only engineer and official answers... also Reddit, YouTube, so on": added section J (forums, tutorials, blogs). Key find: Mix 2021, Illangelo: After Hours vocal = SM7B > Apollo Twin pre (> UAD Manley VOXBOX), Ableton, which is Amir's own rig. Limits: Reddit is blocked for my tools and the built-in browser; Gearspace is behind a Cloudflare check (not bypassed); YouTube gives no transcript text. Notebook page v3. The settings/racks option is still open.
- 11-12 Amir liked the gives/costs summary ("add more"): picker v2 has 4-5 gives + 4 costs per direction, a "Best for" line, his mic per direction (SM7B / AKG / TLM), and a "Mixing two" block. All 🎃 Claude's read unless a source is named.
- 11-12 Amir asked for Deftones, Midwest emo (SDRE, American Football), Nick Cave (Push The Sky Away, Skeleton Tree). Added section K: PTSA full chain (Launay: M49 > 1081 > CL1B, live takes, spring/plate/RE-301 slap, Devil-Loc); Deftones only from a search snippet (RAT + Strymon slap ❓); emo and Skeleton Tree have no documented chain. Notebook v4; picker v3 with a 5th direction "Tuned new wave".
- Amir's direction notes 11-12 (quick notes in chat, NOT 📌 taste rules): his vocal is poppy; audible Auto-Tune is fine; take references from hip-hop mixed with a new wave vibe (Crystal Castles, Robert Smith); Lana = a perfect reference; Depeche Mode feels too complex for now; the close/exposed style only on songs chosen for it; "all of them are options".
- 11-12 Crystal Castles, deeper hunt (Amir: "im sure there is some vocal chain suggestion somewhere online"): section E2. Two YouTube tutorials read in the built-in browser (auto-captions collected while the video played muted, plus frames; the optional-cookies banner was rejected): billyxo (Auto-Tune retune 0 + transpose up + harmony layer, gate > comp > high-band multiband > limiter > EQ > flanger > convolver "ghost" > delay, Gross Beat gating) and Navjaxx (Harmony Engine; REMOVED from both pages on Amir's ask, notebook v7, picker v6). Plus a Gearspace summary (spring on the highs, Auto-Tune on yells ❓). The presets were NOT downloaded. Notebook v6, picker v5.
- 11-12 later: Amir asked "can u start build those fx racks?". Checked (read-only): User Library root has `FX - Vocal Travis.adg` + `FX - Vocal Travis Autotune.adg` (Audio Effect Racks full of VST3 plug-in state; one points to `Presets/Audio Effects/Audio Effect Rack/Travis Voc.adg`). Naming model: "FX - Vocal <name>.adg". No local IR library found. The approach was asked as options (build in Live by screen control / write .adg files / build sheet), plus a proposed new side chat; NOT started.
- 11-12 racks were built by the side session studio-vocal-racks (handover `plans/handovers/studio/vocal-racks.md`); all unproven until Amir loads them. On Amir's "y", renamed after singers in the User Library root: Close and Dark → `FX - Vocal Lana Del Rey.adg`, Far and Haunted → `FX - Vocal Robert Smith.adg`, Modern and Treated → `FX - Vocal The Weeknd.adg`, Tuned New Wave → `FX - Vocal Crystal Castles.adg`. Travis racks untouched. Undo = rename back (mv -n).
- 11-13 Melodyne prep rules (Claude's draft, Amir: "good for me for now"; the rules may later depend on each song's vocal chain; NOT a 📌 taste rule):
  - Work on a copy, original muted; no printing, no comping; one song at a time, Amir's OK before the next.
  - Key from Amir or Melodyne's scale detection (he confirms); fix detection errors only.
  - Correct Pitch center/drift by direction: Lana 30-50% / 0-20%; Robert Smith 40-60% / 20-40%; The Weeknd + Crystal Castles 80-100% / 50-70%.
  - Leave alone: transitions/slides, vibrato on long notes, cracks/yells/breaths.
  - Flag (don't fix): notes still more than about 30 cents off, or fighting the chord/doubled instrument; list with bar:beat, word, cents, suggestion.
  - Timing: no Quantize on the lead; doubles/BVs aligned to the lead, at most about 50%.
  - Per song: a short report (applied / flagged / left on purpose); Amir does the final touch.
- 11-13 Amir has VocAlign 6 Pro (`VocAlign6Pro.vst3` on disk); he asked how Claude can help. Answered in chat; no ticket yet.
- 11-13 Amir: "please read carefully the manuals of melodyne and vocalign, the version i have". Installed: Melodyne 5.4.2.006 (edition ❓), VocAlign 6 Pro 6.1.30. Notes: [melodyne-vocalign-manuals.md](../../../music-tools/research/melodyne-vocalign-manuals.md). Main points: Melodyne in Live = insert/transfer, first in the chain, Arrangement View, constant tempo; distorted rhythm guitars = Universal algorithm; VocAlign in Live = VST3 capture with the Guide on the sidechain; guitars → Low Flexibility first. Scratch trashed. Open: Melodyne edition (essential/assistant/editor/studio).
- 11-18 the rack session reported: 11 racks saved from Live (batch 1: Lana, Weeknd, Robert Smith, Crystal Castles, Nick Cave, Deftones; batch 2: Tool, Steven Wilson, Bon Iver, Thom Yorke, Dream Wash), all still unproven until Amir loads them. Latency in "Night voc rec" is not solved, and the first Melodyne pass on "I See A Dorian" is not saved. Full detail + 🎸 Studio 11 proposal: `plans/handovers/studio/vocal-racks.md`.
- 11-18 the Melodyne session reported (11-14/15): first pass done on "D minor 112 BPM voc rec" (bars 9-25, Lana direction, on duplicates). Two vocal recording templates are saved in `User Library/Templates/` (RME In 10, Apollo In 1). Melodyne edition = editor or studio (Polyphonic is listed), which answers the ❓ above. Full detail + 🎸 Studio 13 proposal: `plans/handovers/studio/melodyne-prep.md`.
- 11-19 the Melodyne session reported: pass on "Night F Dorian" (2 lead bounces: pitch, line levels, sibilants, breaths, formant), set not saved. Next there: a vocal production guide in Amir's method; he adds his conclusions first. Detail: `plans/handovers/studio/melodyne-prep.md`.
- 11-18 voice warm-up MIDI (Amir's ask here): `music-tools/vocal-warmup/` (rolled 1-3-5 chord cue, C2-C3 roots and back, chords + guide versions, `make_warmup.py`). Not yet played in Live.
- Racks (old note): Amir wanted Live racks LATER ("still don't build the racks"). He has a Travis vocal effect rack in his User Library as the model. Not built, not opened.
- Is the Apollo Twin connected when he mixes? (UAD-2 plug-ins need it; the UADx ones do not.)
- Does he want one chain built as a Live Audio Effect Rack (e.g. the Protomartyr one, which maps one-to-one)? That would be a new ticket.

## Scratch

- Fetched pages were saved as text in the session scratchpad only and moved to the Trash at the end of the run.

## Ticket updates (for ⚙️ System to merge)

- 🎸 Studio 10 (new, ST- prefix):
  - `bucket`: ⏭️ next
  - `who`: 🙋 amir
  - `label`: Vocals · famous vocal chains research
  - `next_step`: Amir reads vocal-chains.md and picks one chain to try (or asks for it as a Live rack)
  - `chrome`: false
  - note: research done 2026-11-12, file `music-tools/research/vocal-chains.md`
