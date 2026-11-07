#!/bin/bash
# DRAFT, not installed, needs the SC chat's ok + Amir's yes
#
# SC 13:00 retry gate on launchd. Today the Claude task sc-engagement-retry opens a
# chat every day at 13:00, runs `sc_engagement.py --retry-gate` and in all 12 runs so
# far printed SKIP (or failed on the network). Only when the verdict is RUN is a
# browser session needed, and that needs Claude.
#
# This wrapper runs the same gate without a chat:
#   SKIP -> one line in docs/reports/sc-retry-gate.log, nothing else
#   RUN  -> the log line + a macOS notification "start the retry"; Amir or the SC chat
#           presses Run now on the sc-engagement-retry task (kept registered, its
#           daily cron removed or the task disabled: the SC chat's call)
#   no verdict (script error) -> notification with the exit code
#
# The gate is local only (reads scene_intelligence/engagement_log.json and the
# autonomy state); no SoundCloud call. Verified 2026-11-05 20:46 with the FDA python3.9:
# "RETRY VERDICT: SKIP (82 actions logged today, the 10:00 run worked)", exit 0.

set -u
PY="/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9"
REPO="/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode"
LOG="$REPO/docs/reports/sc-retry-gate.log"
export PYTHONWARNINGS="ignore::Warning"

cd "$REPO" || { echo "repo missing" >> "$LOG"; exit 90; }
STAMP=$(date "+%Y-%m-%d %H:%M")

notify() {
  /usr/bin/osascript -e "display notification \"$2\" with title \"$1\"" >/dev/null 2>&1
}

OUT=$("$PY" scene_intelligence/sc_engagement.py --retry-gate 2>&1)
RC=$?
VERDICT=$(echo "$OUT" | grep "RETRY VERDICT" | head -1)
TODAYLINE=$(echo "$OUT" | grep "^today:" | head -1)

echo "$STAMP | ${VERDICT:-no verdict} | ${TODAYLINE:-} | exit $RC" >> "$LOG"

case "$VERDICT" in
  *"RETRY VERDICT: RUN"*)
    notify "SC 13:00 retry" "The 10:00 run logged 0 actions. Start the retry: Run now on sc-engagement-retry."
    ;;
  *"RETRY VERDICT: SKIP"*)
    : # quiet by design
    ;;
  *)
    notify "SC 13:00 gate" "No verdict (exit $RC). See docs/reports/sc-retry-gate.log"
    ;;
esac

exit "$RC"
