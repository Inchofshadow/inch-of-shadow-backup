#!/bin/bash
# DRAFT, not installed, needs the SC chat's ok + Amir's yes
#
# SC discovery refresh on launchd (replaces the Claude tasks sc-weekly-health 06:30,
# sc-refresh-0730 and, if the SC chat agrees, sc-refresh-0830). One script, three
# calendar slots (see com.inchofshadow.sc-refresh.plist.draft). Each slot runs
# scene_intelligence/sc_weekly_health.py exactly as the three tasks do today:
# gated on pauses.sc + SC cooldowns, stops at the hourly API budget, appends to
# today's discovery file, writes docs/reports/sc-weekly-YYYYMMDD.md.
#
# What changes: no chat per run. One line per run goes to
# docs/reports/sc-refresh-launchd.log; the 20:00 digest already reads the
# sc-weekly file (stats/socials_digest.py line 110). A macOS notification fires
# only for RECIPROCATOR CHURN or a non-zero exit. The 08:30 slot makes the same
# local data commit the sc-refresh-0830 task makes today (never a push).
#
# Interpreter: the python3.9 that has Full Disk Access (same as stats-sync).
# Install path when approved: deploy/launchd/sc_refresh.sh (chmod +x).

set -u
PY="/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9"
REPO="/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode"
LOG="$REPO/docs/reports/sc-refresh-launchd.log"
export PYTHONWARNINGS="ignore::Warning"

cd "$REPO" || { echo "repo missing" >> "$LOG"; exit 90; }

HOUR=$(date +%H)
STAMP=$(date "+%Y-%m-%d %H:%M")
TODAY=$(date +%Y%m%d)
case "$HOUR" in
  06) SLOT=1 ;;
  07) SLOT=2 ;;
  08) SLOT=3 ;;
  *)  SLOT=x ;;   # a manual run or a catch-up after sleep: no commit
esac

notify() {
  /usr/bin/osascript -e "display notification \"$2\" with title \"$1\"" >/dev/null 2>&1
}

OUT=$("$PY" scene_intelligence/sc_weekly_health.py 2>&1)
RC=$?

{
  echo "=== $STAMP refresh $SLOT/3 exit=$RC"
  echo "$OUT" | grep -E "seeds crawled|Rate budget|Same-day merge|New follow-backs|Stopped following back|RECIPROCATOR CHURN|STOP:|SUCCESS|Followers:|Following:"
} >> "$LOG"

if echo "$OUT" | grep -q "RECIPROCATOR CHURN"; then
  notify "SC refresh $SLOT/3" "RECIPROCATOR CHURN DETECTED. Read docs/reports/sc-weekly-$TODAY.md"
fi

if [ "$RC" -ne 0 ]; then
  # sc_weekly_health.py: 1 token expired, 2 CAPTCHA, 3 API budget, 4 health error;
  # a pause or cooldown stops it before the API with its own non-zero exit.
  notify "SC refresh $SLOT/3" "exit $RC (1 token, 2 CAPTCHA, 3 budget, 4 health, other = gate). See sc-refresh-launchd.log"
  exit "$RC"
fi

if [ "$SLOT" = "3" ]; then
  # Same files and message as the sc-refresh-0830 task today. Local only, never push.
  /usr/bin/git add scene_intelligence/sc_follow_tracker.json \
                   scene_intelligence/sc_following_audit.json \
                   scene_intelligence/discovery_candidates_*.json \
                   scene_intelligence/sc_seed_rotation.json \
                   docs/reports/sc-weekly-*.md >> "$LOG" 2>&1
  /usr/bin/git commit -q -m "data(sc): daily refresh" >> "$LOG" 2>&1 \
    || echo "commit: nothing to commit or git error (see above)" >> "$LOG"
fi

exit 0
