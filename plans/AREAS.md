# Areas: one label for everything (since 2026-11-05)

Every ticket, sidebar group, chat and handover uses one of these six labels.
In chat, tickets are shown as `<emoji> <Area> <number>`, e.g. `🎵 Release 2`.
Old ids (R-02, GR-08, Machine-28 ...) stay in the files for code, commits and history only; they are not shown to Amir.

| Label | What's in it | Old ids folded in |
|---|---|---|
| 🎵 Release | singles, EP, covers, metadata, curators | R |
| 🎬 Socials | Instagram, SoundCloud, YouTube, Bandcamp (incl. their maintenance) | IG / SC / YT / BC lanes, G-01, G-10, M- on those lanes |
| 🎧 Booking | DJ outreach, festivals, EPK, mixes | DJ |
| 💶 Income | +500 EUR work, Gap Radar | GR (+ new Income tickets) |
| 🎸 Studio | MPC, guitar / music theory, samples, production | new |
| ⚙️ System | GitHub, contracts, tokens, API caps, Control Panel board, other upkeep | G, M (other lanes), Machine, Look, Formats, Words, Measure, Mkt |

Fields: each ticket in `plans/tickets.json` and `plans/control-panel/tickets.json` has `area` and `area_no`.
New tickets: take the next free `area_no` in their area, counted across BOTH boards (System numbers 6-61 are the Control Panel board). New-ticket id prefixes: IN- (Income), ST- (Studio); the others keep their old prefix.

## Chats and handovers

- No sidebar groups: chats stay under the Inch of Shadow project; each open chat title starts with its area emoji (e.g. "🎵 Half the Night EP"). Automated runs (engagement, refresh, retry, sweep, weekly stats) stay ungrouped and out of sight.
- One parent chat per area (top level, under Inch of Shadow): 🎵 Half the Night EP (Release), 🎬 Socials, 🎧 Booking, 💶 Income, 🎸 Studio, ⚙️ System. Side chats are started FROM the parent so they nest under it. ⚙️ System also merges every area's "Ticket updates" into tickets.json.
- Each open chat keeps a handover file: `plans/handovers/<area>/<chat>.md` (where it stands, open decisions, files, linked tickets).
- A new side chat starts by reading its area's handover files + the open tickets of that area.
- A chat that ends or is dropped writes its result into its handover + the ticket notes first; then it can be archived. Nothing is archived before that.

## Priority (Amir, 2026-11-05)

Every open ticket carries `bucket` (🔥 now / ⏭️ next / 🅿️ parked / 🔁 routine), `who` (🙋 amir / 🎃 claude / 🤖 auto), `label` (short platform + topic name shown with the number), `next_step`, and `chrome` (🌐 true = the work happens in Amir's Chrome: one shared browser, one job at a time, outside the automation windows).
- Max 3 🔥 now per area. It is a cap, not a quota: an area with nothing urgent has 0.
- Each parent chat sets its own buckets and lists them under "Ticket updates" in its handover; the ⚙️ System chat merges.

## Emoji map (Amir, 2026-11-05)

| Group | Emoji | Means |
|---|---|---|
| Areas | 🎵 🎬 🎧 💶 🎸 ⚙️ | Release, Socials, Booking, Income, Studio, System (Socials was 📱, Income 💰, Studio 🎛️ until 2026-11-05) |
| Bucket | 🔥 ⏭️ 🅿️ 🔁 | now (max 3 per area), next, parked, routine |
| Who | 🙋 🎃 🤖 | Amir decides, Claude goes (was ▶️), runs by itself |
| Where | 🌐 | work happens in Amir's Chrome |
| Status | ✅ ⚠️ 🔴 | done, risk, problem; 🟢 🟡 🔴 for scores |
