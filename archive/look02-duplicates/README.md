# archive/look02-duplicates

What: the 13 logo scripts from `references/look02/scripts/` (1,734 lines). Each one is a
byte-identical copy (md5 checked 2026-11-07) of a script that stays beside the renders:
`references/look02/` (all_picks, families, logo_sketches, logo_round_b to logo_round_g),
`references/look02/moon/moon.py`, `references/look02/v2/` (compare_v2, logo_v2),
`references/look02/v3/logo_v3.py`.

Why: dead-code list `plans/strategy/dead-code-list-2026-11-05.md` row A7. Two copies of the same
code; the copy beside the 27 renders stays. Nothing imports or calls the `scripts/` copies.
`references/look02/scripts/pull/` and `cover_notype.png` stay where they are.

Date: 2026-11-07. Approved by Amir 2026-11-07 ("Yes, your picks").

Undo (from the repo root):

```bash
for p in all_picks families logo_sketches logo_round_b logo_round_c logo_round_d logo_round_e logo_round_f logo_round_g moon compare_v2 logo_v2 logo_v3; do git mv "archive/look02-duplicates/$p.py" "references/look02/scripts/$p.py"; done
git rm -q archive/look02-duplicates/README.md
```
