# Listening platforms research, 2026-11-05 (SoundCloud, Spotify algorithm, Bandcamp)

Text-only web research. It builds on `plans/platform-algorithm-research-2026-06.md`, `plans/bandcamp-discovery-research-2026-10-21.md`, `review-2026-11-05-research.md` and `research-release-fans-2026-11-05.md`, and does not repeat them. Editorial pitching is out of scope here because another agent covers it.

Tags: [OFFICIAL] = the platform's own page, newsroom or exec quote. [REPORTED] = trade press (MBW, Music Ally, RA, DJ Mag, Billboard) or a secondhand report of an official source. [CLAIMED] = vendor or blog with no method. [MYTH] = repeated, and contradicted or unsupported. All sources were seen on 2026-11-05. SoundCloud's help center returned 403 to direct fetches, so SC help quotes come from search-engine snippets of those pages (marked "snippet").

## What we believe now vs what is true now

| What we believe now (file:line) | What is true now (source) | Change? |
|---|---|---|
| SC work aims at "raw follower count + ratio" so bookers see a credible profile (`docs/sc-agent-context.md:27`, `docs/sc-engagement-sop.md:19`) | SC Terms of Use (last updated 2026-01-19) ban using "bots, scripts... or other automated means" to "follow or unfollow other users" when the aim is to misrepresent popularity. The Community Guidelines also ban "Repeatedly follow large volumes of accounts in a short period of time". [OFFICIAL] See section 1.4. | Yes. Amir should make the risk decision on purpose (change 1) |
| "Likes show in 'liked by' feed: 3x discovery multiplier" (`docs/sc-agent-context.md:77`, `docs/sc-engagement-sop.md:1100`, `plans/platform-algorithm-research-2026-06.md:100`) | "Liked By" (June 2025) shows the icons of people you follow on tracks they liked, and "Liked By Your Crew" (Oct 2025) builds playlists from your follows' likes. When Amir likes a track, the boost goes to THAT track, shown to HIS followers. The "3x" number appears only in a secondhand write-up of the 2026 report; I could not find it on SoundCloud's own pages. [OFFICIAL feature, REPORTED number] | Yes. Fix the wording; the number is unverified |
| "Recent tracks (21 days or less) get boosted weight" and "Discorank" algorithm (`docs/sc-agent-context.md:76-78`, `docs/sc-engagement-sop.md:1100`) | No SoundCloud source uses "Discorank" or a 21-day rule. The nearest official rule is Amplify: tracks "uploaded or made public within the last 14 days" (help snippet). SC says 46.5% of listening goes to tracks under 18 months old. [MYTH for the name and the 21 days; REPORTED for 46.5%] | Yes. Mark it as unsourced |
| Amplify: "one shot per track", fire it from the mobile app, never at night (`docs/sc-agent-context.md:74`) | Official rules (help snippet): opt in from Artist Studio with the lightning-bolt icon. The track must be public, music, 1-10 minutes, uploaded or made public in the last 14 days, and not Go+-only. Only the first 30 uploads per day count. Eligibility is "not guaranteed" for distributor-delivered tracks. About 100 listeners first, then "up to 1,000 more" if they engage. [OFFICIAL] "One shot", "mobile" and "night" are our own lessons, not SC rules. | Small. Add the 14-day window and the distributor caveat |
| Artist Pro = "unlimited" Amplify; Artist plan $39/yr, 2 tracks a month (`plans/platform-algorithm-research-2026-06.md:108`, `:549`) | Still right. Since 2025-10-30, Artist and Artist Pro also include SC distribution to DSPs with 100% of royalties, a fan Support button with no SC cut, and vinyl/merch. [REPORTED: RA 83912, DJ Mag] In 2026, Pro got Follower Exclusive Releases (2026-03-30) and a direct-download sales beta (2026-08-26, about 200 US artists only). [OFFICIAL newsroom headlines + REPORTED] | Yes. New tools we already pay for (changes 3 and 6) |
| SC is "the primary scene platform" (`docs/sc-engagement-sop.md:19`) | True for electronic. SC's own 2026 report names hard techno, rap and "eclectic new indie" (plays up 2.5x, 89% Gen Z) as rising scenes. It does not mention post-punk, darkwave or new wave. [OFFICIAL] | Yes for songs: SC is not the songs lane's home (section 4) |
| Spotify: followers get every release in Release Radar (`plans/platform-algorithm-research-2026-06.md:156`) | Still official: followers' Release Radar gets one song per artist per week. NEW since 2026-07-10: listeners can narrow Release Radar with up to 5 filters ("Discover new artists", "Editors' picks", genres). A follower who filters may not see us. [OFFICIAL] | Yes. Follower reach is now less certain |
| Discover Weekly genre picker is the only listener control (`plans/platform-algorithm-research-2026-06.md:161`) | There are also Release Radar filters (Jul 2026), Prompted Playlists (beta, NZ Premium from 2025-12-11) and a "Large Taste Model" (Investor Day 2026-05-21). [OFFICIAL] | Context only |
| Spotify signals: saves strongest positive, early skips strongest negative (`plans/platform-algorithm-research-2026-06.md:152-153`) | Spotify's own page (updated 2026-10-23) names "searching, listening, skipping, or saving", "who you follow", plus genre, release date and "possible AI-generated content". It gives no weights. [OFFICIAL] Which signal is "strongest" is still [CLAIMED]. | Keep, but label the weights as unofficial |
| No mention of AI filtering or a verified badge in our Spotify notes | "Verified by Spotify" badge (2026-04-30). Criteria: sustained engagement, policy compliance, and real-world signals (concerts, merch, linked socials). "AI Personas" are kept out of algorithmic and editorial recommendations by default. 50M+ spam tracks were pulled from recommendations in 2026. [OFFICIAL + REPORTED] | Yes (change 5) |
| Spotify 1,000-stream royalty threshold | Unchanged since April 2024; Spotify reconfirmed it on 2026-10-20. No 2026 change found. [OFFICIAL] | No |
| Bandcamp: no personal algorithm, sales and co-purchase drive placement, Fridays Nov 6 and Dec 4 (`plans/bandcamp-traffic-plan-2026-10-21.md:15-21`) | Confirmed. Nothing new after 2026-10-21 except the EU customs fee from Nov 1, which only affects merch. Bandcamp Daily (2026-11-02) confirms Nov 6 is tomorrow and Dec 4 is the last. [OFFICIAL] | No |
| Bandcamp "berlin" tag puts you in location filter (`plans/platform-algorithm-research-2026-06.md:308`, `:328`) | Already corrected on 10-21: the filter uses profile location (`plans/bandcamp-traffic-plan-2026-10-21.md:18`). The June file still says the old thing. | Old line only, already known |

SC ratio check (from `docs/reports/sc-weekly-20261105.md`):

| | Followers | Following | Ratio | Floor | Target |
|---|---|---|---|---|---|
| 2026-08-27 | 225 | 313 | 0.72 | 1.0 | 1.4-1.6 |
| 2026-11-05 | 469 | 456 | 1.03 | 1.0 | 1.4-1.6 |

The same report counts 891 accounts "no longer following" (our unfollows over time). That figure matters for section 1.4.

## 1. SoundCloud 2026

### 1.1 What changed (dated)
- 2025-06-25: "Liked By" indicators, showing the icons of people you follow on tracks they liked. [OFFICIAL] https://community.soundcloud.com/playbook-articles/soundcloud-gets-more-social-with-new-liked-by-indicators
- 2025-10-09: social homepage. "Liked By Your Crew" is a daily list of tracks liked by people you follow. "Liked By Playlists" are opt-out. Also "Hot For You" (one track a day) and suggested follows. [REPORTED] https://musically.com/2025/10/10/soundcloud-gets-more-social-with-its-latest-discovery-features/
- 2025-10-30: "All-in-One Artist Subscription". Artist ($39/yr) and Artist Pro ($99/yr) get distribution with 100% of royalties, a Support button with no SC cut, merch and on-demand vinyl. It was applied to existing subscribers automatically. [REPORTED] https://ra.co/news/83912 ; https://djmag.com/news/soundcloud-launches-all-one-artist-subscription-plan-including-100-distribution-royalties
- 2026-01-19: Terms of Use updated (see 1.4). [OFFICIAL] https://m.soundcloud.com/terms-of-use
- 2026-02-11: Music Intelligence Report 2026. [OFFICIAL] https://soundcloud.com/company/music-intelligence-report-2026---scenes-to-watch/
- 2026-03-30: Follower Exclusive Releases (Artist Pro). A track can be gated behind a follow, for a while or for good. Non-followers see it and are asked to follow to unlock it. [OFFICIAL headline + help snippet, REPORTED details] https://www.musicbusinessworldwide.com/soundcloud-launches-superfan-feature-that-lets-artists-release-music-exclusively-to-followers-before-wider-release/ ; https://help.soundcloud.com/hc/en-us/articles/48605176658075-Follower-Exclusive-Releases
- 2026-07-22: SC buys Nina Protocol. Artists can opt in to move their catalogue. [OFFICIAL headline]
- 2026-08-26: Direct download sales beta, zero SC commission, about 200 US Artist Pro creators with Fan Support on. A wider rollout was promised "later this fall"; I found no confirmation that it has happened. [REPORTED] https://www.musicweek.com/digital/read/soundcloud-launches-direct-to-fan-sales-with-zero-commission/094833
- 2026-10-21 and 2026-11-05: AI partnerships (Moises, ElevenMusic). No artist-facing discovery change. [OFFICIAL headlines] https://soundcloud.com/company/newsroom/

### 1.2 Amplify (the old First Fans)
- The rules are in the top table. [OFFICIAL, help snippet] https://help.soundcloud.com/hc/en-us/articles/16680415453979-Amplify-tracks-to-reach-100-listeners
- "Up to 1,000 more" listeners, and top tracks can reach Buzzing playlists, comes from SC's promo and Buzzing pages, not the Amplify article. [OFFICIAL marketing] https://soundcloud.com/getstarted/getheard/ ; https://help.soundcloud.com/hc/en-us/articles/45800800476699-SoundCloud-s-Buzzing-Playlists
- SC "cannot guarantee" Amplify for tracks delivered through a distributor. If a songs-lane track reaches SC via Symphonic instead of a direct upload, Amplify may not apply. [OFFICIAL, snippet]

### 1.3 Fan-powered royalties and money
- Fan-powered royalties: any artist who monetises through SoundCloud for Artists is in automatically, with no minimum streams. Tracks must be 30 seconds to 10 minutes. [OFFICIAL, SC topic page snippet] https://soundcloud.com/topic/category/how-to-make-money-on-soundcloud/
- Per-stream rates (about $2.50-4.00 per 1,000) are [CLAIMED]. SC publishes no rate.
- Unknown for us: whether Amir's SC uploads are monetised at all (Artist Studio, monetization tab). Checking that is change 6.

### 1.4 Follow automation: what SC says
- Terms of Use (DE version, "last updated 19 January 2026"): you may not use techniques or services, "automated or otherwise", meant to misrepresent the popularity of your content, "in particular through the use of bots, botnets, scripts, apps, plug-ins, extensions or other automated means" to add followers or "to follow or unfollow other users". SC may suspend or terminate "with or without prior notice". [OFFICIAL] https://m.soundcloud.com/terms-of-use
- Community Guidelines, under "Don't do this": "Repeatedly follow large volumes of accounts in a short period of time", "Repeatedly unfollow and refollow the same accounts, in order to draw attention to your own profile", "Randomly bulk follow a large number of users". Enforcement: a written warning by email; "more than two" warnings can lead to suspension; immediate termination is reserved. [OFFICIAL] https://m.soundcloud.com/community-guidelines
- Feature blocks: following many accounts in a short time, or re-following recently unfollowed ones, can block that feature. Blocks get longer each time. There is a 24-hour limit on follow actions (number not published) and a hard cap of 2,000 followings on all plans. [OFFICIAL, help snippets] https://help.soundcloud.com/hc/en-us/articles/115003568608 ; https://help.soundcloud.com/hc/en-us/articles/115003446787-Can-t-follow-other-users
- Anti-bot: SC uses DataDome. [OFFICIAL vendor case study] Our SOP already records the 2026-05-03 CAPTCHA. https://datadome.co/customers-stories/how-soundcloud-beats-fraudulent-traffic-with-datadome-and-aws/
- No public 2026 report of a wave of SC bans for follow tools was found. "Not found" does not mean safe. [gap]
- Reading for us (hypothesis): our sessions are real Chrome clicks driven by an agent, with about 20 follows and 20 unfollows a day. In plain words that is an "automated means" to "follow or unfollow". The SOP's caps keep us under the feature-block limits; they do not make it compliant with the Terms. The 891 unfollows are what the Guidelines describe. No code change is suggested here. This is a risk decision for Amir.

### 1.5 Does SC matter for a songs act?
- SC's audience growth in its own 2026 report is rap, hard techno and Gen Z "eclectic new indie". Electronic fans are its "most engaged" (2024 report). [OFFICIAL] https://ra.co/news/81496
- MIDiA: fan-first platforms like Bandcamp and SoundCloud are "niche to superfan audiences". [REPORTED, older Q&A] https://www.midiaresearch.com/blog/midias-analysts-answer-questions-on-their-2025-predictions
- No source shows post-punk, darkwave or new wave audiences growing on SC. [gap]
- Verdict (hypothesis): SC stays the electronic lane's home. For songs it is a side door: early-access drops via Follower Exclusive, plus Amplify. The follower base the automation built is electronic-scene accounts, so it is not a songs audience.

## 2. Spotify, algorithmic side (no editorial pitching)

### 2.1 Signals Spotify itself names
- "Actions such as searching, listening, skipping, or saving to Your Library influence our interpretation of your taste", plus "who you follow", trends across users, and content traits "such as genre, release date... signals about possible AI-generated content". "Commercial considerations" can influence recommendations. Discovery Mode "increases the likelihood... but does not guarantee it". Page updated 2026-10-23. [OFFICIAL] https://www.spotify.com/us/safetyandprivacy/understanding-recommendations
- Any weights or thresholds (a "20% save rate" and similar) remain [MYTH] or [CLAIMED], as in the June file.

### 2.2 Release Radar, Discover Weekly, Radio, Shuffle, DJ
- Release Radar: one song per artist per week. A skipped song can be swapped for another from the same release. Re-releases and some alternate versions are excluded; remixes count. Results show in the song's Playlists tab in S4A. [OFFICIAL] https://support.spotify.com/us/artists/article/getting-music-on-release-radar/
- 2026-07-10: Release Radar session filters, up to 5 ("Discover new artists", "Editors' picks", genres, etc.), on mobile and desktop. It still mixes followed artists with taste picks, plus "sharper, more personalized recommendations". [OFFICIAL] https://newsroom.spotify.com/2026-07-10/discovery-playlists-release-radar-control-updates/
- Discover Weekly: genre picker (up to 5) since 2025; no 2026 change. [OFFICIAL, same post]
- Shuffle: since 2025-11-13 the default is "Fewer Repeats", and Smart Shuffle can be turned off. [OFFICIAL] https://newsroom.spotify.com/2025-11-13/shuffle-update-fewer-repeats/
- Radio and Autoplay: no 2026 change found. Discovery Mode works there for a commission; it needs about 25k listeners (see review file), so it is out of reach. [OFFICIAL for mechanics]
- DJ and Prompted Playlists: listener tools fed by the taste profile. No artist-side lever. [OFFICIAL] https://newsroom.spotify.com/2025-12-10/spotify-prompted-playlists-algorithm-gustav-soderstrom/
- "Release engagement" in S4A: the % of monthly active listeners who streamed the new release in its first 28 days. A clean metric for our own follower-reach test. [OFFICIAL] https://support.spotify.com/us/artists/article/understanding-release-engagement/
- Claims that "new releases must now earn algorithmic placement first" are [CLAIMED]; no Spotify source says so.

### 2.3 AI, spam and artificial streaming (2026)
- Spam filter (since 2025-09) targets mass uploads, near-duplicates, SEO tricks and tracks just over 30 seconds. 50M+ tracks were removed from recommendations "this year" and 75M+ from the platform. [OFFICIAL] https://newsroom.spotify.com/2026-10-20/prioritizing-human-artistry/
- AI Personas are badged and kept out of recommendations by default. [OFFICIAL, same]
- Verified by Spotify (2026-04-30): sustained listener engagement, good standing, and real-world signals (concerts, merch, linked socials), with human review. Unverified artists can be verified later. [OFFICIAL + REPORTED] https://newsroom.spotify.com/2026-04-30/verified-by-spotify-badge-artist-details/ ; https://thenextweb.com/news/spotify-verified-badge-artists-ai-excluded
- Artist Profile Protection (beta 2026-03-24, for all artists "by end of year"): approve releases before they reach your profile. Mainly for name clashes. [OFFICIAL + REPORTED] https://www.musicbusinessworldwide.com/amid-rise-of-ai-deepfakes-spotify-to-let-artists-vet-releases-before-they-appear-on-their-profiles/
- Duke Sanford study (Oct 2026): 9 undisclosed AI artists all reached new accounts through Release Radar. [REPORTED, secondary only] https://www.aimusicpreneur.com/ai-music-news/duke-sanford-spotify-ai-artists-release-radar-study-2026/
- Artificial streaming: flagged streams earn nothing, do not count, and can lose playlist placement. Since 2024-04-01, labels and distributors have been charged per track for flagrant cases. [OFFICIAL] https://support.spotify.com/us/artists/article/third-party-services-that-guarantee-streams/ ; https://artists.spotify.com/artificial-streaming
- 1,000 streams in 12 months to earn royalties (plus an unpublished minimum of unique listeners). Unchanged, reconfirmed 2026-10-20. [OFFICIAL] https://artists.spotify.com/en/blog/modernizing-our-royalty-system

## 3. Bandcamp 2026
- Ownership: still Songtradr (since 2023). No sale or restructure news in 2026. [REPORTED]
- Since our 10-21 research, the only new post is EU customs: a EUR 2 handling fee from 2026-11-01, merch only. [OFFICIAL] https://blog.bandcamp.com/
- Already known and still true: no personal feed, co-purchase recommender, the "artists you follow" Discover filter (2026-07-16), the AI ban (2026-01-13), publishing fields (2026-02-25). New Bandcamp Radio shows for electronic, indie and gaming (2026-03). [OFFICIAL + REPORTED] https://ra.co/news/84866
- Bandcamp Fridays left: 2026-11-06 (tomorrow) and 2026-12-04. Bandcamp's share is waived from 00:00 to 23:59 Pacific; processor fees stay. [OFFICIAL] https://daily.bandcamp.com/features/bandcamp-fridays
- Nothing here changes `plans/bandcamp-traffic-plan-2026-10-21.md`.

## 4. Which platform should carry fan-building for the songs lane

| Platform | What a "fan" gets you (official mechanics) | Evidence it fits sung post-punk/darkwave | Verdict (hypothesis) |
|---|---|---|---|
| Spotify | A follow means Release Radar on every release (one song a week), plus the "Release engagement" metric | Largest listening base. 2026 Loud & Clear: over a third of $10k+ earners are DIY. [OFFICIAL] No genre split. | Main fan metric for songs: followers and release engagement |
| Bandcamp | A follow brings the release email, the follow filter, listening parties; buyers feed the recommender | Editorial covers darkwave/post-punk (review file). Pays per sale. | Owned, paying core. Convert, don't discover |
| SoundCloud | A follow brings feed and notifications, follower-only drops, Liked By | Growth scenes are rap, hard techno, Gen Z indie. Electronic is the most engaged. No darkwave data. | Electronic lane home. Songs: early-access drops only |
| IG / TikTok (not in scope) | Traffic source to the three above | TikTok is the main Gen Z discovery source per MIDiA [REPORTED] | Traffic, not the fan store |

- Base: Spotify officially wires followers to new releases; Bandcamp officially wires followers and buyers to sales; SC's official growth data points away from our genre. No source compares these for a sub-1k songs act. [gap]
- So: count songs-lane fans as Spotify followers plus Bandcamp followers and emails. Count SC followers as electronic-lane reach.

## 5. What makes our current docs wrong in 2026 (short list)
1. The SC Terms (2026-01-19) name "automated means" to "follow or unfollow". Our SC docs treat detection (CAPTCHA, DataDome) as the only risk. (1.4)
2. "Discorank", "3x Liked By multiplier" and "21-day boost" are unsourced. (Top table)
3. The Amplify 14-day window and distributor caveat are missing from the SC docs. (1.2)
4. Follower Exclusive Releases, the Support button and 100% distribution are in our plan but not in our docs. (1.1)
5. Spotify Release Radar filters (2026-07) and the Verified badge (2026-04) are not in our Spotify notes. (2.2, 2.3)
6. June file lines `:308`/`:328` (Bandcamp berlin tag) are stale; already corrected in the 10-21 plan.

## Recommended strategy changes (heavy ones only)

### 1. Make the SC automation risk a conscious decision
- Was: the SC goal is raw follower count + ratio for bookers; risk = CAPTCHA/DataDome only (`docs/sc-agent-context.md:27`, `docs/sc-engagement-sop.md:19`, `:40`).
- Change to: Amir reads the two official lines (Terms 2026-01-19, Guidelines) and records a yes/no on carrying that account risk, plus what the account is worth to him (catalogue, Pro plan, 469 followers).
- Based on: SC Terms of Use and Community Guidelines [OFFICIAL]; 891 unfollows in our own report.
- Why: a ban costs the whole SC account and the Pro tools below. The CAPTCHA guards do not cover a Terms breach.
- Steps: 1) Amir reads section 1.4. 2) He decides: continue as is / continue with lower volume / pause. 3) The decision goes into the SC docs by whoever owns them. No code change is suggested here.
- Lane: both (the account carries both).

### 2. Measure SC by listening, not follower count
- Was: "raw count + ratio are the booker-facing signals" (`docs/sc-agent-context.md:27`).
- Change to: track per release on SC: plays in the first 14 days, Amplify result, likes and reposts from followers, and Bandcamp visits from `?campaign=sc-*`. Follower count becomes a side number.
- Based on: no study links follow-backs to listeners (review file, section 5); SC's own surfaces (Liked By, Amplify, Buzzing) run on listening and likes [OFFICIAL].
- Why: 469 followers matter only if they play. We do not know if they do.
- Steps: 1) Use SC Insights for the last release (The Deceiver) as a baseline. 2) Read the same numbers after the next upload. 3) Compare with follow-back cohorts.
- Lane: both, mainly electronic.

### 3. Use Follower Exclusive Releases as the SC follow converter for the songs lane
- Was: not used; SC followers come mainly from follow-backs.
- Change to: put the first song (or a demo or early mix) out as Follower Exclusive for a short window, link it from IG, then make it public and Amplify it inside 14 days.
- Based on: Follower Exclusive (Artist Pro, 2026-03-30, "follow to unlock") [OFFICIAL]; Amplify counts tracks "uploaded or made public within the last 14 days" [OFFICIAL, snippet].
- Why: these followers chose to follow for the music, so they are real fans. It costs nothing extra on Pro.
- Steps: 1) Test on one non-key track first. 2) Check by hand that a gated track becomes Amplify-eligible when made public (not confirmed). 3) Upload directly to SC, not via the distributor, so Amplify can apply.
- Lane: songs (works for electronic too).

### 4. Spotify followers + "Release engagement" = the songs-lane fan scoreboard
- Was: Spotify reach assumed via Release Radar to every follower (`plans/platform-algorithm-research-2026-06.md:156`).
- Change to: the songs-lane KPI is Spotify followers (68 now) and the S4A "Release engagement" % per release, read on day 28. Check the song's Playlists tab for Release Radar each release.
- Based on: Release Radar support page and the 2026-07-10 filters [OFFICIAL]; Release engagement metric [OFFICIAL].
- Why: followers are the only official automatic reach, but filters now make it partial, so we must measure it, not assume it.
- Steps: 1) Log day-28 release engagement for Pinocchio when it is out, as the baseline. 2) Same for the first song. 3) Use one follow-ask tool (see the release-fans file).
- Lane: songs (electronic too).

### 5. Earn the "Verified by Spotify" badge
- Was: not on our radar.
- Change to: aim the Spotify profile at the three published criteria: steady listening (not spikes), linked socials, concerts (RA events sync to Spotify), and merch if any.
- Based on: Verified by Spotify 2026-04-30 [OFFICIAL]; AI Personas excluded from recommendations; Duke study on AI in Release Radar [REPORTED].
- Why: at 94 listeners, with AI acts crowding Release Radar, a "real person" mark helps a new fan trust a sung debut. Whether the badge changes recommendations is unknown. [gap]
- Steps: 1) Check in S4A if the profile is verified now. 2) Link IG, SC, Bandcamp and any gig via RA. 3) Never use any stream service (artificial streaming rules).
- Lane: both.

### 6. Check SC monetisation and what Artist Pro already includes
- Was: Artist Pro is used for Amplify only; distribution is Symphonic Starter + Beatport add-on.
- Change to: check in Artist Studio whether SC uploads are monetised (Fan-powered royalties) and whether the Support button is on. Then compare SC distribution (100% royalties, included in Pro) with Symphonic for the songs lane only, where Beatport does not matter.
- Based on: All-in-One subscription 2025-10-30 [REPORTED: RA, DJ Mag]; FPR auto-enrolment [OFFICIAL snippet].
- Why: money may be left on SC, and we may be paying twice for distribution. Distributor-delivered tracks may lose Amplify.
- Steps: 1) Read the Artist Studio monetisation tab (by hand, his Chrome). 2) List what SC distribution covers (stores, pre-save, S4A access) before any switch. 3) No switch without his go.
- Lane: songs (the check covers both).

### 7. Keep SC as the electronic home; do not count it as songs-lane fan building
- Was: "SoundCloud is the primary scene platform" (`docs/sc-engagement-sop.md:19`), with the account goal set before the 2026-09 bridge plan.
- Change to: for songs, fan building runs on Spotify followers + Bandcamp followers/emails, with IG as traffic. SC carries the electronic lane plus the songs early-access drops (change 3).
- Based on: SC 2026 report scenes [OFFICIAL]; MIDiA on fan-first platforms [REPORTED]; Release Radar and Bandcamp follower mechanics [OFFICIAL].
- Why: the current SC follower base comes from electronic-scene seeds; growing it does not grow a songs audience.
- Steps: 1) Amir confirms the split. 2) The strategy docs name each platform's job per lane.
- Lane: both.
