---
name: sync
description: Sync Scene Intelligence and Release Manager data, then push to Google Sheets. Use when the user says "sync", "push to sheets", "update sheets", or wants to sync RM and SI data.
user_invocable: true
---

> **PARKED 2026-11-07 (strategy review M5, Amir's yes):** the Google Sheets push is retired: Amir decided on 2026-11-07 that the master sheet stays as it is and gets no more pushes; `push_to_sheets.py` lives in `archive/si-sheet/`. This skill does nothing now. Run any step only when Amir asks for it in that task; never on a routine.

# Sync SI + RM -> Google Sheets

Run the full sync pipeline: pull manual edits from Sheets, merge with local data (enriched_contacts.json + engagement_log.json), then push everything back to Sheets.

## Steps

1. Run `python3 scene_intelligence/push_to_sheets.py` from the project root (with sync-back enabled by default)
2. Report what was synced (manual Sheet edits pulled, rows pushed, label tiers generated)
3. If the user says "no sync" or "just push", use `--no-sync` flag to skip pulling Sheet edits

## Notes

- RM and SI share `scene_intelligence/enriched_contacts.json` -- no separate merge needed
- Genre tags, engagement, promotion data from RM are already in the shared files
- Sheet manual edits (category, genre, delete, score, promo_list) sync back on pull
- Label tiers JSON auto-regenerates on every push
- Label row colors (green/yellow/red) and DJ boss gold rows auto-apply
