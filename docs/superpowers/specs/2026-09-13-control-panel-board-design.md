# Control Panel Board, design spec

Date: 2026-09-13. Approved in chat by Amir, section by section. Mockup: "Board Mockup" artifact v3.

## Purpose
One place that holds the whole plan for the songs era as small tickets, ordered by build
order and dependency, viewable as a page inside the Release Manager. Control Panel lane is
built first; the Marketing lane is drawn on the board with empty categories so every Control
Panel ticket can name what it will later serve.

## Source of truth
`plans/control-panel/tickets.json`. The page renders it and never writes it. Edits happen in
the file, by Claude (normally) or Amir (by hand). A validator refuses a file with a ticket
missing `why`, `serves` or `question`, an unknown status, an unknown category, a duplicate
id, or a `blocked_on` that names a missing ticket.

### Ticket schema
```json
{
  "id": "Look-01",
  "lane": "Control Panel",
  "category": "Look",
  "floor": 1,
  "title": "Type system",
  "why": "One pair of faces for every text object, or the brand fractures across tools.",
  "serves": "All formats. frame.md, Canva Brand Kit, HyperFrames, thumbnails.",
  "question": "Which pair ... then sizes and weights per use.",
  "status": "approved",
  "blocked_on": [],
  "size": "S",
  "references": [],
  "decision": "",
  "decided_on": "",
  "outputs": ["docs/brand/frame.md § type", "Canva Brand Kit"],
  "notes": ["2026-09-13 opened"]
}
```
- `id`: `<Category>-<NN>`; Marketing uses `Mkt-NN`. Category words: Words, Look, Formats,
  Machine, Measure, Mkt.
- `lane`: `Control Panel` or `Marketing` (names, never letters).
- `floor`: 1..6 build order. 1 Foundation, 2 Identity built, 3 Formats, 4 Machine,
  5 Measurement, 6 Marketing.
- `status`: proposed → approved → in-progress → blocked → done. `blocked` is derived when any
  `blocked_on` ticket is not done; the file may still store it explicitly.
- `references`: list of `{type: image|video|artist|post|url, path_or_url, note}`.
- Top-level file: `{"version": 1, "updated": "YYYY-MM-DD", "deadline": {"floors": [1,2], "date": "2026-09-20"}, "categories": {...}, "tickets": [...]}`.

## The page
Route `/board` in `release_manager/webapp.py`, template `release_manager/templates/board.html`,
sidebar group "Plan". Read-only.
- Header: title, three numbers (waiting on Amir = proposed count, floor now = lowest floor with
  open tickets, deadline). (counted on effective status, so a blocked ticket is not waiting on
  Amir)
- Filters (client-side JS): hide done (default on), waiting on Amir, lane, category.
- Legend: category colours.
- The tower, top to bottom = build order. One block per floor: number, name, "after floor N",
  status line; cards inside. Gold border on the floor being built now. Floor 6 dashed.
- Card: id, title, status pill, "← needs X" tag when blocked. Category as a coloured left edge.
- Click a card: detail panel below the tower with why, serves, question, references, blocked
  on, unblocks, outputs, decision, notes. Pure JS from a JSON blob embedded in the page.
- Styling from the RM's existing tokens and fonts; no new dependencies.

## Working rules
- Amir approves; Claude moves tickets through the rest and writes decisions.
- One floor at a time; children are created only when a parent decision creates them.
- A sitting = one or two tickets, 30 to 60 minutes, decided by eye or ear; Claude prepares first.
- References before options for anything visual or moving: Claude asks Amir for images,
  videos, artists, posts; videos go through `/video-analyze` and HyperFrames reads; photos are
  read directly; findings go into `notes`, the reference set into `frame.md` when decided.
- Every decision lands in three places: the ticket's `decision`, `docs/brand/frame.md`, and the
  Canva Brand Kit where it applies.
- `TICKETS.md` keeps the IG / SC / YouTube / Pinocchio ops lanes. B-01 there points to the board.
  `docs/brand/CONTROL-PANEL-SETUP-ROADMAP.md` and `VIDEO-BRAND-SESSION-KIT.md` get a top line
  pointing to the board and are not edited again.
- Deadline 2026-09-20 for floors 1 and 2.

## Seed (day one)
Floor 1: Words-01 sound paragraph · Words-03 proof refresh · Look-00 strip industrial/EBM/techno
from brand docs (in progress) · Look-01 type system (approved) · Look-03 colour numbers ·
Look-04 image DNA + motifs · Look-08 shoot catalogue.
Floor 2: Words-02 positioning v2 · Look-02 logo mark · Look-05 face rules · Look-06 motion +
anti-brand · Look-09 own edit recipe · Look-07 frame.md v1.
Floor 3: Formats-01 fixed set per single · Formats-02 reel rules (one craft file wins) ·
Formats-03 YouTube formats · Formats-04 TikTok formats.
Floor 4: Machine-01 who makes what · Machine-02 frame.md wired into HyperFrames + Canva Brand
Kit · Look-10 shoot in the machine · Machine-03 YouTube agent hooks · Machine-04 TikTok setup.
Floor 5: none yet (parent added when floor 3 is decided).
Floor 6: Mkt-01 "dark dance wave" SEO check (parked); categories Campaign, Engagement, Ads and
data, Curators and labels, Cadence, empty.
All proposed unless stated. Each ticket carries why / serves / question before Amir sees it.

## Out of scope now
Write routes or forms on the page; links from tickets to releases or video projects; a
published (artifact) copy of the board; Marketing tickets beyond Mkt-01.

## Testing
- Validator unit tests: missing field, bad status, bad category, duplicate id, dangling
  `blocked_on`, valid seed passes.
- Route test: `/board` returns 200 and contains every seed ticket id; derived blocked status
  shown for a ticket whose parent is not done.
- Manual: open the page in the RM, click a card, toggle filters.
