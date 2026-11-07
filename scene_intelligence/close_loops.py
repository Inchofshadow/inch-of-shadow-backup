"""close_loops.py — post-session loop closer (built 2026-07-19, Amir's request).

One command closes everything Amir used to do by hand after an engagement
session:

  IG:  fabrication guard -> merge -> violation/integrity analysis ->
       auto-score 0-10 -> scorecard row -> pool-depth check -> report file
  SC:  day's engagement-log analysis -> caps compliance -> detection scan ->
       auto-score 0-10 -> report file

Escalation (agreed 2026-07-19):
  IMMEDIATE PAUSE — regardless of score — on any of: fabrication-guard trip,
  detection signal (captcha / rate-limit / challenge / DataDome), reciprocator
  churn, or a cap violation.
  TREND PAUSE — two consecutive scores <= 5 on the same platform.
  While paused, this tool refuses to act (observe-and-report only) until Amir
  reviews and runs `--resume`.

Usage:
  python3 scene_intelligence/close_loops.py                # both platforms, today
  python3 scene_intelligence/close_loops.py --platform ig  # one platform
  python3 scene_intelligence/close_loops.py --date 2026-07-20
  python3 scene_intelligence/close_loops.py --resume --platform ig|sc   # Amir clears THAT platform's pause

Exit codes: 0 ok, 1 nothing to do, 2 escalation fired, 3 paused (needs Amir).
"""
from __future__ import annotations

import argparse
import io
import contextlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

SI_DIR = Path(__file__).parent
BASE_DIR = SI_DIR.parent
REPORTS_DIR = BASE_DIR / "docs" / "reports"
SCORECARD = BASE_DIR / "docs" / "ig-session-scorecard.md"
STATE_FILE = SI_DIR / "autonomy_state.json"
TRACKER_FILE = SI_DIR / "ig_follow_tracker.json"
TARGET_LIST_FILE = SI_DIR / "ig_target_list.json"
ENG_LOG_FILE = SI_DIR / "engagement_log.json"

try:
    from scene_intelligence.json_io import atomic_write_json, load_json_checked
except ImportError:
    from json_io import atomic_write_json, load_json_checked

# SC caps are read LIVE from sc_engagement_config (SC-04, 2026-09-01: config
# is THE LAW; this scorer and the SOP only mirror it). Same lesson as IG:
# hardcoding caps here meant a session obeying its own config could score
# "cap violations" and pause autonomy for doing what it was told.
try:
    from scene_intelligence import sc_engagement_config as _scc
except ImportError:
    try:
        import sc_engagement_config as _scc  # script-dir invocation
    except ImportError:
        _scc = None

SC_FOLLOW_TARGET = getattr(_scc, "SESSION_FOLLOWS", 12)
SC_PASS_A_LIKES = getattr(_scc, "SESSION_WARMUP_LIKES", 12)  # one prelike per follow
SC_PASS_C_MAX = getattr(_scc, "SESSION_PASSC_MAX", 12)       # maintenance-like ceiling
SC_CAPS = {
    "sc_like": SC_PASS_A_LIKES + SC_PASS_C_MAX,
    "sc_follow": SC_FOLLOW_TARGET,
    "sc_repost": 1,
    "sc_unfollow": getattr(_scc, "UNFOLLOWS_PER_SESSION", 15),
}
# Total clicks one session should stop at (2026-09-24). Over it = a pacing
# WARNING in the report, never a pause: the throttle is a pacing signal (SOP 3c).
SC_ACTION_STOP = getattr(_scc, "SESSION_ACTION_STOP", 60)

# Strings that mean the platform pushed back. Case-insensitive scan of raw
# session artifacts. Any hit = immediate pause.
DETECTION_MARKERS = ("captcha", "datadome", "rate limit", "rate-limit",
                     "challenge_required", "feedback_required", "suspect",
                     "circuit_breaker", "429")

CLASS_C_SKIP_THRESHOLD = 5  # SOP: 5 consecutive skips -> CC stops the session
TREND_PAUSE_THRESHOLD = 5   # two consecutive scores <= this pause autonomy
TREND_PAUSE_COUNT = 2
ZERO_ACTION_SCORE_CAP = 3  # a day with zero logged actions scores at most this (2026-09-11)
POOL_DEPTH_WARN = 30        # Amir's standing threshold (2026-06-14)


# ---------------------------------------------------------------------------
# Autonomy state
# ---------------------------------------------------------------------------

def notify_mac(title: str, message: str) -> None:
    """Local macOS notification — reaches Amir even with no Claude session.

    Only called for problems (pauses / NEEDS AMIR), per Amir 2026-07-19:
    "send me a msg and tell me something is wrong, broken or needs my
    decision" — routine successes stay in the report files.
    """
    try:
        import subprocess
        safe_t = title.replace('"', "'")
        safe_m = message.replace('"', "'")[:200]
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{safe_m}" with title "{safe_t}" sound name "Basso"'],
            capture_output=True, timeout=10)
    except Exception:
        pass  # notification is best-effort; the report file is the record


def load_state() -> dict:
    state = load_json_checked(STATE_FILE, None, what="autonomy state")
    if state is None:
        state = {"pauses": {"ig": None, "sc": None},
                 "recent": [], "processed": {"ig": [], "sc": []}}
    # 2026-07-24 split: pauses are PER PLATFORM. A single global `paused` flag
    # let an SC captcha gate IG (and an IG-motivated --resume un-gate SC) even
    # though the platforms are unrelated. Migrate any legacy global pause to the
    # platform named in its reason.
    if "pauses" not in state:
        state["pauses"] = {"ig": None, "sc": None}
        if state.get("paused"):
            legacy = {"reason": state.get("paused_reason") or "unknown (migrated)",
                      "at": state.get("paused_at")}
            low = str(legacy["reason"]).lower()
            sc_hit = "sc" in low or "soundcloud" in low
            ig_hit = "ig " in low or "ig:" in low or "instagram" in low
            if sc_hit and not ig_hit:
                state["pauses"]["sc"] = legacy
            elif ig_hit and not sc_hit:
                state["pauses"]["ig"] = legacy
            else:  # ambiguous -- keep both gated, safe default
                state["pauses"]["ig"] = dict(legacy)
                state["pauses"]["sc"] = dict(legacy)
        for k in ("paused", "paused_reason", "paused_at"):
            state.pop(k, None)
    state["pauses"].setdefault("ig", None)
    state["pauses"].setdefault("sc", None)
    state.setdefault("recent", [])
    state.setdefault("processed", {"ig": [], "sc": []})
    return state


def platform_paused(state: dict, platform: str) -> dict | None:
    """Return the pause record for this platform, or None if not paused."""
    return (state.get("pauses") or {}).get(platform)


def save_state(state: dict) -> None:
    atomic_write_json(STATE_FILE, state)


def record_score(state: dict, platform: str, day: str, score: int,
                 immediate_pause: str | None,
                 counts_for_trend: bool = True) -> str | None:
    """Record a score, apply escalation rules. Returns pause reason or None.

    counts_for_trend=False records the score but keeps it out of the TREND
    PAUSE (2026-09-11): a zero-action session stopped from outside is an
    honest low score, not a failing trend, and freezing SC over it would stop
    the automation without Amir's approval (his 2026-09-09 law)."""
    rec = {"date": day, "platform": platform, "score": score}
    if not counts_for_trend:
        rec["trend"] = False
    state["recent"].append(rec)
    state["recent"] = state["recent"][-20:]

    if immediate_pause:
        state["pauses"][platform] = {
            "reason": immediate_pause,
            "at": datetime.now().isoformat(timespec="seconds"),
        }
        return immediate_pause

    same = [r["score"] for r in state["recent"]
            if r["platform"] == platform and r.get("trend", True)]
    if (len(same) >= TREND_PAUSE_COUNT
            and all(s <= TREND_PAUSE_THRESHOLD
                    for s in same[-TREND_PAUSE_COUNT:])):
        reason = (f"{TREND_PAUSE_COUNT} consecutive {platform.upper()} scores "
                  f"<= {TREND_PAUSE_THRESHOLD}: {same[-TREND_PAUSE_COUNT:]}")
        state["pauses"][platform] = {
            "reason": reason,
            "at": datetime.now().isoformat(timespec="seconds"),
        }
        return reason
    return None


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

# Words that mean a nearby detection marker is being DENIED, not reported.
# Added 2026-08-12: reports routinely say "No CAPTCHAs, no DataDome challenges
# today", and the old naive substring match scored that as a real detection,
# costing -5 and triggering an immediate autonomy pause on clean sessions
# (2026-07-23 and 2026-08-06 both hit this). CC flagged it on 2026-07-23 and it
# went unactioned.
NEGATION_CUES = ("no ", "none", "zero ", "without", "not ", "never",
                 "didn't", "did not", "free of", "clear of", "n/a")

_SEGMENT_SPLIT = re.compile(r"[.!?\n;]+")

# A bare-number marker ("429") is a detection signal only in an HTTP-ish
# context. Added 2026-09-07: Laura Aha's follower count (429) in a session
# report's unfollow table scored -5 and paused SC autonomy — same false-
# positive class as the old "No CAPTCHA" hit.
_NUMERIC_MARKER_CONTEXT = re.compile(
    r"http|error|status|retry|too many|rate|response|returned|received|got|hit",
    re.IGNORECASE)


def scan_for_detection(text: str) -> list[str]:
    """Detection markers that are actually ASSERTED, not denied.

    Scans sentence by sentence so a negation in one sentence cannot suppress a
    genuine report in the next.
    """
    if not text:
        return []
    hits: list[str] = []
    for segment in _SEGMENT_SPLIT.split(text.lower()):
        if not segment.strip():
            continue
        for marker in DETECTION_MARKERS:
            idx = segment.find(marker)
            if idx == -1:
                continue
            if marker.isdigit():
                # word-boundary (so "1429" never matches) + HTTP-ish context
                if not re.search(r"\b" + marker + r"\b", segment):
                    continue
                if not _NUMERIC_MARKER_CONTEXT.search(segment):
                    continue
            before = segment[:idx]
            if any(cue in before for cue in NEGATION_CUES):
                continue        # denial, e.g. "no captcha"
            hits.append(marker)
    return hits


def _target_shortfall(counts: dict[str, int], targets: dict[str, int]) -> list[str]:
    """Deductions for under-delivering against the phase/SOP targets.

    Added 2026-07-20 after the first live run scored 10/10 on 6/10 follows,
    15/25 likes and 4/8 unfollows. A score that ignores volume is useless as
    an escalation signal: sessions can quietly decay to zero while reporting
    perfect health. Growth is the point (Amir's own KPI is followers going
    up), so missing targets must cost points.
      < 50% of target -> -3 (severe)
      < 80% of target -> -1 (mild)
    """
    out: list[str] = []
    for action, target in targets.items():
        if target <= 0:
            continue
        got = counts.get(action, 0)
        ratio = got / target
        if ratio < 0.5:
            out.append(f"-3 severe shortfall: {action} {got}/{target}")
        elif ratio < 0.8:
            out.append(f"-1 shortfall: {action} {got}/{target}")
    return out


def ig_caps() -> dict[str, int]:
    """Violation ceiling = phase target + the POSITIVE session jitter the config
    itself authorizes (SESSION_JITTER rolls each session's targets up/down for
    anti-pattern variance), + 1 like for the prominent-like slot.

    Comparing against the bare target false-flagged twice: 2026-07-24 (prelike
    double-count) and 2026-07-25, where the PLAN itself said 26 likes / 9
    unfollows (jitter-rolled) and CC executed it exactly — a session must never
    be paused for following its own plan."""
    caps = dict(_ig_targets())
    try:
        try:
            from scene_intelligence import ig_engagement_config as cfg
        except ImportError:
            import ig_engagement_config as cfg
        jit = getattr(cfg, "SESSION_JITTER", {})
        caps["ig_like"] = caps.get("ig_like", 0) + max(0, jit.get("likes_per_session", (0, 0))[1]) + 1
        caps["ig_follow"] = caps.get("ig_follow", 0) + max(0, jit.get("follows_per_session", (0, 0))[1])
        caps["ig_unfollow"] = caps.get("ig_unfollow", 0) + max(0, jit.get("unfollows_per_session", (0, 0))[1])
    except Exception:
        pass  # fall back to bare targets
    return caps


def _ig_targets() -> dict[str, int]:
    """Current phase targets, read live from the engagement config."""
    try:
        try:
            from scene_intelligence import ig_engagement_config as cfg
        except ImportError:
            import ig_engagement_config as cfg
        lim = cfg.PHASE_LIMITS[cfg.CURRENT_PHASE]
        return {"ig_follow": lim["follows_per_session"],
                "ig_like": lim["likes_per_session"],
                "ig_unfollow": lim["unfollows_per_session"]}
    except Exception:
        return {}


def _growth_target(day: str) -> int | None:
    """The session's follow GOAL (phase target), not what the plan could
    offer. Read from the plan file's _meta.follows_target (2026-09-21).
    The score measures execution against the plan; this line keeps a thin
    supply night from hiding behind a good score (09-21: 9/10 at 4/12)."""
    try:
        data = json.loads((SI_DIR / f"session_plan_{day}.json").read_text(encoding="utf-8"))
        t = (data.get("_meta") or {}).get("follows_target")
        return int(t) if t is not None else None
    except (OSError, ValueError, TypeError, AttributeError):
        return None


def _plan_volumes(day: str) -> dict[str, int]:
    """Volumes the engine actually offered on `day` (session_plan_<day>.json).

    2026-09-07: the plan offered 7 follows / 5 likes / 0 unfollows (thin vetted
    pool, export-gated sweep); the session delivered all of it and still
    scored 5/10 against the config's 12/6/8. Supply is not a protocol
    shortfall. Missing/unreadable plan -> {} (targets fall back to config)."""
    try:
        data = json.loads((SI_DIR / f"session_plan_{day}.json").read_text(encoding="utf-8"))
        return {
            "ig_follow": len(data.get("reach_follows", [])),
            "ig_like": len(data.get("scene_likes", [])) + len(data.get("prominent_likes", [])),
            "ig_unfollow": len(data.get("unfollows", [])),
        }
    except (OSError, ValueError, AttributeError, TypeError):
        return {}


def _overdue_unfollows_remaining() -> int | None:
    """How many active follows are STILL due for unfollow (post-merge tracker).

    None = tracker unreadable (scorer then falls back to the bare phase target).
    Mirrors plan_unfollow_sweep's eligibility: past unfollow_after, not a
    reciprocator, not keep_following.
    """
    try:
        t = json.loads(TRACKER_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    today = date.today().isoformat()
    n = 0
    for e in t.get("active_follows", []):
        if e.get("followed_back") is True or e.get("keep_following") is True:
            continue
        due = str(e.get("unfollow_after") or "")
        if due and due <= today:
            n += 1
    return n


def zero_click_halt(events: list[dict]) -> bool:
    """True when the session halted (session_halt) with no like/follow/unfollow."""
    acts = {"ig_follow", "ig_like", "ig_unfollow"}
    halted = any(str(e.get("action") or e.get("type") or "") == "session_halt" for e in events)
    acted = any(str(e.get("action") or e.get("type") or "") in acts for e in events)
    return halted and not acted


def score_ig_session(events: list[dict], pre_reciprocators: set[str],
                     raw_text: str, merge_code: int) -> tuple[int, list[str], str | None]:
    """Deterministic 0-10 score. Returns (score, deductions, immediate_pause).

    Encodes the rubric items that actually moved historical scorecard scores;
    qualitative judgement (log honesty, caption quality) stays with Amir+Claude
    in the report review.
    """
    deductions: list[str] = []
    immediate: str | None = None
    score = 10

    counts: dict[str, int] = {}
    for ev in events:
        a = str(ev.get("action") or ev.get("type") or ev.get("event") or "")
        counts[a] = counts.get(a, 0) + 1

    # Like-before-follow prelikes belong to the FOLLOW budget (SOP mandates a
    # like before every reach follow), NOT the scene-like cap. Counting them as
    # scene likes false-flagged 2026-07-24 (19 scene + 8 prelikes = 27 raw >
    # cap 25 -> wrongly paused autonomy). Net them out of the ig_like count.
    def _h(ev: dict) -> str:
        return str(ev.get("handle") or ev.get("account")
                   or ev.get("username") or "").strip().lstrip("@").lower()
    prelikes = 0
    for i, ev in enumerate(events):
        a = str(ev.get("action") or ev.get("type") or ev.get("event") or "")
        if a != "ig_like" or i + 1 >= len(events):
            continue
        nxt = events[i + 1]
        na = str(nxt.get("action") or nxt.get("type") or nxt.get("event") or "")
        if na == "ig_follow" and _h(nxt) == _h(ev):
            prelikes += 1
    if prelikes and counts.get("ig_like"):
        counts["ig_like"] -= prelikes

    # Detection signals anywhere in the raw log
    hits = scan_for_detection(raw_text)
    if hits:
        score -= 5
        deductions.append(f"-5 detection signal(s) in log: {sorted(set(hits))}")
        immediate = f"detection signal in IG session log: {sorted(set(hits))}"

    # Reciprocator churn: an unfollow event on a handle that was followed_back
    churned = []
    for ev in events:
        a = str(ev.get("action") or "")
        if a.startswith("ig_unfollow") and "aborted" not in a:
            h = str(ev.get("handle") or "").strip().lstrip("@").lower()
            if h in pre_reciprocators:
                churned.append(h)
    if churned:
        score -= 4
        deductions.append(f"-4 reciprocator churn: {churned}")
        immediate = immediate or f"reciprocator churn: {churned}"

    # Cap violations — exceeding the phase cap, not merely reaching it
    for action, cap in ig_caps().items():
        n = counts.get(action, 0)
        if cap and n > cap:
            score -= 3
            deductions.append(f"-3 cap violation: {action} {n} > {cap}")
            immediate = immediate or f"cap violation: {action} {n} > {cap}"

    # Merge failed (fabrication guard / day gate handled upstream as pause)
    if merge_code not in (0,):
        score -= 3
        deductions.append(f"-3 merge exited {merge_code}")

    # High skip ratio: queue producing junk
    total = sum(counts.values())
    skips = sum(n for a, n in counts.items() if "skip" in a)
    if total and skips / total > 0.6:
        score -= 2
        deductions.append(f"-2 skip ratio {skips}/{total} (stale/junk queue)")

    # Zero substantive actions
    acted = sum(n for a, n in counts.items()
                if a in ("ig_follow", "ig_like", "ig_unfollow"))
    if acted == 0:
        score -= 2
        deductions.append("-2 zero substantive actions")

    # Under-delivery vs the phase targets (added 2026-07-20)
    # Deliberate unfollow SKIPS (protected / reciprocator guard refusals) are
    # the guard WORKING, not under-delivery — the slot was evaluated and
    # correctly refused. Credit them toward the unfollow target so a session
    # is never penalised for protecting followers (07-24: 3 done + 5 skips
    # scored "-3 severe shortfall 3/8" without this).
    # A session that stopped on the Class B/C consecutive-skip breaker OBEYED
    # the protocol -- it is not under-delivery. Signature: the log's trailing
    # events are >= CLASS_C_SKIP_THRESHOLD consecutive skips (SOP: 5 in a row
    # -> STOP). 2026-08-17 stopped correctly at 5 trailing skips and was scored
    # 1/10 (-3/-3/-3 volume shortfalls) for it, which armed a false trend pause.
    # Detection signals and cap violations above still apply, so a breaker stop
    # can never mask a CAPTCHA.
    trailing_skips = 0
    for ev in reversed(events):
        a = str(ev.get("action") or ev.get("type") or ev.get("event") or "")
        if "skip" in a:
            trailing_skips += 1
        else:
            break
    breaker_stop = trailing_skips >= CLASS_C_SKIP_THRESHOLD

    # T-006 (2026-08-31): safety and infrastructure halts are protocol
    # compliance, exactly like a breaker stop. August needed FOUR manual
    # rescores for this (08-07 token exhaustion 4->, 08-17 1->10, 08-26
    # Chrome renderer death 3->7, 08-28 deliberate P0 halt 1->8) because the
    # rule lived only in precedent. Contract: a session that ends early for a
    # good reason writes a final JSONL event
    #     {"action": "session_halt", "reason": "safety|infrastructure", ...}
    # (mandatory in the 2.0 playbook). Detection signals, cap violations and
    # churn deductions above STILL apply — a halt can never mask a CAPTCHA.
    halt_stop = None
    for ev in events:
        a = str(ev.get("action") or ev.get("type") or ev.get("event") or "")
        if a == "session_halt":
            reason = str(ev.get("reason", "")).lower()
            if reason.startswith(("safety", "infrastructure")):
                halt_stop = reason
    protocol_stop = breaker_stop or bool(halt_stop)

    shortfall_counts = dict(counts)
    if counts.get("ig_unfollow_skip"):
        shortfall_counts["ig_unfollow"] = (
            shortfall_counts.get("ig_unfollow", 0) + counts["ig_unfollow_skip"])

    # The unfollow target is SUPPLY-BOUND: a session can only unfollow accounts
    # that are actually due. Once the overdue backlog drains, holding sessions
    # to the phase ceiling punishes success (2026-08-15: only 2 accounts were
    # due, both processed, scored "-3 severe shortfall: ig_unfollow 2/8" and
    # nearly re-armed the trend pause). Cap the target at what was processed
    # plus what is STILL due after the merge -- if nothing due remains, the
    # session cleared its supply and owes nothing more.
    targets = dict(_ig_targets())
    # PLAN-BOUND targets (2026-09-07): never ask more than the plan file offered.
    day_of = ""
    for ev in events:
        ts = str(ev.get("ts") or ev.get("timestamp") or "")
        if len(ts) >= 10:
            day_of = ts[:10]
            break
    planned = _plan_volumes(day_of) if day_of else {}
    for k, v in planned.items():
        if k in targets:
            targets[k] = min(targets[k], v)
    remaining_due = _overdue_unfollows_remaining()
    if remaining_due is not None and "ig_unfollow" in targets:
        supply = shortfall_counts.get("ig_unfollow", 0) + remaining_due
        targets["ig_unfollow"] = min(targets["ig_unfollow"], supply)
    if breaker_stop:
        deductions.append(
            f"note: session stopped on the consecutive-skip breaker "
            f"({trailing_skips} trailing skips) -- volume targets not scored")
    elif halt_stop:
        deductions.append(
            f"note: session halted ({halt_stop}) -- protocol-compliant stop, "
            f"volume targets not scored (T-006 rule, precedents 08-07/08-17/"
            f"08-26/08-28)")
    for d in ([] if protocol_stop else _target_shortfall(shortfall_counts, targets)):
        score -= int(d.split()[0].lstrip("-"))
        deductions.append(d)

    return max(0, score), deductions, immediate


# Phrases that mean the session was cut short from OUTSIDE the protocol
# (operator token budget, crash, manual stop) rather than by CC's own judgment.
# Added 2026-08-12: 2026-08-07 ran 3 follows purely because Amir's token budget
# ran out mid-run, and the rubric scored that as a protocol shortfall and
# counted it toward the two-consecutive-low-scores autonomy pause.
# PRIMARY signal: a structured marker the report writer emits deliberately.
# Prose matching alone proved too fragile — on 2026-08-28 a report saying
# "STOPPED EARLY at 5/12" matched NOTHING in the old list, so a session blocked
# by a browser fault scored 4/10 and counted toward the two-strikes autonomy
# pause. That is precisely what this exemption exists to prevent.
SESSION_INCOMPLETE_MARKER = "session_incomplete:"

TRUNCATION_MARKERS = (
    "ran out of tokens", "out of tokens", "token limit", "token budget",
    "session incomplete", "incomplete session", "ended early", "truncated",
    "interrupted", "context limit",
    # broadened 2026-08-28 after the miss above
    "stopped early", "stopped deliberately", "stopped partway", "halted",
    "could not complete", "did not complete", "was blocked", "blocked partway",
    "cut short",
)

# SC_PASS_A_LIKES / SC_PASS_C_MAX are defined at the top of this file from
# sc_engagement_config (SC-04: one law).
SC_LIKE_COOLDOWN_DAYS = getattr(_scc, "LIKE_COOLDOWN_DAYS", 30)


def scan_for_truncation(text: str) -> bool:
    """True if the report says the session was cut short externally.

    Checks the structured `SESSION_INCOMPLETE: <reason>` marker first (the
    reliable path CC should emit), then falls back to prose phrasings.
    """
    low = (text or "").lower()
    if SESSION_INCOMPLETE_MARKER in low:
        return True
    return any(m in low for m in TRUNCATION_MARKERS)


def _sc_pass_c_available(tracker: dict, day: str) -> int:
    """Reciprocators actually outside the PASS C 30-day cooldown on `day`.

    PASS C maintenance likes can only target accounts that followed back and
    whose last engagement is older than the cooldown. With 33 reciprocators on a
    30-day cooldown the pool yields ~1.1 candidates a day, so a fixed target of
    12 was unreachable by construction.
    """
    try:
        today = date.fromisoformat(day[:10])
    except (ValueError, TypeError):
        return 0
    cutoff = today.toordinal() - SC_LIKE_COOLDOWN_DAYS
    n = 0
    for e in tracker.get("follows", []):
        if not e.get("followed_back") or e.get("followback_lost_at"):  # G-03
            continue
        if e.get("no_longer_following") or e.get("no_longer_engage"):
            continue
        raw = e.get("last_engaged")
        if not raw:
            n += 1                      # never engaged -> eligible
            continue
        try:
            if date.fromisoformat(str(raw)[:10]).toordinal() <= cutoff:
                n += 1
        except ValueError:
            n += 1
    return n


def _sc_like_target(tracker: dict | None, day: str,
                    pass_a: int = SC_PASS_A_LIKES) -> int:
    """Like target = PASS A warm-up likes only (2026-09-24).

    Until 09-24 this added the PASS C pool (reciprocators outside the 30-day
    like cooldown). That pool counts accounts, not tracks: 9-10 of every 10
    had nothing new to like, so a flawless 25/25 session missed a phantom
    target of 37 and lost a point every day. PASS C runs "as the pool allows"
    (SOP 6.2); its likes still count toward the day, as a bonus, never a debt.
    `tracker`/`day` stay in the signature for callers."""
    return pass_a


def _sc_follow_supply(day: str) -> int | None:
    """Eligible follow candidates still left in the newest discovery file, for
    `day` == today only (the file changes over time, so a past day cannot be
    reconstructed). None when unknown: then the full target applies."""
    if not day or day != date.today().isoformat():
        return None
    try:
        try:
            from scene_intelligence import sc_engagement as sce
        except ImportError:
            import sc_engagement as sce  # type: ignore
        out, _ = sce.eligible_candidates()
        return len(out)
    except Exception:
        return None


def _sc_follow_cap(day: str) -> int:
    """Follow cap for `day`: config FOLLOW_CAP_DAYS (dated, Amir-approved,
    2026-10-11) or the standing SESSION_FOLLOWS."""
    days = getattr(_scc, "FOLLOW_CAP_DAYS", {}) or {}
    return int(days.get(str(day)[:10], SC_FOLLOW_TARGET) or SC_FOLLOW_TARGET)


def _sc_unfollow_catchup(day: str) -> int:
    """Amir-approved one-off unfollow allowance for `day` (config
    UNFOLLOW_CATCHUP_DAYS, 2026-09-15), so a planned catch-up is not scored
    as a cap violation and does not pause SC."""
    days = getattr(_scc, "UNFOLLOW_CATCHUP_DAYS", {}) or {}
    return int(days.get(str(day)[:10], 0) or 0)


def score_sc_day(day_actions: dict[str, int], report_text: str,
                 tracker: dict | None = None,
                 day: str = "") -> tuple[int, list[str], str | None]:
    """Deterministic SC score from the day's engagement-log actions."""
    deductions: list[str] = []
    immediate: str | None = None
    score = 10

    hits = scan_for_detection(report_text)
    if hits:
        score -= 5
        deductions.append(f"-5 detection signal(s): {sorted(set(hits))}")
        immediate = f"detection signal in SC session: {sorted(set(hits))}"

    caps = dict(SC_CAPS)
    caps["sc_unfollow"] += _sc_unfollow_catchup(day)
    caps["sc_follow"] = _sc_follow_cap(day)
    for action, cap in caps.items():
        n = day_actions.get(action, 0)
        if n > cap:
            score -= 3
            deductions.append(f"-3 cap violation: {action} {n} > {cap}")
            immediate = immediate or f"cap violation: {action} {n} > {cap}"

    if sum(day_actions.values()) == 0:
        score -= 2
        deductions.append("-2 zero logged actions")

    # Under-delivery vs the SOP session targets (added 2026-07-20, recalibrated
    # 2026-08-12). Three corrections:
    #   - the like target is now PASS A + the REAL PASS C pool, not a fixed 24
    #     that the cooldown made unreachable;
    #   - `sc_like_skip` (every visible track already liked, SOP D.4) counts
    #     toward the target, mirroring what IG already does with
    #     `ig_unfollow_skip`;
    #   - a session truncated from outside (token budget, crash) is not a
    #     protocol shortfall. Detection signals and cap violations above still
    #     apply, so truncation cannot be used to hide a CAPTCHA.
    catchup_only = (_sc_unfollow_catchup(day) > 0 and day_actions.get("sc_unfollow")
                    and not day_actions.get("sc_like") and not day_actions.get("sc_follow"))
    if catchup_only:
        # An Amir-approved unfollow catch-up day with no engagement session
        # (2026-09-16): likes/follows were never planned, so no shortfall.
        deductions.append("note: unfollow catch-up day, like/follow targets not scored")
    elif scan_for_truncation(report_text):
        deductions.append("note: session truncated externally, volume targets not scored")
    else:
        shortfall_counts = dict(day_actions)
        if day_actions.get("sc_like_skip"):
            shortfall_counts["sc_like"] = (
                shortfall_counts.get("sc_like", 0) + day_actions["sc_like_skip"])
        # SUPPLY CAP (2026-09-24): a session cannot follow people who do not
        # exist. Target = what was on offer (done today + still eligible now),
        # capped at the session target. Prelikes are 1:1 with follow candidates.
        # Without this, 25/25 targets turned every thin-supply day into a <=5
        # score and two of those auto-pause SC for a supply gap, not a fault.
        follow_target = _sc_follow_cap(day)
        left = _sc_follow_supply(day)
        if left is not None:
            offered = day_actions.get("sc_follow", 0) + left
            if offered < follow_target:
                follow_target = offered
                deductions.append(f"note: follow target capped at {offered} by supply "
                                  f"({left} eligible left in the discovery file)")
        targets = {"sc_like": _sc_like_target(tracker, day,
                                              pass_a=min(SC_PASS_A_LIKES, follow_target)),
                   "sc_follow": follow_target}
        for d in _target_shortfall(shortfall_counts, targets):
            score -= int(d.split()[0].lstrip("-"))
            deductions.append(d)

    clicks = sum(n for a, n in day_actions.items() if a != "sc_like_skip")
    stop = SC_ACTION_STOP + _sc_unfollow_catchup(day)
    if clicks > stop:
        deductions.append(f"note: PACING WARNING {clicks} actions > session stop {stop} "
                          f"(no pause; tell Amir)")

    # A day with zero logged actions cannot score above 3/10, even when it is
    # marked incomplete (2026-09-11): that session did nothing and scored 8/10
    # because the incomplete marker waived the volume targets.
    if sum(day_actions.values()) == 0 and score > ZERO_ACTION_SCORE_CAP:
        deductions.append(f"cap {ZERO_ACTION_SCORE_CAP}/10: zero logged actions")
        score = ZERO_ACTION_SCORE_CAP

    return max(0, score), deductions, immediate


# ---------------------------------------------------------------------------
# IG loop
# ---------------------------------------------------------------------------

def close_ig(day: str, state: dict) -> tuple[int, str]:
    """Close the IG loop for a date. Returns (exit_code, report_text)."""
    jsonl = SI_DIR / f"ig_session_{day}.jsonl"
    if not jsonl.exists():
        return 1, f"No IG session log for {day} — nothing to close."
    if day in state["processed"]["ig"]:
        return 1, f"IG {day} already processed — nothing to do."

    raw_text = jsonl.read_text(encoding="utf-8", errors="replace")

    try:
        from scene_intelligence import ig_merge_session_log as m
    except ImportError:
        import ig_merge_session_log as m

    events = m.parse_jsonl(jsonl)
    events = [m._normalize_event(dict(ev)) for ev in events]

    # Reciprocators BEFORE the merge mutates the tracker
    tracker = load_json_checked(TRACKER_FILE, {}, what="IG follow tracker")
    pre_recip = {str(e.get("username", "")).lower()
                 for e in tracker.get("active_follows", [])
                 if e.get("followed_back")}

    # Merge — NEVER with --force here: a guard trip is an escalation, not an
    # obstacle. Amir decides forces by hand.
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        merge_code = m.merge(day)
    merge_out = buf.getvalue()

    if merge_code == 2:
        reason = f"IG merge guard tripped for {day} (fabrication or non-session-day)"
        record_score(state, "ig", day, 0, reason)
        notify_mac("IG loop — NEEDS AMIR", reason)
        report = (f"# IG loop {day} — ESCALATION\n\n**{reason}**\n\n"
                  f"Score: 0/10 (guard trip)\n\n```\n{merge_out}\n```\n\n"
                  f"**NEEDS AMIR.** Autonomy paused. After review: quarantine "
                  f"the log, or merge by hand with --force, then run "
                  f"`close_loops.py --resume --platform ig`.\n")
        return 2, report

    score, deductions, immediate = score_ig_session(
        events, pre_recip, raw_text + merge_out, merge_code)

    # Pool depth after merge — use the merge script's VETTED calculation.
    # (Bug found 2026-07-20: this used len(queue) = 1423, which counts
    # followed/skipped/stale entries too and can never fall below the
    # threshold. The real vetted-and-fresh depth that day was 33.)
    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2), contextlib.redirect_stderr(buf2):
        depth = m.report_vetted_pool_depth()
    depth_line = (f"**POOL LOW: {depth} vetted targets (<= {POOL_DEPTH_WARN}) — "
                  f"schedule a queue refresh.**" if depth <= POOL_DEPTH_WARN
                  else f"Pool depth: {depth} vetted targets.")

    pause_reason = record_score(state, "ig", day, score, immediate)
    if pause_reason:
        notify_mac("IG loop — NEEDS AMIR", pause_reason)
    if zero_click_halt(events):
        # 2026-09-11: a halt with no clicks (browser not connected, gate
        # refused) must not consume the day — the real session can still run
        # and be scored later (09-07 and 09-11 both needed a manual unlock).
        locked_note = "day NOT marked processed (zero-click halt); a real session may still run"
        # 2026-09-26: also give back the ledger claim, otherwise the halted
        # run's claim reads as "ran today" and blocks the real session.
        try:
            try:
                from scene_intelligence.ig_daily_ledger import release_claim
            except ImportError:
                from ig_daily_ledger import release_claim
            if release_claim("ig_session", day):
                locked_note += "; ledger claim released"
        except Exception as exc:  # never fail the close over this
            locked_note += f"; ledger claim NOT released ({exc})"
    else:
        state["processed"]["ig"].append(day)
        locked_note = ""
        # 2026-09-17: the pre-confirm flag is single-use -- consumed by the
        # merge of the session it confirmed (the date guard already stops it
        # carrying over; this just keeps the folder clean).
        try:
            from scene_intelligence.ig_session_confirm import clear_flag
        except ImportError:  # run from inside scene_intelligence/
            from ig_session_confirm import clear_flag
        clear_flag(only_date=day)

    counts: dict[str, int] = {}
    for ev in events:
        a = str(ev.get("action") or "")
        counts[a] = counts.get(a, 0) + 1
    count_line = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) or "none"

    report = [f"# IG loop {day} — closed automatically",
              "",
              f"**Score: {score}/10**" + (" — auto rubric" if not deductions
                                          else "") + " (execution vs plan)",
              ""]
    goal = _growth_target(day)
    if goal:
        got = counts.get("ig_follow", 0)
        report.insert(3, f"**Growth: {got} / {goal} follows**"
                         + ("" if got >= goal else
                            f" — short by {goal - got}; supply, not execution, when the score is high"))
        report.insert(4, "")
    if deductions:
        report.append("Deductions:")
        report.extend(f"- {d}" for d in deductions)
        report.append("")
    report += [f"Actions: {count_line}", "", depth_line + (f"  \n_{locked_note}_" if locked_note else ""), "",
               "## Merge output", "```", merge_out.strip(), "```", ""]
    if pause_reason:
        report += [f"**NEEDS AMIR — IG autonomy paused: {pause_reason}**",
                   "Run `close_loops.py --resume --platform ig` after review.", ""]

    # Scorecard row (auto)
    if SCORECARD.exists() and counts:
        weekday = date.fromisoformat(day).strftime("%a")
        verdict = "; ".join(deductions) if deductions else "clean auto-close"
        row = (f"| {day} | {weekday} | **{score}** (auto) | "
               f"{counts.get('ig_follow', 0)} | {counts.get('ig_like', 0)} | "
               f"{counts.get('ig_unfollow', 0)} | {verdict} |")
        with open(SCORECARD, "a", encoding="utf-8") as f:
            f.write(row + "\n")

    return (2 if pause_reason else 0), "\n".join(report)


# ---------------------------------------------------------------------------
# SC loop
# ---------------------------------------------------------------------------

def forget_sc_day(state: dict, day: str) -> None:
    """Drop an SC day's processed mark and score so close_sc can run again.
    Idempotent: a day that was never closed is left as it is."""
    if day in state["processed"]["sc"]:
        state["processed"]["sc"].remove(day)
    state["recent"] = [r for r in state.get("recent", [])
                       if not (r.get("platform") == "sc" and r.get("date") == day)]


def close_sc(day: str, state: dict) -> tuple[int, str]:
    if day in state["processed"]["sc"]:
        return 1, f"SC {day} already processed — nothing to do."

    eng = load_json_checked(ENG_LOG_FILE, {"log": {}}, what="engagement log")
    log = eng.get("log", eng)
    day_actions: dict[str, int] = {}
    for acts in log.values():
        if not isinstance(acts, list):
            continue
        for a in acts:
            if (str(a.get("date", "")) == day
                    and str(a.get("action", "")).startswith("sc_")):
                k = str(a["action"])
                day_actions[k] = day_actions.get(k, 0) + 1

    report_file = SI_DIR / f"sc_session_report_{day.replace('-', '')}.md"
    report_text = (report_file.read_text(encoding="utf-8", errors="replace")
                   if report_file.exists() else "")

    if not day_actions and not report_text:
        return 1, f"No SC activity logged for {day} — nothing to close."

    # Tracker drives the achievable PASS C like target (2026-08-12).
    tracker = load_json_checked(
        SI_DIR / "sc_follow_tracker.json", {"follows": []}, what="follow tracker")
    score, deductions, immediate = score_sc_day(
        day_actions, report_text, tracker=tracker, day=day)
    # A zero-action day stopped from outside keeps its honest low score but
    # stays out of the trend pause (2026-09-11, see record_score).
    zero_incomplete = not day_actions and bool(scan_for_truncation(report_text))
    pause_reason = record_score(state, "sc", day, score, immediate,
                                counts_for_trend=not zero_incomplete)
    if pause_reason:
        notify_mac("SC loop — NEEDS AMIR", pause_reason)
    state["processed"]["sc"].append(day)

    count_line = ", ".join(f"{k}: {v}" for k, v in sorted(day_actions.items())) or "none"
    report = [f"# SC loop {day} — closed automatically", "",
              f"**Score: {score}/10**", ""]
    if deductions:
        report.append("Deductions:")
        report.extend(f"- {d}" for d in deductions)
        report.append("")
    report += [f"Logged actions: {count_line}", ""]
    if zero_incomplete:
        report += ["Zero-action incomplete session: recorded, not counted "
                   "toward the trend pause.", ""]
    if pause_reason:
        report += [f"**NEEDS AMIR — SC autonomy paused: {pause_reason}**",
                   "Run `close_loops.py --resume --platform sc` after review.", ""]
    return (2 if pause_reason else 0), "\n".join(report)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--platform", choices=["ig", "sc", "all"], default="all")
    p.add_argument("--date", default=str(date.today()),
                   help="Session date YYYY-MM-DD (default today)")
    p.add_argument("--resume", action="store_true",
                   help="Amir-only: clear a pause after reviewing the escalation")
    p.add_argument("--rescore", action="store_true",
                   help="SC only: score the day again after a retry run "
                        "(replaces the earlier score for that date)")
    args = p.parse_args()

    state = load_state()

    if args.rescore:
        # 13:00 retry (2026-10-25): the 10:00 run may already have closed the
        # day with a 3/10 for zero actions. A successful retry scores the day
        # again; the old entry for that date is replaced, not added to.
        if args.platform != "sc":
            print("--rescore is for --platform sc only.")
            return 1
        forget_sc_day(state, args.date)

    if args.resume:
        # Resume is PER PLATFORM -- clearing an SC pause must never un-gate IG
        # or vice versa. Refuse the ambiguous form.
        if args.platform == "all":
            print("Resume which platform? Run with --platform ig or --platform sc.")
            for plat in ("ig", "sc"):
                rec = platform_paused(state, plat)
                print(f"  {plat}: " + (f"PAUSED ({rec['reason']})" if rec else "not paused"))
            return 1
        rec = platform_paused(state, args.platform)
        if not rec:
            print(f"{args.platform.upper()} is not paused — nothing to resume.")
            return 0
        print(f"{args.platform.upper()} pause cleared (was: {rec['reason']}).")
        state["pauses"][args.platform] = None
        save_state(state)
        return 0

    worst = 1
    platforms = ["ig", "sc"] if args.platform == "all" else [args.platform]
    # Per-platform gate: a paused platform is observe-and-report only; the
    # OTHER platform keeps closing normally.
    gated = []
    for plat in list(platforms):
        rec = platform_paused(state, plat)
        if rec:
            print(f"[PAUSED] {plat.upper()} autonomy is paused: {rec['reason']}")
            print(f"Review, then run: close_loops.py --resume --platform {plat}")
            gated.append(plat)
            platforms.remove(plat)
    if not platforms:
        return 3
    for platform in platforms:
        code, report = (close_ig if platform == "ig" else close_sc)(args.date, state)
        if code == 1:
            print(report)
            continue
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        out = REPORTS_DIR / f"loop-close-{platform}-{args.date}.md"
        out.write_text(report, encoding="utf-8")
        print(report)
        print(f"\nReport saved: {out}")
        worst = max(worst, code) if worst != 1 else code

    save_state(state)
    return 0 if worst in (0, 1) else worst


if __name__ == "__main__":
    sys.exit(main())
