# Half the Night EP: where the description shows + what serves SEO (2026-11-12)

🎵 Release 17. Builds on `htn-description-map-2026-11-10.md` (first start) and `htn-seo-pass-2026-11-11.md` (SC + Bandcamp fields, not redone here).
Nothing changed live. Research = text only (`fetch_text.py`, WebFetch, plain `curl` of our own public pages, no Chrome).
Labels: [OFFICIAL] platform help/spec page · [OWN DATA] our files or our own live pages · [HYPOTHESIS] my read, not proven · [CHECK] look once on the live form/page.
✍️ = a draft in Amir's voice/name. Drafts only; each needs his OK in the main EP chat (hard rule 13).

Approved description (Amir 11-10), used word for word below wherever it appears:
> Half the Night is a restless 303 acid line over electro drums and a bass that never lets go, falling deeper into a dark, rolling trance arp. Pinocchio twists its 303 leads through a minimal groove full of echo and smoke. Hypnotic dark disco for the lost hours, from Berlin.

## New facts found today

- **Bandcamp builds the Google meta description from the page itself** [OWN DATA, our live pages read 11-12]:
  - Album page (Eastern Stars): `<Title> by <Artist>, released <date>` + numbered tracklist + the **full About text**.
  - Track page (The Deceiver): only `The Deceiver by Inch of Shadow, released 10 July 2026`. The track About is on the page but **not** in the meta description.
  - So on the HTN album page, Google's ~155-char snippet is mostly Bandcamp's own line + "1. Half the Night 2. Pinocchio", and only the **first ~50-60 chars of the About** fit after it. Bandcamp already writes the title, artist and date, so the About's first words don't need to repeat them.
- **YouTube Art Tracks have no free-text description** [OFFICIAL, [YouTube Art Track spec](https://support.google.com/youtube/answer/3504912)]: the description is built from delivered fields (copyright, release date, contributors). Channel owners can't edit it [third-party distributor pages, e.g. [AWAL](https://help.awal.com/hc/en-us/articles/7877380493843-YouTube-Topic-Channel-and-Art-Track-Overview)]. It starts "Provided to YouTube by <distributor>" [third-party example, exact wording HYPOTHESIS].
- **Spotify pitch** [OFFICIAL, [Spotify: pitching](https://support.spotify.com/us/artists/article/pitching-music-to-playlist-editors/)]: seen only by the S4A team and editors; pitch 7+ days before release for Release Radar; edits up to release day may not be seen. The 500-char limit is not on that page (third-party guides + our spec file).
- **Apple Music album notes** = the `editorialNotes` field in Apple's API ([Apple docs](https://developer.apple.com/documentation/applemusicapi/editorialnotes)). Who writes them is not documented; no artist or Symphonic Starter field feeds it [HYPOTHESIS].
- **Symphonic**: its public metadata guide lists no release description field ([metadata guide](https://blog.symphonic.com/2023/04/18/how-to-input-your-metadata-in-the-sms/)). The help desk returns 403 to text readers. Whether the HTN form had a description box, and whether the approved text went in, isn't written down anywhere in our files. [CHECK: Symphonic draft 3697587 overview, uploads/Symphonic chat]
- **Side find, credits spelling**: `docs/brand/proof.md` and the YouTube playbook say "Ambertone **Studios**"; the HTN upload pack says "Ambertone **Studio**, Berlin". Memory: @ambertone.studios. Fixed in the drafts below to "Studios"; the Bandcamp credits line in the pack is Amir's call.

## The map (one table)

| Place | Description shown? | Where on the page | Chars before cut | Indexed by | SEO value (advanced) | Write-once? | Draft |
|---|---|---|---|---|---|---|---|
| **Bandcamp album (pre-order from ~Nov 16)** | ✅ yes, full About | under the player + tracklist, above credits; tags below | page: no cut. Google snippet: ~50-60 chars of About after Bandcamp's own line + tracklist [OWN DATA] | Google ✅ (album meta description = full About [OWN DATA]); Bandcamp search ❌ for About text, it matches names + tags [HYPOTHESIS, Rovics post + 10-21 research] | **Highest public text value.** Google = 46 of 595 BC visits, BC search 13 [OWN DATA]. Live ~4 weeks before SC. Only the first About sentence reaches the snippet; the rest is on-page relevance (acid, electro, dark disco, Berlin, label). Tags do the in-platform work. | editable any time | ✍️ D1 |
| **Bandcamp track pages** | ✅ yes | under the player | no cut | Google: page text yes, meta description = Bandcamp's line only [OWN DATA] | Low. Thin pages, but their own Google URL + tag source. One EP line is enough. | editable | ✍️ in SEO pass 11-11 (unchanged) |
| **SoundCloud tracks + EP playlist** | ✅ yes | under the waveform/artist bar, collapsed after a few lines ("Show more") [HYPOTHESIS, SC help 403] | field 4000 [spec file, third-party]; visible ~2-3 lines before "Show more" [HYPOTHESIS] | SC search reads title + tags + genre [OFFICIAL, SC help via 11-11 pass]; description in SC search = not documented [HYPOTHESIS]; Google sees the page title built from title + username [OWN DATA 11-11] | Medium. Google title = title + "Inch Of Shadow" (capital O, 11-11). Description = links + context; related tracks run on audio + social graph, not text [HYPOTHESIS]. Public only from Dec 11. | editable | uses approved text + ✍️ first line from SEO pass (unchanged) |
| **YouTube Art Track (Topic, via Symphonic)** | auto text only | under the video | n/a | YouTube + Google, but text is metadata only | None to write. Value comes from clean metadata: title, artist, ISRC, label, P-line. | ❌ not editable [third-party distributor docs] | none |
| **YouTube own upload (Official Audio, our channel)** | ✅ yes | under the video | ~100 mobile / ~150-200 desktop before "Show more"; search results ~140-160 [spec file] | YouTube search ✅ (title + description) and Google video results ✅ [OFFICIAL via playbook §5.4] | Medium-high long tail: the only YouTube text we control. First ~150 chars = track, artist, EP, label. Tags ≈ nothing [OFFICIAL, quoted in playbook]. | editable (yt_apply.py) | ✍️ D2 (both tracks) |
| **Spotify release page** | ❌ no release description field | n/a | n/a | n/a | None. Discovery = pitch tags + listening signals. | n/a | none |
| **Spotify pitch (S4A)** | editors only, never public | S4A form | 500 [third-party + spec file] | not indexed | **High, but internal**: genre, mood, style tags route the pitch at least as much as the text [spec file]. One song per release is pitched. | edits up to release day may not be seen [OFFICIAL] → write-once in practice | ✍️ D3 (input for the 🎵 "HTN Spotify pitch" ticket) |
| **Spotify bio / Artist Pick** | bio = artist level, not release; Artist Pick message shows on the profile | profile top (Pick), About tab (bio) | Pick message 140; bio 1500 [spec file] | Pick/bio not in Spotify's Google snippet [HYPOTHESIS] | Pick: no ranking value, steers profile visitors to the EP [spec file]. Bio is out of scope (positioning rules, songs switch). | editable | ✍️ D4 (Pick message only) |
| **Apple Music** | ❌ no artist-supplied release text; album notes = Apple editorial | n/a | n/a | Google indexes the album page title ("Half the Night - EP by Inch of Shadow") [HYPOTHESIS for the suffix] | None from text. Clean metadata + Shazam + library adds. No Starter pitching. | n/a | none |
| **Beatport (via Symphonic, Starter add-on)** | ❓ only if the Symphonic form had a description field and it went in; public display on Beatport release pages unconfirmed (pages return 403 to text readers) | ❓ | ❓ | Beatport search = artist/title/label/genre [HYPOTHESIS] | ~None. Beatport = sales-velocity charts per genre [spec file]. Genre pick is the real lever and is already delivered. | ✅ **write-once**: edits after delivery don't reach Beatport [OWN DATA, Symphonic chat 11-11] | none (already delivered as submitted) [CHECK what went in] |
| **Deezer / Tidal / Amazon Music / other Symphonic DSPs** | ❌ no artist release text on their pages [HYPOTHESIS] | n/a | n/a | n/a | None. | n/a | none |
| **Smart link / pre-save page** (the one now possible with the UPC) | depends on the tool; most show title + artist + cover, some a short line | landing page | tool-specific | Google: these pages usually rank weakly and duplicate the stores [HYPOTHESIS] | Low. Use the EP line from D4 if the tool asks. | editable | reuse D4 |
| **Discogs (optional, not set up)** | release "Notes" field, public | release page | no cut | Google ✅, Discogs ranks well for release + catalogue number searches [HYPOTHESIS] | Low-medium for "ICR-003" / label searches. Factual only (credits, catalogue no.). Only if Amir wants a Discogs entry; nobody asked. | community-edited | none (offer only) |

## Drafts (✍️ his voice, files only, all need his OK in the main EP chat)

Rules checked on every draft: no key, no BPM, no em-dashes, "Inch of Shadow" in full, date = Friday 11 December 2026, no feedback ask, no meta line, approved text word for word.

### ✍️ D1. Bandcamp album About (pre-order phase, from ~Nov 16)

The SEO pass (11-11) already drafted option A. New today: Bandcamp's snippet already starts with "Half the Night by Inch of Shadow, released 11 December 2026" + the tracklist, so option B skips the repeat and puts the label + pre-order first.

- **A (from the SEO pass, unchanged):**
  > Half the Night EP, out 11 December 2026 on Indigo Children Records (ICR-003). Pre-order now and Half the Night is yours right away.
  >
  > Half the Night is a restless 303 acid line over electro drums and a bass that never lets go, falling deeper into a dark, rolling trance arp. Pinocchio twists its 303 leads through a minimal groove full of echo and smoke. Hypnotic dark disco for the lost hours, from Berlin.
- **B (new, shorter first line, my pick):**
  > Indigo Children Records, ICR-003. Pre-order now and Half the Night is yours right away.
  >
  > Half the Night is a restless 303 acid line over electro drums and a bass that never lets go, falling deeper into a dark, rolling trance arp. Pinocchio twists its 303 leads through a minimal groove full of echo and smoke. Hypnotic dark disco for the lost hours, from Berlin.
- On Dec 11: drop the pre-order sentence; keep "Indigo Children Records, ICR-003." or remove the line.

### ✍️ D2. YouTube own upload, Official Audio (only if we upload the tracks to our channel; yt_apply.py)

First ~150 chars hold track, artist, EP, label. Then the approved text, links, credits, 4 hashtags last. Lead link + Bandcamp `?campaign=yt-desc` (channel exists in `bandcamp_links.py`).

**Half the Night**
> Half the Night by Inch of Shadow, from the Half the Night EP on Indigo Children Records (ICR-003). Released Friday 11 December 2026.
>
> Half the Night is a restless 303 acid line over electro drums and a bass that never lets go, falling deeper into a dark, rolling trance arp. Pinocchio twists its 303 leads through a minimal groove full of echo and smoke. Hypnotic dark disco for the lost hours, from Berlin.
>
> Listen: [smart link]
> Bandcamp: [Bandcamp URL ?campaign=yt-desc]
>
> Written and produced by Inch of Shadow. Mixed and mastered by Inch of Shadow at Ambertone Studios, Berlin.
>
> Instagram: instagram.com/inch_of_shadow
> SoundCloud: soundcloud.com/inch-of-shadow
>
> #InchofShadow #darkdisco #acid #electro

**Pinocchio**: same text, first line:
> Pinocchio by Inch of Shadow, from the Half the Night EP on Indigo Children Records (ICR-003). Released Friday 11 December 2026.

### ✍️ D3. Spotify pitch, 493/500 chars (pitched song: Half the Night; input for the 🎵 "HTN Spotify pitch + Canvas + header" ticket, which owns the send)

> Half the Night is the title track of my new EP on Indigo Children Records, from Berlin. A restless 303 acid line runs over electro drums and a bass that never lets go, then falls into a dark, rolling trance arp. Hypnotic dark disco for the lost hours. The second track, Pinocchio, twists its 303 leads through a minimal groove full of echo and smoke. Around release day: a Bandcamp listening party on Dec 11, both tracks on SoundCloud, reels on Instagram and a promo to dark disco and EBM DJs.

- Reuses the approved wording, lightly reshaped to fit a single-song pitch (not word for word, because the pitch isn't in use yet). The plan items at the end come from the upload pack (listening party Dec 11), the content plan and the DJ promo handover. [CHECK they all still hold on pitch day]
- Tags (from the release file, read the real dropdown on pitch day): genre Electronic / Dark Disco, moods from `platform_tags.spotify.moods`, instrumental. Never trance/house/techno as a tag.

### ✍️ D4. Spotify Artist Pick message (69/140), reused for a smart link line

> Half the Night EP, out Friday 11 December on Indigo Children Records.

From Dec 11 the same Pick message can drop "out Friday 11 December": `Half the Night EP on Indigo Children Records.`

### No draft (no field, or nothing worth it)
- YouTube Art Track, Apple Music, Spotify release page, Deezer/Tidal/Amazon: no artist text field.
- Beatport: already delivered; edits don't reach it.
- SoundCloud + Bandcamp track lines: already drafted in `htn-seo-pass-2026-11-11.md`, unchanged.

## Open checks ([CHECK], one look each, uploads/Symphonic chat)
1. Symphonic draft 3697587: was there a description box, and what went in? (Beatport is write-once.)
2. Bandcamp pre-order page meta description once published: does it say "releases" + include the About? (expected yes, as on album pages)
3. Credits spelling "Ambertone Studio" vs "Studios" in the Bandcamp credits line (Amir's call).

## 🐞 Mistakes / 📚 lessons (for the chat delete)
- 🐞 My zsh `echo =====` separators failed (zsh reads `=word` as a path lookup); use `echo '---'`.
- 🐞 The brief listed `htn-seo-pass` as "SC + Bandcamp SEO done", so I almost redrafted Bandcamp lines; kept them unchanged and only added option B.
- 📚 Read our own live pages' `<meta name="description">` with plain curl before guessing what Google sees: Bandcamp album vs track pages differ, and that changed the D1 advice.
- 📚 Symphonic help, SC help and Beatport pages return 403 to text readers; don't spend more calls there, mark [CHECK] and move on.
- 📚 Before drafting for a place, check whether another ticket owns it (Spotify pitch belongs to the "HTN Spotify pitch" ticket), and label the draft as input for that ticket.
