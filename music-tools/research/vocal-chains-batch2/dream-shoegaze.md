# Vocal chains batch 2: dream pop and shoegaze singers

🎸 Studio · research, 2026-11-15. Text only. Nothing downloaded, nothing modified.
Singers: Victoria Legrand, Slowdive (Halstead + Goswell), DIIV (Zachary Cole Smith), Greg Gonzalez, Julee Cruise, Jeremy Enigk.
Labels: **engineer says** · **artist says** · **tutorial** · **forum guess ❓** · 🎃 = my own inference.
❓ = unsure or not checked. UAD-2 plug-ins (names starting "UAD ") need the Apollo: marked ❓UAD-2.
Style model: `../vocal-chains.md` (sections A-K).

## 0. Honest headline

Dream pop and shoegaze engineers almost never publish vocal chains.
Searched: Sound On Sound, Tape Op, Mix, Sonic Scoop, Interview, Reverb.com, NPR, Quietus, Believer, Gearspace, Equipboard.
Result: **no singer here has a documented mic > pre > comp > EQ chain.**
What IS documented is small but real: rooms, mic placement, a few reverb units, and who mixed.
Everything else below is labelled 🎃 or tutorial. Racks are built from the style, not from stated settings.

| Singer | Source quality | Best single finding |
|---|---|---|
| Legrand | Partly | Coady recorded her in a big live room with no baffles; effects are secret by band request |
| Slowdive | Unverified | Halstead: vocals "buried"; reverb "discovered" at a demo mix; no vocal chain exists in print |
| DIIV | Unverified | Smith: Oshin vocals drowned in reverb; Deceiver pushed them forward slightly |
| Gonzalez | Unverified | Self-recorded and self-produced; only whisper-style backing vocals and "high reverb" are stated |
| Cruise | Partly | Badalamenti had her whisper the song; heavy digital reverb; mic and unit unnamed |
| Enigk | Partly | Realistic PZM mic mounted on a wall (solo era); dislikes compression; Diary chain not found |

## 0.1 Owned plug-ins used in this file (from the four owned lists)

- Native/UADx (`uaudio_*`): LA-2A Silver/Gray, LA-3A, 1176 Rev A / AE / LN, Neve 1073, Fairchild 660/670, Pultec EQP-1A, HLF-3C, MEQ-5, Manley Massive Passive, Manley VoxBox, Distressor, Studer A800, Ampex ATR-102, Galaxy Tape Echo, EMT 140, EMT 250, Lexicon 224, Pure Plate, Capitol Chambers, Ocean Way, Brigade Chorus, Studio D Chorus, Little Labs VOG, Avalon VT-737sp.
- UAD-2 only ❓UAD-2: AMS RMX16, Lexicon 480L, EP-34 Tape Echo, Roland RE-201, Roland Dimension D, Roland CE-1, Eventide H910, Korg SDD-3000, Cooper Time Cube, Vitalizer, Thermionic Vulture.
- Soundtoys: EchoBoy (+Jr), Crystallizer, Decapitator, Devil-Loc, Radiator, MicroShift, PrimalTap, PhaseMistress, Tremolator, FilterFreak, PanMan, Little AlterBoy, Little Plate.
- Valhalla: VintageVerb, Room, Plate, Shimmer, Supermassive, Delay, FreqEcho, SpaceModulator, UberMod.
- Waves: RVerb, H-Delay, Doubler, Reel ADT, MetaFlanger, Abbey Road Chambers, ARPlates, Abbey Road Reverb Plates, J37, REDD37-51, API-2500, SSL channels, RS56, RComp, DeEsser, Harmony, UltraPitch, Waves Tune Real-Time, Silk Vocal, Butch Vig Vocals, JJP-Vocals, Greg Wells VoiceCentric, Clarity Vx.
- Others: FabFilter Pro-Q 3, Pro-C 2, Pro-R, Pro-MB, Saturn 2, Timeless 3, Volcano 3; oeksound soothe2; Auto-Tune Artist; Melodyne; Vocal Doubler; AIR Tape Double Track; SketchCassette (I and II); RC-20; Decimort 2; ShaperBox 3; Tube-Tech CL 1B (mk II); bx_digital V3; Ozone Imager 2; RX 11 (De-ess, De-plosive, Breath Control); Trackspacer 25.
- Live 12 Suite stock: EQ Eight, Compressor, Glue Compressor, Multiband Dynamics, Limiter, Gate, Echo, Delay, Reverb, Hybrid Reverb, Chorus-Ensemble, Phaser-Flanger, Saturator, Roar, Pedal, Redux, Auto Filter, Auto Pan, Utility, Spectral Resonator, Grain Delay.

## 0.2 Local preset folders checked (read-only)

Searched: `~/Library/Audio/Presets`, `/Library/Audio/Presets`, `~/Music/Ableton/User Library/Presets`, `/Users/Shared/Waves/Plug-In Settings`, Soundtoys and Documents/Soundtoys (does not exist).
No preset is named for any of these singers or bands.
Useful generic vocal-reverb presets that DO exist (Valhalla Room, all under `/Library/Audio/Presets/Valhalla DSP, LLC/ValhallaRoom/`):

- `Den/BalladVocalFemale.vpreset`, `Den/BalladVocal1.vpreset`, `Den/BalladVocal2.vpreset`, `Den/VocalHall1.vpreset`, `Den/VocalHall2.vpreset`, `Den/BigVocalHall.vpreset`
- `Halls/Vocal-HugeDarkRoom.vpreset`, `Halls/BigVocalHall.vpreset`
- `Dense Room/DR-Wide Female Vocal.vpreset`
- `Max Braiman Essentials Send/VOCAL - Heavy`, `VOCAL - Modulate`, `VOCAL - Chamber`, `FX - Ghost`, `FX - Foggy`, `FX - Forever`
- `Sulaco/SulacoGothicCathedral.vpreset`, `LV426/LV426Cathedral.vpreset`, `patchpool/Ghosts.vpreset`
- Dark halls in `Den/`: `DeepNarcissusHall`, `LexDarkHall`, `Large Hall-480 Dark`, `Dark Chamber`

UberMod (`/Library/Audio/Presets/Valhalla DSP, LLC/ValhallaUberMod/`): `Echos/VocalEcho.vpreset`, `Echos/BasicTapeEcho.vpreset`, `Chorus/VocalDualPitch.vpreset`, `Reverbs/TapeVerb.vpreset`, `patchpool/Endless Dream.vpreset`, `patchpool/60s Dream V1.vpreset`.
Valhalla Shimmer: `ValhallaShimmer/BrightHall`, `ConcertHall`, `DeepBlueDay`, `Chorus` (`.aupreset`).
Empty: Waves `Butch Vig Vocals`, `JJP-Vocals`, `Silk Vocal` user-preset folders (0 files; the built-in factory presets live inside the plug-in, not on disk).
ValhallaVintageVerb, Delay, Supermassive, Plate: no preset files on disk (factory presets are inside the plug-in).
Soundtoys: factory presets are inside the plug-in, not on disk ❓.

Commercial named presets found online (names only, not downloaded, seller claims):
- Cedar Sound Studios "Cigarettes After Sex Vocal Preset" and "Shoegaze Vocal Preset" (seller says: built from stock DAW plug-ins, light pitch correction).
- No Waves, Soundtoys, Valhalla, FabFilter or UAD signature preset for Coady, Legrand, Slowdive or any singer here was found.

---

## 1. Victoria Legrand (Beach House)

### Sources
- [Sonic Scoop: Behind the Release, Beach House *Bloom*](https://sonicscoop.com/?p=28515) (Coady)
- [Sonic Scoop: Chris Coady on Beach House](https://sonicscoop.com/?p=5787) (*Teen Dream* room mics; no vocal detail)
- [Mix: Beach House *Bloom*](https://www.mixonline.com/?p=50655) (credits only)
- [Interview Magazine: Chris Coady](https://www.interviewmagazine.com/music/chris-coady-beach-house)
- [DMY: Beach House interview](https://dmy.co/features/beach-house-interview-uh-oh-trouble)
- [Reverb Machine: She's So Lovely remake](https://reverbmachine.com/blog/how-beach-house-created-shes-so-lovely/) (tutorial)
- [Tape Op 168: Chris Coady](https://tapeop.com/interviews/168/chris-coady) (paywalled, vocal part not readable ❓)
- Gearspace *Devotion* thread and Equipboard (403 or aggregator; seen only through search summaries ❓)

### What is documented
- *Bloom* (2012). Producer/engineer/mixer Chris Coady. Tracked at Sonic Ranch (Texas), mixed at Electric Lady. **engineer says**: vocals recorded in the huge live room "with no baffles".
- Effects on her voice: Coady called it a "secret cocktail". **engineer says**: the band asked him not to say. So reverbs and delays are deliberately unpublished.
- Mix writer: her vocals sit in a "deeply reverberant field" (writer's description, not gear).
- *Teen Dream* (2010). Dreamland church studio, API console, two Earthworks room mics high and far away. **engineer says** (Sonic Scoop). Not tied to vocals.
- Coady: recording her was "effortless"; she was trained as a singer; nothing may overpower her voice. **engineer says** (Interview). Scally (not Legrand) did "25 takes" on some songs. **artist says** (DMY).
- *Devotion* (2008, different engineer): clean reverbs from a TC M3000, dirtier ones from an Eventide H3000. **forum guess ❓** (Gearspace quoting Rob Girardi; page blocked, summary only).
- Live: Audix OM7 mic and an Electro-Harmonix Holy Grail reverb. **forum guess ❓** (Equipboard photo guess, bio site).
- Mic, preamp, compressor, EQ on the studio vocal: **not documented anywhere I could reach.**

### Plug-ins / presets named
- None by the engineers. TC M3000 and Eventide H3000 (hardware) from the forum.
- Tutorial only: Valhalla VintageVerb on a shared reverb send, high cut lowered, modulation 10%, pre-delay removed, shorter decay (Reverb Machine, about the instruments, vocal unclear).
- Local presets that fit the idea: `Den/BalladVocalFemale`, `Halls/Vocal-HugeDarkRoom`, `Dense Room/DR-Wide Female Vocal`.

### Mapping

| Step | Source label | Owned |
|---|---|---|
| Big live room, no baffles | **engineer says** | Your room: record in the biggest room you have, mic 1 to 1.5 m away. Hybrid Reverb can add a room IR 🎃 |
| Mic / pre | undocumented | TLM 103 > Apollo pre. UADx Neve 1073 as pre colour 🎃 |
| Light compression | 🎃 | UADx LA-2A Silver or Waves RS56 + RComp, 2-3 dB |
| EQ | 🎃 | Pro-Q 3: HP 90 Hz, small air shelf |
| TC M3000 clean | **forum guess ❓** | Valhalla VintageVerb (Concert Hall or Large Plate), or UADx Lexicon 224 |
| H3000 dirty | **forum guess ❓** | Valhalla Room "Dark Chamber" into Decapitator, or ❓UAD-2 Eventide H910 |
| Tape / room colour | 🎃 | UADx Studer A800 or Oxide Tape on the return |

### Proposed rack: "Legrand, big hall"
Inserts (in order): Utility (gain) > UADx Neve 1073 (light drive) > UADx LA-2A Silver (2-3 dB) > Pro-Q 3 (HP 90 Hz, +1.5 dB air at 10 kHz) > RX 11 De-ess (only if needed).
Sends rack (Audio Effect Rack, 4 chains):
1. Dry, 0 dB.
2. Hall: ValhallaVintageVerb, large hall, decay 3.5-4.5 s, pre-delay 40 ms, high cut about 6 kHz, then Trackspacer or Live Compressor sidechained to dry vocal. Chain volume start -12 dB.
3. Dirty room: ValhallaRoom `Dark Chamber` > Decapitator (low drive, "A" style) > Pro-Q 3 (LP 5 kHz). Start -18 dB.
4. Tape echo: UADx Galaxy Tape Echo or EchoBoy, 1/4 dotted, feedback 25%, filter dark. Start -20 dB.
Set Dry 0 dB first, bring wets up until the voice floats, never covers words.

Source quality: **partly** (room documented, chain not).

### Open ❓
- Real mic/pre/comp on Teen Dream, Bloom, Depression Cherry: not found. Tape Op 168 may say, paywalled.
- Is the M3000/H3000 claim true for her later records?

---

## 2. Slowdive (Neil Halstead, Rachel Goswell)

### Sources
- [Reverb.com: Slowdive interview](https://reverb.com/news/slowdive-interview) (403 for me, used through search summary ❓)
- [NPR: Halstead on *everything is alive*](https://www.npr.org/2023/09/09/1198625743/slowdives-neil-halstead-on-their-new-album-everything-is-alive) (summary only; page timed out ❓)
- [The Quietus: Halstead interview](https://thequietus.com/interviews/neil-halstead-slowdive-interview/)
- [Guitar World: Christian Savill](https://www.guitarworld.com/features/slowdive-christian-savill-everything-is-alive) (guitar pedals)
- Credits: Discogs / Rate Your Music for *Souvlaki* and *Slowdive* (2017)

### What is documented
- **artist says** (Halstead, NPR 2023, via summary ❓): bands of that era did not want audible vocals; the vocals are "buried" in the mix.
- **artist says** (Halstead, Reverb.com, via summary ❓): the band "discovered" reverb on their second demo at Martin Nichols' studio, where it was added to the vocals during mixing. Before that he had only distortion and delay.
- *Souvlaki* (1993) credits: mixed by Ed Buller and band; Brian Eno credited "treatments" and keyboards; engineers Guy Fixsen, Andy Wilkinson, Chris Hufford, Martin Nichols. Credits only.
- *Slowdive* (2017): mixed by Chris Coady at Sunset Sound, LA; Steve Clarke "additional vocal engineer". Credits only.
- Halstead (Quietus): the sound came before the melody; closed sessions. Not about vocals.
- Pedals on guitars (Savill): Strymon reverb and similar. Not vocals.
- Mic, preamp, compressor, EQ, reverb unit on either singer: **not found. Nobody has published it.**

### Plug-ins / presets named
None. No named presets from any maker.
Community description only: heavy reverb, doubled harmony between Halstead and Goswell, vocal level tucked low 🎃.

### Mapping (all 🎃 unless marked)

| Step | Owned |
|---|---|
| Mic | SM7B or TLM 103 (his pick) |
| Light comp | UADx 1176 Rev A, slow attack, 2 dB |
| EQ | Pro-Q 3, HP 100 Hz, dip 300 Hz a little, soft top |
| Harmony pair (two voices) | Record two takes; or Waves Harmony / Little AlterBoy for a second voice ❓ |
| Doubling | Waves Doubler, Vocal Doubler, or AIR Tape Double Track |
| "Reverb added at mix" | Valhalla VintageVerb, long decay; Valhalla Shimmer for lift |
| Chorus / flange colour (Buller credited "flanger") | Live Chorus-Ensemble, Waves MetaFlanger, Soundtoys PhaseMistress |
| Tape grit | UADx Studer A800 or SketchCassette |

### Proposed rack: "Slowdive, tucked"
Inserts: Utility > UADx 1176 Rev A (2 dB) > Pro-Q 3 > Waves Doubler (subtle, 15-20 ms) > RX 11 De-ess.
Sends rack:
1. Dry, 0 dB (keep it low in the song mix, this style hides the voice).
2. Huge reverb: VintageVerb, decay 6-8 s, pre-delay 20 ms, damping high, modulation up. Start -8 dB.
3. Shimmer: ValhallaShimmer `BrightHall` (preset on disk), mix 100%, blend by chain volume. Start -16 dB.
4. Modulated delay: ValhallaDelay or EchoBoy 1/4, feedback 40%, then MicroShift or MetaFlanger. Start -14 dB.
5. Optional fader automation of sends 2-4 during phrases, like Halstead playing the faders live in a mix 🎃 (this "live fader" idea came from a search summary, not read directly ❓).

Source quality: **unverified**.

### Open ❓
- Reverb.com and NPR pages not read in full (403 / timeout). Re-check the Halstead quotes.
- Coady / Steve Clarke vocal gear on the 2017 album.
- Which reverb unit Nichols and Buller used on *Souvlaki*.

---

## 3. DIIV (Zachary Cole Smith)

### Sources
- [Interview Magazine: DIIV *Oshin*](https://interviewmagazine.com/music/diiv-oshin) (Smith on Schlett)
- [Rolling Stone: DIIV on new LP](https://www.rollingstone.com/music/music-features/diiv-on-how-heroin-sky-ferreira-influenced-new-lp-178584/)
- [NME: DIIV 2024](https://www.nme.com/features/music-interviews/diiv-interview-looking-easy-solution-addiction-found-theres-not-one-2555618)
- [Guitar World: DIIV, *Frog in Boiling Water*](https://www.guitarworld.com/features/diiv-zachary-cole-smith-andrew-bailey-frog-in-boiling-water) (guitar only)
- AllMusic *Deceiver* review; credits via Discogs / RYM

### What is documented
- *Oshin* (2012): engineer and mixer Daniel James Schlett at Strange Weather, Brooklyn; Smith produced. Credits.
- **artist says** (Smith, via search summary ❓): *Oshin* vocals "bathed in reverb and buried deep in the mix"; the album was partly "hiding behind a sound".
- **artist says** (Smith, Interview, read via snippet): he often asked Schlett for extreme things, e.g. "Turn that compression up more!" General, not tied to the vocal ❓.
- *Is the Is Are* (2016): Smith self-produced; Strange Weather and The Bunker; engineers unclear ❓. He said he took a new approach to vocals (no details).
- *Deceiver* (2019): producer/engineer/mixer Sonny DiPerri. AllMusic reviewer: vocals pushed forward slightly. NME: Smith's vocal is mostly backed by a quiet second voice (Colin).
- Guitar World 2024: both guitarists use Strymon Timeline and Big Sky. **Guitars only.**
- Mic, preamp, vocal reverb unit, vocal compressor: **not found.**

### Plug-ins / presets named
None for voice. Strymon Timeline / Big Sky are hardware on guitars; not applicable to vocals.

### Mapping (🎃 from the descriptions)

| Step | Owned |
|---|---|
| Mic | SM7B (close, dry) or TLM 103 |
| Heavy compression (Smith likes it) | UADx 1176 Rev A or LN, fast, 6-8 dB, or Distressor |
| EQ | Pro-Q 3, HP 120 Hz, scoop mud, +2 dB at 4 kHz for the Deceiver-era forward vocal |
| Second quiet voice (Colin style) | Duplicate lane, -6 dB, Waves Doubler or Harmony |
| Reverb (Oshin: drowned) | Valhalla VintageVerb / Room, decay 3-5 s |
| Modulated delay | Valhalla Delay, or Echo |

### Proposed rack: "DIIV, forward-in-fog"
Inserts: Utility > UADx 1176 Rev A (6 dB) > Pro-Q 3 > Saturn 2 or Decapitator (low) > RX 11 De-ess.
Sends rack:
1. Dry, 0 dB.
2. Plate/Hall: ValhallaPlate or VintageVerb, decay 3-4 s, pre-delay 25 ms. Start -10 dB (go -6 dB for the Oshin fog).
3. Shimmer-lite: Valhalla Supermassive, "Gem" or similar, 20% mix. Start -18 dB.
4. Delay: EchoBoy 1/8, feedback 20%, Roar or Decimort to dirty it. Start -16 dB.
Two switches: Oshin = dry down 6 dB, send 2 up. Deceiver = dry 0 dB, send 2 down.

Source quality: **unverified** (only one general compression remark).

### Open ❓
- Dan Schlett and Sonny DiPerri interviews about the vocal chain: not found.
- Read the full Interview Magazine *Oshin* page (excerpt only).
- Smith's Oshin reverb quote: confirm in a primary page, not a summary.

---

## 4. Greg Gonzalez (Cigarettes After Sex)

### Sources
- [Daijiworld: Gonzalez on the dreamy sound](https://www.daijiworld.com/news/newsDisplay?newsID=1043403)
- [Magnet: *Songs from a Room* (self-titled)](https://magnetmagazine.com/2017/09/27/cigarettes-after-sex-songs-from-a-room/) (via search summary)
- [Equipboard: Greg Gonzalez](https://equipboard.com/pros/greg-gonzalez) (crowd)
- [Cedar Sound Studios: shoegaze vocal guide](https://cedarsoundstudios.com/blogs/news/mastering-the-art-of-mixing-shoegaze-vocals-a-comprehensive-guide) (seller)
- [Cedar: Cigarettes After Sex vocal preset](https://www.cedarsoundstudios.com/products/cigarettes-after-sex-vocal-preset) (seller)

### What is documented
- Credits (RYM, via search): Gonzalez recorded and produced the debut; Rocky Gallo mixed; Greg Calbi mastered. *X's*: Gonzalez produced and recorded, Los Angeles.
- **artist says** (Daijiworld): he records "live inside the studio"; guitars on high reverb; background vocals arranged like a whisper; soft, understated mix. No gear named.
- **artist says** (Magnet, via summary ❓): earlier home recording "didn't capture what I heard".
- Live KEXP: Shure Beta 57A. **forum guess ❓** (Equipboard).
- A Magnet note says his voice is NOT buried like other dream pop ❓ (summary; conflicts with other reviews that say "reverb-cloaked").
- Vocal chain: **not documented.** No SOS, Tape Op or engineer piece found.

### Plug-ins / presets named
- Seller blog (**tutorial**, commercial): pre-delayed hall reverb, Valhalla VintageVerb named; dreamy delay with automation and ducking (Valhalla Delay named); phaser/chorus (Valhalla Supermassive named); pitch correction optional.
- Cedar "Cigarettes After Sex Vocal Preset" (3 DAW chain tabs, stock plug-ins, light pitch correction, seller claim). Not downloaded.

### Mapping

| Step | Owned |
|---|---|
| Close, intimate mic | TLM 103 close at low gain, or SM7B 🎃 |
| Soft comp | UADx LA-2A Gray or Waves RS56 + RComp, 3 dB 🎃 |
| EQ | Pro-Q 3: HP 80 Hz, low-mid warmth, rolled top 🎃 |
| Light tuning (seller) | Auto-Tune Artist, retune 25-40 ❓ |
| Pre-delayed hall (tutorial) | Valhalla VintageVerb Hall, pre-delay 60-80 ms |
| Ducked delay (tutorial) | Valhalla Delay with ducking, or EchoBoy + Trackspacer |
| Whisper backing voices | 2nd lane, -10 dB, Pro-Q 3 LP 6 kHz, Waves Doubler |

### Proposed rack: "Gonzalez, whisper hall"
Inserts: Utility > UADx LA-2A Gray (3 dB) > Pro-Q 3 > Auto-Tune Artist (optional, slow) > RX 11 De-ess > Soothe2 (light, tame the close-mic hiss).
Sends rack:
1. Dry, 0 dB.
2. Hall: VintageVerb hall, 3 s, pre-delay 70 ms, bass cut. Start -11 dB. Sidechain to dry.
3. Ducked delay: ValhallaDelay 1/4, feedback 30%, duck 50%. Start -14 dB.
4. Whisper bus (for backing lane): Pro-Q 3 LP 5 kHz > hall at 100% on a second return.

Source quality: **unverified**.

### Open ❓
- Which engineer or studio recorded each album? Credits show Gonzalez as recorder.
- Any Tape Op or Mix feature on Rocky Gallo.
- Check the Magnet and Daijiworld quotes against the full pages.

---

## 5. Julee Cruise (Badalamenti / Lynch)

### Sources
- [The Believer: An Interview with Angelo Badalamenti](https://believermagazine.substack.com/p/an-interview-with-angelo-badalamenti) (read directly)
- [Twin Peaks Blog: Gavin Report, May 1990](https://twinpeaksblog.com/2025/06/02/david-lynch-julee-cruise-and-angelo-badalamenti-in-the-gavin-report-from-may-11-1990/) (via summary)
- [Uncut on *Floating into the Night*](https://www.uncut.co.uk/?p=100880) (403; summary only ❓)
- [Film Comment: Playing Along, music of Twin Peaks](https://www.filmcomment.com/article/playing-along-the-music-of-twin-peaks?print) (not read ❓)
- Credits (album sleeve via Discogs): Excalibur Sound, New York

### What is documented
- **artist says** (Badalamenti, Believer): "I had her whisper the song" and it "made that song float". This is the technique.
- **engineer says** (Badalamenti on engineer, via summary ❓): Artie Polhemus (Excalibur Sound, owner) recorded, mixed and edited the album; the room was "nothing pristine".
- Lynch took part in writing, recording, mixing and doubling Cruise's voice on "Mysteries of Love" (Gavin Report 1990, via summary ❓).
- Heavy digital reverb on her voice (reviewers' description). The 1980s unit is not named in any source I read.
- Mic, preamp, compressor, reverb model, delay times: **not found.**

### Plug-ins / presets named
None. 🎃 Era guess: 1989 NYC studio = digital reverbs of that time (Lexicon, AMS); not documented, not to be quoted as fact.

### Mapping (all 🎃)

| Step | Owned |
|---|---|
| Close, breathy whisper delivery | SM7B or TLM 103 close, pop filter, low level; De-plosive in RX 11 |
| Soft comp | UADx LA-2A Silver or Fairchild 660, 2-4 dB |
| EQ | Pro-Q 3, HP 80 Hz, gentle boost 8-10 kHz for air |
| Doubling (Lynch doubling track) | Record the part twice; or Waves Doubler / AIR Tape Double Track |
| 80s digital hall | UADx Lexicon 224 (long hall); ❓UAD-2 AMS RMX16 or Lexicon 480L as alternates |
| Plate + tail | UADx EMT 250, Pure Plate, or Valhalla Plate |
| Slow chorus on the tail | UADx Brigade Chorus or Studio D Chorus |

### Proposed rack: "Cruise, floating"
Inserts: Utility > UADx LA-2A Silver (3 dB) > Pro-Q 3 > RX 11 De-plosive / Breath Control > Waves Doubler (very subtle).
Sends rack:
1. Dry, 0 dB, kept quiet and whispered.
2. 224 hall: UADx Lexicon 224, large hall, decay 4-5 s, pre-delay 30 ms. Start -8 dB.
3. Plate shimmer: ValhallaPlate decay 3 s > Brigade Chorus (slow, wide). Start -14 dB.
4. Slap: EchoBoy, single slapback 110 ms, no feedback, filtered dark. Start -20 dB.

Source quality: **partly** (whisper technique and studio are documented; the gear is not).

### Open ❓
- Which reverb unit Polhemus used on *Floating into the Night*.
- Uncut and Film Comment pages could hold more; both not read.
- "Early sessions were hard until she heard her voice with effects" appeared only in a search summary; not confirmed ❓.

---

## 6. Jeremy Enigk (Sunny Day Real Estate)

### Sources
- [Tape Op #14: Jeremy Enigk](https://tapeop.com/interviews/14/jeremy-enigk) (partial, paywalled after the opening)
- [Life of the Record: Making of *Diary* (notes)](https://lifeoftherecord.com/sunny-day-real-estate-notes)
- [Talkhouse: Making of *Diary*](https://talkhouse.com/the-making-of-diary-by-sunny-day-real-estate-feat-jeremy-enigk-dan-hoerner-and-william-goldsmith)
- [Tiny Mix Tapes: Jeremy Enigk](https://tinymixtapes.com/features/jeremy-enigk) (voice injury; not gear)

### What is documented
- *Diary* (1994): producer, engineer, mixer Brad Wood at Idful, Chicago; recorded in about six days, little overdubbing (Hoerner, via summary ❓). Credits.
- **artist says** (Enigk, Life of the Record): on "Grendel", Wood recorded many vocal melodies, took the best parts and put a "crazy effect" on them. Effect unnamed.
- **artist says**: Wood stopped the music and told stories for an hour to get the performance. (Technique: producer as coach.)
- Enigk's voice was strained at the time (screaming, high range); he said he lost his voice before *Diary* (Tiny Mix Tapes, via summary ❓).
- Solo era *Return of the Frog Queen* (1996), **artist says** (Tape Op #14): sang into a **Realistic PZM** boundary mic mounted on a wall; engineer Greg Williamson "pushes it right before it distorts". Placement changes tone without EQ: on wood adds lows, hand-held adds highs.
- Same interview: probably a Neumann U 47 on *How It Feels to Be Something On* (he is unsure ❓). He says he does not like compressors, leaves them to the producer.
- *Diary* mic, preamp, compressor, reverb: **not found.**

### Plug-ins / presets named
None. Realistic PZM (Radio Shack boundary mic) is the one named mic (solo era only).

### Mapping

| Step | Owned |
|---|---|
| PZM wall mic (solo era) | Boundary effect 🎃: SM7B/TLM 103 placed close to a wall or hard board; EQ Eight small shelf to taste |
| "Push the level to the edge of distortion" | UADx Neve 1073 driven, or Saturn 2 / Saturator on a very low drive |
| U 47 (later) | TLM 103 + UADx Ocean Way / Hemisphere ❓UAD-2 mic model 🎃 |
| Compression (he leaves it to producer) | UADx 1176 Rev A or Distressor, 3-4 dB 🎃 |
| Stacked best takes + "crazy effect" (Grendel) | Comp 3-4 takes; effect = Roar or Crystallizer or Decimort on a parallel lane |
| Raw 90s drum-room feel | Hybrid Reverb with a room IR, small mix |

### Proposed rack: "Enigk, raw lead"
Inserts: Utility > UADx Neve 1073 (drive up) > UADx 1176 Rev A (4 dB) > Pro-Q 3 (mild presence +2 dB at 3 kHz) > RX 11 De-ess.
Sends rack:
1. Dry, 0 dB (this style keeps the voice upfront).
2. Room: Hybrid Reverb or ValhallaRoom `Den/BalladVocal1`, decay 1.5 s. Start -14 dB.
3. Stack/FX lane: Crystallizer or Roar, wet only, EQ'd with Pro-Q 3 HP 300 Hz. Start -18 dB (the "Grendel" effect idea, 🎃).
4. Echo: Waves H-Delay or EchoBoy 1/4, feedback 25%. Start -20 dB.

Source quality: **partly** (solo-era mic documented; *Diary* chain not).

### Open ❓
- The rest of Tape Op #14 (paywalled) may name more gear.
- Brad Wood's own Tape Op interview for Idful gear: not read.
- What was the "crazy effect" on "Grendel"?

---

## 7. Cross-singer notes

- These styles share one pattern: **mostly dry-ish record, big wet sends, vocals tucked.** The rack idea in all six = inserts light, Sends rack heavy.
- Common send lanes for every rack: Hall (VintageVerb), Plate (ValhallaPlate), Echo (EchoBoy/Valhalla Delay), Dirty/Shimmer lane. Only levels and decay change per singer.
- The best "real" documented tricks to copy: record in a big room (Legrand), whisper delivery (Cruise), mic placement against a wall (Enigk), tuck the vocal in the mix and add reverb at the mix stage (Slowdive).
- Ask the manager before building: which one to turn into the first rack. Suggest Legrand or Cruise, because both have at least one documented hook.

## 8. Open ❓ (all singers)

- Sound On Sound has no vocal-chain article for any of these six. Checked via search only; a site-search on soundonsound.com is not done ❓.
- Blocked pages (403): Reverb.com Slowdive, Uncut, Gearspace *Devotion*. Re-check by hand in a browser if the quotes matter.
- Paywalled: Tape Op 168 (Coady) and Tape Op #14 (rest of Enigk).
- Mix and Tape Op interviews with Coady about Beach House vocals: not found.
- DIIV, Cigarettes After Sex, Slowdive 2017: no engineer interview naming a vocal mic or chain found.
- Little AlterBoy and Vocal Doubler are in the owned lists, but I did not check which formats are loadable in Live.
- UAD-2 items (AMS RMX16, Lexicon 480L, RE-201, H910) need the Apollo. Marked ❓UAD-2.
