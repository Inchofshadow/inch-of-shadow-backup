# Gate: the parent chats' lists, part 2 (2026-11-15, Fable, on Amir's "Yes, continue")

Queue items 4 to 15 of `QUEUE.md`. Each claim below was checked on disk or on the live page. What I did not read in full is listed at the end.

## 🎵 Release

### Description map + drafts D1 to D4 (plans/htn-description-map-2026-11-12.md). Verdict: approve; one live problem found while checking.
- ✅ **Bandcamp's Google text is built as the map says.** Live page today: "Half the Night by Inch of Shadow, releases 11 December 2026", then the track list, then the About. Option A of D1 is the one that went live. Open check 2 of the map is answered: yes.
- ✅ The drafts keep the rules: no key, no tempo, no em-dashes, the name in full, Friday 11 December, the approved description word for word.
- ❗ **The live Half the Night page on Bandcamp carries a "techno" tag.** The page shows the tags Acid, Dark Disco, EBM, Electro, Electronic, Techno (capitalised, so they come from the artist profile's genre settings, which Bandcamp adds to every release) plus the album's own tags. The locked tag rules of 11-03 say never techno. The SEO pass wrote "no profile genre tags are visible on the public page"; they are, on the album page. Fix = remove Techno from the Bandcamp profile genre tags. That is a profile setting in Amir's account: his yes, old value written down first. It changes the tags on every release page.

### EP plan (plans/half-the-night-ep-plan.md). Verdict: redo the pointers, or mark it as history.
- The banner "read Dec 4 as Dec 11" is not enough. Three statements are wrong beyond the date:
  1. "Follow `plans/release-day-playbook.md` A1 to A4" points to the OLD playbook, whose Bandcamp step says the pre-order flips by itself. It does not. The Dec 11 playbook replaces it.
  2. "DJ promo: 28 DJs, send Nov 20 to 25 before release" is replaced: DJs go after release (Dec 14 to 19), show hosts Nov 25 to 27.
  3. "Bandcamp Friday" as the release day no longer holds (Bandcamp Friday is Dec 4).
- The pitch line says "latest about Nov 25" (now about Dec 2). "Latest" is the floor: send the pitch as soon as the release shows in Spotify for Artists.

## 🎧 Booking

### Label drafts (queue item 4). Verdict: too late for a gate.
- The handover's own log says Amir sent the last 26 Gmail drafts on 11-14 (drafts folder empty, about 80 labels reached, 4 more bounces). What is left are contact forms.

### Post-release DJ wave + show hosts (plans/handovers/booking/htn-dj-promo.md). Verdict: approve the plan, fix the texts' source before anything is approved.
- ✅ Mechanical check of all 45 draft blocks: no em-dash, no short name, no wrapped links, no gig ask, no feedback ask, no Tel Aviv target (the two mentions are in the dropped list). The combined send table is the only live one (the Round 2 plan is marked superseded).
- ❗ **Two copies of the texts, and the handover copy is stale.** In the handover file 10 drafts still name the tempo ("around 126") and all 45 offer WAVs. The send page (`htn-send-plan.html`) has the tempo removed (0) but still offers WAVs in 34 texts, while the 11-13 note says "WAV line removed: just Download is on". Either the WAV rule was for the show hosts only or the page is not updated. One source of truth is needed before Amir approves the 38 post-release drafts.
- 40 drafts open with a first name. Rule of 11-13: a first name only when it is confirmed. Check each name against its source before approval.
- The send table still marks Local Suicide with ❓ although the 11-13 log says the handle is verified. Alberto Melloni is still ❓.

### DJ outreach week 1 + 2 cards (queue item 6). Not read in depth.
- Nothing is sent and the Booking chat already lists the open flags (young_love_berlin vs Master & Servant, Electric Baile vinyl-only, two wrong handles). Those flags stand; the drafts are not ready for approval until they are closed.

## 🎬 Socials

### IG ratio plan, option B (plans/ig-ratio-plan-2026-11-12.md). Verdict: approve; one thing the plan does not say.
- ✅ The numbers match the snapshots (992 / 1,016 on 11-11; 997 / 1,046 on 11-14) and the projection arithmetic holds (about +2.9 followers a day gives about 1,135 on Dec 31).
- ✅ The duplicate-row bug it describes is fixed: the coverage check counts unique names now (45e4416).
- ⚠️ **The follows cut pulls against the follower target.** The projection assumed 16 follows a session. Since 11-14 it is 10 until at least Dec 5. Fewer follows mean fewer follow-backs, so the follower rungs Amir set on 11-09 (1,030 by Nov 30, 1,110 by Dec 31) get harder: Nov 30 needs +33 in 15 days from 997. The plan should state the trade once, so a missed follower rung in the brief is not read as a failure.

### Content plan + listening party plan. Verdict: approve; one clash.
- ✅ Dates are on Dec 11, all local, no AI on images, his-voice text goes to the main EP chat.
- ❗ **Two files disagree on the reel time.** The party plan says "the release reel moves to 17:30 so the two do not clash". The release-day playbook still has the reel at 18:30 and lists the clash as open for Amir. One answer has to be written in both.

## 💶 Income

### Brief v4 "learn then build". Verdict: approve with two memory fixes.
- ❗ **Two memory rules now contradict each other.** v4 says "don't drop an idea only because the crowding signal is crowded". `only-pitch-vetted-ideas` says show only an idea that passed the crowding check. v4 is newer and came from Amir's "ideas were being missed and dismissed too quickly", but the old rule is not amended and v4 even lists it under "older rules still apply". Amir should confirm in one line: crowding is a score, not a veto.
- v4 also lists `no-selling-tracks-or-music-for-others` as a rule that still applies. That rule is marked SUPERSEDED (he is open to it since 11-05).

### App factory plan v1 (on hold). Verdict: a fair draft; one missing fact before any sign-up.
- ✅ Honest on money and time: weeks 1 and 2 cost $0, 500 EUR a month "only after 6 to 12 months and several apps", no build before a keyword has proof.
- ⚠️ **Missing: what the seller question costs in privacy.** The plan asks who the seller is. In the EU a seller who trades through the App Store has to show contact details on the store page (my knowledge of Apple's trader rule, not re-checked today). For a person that can mean his own address and phone number in public. Check this at the source before the $99 sign-up; it may decide the seller question.

### Radar cap and spend rules. Verdict: approve; one stale label.
- ✅ `gate()` does what the rule says: the radar stops at $70 a month, and it also stops when the month's total would eat into the $80 kept for Inch of Shadow work. November: $70.54 used, so every profile is blocked until Dec 1 with no spend.
- `schedule.json` still says "status: default, Amir confirms". He confirmed on 11-08 ("Keep the cap"). Update the label.

## Not read in full (stated, not hidden)
- The Symphonic submit checklist memory and the vinyl-frame memory: next used in January or later.
- The five new rule memories of 11-11 to 11-13: read as index lines only; no clash seen beyond the Income one above.
- The Reddit back-off (13c5e19), the pool refill task and the two small SoundCloud items: small, tests exist, not read.
- The Studio service agreement: not ready for a gate (waits on Amir's numbers).

## Decided after the gate (2026-11-15)
- **The "Techno" profile genre on Bandcamp stays.** The EP chat showed Amir where it sits; his answer: "ahhh now i see its fine". The never-techno lock of 11-03 covers release tags, not the profile genres. Nothing changed. Do not raise it again.
