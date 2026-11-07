#!/bin/bash
cd "/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode"

# Confirmation guard (audit item 25 leftover, added 2026-07-19): a stray
# double-click used to start a full re-enrichment of 750+ SC profiles with
# zero warning — hundreds of API calls against the SC pre-announce hard rule.
echo "This will RE-ENRICH ALL SoundCloud contacts (750+ profiles, two full"
echo "passes, several hundred SC API calls, ~30+ minutes)."
echo ""
read -r -p "Type YES (all caps) to continue, anything else aborts: " CONFIRM
if [ "$CONFIRM" != "YES" ]; then
    echo "Aborted. Nothing was run."
    exit 0
fi

LOG="/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode/sc_enrich_log_$(date +%Y%m%d_%H%M%S).txt"
echo "=== SC Re-Enrichment Run: $(date) ===" | tee "$LOG"
echo "" | tee -a "$LOG"
echo "--- Step 1: Re-enriching existing contacts (--force) ---" | tee -a "$LOG"
python3 scene_intelligence/enrich_soundcloud.py --force 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "--- Step 2: Finding SC profiles for contacts without SC data (--all) ---" | tee -a "$LOG"
python3 scene_intelligence/enrich_soundcloud.py --all 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "=== Done: $(date) ===" | tee -a "$LOG"
echo ""
echo "Log saved to: $LOG"
