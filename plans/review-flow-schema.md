# Review flow schema (System 82, card M10)

Built 2026-11-06. Spec: `plans/strategy/gero-cp-deep-dive-2026-11-06.md` section C.
Placement: `plans/strategy/rm2-dry-run-2026-11-06.md` section 1c (Work area; the routes
sit in `release_manager/webapp.py` next to the clips route until the RM 2.0 split moves
them to `views/work.py`, same endpoint names).

Principle: a file is identified by its path and its SHA-256, never by a folder or a name.
Approval is a field in the release JSON. The agent writes files and records, Amir decides.
The code never posts, moves, renames, deletes, approves or marks used by itself.

## Where

- Model, hashing, state machine, checks, export, demo: `release_manager/review.py`
- Page: RM `/review` (`review_page`), filters `?release=<slug>` and `?area=<area>`, `?demo=1`
  renders a throwaway release in memory (nothing written)
- Thumbnail: `GET /review/thumb/<slug>/<item_id>` (path comes from the JSON, never the request)
- Tick: `POST /api/review/<slug>/<item_id>` with `{action: approve | change | drop, note, sha256}`
- Phone export: `plans/review-export-<slug>.json` (`python3 release_manager/review.py export <slug>`)
- Tests: `tests/test_review.py`

## The block, inside `releases/<slug>.json`

```
"review": {
  "version": 1,
  "updated_at": "2026-11-06T18:02:00",
  "consumed_ticks": ["<page db doc id>"],  # phone ticks already looked at, never imported twice
  "items": {
    "r-001": {
      "id": "r-001",
      "kind": "render",                      # render / cover / caption / post-draft / canvas
      "label": "reel, 9:16, cut 3",
      "area": "socials",                     # release / socials / booking / income / studio / system
      "destination": ["reel_instagram"],     # video_resizer.py / artwork_resizer.py preset keys
      "path": "videos/half-the-night/renders/reel-v3.mp4",   # relative to the repo or absolute; never changes
      "sha256": "...",                       # the BOUND hash, written once at submit, never rewritten
      "observed_sha256": "...",              # what the last re-hash saw on disk
      "bytes": 48213340,
      "probe": {"width": 1080, "height": 1920, "duration": 14.9, "fps": 30.0, "codec": "h264",
                "has_audio": true, "audio_codec": "aac"},
      "created": "2026-11-06T13:10:00", "made_by": "claude",
      "text": null,                          # captions and post drafts carry their text here (hash of the text)
      "text_boxes": [[200, 900, 600, 120]],  # optional [x, y, w, h] of readable type, for the safe-zone chip
      "version": 3, "supersedes": "r-000", "superseded_by": null,
      "state": "needs-you",
      "note": "",                            # the latest note (his, or the code's "file changed ..." line)
      "checks": [{"name": "hash", "pass": true, "reason": "1e69c02ce455"}],
      "approved": {"by": "amir", "at": "...", "sha256": "..."},   # null until he says yes
      "proposed": {"action": "approve", "note": "", "by": "phone", "at": "...", "tick_id": "..."},   # a phone tick; the state does not move until his local confirm
      "used": {"where": "instagram", "at": "...", "by": "amir", "ref": "post url"},   # null until his words
      "ticks": {"by": "amir", "at": "...", "via": "rm", "note": ""},   # his last tick
      "history": [{"state": "draft", "by": "claude", "at": "...", "via": "chat", "note": ""}]
    }
  }
}
```

## States

| State | Meaning | Who moves it there |
|---|---|---|
| `draft` | made, checks not run | `new_item` + `add_item` (agent) |
| `needs-you` | waiting for him, chips visible | `submit` (agent, after the checks); the code, when an approved file changed |
| `approved` | he said yes to this hash | his tick, with the hash he saw |
| `change` | he wants a change, note attached | his tick (note required) |
| `dropped` | not this one; the file stays | his tick |
| `superseded` | replaced by a newer item (`superseded_by`) | `add_item(..., supersedes=)` |
| `used` | it went out | `mark_used`, from his words only (CLI `used`, no route) |

Allowed steps (`TRANSITIONS`): draft -> needs-you / dropped / superseded; needs-you -> approved /
change / dropped / superseded; change -> needs-you (a new submit) / dropped / superseded;
approved -> used / change / dropped / needs-you (file changed) / superseded; used, dropped and
superseded are final. A phone tick is not a step: it only fills `item.proposed` (below). A used item can still be superseded by a newer one; it stays used.

## Hash binding

- `sha256` is computed once (file bytes, or the UTF-8 text) and never rewritten. Re-hashes write
  `observed_sha256` and the `hash` chip.
- **approve** needs three equal hashes: the one in the tick (what the reviewer saw), the bound
  `sha256`, and the file on disk now. Disk differs: refused with `file changed after approval`
  and the item is flagged (approved items go back to needs-you, note set, approval cleared).
  Tick differs: refused with `hash mismatch`. Any failing chip (`gate == held`): refused with
  `held: <chips> failing, a new version is needed`. (The spec's "he may approve a held item"
  line is not honoured; the security review asked for the refusal. Change and drop still work
  on a held item.)
- `refresh(rel)` runs on every `/review` GET: an approved item whose file changed falls back to
  needs-you with the note and the page saves the release (backup first); a needs-you item whose
  file changed gets a failing hash chip. Nothing else is written on a GET.
- A new version is a NEW item with `supersedes`; approval never carries over.

## Chips (`run_checks`)

| chip | pass / fail / na | how |
|---|---|---|
| `hash` | disk equals the bound hash | SHA-256, file missing = fail |
| `format` | size per destination preset | `video_resizer.VIDEO_EXPORTS` for render/canvas, `artwork_resizer.EXPORTS` for cover, via the bundled imageio-ffmpeg probe / PIL; unknown preset = fail; no destination = na |
| `duration` | inside the preset's min/max | ffmpeg probe (canvas 3 to 8 s, reels max 180 s) |
| `audio` | stream present where the preset wants one, silent where it must be | ffmpeg probe |
| `safe-zone` | Meta 270 / 672 / 65 on 9:16 | from `text_boxes` (scaled to the frame); no boxes = manual; not 9:16 = na |
| `no-text-over-face` | manual | `set_manual_check` keeps his word across re-runs |
| `first-3s` | manual (no branding in the first 3 s) | same |
| `copy` | no em-dashes; `caption_check.check` has no FAIL | WARNs pass with a count |
| `handles` | every @handle known (own + IG tracker + target list) | unknown = `? unverified: @x`, never pass, not a fail |

`gate(item)`: held when any chip fails, pending when none ran, passed otherwise. Held items sit
on top of needs-you.

## The page

RM `/review`: grouped by release (newest activity first), inside a release needs-you first with
held on top (a row with a phone proposal rises inside its state), then change, draft, approved; done items (used / dropped / superseded) collapse under
"Done". A row = thumbnail or text preview, state and held pills, label, kind, area emoji, version,
who, file name, size, hash, destinations, probe, chips as words (pass sage, fail oxblood with the
reason, unverified champagne with the question, manual dashed, na dim), note, Approve / Change /
Drop, a note field. Keys: j / k move, a / c / d act on the selected row, n focuses the note, Escape
leaves it. Approve is disabled on held and change-state rows. No delete, move, rename or post
exists on the page or in the API; `used`, `delete` and any other action get a 400.

## Phone page (built 2026-11-06)

Live: https://claude.ai/artifact/D9BYUSMqNCgVbSiDrEsKVL (private, db collection `ticks`). Rebuild: `python3 release_manager/review.py export <slug>` then `python3 plans/review-page/gen.py`, publish `plans/review-page/review.html` to the same URL. Read back: ArtifactData list `ticks` with out_dir, then `python3 plans/review-page/read_ticks.py <out_dir>` (proposals only), then Amir confirms at the desk.


`export <slug>` writes `plans/review-export-<slug>.json`: open items with chips, text, a JPEG
thumbnail (data URI) and the item's `sha256`. The file holds no secret because the page is
readable, so nothing in it grants anything. The System chat publishes it with the outreach-page
pattern (`plans/outreach-page/gen.py`, private claude.ai page, db collection `ticks`).

A tick is `{tick_id, id, action, note, sha256, at}` (`tick_id` = the page db doc id).
`import_ticks(rel, ticks)` never changes `state`: a valid tick (known open item, `sha256` equal
to the bound hash AND to the file on disk, change with a note) fills `item.proposed`
`{action, note, by: phone, at, tick_id}`; a later valid tick replaces the earlier proposal. The
page shows it as a dashed chip next to the real state ("phone: approve?"). The real step to
approved / change / dropped happens only locally: the RM page keystroke, or
`python3 release_manager/review.py confirm <slug> <item>` which the System chat runs on Amir's
words; both go through `tick()` and record `by: amir`. A local tick may overrule the proposal.
Every `tick_id` goes into `review.consumed_ticks` (refused ones too), so a replayed tick is
ignored. The proposal is cleared by the local tick and when the file changes (`refresh`).
`tick(..., via="phone")` is refused by design.

## Agent CLI

```
python3 release_manager/review.py add <slug> --kind render --label "..." --path ... --dest reel_instagram [--supersedes r-001]
python3 release_manager/review.py check <slug> [r-001]
python3 release_manager/review.py export <slug> [--no-thumbs]
python3 release_manager/review.py confirm <slug> r-001 [--action approve|change|drop] [--note ...]   # his words on a phone proposal
python3 release_manager/review.py used <slug> r-001 --where instagram --ref <url>   # his words only
python3 release_manager/review.py list <slug>
python3 release_manager/review.py --demo                                              # temp dir, nothing in releases/
```

Every save backs the release file up once per day (`<slug>.bak.<date>_review.json`).
