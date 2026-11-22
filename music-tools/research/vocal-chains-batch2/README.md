# Vocal chains batch 2 (27 singers, 2026-11-15)

Picks: Amir's tick page https://claude.ai/artifact/KNS6mZULRLqUxDJ4waVPYc (db `picks`).
Research: 5 Sonnet agents, text only, nothing downloaded. Detail per singer in the 5 group files here.
Rule applied: a new rack only if the chain is clearly different from the existing racks (memory: racks-only-if-distinct).

## Source quality

| Singer | Quality | Key documented fact |
|---|---|---|
| Maynard / Tool | documented | Barresi: clean mic + heavily distorted SM57 at once, distorted path via Helios; tape-speed octave takes |
| Maynard / A Perfect Circle | partly | live FOH only: dynamic EQ, "doesn't like compression" |
| Maynard / Puscifer | unverified | engineer named only |
| Billy Corgan | partly | Siamese Dream: SM7 > API pre > TLA-100 limiter; Mellon Collie: SM58 with speakers |
| Steven Wilson | documented | U87 > Apogee soft limiter, no comp; megaphone = D2 EQ band-pass ~2 kHz; Space Echo slap |
| Andrew Eldritch | unverified | nothing on the vocal chain |
| Ian McCulloch | unverified | producer named only |
| Liz Fraser | partly | Guthrie 1987: U87, light 3-4:1 comp, de-ess, 1 kHz cut, quiet delays, sparing room reverb |
| Gary Numan | partly | late era: dry, "in the room" |
| Grian Chatten | unverified | live in one room |
| Faris Badwan | partly | Neumann CMV3 bottle mic; demo takes kept |
| Boy Harsher | unverified (studio) | live: delay pedal into chorus pedal |
| Lebanon Hanover | unverified | taste only: warm, no sharp highs, raw take |
| Fever Ray / The Knife | partly | pitch and formant shifting, doubled at different pitches |
| Grimes | partly | Ableton, Manny Marroquin reverbs, Nectar (not owned) |
| Charli XCX | partly (Crash era) | 1176 hit hard > EQ > Pro-Q 3; H3000 widener, ping-pong, Valhalla; Auto-Tune in headphones |
| Victoria Legrand | partly | big live room, no baffles; effects kept secret |
| Slowdive | unverified | vocals buried, reverb |
| DIIV | unverified | drowned in reverb |
| Greg Gonzalez | unverified | live, high reverb, whisper backing vocals |
| Julee Cruise | partly | whispered vocal, heavy digital reverb |
| Jeremy Enigk | partly | PZM mic on a wall, level pushed to near distortion, no compressor |
| Playboi Carti | unverified | one-take performances; recreations only |
| Don Toliver | partly, thin | CL 1B, 1176LN, Lexicon 224 (live); uses the room |
| XXXTentacion | partly | lead delay ~10% feedback; earbud-mic and bedroom takes |
| Thom Yorke | partly | Kid A: vocoder lead; reader Q&A: bright, heavy comp, dull reverb |
| Bon Iver | documented | SOS: Auto-Tune > Auto-Tune (tonic) > H8000 MIDI harmony, blended; SM7, ~40 takes |

## Grouping against the existing racks (proposal, not built)

New racks (clearly different):
1. **Bon Iver** (Prismizer harmony stack). Documented. Quadravox as H8000 stand-in ❓.
2. **Tool** (clean + distorted parallel mic, octave layers). Documented. Covers APC/Puscifer as variations.
3. **Megaphone / Lo-fi** (band-pass megaphone, soft limiter, slap; earbud/PZM rawness). Steven Wilson documented; XXXTentacion, Enigk as variations.
4. **Pitch Layers** (formant-down double for Fever Ray, high octave/baby voice for Carti, two chains). Partly.
5. **Vocoder** (Thom Yorke Kid A, Live Vocoder + dull reverb). Partly.
6. **Dream Wash** (whisper, buried, huge wet reverb). One shared rack for Beach House, Slowdive, DIIV, Cigarettes After Sex, Julee Cruise. Mostly unverified.

Variations only (no new rack):
- Liz Fraser -> Lana Del Rey / Robert Smith
- Charli XCX, Grimes, Don Toliver -> The Weeknd
- Billy Corgan -> Deftones
- Eldritch, McCulloch, Numan, Chatten, Badwan -> Nick Cave / Robert Smith
- Boy Harsher, Lebanon Hanover -> Robert Smith

## Final build spec (Amir OK 11-15; no Live stock devices; Fever Ray dropped, overlaps the Auto Shift rack)

All: Pro-Q 3 on Zero Latency. Sends rack after the inserts: Dry 0 dB + effect chains, every effect 100% wet. Levels are Claude's starting points.

1. **FX - Vocal Tool**: Pro-Q 3 > UADx Neve 1073 > UADx 1176 Rev A > Waves DeEsser. Sends: Dirt (UADx Helios 69 > Decapitator E, mix 100 > Pro-Q 3 band-pass) -12 | Octave Down (Little AlterBoy -12) -14 | Octave Up (Little AlterBoy +12) -18 | Delay (EchoBoy) -14 | Space (ValhallaVintageVerb) -16.
2. **FX - Vocal Steven Wilson**: Pro-Q 3 > UADx Neve 1073 > UADx 1176LN > Waves DeEsser. Sends: Slap (UADx Galaxy, wet solo) -12 | Megaphone (Pro-Q 3 band-pass ~2 kHz > Decapitator light > Retro Fi) -10 | Tape Delay (EchoBoy) -16 | Room (ValhallaRoom) -22.
3. **FX - Vocal Bon Iver**: Auto-Tune Artist > Pro-Q 3 > Pro-MB > UADx LA-2A Silver > Pro-L 2. Sends: Messina (Auto-Tune Artist retune 0 > Waves Harmony, MIDI-played) -8 | Fixed Harmony (Quadravox "02 - C Maj +3 +5", key per song) -10 | Choir (Little AlterBoy > MicroShift) -12 | Chamber (ValhallaRoom) -14.
4. **FX - Vocal Thom Yorke**: UADx 1176 Rev A > UADx Pultec EQP-1A > UADx LA-2A Gray > Waves DeEsser. Sends: Dull Verb (ValhallaRoom, high cut ~2.5 kHz) -12 | Vocoder (Waves OVox) -10 | Granular (Output Portal) -16 | Reverse (Crystallizer "06 Echo Reverse") -16.
5. **FX - Vocal Dream Wash**: UADx LA-2A Silver > Pro-Q 3 > Soothe2. Sends: Hall (ValhallaVintageVerb) -10 | 224 (UADx Lexicon 224) -12 | Plate Shimmer (ValhallaPlate > UADx Brigade Chorus) -14 | Tape Echo (UADx Galaxy) -18.
