#!/bin/bash
# DRAFT, not installed, needs the SC chat's ok + Amir's yes
#
# SoundCloud release stats for The Deceiver and Farewell on launchd, replacing the
# Claude task sc-weekly-release-stats (Fri 18:00). Runs scene_intelligence/sc_release_stats.py
# exactly as the task does: two read-only /resolve calls, one datapoint per track appended
# to releases/<slug>.json (de-duplicated by date, backup made by the script). The script
# prints the plays/likes/reposts table; this wrapper appends it to
# docs/reports/sc-release-stats-launchd.log and notifies only on an error or NO DATA.
#
# Cadence: the plist carries the task's Friday 18:00. The audit's suggestion is monthly
# (both tracks are 4-6 months old); for that, replace StartCalendarInterval in the plist
# with Day 1 / Hour 12 / Minute 10 (right before the SC maintenance task reads the files).
# Nobody reads the weekly chat today; the release JSON is read by the Release Manager.

set -u
PY="/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9"
REPO="/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode"
LOG="$REPO/docs/reports/sc-release-stats-launchd.log"
export PYTHONWARNINGS="ignore::Warning"

cd "$REPO" || { echo "repo missing" >> "$LOG"; exit 90; }
STAMP=$(date "+%Y-%m-%d %H:%M")

notify() {
  /usr/bin/osascript -e "display notification \"$2\" with title \"$1\"" >/dev/null 2>&1
}

OUT=$("$PY" scene_intelligence/sc_release_stats.py 2>&1)
RC=$?

{
  echo "=== $STAMP sc_release_stats exit=$RC"
  echo "$OUT" | grep -v "NotOpenSSLWarning\|warnings.warn"
} >> "$LOG"

if [ "$RC" -ne 0 ] || echo "$OUT" | grep -q "NO DATA"; then
  notify "SC release stats" "exit $RC or NO DATA. See docs/reports/sc-release-stats-launchd.log"
fi

exit "$RC"
