# Vocal chains batch 2: tuned hip-hop / art-pop singers

🎸 Studio 10 · research, 2026-11-15. Text only. Nothing downloaded, nothing changed on disk.
Singers: Playboi Carti, Don Toliver, XXXTentacion, Thom Yorke, Bon Iver (Justin Vernon).
Style model: `music-tools/research/vocal-chains.md` (A-K).

Labels: **engineer says** / **artist says** / **tutorial** / **forum guess ❓** / 🎃 my own inference.
❓ = unsure or not checked. UAD-2 (names starting "UAD ") needs the Apollo, marked ❓. UADx = native.
Quotes are under 15 words. Wikipedia was not used as a source.
**preset seller** = a shop blog that sells a "Carti preset" etc. Same grade as forum guess. Never an engineer.

## Honest headline

- **Bon Iver: well documented.** One real Sound On Sound Inside Track (mixer Zach Hanson, engineer Chris Messina). The Messina signal chain is written out.
- **Thom Yorke: partly.** No engineer interview about his vocal chain was found. We have a Sound On Sound reader Q&A, a Kid A magazine mention of the vocoder, a 2004 reviewer's ear, and second-hand fan-site gear lists.
- **XXXTentacion: partly.** Mix engineer Koen Heldens talks about one thing: the delay. Plus a Waves chain he published. Nothing on mic, distortion or tuning.
- **Don Toliver: partly, thin.** Recording engineer Derek Anderson gives mic technique only (room, head turns). No plug-ins named by anyone close to the records.
- **Playboi Carti: unverified.** No engineer says anything about his chain. All "Carti chains" online are preset sellers.

Reach limits this run: Reddit, Gearspace, YouTube not read. AudioTechnology, Reverb.com, thekingofgear.com, Gearspace returned HTTP 403 or empty text, so those claims come from search snippets only (marked ❓). MusicRadar pages came back as navigation text only (not read). `fetch_text.py` returned the wrong pages for several URLs, so everything below was read with WebFetch instead.

## What he owns that matters here (checked in the plug-in lists)

- Soundtoys: Decapitator, EchoBoy (+Jr), Little AlterBoy, Crystallizer, MicroShift (+Little), Radiator (+Little), Devil-Loc (+Deluxe), PhaseMistress, Tremolator, SuperPlate, Little Plate, PrimalTap, FilterFreak 1+2, SpaceBlender, Sie-Q, PanMan.
- Valhalla: Room, Plate, VintageVerb, Delay, Shimmer, Supermassive, UberMod, FreqEcho, SpaceModulator.
- FabFilter: Pro-Q 3, Pro-C 2, Pro-G, Pro-MB, Pro-R, Saturn 2, Timeless 3, Volcano 3.
- Pitch / harmony / vocoder: Auto-Tune Artist (the only Antares one), Melodyne, VocAlign 6 Pro, UADx Topline Vocal Tune, Waves Tune Real-Time, Waves Harmony, Waves UltraPitch, Waves SoundShifter, Waves OVox, Waves Morphoder, **Eventide Quadravox** (4-voice harmonizer, plus SplitEQ), Vocodine, Vestral Voices, iZotope Vocal Doubler. No H3000 / H8000 / Harmony Engine / Blackhole.
- UADx native: 1073, 1176 Rev A / AE / LN Rev E, LA-2A (Silver, Gray, original), LA-3A, Distressor, Fairchild 660 / 670, Pultec EQP-1A / MEQ-5 / HLF-3C, Manley VOXBOX / Massive Passive / Variable Mu / Preamp, Little Labs VOG, API Vision, SSL E and G, Studer A800, Ampex ATR-102, Galaxy Tape Echo, Oxide Tape, Lexicon 224, EMT 140, EMT 250, Pure Plate, Brigade Chorus, Studio D Chorus, dbx 160, Avalon VT-737sp.
- Waves: DeEsser, RDeEsser, Sibilance, RVox, RComp, RVerb, H-Delay, Doubler, Reel ADT, MetaFlanger, MagmaSprings, API-550 / 560 / 2500, SSL channel + comp, C4, C6, MV2, Retro Fi, Lofi Space, Aphex AX, REDD, Silk Vocal, Space Rider, Greg Wells VoiceCentric, JJP Vocals, Butch Vig Vocals.
- Others: Softube Tube-Tech CL 1B (+mk II), Maag EQ4 (has an Air Band), Purple Audio MC 77, bx_blackdist2, bx_distorange, bx_greenscreamer, bx_yellowdrive, Saturn 2, RC-20, Decimort 2, Devastor 2, ShaperBox 3, SketchCassette II, soothe2, RX 11, Neutron 5, Ozone Imager 2, Black Box HG-2.
- UAD-2 only (Apollo, ❓): Eventide H910, Roland RE-201, EP-34, AMS RMX16, Lexicon 480L, Oxford Dynamic EQ, API 560, Neve 1081, MXR Flanger-Doubler.
- Live 12 Suite stock: EQ Eight, Channel EQ, Compressor, Glue Compressor, Multiband Dynamics, Gate, Limiter, Saturator, Pedal, Roar, Redux, Dynamic Tube, Amp, Echo, Delay, Grain Delay, Reverb, Hybrid Reverb, Chorus-Ensemble, Phaser-Flanger, Shifter, Auto Shift (he already has a rack with it), Vocoder, Spectral Resonator, Resonators, Corpus, Utility, Auto Pan, Auto Filter.

Mics: SM7B, Neumann TLM 103, an AKG (model ❓). Interfaces: Apollo Twin (studio), RME (home).
Note: the SM7B is exactly the mic Bon Iver's mixer names (section 5).

## Preset check (read-only, 11-15)

Searched: `~/Library/Audio/Presets`, `/Library/Audio/Presets`, `~/Music/Ableton/User Library`, `/Users/Shared/Soundtoys`, `/Users/Shared/Waves`, `/Library/Application Support/Waves`, `~/Library/Application Support/FabFilter`, `~/Documents` (Antares, Eventide: empty).

- **No preset named for Carti, Toliver, XXXTentacion, Yorke, Radiohead, Bon Iver or Messina.** Vendor signature presets for these five: none found by search either (Eventide's artist presets are for other artists).
- **Racks from batch 1 already in `~/Music/Ableton/User Library/`:** `FX - Vocal Travis.adg`, `FX - Vocal Travis Autotune.adg`, `FX - Auto Shift Live Harmonizer.adg`, `FX - Bvoc Choir.adg`. These are the nearest start for Carti, Toliver (tuned melodic rap) and for the Bon Iver harmonizer idea. Also `Presets/Plugin Presets/Auto-Tune/Auto-Tune Artist.vstpreset` and his Templates `Vocal Template - Apollo (In 1).als`, `Vocal Template - RME (In 10).als`.
- **Soundtoys, Little AlterBoy** (`/Users/Shared/Soundtoys/Soundtoys 5/Little AlterBoy/`): `01 Hard Tuner`, `02 Hard Tune Drive`, `03 Modern Double`, `05 Rich 5ths`, `08 High Octave Double`, `09 Low Octave Double`, `11 Robotic` (all `.toy`). Carti, Toliver, Bon Iver layers.
- **Soundtoys, Crystallizer** (`.../Crystallizer/`): folders `05 Echo Pitch`, `06 Echo Reverse`, `09 Harmonized`, `12 Pitch Up`, `13 SpacedOut`. Carti ad-libs, Thom reverse-echo.
- **Soundtoys vocal sets:** `.../EffectRack/10 Vocals/` (`Vocal Twin Double Slap`, `Classic 140 Vocal Plate`, `Dirt Echo`, `Classic Tape Slap 15 ips`, `Super Compressed Double`), `.../EchoBoy Jr/10 Vocal/`, `.../Radiator/Vocal Warmer.toy`, `.../Little Radiator/Vocal OverHeated.toy`.
- **Valhalla (names only):** `/Library/Audio/Presets/Valhalla DSP, LLC/ValhallaRoom/Halls/Vocal-HugeDarkRoom.vpreset`, `.../Halls/BigVocalHall.vpreset`; `.../ValhallaUberMod/Chorus/VocalDualPitch.vpreset`, `.../Echos/VocalEcho.vpreset`, `.../SP/SP Vocal Double`; `.../ValhallaShimmer/` `OctaveUpDown`, `BigReverse`, `BlackHole`. `.../ValhallaRoom/Den/Vocal XXX.vpreset` and `Vocal XXX2.vpreset` exist, but "XXX" here is the factory naming, nothing to do with XXXTentacion ❓.
- **Waves:** `/Users/Shared/Waves/Plug-In Settings/Waves Harmony Startup Preset.xps` only (his own start preset). No artist banks.
- **Online presets found by name only (not downloaded, not endorsed):**
  - Waves StudioVerse chains by Koen Heldens (XXXTentacion's mixer): `Small Vocal`, `Large Vocal`, `Large Background Vocal Space`. Plug-in list of `Small Vocal` below (section 3).
  - Preset sellers: RysUp "Playboi Carti Vocal Preset" / "Don Toliver Vocal Preset" / "XXXTentacion Vocal Preset", Cedar Sound Studios Carti preset, TuneDrip Carti + Toliver, Bumsonbeats Carti, Vocal Trappers Only Toliver, CrabLord Toliver pack. All third-party shops.

---

## 1. Playboi Carti (baby voice, Die Lit, Whole Lotta Red)

Source quality: **unverified** (no engineer or producer describes his vocal chain).

Sources read:
- [Powmag interview with engineer Ajruinedmyrecord](https://www.powmag.net/p/an-interview-with-ajruinedmyrecord) (2019). **engineer says**: works at Mean Street Studios; Carti "used to punch in more", but on the tape he cut many vocals as one performance; he is "more experimental now" with his voice.
- Search summaries of Fader / Complex interviews: sessions at DJ Drama's Mean Street Studios (Atlanta) and at his own home. Nothing about gear ❓ (pages themselves not read).
- Pi'erre Bourne, Paper / Fader profiles (via search summary ❓): says he found Auto-Tune at about 12 and the "T-Pain effect" shaped his style. Nothing about Carti's chain.
- Preset-seller blogs (**forum guess ❓**): [Cedar Sound Studios](https://www.cedarsoundstudios.com/blogs/news/carti-vocal-chain-how-to-nail-the-ad-libs-and-main-vox) (read in full: no engineer, no plug-in names, no settings), [VocalPresets.com](https://vocalpresets.com/blog/playboi-carti-vocal-chain) (read in full: "VocalPresets Team", no engineer). Tunedrip, Bumsonbeats, Mesh, RysUp: search summaries only.

### What is documented
- Engineer credit: Roark Bailey is listed as engineer on Whole Lotta Red in credit listings (search summary ❓). Aj is the engineer who gave the interview above. Neither says anything about the chain.
- The baby voice and the higher falsetto are **performance** (Carti's choice), not a plug-in. Pitch-up is only a community guess.
- Mojo Jojo / Shoota Auto-Tune: heard on the records, no settings documented anywhere found.

### Community recreation (forum guess ❓, 🎃 where marked)
Order used by the two blogs: pitch shift, Auto-Tune retune 0, hard compression, distortion, EQ, dark reverb send, layers.
- Pitch: +2 to +5 st for the high voice, -3 to -5 st for the deep voice.
- Auto-Tune retune speed 0, humanize 0.
- Compression 10:1 to 20:1, fast attack, 10-15 dB gain reduction.
- Distortion: tube saturation drive 50-80%, plus hard clip, highs cut at 6-8 kHz.
- EQ: high-pass 150-200 Hz, low-pass 6-8 kHz, scoop 500-800 Hz, bump 2-3 kHz.
- Reverb: hall 2-3 s, low cut 400 Hz, high cut 3-5 kHz, 30-40% wet.
- Layers: +12 st heavy distortion at -6 dB; -12 st filtered at -8 dB. Ad-libs +3 to +5 st, hard-panned, big reverb, tempo delay 1/8 or 1/4.
- Cedar says the ad-lib chain is more saturated than the lead. Both blogs call these typical, neither cites a source.

### Mapping table (what he owns)

| Step | Closest owned |
|---|---|
| Mic | SM7B (loud, close) or TLM 103. Carti's mic: not documented ❓ |
| Pitch up / down | Little AlterBoy (formant off), presets `08 High Octave Double`, `09 Low Octave Double`; or Live Shifter / Waves UltraPitch |
| Auto-Tune retune 0 | Auto-Tune Artist (his vstpreset exists), or Waves Tune Real-Time, or UADx Topline Vocal Tune |
| Crush compressor | UADx 1176 Rev A / LN Rev E, or Pro-C 2 (fast, 10:1+) |
| Distortion stages | Decapitator, bx_blackdist2, Saturn 2, Live Roar; bitcrush: Decimort 2 or Live Redux |
| EQ | Pro-Q 3 (HP 150-200, LP 6-8k) |
| Dark hall | ValhallaVintageVerb or ValhallaSupermassive, low cut 400 Hz, high cut 3-5 kHz |
| Tempo delay | EchoBoy or Live Echo 1/8 or 1/4 |
| Ad-lib detune / chorus | MicroShift, Doubler, Crystallizer (`12 Pitch Up`) |
| Width on layers | Ozone Imager 2 or Live Utility width |

### Proposed rack: "FX - Vocal Carti" (🎃 built from the community order, label it so)
Inserts (in order): Utility (gain) > Little AlterBoy (formant off, pitch to taste) > Auto-Tune Artist (retune 0) > UADx 1176 Rev A (fast, hard) > Decapitator (or bx_blackdist2) > Pro-Q 3 (HP 150, LP 7k, scoop 600) > Limiter.
Sends rack (Audio Effect Rack, chains, Dry chain at 0 dB):
- Dry 0 dB
- Layer up: AlterBoy +12 st > Decapitator hard > LP 6k, chain -6 dB
- Layer down: AlterBoy -12 st > Pro-Q 3 LP, chain -8 dB
- Dark hall: ValhallaVintageVerb 2.5 s, low cut 400 Hz, high cut 4 kHz, 100% wet, chain -14 dB
- Delay: EchoBoy 1/8, 2 repeats, HP 400 Hz, chain -18 dB
- Ad-lib chain (mute by default): AlterBoy +4 st > MicroShift > big Valhalla Supermassive, chain -12 dB
Existing start: `FX - Vocal Travis Autotune.adg` is probably close; compare before building.

### Open ❓ (Carti)
- Any engineer interview (Roark Bailey, Aj, Pi'erre Bourne's engineer) naming the chain.
- Is the "baby voice" a pitch shift in the mix or only his delivery? Not documented.
- Mic used (nothing found).

---

## 2. Don Toliver

Source quality: **partly, thin** (mic technique and live-sound facts only; no plug-in is attributed to his studio records).

Sources read:
- [Revolt: Derek "206derek" Anderson interview](https://www.revolt.tv/article/2023-03-24/282127/derek-anderson-don-toliver-has-albums-worth-of-songs-ready-interview) (Mar 2023). **engineer says**: Anderson has engineered Don since 2021, recorded every song on *Love Sick*, "my only responsibility is vocals" on albums he only engineers. Don "uses the room like Michael Jackson", turns his head for some ad-libs and may cover his mouth a little. Anderson applies effects mostly "following his lead". No mic, no chain, no mixer named.
- [UA blog: Apollo live for Don Toliver, Lil Durk, Karol G](https://www.uaudio.com/blogs/ua/apollo-delivers-studio-sound-live-for-don-toliver-lil-durk-trey-songz). **engineer says** (live, FOH John Buitrago): the Sonnox Oxford Dynamic EQ is the only plug-in that handles Don's whisper-to-scream range transparently, using per-band side-chain filters. Lexicon 224 as his go-to vocal reverb and Tube-Tech CL 1B + 1176LN as "vocal glue" are named for his vocals in general; the page does not say they are on Don's chain.
- Preset sellers (**forum guess ❓**): TuneDrip, RysUp, Vocal Trappers Only, CrabLord. They say Auto-Tune Pro, short delay, big reverb, leave peaks around -6 dB, automate FX in and out. No source.
- TuneDrip also says Mike Dean runs Don's vocals through analog gear before tuning. **No source, unverified ❓.** Credit listings (search summary) name Mike Dean as a mixer on *Heaven or Hell*, but that is not a chain.

### What is documented
- Tracking: a lot of room sound, and head and hand movement for ad-libs. 🎃 This means an open booth feel and some room reverb on the ad-libs, not a dry tight vocal.
- Effects are done by the engineer while recording, following Don's lead (so printed or monitored effects, same idea as the Future / Travis method in vocal-chains.md section G).
- Live: dynamic EQ is the key tool for his range.

### Mapping table

| Step | Closest owned |
|---|---|
| Room-style recording, head turns | SM7B or TLM 103 a bit back, plus a short room send (see rack) |
| Auto-Tune (blog claim ❓) | Auto-Tune Artist, retune about 10-20 ms for "floaty", or 0 for hard 🎃 |
| Oxford Dynamic EQ (live) | **Pro-Q 3 dynamic bands** (cut on peaks) or soothe2. Oxford Dynamic EQ itself is UAD-2 ❓ |
| Lexicon 224 vocal reverb | UADx Lexicon 224: **exact** |
| CL 1B + 1176LN glue | Softube Tube-Tech CL 1B + UADx 1176LN Rev E: **exact pair** |
| Delay + reverb "float" | EchoBoy / Live Echo 1/4, ValhallaVintageVerb or UADx EMT 250 |
| Ad-lib width | MicroShift, Doubler |

### Proposed rack: "FX - Vocal Don Toliver" (live facts + 🎃 for the rest)
Inserts: Utility > Auto-Tune Artist (retune 10-20 ms, key set) > Pro-Q 3 (dynamic band on the loud range, cut 2-4 kHz only when it spikes) > Tube-Tech CL 1B (fixed 1 ms / 50 ms, 3-5 dB) > UADx 1176LN Rev E (light) > Pro-Q 3 (static tone) > Limiter.
Sends rack (Dry chain at 0 dB):
- Dry 0 dB
- Lexicon 224 hall 2.5 s, 100% wet, chain -12 dB
- Echo 1/4, 2-3 repeats, HP 500 Hz, LP 4 kHz, chain -16 dB
- Room (ValhallaRoom small, 0.8 s, chain -14 dB), for the "Michael Jackson room" feel
- Ad-lib chain (mute by default): MicroShift > Little AlterBoy +3 st > EchoBoy 1/8 > Valhalla Supermassive, chain -12 dB
Start from `FX - Vocal Travis.adg` if it is close.

### Open ❓ (Toliver)
- Mic and preamp for the studio records (nothing found).
- Who mixes the vocals on each album (Mike Dean per credit listings, not checked).
- Auto-Tune settings: only preset-seller claims.

---

## 3. XXXTentacion

Source quality: **partly** (one real engineer, but he only discusses delay, the drums and a lo-fi mic story).

Sources read:
- [Studio Talks: Koen Heldens interview](https://studiotalksevents.com/blog/koen-heldens-xxxtentacion-sad-interview) and [XXL write-up of the same interview](https://www.xxlmag.com/xxxtentacion-engineer-details-recording-process/). **engineer says** (Heldens, mixer of "Sad!" and "Jocelyn Flores"):
  - "I had a delay line on the lead vocal." On "Sad!" he usually keeps feedback "around 10 percent", but it was almost infinite, so the vocal echoes through the open verse. A "happy accident".
  - "Red Light!" vocals were recorded with the mic of old iPhone earbuds. He had to make that usable.
  - He clips **drums and bass, not vocals**. The heavy distortion on "Look At Me!" came from a different session, not from X's vocal chain.
  - Kick re-amped through an Ampeg SVT + 8x10 cabinet. Snare pushed loud.
- [XXL: John Cunningham on the *?* album](https://www.xxlmag.com/xxxtentacion-john-cunningham-question-mark-album-interview/). **producer says**: about 90% of the album was recorded in X's bedroom, and X recorded "Sad!" himself at his computer. No gear.
- [Waves StudioVerse: Koen Heldens creator page](https://www.waves.com/studioverse/creator/mixedbykoenheldens) and the [`Small Vocal` chain](https://www.waves.com/studioverse/chain/c6b42930-a74b-4160-90e1-2bb760079fdb). Plug-in list only: CLA-76, DeEsser, PuigTec EQs, Renaissance Vox, Space Rider, SSL EV2 Channel. Tags: Chorus, Dance, Delay, EDM, Reverb, Vocals. **This is Heldens' own all-purpose chain, not the X chain.** No settings, order not stated.
- Equipboard's "SAD!" list (Auto-Tune Pro, Renaissance Vox, MV2, H-Delay, TSAR-1, Neve 1073, CL-1B, Apollo Twin) cites only a YouTube short (**forum guess ❓**, search summary only).
- Rolling Stone, "Look At Me!" feature (search snippet only ❓): he recorded it on a headphone mic, in about 15 minutes per producer Rojas. Page not read.
- [Black Rooster Audio](https://blackroosteraudio.com/en/artists/koen-heldens): Heldens' own vocal picks are their VPRE-73 preamp and VLA-2A compressor (promo page, **artist says** in a sponsored profile ❓).
- Cedar Sound / RysUp guides (**preset seller**): SM58, heavy compression, reverb, doubles. No source.

### What is documented
- The X sound is mostly **the source**: untreated rooms, cheap mics (earbuds, headphones), a bedroom. The mixer did not add fuzz to the vocal.
- The one named effect is a **vocal delay**, feedback 10% normally, runaway on purpose once.
- Heldens' general vocal tools (Waves chain above, VPRE-73, VLA-2A, SSL E channel) are his taste, not X's chain.

### Mapping table

| Step | Closest owned |
|---|---|
| Earbud / headphone mic color | Not a real mic: Live EQ Eight band-pass (about 200 Hz to 6 kHz) + Waves Retro Fi or Lofi Space 🎃 |
| CLA-76 | UADx 1176 Rev A / AE / LN (Waves CLA-76 not owned) |
| DeEsser | Waves DeEsser: **exact** |
| PuigTec EQs | UADx Pultec EQP-1A + MEQ-5: **same originals** |
| Renaissance Vox | Waves RVox: **exact** (that is its current name ❓ check) |
| Space Rider | Waves Space Rider: **owned** |
| SSL EV2 Channel | Waves SSL EV2 Channel: **owned** (name in his Waves list: SSL EV2 Channel) |
| VPRE-73 / VLA-2A | UADx 1073 / UADx LA-2A |
| Vocal delay, feedback 10% | EchoBoy or Live Echo, feedback 10%; runaway: raise feedback near 100% by automation for one phrase |
| Distortion on the drums/bass, not the voice | If you want grit on the voice: Decapitator on a parallel chain (🎃, not X's method) |

### Proposed rack: "FX - Vocal XXXTentacion"
Inserts (order 🎃, plug-in set from Heldens' Waves chain): Utility > Waves DeEsser > UADx 1176 Rev A (moderate) > Pultec EQP-1A + MEQ-5 > Waves RVox > Waves SSL EV2 > Limiter.
Lo-fi macro (Live EQ Eight band-pass + Retro Fi), wet/dry 0 to 100%, to get the earbud sound.
Sends rack (Dry chain at 0 dB):
- Dry 0 dB
- Delay: EchoBoy 1/4, **feedback 10%** (macro: feedback to 95% for the "Sad!" runaway), HP 300 Hz, chain -12 dB
- Space: Waves Space Rider, chain -16 dB
- Chorus: Brigade Chorus (the Heldens tags list Chorus), 100% wet, chain -18 dB
- Parallel grit (optional 🎃): Decapitator > Redux, chain -20 dB

### Open ❓ (XXXTentacion)
- What Heldens does on the "Look At Me!" or *17* vocals: not documented (he did not mix them as far as found).
- Rolling Stone headphone-mic line (only a snippet).
- Mic on the *?* album: not stated.
- Heldens' Sonic Scoop and Mixing Music podcast episodes likely say more; audio only, not read.

---

## 4. Thom Yorke (Radiohead, Kid A era)

Source quality: **partly** (no engineer interview naming the chain; one magazine Q&A, one magazine line on the vocoder, a reviewer's ears, fan-site lists).

Sources read:
- [Sound On Sound, Sound Advice: "How do I copy Thom Yorke's vocal sound?"](https://www.soundonsound.com/sound-advice/q-how-do-copy-thom-yorkes-vocal-sound) (Oct 2007, Mike Senior). **tutorial** (reader Q&A, a guess by ear, not Godrich):
  - Large-diaphragm condenser with extended lows and a high-end boost: AKG C12, C414B, MXL V77. Mic slightly below nose level, head tilted back, very close, maybe no pop shield.
  - Boost above 16 kHz, a "fairly hefty dose of compression", maybe de-ess, saturation or enhancer for fizz.
  - A **very dull reverb**, so the bright dry vocal stays in front.
- [MusicTech: Landmark Productions, Radiohead Kid A](https://musictech.com/guides/essential-guide/landmark-productions-radiohead-kid-a). **magazine text** (not a quote from Yorke): the title track has "vocoder-treated lead vocal" from Thom, manipulated further in Pro Tools. No mic named for the vocals.
- [Computer Music Journal review (Nick Collins, 2004), via citizeninsane.eu](https://citizeninsane.eu/media/usa/etc/06/pt_2004-05_computermusicjournal.html). **reviewer's ears**: "Everything in its Right Place" vocal repitched and processed; "Kid A" vocoding moving from reverb to feedback to distortion; *Amnesiac*: granular processing ("Packt Like Sardines"), pitch deviations and heavy reverb on words ("Pull/Pulk"). No plug-ins named.
- [ProSoundWeb, Radiohead tour sound (2012)](https://www.prosoundweb.com/a-busy-place-an-exclusive-look-at-sound-for-the-current-radiohead-tour/3/). **caption**: Yorke live on a Heil Sound PR 35. Monitor plug-ins named are the monitor engineer's, not stated for Thom.
- [HomeRecording.com thread (2002)](https://homerecording.com/bbs/threads/nigel-goodrich-implementing-vocal-effects-before-tracking.41704). **forum guess ❓**: a poster says Godrich had the vocal effects running before tracking so Thom could "play" them. The interview it quotes is not named.
- Search snippets only (pages blocked, **forum guess ❓**): fan site thekingofgear.com, quoting a 2001 *Wire* interview where Yorke says they "used Autotuner on Amnesiac twice"; Reverb.com's OK Computer gear piece, quoting Godrich's 1997 kit list: Neumann valve U47 and an Australian Rode valve mic, Urei 1176, Pultec EQ; In Rainbows: Electro-Voice RE20 (fan site). Gear lists on a fan site that says Jonny Greenwood looped and cut up Thom's voice with a Korg Kaoss Pad on "Everything in Its Right Place" (a live-rig description, ❓).
- [Mix magazine, "The Making of Tool's 10,000 Days"] was returned by `fetch_text.py` by mistake: ignore.

### What is documented
- Kid A: vocoder on the title track, Pro Tools editing, heavy treatment as texture (MusicTech, CMJ). Amnesiac: Auto-Tune, granular, pitch moves (Yorke's *Wire* quote via fan site ❓).
- OK Computer era: U47 > 1176 > Pultec as a Godrich kit list (second hand ❓).
- Live: Heil PR 35.
- The "dull reverb" idea is a magazine reader answer, not Godrich ❓.

### Mapping table

| Step | Closest owned |
|---|---|
| U47 / C12 type bright condenser | Neumann TLM 103 (closest), head tilted back, close (tutorial) |
| 1176 | UADx 1176 Rev A or LN Rev E |
| Pultec EQP-1A | UADx Pultec EQP-1A: **exact** |
| Boost above 16 kHz | Maag EQ4 **Air Band** (boost at the top) or Pro-Q 3 high shelf; Aphex AX for exciter 🎃 |
| Hefty compression | UADx LA-2A or Fairchild 660 after the 1176 🎃 |
| Saturation / valve fizz | Decapitator (Warm), Saturn 2, or Live Dynamic Tube |
| De-ess if bright | Waves DeEsser or RX 11 De-ess |
| Dull reverb | ValhallaRoom or VintageVerb, high cut about 2-3 kHz, longer decay, low in the mix 🎃 |
| Vocoder (Kid A) | Live **Vocoder** (carrier: a synth pad), or UAD Softube Vocoder (UAD-2 ❓), or Vocodine |
| Auto-Tune effect (Amnesiac) | Auto-Tune Artist, retune 0 on one chain |
| Granular / pitch smear | Live Grain Delay, Spectral Resonator, Spectral Time; Crystallizer |
| Comb / resonant filter (🎃, MusicRadar says GRM Comb on "The National Anthem", page not read ❓) | Live Corpus or Resonators, or Soundtoys FilterFreak |
| Kaoss-style cut-up (fan lists ❓) | ShaperBox 3 volume + filter shapes, Live Beat Repeat |
| Reverse echo | Crystallizer `06 Echo Reverse` |

### Proposed rack: "FX - Vocal Thom Yorke"
Inserts: Utility > UADx 1176 Rev A (3-6 dB) > UADx Pultec EQP-1A > UADx LA-2A (light) > Maag EQ4 (Air Band up) > Waves DeEsser > Auto-Tune Artist (macro: retune 0 on/off) > Limiter.
Sends rack (Dry chain at 0 dB):
- Dry 0 dB
- Dull reverb: ValhallaRoom, long decay, **high cut 2-3 kHz**, 100% wet, chain -12 dB (the "dull reverb" trick: the voice stays bright in front)
- Vocoder: Live Vocoder with a pad carrier, chain -10 dB (Kid A title track)
- Granular: Live Grain Delay or Spectral Resonator, chain -16 dB
- Reverse echo: Crystallizer `06 Echo Reverse`, chain -16 dB
- Comb: Live Corpus or Resonators, chain -18 dB (optional 🎃)
Macro idea 🎃: "play the effects" (Godrich method per the forum ❓): map the chain levels to Macros so the singer can ride them while recording.

### Open ❓ (Thom Yorke)
- Is there an engineer interview (Godrich, Tape Op / SOS / Mix) for Kid A vocals? None found.
- Original *Wire* 2001 quote and the Reverb.com list: not read, only second-hand snippets.
- Kid A vocal mic and preamp: not found.
- MusicRadar "National Anthem" vocal-effect tutorial: page came back empty, not read.

---

## 5. Bon Iver / Justin Vernon (22, A Million; the Messina; Woods)

Source quality: **documented** (22, A Million, Sound On Sound Inside Track). Earlier records: thin.

Sources read:
- [Sound On Sound Inside Track: Bon Iver *22, A Million*](https://www.soundonsound.com/techniques/inside-track-bon-iver-22-a-million) (Paul Tingen, about Jan 2017). **engineer says** (mixer Zach Hanson, engineer Chris Messina):
  - Vernon sings into an **SM7**, sings a line, duplicates the track, sings again. Some songs have about 40 vocal tracks, in blocks of 6 or 8 per section, each a real take. He changes tone by using different SM7 mics or different distances.
  - Almost every vocal track has **Auto-Tune**. Hanson: it "doesn't only tune his vocal, it also adds a kind of saturation".
  - On one song a **Tube-Tech multiband compressor** on the vocal bus calmed parts of the voice as the stack built.
  - Vocals and effects go to Bus B of an SSL Duality, with the SSL bus compressor on the stereo mix.
  - Reverb: Bricasti M7 (Dark Chamber), two AMS RMX16, an AKG spring, an EMT 140 plate. Eventide H3000 used across the album (use on vocals not stated).
  - Speed trick: "#29 Strafford Apts" sped-up, pitched-up vocals via varispeed on an Antelope Isochrone Trinity master clock; session slowed slightly, printed to an Ampex ATR-102, re-recorded at the right speed.
  - Another song's tracks were tuned down a few cents on the clock, which shifts the formant (the mixer says it sounds "more feminine", the tracking only).
- **The Messina, same article. engineer says** (Messina, Vernon). Signal chain:
  1. Input into **Ableton Live**.
  2. **Two Auto-Tune plug-ins**: the first tunes the vocal as usual; the second outputs a **single tonic note** for the key of the phrase.
  3. An **Eventide H8000** set to a MIDI harmony program gets the tonic, the dry signal and Vernon's **MIDI keyboard**; it makes up to **four notes**, with some randomisation and many artifacts (key-change clicks kept on purpose).
  4. Messina blends dry, tuned, tonic and harmony signals.
  - They tested "every single vocoder" and all sounded like a vocoder. The Prismizer (Francis Starlite) was only an inspiration, not the same tech. Also used live. "715" is Vernon alone with the Messina, mostly one take.
- [W Magazine on Messina](https://www.wmagazine.com/story/the-engineer-behind-bon-ivers-22-a-million-clears-up-any-confusion-about-its-high-tech-sound): **engineer says** (Messina): a laptop running software feeds a physical piece of hardware; parts are off-the-shelf "used the way they're not normally intended"; "It's merely an effect." No model names there.
- [Antares blog, Bon Iver live](https://www.antarestech.com/blog/bon-iver-vocal-sounds-live): **engineer says** (Messina), tour: multiple Auto-Tune and Harmony Engine instances plus some Eventide hardware.
- [Bonedo, "Mythos Prismizer"](https://www.bonedo.de/artikel/mythos-prismizer-der-unkaeufliche-vocal-effekt/) (German). **tutorial**: harmonizer (Antares Harmony Engine) with Auto-Tune on the input, a MIDI keyboard to pick notes; or several copies of the vocal, each with its own Auto-Tune, pitch per track by MIDI; blend with the lead. Quotes Messina that the Prismizer is "many things working together".
- Search snippets only, pages blocked (❓): AudioTechnology on *i,i* (HTTP 403), where Messina's rig is described with the H8000 sent a tonic note, and the studio early gear is LA-2As and Neve 1073 preamps; Brad Cook (Tape Op #156 snippet) calls it the H9000 "or maybe the H8000". So the Eventide model is H8000 per SOS, which is the better source.
- Far Out / W Magazine: "Woods" (2009, *Blood Bank*) is the song where Auto-Tune started; **no gear or settings** found for it. *For Emma* (2007): **an SM57**, layered falsetto stacks (MusicRadar headline, text not read ❓).
- Not found: a Vernon mic *preamp*, or a Messina setting list.

### What is documented (the core)
- SM7(B) into a modern session, **many layered takes**, **Auto-Tune on nearly everything**.
- The Messina: Auto-Tune (normal) + Auto-Tune (tonic only) + H8000 MIDI harmonizer + MIDI keys, blended.
- Varispeed through a tape machine for the pitched-up voices.

### Mapping table

| Step | Closest owned |
|---|---|
| SM7 | **SM7B: exact** |
| 40-take stack | Live: 6-8 takes per section, different distances; Vocal Doubler / Waves Doubler for quick fakes |
| Auto-Tune on everything | Auto-Tune Artist (or UADx Topline Vocal Tune / Waves Tune Real-Time) |
| Tonic-note Auto-Tune | Not a feature of Auto-Tune Artist ❓ (check). Workaround: play the tonic yourself on MIDI to the harmonizer |
| Eventide H8000 harmonizer, 4 notes, MIDI | **Eventide Quadravox** (4 voices; MIDI control ❓ check in the plug-in); or Waves Harmony (MIDI ❓); or Live Auto Shift (MIDI in, he already has a rack); or UAD Eventide H910 (UAD-2 ❓) |
| Random artifacts | Live Shifter with small jitter 🎃, or Quadravox glide; Decimort 2 on the harmony chain |
| Tube-Tech multiband | Pro-MB or Live Multiband Dynamics (Tube-Tech SMC 2B not owned) |
| SSL bus compressor | Waves SSL comp or UADx SSL G |
| Bricasti M7 Dark Chamber | Pro-R (dark), or ValhallaRoom dark chamber preset 🎃 |
| AMS RMX16 | UAD AMS RMX16 (UAD-2 ❓); native: UADx Lexicon 224 or ValhallaRoom |
| AKG spring | Waves Magma Springs (UAD AKG BX 20 is UAD-2 ❓) |
| EMT 140 plate | UADx EMT 140: **exact** |
| H3000 | UAD H910 (UAD-2 ❓); native: Quadravox or Little AlterBoy |
| Varispeed + ATR-102 | UADx Ampex ATR-102 plus Live warp off, transpose clip (tape-speed effect) |
| Formant drop via clock | Little AlterBoy formant, or Live Shifter formant |

### Proposed rack: "FX - Vocal Bon Iver"
Inserts: Utility > Auto-Tune Artist (normal tuning, tune to key) > Pro-Q 3 (HP 80 Hz, tone) > Pro-MB (gentle, on 2 bands) > UADx LA-2A (light) > Limiter.
Sends rack (Dry chain at 0 dB):
- Dry 0 dB
- **Messina chain** (audio effect rack inside, 100% wet, chain -8 dB): Auto-Tune Artist (hard, retune 0) > **Eventide Quadravox** (4 voices to the key, play it from a MIDI keyboard) > Decimort 2 (light, for artifacts) > Pro-Q 3 (LP 8 kHz). Keep a dry, a tuned and a harmony level each as a macro.
- Choir double: Little AlterBoy `03 Modern Double` / `05 Rich 5ths` > MicroShift, chain -12 dB
- Tape pitch: UADx Ampex ATR-102 with a pitched clip (varispeed-style) chain -14 dB (print and move to a track)
- Dark chamber: ValhallaRoom dark chamber, 100% wet, chain -14 dB
- Plate: UADx EMT 140 2 s, chain -16 dB
- Spring: Waves Magma Springs, LP, chain -18 dB
Existing start: `FX - Auto Shift Live Harmonizer.adg` and `FX - Bvoc Choir.adg` in his User Library.

### Open ❓ (Bon Iver)
- Does Eventide **Quadravox** take MIDI note input like the H8000 program, and can it follow a tonic note? Check in the plug-in before building.
- Can Auto-Tune Artist output a single tonic note (the second Auto-Tune in the Messina)? Probably not as such ❓.
- "Woods" (2009) and *For Emma* (2007) vocal chain: only the SM57 + stacking claim (snippet), nothing else.
- Preamp used on 22, A Million vocals: not stated in the SOS text read. AudioTechnology page blocked.

---

## Open ❓ list (all five)

- **Carti:** any engineer or producer interview that names a chain (none found). Whether the baby voice is processed.
- **Toliver:** studio mic, mixer per album, Auto-Tune settings. Mike Dean claim (TuneDrip) unverified.
- **XXXTentacion:** Rolling Stone headphone-mic line (snippet); what Heldens does on the "Look At Me!" era vocals; Waves `Small Vocal` plug-in order and settings (StudioVerse needs an account, settings not shown).
- **Thom Yorke:** a Godrich interview on Kid A / Amnesiac vocals; the *Wire* 2001 Autotuner quote and Reverb.com kit list (second-hand only); MusicRadar "National Anthem" tutorial (page empty).
- **Bon Iver:** Quadravox MIDI behaviour; a tonic-note Auto-Tune; "Woods" chain.
- Waves CLA-76 and PuigTec EQs are in the Heldens chain but not in his owned Waves list: UADx 1176 and Pultecs are used instead.
- UAD-2 items (H910, RE-201, RMX16, Oxford Dynamic EQ, Softube Vocoder): need the Apollo, marked ❓. At home with the RME, use the native stand-ins.
- Existing racks from batch 1 (`FX - Vocal Travis*.adg`, `Auto Shift Live Harmonizer`, `Bvoc Choir`) were not opened (read-only); check how close they are before building new ones.
- Buy: nothing needed for any of the five. Eventide H3000/H8000 and Antares Harmony Engine are the only named tools he lacks; Quadravox / Waves Harmony / Live Auto Shift stand in.
