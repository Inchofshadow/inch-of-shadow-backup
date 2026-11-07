# Guest mix launch pack

Checklist for every guest mix or set that someone else publishes (podcast, radio, mix series).
Built from the Blank Wave Guest Mix 130 campaign (ticket G-02, 2026-10-08 to 10-13: 29 → 222 plays in 5 days).
Get it ready in the days before it goes live, not on the day.

**Day 1 = the day the host posts it.** Everything is counted from there. Blank Wave posted on 10-08 afternoon, but Amir (sick) missed the host's IG message, so our day 1 actions slipped to 10-09. The first 24-48 hours matter most, so catching the publish is part of the job.

## 1. Before it goes live

- [ ] **Facts:** host account(s), expected date, the private link we sent (never share that one publicly).
- [ ] **Catch the publish:** ask the host for the exact date; from the expected week on, check the host's SC page once a day (logged out, read-only) and tell Amir the moment it is live, so a missed IG message can't cost day 1.
- [ ] **Tag list, verified only.** For every artist in the tracklist (and remixer, featured singer, label):
  - check our own data first: latest IG export (following / followers), `scene_intelligence/ig_follow_tracker.json`, SI;
  - then a real profile page, or the artist's own Bandcamp / SoundCloud link;
  - anything not confirmed gets ❓, and Amir taps it before it goes public. Never a handle from a search snippet (IG comments cannot be edited).
  - Watch for aliases (Lapse of Reason = Pablo Bozzi).
- [ ] **Host look:** grab the host's cover (`og:image` on their SC page, `original` size) and sample their colours/font, so our pieces match theirs.
- [ ] **Story 1, announcement:** B&W photo + host-style text, no audio (Amir adds his own track in IG). Script: `videos/blank-wave-130-story/make_story_bw.py` (static variant `make_story_bw_static.py`).
- [ ] **Story 2, tracklist card:** every line centred under the header, all tracks the same colour (artists reshare a list where they stand level), 39 px text. Script: `videos/blank-wave-130-story/make_tracklist_story.py`. Tag all verified artists on it: a story mention can be reshared with one tap.
- [ ] **Messages in Amir's style** (memory: dm-style-cold-contacts): "Hi, how are you? :)", a warm line about THEIR music, "some of my tracks are in it" (no track names), "if you wanna listen here is the link, hope you will like the mix 🙏", link alone, "thank you!".
  - SC inbox: read every thread in full; anyone who sent a track gets a 20-30 s play + like first.
  - IG: artists whose tag is broken or missing, DJs he knows, manual follows that fit (from the latest export).
- [ ] **SC sending permission** set up in advance, so sends after Amir's go don't get blocked.
- [ ] **Playlist cover** ready for "DJ Sets & Mixes" (soundcloud.com/inch-of-shadow/sets/dj-sets-mixes).

## 2. Day 1 (the day it is posted)

- [ ] Accept the collab invite (check @inch_of_shadow + the right photo; photo 55 = retouched copy).
- [ ] Repost on SC, add to "DJ Sets & Mixes", keep the playlist in Spotlight.
- [ ] Story 1 with link sticker ("Listen to the full mix"); tap the sticker yourself after posting. If the link fails: SC app → Share → Copy link, delete and repost.
- [ ] Tracklist comment on the collab post, verified tags only.
- [ ] Booking file: add the public URL to `scene_intelligence/booking_targets.json` → `sets_public`.
- [ ] SC inbox messages + IG messages, first 48 hours.

## 3. Days 2-7 (counted from the posting day)

- [ ] Story 2 (tracklist card) on day 2-3.
- [ ] Pin the collab post; save both stories to a highlight.
- [ ] Reddit only if Amir wants it (research: 19:30 Berlin, SC link, Self Promotion flair, context comment, max 4 subs in 24 h; r/AcidTechno Saturdays only, r/EBM 30-day cooldown).
- [ ] Stats snapshot on day 1, 3 and 7 after posting (plays, likes, reposts, comments) into the ticket.

## Not worth it last time

Media / booking outreach for the mix, the SI scene list, DMs to big names outside his scene (Yahel, Eitan Reiter).
