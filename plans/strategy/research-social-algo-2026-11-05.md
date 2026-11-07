# Social algorithm research, 2026-11-05 (Instagram + YouTube)

Text-only web research, all links seen 2026-11-05. Builds on `review-2026-11-05-research.md` (same day).

Tags:
- **[OFFICIAL]** Meta/Instagram/YouTube's own page, help centre, earnings call or an executive on record.
- **[REPORTED]** a named outlet quotes an official source we could not open ourselves (Instagram's help centre and Meta policy pages render empty for our tools).
- **[CLAIMED]** vendor, agency or blog number with no published method. Directional at best.
- **[MYTH]** circulating claim with no source, or contradicted by an official one.

No Wikipedia. No raw pages or PDFs saved. No downloads happened in this pass, so nothing needed moving to the Trash.

## Top table: what we believe now vs what is true now

| What we believe now (file:line) | What is true now (source) | Change? |
|---|---|---|
| Trial Reels need 1,000 followers, "31 to go" (`plans/strategy/review-2026-11-05-research.md:34`, `:62`; `plans/platform-algorithm-research-2026-06.md:53`) | Help centre text, quoted by several sites: professional accounts need **200** followers, personal accounts 1,000; the account must be public and eligible for recommendations [REPORTED] (Junibloom 2026-11-04, Flowgent 2026-10-29). We are a Creator account at about 969. | **yes** |
| Reels should stay under 90 s to reach non-followers (`plans/platform-algorithm-research-2026-06.md:50`) | Reels can be up to 20 min; over 3 min "won't be recommended to new audiences" [REPORTED] (help-centre line quoted by createsocial.ai, tryunlockdm). `docs/ig-settings-2026.md:16` already says 3:00. | **adjust** (June doc only) |
| Top 3 signals are sends, watch time, **saves**; "likes are the weakest signal" (`plans/ig-engagement-strategy.md:52-58`) | Mosseri names watch time, likes per reach, sends per reach; likes matter most with followers, sends with non-followers [OFFICIAL, Mosseri 2025-01 and 2026-05-26 per `mosseri-guide.md:29`]. Saves are not on his list. | **yes** (doc wording) |
| Setting "Your Algorithm" topics on @inch_of_shadow "directly affects who Instagram routes your content to" (`plans/ig-engagement-strategy.md:60-64`, `:435`) | Your Algorithm changes what **the viewer** sees (Reels Dec 2025, Explore Apr 2026, Feed Jun 2026) [OFFICIAL, about.instagram.com; REPORTED dates]. Nothing says it changes who sees **our** posts. | **yes** ([MYTH] as written) |
| "10+ reposts in 30 days = excluded", "smaller creators get an Explore boost", "one strong reel adds 50-100 followers" (`plans/ig-engagement-strategy.md:70-73`) | Rule is "mostly other people's content" over the account's mix, extended to photos/carousels 2026-04-30 [OFFICIAL, Mosseri via PetaPixel]. No fixed count. No small-creator boost is official. 50-100 is unsourced. | **yes** ([MYTH] numbers) |
| Action-block ladder 24-72 h, 7 days, suspension, ban (`plans/ig-engagement-strategy.md:138-147`) | No Meta source publishes a ladder or limits. The official mechanism we can see is **recommendation eligibility** in Account Status [OFFICIAL]. | **adjust** (label as unsourced, add eligibility) |
| Trial reels: "up to 25 a day" unverified (`docs/brand/reel-craft.md:95-97`) | Creators report a limit and a block of up to 30 days on new trials when over it; normal reels still work [REPORTED/CLAIMED, Threads post 2026-04-13, ytviews.in]. No official number. | **adjust** |
| Instagram leans into long video, clips drive the full piece (`docs/brand/mosseri-guide.md:97`) | Confirmed and concrete: "Features", horizontal up to 90 min, US test from 2026-10-26, plus "Clips as Reels" linking up to 8 reels to one full video [OFFICIAL Mosseri/Tessa Lyons via TheNextWeb, TechRepublic]. Not in Germany yet. | **no** (watch only) |
| Release news goes out on the day, system reacts within hours (`docs/brand/mosseri-guide.md:32`) | Stronger now: nearly 45% of recommended Reels are under 1 day old (+11 pts since Q2); Reels are ranked as **sequences** [OFFICIAL, Meta Q3 2026 call, 2026-10-21]. | **no** (confirmed, raise weight) |
| Hashtags max 5, keywords in captions (`docs/ig-settings-2026.md:19`, `plans/platform-algorithm-research-2026-06.md:57-60`) | Unchanged. Google indexing of pro-account posts since 2025-07 [REPORTED]; Google Search Console added Instagram properties July 2026 [REPORTED, keywordseverywhere citing Google Search Central]. | **no** |
| Shorts before release day must carry their own audio; official sound only from release day (`youtube/PLAYBOOK.md:302-308`) | YouTube "Previews": a song clip available on Shorts **before** release, Shorts move to the song page, fans get a "Notify me" button [OFFICIAL, artists.youtube pre-release page]. Delivered by the distributor (FUGA documents it per track) [OFFICIAL vendor doc]. Symphonic support not confirmed. | **yes** (ask Symphonic) |
| Shorts: "first frame beats a custom thumbnail" (`youtube/PLAYBOOK.md:314`) | Custom Shorts thumbnails rolled out July 2026, reportedly YPP channels first, desktop Studio [REPORTED, outlierkit citing Creator Insider IsoUDk7m3yA]. We are not in YPP, so likely not available yet. | **adjust** |
| YPP: 1,000 subs + 4,000 h or 10M Shorts views (`youtube/PLAYBOOK.md:436-441`) | From 2027-02-01 new entrants need 1,000 subs + **8,000** h or **20M** Shorts views; fan-funding tier unchanged (500 subs + 3,000 h or 3M Shorts) [OFFICIAL, YouTube Help 12843009]. | **adjust** |
| Shorts "originality push 2026-10-01" (`youtube/PLAYBOOK.md:340`) | Confirmed: re-uploads lose reach, own clips are fine; narration over others' clips is not original [OFFICIAL TeamYouTube post, Rene Ritchie on Creator Insider, via outlierkit/artvoice]. Helps us. | **no** |

## 1. Instagram ranking changes, Jun-Nov 2026

**Ranking core (unchanged)**
- Separate ranking per surface (Feed, Stories, Reels, Explore), each split into followers vs recommendations. Most reach now comes from recommendations [OFFICIAL, Mosseri 2026-10-23 on political content, via metricool roundup].
- Named signals: watch time, likes per reach, sends per reach; plus originality, recency, "breaking content" [OFFICIAL, Mosseri 2026-09-09, see `mosseri-guide.md`]. "Sends are 3-5x a like" stays [MYTH] (keywordseverywhere tracker, Nov 2026).
- New Insights fields: share rate, skip rate, views over time [REPORTED, Pepper Agency 2026-10-19].

**Freshness and sequences** [OFFICIAL]
- Meta Q3 call, 2026-10-21: nearly 45% of recommended Reels under 1 day old, up 11+ points from Q2; a new model ranks **sequences** of Reels instead of each one alone, live on about half of Reels views; Reels time spent +4% from Q3 relevance launches. https://www.fool.com/earnings/call-transcripts/2026/10/21/meta-meta-q3-2026-earnings-call-transcript/ ; https://www.buzzincontent.com/news/nearly-half-of-recommended-instagram-reels-are-now-under-a-day-old-12716537
- Meaning for us (hypothesis): the first hours of a reel matter more than before; a reel that stalls on day 1 is unlikely to be rediscovered.

**Trial Reels**
- Eligibility: professional 200 / personal 1,000 followers, public, recommendable; "If your public account is ineligible to appear in recommendations, you will also lose access to trial reels" [REPORTED, help-centre text quoted]. https://www.junibloom.com/blog/instagram-trial-reels-0-views (2026-11-04) ; https://flowgent.ai/blog/instagram-trial-reels (2026-10-29, cites help.instagram.com/1013292530224018)
- Scheduling of trials since 2026-04-02 [OFFICIAL, Mosseri via Social Media Today]. https://www.socialmediatoday.com/news/instagram-allows-creators-to-schedule-trial-reels/816549/
- A cap on trials with a block of up to 30 days when exceeded [REPORTED/CLAIMED]; "about 5 a day" [CLAIMED]. https://www.threads.com/@theahmedghanem/post/DXET84SDDjQ ; https://www.ytviews.in/instagram-trial-reels-2026-rules/
- Auto-share if it does well in 72 h [OFFICIAL, creators.instagram.com/blog/instagram-trial-reels].

**Your Algorithm** [OFFICIAL feature, REPORTED dates]
- Reels Dec 2025, Explore April 2026, main Feed 2026-06-10; tests of making it central (pull-down, buttons under Reels) 2026-06-27. Viewer-side control only. https://about.instagram.com/blog/announcements/reels-algorithm-control ; https://thenextweb.com/news/instagram-your-algorithm-central-experience-mosseri ; https://keywordseverywhere.com/news/instagram-algorithm-updates/
- Implication: viewers can now type topics in. Clear genre words in caption, on-screen text and audio name help us get classified into topics people pick (hypothesis).

**Originality and AI**
- 2026-04-30: accounts that mostly post others' content lose recommendations, now incl. photos and carousels [OFFICIAL, Mosseri via PetaPixel]. https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/
- 2026-08-31: profiles featuring an AI-generated person must carry "AI-generated profile" or lose recommendations. Using AI tools for edits/graphics does not need the label [REPORTED, Instagram for Creators via TechRepublic]. https://www.techrepublic.com/article/news-instagram-ai-generated-profile-label-recommendations/ . Not us, but our AI covers must never present an AI person as him.
- 2026-10-30: Mosseri again: other-app edits are not demoted, only watermarks [REPORTED, metricool roundup].

**Length**
- Upload up to 20 min; over 3 min not recommended to new audiences [REPORTED help-centre line]. https://createsocial.ai/blog/how-long-can-instagram-reels-be
- "Features" 90-min horizontal, US test only, from 2026-10-26 [OFFICIAL]. https://thenextweb.com/news/instagram-tests-90-minute-horizontal-videos-called-features

**Carousels and music on posts**
- Music on a photo/carousel usually raises reach because the post becomes eligible for the Reels viewer, not because of a boost [REPORTED, Mosseri Aug 2026 Q&A]. https://kompozy.io/guides/instagram-reach-expansion-features-2026 ; https://www.kontentino.com/q-and-a/add-music-to-instagram-post-reach/
- "Replace audio" on already-published posts and carousels, keeps likes/comments, from about 2026-07-21 [REPORTED, Music Ally quoting Instagram]. https://musically.com/2026/07/22/instagrams-latest-feature-swaps-new-music-into-old-posts/
- Up to 20 slides (date disputed, 2024 or 2026) [REPORTED].

**Edits app**
- Carousel editor, AI video generation, audio loudness match, 200+ SFX, bilingual captions; desktop "no date" (Mosseri, Aug 2026) [REPORTED]. Using Edits helps reach "a little" [CLAIMED, newsletter quote, no primary clip]. https://embedsocial.com/blog/new-instagram-features-2026/

**Paid layer (new)**
- Instagram Plus $3.99/month (story first in trays), 2026-06-04 [OFFICIAL, via keywordseverywhere].
- Meta One, 2026-09-15: creator tiers from $14.99; Advanced $49.99 adds **links in organic posts and Reels** (4 posts + 4 reels a month), a bold follow button on Reels and automatic follow invitations to people who engage [OFFICIAL, Meta Newsroom; caps REPORTED from Meta help]. UK CMA is looking into it [REPORTED]. https://about.fb.com/news/2026/09/introducing-meta-one-subscription-service-more-features-ai/

**Threads crossover**
- Cross-posting to Threads is opt-in ("Always share posts") [OFFICIAL, Mosseri 2025 Q&A]. No 2026 data that it helps or hurts Instagram reach. https://www.kontentino.com/q-and-a/common-questions-about-instagram-threads-facebook/

**Myths flagged this pass:** "July 2026 update added skip rate as a signal", "2026 Year of Raw Content algorithm shift", "shadowban update", "original content gets 40-60% more" [MYTH] (keywordseverywhere tracker). Podswap/Hypebot numbers: shares 4x likes, raw +35%, location tags +215%, Monday best [CLAIMED]. https://www.hypebot.com/cracking-the-instagram-algorithm-a-2026-guide-for-musicians/

## 2. Follow/unfollow + like automation in 2026 (facts only)

No change to the engagement automation is proposed here. Facts:

- Instagram has said since 2018 that third-party apps generating likes, follows and comments break its Community Guidelines and Terms, that it removes such activity with machine learning, and that accounts that keep doing it "may see their Instagram experience impacted" [OFFICIAL, old]. https://business.instagram.com/blog/reducing-inauthentic-activity-on-instagram
- Meta's Inauthentic Behavior policy covers "inauthentic engagement" and "inauthentic audience building" [OFFICIAL, policy page; text read via search snippet only]. https://transparency.meta.com/policies/community-standards/inauthentic-behavior
- Meta, 2025: action on about 500,000 accounts for spammy behaviour or fake engagement, with demoted comments and reduced distribution (Facebook focus) [REPORTED]. https://tribune.com.pk/story/2555997/meta-moves-to-curb-ai-driven-unoriginal-content-on-facebook
- The visible penalty is **recommendation eligibility**: an ineligible account still reaches followers but not Explore, Reels, Search, Suggested accounts or Feed recommendations, and loses Trial Reels [OFFICIAL concept, REPORTED wording]. https://www.awarexone.com/research/instagram-not-eligible-to-be-recommended
- May 2026 follower drops ("bot purge"); Meta called it routine inactive-account removal [REPORTED]. https://dontfollowback.com/blog/2026-05-06-instagrams-2026-bot-purge-why-celebrities-and-influencers-suddenly-lost-millions-of-followers
- The only published follow limit is 7,500 total following [OFFICIAL, help centre via socialrails]. Daily limits (20-200/day) are [CLAIMED] and conflict. Strike ladders with 14-30 day reach cuts [CLAIMED, no Meta source].
- Meta now sells its own follow mechanics (bold follow button, automatic follow invitations, Meta One) [OFFICIAL]. It shows Meta wants follows from engagement, through its tools.
- No 2026 independent study measures follow-back rates or reach effects of low-volume follow/like automation. Gap, not evidence either way. Our own numbers (22% follow-back; "reach does not turn into follows", `reel-craft.md:50`) remain the only data.
- What to watch, manually: Account Status "can be recommended". If it ever flips, Trial Reels go with it.

## 3. What works for small musicians launching songs on IG (2026)

- **Music on Profile + New Music Notifications** [REPORTED, Meta announcement after 2025 test, March 2026]: add a pre-release teaser or a new track to the profile and send an in-app alert to top fans; teasers before release, tracks within 7 days after; up to 4 songs per 30 days, 3-day cooldown. Needs the track in Meta's music library via the distributor. https://imusician.pro/en/resources/blog/instagram-unveils-new-music-notifications ; https://www.absolutelabelservices.com/news/promoting-your-music-on-instagram
- **Own song on carousels and photos** for Reels-viewer eligibility, and **replace audio** to put the new single onto older posts [REPORTED, above].
- **Collabs**: the initiating account matters most for reach; collabs can be added after posting [OFFICIAL, Mosseri 2025-11-18]. YouTube's internal Feb 2026 study: collabs with similar-size creators +25% views, slightly smaller +60% over the first weeks [OFFICIAL, YouTube's own claim, artists.youtube]. Peer-size collab is the best-evidenced lever we have for a small act.
- **Tagged posts on the grid** (fan/venue posts added to the profile) [REPORTED, Sept 2026].
- **Stories**: everyday raw sharing; replies open a DM; question sticker [OFFICIAL, Mosseri]. Spotify-shared story stickers show "Open on Spotify" [OFFICIAL, Spotify newsroom]. Link sticker remains the free link.
- **Broadcast channels**: one-way to opted-in followers; 1.5B messages a month on Instagram (Dec 2024) [REPORTED]. No data on small artists. Value is retention, not reach [CLAIMED].
- **Live boost** from the live composer [REPORTED, Hypebot].
- **Performance and process clips**: no 2026 study with method. "Raw phone-shot beats studio by 35%" [CLAIMED]. Mosseri's "rawness is proof" [OFFICIAL, 2025-12-31]. Our own data: process beat announcement [OWN].
- Frequency: Buffer 2025 correlation (3-5/week grows faster) [CLAIMED, large sample]; Mosseri: a pace you can keep [OFFICIAL].

## 4. YouTube 2026

**Engine**
- Shorts and long-form remain separate systems. Recommendations are pulled per viewer at session start; nothing is "pushed" at upload [OFFICIAL, Todd Beaupré, Creator Insider 2026-09-01, https://www.youtube.com/watch?v=rHLjxrbXmmY , summary REPORTED]. A weak video does not hurt the channel [OFFICIAL, Beaupré].
- 2026-10-01 Shorts originality: re-uploads lose reach, own footage fine [OFFICIAL via TeamYouTube/Ritchie]. https://outlierkit.com/resources/youtube-shorts-original-content-update/
- 2026-08-24 public views count from first frame, "engaged views" in Studio [OFFICIAL, YouTube blog via outlierkit]. Playbook already uses this.
- Shorts: dislike removed (2026-06-25) [REPORTED]; custom thumbnails (July 2026) [REPORTED, likely YPP-first]; Shorts Series (seasons/episodes, autoplay) from Made on YouTube 2026-09-23 [OFFICIAL]; custom feeds for US viewers 2026-10-22 [OFFICIAL]. Changelog: https://outlierkit.com/resources/youtube-algorithm-updates/
- Spam test 2026-10-29: 30-day lock instead of termination for some spam violations [OFFICIAL test].

**Artist tools**
- Pre-release page (artists.youtube, read 2026-11-05): Shorts **Previews** + "Notify me", one shared audio snippet if no Preview, trailer about 2 weeks before as featured video and Premiere trailer, Premiere with reminders, Community posts with countdowns and polls, pre-save link, playlist for the release [OFFICIAL]. https://artists.youtube/resources/pre-release-strategy/
- Previews are switched on per track by the distributor/aggregator [OFFICIAL vendor doc, FUGA]. https://support.fuga.com/hc/en-us/articles/39581419161748-YouTube-Shorts-Previews-Getting-Started
- YouTube Music release countdowns, album pre-saves, fan drops: "trusted tester" phase since Sept 2025 [OFFICIAL via MBW]. Not for us yet. https://www.musicbusinessworldwide.com/youtube-music-launches-new-tools-to-connect-artists-with-superfans/
- OAC: still distributor-only. Our request (2026-09-08) is now 2 months old vs "~1 month" quoted (playbook:29). Worth a chase.
- YPP from 2027-02-01: 8,000 h or 20M Shorts views for new entrants; Shorts creator-pool earnings need 10M Shorts views per 90 days [OFFICIAL]. https://support.google.com/youtube/answer/12843009?hl=en . Monetisation is out of reach either way; Hype needs YPP, so Hype stays out of reach.

**What works for a small artist channel** [OFFICIAL unless tagged]: official video on release day, Shorts with official audio tied to the video, Premiere, featured video, Community post; collabs (+25/60%). Our own data: 94% non-subscriber views, 0 subs gained from the catalogue [OWN].

## 5. Things in 2026 that make our docs wrong (summary)

1. Trial Reels threshold: 200 for Creator accounts, not 1,000. (3 files.)
2. `ig-engagement-strategy.md` Part 1: saves as a top-3 signal, "likes weakest", "Your Algorithm routes our content", "10+ reposts", "small-creator Explore boost", "50-100 followers per reel": unsupported or wrong.
3. June research "under 90 s": now 3 min.
4. Action-block ladder: unsourced; the real, visible risk is recommendation eligibility.
5. YouTube playbook: pre-release Shorts audio has an official path (Previews); Shorts custom thumbnails now exist (for YPP first); YPP table needs the 2027 numbers.
6. `reel-craft.md` trial reels: a reported 30-day block if over a cap replaces "25 a day".

## Recommended strategy changes (max 8)

**1. Start Trial Reels now, not at 1,000**
- Was: wait for 1,000 followers (31 to go).
- Change to: check the Trial toggle in the app this week; if present, every new reel's first post is a trial with 2-3 hook versions (formats.md object 4).
- Based on: help-centre text, 200 for professional accounts [REPORTED].
- Why: hook testing on strangers is our weakest point (2 s drop-off) and needs no follower growth.
- Steps: 1) open a new reel in the app, look for "Trial"; 2) if missing, check Account Status and app version; 3) set the win bar before posting; 4) stay well under any cap (2-3 trials a week) to avoid the reported 30-day block.
- Lane: both.

**2. Make recommendation eligibility the risk metric, not only action blocks**
- Was: risk = action-block ladder (`ig-engagement-strategy.md:138-147`).
- Change to: a weekly manual look at Account Status "can be recommended", logged with the session report. No code change.
- Based on: eligibility is the official penalty surface and Trial Reels depend on it [OFFICIAL/REPORTED].
- Why: losing it would quietly kill non-follower reach and trials right when the songs launch.
- Steps: Amir or the IG agent reads Account Status weekly; if it ever shows "can't be recommended", stop and tell Amir.
- Lane: both.

**3. Correct the algorithm section of the engagement strategy doc**
- Was: saves top-3, likes weakest, "set Your Algorithm on our account to route our content", 10+ reposts rule, 50-100 followers per reel.
- Change to: Mosseri's list (watch time, likes per reach, sends per reach, originality, recency); Your Algorithm is viewer-side; drop unsourced numbers. Doc text only, needs Amir's yes because the file sits next to the automation.
- Based on: sources in section 1 [OFFICIAL].
- Why: the agents read this file; wrong beliefs leak into plans.
- Steps: propose the edit as a ticket; Amir approves; one-line note in TICKETS history.
- Lane: both.

**4. Release-day first hours as the main IG event**
- Was: release reel winner "on release day", no hour stated (`formats.md:20`).
- Change to: winner reel live in the morning of release day (Berlin), story set and collab invites the same hour, nothing else posted for a few hours around it.
- Based on: 45% of recommended Reels under 1 day old, sequence ranking [OFFICIAL, Meta Q3]; recency within hours [OFFICIAL, Mosseri].
- Why: day-one push now decides most of a reel's life.
- Steps: add a time field to the Release Manager release-day checklist.
- Lane: both.

**5. Use Music on Profile + New Music Notifications for every song**
- Was: not in any file.
- Change to: pre-release teaser on profile with a notification to top fans (about T-7), track notification on release day.
- Based on: Meta feature, 4 songs per 30 days, 7-day window [REPORTED].
- Why: a free in-app push to our most engaged followers, at the moment that matters.
- Steps: 1) ask Symphonic whether the song (and a pre-release teaser) reaches Meta's library before release; 2) check the option shows on the profile; 3) add to formats.md as object 12.
- Lane: songs (works for drops too).

**6. Put the new song on carousels and old posts**
- Was: carousels "feed the base" only (98% followers).
- Change to: reveal carousel (object 7) always carries the song; on release day use "replace audio" to put the single on 3-5 strong older posts.
- Based on: music makes posts eligible for the Reels viewer [REPORTED, Mosseri Aug 2026]; replace audio keeps engagement [REPORTED, Music Ally].
- Why: cheap extra surfaces for the song's sound page from posts we already have.
- Steps: after the track is in the library, pick posts with his face/process; log which posts got it.
- Lane: songs.

**7. YouTube Shorts Previews for pre-release Shorts**
- Was: pre-release Shorts carry their own audio; official sound only from release day (`youtube/PLAYBOOK.md:302-308`).
- Change to: request a Shorts Preview for each song so teasers from T-14 use the official audio with a "Notify me" button; trailer at T-14 as featured video and Premiere trailer.
- Based on: artists.youtube pre-release page [OFFICIAL]; FUGA per-track setup [OFFICIAL vendor].
- Why: closes the playbook's open question and links every teaser to the song.
- Steps: 1) ask Symphonic if Starter can deliver Shorts Previews; 2) if not, use one shared audio snippet for all pre-release Shorts (YouTube's fallback); 3) chase the OAC request (2 months, quoted 1).
- Lane: songs.

**8. Peer-size collabs as the growth lever to test**
- Was: growth from follow/like automation; collabs only as a Mosseri rule.
- Change to: one collab per song with a peer act or venue of similar or slightly smaller size, on IG (they or we start, bigger account starts) and a Short on YouTube.
- Based on: YouTube internal study +25%/+60% [OFFICIAL, YouTube's claim]; collab reach mechanics [OFFICIAL, Mosseri].
- Why: the only 2026 lever with an official uplift figure for small acts; it also fits "reach does not turn into follows" better than cold follows.
- Steps: shortlist 3 Berlin post-punk/darkwave peers from SI and the IG export; propose per release.
- Lane: songs.

Not recommended now: Meta One Advanced ($49.99/month for 4 linked reels) until the songs have a link worth paying for; Threads cross-posting (no data); Instagram "Features" (US test).
