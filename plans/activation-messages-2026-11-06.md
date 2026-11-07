# Activation messages (S11 drafts, 2026-11-06)

DRAFTS ONLY. Nothing here is sent, pinned or uploaded. Amir reads and edits first.

The rule (card S11, approved 2026-11-06): a new fan gets one message, once, per door.
Three doors: the email list, the Spotify profile, the SoundCloud follow. It is not a
newsletter and it does not break "one mail per release, nothing else".

Sources: `plans/strategy/product-lens-2026-11-06.md` section 5, `docs/brand/voice.md`,
`docs/brand/positioning.md` (PUBLIC STATUS: the songs are not public, so the songs-era
texts below wait for the switch and carry no song names), `docs/brand/proof.md`
(Half the Night EP: Half the Night + Pinocchio, Indigo Children Records, date open,
never claimed as released), `releases/pinocchio-single.json` (sound notes).

---

## 1. Welcome mail (Buttondown, sent once when someone joins the list)

Plain text. One link, the Bandcamp page. Spotify and Instagram links belong in the
Buttondown footer, not in the body. No date in the body: a welcome automation is static,
and the date is open anyway.

### 1a. Electronic era, now (Half the Night coming)

Subject: Hi from Inch of Shadow

Hi,

Thank you for joining the list. I'm Amir, I make music as Inch of Shadow in Berlin.

Next up is the Half the Night EP on Indigo Children Records. Two tracks, dark disco
at 127, a 303 acid melody over a driving rolling bass. It is coming as soon as it is
ready, and you will hear about it here first.

Everything that is out so far is on Bandcamp:
[BANDCAMP LINK]

I write when something comes out, not more. You can also find me on Spotify and
Instagram.

Hope you will like it 🖤

Amir
Inch of Shadow

### 1b. Songs era, later (first single coming)

Subject: Hi from Inch of Shadow

Hi,

Thank you for joining the list. I'm Amir, I make music as Inch of Shadow in Berlin.
I write, play and produce everything myself.

The first single of the new songs is next. My voice on it, guitars and synths, a new
wave beat around 110. It is coming as soon as it is ready, and you will hear about it
here first.

Everything that is out so far is on Bandcamp:
[BANDCAMP LINK]

I write when something comes out, not more. You can also find me on Spotify and
Instagram.

Hope you will like it 🖤

Amir
Inch of Shadow

---

## 2. Spotify Artist Pick text (Spotify for Artists, pinned on the profile)

Max two lines, what comes next, no date. Pinned to the newest release, or to the lead
track once it is live. Rotate at T+12 to 14 days (release-day playbook). An Artist Pick
stays live 180 days at most.

### 2a. Electronic era, now

Next: the Half the Night EP on Indigo Children Records. Two tracks, dark disco, 303 acid over a rolling bass.

### 2b. Songs era, later

Next: the first single of the new songs. My voice, guitars and synths, a new wave beat.

---

## 3. SoundCloud follower-only early drop (songs era)

Mechanism, not copy: the single goes up as a follower-only track in SC Artist Pro,
direct upload (not via the distributor, so Amplify applies later), then public and
Amplify inside 14 days (`platform-plan-songs-2026-11-05.md`). SoundCloud shows its own
"follow to unlock" button on a gated track. The text Amir writes is the track
description under it:

Early for followers. Public in two weeks.
Hope you will like it 🖤

---

## 4. When each fires

| Door | Trigger | Tool | Who presses it | What is measured |
|---|---|---|---|---|
| Email list | A new subscriber confirms the double opt-in | Buttondown welcome automation | Amir sets it once; Buttondown sends it to each new subscriber | Opens of the welcome mail, clicks on the Bandcamp link (Buttondown stats) |
| Spotify profile | A new follower or listener lands on the profile | S4A, Artist Pick | Amir pins it on release day, rotates at T+12 to 14 | Profile visits and follows gained, from the S4A Monday read |
| SoundCloud follow | The follower-only drop goes up (one per single) | SC Artist Pro, follower-only track | Amir uploads and gates it, then opens it inside 14 days | Follows gained during the gated window, plays in the first 14 days |

Open (from the product lens): whether Buttondown or Bandcamp's own message tool sends
the welcome mail. The texts above work in either.

Checks before anything goes live: no song names or lyrics in the songs-era texts until
the switch; Half the Night never written as released before its date; handles only from
`artist_profile.json`; no em-dashes.
