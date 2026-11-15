# Gate: Layout page studio drawer and the shared tag list (⚙️ System 94) (2026-11-15, Fable, on Amir's "gate")

Opus built it on 11-11 (commit fd1c30e) after Amir ticked A (side drawer) + T1 (one fixed tag list). Read: `release_manager/studio_tags.py`, the drawer route in `views/playground.py`, `docs/brand/tags.json`. Tests: 16 pass.

## Verdict: approve with three small fixes.

| Claim | Checked | Result |
|---|---|---|
| The drawer only reads | the route `/api/playground/<slug>/drawer` | ✅ GET only, writes nothing, checks the release slug |
| Counts: Archive 24, Effects 287, Imagine 23, fonts with files | `tags.json` assign + the route | ✅ 24 / 287 / 23; 95 fonts are tagged and the drawer shows only those with a file on this Mac |
| Only tags from the list are used | every assigned tag against the 37 | ✅ 0 outside the list |
| Trial fonts are marked | the route passes `public_ok` per font | ✅ |
| Half the Night's data is unchanged | not re-proved here; the Layout chat proved it in one browser session (keep #50 identical) | accepted |

## Fixes
1. **65 items have no tag (59 effects, 6 archive references).** They never show under any tag chip, only in search. Tag them, or add an "untagged" chip so nothing hides.
2. **The tag text says "The rose, our symbol".** Roses are one of Amir's saved ideas (R-018) and a motif option in `frame.md`; nothing names the rose as the symbol, and the logo search is still open. Reword to "Roses (one of our motifs)". A tag list must not state taste Amir has not pinned.
3. **The new rule lives only in code comments.** "`docs/brand/tags.json` is the tag source from now on" is not in `docs/brand/README.md` or the toolkit, so other chats adding effects, fonts or references will not know. Add one line to the brand README.

## Small
- The `owl` tag has no item yet (the Half the Night owl lives in the cover layers, not in a library).
