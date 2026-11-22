# Half the Night EP: SoundCloud + Bandcamp upload pack (2026-11-10)

Amir uploads; the files are over Claude's 10 MB browser upload limit, and the Bandcamp AUP bans automation. Everything below is ready to paste.
Approved text = the description Amir approved on 11-10. Anything marked ❓ needs his OK.

## Files (both platforms)

| What | File |
|---|---|
| Track 1 audio | `~/Desktop/Inch of Shadow/Inch of Shadow - Half the Night (Indigo Children Records).wav` (24-bit / 44.1k) |
| Track 2 audio | `~/Desktop/Inch of Shadow/Inch of Shadow - Pinocchio (Indigo Children Records).wav` |
| Cover | `Releases/Half the Night EP/Artwork & Designs/Platform sizes/Spotify_AppleMusic_Bandcamp_Beatport_3000x3000_Release_Half the Night EP.jpg` |
| SoundCloud header (picked 11-10) | `Releases/Half the Night EP/Artwork & Designs/Platform sizes/Banners/` (one of A, B, D, E) |

ISRCs (from the Symphonic draft, use the same everywhere): Half the Night **QZWDE2693303**, Pinocchio **QZWDE2693308**.

## SoundCloud: upload PRIVATE now, public on Fri Dec 11 at 09:00 Berlin

- Upload both tracks, then make a **playlist, type EP**, title "Half the Night". Keep everything **Private** until Dec 11. The private links feed the DJ promo (Nov 20-25) and the label exceptions.
- Per track:
  - Title: `Half the Night` / `Pinocchio`
  - Main artist: Inch of Shadow
  - Genre: **Dark Disco**
  - Tags: `electro` `dark disco` `acid` `EBM` `italo disco` `Berlin` `Indigo Children Records` `127 bpm` (Pinocchio: `126 bpm`)
  - Description (approved text, then links):
    > Half the Night is a restless 303 acid line over electro drums and a bass that never lets go, falling deeper into a dark, rolling trance arp. Pinocchio twists its 303 leads through a minimal groove full of echo and smoke. Hypnotic dark disco for the lost hours, from Berlin.
    >
    > Indigo Children Records · ICR-003
    > Bandcamp: [link with ?campaign=sc-desc, once the Bandcamp page exists]
  - Metadata tab: record label Indigo Children Records, ISRC (above), release date 2026-12-11 (set only when public), P-line 2026 Indigo Children Records, composer Amir Miller.
  - Buy link: the Bandcamp release URL with `?campaign=sc-buy` (`python3 bandcamp_links.py <url> --channel sc-buy`).
  - ✅ Downloads ON for the private link (Amir 11-10), so DJs can grab the WAVs. Whether it stays on when public on Dec 11 is still open.
- Dec 11, 09:00: flip public, pin the EP, then Amplify in the mobile app (one shot, tracks only).

## Bandcamp: pre-order live by Nov 16, release Fri Dec 11 (moved from Dec 4, Amir 11-11)

- Album:
  - Title "Half the Night", artist Inch of Shadow
  - Release date 2026-12-11
  - Label: Indigo Children Records
  - Catalog ICR-003
  - UPC: the Symphonic one once it's assigned (optional on Bandcamp)
- About (approved text):
  > Half the Night is a restless 303 acid line over electro drums and a bass that never lets go, falling deeper into a dark, rolling trance arp. Pinocchio twists its 303 leads through a minimal groove full of echo and smoke. Hypnotic dark disco for the lost hours, from Berlin.
- Credits: "Written and produced by Amir Miller. Mixed and mastered by Amir Miller at Ambertone Studios, Berlin. Cover art: Inch of Shadow." ✅ Amir 11-10: credits = Amir Miller.
- Tags: `darkwave` `dark disco` `acid` `electro` `ebm` `italo disco` `berlin` (set 11-03; darkwave first = the bridge to the songs)
- Price (BC-09): EP **EUR 4**, tracks EUR 1.50, "let fans pay more" ON.
- Pre-order:
  - pre-order date = upload day, release 2026-12-11
  - ✅ instant-grant track = Half the Night (Amir 11-10); pre-order set in the draft, Amir clicks Publish
  - tick "notify followers" (The Deceiver notified 44)
- ISRCs per track (above).
- Track lyrics: none (instrumental).
- Same day: schedule the Listening Party for Dec 11, 19:00 Berlin (plan: `plans/bc06-nov6-half-the-night.md`), and Claude runs `python3 bandcamp_links.py --write` for the campaign links.
- 🎬 Socials 17 (discography bundle) can switch on with the pre-order. It notifies all followers, so it's Amir's call.

## Order

1. Bandcamp page + pre-order (needs only audio, cover and text, nothing from Symphonic).
2. SoundCloud private upload, with the Bandcamp buy link and description links from step 1.
3. Claude: campaign links + release file updated with both URLs.

## Bandcamp pre-order note to followers (DRAFT 2026-11-10, needs Amir's OK in the main EP chat)

> Hi all,
>
> My new EP Half the Night is up for pre-order: two tracks, Half the Night and Pinocchio, out Friday December 11 on Indigo Children Records. Pre-order now and Half the Night is yours right away.
>
> Hope you will like it,
> Amir

## Tag "acid disco" (Amir 11-11: "Yes, if it exists")

Checked on 11-11 in Chrome:
- Bandcamp: exists. bandcamp.com/discover/acid-disco shows 24 real releases (e.g. Cobra303, DECIUS, SEMID label), and the tag field suggests "acid disco".
- SoundCloud: exists. soundcloud.com/tags/acid disco shows active tracks (newest about 12 days old).
- Added on Bandcamp to the album and both tracks; Bandcamp saved the order as electro, darkwave, acid disco, acid, berlin, dark disco, ebm, italo disco. Draft saved, still not published.
- Added on SoundCloud to both tracks and the playlist. Checked on the pages after saving.
- BPM tags on SoundCloud stay (Amir 11-11: BPM is fine where it helps SEO; the musical key never goes anywhere).

## Bandcamp profile genres (Amir 11-15: "y")

RECORDED BEFORE THE CHANGE, 2026-11-15, as read on the live HTN album page (artist-level genre tags):
- acid, dark disco, ebm, electro, electronic, techno
- HTN release tags at that time: acid, acid disco, berlin, dark disco, darkwave, ebm, electro, italo disco (location tag Berlin)
Change asked: profile techno -> darkwave; add release tag "techno" to Meltscape EP + its tracks only.
- Exact profile fields before (bandcamp.com/profile, 2026-11-15): Genre select = band.genre_id 10 (electronic, unchanged); "Genre tag(s)" = `Electro, Acid, Dark Disco, Techno, EBM`.
- Meltscape EP before (edit_album?id=22720250, 2026-11-15): album tags `techno, underground, acid, berlin, dancefloor, acid techno, ebm, trance, hypnotic` (techno ALREADY there, not changed). Tracks: The Cure `Acid, Trance, Acid Techno, Rave`; Meltscape `Trance, Underground, Acid Techno, Hypnotic`; Mind Eaten `Trance, Berlin, Acid Techno, Analog`.
- AFTER (2026-11-15, checked on the live pages):
  - Profile "Genre tag(s)": `Electro, Acid, Dark Disco, Darkwave, EBM` (Genre select still Electronic, nothing else touched).
  - HTN album page artist tags: acid, dark disco, darkwave, ebm, electro, electronic. No techno.
  - Meltscape tracks: The Cure `Acid, Trance, Techno, Acid Techno, Rave`; Meltscape `Trance, Underground, Techno, Acid Techno, Hypnotic`; Mind Eaten `Trance, Berlin, Techno, Acid Techno, Analog`. Album tags unchanged (already had techno). The Meltscape and The Cure pages show "techno".

## SoundCloud tag swap: italo disco -> indie dance (Amir 11-17, via the EP chat)

Done 2026-11-17 on the 3 private uploads; only that one tag changed, live tag_list checked after each save.

| Item | Before | After |
|---|---|---|
| Half the Night (track) | electro, dark disco, acid, EBM, italo disco, Berlin, 127 bpm, acid disco | electro, dark disco, acid, EBM, Berlin, 127 bpm, acid disco, indie dance |
| Pinocchio (track) | electro, dark disco, acid, EBM, italo disco, Berlin, 126 bpm, acid disco | electro, dark disco, acid, EBM, Berlin, 126 bpm, acid disco, indie dance |
| Half the Night (EP set) | electro, dark disco, acid, EBM, italo disco, Berlin, acid disco | electro, dark disco, acid, EBM, Berlin, acid disco, indie dance |

Bandcamp tags unchanged.

## Bandcamp credit: Ambertone Studio -> Ambertone Studios (Amir 11-21 "Yes, change both", via the EP chat)

Done 2026-11-21, only "Studio," -> "Studios," changed; curl check after: HTN 3x Studios / 0 old, The Deceiver 6x Studios / 0 old.
- Half the Night album credits, before: "Written and produced by Amir Miller. Mixed and mastered by Amir Miller at Ambertone Studio, Berlin."
- The Deceiver track credits, before: "Written and produced by Amir Miller. / Mixed and mastered at Ambertone Studio, Berlin. / ℗ 2026 Indigo Children Records"
- The Deceiver track about, before (last line): "Mixed and mastered at Ambertone Studio, Berlin, 2026. The second half of the Farewell pair."
