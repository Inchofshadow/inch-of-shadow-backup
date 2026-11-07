# archive/root-tools

What: `description_scorer.py`, a root tool that scored a bio before posting (284 lines).

Why: dead-code list `plans/strategy/dead-code-list-2026-11-05.md` row A6 (part). Nothing imports
or calls it (no code, test, scheduled task, launchd job, skill or doc); `caption_check` and the SEO
checks in the Release Manager do this job now. `letter_slides.py` from the same row stays at the
repo root (three brand docs still name it).

Date: 2026-11-07. Approved by Amir 2026-11-07 ("Yes, your picks").

Undo (from the repo root):

```bash
git mv archive/root-tools/description_scorer.py description_scorer.py
git rm -q archive/root-tools/README.md
```
