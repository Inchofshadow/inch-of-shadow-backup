# Release Manager audit, 2026-09-26 (Machine-15, read only)

Every page was opened in the browser and fetched with the app's own test client. Nothing
was changed. Numbers below were measured, not guessed. The stylesheet was started on
2026-04-07 and has grown through 31 commits to 7,023 lines; it was never audited before.

## 1. Broken

| # | What | Where | Cause | Fix |
|---|---|---|---|---|
| 1 | **The Engagement page crashes (500).** | `/engagement` | `_recent_engagement_history` compares `entry["date"] >= cutoff` and the engagement log holds entries whose date is `None` | one line in `webapp.py`: skip entries without a date. The data file is automation state and is not touched |

That is the only error. No other page fails and the browser console is clean everywhere else.

## 2. Stale and noisy (what makes the app tiring to sit with)

| # | What | Evidence |
|---|---|---|
| 2 | The Dashboard opens with a red block of **16 overdue milestones**, all from Farewell (May) and The Deceiver (July), releases that are long finished. It never goes away | screenshot of `/` |
| 3 | Autopilot lists **17 overdue tasks for The Deceiver**, 54 to 104 days late. The app does not know a release is over | `/autopilot` |
| 4 | Stats says **last synced 2026-07-19** | `/stats` |
| 5 | Promotion is an empty page until a release is chosen; Autopilot repeats what Tickets and the release checklist already show | `/promotion`, `/autopilot` |

## 3. Heavy

| # | Page | Size | Why |
|---|---|---|---|
| 6 | `/sc-automation` | **531 KB** | the whole follow tracker rendered as 676 table rows on every load |
| 7 | `/board` | 214 KB | the entire tickets JSON (187 KB) is embedded in the page as a script |
| 8 | release pages | 110 KB each | fine, but the calendar and checklist are always fully expanded |
| 9 | `/seo-copy` | 357 ms | the only slow page; every other page renders in under 50 ms |

## 4. Design, measured

| # | Finding | Number |
|---|---|---|
| 10 | **Text is too small for long sessions.** On a release page 199 of 374 text pieces are under 12 px; the smallest is 8 px. The body is 17.6 px but the UI shrinks almost everything with sizes from 0.58 rem up | 51 CSS rules under 12 px |
| 11 | **Colours bypass the variables.** A `:root` block with tokens exists, but 218 hard-coded hex values (106 distinct) sit beside it; the Settings palette page changes the tokens and misses the rest, so pages drift apart (corrected after the first write: the tokens do exist) | 218 / 106 |
| 12 | **The stylesheet fights itself.** 74 selectors are defined more than once (`.sidebar`, `.main-content`, `main`...), 12 `!important`, 13 media queries, 63 inline `style=` attributes in templates, two pages carry their own `<style>` block | 7,023 lines |
| 13 | **Two UI fonts** (Inter and Space Grotesk) plus monospace; neither is the brand face. Headings in Space Grotesk give the tech-dashboard look that was already rejected once for the thumbnails ("very claudy") | 2 font files |
| 14 | **Status colours are a generic dashboard set** (green, red, amber, blue) that ignores the brand moods | Settings page |
| 15 | **The sidebar does not fit the window**: 981 px of nav in a 768 px window, so Settings sits below the fold; the loudest control on every page is "+ New Release", used a few times a year | measured |
| 16 | The Tools group mixes making (the resizers) with words (SEO, bios); the two newest pages, Tickets and Board, already use a calmer platinum look and read as the model for the rest | sidebar |

## 5. What is good and stays

- Fast: every page but one renders in under 50 ms.
- The release page's structure (header, calendar, checklist by category, timeline) works.
- Tickets and Board (September) are already in the brand: platinum on warm black, calm density.
- 617 tests pass; the app is backed up (2026-09-24, Intenso).
- No page writes to a platform; the automation pages only show state.

## 6. What Machine-16 should do, in order

1. **Fix the crash** (finding 1). One line, its own commit, a test that feeds an entry with no date.
2. **Design tokens first.** A `:root` block generated from `frame.md` (M2 platinum and warm black, the moods for status colours), one type scale with a **13 px floor**, one UI font (Inter stays, Space Grotesk goes), the brand face for page titles only. Every page then inherits.
3. **Finished releases go quiet.** A release past its date plus 30 days stops raising overdue items on the Dashboard and Autopilot; the Dashboard shows the next release and the board only.
4. **Lighten the two heavy pages.** The Board fetches its JSON instead of embedding it; the SC tracker shows the last 50 rows with a "show all".
5. **The sidebar fits.** Groups: Releases, Plan, Studio (new, Machine-10), Words (SEO, Bio), Outreach, Analytics; Settings visible; "New Release" demoted to the Releases group.
6. **Then page by page**, each on its own commit with a before and after screenshot, in this order: base and Dashboard, release page, Board and Tickets (already close), the resizers, SEO and Bio, Stats, Engagement, Promotion, SC Automation (skin only, no logic), Autopilot last (or folded into the Dashboard).

Screenshots were taken live in the browser pane during this audit; the pane cannot save
them to disk, so the before/after set will be made with the refresh itself.
