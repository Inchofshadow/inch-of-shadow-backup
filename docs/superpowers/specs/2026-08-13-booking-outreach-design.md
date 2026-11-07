# Booking Outreach Campaign — Design

Date: 2026-08-13
Status: approved by Amir 2026-08-13
Goal: Inch of Shadow DJ bookings in Berlin, starting autumn 2026.

## What is being pitched

DJ sets only. Not live sets. Decided 2026-08-13.

Proof material: two publicly available recorded sets (Johnny Knuppe DJ set, Live at
THE CODE MARATHON 29.12). URLs to be confirmed by Amir before wave 1.

## Target universe

In scope:
- Berlin clubs and venues
- Berlin promoters, collectives, party series
- Booking agencies
- Club streaming channels (HÖR, Boiler Room, Telekom Electronic Beats and similar)
- Online radio stations (Refuge Worldwide, Cashmere, Kiosk, The Lot, LYL, Noods,
  Operator, Radio 80000 and similar)
- Podcast and mix series

Out of scope:
- Spotify and Apple editorial playlist pitching. That is a different campaign and
  is already covered by the release-platforms skill.
- Live set bookings.

## Strategy: promoter-first, in tiers

The core insight: in Berlin most clubs do not book individual DJs. Party series and
collectives rent the room and curate their own lineups. About blank, OHM, Renate,
RSO, Void, Arkaoda and Sameheads all work this way. So the person who can give Amir
a slot is usually the promoter, not the venue booking desk.

Tiers, in send order:

1. Radio and mix series. Highest yes rate, costs the curator nothing, and a
   published show or mix is the credit that makes tier 3 land later.
2. Berlin promoters and collectives in the dark disco / EBM / coldwave / acid lane.
3. Venue booking desks where the genre genuinely fits.
4. Long game (Sisyphos, HÖR, Tresor). Open the relationship, expect nothing,
   follow up quarterly with news. 12 to 24 months is normal.

AMENDMENT 2026-08-13 (Amir): pull some tier 3 venue-desk sends forward into the
early waves rather than deferring them to after tiers 1 and 2. Genre mismatches
(Kater Blau, Club der Visionaere, Klunkerkranich, Golden Gate, Ritter Butzke, AVA,
Crack Bellmer, Der Weisse Hase) stay excluded or deferred.

Wave 1 composition: warm contacts (venues and promoters who have already booked
Amir) plus 2 to 3 radio stations plus a small number of genre-fit venue desks.

## Timeline reality

Berlin club calendars run 2 to 4 months ahead. Emails sent in August 2026 are
pitching October to December 2026. That is realistic for tiers 1 to 3. It is not
realistic for Sisyphos or Tresor.

## Data files

Two new files. Neither touches existing SI state or the IG/SC engagement automation.

`scene_intelligence/booking_targets.json`
One record per contact:
- name, type (venue | promoter | radio | mix_series | agency | streaming_channel)
- tier (1-4), city, genre_fit (strong | medium | weak)
- contact_name (the actual decision maker, where findable)
- email, instagram, website, ra_url
- hook: the specific verifiable personal detail this email will be built on
- hook_source: where the hook came from, so it can be re-checked
- status: researched | drafted | approved | sent | replied | booked | passed
- in_si: whether the contact already exists in enriched_contacts.json

`plans/booking-outreach-tracker.md`
Human-readable log: who, when, what was sent, what came back, next follow-up date.
SI currently has no booking outreach record of any kind. This is the missing piece
and it is what makes the multi-year targets workable instead of forgotten.

## The hook rule

Every email is built on one specific, true, verifiable detail: a night they ran and
roughly when, a DJ they booked whose lane overlaps, a track on their SoundCloud, or
the fact that Amir was in the room.

Hard rule: if no real hook can be found for a target, that target does not get an
email. Bring it to Amir. He either supplies the hook from his own knowledge of the
scene, or the target is dropped. Never invent a detail to fill the slot.

## Email anatomy

Format:
- Under 150 words.
- No bio paragraph. Genre gets half a sentence at most.
- One hook, one ask, one link. The ask is explicit: a slot, a warm-up, a guest mix.
- State that he lives in Berlin (Neukölln). Local DJs are cheap to book and fill gaps.
- Links bare on their own line. Never "you can find my work at".
- Sign off "Amir". No signature block, no title, no logo.
- No attachments. Cold PDFs hurt deliverability and do not get opened. The EPK goes
  out only on request.
- Subject lines lowercase and concrete.

Banned, because these are the tells that read as AI-written:
- Em-dashes. Standing rule across all of Amir's copy, and loudest in email.
- "I hope this email finds you well", "I wanted to reach out", "As someone who".
- Three-adjective runs ("raw, hypnotic and cinematic").
- Paragraphs of matching length.
- A closing summary sentence that restates the ask.
- Formal complete-sentence register throughout.
- ADDED 2026-08-13 after Amir rejected a draft: no knowing, wry, self-aware lines
  that comment on the email itself. "I won't pretend this is anything other than a
  first email", "is there a proper way to pitch this, or is this it". These read as
  machine-written, they flag the email as cold, and they start from a weak position.
  Say the thing, make the ask, stop.
- Related: never put the campaign strategy into the email. The long-game handling
  for a target like Sisyphos belongs in the tracker. The recipient sees a normal,
  direct, confident email and nothing about how they are being managed.

Required: contractions, some sentence fragments, English (Berlin booking runs in
English).

## Follow-up rule

No reply is the default outcome, not a rejection.
- One follow-up after 3 weeks, and it must carry something new: a fresh mix, a
  release, a gig played.
- After that, quarterly, and only ever with new news.
- Never an empty "just bumping this".
- Tracked in booking-outreach-tracker.md.

## Delivery and consent

1. Drafts are reviewed by Amir in the conversation (or as an HTML file).
2. On approval, drafts are created in Gmail via the connected account.
3. Amir hits send himself for the first emails.
4. Later he may delegate sending. Even then, explicit confirmation is required
   before any email is sent on his behalf.

## Pre-flight checklist before wave 1

Bookers look you up before replying. Confirm:
- [ ] RA profile (ra.co/dj/inchofshadow) lists past gigs
- [ ] Both SoundCloud sets are public and properly titled and tagged
- [ ] The two set URLs are confirmed
- [ ] A three-line short bio exists, distinct from the long platform bios

## Volume

5 to 8 emails per wave, roughly one wave a week. Small enough that every email is
genuinely specific to its recipient, and small enough that Amir can handle the
replies and follow-ups.

## Source of truth for facts

`docs/brand/proof.md` and `artist_profile.json`. Never claim beyond them.
Venues played: About Blank, Beate Uwe, KitKat, Insomnia, Torture Garden at Metropol,
among others. Labels: MM Discos, Stereo Society, NaNa Disc, Indigo Children Records.
Curation credit: Shape of Us 2.0 and 3.0 at Dark Matter, Berlin Fashion Week.
