# Clip pack per song: research, 2026-11-06

Question: per single, fix the timecodes once (TikTok 60 s clip start, the reel "hook bar", a Spotify Canvas loop, a Shorts Preview window), post the same clean clips on IG Reels, TikTok and YouTube Shorts, and keep a `used_in` list. Is that a good move?

Builds on `research-tiktok-2026-11-05.md`, `research-social-algo-2026-11-05.md`, `research-content-language-2026-11-05.md` section 5 and `plans/platform-algorithm-research-tiktok.md`. Facts already in those files are referenced, not repeated.

Tags: **[OFFICIAL]** the platform (or Symphonic, YouTube, Spotify) about its own product. **[REPORTED]** named press or a primary text read only through a quote or search snippet. **[CLAIMED]** blog, vendor or single creator, no method. **[JUDGEMENT]** my reasoning, not evidence. All links seen 2026-11-06 unless marked. No Wikipedia. No file was downloaded in this research (text fetches only), so nothing went to the Trash.

## Verdict (5 lines)

1. **Good move, with adjustments.** No platform penalises the same clean file of your own on Reels, TikTok and Shorts; the official penalties are watermarks and re-uploading other people's work.
2. **The real duplicate risk is on the SAME platform:** Instagram recommends only the first of two identical pieces and recommends only the original when it finds two or more identical pieces; TikTok makes "unoriginal or reused material without anything new" ineligible for the For You feed. So `used_in` must block a second identical upload on the same platform.
3. **Fix the hook as an audio section, not as a fixed opening frame:** one sound everywhere is what YouTube officially advises and what builds a sound page; the first visual frame should change per post.
4. **60 s is the shared ceiling** (TikTok library cap; Shorts over 1 min with a Content ID claim are blocked), and every TikTok cut must sit inside the delivered 60 s window.
5. **Attach the sound in each app, do not bake it in,** and treat Canvas and Shorts Preview as separate fields with their own rules (Canvas is a silent visual loop; Preview needs Symphonic to deliver it via DDEX).

## 1. Same clip on Reels, TikTok and Shorts: any penalty?

**Instagram**
- **[OFFICIAL]** Originality page (dated 2024-04-30, read in German): recommended content must have "keine sichtbaren Wasserzeichen" (no visible watermarks). "Wenn wir zwei oder mehr identische Inhalte auf Instagram finden, empfehlen wir nur das Original." Matching uses audio-visual signals. The text is about copies **on Instagram**; it says nothing about your own work posted on other apps. [creators.instagram.com/recommendations-and-originality](https://creators.instagram.com/recommendations-and-originality)
- **[OFFICIAL]** Original Content Guidelines: original = work you created yourself; borders, watermarks, speed changes or a new caption do not make someone else's content original. No line on cross-posting your own work. [creators.instagram.com/original-content-guidelines](https://creators.instagram.com/original-content-guidelines/)
- **[OFFICIAL]** 2026-04-30 Creators blog: aggregator rules extended to photos and carousels; accounts that mainly post non-original content lose recommendations; follower feeds unaffected. [Rewarding original creators](https://creators.instagram.com/blog/rewarding-original-creators-on-instagram)
- **[OFFICIAL]** Mosseri, "Instagram Ranking Explained", 2023-05-31: Reels made less visible include "low-resolution or watermarked reels", muted reels, reels with borders, majority-text reels, "or reels that have already been posted on Instagram". [about.instagram.com](https://about.instagram.com/blog/announcements/instagram-ranking-explained)
- **[REPORTED]** Mosseri, Oct 2024: your own logo on a reel is fine; other apps' logos are the problem. [Social Media Today](https://www.socialmediatoday.com/news/instagram-clarifies-that-including-your-own-logo-on-a-reel-is-ok/730852/) (seen via post-bridge summary)
- 2026-10-30 Mosseri: other-app edits are not demoted, only watermarks [REPORTED, already in `research-social-algo-2026-11-05.md`].

**TikTok**
- **[OFFICIAL]** Community Guidelines in force 2026-09-24: For You ineligible "if it includes unoriginal or reused material without anything new". No examples on the page. [Integrity and Authenticity](https://www.tiktok.com/community-guidelines/en/integrity-authenticity)
- **[OFFICIAL, 2020]** TikTok does not recommend "duplicated content, content you've already seen before, or any content that's considered spam"; the feed "generally won't show two videos in a row made with the same sound or by the same creator". [TikTok Newsroom](https://newsroom.tiktok.com/en-us/how-tiktok-recommends-videos-for-you)
- **[CLAIMED]** Creator Academy originality page reportedly lists four kinds of unoriginal content: exact copies, reposts without creative edits, low-value compilations, other apps' watermarks. The page loads empty for a text fetch, so not verified. [Creator Academy](https://www.tiktok.com/creator-academy/article/tiktok-originality-policy), summary via [shapelessai](https://shapelessai.com/notes/unoriginal-content-rules-youtube-tiktok-instagram)
- **[CLAIMED]** TikTok's in-app music licence does not cover re-uploading a TikTok (with library sound) to other apps. One more reason to work from our own clean master, never from a TikTok download. [shapelessai](https://shapelessai.com/notes/unoriginal-content-rules-youtube-tiktok-instagram)

**YouTube Shorts**
- **[OFFICIAL]** TeamYouTube, 2026-10-01, "Prioritizing original content on Shorts": "reduce the reach of content re-uploaded from other creators"; channels "primarily aggregating or re-uploading other creators' videos" get less Shorts distribution. Spam policy wording: "Re-posting material from other websites or platforms, or other videos without adding anything of your own." The target is other people's work. [ppc.land summary](https://ppc.land/re-uploaded-shorts-lose-reach-as-youtube-favours-original-clips/), [Help Community thread](https://support.google.com/youtube/thread/470890423/prioritizing-original-content-on-shorts?hl=en) (body not readable), [9to5Google](https://9to5google.com/2026/10/02/youtube-wont-recommend-unoriginal-shorts/)

**What creators measured**
- No study isolates "same clean file on three apps vs native per app". NOT FOUND.
- **[REPORTED, vendor data]** Metricool Short Video Report 2026 (6M+ videos, 375k accounts), published 2026-11-02: TikTok about 42.6% more average views than Reels and over 6x Shorts; accounts under 2,000 followers average about 2,430 TikTok views; Reels win on shares and comments. These are platform averages, not a duplicate test. [Metricool](https://metricool.com/how-to-repurpose-video-content/)
- **[CLAIMED]** Hootsuite lab, 2021-09-08: five near-identical videos made fresh in each app; Reels on a new account got at most 2 views, TikTok about 450 from zero followers. Small, old, not identical files. [Hootsuite](https://blog.hootsuite.com/experiment-reels-vs-tiktok/)
- **[CLAIMED]** Blogs that claim a shared "originality score" or cross-platform fingerprinting give no primary source. Treat as myth until shown. [syncstudio](https://syncstudio.ai/blog/cross-post-business-videos-2026), [socialync](https://www.socialync.io/blog/avoid-content-duplication-penalties-cross-posting-2026)

**Answer:** same clean file on the three apps: no official penalty anywhere [OFFICIAL wording scope]. Same file twice on one app: officially down-ranked on Instagram, officially not recommended as "duplicated" on TikTok.

## 2. One hook for all platforms or one per platform?

**Opening (first 1 to 2 s)**
- No source compares the same opening on TikTok vs Reels with a method. NOT FOUND.
- **[OFFICIAL]** Sound behaviour differs: over 75% of Instagram Reels views are sound on (Meta developer blog, 2024-11) vs "over 30%" of TikTok users watching on mute (Creator Academy, base file). [Meta for Developers](https://developers.facebook.com/blog/post/2024/11/07/unlock-the-power-of-reel-ads/). **[JUDGEMENT]** The same audio hook works on both, but on TikTok the first frame must also work silent (a text line or motion).
- **[OFFICIAL]** Instagram Trial Reels show a reel to non-followers first (eligibility per `research-social-algo-2026-11-05.md`: 200 for professional accounts [REPORTED], sources still conflict). It is the only tool any of the three platforms offers for testing openings on strangers.
- **[REPORTED, old]** Music listening: 24% of Spotify plays skipped in the first 5 s (Echo Nest / Paul Lamere data, 2014). The first seconds of the section matter as much as the first frame. [Hypebot](https://www.hypebot.com/new-data-reveals-almost-25-of-people-skipping-song-within-5-seconds/)

**Same bar every time: recognition or fatigue?**
- **[OFFICIAL]** YouTube's pre-release guide: without a Preview, use "the same Shorts audio snippet for all content uploaded before release day" so fans' videos gather under one sound. [artists.youtube](https://artists.youtube/resources/pre-release-strategy/)
- **[OFFICIAL]** TikTok's sound page counts and shows every video using the library sound (base file). Scene breakouts came from many videos using one sound (`research-tiktok-2026-11-05.md` section 3).
- **[OFFICIAL]** TikTok will not show two videos with the same sound in a row, so one sound across his posts will not stack in one viewer's session.
- **[REPORTED, research]** Repetition and liking follow an inverted U: 50 of 57 studies in a century-long review fit it (Chmiel and Schubert 2017, via [Frontiers](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00147/pdf) citing it); Deezer streaming data shows re-listening probability follows the same curve ([Sguerra et al., arXiv 2210.16226](https://arxiv.org/abs/2210.16226)). One naturalistic study found liking kept rising over four weeks (Madison and Schiolde). **[JUDGEMENT]** A few weeks of one hook per song sits on the rising side; fatigue is a risk across many weeks with the same footage, not with the same sound.
- **[OFFICIAL]** Instagram matches identical content by audio-visual signals. **[JUDGEMENT]** Same sound plus different footage is normal (every user of a song shares the audio). Same sound plus the same opening shot every time moves toward "identical". Keep the audio fixed, vary the picture.

**Length**
- TikTok: library music capped at 60 s per video (base file, Symphonic FAQ 2026-06-16 [OFFICIAL]). **[CLAIMED]** Buffer says TikTok videos over 60 s reach more, but that needs non-library audio, which loses the sound page.
- Instagram: Reels up to 20 min, recommended to new audiences only up to 3 min [REPORTED, social-algo file]. Library songs: Mosseri, 2025-02-01: "I don't believe we have the licenses for three minutes of audio tracks" [OFFICIAL, Threads](https://www.threads.com/@mosseri/post/DFitJNnSidg?hl=en); a 90 s music limit is [CLAIMED] by many guides, no Meta page found.
- YouTube Shorts: up to 3 min; "most songs for up to 90 seconds in a 3 minute Short", some only 60 or 30 s; **any Short over one minute with an active copyright claim is blocked globally** [OFFICIAL]. [Understand three-minute Shorts](https://support.google.com/youtube/answer/15424877?hl=en), [Music eligibility for Shorts](https://support.google.com/youtube/answer/13486873?hl=en). **[JUDGEMENT]** If Symphonic runs Content ID on his tracks, his own Short over 60 s with his song could be claimed by his own distributor and blocked. Keep Shorts at 60 s or under, or have his channel whitelisted.
- Our own data: about 6 s average watch, 50 to 65% gone by 0:02 [OWN, reel-craft]. Most cuts should be 8 to 20 s; the 60 s cut is for TikTok's library window and fan use.

**Aspect and safe zones**
- All three: 9:16, 1080x1920. Safe zones (all published for ads, organic use is an assumption):
  - Instagram Reels: 14% top, 35% bottom, 6% sides = about 269 / 672 / 65 px [REPORTED, Meta ad specs via [inro](https://www.inro.social/tools/instagram-reels-safe-zone-checker)]. Already our rule (`render-and-shrink` memory).
  - TikTok: no pixel numbers on TikTok's help pages; only a template ZIP in the ads help centre; guides read it as 130 to 240 top, 484 to 660 bottom, 120 to 140 right [CLAIMED, conflicting]. [selzee](https://selzee.com/blog/tiktok-ad-specs), [yosefk](https://yosefk.me/blog/tiktok-safe-zone/)
  - YouTube Shorts: 288 top, 672 bottom, 48 left, 192 right [REPORTED, Google ads guidance via third parties; Google's PDF](https://services.google.com/fh/files/misc/universalsafezones-youtube.pdf).
  - **[JUDGEMENT]** One master works if text and face stay inside the union: top 288, bottom 672, left 65, right 192.

**Sound handling**
- TikTok: pick the library sound in the app; it replaces all audio; baked-in audio gets no sound page, no count, no royalties [OFFICIAL, base file].
- Instagram: pick the song from the music library; **[REPORTED]** if a reel's audio matches a licensed track, Instagram may change "Original audio" to the artist and song and add the reel to that audio page (help-centre text via search snippet; [Sked help](https://help.skedsocial.com/how-audio-selection-works-on-instagram-reels-when-you-upload-a-video-edited-on-desktop-or-inside-sked)). Not reliable enough to depend on; pick it in the app.
- Shorts: "Always use official audio clips from the Shorts audio picker" [OFFICIAL, [YouTube Help 18736733](https://support.google.com/youtube/answer/18736733?hl=en)].
- **[JUDGEMENT]** So the master file should be exported silent (plus a guide-audio version for checking sync), with the song attached in each app at the logged song timecode.

**Answer:** one fixed audio hook per song across platforms is supported by YouTube's own advice and by how sound pages work. Per-platform differences are in the picture (silent-first frame for TikTok), the length (60 s ceiling) and the sound attachment, not in the musical section.

## 3. Re-using a clip over time (`used_in`)

- **Instagram, same file again:** officially down-ranked: "only recommend the original" when two or more identical pieces exist [OFFICIAL, section 1]. (The phrase "already posted on Instagram" is not on the page; corrected per the 2026-11-06 Gero-studies gate and again at the Batch 4 gate.) A re-upload reaches followers at best. **[CLAIMED]** waiting weeks does not change it ([noobclaw](https://noobclaw.com/blog/same-reel-multiple-accounts-2026/)).
- **Instagram Reposts:** since Aug 2025, public reels and posts can be reposted to followers' feeds, with a Reposts tab on the profile; **[CLAIMED]** works on your own public reels. [PetaPixel 2025-08-06](https://petapixel.com/2025/08/06/instagram-adds-a-reposts-tab-to-users-profiles-similar-to-tiktok/), [socialz](https://socialz.ai/blog/how-to-repost-a-reel-on-instagram). This is the no-risk way to bring an old clip back.
- **Instagram Replace audio:** "change your in-app audio on a post or carousel you've already shared", keeps likes, comments, shares [REPORTED, Instagram quoted by [Music Ally 2026-07-22](https://musically.com/2026/07/22/instagrams-latest-feature-swaps-new-music-into-old-posts/)]. Reels are not named. Use: put the new single on older posts; log it in `used_in` as an audio swap, not a new post.
- **Instagram Linked Reels (series):** reportedly removed from 2026-10-28 [REPORTED, single source, [selfemployed.com](https://www.selfemployed.com/news/instagram-removes-reels-series-linking-october-28-2026/) citing Social Media Today]. Do not build the pack around linking reels.
- **Instagram Edits audio links:** a tappable link from a reel to a song's audio page, October 2026 [CLAIMED, one how-to, no Meta announcement found]. Check in the app before relying on it.
- **TikTok, same file again:** official line says no "duplicated content" [OFFICIAL 2020]. **[CLAIMED]** Jon Loomer re-posted the identical file within 11 hours and got over 10x the plays (undated, one test). [jonloomer](https://pubcast.jonloomer.com/videos/should-you-repost-videos-on-tiktok/). **[CLAIMED]** no rule against re-uploading your own video in the 2026-09-24 guidelines ([noobclaw](https://noobclaw.com/blog/post-same-video-twice-tiktok-2026/)). Mixed; treat a re-upload as a rare rescue of a flop, not a plan.
- **TikTok Repost button:** shares a video to your followers' or friends' feeds, not to your profile; availability varies [CLAIMED, guides, no official page read]. [Kapwing](https://www.kapwing.com/resources/how-to-repost-on-tiktok/)
- **What small music accounts do:** no method-backed source found. **[CLAIMED]** small artists "spam post" the same song with new framing ("7 exposures"); Artist Advisory 2026 advises testing three hooks of one song before release. [artistadvisory](https://artistadvisory.io/guides/independent-artist-growth-playbook-2026). The press cases in our TikTok file (Molchat Doma, NESYA, Sinnerella) grew from OTHER people's videos, not from re-posts.

**Answer:** reusing the same **footage** in a new cut is fine and normal. Reusing the same **file** on the same platform is the one thing the evidence says hurts (IG) or is not recommended (TikTok). The registry is useful exactly because it stops that.

## 4. TikTok 60 s Clip Start Time and library caps, Nov 2026

- **STILL TRUE [OFFICIAL, Symphonic, read via search index today; the page itself returns 403]:** "The duration of the clip we send to TikTok is 60 seconds long." Field "Clip Start Time (optional)", format HH:MM:SS; can be added after delivery by editing the release. [Symphonic TikTok Overview](https://support.symdistro.com/hc/en-us/articles/360042330411-TikTok-Overview)
- An old Symphonic blog (2020) and an undated guide still say 30 s, fixed. **[MYTH]** for 2026; it is the outdated text. [Symphonic 2020](https://blog.symphonicdistribution.com/2020/04/how-to-get-music-on-tiktok), [Indie Music Academy](https://www.indiemusicacademy.com/blog/choosing-tiktok-song-preview-start-time)
- **[OFFICIAL, other distributors]** TuneCore: the clip is "the next 60 seconds"; allow 2 weeks for TikTok to process a change. [TuneCore](https://support.tunecore.com/hc/en-us/articles/360034924992-TikTok-TikTok-Music). EmuBands, 2026-07-06: up to **three** TikTok clips per track, each starting anywhere, each up to 60 s, live in 24 to 48 h. [EmuBands](https://www.emubands.com/new-feature-multiple-tiktok-sound-clips/). UnitedMasters: custom clips of 15 to 60 s (page 403 today, search snippet). So TikTok itself accepts more than one clip per track; whether Symphonic offers it: UNKNOWN.
- **Changes since September:** none found. No TikTok, Symphonic or Instagram announcement changing library music length between 2026-09-20 and today. Searches returned trend lists and older guides only.
- **Pre-release:** TikTok for Artists pre-release tool needs a certified Artist Account [OFFICIAL, base file].

## 5. Spotify Canvas and YouTube Shorts Previews: specs

**Spotify Canvas [OFFICIAL, [Canvas guidelines](https://support.spotify.com/us/artists/article/canvas-guidelines/), [Canvas content policy](https://support.spotify.com/artists/article/canvas-content-policy/)]**
- 3 to 8 s, vertical 9:16, 720 to 1080 px tall, MP4 or JPG. File size: not stated.
- Avoid talking, singing or rapping on screen; avoid rapid cuts and intense flashing. "The edges may get cut off on some phones." Loop types: continuous, hard cut, rebound. Can be changed later; views add up.
- Consider leaving out song and artist name (Now Playing shows them).
- No links or URLs, no ticket sellers, no "follow or like us" calls, no other brands (Spotify logo included), no selling; text must relate to the song.
- **[CLAIMED, consistent]** It plays muted over the song and is not synced to the track position. So a Canvas field is a footage in/out, not a song timecode.
- **[OFFICIAL, old]** "up to 120%" streams and "up to 114%" saves with a good Canvas, Spotify, 2019-10-10, no baseline stated. [Canvas Metrics Guide](https://artists.spotify.com/blog/canvas-metrics-guide)
- **[OFFICIAL]** Spotify Clips (3 to 30 s) closed to new uploads since 2026-06-17; Clips on Countdown Pages are now "countdown videos". Do not add a Clips field. [Spotify: Clips](https://support.spotify.com/artists/article/clips)

**YouTube Shorts Previews [OFFICIAL, [Deliver Shorts previews](https://support.google.com/youtube/answer/12815646?hl=en)]**
- Delivered only by a label or distributor via YouTube Content Manager and DDEX ERN 3.6+; "not currently supported in ERN 4".
- Segment = `StartPoint` (seconds from track start) plus `EndPoint` or `Duration` (ISO 8601, e.g. PT0H0M45S). "No official recommendation" on length; the page notes a Short can be up to 60 s; YouTube's own example uses 30 s.
- `ClipPreviewStartDate` must be before the release date. On release, Shorts using the Preview redirect to the full track. The Shorts preview policy reference match must be over 16 s.
- Fans get a "Notify me" button; trailer about two weeks before release [OFFICIAL, artists.youtube].
- Symphonic support: NOT FOUND in any public source. Ask.

## What the pack should contain

One pack per song, in the release JSON (or `releases/<slug>-clips.json`). Each field with the spec behind it.

| Field | What it holds | Spec behind it |
|---|---|---|
| `tiktok_clip_start` | HH:MM:SS sent to Symphonic | 60 s window, Symphonic format HH:MM:SS; change takes up to ~2 weeks [OFFICIAL, Symphonic/TuneCore] |
| `tiktok_clip_window` | start and start+60 s, derived | every TikTok cut with the library sound must sit inside it |
| `tiktok_extra_clips` | empty until Symphonic says yes | TikTok accepts up to 3 clips per track via some distributors [OFFICIAL, EmuBands] |
| `hook_bar` | song in/out (e.g. 1:12.0 to 1:15.5), inside the TikTok window | one sound for all pre-release Shorts [OFFICIAL, YouTube]; sound pages [OFFICIAL, TikTok] |
| `shorts_preview` | StartPoint, Duration (30 to 60 s), ClipPreviewStartDate | DDEX ERN 3.6+, start date before release, only via distributor [OFFICIAL] |
| `canvas` | source footage file, in/out, loop type, 3 to 8 s | 9:16, 720 to 1080 px tall, MP4/JPG, no talking/singing, no rapid cuts, no links or handle, no sting [OFFICIAL, Spotify] |
| `master_cuts[]` | id, song in/out, length, file (silent export + guide-audio copy) | 1080x1920; text and face inside top 288 / bottom 672 / left 65 / right 192 [REPORTED, union of the three] |
| `cut.length` | seconds | TikTok 60 s max with library sound; Shorts 60 s max if any claim; Reels under 3 min [OFFICIAL/REPORTED] |
| `cut.first_frame` | short note of the opening shot | vary per post; same audio, different picture (IG audio-visual matching) [OFFICIAL + JUDGEMENT] |
| `cut.silent_ok` | yes/no: does frame one read without sound | TikTok over 30% mute vs IG over 75% sound on [OFFICIAL] |
| `used_in[]` | platform, date, post URL, cut id, kind (`post` / `trial` / `repost` / `replace_audio`), sound attached (library / original / preview) | a second `post` of the same cut id on the same platform is blocked [OFFICIAL, IG + TikTok duplicate lines] |
| `content_id_note` | whether his channel is whitelisted at Symphonic | Shorts over 1 min with any active claim are blocked [OFFICIAL, YouTube] |

## What to change in the idea

1. **Fix the hook as a song section, not as a fixed opening shot.** Was: the same hook bar opens every reel. Change: the same audio section opens every reel; the first frame changes each time. Why: same sound is advised and aggregates (YouTube, TikTok); identical audio-visual openings drift toward Instagram's "identical content" test.
2. **Put the hook bar inside the TikTok 60 s window.** Choose the clip start first, then the hook bar and all cuts inside it. Otherwise the best part is unusable on TikTok with the library sound.
3. **Export the masters silent and attach the sound in each app.** Keep a guide-audio copy only for checking sync. Baked audio loses the sound page on TikTok and is not reliably matched on Instagram.
4. **Cap every shared cut at 60 s.** TikTok's cap and YouTube's 1-minute claim block make 60 s the real ceiling; most cuts 8 to 20 s given our 6 s average watch.
5. **Make `used_in` a guard, not only a log.** Block a second identical upload on the same platform; route reuse to Repost (IG, TikTok), Replace audio (IG posts and carousels) or a new cut from the same footage.
6. **Use Trial Reels for the per-platform hook test on IG,** not three separate TikTok/Reels/Shorts edits. One build, 2 to 3 first-frame variants, as in content-language experiment 5.
7. **Canvas is its own object.** 3 to 8 s silent loop of footage, no handle, no sting, no text beyond the song; not a timecode of the song.
8. **Ask Symphonic two questions before building the Preview and extra-clip fields:** (a) can Starter deliver YouTube Shorts Previews (DDEX ERN 3.6, StartPoint and Duration, preview start date)? (b) can it deliver more than one TikTok clip per track? Plus (c) is Content ID on for his tracks, and can his own channel be whitelisted?
9. **Drop Spotify Clips** from any plan: closed to new uploads since 2026-06-17.

Noticed, out of scope (one line): Music Ally (2026-11-04) and Hypebot say the Wrapped 2026 artist asset deadline is today, 2026-11-06, and recommend a Canvas on every track.

## Sources not readable today
Symphonic support (403; Clip Start Time text read from the search index), UnitedMasters help (403), TikTok Creator Academy originality page (empty shell), YouTube Help Community thread body (truncated), Instagram help centre audio page (empty shell), Meta Business Help Reels safe zones (not found, third-party quotes used). No Wikipedia used.
