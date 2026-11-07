# Playlist Curator Research - Context Handoff (Inch of Shadow)

Self-contained context for continuing the Spotify playlist-curator work in a new conversation.
Scope: PLAYLIST targeting only. Date: 2026-06-09.

## Goal
Build a real curator-playlist pitch list for Inch of Shadow. Farewell got thin playlist
results; improve it for The Deceiver (release 2026-07-10, dark EBM/electro, 122 BPM) and
pitch Farewell (already live) alongside it.

## Work method (how we find playlists)
1. Pick a same-lane reference artist slightly bigger than IoS. First one: **Alen Skanner**
   (~4,315 monthly listeners, dark / "trancy" EBM / dark disco). Spotify artist id
   `34DjyfohleZ08Z2W0jB0yC`, SC `soundcloud.com/alenskanner`.
2. Open their Spotify artist page -> **"Discovered on"** = the playlists driving their
   streams = the target list.
3. Filter to IoS's exact sound (dark EBM / electro / darkwave / dark disco / industrial).
   Set aside divergent placements (Alen's italo/trance lists don't fit IoS's darker sound).
4. For each target: get the playlist URL -> WebFetch the description to extract contact
   (IG / email / submission link). No contact in description -> SubmitHub / Groover (paid
   ~$1-3 per submission) or DM the curator.
5. Expand: repeat with more reference artists. Playlists appearing across MULTIPLE same-lane
   artists = highest value.

## Recommendations
- At IoS's size, **independent curator playlists are the realistic lever, NOT Spotify
  editorial** (editorial is a moonshot - pitch via S4A anyway, do not bet on it).
- **Pitch BOTH** Farewell (live now) and The Deceiver (at release) to every curator.
- Next reference artists to mine (Alen's "fans also like"): **Silicodisco, Soft Crash,
  Karassimeon**, plus **Pablo Bozzi / Phase Fatale** (recurring).
- Flag **free vs paid** route per curator.

## Target playlists (from Alen Skanner's "Discovered on", my screenshots)

TOP fit (pitch first):
- Dark Discoteque (dark disco / dark italo / darkwave / new beat)
- Industrial | EBM | Darkwave | Dark Electro (curator DARKLARK)
- EBM / Electro Industrial / Dark ("music for body and mind")
- Dark Disco by Lust (dark dance + body music)

GOOD fit:
- Modern Darkwave
- Darkwave / Coldwave (curator Vioflesh)
- Industrial Goth Club
- Dark Synth Wave 2026
- Darkwave NOW!
- Electro Acid Breaks (acid / electro angle)

PARTIAL (B-list):
- Modern Italo Disco 2026, INDIE DANCE / DARK DISCO, BDSM (dark techno/electronica),
  Moog Barcelona Techno, The omen, Rotterdam

LABEL-only (not pitchable as a playlist; aspirational label target):
- BITE Records (Phase Fatale's label playlist)

SET ASIDE (off-lane for IoS - Alen's trancy/italo side, or DJ setlists):
- Italo Disco & Trance 2026, Italo-Trance by Kendal, Trance Edits, Italo Disco Dance
  Machine, Space Disco, Pablo Bozzi Boiler Room setlist, Pablo Bozzi x Boiler Room Khidi,
  K41 Pablo Bozzi/Phase Fatale, Parasol, Pain & Pleasure (fetish-themed), EXE Beach Bar,
  Bangers, Durx

## Contacts found so far
- **DARK DISCOTHEQUE 2026** - curator PilatusMusic (sven.twardon), 494 saves,
  IG **@pilatusmusic** (free DM). URL `open.spotify.com/playlist/6Hg8HcPaJ64jQbAwBj8P9O`.
- **DARKLARK - Industrial | EBM | Darkwave** - 22,271 saves (top target). No email in
  description; route via SubmitHub or Spotify/IG DM. URL
  `open.spotify.com/playlist/7JFbHdM6wXIJhb67N7f0Ct`. Also runs **"Berliner scene: EBM |
  Techno | Coldwave | Darkwave | Electro"** (`6ndaZWRs76O1g2sQrUCYpO`) - Berlin-specific,
  high fit, pitch both.

Note: "Dark Discoteque" in Alen's Discovered-on may differ from PilatusMusic's "DARK
DISCOTHEQUE 2026" - both in lane, confirm.

## Other notes
- Alen's "Appears On" (compilations/EPs, NOT playlists): Penultimate Truth, Unknown Prospect
  Vol 2, Manteca, Caustic Motion, NRG (Soft Crash), Neurovision, Ritmo Fatale Anthology,
  ROCOCO Remixes, Tomorrow Never Dies 001, Silicodisco & Bias, etc. -> useful for LABEL
  targeting later, not playlists.
- Reachable curator contacts are NOT web-searchable in bulk. Reliable routes: (a) playlist
  description in the Spotify app, (b) SubmitHub/Groover genre search (paid).

## Saved data
`scene_intelligence/playlist_curator_targets.json` - structured target list (name, curator,
fit, url, saves, submission route; URLs/contacts mostly TBD).

## Next steps
1. Copy Spotify URLs for the TOP/GOOD targets from the app -> batch WebFetch descriptions
   for contacts.
2. Screenshot "Discovered on" for Silicodisco + Soft Crash -> aggregate; cross-list winners.
3. Build the pitch sheet: per playlist = route (free DM / SubmitHub) + free/paid flag,
   pitching Farewell now + The Deceiver at release.
