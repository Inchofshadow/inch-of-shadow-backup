# Inch of Shadow release guide, songs era (S3, written 2026-11-06)

Status: gated by Opus 2026-11-06 (approve with fixes, `gates/2026-11-06-batch-4.md`); written as Batch 4
task S3 of the strategy review. The electronic lane keeps its own guide: `inch-of-shadow-release-guide.md` (Beatport variant).

What this file is: the per-single release process for the sung songs. One model, one timeline, one
job per platform. Every rule names its source and keeps the research tag: [OFFICIAL] the platform's
own page, [REPORTED] press or research, [SEEN] read on a real profile page, [CLAIMED] blog or
vendor, [OUR DATA] our own logs, [JUDGEMENT] reasoning, not evidence. Where a fact is missing from
the nine source files it says "not in our research". Nothing here was researched fresh.

Public status (`docs/brand/positioning.md`, PUBLIC STATUS): the songs are not public. No song name,
no lyric and no release date appears in this guide or in any public copy before Amir calls the
switch. The first single's date is open.

---

## 1. The model

- 8 songs = 8 singles, released every 4 to 8 weeks, then an album that collects them (card S3,
  `refresh-page/index.html`).
- Each single is pitched to Spotify and to Amazon. Never two pitches at once: Spotify allows one
  pitch at a time, the next opens only when the pitched song is live, and only unreleased songs
  can be pitched [OFFICIAL, Spotify pitching page via `research-pitch-2026-11-05.md` row 4].
- Each single opens one Release Radar week: followers and listeners get one song per artist per
  week, for up to 4 weeks if unheard [OFFICIAL, Release Radar page via research-pitch row 3].
- Why singles and not an EP first: each release opens one pitch and one Release Radar week, and
  streams pile up on fewer tracks, which matters because a track earns recorded royalties only
  with at least 1,000 streams in the previous 12 months [OFFICIAL, research-pitch row 13]. Farewell
  (297) and The Deceiver (293) sat under that on the 12-month view [OUR DATA, same row].
- The 4 to 8 week gap is advice only; no study measures it [CLAIMED, research-pitch row 15 and
  card S3]. The official mechanics behind it (one pitch at a time, 7 days minimum lead, one
  Release Radar song per week) are what the spacing is built on, not the number itself.
- Our own spacing rule (card S3): the next single's pitch opens only after this single's Release
  Radar week has run. Spotify itself opens the next pitch the moment the song is live
  [OFFICIAL]; the extra week is our rule, so each song gets its own Release Radar slot
  [JUDGEMENT, derived in research-pitch section 2: with 7 days minimum lead, 4 weeks apart is the
  practical minimum that lets each pitch sit 2 to 3 weeks].
- Pitch every release. The old line "pitching every release can hurt you" has no source and is
  dropped [MYTH, research-pitch row 2].

---

## 2. One single, one page: the timeline

T = release day, a Friday. Release Radar and New Music Friday refresh on Friday [OFFICIAL,
research-pitch section 2]. Nothing on a Thursday: no proof it performs better [CLAIMED, same].

| When | What | Rule and source |
|---|---|---|
| T-8 weeks | Bandcamp private draft of the single; Bandcamp Daily pitch through the Bandcamp form with that draft link; press list for the songs ladder ready (section 7) | "Eight weeks before your release date is ideal"; send a Bandcamp link, not another platform; about 1,000 pitches a week [OFFICIAL, bandcamp.com/guide via research-pitch rows 16 and 17] |
| T-8 to T-5 weeks | Clip pack decided and stored in `releases/<slug>.json` (section 5): the 60 s TikTok clip start, the hook bar inside it, the Canvas footage, the Shorts Preview window if Symphonic delivers it. One listening pass with Amir per track | The TikTok clip start is a release decision, written before submission [research-tiktok change 2; 60 s window OFFICIAL, Symphonic]. Schema: `plans/clip-pack-schema.md` |
| T-4 weeks | Teaser reel: 10 to 15 s, the chorus, his face into the lens, the song as named audio, no date on screen. Also the TikTok and Shorts cuts of the same clean file. Artwork and metadata final; Symphonic submission with the TikTok Clip Start Time | Teaser with the song 3 to 4 weeks out beat the release-day post unless that post carries the video; the date card is the floor [SEEN, content-language patterns 1 and 7; gate 2026-11-05: strong tendency, not a law]. Symphonic approval took about 24 h [OUR DATA, research-pitch row 1] |
| Delivery day (T-4 to T-3 weeks) | Spotify pitch from Music > Upcoming the day the song shows there. Amazon Music for Artists pitch the same day (Owner or Admin, one track per release). Video pitch separately if an eligible video exists and reaches Spotify | Deliver and pitch at least 7 days before release; one song at a time; unreleased only; edits possible until release day but editors may not see them [OFFICIAL, research-pitch section 1]. Amazon: one track per new release [OFFICIAL, row 9]. Video: unreleased or within 7 days of release, separate pitch [OFFICIAL, row 20] |
| T-2 weeks | Pre-save link with a follow ask. YouTube Shorts Previews with the official audio from about T-14, only if Symphonic delivers them (open question 1 in the clip pack schema). Artist Pick text and welcome mail text approved by Amir in the main chat | Pre-save is a follow and fan-capture tool, not a ranking input [CLAIMED / derived, research-pitch row 12]. Shorts Preview: distributor-only delivery, DDEX ERN 3.6+, start date before release [OFFICIAL, research-clip-pack section 5]. Activation texts: `plans/activation-messages-2026-11-06.md` |
| T-1 evening | Prep done, nothing improvised on the day: Canvas uploaded, release-day reel in drafts, caption locked, hashtags picked, grid image ready, Artist Pick text ready. Post-midnight once Spotify is live: clean URL, pin the Artist Pick, check Bandcamp flipped from pre-order | `plans/release-day-playbook.md` part A1 [OUR DATA]. No audience-facing posts at night (same) |
| T, release day | Section 3 below | |
| T+0 to T+14 | Amazon pitch window still open if it was missed. SoundCloud: the follower-only track goes public and Amplify fires, inside 14 days of the gated upload. Side-Line news item on release day or the day before (free). One mail to the list | Amazon: up to 14 days after street date [OFFICIAL, research-pitch row 9]. Amplify: public, music, 1 to 10 min, uploaded or made public in the last 14 days, direct upload [OFFICIAL snippet, research-listening-platforms 1.2]. Side-Line timing [OFFICIAL, research-pitch section 5]. Email: one mail per release, nothing else [platform plan] |
| T+12 to 14 | Rotate the Spotify Artist Pick (max two lines, what comes next, no date) | Release-day playbook A4; activation messages section 2. An Artist Pick stays live 180 days at most [activation messages] |
| T+28 | Day-28 read: Release engagement in S4A plus the fan actions, written to the release file (section 4) | Release engagement = % of monthly active listeners who streamed the release in its first 28 days [OFFICIAL, research-listening-platforms 2.2] |
| After T+7 | The next single's Spotify pitch may open (our rule, section 1) | One pitch at a time [OFFICIAL]; the extra week is ours |

Bandcamp Friday: release on a Bandcamp Friday when the dates line up (platform plan). The dates
known in our research are 2026-11-06 and 2026-12-04 [OFFICIAL, research-listening-platforms
section 3]; 2027 dates are not in our research, check daily.bandcamp.com/features/bandcamp-fridays
when the single's date is set.

---

## 3. Release day

Order and hours follow `plans/release-day-playbook.md` part A2 (start 09:00 Berlin, reel in the
evening with the engagement hour after it). The songs-era pieces:

1. 09:00 verify the DSPs are live and collect the links; click through every auto-matched link
   (Apple matched Farewell to a movie once) [OUR DATA, playbook A2 and E].
2. Bandcamp live, not pre-order; the single pinned; mailing list sign-up visible on the release
   page [platform plan, Bandcamp row].
3. Spotify: Artist Pick pinned to the single (text approved beforehand, section 2 of the
   activation messages); Canvas live: 3 to 8 s loop, 9:16, 720 to 1080 px tall, MP4 or JPG; no
   talking or singing on screen, no rapid cuts, no links, no "follow us", no other brands, text
   only about the song; our own rule adds no handle and no sting [OFFICIAL, Spotify Canvas
   guidelines and content policy via research-clip-pack section 5; `clip-pack-schema.md` canvas].
4. SoundCloud: the single goes up as a follower-only track in Artist Pro, direct upload, not via
   the distributor (Amplify is "not guaranteed" for distributor-delivered tracks). Description:
   the approved text from activation messages section 3. Public and Amplify inside 14 days
   [OFFICIAL snippet, research-listening-platforms 1.2; platform plan SoundCloud row]. Amplify
   from the mobile app, tracks only, in daytime [OUR DATA, playbook A2 step 2b].
5. Instagram, the release-day reel: the song with his face or hands, never a card with a date.
   The story set carries the date and the link sticker; stories go out inside the reel's first
   hour [SEEN, content-language section 4 "where the kit contradicts"; playbook A2 steps 10 to 12].
   Before Share: the checklist in `docs/brand/mosseri-guide.md`; the song as named audio from the
   library, not baked in [SEEN, content-language pattern 5].
6. TikTok: the release-day cut posted clean with the library sound picked in the app; the
   "By Artist" video pinned on the sound page once certified [OFFICIAL, research-tiktok section 4
   idea 10].
7. YouTube: the official video (one per single, performance or studio) is the top piece; Shorts
   point at it [SEEN, platform plan YouTube row].
8. Email: the welcome mail automation is already on (one message, once, when someone joins); the
   release mail goes out once. Whether Buttondown or Bandcamp's own message tool sends the welcome
   mail is still open [activation messages section 4].
9. Press: Side-Line news item (genre in the subject and first line, Bandcamp link) [OFFICIAL,
   research-pitch section 5]. Warm curators only; the paid route follows the D9 rule (section 7).
10. Smart link, Linktree and the IG bio links as in the playbook A2 steps 3, 7 and 8 [OUR DATA].

---

## 4. The day-28 read

On day 28 after the release date, one object is written to `releases/<slug>.json` at
`outcomes.stats.engagement_d28` (the score board metric id is `release_engagement_d28`,
`plans/targets.json`). Fields: `value` (the sum of the parts), `as_of`, `release_date`, `parts`,
`source`, `note`. Parts counted: `spotify_saves`, `spotify_playlist_adds`, `sc_likes`,
`sc_reposts`, `ig_comments`, `ig_shares`, `bandcamp_follows` [OUR DATA, targets.json schema].

Read alongside it, not summed into it: the S4A Release engagement % and the song's Playlists tab
(did Release Radar carry it) [OFFICIAL, research-listening-platforms 2.2 and change 4]; Spotify
followers before and after; Amplify result and plays in the first 14 days on SoundCloud; views per
follower, non-follower share, sends, profile visits and follows on Instagram; videos by others per
sound and Add to Music App saves on TikTok (platform plan, measure column).

The baseline is the first day-28 read; rungs are set after it [targets.json rule]. The first
songs-era read is compared with it, not with the electronic releases.

---

## 5. Clip pack, TikTok, Reels, Shorts

Decided once per single, stored in the `clips` block of the release file
(`plans/clip-pack-schema.md`, built from `research-clip-pack-2026-11-06.md`). The rules:

| Rule | Source |
|---|---|
| Masters are exported silent (plus a guide-audio copy for sync checks); the song is attached inside each app: TikTok library sound, Instagram music library, Shorts audio picker. Baked-in audio gets no sound page on TikTok and is not reliably matched on Instagram | [OFFICIAL] TikTok base file, YouTube Help 18736733; [REPORTED] Instagram audio matching; research-clip-pack change 3 |
| The TikTok clip start is chosen first; the hook bar and every TikTok cut sit inside that 60 s window | "The duration of the clip we send to TikTok is 60 seconds long" [OFFICIAL, Symphonic via search index]; change 2 |
| 60 s is the ceiling for every shared cut: TikTok's library cap, and any Short over one minute with an active Content ID claim is blocked. Most cuts 8 to 20 s (our average watch is about 6 s) | [OFFICIAL] YouTube music eligibility for Shorts; [OUR DATA] reel-craft; change 4 |
| The audio hook is fixed per song; the first frame changes per post. Same sound, different picture | YouTube pre-release guide: one audio snippet for all pre-release content [OFFICIAL]; Instagram matches identical content by audio-visual signals [OFFICIAL]; change 1 |
| Never the same cut twice on one platform. `used_in` refuses a second `post` or `trial` of one cut label on one platform. Reuse goes to Repost (IG, TikTok), Replace audio (IG posts and carousels) or a new cut from the same footage | Instagram: when it finds two or more identical pieces it recommends only the original [OFFICIAL, originality page]. TikTok: For You ineligible "if it includes unoriginal or reused material without anything new" [OFFICIAL, Community Guidelines 2026-09-24]; change 5 |
| The same clean file of his own on Reels, TikTok and Shorts: no official page penalises it; the official penalties are visible watermarks and other people's work | Pages are silent on own cross-posts [OFFICIAL, silence]; Mosseri 2026-10-30: other-app edits not demoted, only watermarks [REPORTED]; research-clip-pack section 1 |
| TikTok frame one must also read silent (a text line or motion): over 30% of TikTok viewers watch muted vs over 75% of Reels views with sound on | [OFFICIAL] TikTok Creator Academy base file, Meta developer blog; section 2 |
| Text and face inside the union of the three safe zones: top 288, bottom 672, left 65, right 192 px on 1080x1920 | [REPORTED] ad specs, union is [JUDGEMENT]; section 2 |
| No AI images on TikTok; realistic AI content must carry the AI label | Community Guidelines in force 2026-09-24 [OFFICIAL]; platform plan TikTok row |
| No engagement automation on TikTok | Guidelines ban it; a ban reportedly reaches linked accounts [OFFICIAL / CLAIMED, research-tiktok section 4] |
| Trial Reels are the hook test on Instagram: one build, 2 to 3 first-frame variants shown to non-followers first | [OFFICIAL] Trial Reels; content-language experiment 5; change 6 |
| Spotify Canvas is its own object: footage in and out, 3 to 8 s, not a song timecode. Spotify Clips are closed to new uploads since 2026-06-17, no Clips field | [OFFICIAL] Canvas guidelines, Clips page; changes 7 and 9 |

Three Symphonic questions are open and block three fields (clip-pack schema): Shorts Previews on
Starter, more than one TikTok clip per track, Content ID whitelist for his own channel. Until the
answers, `shorts_preview` stays empty, there is one TikTok start per track, and every shared cut
stays at 60 s or under.

TikTok posting rhythm while a content round runs: 2 to 3 posts a week, the same clean files as the
Reels, the library sound picked in the app on every post with his music [research-tiktok section 4;
platform plan]. Go or no-go after 8 weeks of posting, measured on both paths: videos by others per
sound and own-account reach and saves, never views alone [research-tiktok checkpoint; MIDiA 26% vs
45% follower-to-listener, REPORTED].

Review flow: every file that goes out (render, cover, caption, post draft, Canvas) is approved by
Amir by hash on RM `/review` before posting. A file that changes after approval falls back to
needs-you; a new version is a new item, approval never carries over
(`plans/review-flow-schema.md`). The agent writes files and records; it never posts, moves or
approves.

---

## 6. One job per platform

From `plans/strategy/platform-plan-songs-2026-11-05.md` (approved by Amir 2026-11-06, D5) and the
"Platform jobs" section of `docs/brand/positioning.md`. Counts are the 2026-11-05 baseline [OUR DATA].

| Platform | Job | What we do per single | What we do not do | What we measure |
|---|---|---|---|---|
| Spotify (68 followers) | Hold the fans: a follow puts every new song in their Release Radar, unless they filter it [OFFICIAL, filters since 2026-07-10] | Pitch on delivery day; Artist Pick and Canvas; aim at the Verified badge (sustained listener engagement, good standing, real-world signals such as concerts, merch and linked socials, human review) [OFFICIAL + REPORTED, 2026-04-30] | Two pitches at once; any stream or "guaranteed placement" service (artificial streams earn nothing and can cost placement [OFFICIAL]); Countdown, Marquee, Discovery Mode (section 8) | Followers; day-28 Release engagement; Release Radar adds in S4A |
| Amazon Music | Second editorial door, free | One track pitched per release in Amazon Music for Artists, Owner or Admin, by T+14 [OFFICIAL] | Edit after submit (not possible) [CLAIMED, Ditto] | Whether the pitch landed, read in Amazon Music for Artists |
| Bandcamp (51 followers, 16 on the list) | The owned, paying core and the email list | Private draft at T-8 with the Bandcamp Daily pitch; release on a Bandcamp Friday when it fits; mailing list sign-up at every release and gig | Use another platform's link in the Bandcamp Daily pitch [OFFICIAL] | Followers; email list; sales per release |
| Instagram (about 969 followers) | Bring traffic: the face, the process, the first hours of each release | Teaser reel at T-4; release-day reel with face or hands; Music on Profile and notifications per song; one peer collab per song, started by the bigger account; Trial Reels as the hook test | A date card as the release reel; cold DMs from the agent (collab requests are drafted for Amir to send himself) [content-language experiment 3] | Views per follower vs 0.77x; non-follower share; sends; profile visits and follows per release |
| TikTok | Exposure: let others use the sound, and post our own raw work | Account open with the first single (D8), certified with a delivered track; the 60 s clip start per song; the same clean cuts as the Reels, 2 to 3 a week while a round runs | AI images; engagement automation; judging on views | Videos by others per sound; own-account reach; Add to Music App saves; Spotify followers the same week |
| YouTube (count not in the sources) | Carry the video: one finished official video per single, Shorts Previews before it | One performance or studio video per single (also the Spotify video pitch); Shorts Previews from about T-14 if Symphonic delivers them; chase the Official Artist Channel | A Short over 60 s with the song before the Content ID answer [OFFICIAL]; teaser and "out now" Shorts as the main piece (they sit at the bottom on 13 scene channels [SEEN]) | Views on the official video vs channel size; Shorts to song-page clicks; subscribers |
| SoundCloud (470 followers, electronic seeds) | Home of the electronic lane; a side door for the songs | One follower-only early drop per single (Artist Pro), direct upload, then public and Amplify inside 14 days | Deliver the song to SoundCloud via the distributor; count SC followers as songs-lane fans [research-listening-platforms change 7] | Follows gained from the gated drop; plays in the first 14 days; Amplify result |
| Email (16 subscribers) | The only audience no feed can filter | Buttondown (free to 100, EU double opt-in); sign-up link in bios and on every release page; one welcome mail once; one mail per release | A newsletter; a second mail per release | List size; opens per mail |

No platform is the engine; the song is. Exposure may come from TikTok or Instagram; it has to land
on Spotify and the email list [platform plan, short answer].

---

## 7. Press, radio, curators per single

The songs ladder from `research-pitch-2026-11-05.md` section 5 and change 5. Pitches cannot go out
before the positioning switch (`positioning.md` PUBLIC STATUS), so the switch date sets the press clock.

| Route | When | Cost | Tag |
|---|---|---|---|
| Bandcamp Daily | T-8 weeks, Bandcamp draft link, tell a story | Free | [OFFICIAL] |
| Side-Line | News: the day before or on release day, max 2 days ahead; genre in subject and first line; one follow-up after a week | Free | [OFFICIAL] |
| FluxFM Radar (Berlin) | Around release; they reply only if it fits | Free | [OFFICIAL] |
| WhiteLight//WhiteHeat weekly tips column | Route not stated; contact page only | Unknown | [OFFICIAL page, route gap] |
| ByteFM Anstoss | Status unverified; check alive first | Free | [CLAIMED / REPORTED] |
| Berlin community radio hosts (Refuge, Cashmere) | Through hosts we know, not a form | Free | [OFFICIAL] |
| Post-Punk.com premiere | Paid or "donation" per lead time | Paid | [OFFICIAL]; counts as the one paid route under D9, so only inside the EUR 50 cap |
| BBC Introducing | Not for us (UK postcode) | n/a | [REPORTED] |

Curators, order per release: people we know (prior add or chat), then curators with a free public
route, then a capped paid test judged on Spotify adds and saves at day 28, then nothing. Cold IG
DMs land in Requests with links stripped [OUR DATA, release-lessons via research-pitch section 4].
Spotify on paid "consideration" services: "Be highly skeptical" [OFFICIAL].

**Paid promotion rule (D9, Amir, 2026-11-06: option A).** Per release, in this order: people we know,
free routes, then at most one paid route at EUR 50 or less (a curator service or a premiere; a premiere
above EUR 50 is out). The paid route stays in the plan only if Spotify adds plus saves at day 28 beat the
last unpaid release's day-28 read; if not, the next release runs unpaid. Premieres (Amir, 2026-11-06:
"mainly one route, B is an option, for now 50 EUR"): a premiere is the one paid route for now, so the
ladder's fees sit under the EUR 50 cap. A separate premiere on top, up to EUR 80, stays an option
he may switch on later; it is not the rule today.

---

## 8. What leaves the plan and why

| Tool | Why it leaves | Comes back when |
|---|---|---|
| Spotify Countdown Pages | 3,000 monthly active listeners, albums and EPs only, singles not eligible [OFFICIAL, research-pitch row 7] | The album, if the listener count is there |
| Spotify Marquee and Showcase | Marquee 5,000 monthly active listeners; Showcase 1,000 streams in 28 days in one market [OFFICIAL, row 6] | The thresholds are reached; re-check in S4A each release |
| Spotify Discovery Mode | About 25,000 listeners per blogs; official page not reachable; 30% commission [CLAIMED, row 5] | Not in reach; re-check when an official page exists |
| Apple Music editorial pitch | Apple Music Pitch is for Connect Admin or Marketing Manager roles; Symphonic Starter does not pitch [OFFICIAL / REPORTED, row 8]. Keep the Apple Music for Artists profile complete | A plan or distributor that pitches |
| Deezer and YouTube Music pitch | Labels and distributors only; no public YouTube Music form [CLAIMED, row 10] | Nothing to do on Starter |
| Spotify Clips | Closed to new uploads since 2026-06-17 [OFFICIAL] | Never; video pitch replaces it |
| Beatport-driven 8-week rule, "3 EPs a year" | The songs do not use Beatport; the 8 weeks now belong to Bandcamp Daily [OFFICIAL, row 16] | Electronic lane only, see the Beatport variant |
| Paid curator listens and paid premieres above the cap | D9: one paid route per release, EUR 50 cap, kept only on a day-28 win | Amir, 2026-11-06 |

---

## 9. The album rule

The album collects the singles: the same recordings, the same ISRCs, so the streams stay on each
song and keep counting toward the 1,000 streams in 12 months per track [derived from the OFFICIAL
royalty rule and the waterfall practice, research-pitch section 2 and change 3; card S3 step 1]. Re-releases and some alternate versions are excluded
from Release Radar; remixes count [OFFICIAL, research-listening-platforms 2.2], and Spotify pitches only
unreleased songs [OFFICIAL], so an album made only of the released singles has no pitch and no
Release Radar slot. The album needs at least one song that was never a single (section 10). The album is
the first release that can qualify for a Countdown Page if the listener threshold is met by then
[OFFICIAL]. Album reviews at Side-Line: 2 to 4 weeks before release [OFFICIAL]. Whether the
distributor keeps the ISRC on a re-delivered track inside an album: not in our research, confirm
with Symphonic before the album goes in.

---

## 10. What is still a guess

Copied in substance from the platform plan and card S3; none of these is a measured fact.

- The 4 to 8 week gap between singles: advice only, no study measures it [CLAIMED].
- TikTok as the big engine: the scene's breakouts came from other people using the sound
  [REPORTED]; own-account exposure happened once for a one-person act [REPORTED, ThxSoMch]; the
  26% follower-to-listener figure is a market average, not our number [REPORTED, MIDiA].
- Hook fatigue: a few weeks of one audio hook per song sits on the rising side of the repetition
  curve; fatigue is a risk across many weeks with the same footage, not with the same sound
  [REPORTED research, JUDGEMENT applied; research-clip-pack section 2].
- Whether Symphonic Starter delivers Shorts Previews, Spotify video and TikTok: one support ticket.
- Whether a gated SoundCloud track becomes Amplify-eligible when made public: test on a non-key
  track first.
- Whether Release Radar filters cut a small artist's follower reach: effect unknown [OFFICIAL that
  filters exist; no data].
- Whether the teaser reel can use the song as named audio before release depends on the song
  being in the Meta library by T-4; if not, Original audio [content-language experiment 8]. Whether
  Symphonic delivers to the Meta library ahead of the release date: not in our research.
- The album pitch: "8 songs = 8 singles, then an album" leaves no unreleased song to pitch the album
  with. Hold one song back for the album, or accept an album with no pitch [JUDGEMENT, Opus gate
  2026-11-06; decide before the sixth single].
- The face rule for his own reels stays [ERA] until the first songs-era round measures it
  [content-language section 4].

---

## Sources

1. `plans/strategy/platform-plan-songs-2026-11-05.md` (approved 2026-11-06, D5; Opus gate applied)
2. `docs/brand/positioning.md`, section "Platform jobs" (approved 2026-11-06) and PUBLIC STATUS
3. `plans/strategy/research-pitch-2026-11-05.md` (2026-11-05)
4. `plans/strategy/research-listening-platforms-2026-11-05.md` (2026-11-05)
5. `plans/strategy/research-tiktok-2026-11-05.md` (2026-11-05) and
   `plans/strategy/research-clip-pack-2026-11-06.md` (2026-11-06)
6. `plans/strategy/research-content-language-2026-11-05.md` (2026-11-05) and
   `plans/strategy/gates/2026-11-05-content-language.md` (Fable gate, approve with fixes)
7. `plans/activation-messages-2026-11-06.md` (drafts; Amir approves texts in the main chat before use)
8. `plans/clip-pack-schema.md`, `plans/review-flow-schema.md`, `plans/release-day-playbook.md`
   (mechanics; built 2026-11-06, 2026-11-06 and 2026-05-16)
9. `plans/strategy/refresh-page/index.html`, card S3 (Batch 4) and decision D9 (answered 2026-11-06: A)
10. `plans/targets.json`, `release_engagement_d28` schema (D4, 2026-11-05)

Electronic lane: see `inch-of-shadow-release-guide.md` (Beatport variant). Next electronic drop:
the Half the Night EP on Indigo Children Records, date open, not released.
