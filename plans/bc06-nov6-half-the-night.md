# BC-06: Bandcamp Friday + Listening Party (Half the Night EP, date open)

Drafted 2026-10-21. Nothing scheduled or sent. Release file: `releases/pinocchio-single.json` (single "Half the Night", tracks Half the Night + Pinocchio, ICR-003; not out on 2026-11-06, date open, as early as possible; next Bandcamp Friday 2026-12-04).

## Facts checked 2026-10-21

- Bandcamp Friday Nov 6 is official (help page): midnight to midnight Pacific = **Fri 09:00 to Sat 08:59 Berlin** (US clocks change Nov 1). Only Bandcamp's revenue share is waived; card fees stay.
- A Listening Party needs a **public** release; a pre-order counts. Followers get an invite email, RSVPs get reminders (2 days, 1 day, 1 hour before), attendees get a follow-up buy email. Free. Ends when the release finishes playing. Chat can be limited to supporters; a moderator can be invited. (Hypebot / Brian Hazard 2023-10-26; Bandcamp blog 2023-08-08.)
- So the Bandcamp page with the pre-order has to be live before the party can be scheduled.

## Order of steps

| When | What | Who |
|---|---|---|
| Pre-order day | Publish the pre-order, tick "notify followers" (as for The Deceiver: 44 notified) | Amir |
| Same day | Schedule the Listening Party (release edit page > Listening Party) | Amir |
| Same day | `python3 bandcamp_links.py --write` for the campaign links, then BC-02/03 steps for the new release | Claude |
| Release day or a Bandcamp Friday after it (date open), about 09:30 Berlin | Send the follower message below (Tools/Community > Send followers a message) | Amir |
| Release day or a Bandcamp Friday after it (date open), 19:00 Berlin (10:00 Pacific) | Listening Party, be there 30 min early with a welcome line | Amir |

Why Friday 19:00 and not the day before (Bandcamp's own suggestion): on release day the music is buyable at once, and the whole party sits inside the Bandcamp Friday window, so every sale during it skips Bandcamp's share. 19:00 Berlin = 10:00 Pacific, the time slot used in the Hypebot example for overseas fans. Alternative: Thu Nov 5, 19:00 as a pre-release preview.

If the date slides to Nov 13: no Bandcamp Friday that day. The party moves to Fri Nov 13, 19:00; the Friday message moves to Dec 4.

## Follower message, release day (draft)

Copy rules: "Hi all", the music described, "Hope you will like it", no em-dashes, no asks for opinions.

> Hi all,
>
> Half the Night is out today, two tracks: Half the Night and Pinocchio. [AMIR: one line on how they sound]
>
> It is Bandcamp Friday, so Bandcamp takes no share of today's sales.
>
> Listening party tonight at 19:00 Berlin time, here on the release page.
>
> Hope you will like it 🙏

## Notes for the party chat (draft, one line per track)

- Half the Night: [AMIR: one line, the sound or how it was made]
- Pinocchio: [AMIR: one line]

## Dec 4 (second Friday)

One short message pointing back to Half the Night and the catalogue, same rules. Drafted closer to the date.
