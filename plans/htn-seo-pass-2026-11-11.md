# Half the Night EP: SEO pass for SoundCloud + Bandcamp (2026-11-11)

**Date update 11-11:** the release moved to Fri 2026-12-11 (Symphonic chat, Amir). All dates below say Dec 11. Bandcamp Friday (Dec 4) is no longer the release day.

✅ SoundCloud duplicate risk closed: SoundCloud is excluded from the Symphonic partners (Amir 11-11, confirmed on the draft overview by the Symphonic chat). The self-uploads stay the only SC copies.

Proposal only. Nothing was changed live (no Chrome, no SC/Bandcamp edits; the 🎵 HTN uploads chat owns those pages).
The approved description stays word for word. Every line marked ✍️ is a **draft in his voice/name, needs Amir's OK in the main EP chat**.
Labels: [OWN DATA] from our files · [OFFICIAL] platform help page · [HYPOTHESIS] my read, not proven · [CHECK] look on the live form.

The tag rules locked on 2026-11-03 still hold (`releases/pinocchio-single.json` → `platform_tags.tag_rules`): never techno / trance / house / dark electro / indie dance; "303", "rolling bass", "dark trance atmosphere" go in text only, never in tags. Nothing below breaks them.

## What the data says (short)

- **SC catalogue titles all use "Inch of Shadow - X"** (12 tracks in `stats_snapshots/snapshot_2026-11-09`). The HTN uploads are plain ("Half the Night", "Pinocchio"). [OWN DATA]
- **SC builds the Google title from title + username**: the live Farewell page reads "Stream Inch of Shadow - Farewell by Inch Of Shadow | Listen online for free on SoundCloud" (fetched 11-11). The artist prefix only repeats the name. A plain title gives "Stream Half the Night by Inch Of Shadow". [OWN DATA, live page]
- **Side find: SC shows the username as "Inch Of Shadow"** (capital O) in that title. That's a profile setting, outside this ticket, so it's only noted here. [CHECK]
- **SC genre field**: it's the first tag, shown on the waveform in Stream and Search. The preset list matches SC's Charts, and a custom genre is allowed. Tracks whose genre matches a genre search rank higher. SC says stacking similar genre tags does not boost search. Multi-word tags must stay whole. [NOT VERIFIED: cited from [Adding a genre and tags](https://help.soundcloud.com/hc/en-us/articles/115003446007) and [Edit and customize your tracks](https://help.soundcloud.com/hc/en-us/articles/46022345620123), but the help site answers 403 to text readers (11-11 and again 11-15), so none of this was re-read at the source. Fable gate 2026-11-15. It only supports "keep" decisions.]
- **SC related tracks / autoplay**: no SC source says tags drive it. Our June research puts audio analysis (Musiio) and the social graph (likes, reposts, Liked By) behind it (`plans/platform-algorithm-research-2026-06.md`, SoundCloud section). So tags = **search + tag pages**; related tracks = **audio + who plays/likes it**. [HYPOTHESIS for the split, no official statement either way]
- **SC tag limit**: the help pages fetched today give no number. The "30" in the brief is unverified. It doesn't matter here: we propose fewer than 12. [CHECK]
- **The scene's own genre words** (our 22 tagged DJ promo targets, `scene_intelligence/dj_promo_targets.json`): EBM 13, acid 8, dark disco 7, electro 7, industrial 5, post-punk 2 (recounted 11-15; the first count had dark disco 8, acid 6, post-punk 3). HTN's set (dark disco, electro, acid, EBM, italo disco) matches how these DJs file music. [OWN DATA]
- **Past releases on SC**: Farewell (genre EBM) 872 plays, The Deceiver (EBM) 642, The Tour remix (Dark Disco) 259 (snapshot 11-09). Different songs and push, so this does **not** test which genre field works better. No genre change follows from it. [OWN DATA]
- **Bandcamp**: the "top genre" is a pick from a preset list, separate from free tags. Tags come from the profile genre, profile genre tags, profile location, and album + track tags. Discover matches exact (autocomplete) tag spelling. **No tag order or tag limit is documented.** [OFFICIAL: [What are tags](https://get.bandcamp.help/en/articles/15263096-what-are-tags-and-how-do-I-use-them)]
- **Bandcamp traffic, all time** (595 visits): Google 46, Bandcamp search 13, Discover dark-disco 5. Google beats every Bandcamp-internal surface, so the page text matters more than tag tweaks. [OWN DATA, `plans/bandcamp-traffic-plan-2026-10-21.md`]
- **Timing**: the Bandcamp pre-order page goes public at publish (by Nov 16). SC stays private until Dec 11, 09:00. So Google sees the **Bandcamp text about 4 weeks before the SC text**. Bandcamp's top line is the most time-critical field in this file. [OWN DATA dates; indexing speed = HYPOTHESIS]

## SoundCloud: proposal

**Genre (both tracks + EP playlist): keep "Dark Disco".**
- Pro: it's the locked choice, the scene's word, and the exact phrase people search.
- Con: a custom genre is not in the preset Charts list, so no genre chart.
- Charts are not a realistic lever at this size. "Electronic" would put the tracks into a huge pool, and "Techno" / "House" / "Trance" are banned.
- [HYPOTHESIS: a genre chart slot isn't reachable at ~100-800 plays per track.]

**Title: keep plain** ("Half the Night", "Pinocchio"). Leave the old catalogue as it is.
- Why plain is better: cleaner Google title (see the data above), the same title as the ISRC / Symphonic / Bandcamp metadata, and SC always shows the uploader's name next to the title anyway.
- Leave the permalinks alone: `/half-the-night`, `/pinocchio`, `/sets/half-the-night` are already in the DJ promo and label drafts.

**EP playlist title: optional change to "Half the Night EP"** (permalink stays the same).
- Why: on SC search, a set and a track with the same name look alike. "EP" separates them and matches "half the night ep" searches.
- Con: Symphonic carries "Half the Night", so the stores will show "Half the Night - EP" by their own rule.
- Small upside, Amir's taste call.

**Tags.** The genre field is already "dark disco", so the extra `dark disco` tag adds nothing in search (SC: genre = first tag). It's harmless, so keep it unless Amir wants it tidy. The proposed sets:

| | Half the Night | Pinocchio | EP playlist |
|---|---|---|---|
| Search tags (the words people type) | electro · acid · EBM · italo disco · Berlin | electro · acid · EBM · italo disco · Berlin | electro · acid · EBM · italo disco · Berlin |
| DJ / niche tags | none new (Amir 11-11: no key, BPM not pushed) | none new | none |
| Label (restore Dec 11, already planned) | Indigo Children Records | Indigo Children Records | Indigo Children Records |
| Optional add | **acid disco** (new, see below) | **acid disco** (new) | acid disco |

- **No key, no BPM in copy** (Amir 11-11). The `F minor` tag idea is dropped. The existing `127 bpm` / `126 bpm` SC tags stay as they are unless Amir says remove.
- **acid disco**: an exact phrase in the scene (DJ targets file as "dark disco / acid"). It sits between two tags we already use, so it isn't a new genre claim. [CHECK that the SC tag page is active before adding.] If Amir says no, nothing is lost.
- Stay off: darkwave on SC (Amir's 11-03 choice: electro instead), and anything on the never list.

**Description: an optional first line above the approved text (✍️ draft, needs his OK)**
- Why: SC search and Google snippets read the top of the description. These lines put the release words (EP, date, label) in front without touching the approved text.
- Until Dec 11 (label removed for the pitches, per the 11-10 decision):
  - ✍️ Half the Night: `Half the Night EP · out 11 December 2026`
  - ✍️ Pinocchio: `Half the Night EP · out 11 December 2026`
- From Dec 11: add `· Indigo Children Records ICR-003` to the end of the line. That replaces the separate "Indigo Children Records · ICR-003" line on the restore list, so it lives in one place.
- Then a blank line, then the approved text, unchanged.

**Link block (below the approved text, from Dec 11)**
```
Bandcamp: <album URL>?campaign=sc-desc
Spotify / all stores: <smart link>
```
- Bandcamp goes first: it's the only link with sales attribution (`bandcamp_links.py --channel sc-desc`), and the "Buy" field carries `sc-buy` separately.
- Two links at most. [HYPOTHESIS: more links dilute the click]
- The EP playlist gets the same block.

## Bandcamp: proposal

**Tag order: keep darkwave first.**
- Bandcamp documents no ranking by tag order. The "top genre" is a separate preset pick. So darkwave first costs no placement and keeps the bridge to the songs. [OFFICIAL, help page above]
- [CHECK on the form]:
  - which preset top genre the album/profile uses. It should be **electronic** (true to the sound; darkwave stays in the free tags).
  - profile location = Berlin (that powers the location filter, not the tag; `plans/bandcamp-discovery-research-2026-10-21.md`).

**Album tags: add 1-2, remove none.**
- Now: darkwave · dark disco · acid · electro · ebm · italo disco · berlin
- Proposed additions:
  - **germany**: location intersection in combined-tag Discover (berlin + germany). [OWN research 06 + OFFICIAL combine-tags]
  - **acid disco**, only if it shows in the autocomplete. [CHECK]
- Not added:
  - techno / trance (never list)
  - 303 (text only, locked rule)
  - minimal (pulls minimal techno/house buyers)

**Track-level tags**
- Copy the album set to both tracks. Each track page is its own Google-indexed URL, and Bandcamp lists track tags as a separate tag source.
- No per-track differences: the true extra words (303, trance arp, minimal groove) are all text-only under the 11-03 lock.

**About: an optional first line above the approved text (✍️ draft, needs his OK)**
- ✍️ `Half the Night EP, out 11 December 2026 on Indigo Children Records (ICR-003). Pre-order now and Half the Night is yours right away.`
- Why: this is the text Google sees from Nov 16, four weeks before SC. It puts the release name, label and catalogue number in the first sentence.
- The approved description follows, unchanged.
- After Dec 11, drop the pre-order sentence.

**Track pages: a one-line track "about" each (✍️ draft)**
- Half the Night: `From the Half the Night EP (ICR-003).`
- Pinocchio: `From the Half the Night EP (ICR-003).`
- Why: track pages are thin without it. Each line names the EP for internal linking. No BPM or key (Amir 11-11).

**Credits: keep as approved**
- "Ambertone Studio, Berlin" already gives a second city mention plus the studio name.
- The only add worth asking about: gear words (e.g. which 303 he used). That's his fact to give, not mine to guess. [ASK]

## One table

| Field | Now | Proposed | Why | Evidence |
|---|---|---|---|---|
| SC genre (tracks + EP) | Dark Disco | keep | locked, scene word, exact search phrase; charts not reachable | SC help (genre = first tag, preset = Charts); DJ targets: dark disco 7/22 |
| SC track titles | Half the Night / Pinocchio | keep plain | the artist prefix only repeats the name in Google's title | live Farewell page title (11-11) |
| SC EP playlist title | Half the Night | optional: Half the Night EP | tells the set from the track in SC search | [HYPOTHESIS] |
| SC tags | electro, dark disco, acid, EBM, italo disco, Berlin, 127/126 bpm | keep, + `acid disco` (opt.), label tag back on Dec 11 | no genre stacking; no key tag (Amir 11-11) | SC help (no boost from similar tags) |
| SC description top | approved text first | ✍️ factual first line (EP · date; label from Dec 11) | the top of the text feeds search + snippets; approved text untouched | SC help (description); description map 11-10 |
| SC link block | label line + Bandcamp (pending) | Bandcamp ?campaign=sc-desc first, smart link second | only attributed sales link; 2 links max | `bandcamp_links.py`; SC sent 2 BC visits ever before campaign links |
| BC tag order | darkwave first | keep | no documented order ranking; top genre is a separate pick | Bandcamp help "What are tags" |
| BC album tags | 7 tags | + germany, + acid disco if autocomplete | combined location filter; exact-spelling match | BC help + 2024 combine-tags blog |
| BC top genre / location | [CHECK] | electronic / Berlin | location filter = profile location | BC research 10-21 |
| BC track tags | [CHECK] | = album set on both tracks | track pages are their own tag source + Google URL | BC help (5 tag sources) |
| BC about | approved text | ✍️ release line first (pre-order wording until Dec 11) | Google sees BC 4 weeks before SC | traffic: Google 46 > BC search 13 > Discover 5 |
| BC track about | empty | ✍️ EP name + ICR-003 | thin pages; internal link | [HYPOTHESIS] |
| BC credits | approved | keep; gear line only if Amir gives the fact | no guessing gear | rule: never guess |

## Do these 3 first

1. **Bandcamp about top line + track lines** (✍️, before the pre-order publish, about Nov 16). It's the first HTN text Google indexes.
2. **Bandcamp form check**: top genre = electronic, location = Berlin, album tags copied to both tracks, + `germany`. All by hand in the uploads chat.
3. **SC first line + link block** (✍️), saved now on the private tracks (the label part waits for Dec 11). On Dec 11, run the restore list in the same pass: label tag, record label, P-line, `sc-desc` link.

Open for Amir: `acid disco` yes/no; EP playlist title; gear words for the credits.

## Check results (2026-11-11, public pages read as text, nothing logged in)

| Check | Result |
|---|---|
| SC username capital O | ✅ confirmed: the profile page title reads "Stream Inch Of Shadow music" too, so the username is "Inch Of Shadow" (capital O) everywhere on SC, the Google titles included. Changing it is a profile edit for the uploads chat, only with Amir's yes. |
| Bandcamp profile location | ✅ "Berlin, Germany", so the location filter is covered. Because the location already says Germany, the `germany` tag adds little; it's optional now. |
| Bandcamp profile bio genres | Shows "dark disco, EBM, coldwave, acid, and electro". No profile genre tags are visible on the public page. The preset top genre is still a form check. |
| `acid disco` tag pages (SC + Bandcamp) | ❌ couldn't check: both pages load their results by script, and Bandcamp shows a bot challenge to text readers. Needs one look in a normal browser (uploads chat), or drop the idea. |
| SC tag limit | ❌ couldn't check: SC help returns 403 to text readers. Not needed for this proposal (fewer than 12 tags). |
