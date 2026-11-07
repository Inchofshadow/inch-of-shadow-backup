# Parked: the Google Sheet push (M5, 2026-11-07)

Amir's decision (strategy review, M5): the master sheet stays as it is and gets no more pushes from Scene Intelligence. Parked here: `push_to_sheets.py`, `sync.sh`, `runsync`, `test_sheets_sync_safety.py`. The /sync, /discover and /enrich skills are marked parked.

Undo:
```
git mv archive/si-sheet/push_to_sheets.py scene_intelligence/
git mv archive/si-sheet/sync.sh .
git mv archive/si-sheet/runsync .
git mv archive/si-sheet/test_sheets_sync_safety.py tests/
```
