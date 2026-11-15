# Half the Night EP: release-day playbook, Fri 2026-12-11

Inch of Shadow · Half the Night + Pinocchio · Indigo Children Records ICR-003 · UPC 708208624645 · ISRCs QZWDE2693303 / QZWDE2693308.
Written 2026-11-13 overnight (🎵 Release side chat). Text only: nothing live was changed, no Chrome.
All times Berlin. 🙋 Amir · 🎃 Claude · 🤖 runs by itself · 🌐 = work in his Chrome (one chat at a time, Chrome queue).

**Tue Dec 8: re-check every ⚠️ below against the release file** (Fable gate 11-15).

**Truth for links and dates:** `releases/pinocchio-single.json`. Where another file disagrees, the release file wins and the clash is listed under ⚠️.
**No captions or his-voice text here.** Every text that goes out as Amir (reel caption, stories, Artist Pick, Bandcamp follower message, party lines, SC first line) is approved by him in the main 🎵 Release EP chat first. This file only points to where the approved text lives.

Sources: release file (`distribution`, `checklist`, `timeline`) · `plans/half-the-night-ep-plan.md` · `plans/release-day-playbook.md` (A1-A3, Farewell base) · `plans/htn-upload-pack-sc-bandcamp.md` · `plans/htn-seo-pass-2026-11-11.md` · `plans/half-the-night-content-plan.md` + `plans/handovers/socials/htn-ep-content.md` · `plans/handovers/socials/bandcamp.md` + `plans/bc06-nov6-half-the-night.md` · `plans/handovers/booking/htn-dj-promo.md` · `plans/half-the-night-ep-tickets.html` · `plans/handovers/release/htn-platform-slots.md`.

---

## Gate: must be true before Thu Dec 10 (not release-day work, but the day fails without it)

| Item | Where | Who | Done-check |
|---|---|---|---|
| ✅ done 11-13 · Bandcamp pre-order published | https://inchofshadow.bandcamp.com/edit_album?id=2458881269 | 🙋 🌐 | album page opens without login; URL written to release file `platform_links.bandcamp` |
| ✅ done · Bandcamp listening party scheduled for Dec 11 19:00 (announced, 54 notified) | release edit page > Listening Party | 🙋 🌐 | party shows on the album page with the Dec 11 time |
| ✅ done 11-13 · `bandcamp_links.py` run for HTN (needs `platform_links.bandcamp` filled first, the script reads it from there) | `python3 bandcamp_links.py pinocchio-single` · then `--write` | 🎃 | `bandcamp_campaign_links` key in the release file has `sc-buy` + `sc-desc` |
| Smart link / pre-save built (Hypeddit via SymphonicMS > Marketing > Client Offerings) | SymphonicMS | 🙋 + 🎃 🌐 | smart-link URL written to the release file |
| Spotify pitch sent (needs 7+ days: latest ~Dec 2) | Spotify for Artists > upcoming release | 🎃 drafts · 🙋 sends 🌐 | pitch shows "submitted" in S4A |
| Spotify Canvas uploaded (per track, after the release shows in S4A) + Spotify artist header | S4A; files in `Releases/Half the Night EP/Artwork & Designs/Platform sizes/Banners/` and `videos/htn-ep/renders/` | 🙋 🌐 | Canvas plays on the track in S4A preview |
| YouTube 4K video uploaded + Premiere scheduled for Dec 11 | YouTube Studio (release file checklist `yt_*`) | 🎃 renders · 🙋 uploads | Premiere card shows the Dec 11 time |
| Release reel file chosen (trial winner, content plan step D) | `videos/htn-ep/renders/` | 🎃 builds · 🙋 picks | file named in `htn-ep-content.md` |

---

## Thu Dec 10: night before

| Time | Step | Where | Who | Done-check |
|---|---|---|---|---|
| day | Reel file locked (no edits on the day) | `videos/htn-ep/renders/` | 🙋 🎃 | final file name in `htn-ep-content.md` |
| day | Reel caption approved in the main EP chat (Mosseri checklist run on the plan) | main 🎵 Release EP chat · `docs/brand/mosseri-guide.md` | 🎃 drafts · 🙋 approves | his "yes" quoted in the EP handover |
| day | Hashtag set for the reel: max 5 in IG's own field, from release file `platform_tags.hashtags` | release file | 🎃 | 5 picked, written next to the caption |
| day | Story frames + sticker plan ready, text approved in the main EP chat | main EP chat | 🎃 builds · 🙋 approves | files listed in `htn-ep-content.md` |
| day | Spotify Artist Pick line (140 chars) approved in the main EP chat | main EP chat | 🎃 drafts · 🙋 approves | approved text quoted in the EP handover |
| day | Bandcamp release-day follower message approved (old draft in `bc06-nov6-half-the-night.md` needs a rewrite, see ⚠️) | main EP chat | 🎃 drafts · 🙋 approves | approved text quoted in the EP handover |
| day | Listening-party lines (one per track, his words: `[AMIR]` gaps in `bc06-nov6-half-the-night.md`) | main EP chat | 🙋 | both lines approved |
| day | SoundCloud restore pack: the exact field values for both tracks + EP, in one block, ready to paste | this file, section "SC restore pack" below | 🎃 | values match the release file |
| evening | Delete old IG stories that say "out soon" / pre-save, if any | IG app | 🙋 | none left in his story tray |
| ~00:00 | Spotify goes live. Quiet steps only: grab the clean Spotify URL (strip `?si=`) | open.spotify.com | 🙋 or 🎃 🌐 | clean URL in release file `platform_links.spotify` |
| ~00:00 | Pin Spotify Artist Pick with the approved line | S4A > Profile > Artist Pick | 🙋 🌐 | Pick shows on the profile |
| ~00:00 | Hypeddit: Source -> the Spotify URL | Hypeddit | 🙋 🌐 | smart link page shows the right cover + title |
| night | DO NOT: SoundCloud public, Amplify, IG reel/stories, DJ messages | | | |

---

## Fri Dec 11: release day

| Time | Step | Where | Who | Done-check |
|---|---|---|---|---|
| 09:00 | **Stores check: Spotify, Apple Music, Beatport** (+ YouTube Music, Deezer, Tidal as they come; Apple/others can lag 12-72 h). Click through every link: right artist, right track, right cover (Farewell lesson: Apple's first match was a movie). Beatport label shows "Symphonic Starter" and takes no edits. | open.spotify.com · music.apple.com · beatport.com | 🙋 or 🎃 🌐 | each URL in release file `platform_links`; `distribution.live_date` = 2026-12-11 |
| 09:00 | **Bandcamp: "release pre-order now" + Update** (Bandcamp does NOT auto-release) | https://inchofshadow.bandcamp.com/edit_album?id=2458881269 | 🙋 🌐 | album page shows "buy" not "pre-order"; both tracks playable |
| 09:05 | Bandcamp About: drop the pre-order sentence if it is in the top line (SEO pass: "after Dec 11, drop the pre-order sentence"); any new wording = his OK | same edit page | 🙋 🌐 | top line has no "pre-order" |
| 09:00 | **SoundCloud: flip both tracks + the EP playlist to public** | https://soundcloud.com/inch-of-shadow/half-the-night · /pinocchio · /sets/half-the-night | 🙋 🌐 (Amir, or Claude with his yes) | logged-out view opens all three |
| 09:05 | **SC restore list** (release file `distribution.soundcloud_private.restore_on_release_day`), on both tracks + EP: playlist type -> **EP** + release date 2026-12-11 · record label **Indigo Children Records** · tag **Indigo Children Records** · release date **2026-12-11** + P-line **2026 Indigo Children Records** (tracks) · **UPC 708208624645** (if SC has a field) · label line (see ⚠️ on where it goes) | SC edit page > Basic info + Metadata | 🙋 🌐 | each field read back after save |
| 09:10 | **SC campaign links**: Buy link = Bandcamp URL `?campaign=sc-buy`; description link block (Bandcamp `?campaign=sc-desc` first, smart link second, per SEO pass) on both tracks + EP | values from release file `bandcamp_campaign_links` | 🎃 values · 🙋 pastes 🌐 | buy button opens the Bandcamp album with `campaign=sc-buy` |
| 09:15 | **SC pin** the EP playlist to the profile (Spotlight) | soundcloud.com/inch-of-shadow | 🙋 🌐 | EP shows at the top of the profile |
| 09:15 | **SC Amplify** (mobile app only, tracks only, one shot per track, while people are awake) | SoundCloud mobile app | 🙋 | Amir says "fired" (do not assume from "public") |
| 09:20 | **Smart link live**: audio preview -> own SC track, add every verified store link | Hypeddit | 🙋 + 🎃 🌐 | logged-out smart link shows Spotify, Apple, Beatport, Bandcamp, SC |
| 09:30 | Linktree: HTN + smart link on top, direct track links below | linktr.ee/inchofshadow | 🙋 🌐 | top entry = HTN |
| 09:30 | IG bio link 1 = smart link (Edit profile = his hands only, rule 10) | IG app | 🙋 | bio shows the smart link |
| 09:30 | Bandcamp follower message, approved text only (if followers were not already notified at publish) | Bandcamp > Tools > message followers | 🙋 🌐 | sent count noted in `handovers/socials/bandcamp.md` |
| 09:30 | YouTube: Premiere / video live on the channel; description has the `yt-desc` Bandcamp link | YouTube Studio | 🙋 | video public |
| afternoon | Collect late store links; record all in the release file; restart Release Manager | release file · RM | 🎃 | RM /release page shows the links |
| 18:15 | Before Share: Mosseri checklist done; location Berlin; tag/collab (@ambertone.studios if used, verified handles only); rename audio to "Half the Night - Inch of Shadow" | IG app | 🙋 | all 3 ticked |
| 18:30 | **Release reel** on the grid, approved caption only | IG app | 🙋 | reel live |
| 18:30-18:40 | **Stories** right after the reel (link sticker = smart link or `ig-story` Bandcamp link), approved frames only | IG app | 🙋 | stories live within 10 min of the reel |
| 18:30-19:30 | Reply window: comments + DMs | IG app | 🙋 | |
| 19:00 ⚠️ | **Bandcamp listening party** (planned 19:00 = 10:00 Pacific), be there 30 min early with the approved welcome line. Clashes with the reel hour, see ⚠️ | album page | 🙋 | party ran; attendee count noted in the bandcamp handover |

### SC restore pack (values only, from the release file)

| Field | Half the Night | Pinocchio | EP playlist |
|---|---|---|---|
| Visibility | Public | Public | Public |
| Playlist type | | | EP |
| Release date | 2026-12-11 | 2026-12-11 | 2026-12-11 |
| Record label | Indigo Children Records | Indigo Children Records | Indigo Children Records |
| Tag added | Indigo Children Records | Indigo Children Records | Indigo Children Records |
| P-line | 2026 Indigo Children Records | 2026 Indigo Children Records | (none, tracks only) |
| ISRC (already set) | QZWDE2693303 | QZWDE2693308 | |
| UPC | 708208624645 if a field exists | same | same |
| Buy link | Bandcamp album `?campaign=sc-buy` | same | same |
| Description block | Bandcamp `?campaign=sc-desc`, then smart link | same | same |
| Downloads | ⚠️ on or off when public: open | same | |

---

## Sat Dec 12: day after

| Time | Step | Where | Who | Done-check |
|---|---|---|---|---|
| morning | **Overnight stats**: SC plays/likes/reposts (API, normal sync), reel views + non-follower share + skip rate (IG Insights, his phone or 🌐 outside automation windows), Bandcamp sales by hand (no automation, AUP), Spotify first-day streams if S4A shows them (one read only) | stats sync · IG Insights · Bandcamp Tools · S4A | 🎃 (SC, S4A 🌐) · 🙋 (Bandcamp, IG on phone) | numbers in release file `outcomes.stats` + `plans/ig-content-performance-log.md` |
| morning | Late store links (Apple, Tidal, Deezer, YouTube Music) clicked through + recorded | stores | 🎃 🌐 | release file `platform_links` complete or gaps named |
| any time | Story reshare of the reel | IG app | 🙋 | |
| day | **DJ wave prep**: post-release drafts get the public SC link in place of `[SC LINK]`; drafts shown in the main EP chat for approval (the 38 post-release drafts are NOT approved yet) | `plans/handovers/booking/htn-dj-promo.md` | 🎃 | approval quoted in that handover |

## After (pointers, outside the 3 days)

| Date | Step | Who | Source |
|---|---|---|---|
| Sun 12-13 | Pinocchio version of the winning reel style on the grid | 🙋 | content plan |
| **Mon 12-14** | **DJ wave starts**: public link, max 5 IG a day + SC apart, warm first, varied text; day list = send table in `htn-dj-promo.md` (12-14 to 12-19) | 🎃 drafts · 🙋 sends | release file `dj_promos_sent` (due 12-21) |
| Mon 12-14 | Spotify saves / retention check (72 h) via the Monday S4A read | 🤖 + 🎃 | release file `spotify_check` |
| 12-16 | All platform links collected | 🎃 | `platform_links` |
| 12-21 / 12-22 | Final content read; DJ follow-up | 🎃 | content plan, `dj_followup` |
| 12-25 | Rotate Spotify Artist Pick (text = his OK again) | 🙋 | `artist_pick_rotate` |

---

## ⚠️ Conflicts and missing inputs (listed, not fixed)

**Timing**
- ⚠️ Listening party is ANNOUNCED for 19:00, so it stays. The reel's 18:30-19:30 reply hour clashes: move the reel to 17:30, or accept the overlap. Question to Amir (main EP chat).
- ⚠️ The Bandcamp follower message draft in `plans/bc06-nov6-half-the-night.md` says "It is Bandcamp Friday": wrong for Dec 11 (Bandcamp Friday is Dec 4). It also still has `[AMIR]` gaps.
- ✅ SETTLED 11-13 (published publicly, followers notified at pre-order). Was: Amir doesn't want followers notified early; the "publish private" option is still unchecked (EP handover, parked uploads chat). If the album stays private, the party cannot be scheduled (it needs a public page).
- ⚠️ `plans/release-day-playbook.md` A1 says "verify Bandcamp auto-flipped from pre-order to live"; the release file says Bandcamp does NOT auto-release. Release file wins.
- ⚠️ DJ wave dates disagree inside `htn-dj-promo.md`: the main send table = Mon 12-14 to Sat 12-19; the Round 2 note says "from Mon 12-21"; the post-release header says "sent from Dec 7"; the R2 post plan (12-14 to 12-16) overlaps the main table. Release file: 12-14 to 12-21. DJ count also differs: 34 / 37 (handover) vs 38 (tickets page).
- ⚠️ Blog premiere: release file timeline `premiere_live` = 12-10, checklist says SKIP (light lane), tickets page says D9 decides it. Open.

**Still saying Dec 4 (other chats' files, not edited here)**
- ⚠️ `plans/half-the-night-ep-plan.md` body (lines 5, 20, 28, 32, 45); a top banner says "read Dec 4 as Dec 11".
- ⚠️ `plans/handovers/release/half-the-night-ep.md` lines 98, 110, 122, 161, 168 ("Next on Dec 4: restore label/date/EP type, flip public"), 170 (OAC "must be settled before Dec 4").
- ⚠️ `plans/bc06-nov6-half-the-night.md` (party/message plan built around a Bandcamp Friday release day).
- ⚠️ The brief's key name `restore_on_dec4` is old; the release file key is now `restore_on_release_day` (already Dec 11).

**Links / values not recorded yet**
- ⚠️ `platform_links`: Bandcamp ✅ set 11-13 (+ campaign links). Still empty: Spotify, Apple, Beatport, SC public, smart link.
- ⚠️ No smart-link field or URL exists in the release file (smart link not built).
- ⚠️ SC UPC field: "if SC offers a field" is unverified.
- ⚠️ SC label line: the restore list adds a separate "Indigo Children Records · ICR-003" line; the SEO pass proposes adding it to the end of a new first line instead, and that first line still waits on his OK. Pick one before Dec 11.
- ⚠️ SC downloads on/off once public: open (upload pack).
- ⚠️ Release-file `notes` field is stale: "NO Beatport", "SKIP DJ waves", date 2026-11-06. Beatport IS on, DJ wave IS planned.

**Texts in his voice with no approved version on disk**
- ⚠️ Reel caption, story frames text, Artist Pick line, Bandcamp release-day message, party welcome + track lines, SC first line. All need his OK in the main EP chat.
- ⚠️ The 38 post-release DJ drafts are not approved (the 11-11 approval covered only the 11 show hosts + 7 label drafts).

**Content / assets**
- ⚠️ Two Canvas files compete (content chat `canvas-half-the-night` vs platform-slots Canvas A); "only one goes to Spotify, Amir's tick decides". Pinocchio Canvas exists too: one or two Canvases?
- ⚠️ The release-day story set is "not in this plan" in the content plan, but the release file checklist has `fmt_story_set` (3 frames + link). No owner has it built.
- ⚠️ Release reel depends on the trial winner (read Mon 11-30); no fallback named if no trial beats the bar.
- ⚠️ Cover state: vinyl-frame swap still open (DSP cover). Beatport takes no edits, so Beatport may show a different cover than Spotify/Apple. Check per store on the day.
- ⚠️ [HYPOTHESIS] Stores may label it "Single", not "EP": 2 tracks, 11:37 total, each under 10 min, which is inside Spotify's and Apple's single rules. Release file `metadata.release_type` = "Single". The SEO pass expected "Half the Night - EP". Check on the day; no action unless Amir wants one.

**Owners needed before Dec 10 (Fable gate 11-15)**
- ⚠️ Which Canvas goes to Spotify (one or two) · who builds the story set · SC downloads on/off once public · where the label line sits on SC. Owner: 🎵 main EP chat asks Amir.

**Owners / scope not set**
- ✅ Amplify: BOTH tracks (one shot per track; main EP chat 11-13).
- ⚠️ Reddit, FB groups, Discogs (Farewell playbook A2/A3): the release file's light-lane note skips the Reddit ladder; nothing says yes or no for Discogs / FB on this release. Not in this playbook until Amir says.
- ✅ YouTube OAC GRANTED 11-13 (Symphonic reply; ♪ badge + Releases tab seen by Amir 11-14). Release-day check: HTN Art Tracks show under @InchofShadow.

---

## Final report

- 🎯 What: one Dec 10-12 release-day checklist for the Half the Night EP, in this file.
- 💡 Why: the steps sat in 9+ files, some still on Dec 4.
- ✅ Result: gate list + night before + release day (with SC restore pack) + day after + pointers to 12-25; nothing live changed.
- ⏭️ Next: Amir picks the party vs reel time; the main EP chat gets the texts for approval; the System chat fixes the Dec 4 lines.
- ⚠️ 26 items above (timing 6, Dec 4 files 4, links 6, texts 2, content 5, owners 3).
- 🐞 Mistakes: the brief named `restore_on_dec4`, but the key is `restore_on_release_day` (renamed already); the old playbook's Bandcamp "auto-flip" step would have left the EP on pre-order.
- 📚 Lessons: two live events on one Friday evening need one time owner; a campaign-link script that reads the release file needs the URL written there first.
