# Release Day Playbook + Farewell Handoff

**Built from the Farewell release (2026-05-15).** Two parts:
- **Parts A-C, E**: reusable playbook for every future release. Work in this order.
- **Part D**: Farewell-specific status -- what is done, what is still open. For the next conversation to pick up exactly where we stopped.

When starting the next release, read Parts A-C. When continuing Farewell, read Part D.

---

## PART A: THE ORDERED PLAYBOOK

### A1. NIGHT BEFORE (T-1 evening, into post-midnight)

Amir is usually awake past midnight, so some day-of items can start once Spotify goes live (~00:00). But do NOT do audience-facing pushes at night.

Prep that should be DONE before release day, in advance:
1. **Smart link shell** -- create in Hypeddit via Symphonic (SymphonicMS -> Marketing -> Client Offerings -> Hypeddit). Free.
   - Source field: a track URL for metadata (use the premiere channel's URL as a temporary placeholder if your own isn't public yet; swap to Spotify on release day)
   - Genre: pick closest available (Hypeddit had no EBM -> used Techno)
   - Custom URL slug: paywalled -- accept the auto-generated one
   - Release settings: both "feature" checkboxes are paid -- leave OFF
   - Audio preview: SoundCloud is best (full track, in-page player). Use own SC once public.
   - Tracking pixels: leave blank unless running paid ads
2. **Spotify Canvas** uploaded (9:16 vertical MP4, 3-8 sec loop, 1080x1920, no audio). Boosts saves.
3. **Reel video file** finished and in drafts -- locked, not edited day-of
4. **IG caption** locked in a notes file -- not improvised day-of
5. **Hashtag set** picked (IG caps the dedicated hashtag field at 5)
6. **Reddit post drafts** saved (title + context comment) for each sub
7. **FB group post copy** locked, with per-group variants
8. **Discogs metadata** pre-filled (UPC, ISRC, credits, label, styles) ready to paste
9. **Old IG stories deleted** if any say "out tomorrow" / pre-save
10. **Profile grid image** prepped IF doing a grid post (Farewell skipped this; The Deceiver should have one ready -- this was a delay cause)

Post-midnight, once Spotify is live, OK to do quietly (no audience):
- Grab the clean Spotify URL (strip the `?si=` parameter)
- Update Hypeddit Source to the Spotify URL
- Pin Spotify Artist Pick
- Verify Bandcamp auto-flipped from pre-order to live

DO NOT at night:
- Flip your own SoundCloud track public -- the SC discovery push needs a daytime/active audience, not 2am
- Post IG reel / stories
- Send DJ promos
- Post to Reddit

### A2. RELEASE DAY (Friday, start 09:00 Berlin)

Critical path -- each step feeds the next:

1. **09:00 -- Verify DSPs live + collect URLs.** Spotify usually live first; Apple, YouTube Music, Tidal, Deezer lag 12-72h. Recheck through the day. VERIFY each link is the right track (Apple's first auto-match for Farewell was a wrong movie -- always click through).
2. **09:00 -- Flip own SoundCloud track public.** Full description, tags, release date set to today, pin to profile. This fires the SC discovery push -- timing it for active hours matters.
2b. **09:05 -- Fire SoundCloud AMPLIFY** (SC's new-track push; the old "First Fans" name is dead). Confirmed 2026-07-10: it is **far easier to trigger from the SC MOBILE app** than desktop, and it works on **TRACKS ONLY, not DJ sets/mixes**. Effectively one shot per track -- fire it right after the track goes public, while the audience is awake. Never at night.
3. **09:15 -- Update Hypeddit.** Source -> Spotify URL. Audio preview -> own SC URL. Section 5 Links -> add every verified DSP link.
4. **Pin Spotify Artist Pick** with a 140-char message.
5. **Bandcamp** -- confirm live (not pre-order), pin the track.
6. **Discogs** -- submit the release (slow moderation queue, start it early).
7. **Linktree** -- Farewell + smart link on top, per-platform DIRECT TRACK links below, full-catalog links at the bottom.
8. **IG bio** -- Link 1 = smart link, Link 2 = Linktree (IG native multi-link supports both).
9. **Afternoon buffer** -- collect any DSP links that came live late; prep story assets.
10. **18:30 -- POST THE REEL.** Friday evening (18:00-20:00) is peak for EBM/electronic. Audio = select the track from IG's library (not embedded). Hashtags in IG's dedicated field. Geotag Berlin. Tag collaborators.
11. **18:30-18:40 -- Fire Stories immediately** (Spotify share + link sticker, etc.). Stories within the reel's first hour COMPOUND its reach. Do not delay stories.
12. **18:30-19:30 -- Engagement window.** Reply to every comment + DM within minutes. This hour is the single biggest algo lever -- be present for it.
13. **19:30 -- Reddit r/industrialmusic.** US lunch peak. Link = SoundCloud (Reddit is anti-DSP). Self Promotion flair. Post a context comment immediately.
14. **Evening -- FB groups** (2-3, spread over hours, vary the text per group).
15. **Optional ~22:00 -- second story wave** (poll / refresh). Skip if no genuine angle.

### A3. DAY AFTER (Saturday)

1. Morning -- check overnight stats (Spotify saves, SC plays, reel, Reddit). Reply to anything. Don't dwell.
2. **11:00 -- r/AcidTechno** (self-promo allowed Saturdays ONLY -- mod-enforced).
3. **r/electro** (genre-fit risk if track is EBM-leaning; accept it or skip).
4. **Story reshare** of the reel (low-stakes, post any time).
5. **DJ promo wave** -- see Part A's DJ section logic.
6. FB groups -- 2-3 more.

### A4. DAY 3+ (Sunday onward)

- Sunday: r/darkwave, r/IndieMusicFeedback (requires giving feedback on 3 tracks first). Never post 5+ subs in 24h -- Reddit spam-flags it.
- Tue (~T+4): DJ promo follow-up to non-responders.
- ~T+5: collect all final platform links into the release JSON.
- T+12-14: rotate Spotify Artist Pick. (No Beatport/Traxsource charts check: Beatport is not used for new releases.)
- T+~20 days: r/EBM opens if last post was 30+ days ago (best genre sub -- time future r/EBM posts to land AT release, not weeks before).
- T+~25 days: stats review, update SI contact scores.

---

## PART B: KEY DECISIONS & RATIONALE

Every non-obvious choice made during Farewell, with the reasoning, so they are not re-litigated next time:

- **Start at 09:00, not 07:00** -- DSPs are live overnight; no need to be up at dawn.
- **Flip SC public at 09:00, not midnight** -- the SC discovery push needs a live audience; firing it at 2am wastes it.
- **Smart link via Hypeddit (free, through Symphonic)** -- no separate subscription; found under Marketing -> Client Offerings.
- **Reel posted 18:30 Friday** -- evening is peak for EBM/electronic; also ensures Amir is present for the post-reel engagement hour. The "+30% reach" figure was an overstatement; the real driver is the engagement window + story compounding.
- **Stories fire immediately after the reel, never delayed** -- stories in the reel's first hour compound its reach; hours-later stories do not.
- **Reel-only, no feed/grid post** -- grid post deferred to The Deceiver. (Next release: prep the grid image in advance -- improvising it caused a delay.)
- **Reel audio = IG library track, not embedded** -- gives attribution, audio-tab discoverability, lets other creators use it.
- **Hashtags: 5 in IG's dedicated field** -- IG caps it at 5. First-comment extra hashtags were tried and dropped (looked bad; algo counts dedicated-field tags fine).
- **IG bio: smart link slot 1 + Linktree slot 2** -- both, via IG native multi-link. Smart link for release-funnel visitors, Linktree for catalog browsers. Did NOT delete Linktree.
- **Linktree: kept existing, Farewell on top** -- per-platform entries point to DIRECT TRACK pages during a release, not artist homepages.
- **Reddit links = SoundCloud, not Spotify** -- Reddit culture is anti-DSP; SC embeds an inline player.
- **Reddit timing = 19:30 Berlin** -- US lunch peak; the subs skew US-heavy.
- **Reddit subs**: r/industrialmusic (Fri), r/AcidTechno (Sat-only window), r/electro (Sat), r/darkwave + r/IndieMusicFeedback (Sun). r/EBM was BLOCKED (posted there 2026-05-05, 30-day rule -> reopens 2026-06-04).
- **DJ promo: the `farewell-single` RM campaign is NOT a DJ list** -- it is 54 labels (a demo-submission campaign, mostly already sent in March). DJ promo needs its own pool, built fresh from Scene Intelligence DJs.
- **DJ promo channel = IG DM** -- the chosen DJs are `contact_method: social` with IG handles.
- **Discogs credits = "Amir Miller"** (real name) -- matches Deezer/YouTube auto-metadata; convention is real name for credits, stage name only in the Artist field. Studio "Ambertone Studio" went in the Notes field, not as a credit (Discogs location credits require a registered Company entity). Same rule on every platform (Amir, 2026-09-14): text people read (Bandcamp About, SoundCloud and YouTube descriptions) says "Inch of Shadow", credit boxes (Bandcamp Credits, Discogs, distributor) say "Amir Miller". Amir mixes and masters himself at Ambertone Studios, so the line is "mixed and mastered by [name] at Ambertone Studios, Berlin"; Eastern Stars is the exception (Riverside Studios, no Ambertone).
- **Pre-saves: skipped** -- never set up. LESSON: set up a pre-save campaign at T-14 days for the next release.
- **Nina has NO algorithm and NO crypto wallet** -- it is a community/curation platform, account-based login. Discovery = tags, hubs, reposts, editorial. Do not try to "game an algorithm" or reference Solana/Phantom/wallet.
- **Nina daily automation rewritten** -- reposts cut 8 -> 3-4 (a hub is curated, not a dump), favorite/repost split, volume varies daily, added safety precheck + reciprocity + growth tracking. Unfollow window kept at 7 days (Amir's call). Saved as Task 4 in `docs/cowork-task-bodies.md`.

---

## PART C: TAGS & COPY REFERENCE (Farewell)

**Release facts:** "Farewell" by Inch of Shadow. EBM / Acid / Electro, 122 BPM. Catalog ICR-001, Indigo Children Records (own label). UPC 824296260678. ISRC GBRKQ2619039. Distributor Symphonic. Released 2026-05-15. First track from "The Deceiver" EP (title track June). Premiered by THE BRVTALIST ~2026-05-08; Amir reposted it.

**Platform links:**
- Spotify: `https://open.spotify.com/track/6lOM9849xsWTUGiBJBjpuE`
- Apple Music: `https://music.apple.com/us/song/farewell/1892685171`
- Bandcamp: `https://inchofshadow.bandcamp.com/track/farewell`
- SoundCloud: `https://soundcloud.com/inch-of-shadow/inch-of-shadow-farewell`
- YouTube: `https://www.youtube.com/watch?v=ruZETDOTCPs`
- Deezer: `https://www.deezer.com/track/3955155371`
- Tidal: `https://tidal.com/track/515178072`
- Smart link: `https://hypeddit.com/4297o2`
- Linktree: `https://linktr.ee/inchofshadow`
- Beatport: pending approval

**Tags chosen, per platform:**
- **SoundCloud:** EBM, Acid, Electro, Dark Disco, Industrial, Berlin, Indigo Children Records, 122bpm
- **IG reel (dedicated field, 5 max):** ebm, acid, 303, electro, berlinunderground
- **IG extra set (not used in first comment):** darkdisco, industrialtechno, electronicmusic, indigochildrenrecords, 122bpm
- **Discogs styles:** EBM, Electro, Acid (genre: Electronic)
- **Nina release tags (4-tag platform cap):** CC set `#ebm #303 #berlin #acid`. Recommended final: `#ebm #acid #electro #berlin`. STILL OPEN -- see Part D.
- **Nina automation discovery tags (priority order):** ebm, acid, darkdisco, electro, techno, acidtechno, industrial, italodisco, nudisco, disco, synthwave, electronic

**Reel caption (final, used):**
```
Farewell. Out now.

An EBM track. Acid melody, brooding atmosphere, rolling bass.

First track from The Deceiver, an EP born while my mind wandered between the Mountains of Shadow and clouds of corruption.

Mix and master at @ambertonestudio.
Premiered by @thebrvtalist.
Indigo Children Records · ICR-001.

Stream anywhere. Link in bio.

Title track. June.
```

**SoundCloud track description:** signature line "EBM and acid shaped by dark disco sensibility. Analog synthesizers, drum machines." + track copy + cross-platform links + credits + "Berlin." sign-off.

**FB group post:** short first-person post, EBM/acid/electro framing, BRVTALIST premiere credit, "Mixed and mastered by Inch of Shadow at Ambertone Studios, Berlin." line, SC link, "Hope you will like it." close.

---

## PART D: FAREWELL CURRENT STATUS (handoff -- where we stand now, Saturday 2026-05-16)

### DONE
- All platform setup: Spotify, Apple, Bandcamp, SC, YouTube, Deezer, Tidal links collected + saved to `releases/farewell-single.json`
- Hypeddit smart link built + populated
- Linktree + IG bio updated
- Spotify Artist Pick pinned; Spotify Canvas up
- Discogs entry submitted (in moderation queue)
- IG reel posted Friday 18:30 + Story Frame 1 + Story Frame 3 (Sat reshare)
- Reddit: r/industrialmusic (Fri), r/AcidTechno (Sat), r/electro (Sat) posted
- FB groups: Friday batch posted
- Nina: Farewell uploaded, a duplicate archived; release is position 1 in the hub
- Nina Farewell push CC task delivered
- Improved Nina daily automation written + saved as Task 4 in `docs/cowork-task-bodies.md`; `scene_intelligence/nina_hub_stats.json` created
- DJ promo candidates selected

### OPEN -- what still needs doing
1. **DJ IG DMs** -- ~12 DJs. List: Curses (cursesforever), nightcrawlermusic, patyvapor, giulyeaaah, zaatar___, Alen Skanner, Sharlese_m, MORAN, ilayddab, delectro_dtronx, transgressionmusic, belaria. All via IG DM. Curses has no real SC (junk 2-follower match) -> IG only. Message template drafted; nightcrawlermusic wants a personalised version + "how are you" (Amir has talked to him before). Warm contacts (Alen Skanner, nightcrawler, etc.) get a download-link offer. **RISK: 12 IG DMs in one day is too many given the past near-miss bot warning -- split across 2-3 days, warm first, vary the text.**
2. **CC read-only DM scan** -- task delivered (in this conversation's history). CC scans IG DMs for who Farewell-relevant promo / "The Tour" went to in the last 6-7 months, skips Hebrew threads. Output = warm contacts to fold into the DJ list.
3. **Nina hub post** -- draft built by CC; needs publishing. Title "Farewell", body: "122 BPM. EBM weight under an acid lead. Spoken sample in the break. First track from The Deceiver. Indigo Children Records, ICR-001." (Nina is account-based, no wallet -- the earlier "wallet signature" blocker was CC misreading the page.)
4. **Nina tags** -- finalize the 4: recommended `#ebm #acid #electro #berlin`.
5. **Deploy improved Nina automation** -- paste Task 4 body from `docs/cowork-task-bodies.md` into Cowork `/schedule`, replace the old task. Suggested daily 16:00 Berlin.
6. **FB groups** -- 2-3 more.
7. **Audius upload.**
8. **Beatport** -- recheck delivery (approval was pending).
9. **Sunday Reddit** -- r/darkwave; r/IndieMusicFeedback (must give feedback on 3 tracks first).
10. **RM worktree split** -- the RM server runs from the `curator-discovery` git worktree, so promotion data saves to `/Users/amir/.config/superpowers/worktrees/Inchofshadowcode/curator-discovery/scene_intelligence/promotion_log.json`, NOT the main repo. Resolve so data does not diverge.
11. **YouTube OAC application** -- next week, via a SymphonicMS support ticket (Farewell + the 2024-2025 catalog qualifies).
12. **Symphonic Client Offerings** -- Amir to share the full list; flag which tools to use for The Deceiver.
13. `scene_intelligence/dj_promo_targets.json` -- Amir opened this file; unknown contents; check it in the next session.

---

## PART E: LESSONS FOR THE NEXT RELEASE

- **Set up pre-saves at T-14 days.** Farewell had none.
- **Prep the grid image in advance.** Improvising it on release day delayed the reel.
- **Time the r/EBM post to land ON release day.** Farewell could not use r/EBM (posted there 11 days before, hit the 30-day cooldown). r/EBM is the best-fit sub -- do not waste it.
- **Build the DJ promo list early and separate from the label/demo campaign.** They are different audiences with different goals.
- **Always click through auto-matched DSP links.** Apple Music's first match for Farewell was the wrong title (a movie).
- **Keep IG DM volume low per day** (past bot-warning history). Split promo DMs across days, vary the text.
- **Confirm which directory the RM server runs from** before a release, to avoid the worktree data split.
