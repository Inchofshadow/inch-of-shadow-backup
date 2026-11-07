# Loop Closer — post-session automation

**Built 2026-07-19 at Amir's request: close every post-session loop without him.**

One command replaces the manual post-session ritual (merge, integrity check,
scoring, scorecard, pool check, report):

```
python3 scene_intelligence/close_loops.py                # both platforms, today
python3 scene_intelligence/close_loops.py --platform ig  # one platform
python3 scene_intelligence/close_loops.py --date 2026-07-20
```

## What it does

**IG:** runs the merge (fabrication guard + non-session-day gate included,
NEVER with --force), analyses the session for violations (reciprocator churn,
cap breaches, detection signals, skip ratio), scores it 0-10 on a
deterministic rubric, appends an (auto) row to `docs/ig-session-scorecard.md`,
checks vetted-pool depth (warns <= 30), and writes
`docs/reports/loop-close-ig-<date>.md`.

**SC:** reads the day's `sc_*` actions from the engagement log, checks SOP
caps (24 likes / 12 follows / 1 repost / 15 unfollows), scans the session
report for detection markers, scores 0-10, writes
`docs/reports/loop-close-sc-<date>.md`.

## Escalation rules (agreed with Amir 2026-07-19)

- **Immediate pause** regardless of score: fabrication-guard trip, detection
  signal (captcha / DataDome / rate limit / challenge), reciprocator churn,
  or any cap violation.
- **Trend pause:** two consecutive same-platform scores <= 5.
- While paused, the tool refuses to act (exit 3) and every report says
  **NEEDS AMIR**. Only Amir clears it: `close_loops.py --resume`.

State lives in `scene_intelligence/autonomy_state.json` (paused flag, recent
scores, processed dates).

## Standing approvals (Amir, 2026-07-19)

- SC: Wednesday health pass <= 30 API calls without per-run pre-announce;
  follow-back checks on their scheduled day. Anything beyond still asks.
- IG: one API script per day (ledger-enforced), scheduled days only.
- The Chrome click sessions themselves stay supervised — Amir present. That
  is deliberate (2026-07-18 fabrication incident) and not to be automated
  without a new explicit decision.

## Not yet: background scheduling

Running this on a timer with no human present requires the project folder to
move out of ~/Desktop (macOS TCC blocks background processes from Desktop —
proven by audit item 25). Decision pending with Amir. Until then: Amir runs
one command (or asks Claude) after each session.
