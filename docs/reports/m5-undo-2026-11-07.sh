#!/bin/bash
# M5 dead-code moves of 2026-11-07: undo script.
# Puts every file moved by the M5 commits back where it was, newest group first.
# Run from anywhere; it changes to the repo root. Review `git status` after, then commit.
# Groups NOT moved on 2026-11-07 (A2 si-sheet, A3, A4, letter_slides) are not touched here.
set -e
cd "/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode"

# A7 look02-duplicates
for p in logo_v3 logo_v2 compare_v2 moon logo_round_g logo_round_f logo_round_e logo_round_d logo_round_c logo_round_b logo_sketches families all_picks; do
  git mv "archive/look02-duplicates/$p.py" "references/look02/scripts/$p.py"
done
git rm -q archive/look02-duplicates/README.md

# A6 root-tools (description_scorer only)
git mv archive/root-tools/description_scorer.py description_scorer.py
git rm -q archive/root-tools/README.md

# A5 rm-cli
git mv archive/rm-cli/cli.py release_manager/cli.py
git rm -q archive/rm-cli/README.md

# A1 si-discovery
git mv archive/si-discovery/run_sc_enrich.command run_sc_enrich.command
for p in enrich_soundcloud scene_plan_recency_filter scrape_label_emails classify_subtypes update_scores fetch_youtube_subs re_enrich_discogs enrich_youtube enrich_urls enrich_spotify enrich_contacts extract_rekordbox discover_contacts; do
  git mv "archive/si-discovery/$p.py" "scene_intelligence/$p.py"
done
git rm -q archive/si-discovery/README.md

# This undo script itself was added in the last M5 commit; remove it by hand if wanted:
#   git rm docs/reports/m5-undo-2026-11-07.sh
echo "M5 moves undone. Check: git status; python3 -m pytest tests -q"
# A2 si-sheet (moved after the /sync skill was parked)
git mv archive/si-sheet/push_to_sheets.py scene_intelligence/
git mv archive/si-sheet/sync.sh .
git mv archive/si-sheet/runsync .
git mv archive/si-sheet/test_sheets_sync_safety.py tests/
