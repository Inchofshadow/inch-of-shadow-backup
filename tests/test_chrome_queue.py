"""tools/chrome_queue.py + tools/chrome_queue_hook.py (ticket System 67, G-25).

Every test runs on a tmp root, never the real ~/.claude/chrome-queue.
"""
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import chrome_queue as cq  # noqa: E402
import chrome_queue_hook as hook  # noqa: E402

T0 = 1_800_000_000.0
CLICK = "mcp__claude-in-chrome__computer"


@pytest.fixture(autouse=True)
def _no_real_root(monkeypatch, tmp_path):
    """Belt and braces: even a default-root call lands in tmp."""
    monkeypatch.setenv("CHROME_QUEUE_ROOT", str(tmp_path / "env-root"))


@pytest.fixture
def root(tmp_path):
    return tmp_path / "cq"


def cli(root, *args, now=T0):
    buf = io.StringIO()
    code = cq.main(["--root", str(root), "--now", str(now)] + list(args), out=buf)
    return code, buf.getvalue()


def run_hook(root, payload, now=T0):
    buf = io.StringIO()
    code = hook.main(json.dumps(payload), root=str(root), now=now, out=buf)
    return code, buf.getvalue().strip()


def chrome_call(session, cwd="/Users/amir/Desktop/BERLIN", tool=CLICK, tool_input=None):
    return {"session_id": session, "hook_event_name": "PreToolUse", "tool_name": tool,
            "tool_input": tool_input or {}, "cwd": cwd}


def lock(root):
    return json.loads((root / "lock.json").read_text())


def queue(root):
    return json.loads((root / "queue.json").read_text())


# ---------- helper CLI ----------

def test_claim_release(root):
    code, out = cli(root, "claim", "--session", "s1", "--title", "BERLIN invoice", "--profile", "a9ab2708")
    assert code == 0 and "You hold Chrome" in out
    assert lock(root)["session"] == "s1" and lock(root)["profile"] == "a9ab2708"
    code, out = cli(root, "release", "--session", "s1")
    assert code == 0 and lock(root) == {}


def test_second_claim_queues_and_force_release_promotes(root):
    cli(root, "claim", "--session", "s1", "--title", "BERLIN", "--profile", "Browser 1")
    code, out = cli(root, "claim", "--session", "s2", "--title", "Radar", "--profile", "Browser 2", now=T0 + 5)
    assert code == 2 and "number 1 in line" in out
    assert lock(root)["session"] == "s1"
    code, out = cli(root, "release", "--force", now=T0 + 60)
    assert code == 0 and "Chrome is free" in out
    assert lock(root)["session"] == "s2"
    assert lock(root)["profile"] == "Browser 2"
    assert queue(root) == []


def test_force_release_when_free(root):
    code, out = cli(root, "release", "--force")
    assert code == 0 and "already free" in out


def test_release_by_non_holder_does_not_free(root):
    cli(root, "claim", "--session", "s1", "--title", "A", "--profile", "p")
    cli(root, "release", "--session", "s2")
    assert lock(root)["session"] == "s1"


def test_queue_order_and_promotion(root):
    cli(root, "claim", "--session", "s1", "--title", "A", "--profile", "p")
    assert "number 1" in cli(root, "wait", "--session", "s2", "--title", "B", now=T0 + 1)[1]
    assert "number 2" in cli(root, "wait", "--session", "s3", "--title", "C", now=T0 + 2)[1]
    assert "number 2" in cli(root, "wait", "--session", "s3", "--title", "C", now=T0 + 3)[1]  # no double entry
    assert [e["session"] for e in queue(root)] == ["s2", "s3"]
    cli(root, "release", "--session", "s1", now=T0 + 10)
    assert lock(root)["session"] == "s2"
    assert [e["session"] for e in queue(root)] == ["s3"]
    cli(root, "release", "--session", "s2", now=T0 + 20)
    assert lock(root)["session"] == "s3"


def test_inch_of_shadow_goes_ahead_in_line(root):
    cli(root, "claim", "--session", "s1", "--title", "BERLIN", "--profile", "p")
    cli(root, "wait", "--session", "s2", "--title", "Radar", now=T0 + 1)
    code, out = cli(root, "wait", "--session", "s3", "--title", "Inch of Shadow", now=T0 + 2)
    assert "number 1" in out
    assert [e["session"] for e in queue(root)] == ["s3", "s2"]
    assert lock(root)["session"] == "s1"  # priority never pushes the holder out


def test_wait_when_free_takes_chrome(root):
    code, out = cli(root, "wait", "--session", "s1", "--title", "A")
    assert "You hold Chrome" in out and lock(root)["session"] == "s1"


def test_touch(root):
    cli(root, "claim", "--session", "s1", "--title", "A", "--profile", "p")
    assert cli(root, "touch", "--session", "s1", now=T0 + 100)[0] == 0
    assert lock(root)["last_touch"] == T0 + 100
    code, out = cli(root, "touch", "--session", "s2", now=T0 + 100)
    assert code == 1 and "does not hold" in out


def test_stale_holder_released_after_20_min(root):
    cli(root, "claim", "--session", "s1", "--title", "A", "--profile", "p")
    cli(root, "wait", "--session", "s2", "--title", "B", now=T0 + 1)
    cli(root, "touch", "--session", "s1", now=T0 + 600)
    cli(root, "status", now=T0 + 600 + 19 * 60)
    assert lock(root)["session"] == "s1"  # 19 min: still held
    code, out = cli(root, "status", now=T0 + 600 + 20 * 60)
    assert "released stale holder A" in out
    assert lock(root)["session"] == "s2"
    assert lock(root)["since"] == T0 + 600 + 20 * 60


def test_stale_without_queue_frees(root):
    cli(root, "claim", "--session", "s1", "--title", "A", "--profile", "p")
    code, out = cli(root, "claim", "--session", "s2", "--title", "B", "--profile", "q", now=T0 + 21 * 60)
    assert code == 0 and lock(root)["session"] == "s2"


def test_status_shows_holder_since_last_call_queue(root):
    cli(root, "claim", "--session", "s1", "--title", "BERLIN", "--profile", "Browser 1", "--note", "invoice")
    cli(root, "wait", "--session", "s2", "--title", "Radar", now=T0 + 1)
    cli(root, "touch", "--session", "s1", now=T0 + 300)
    out = cli(root, "status", now=T0 + 420)[1]
    assert "Holder: BERLIN (session s1)" in out
    assert "profile: Browser 1" in out
    assert "since: %s" % cq.hhmm(T0) in out
    assert "last call: %s (2 min ago" % cq.hhmm(T0 + 300) in out
    assert "note: invoice" in out
    assert "1. Radar (session s2)" in out


def test_status_free(root):
    assert "Chrome is free" in cli(root, "status")[1]


def test_writes_are_atomic_no_tmp_left(root):
    cli(root, "claim", "--session", "s1", "--title", "A", "--profile", "p")
    cli(root, "wait", "--session", "s2", "--title", "B")
    leftovers = [p.name for p in root.iterdir() if p.name.endswith(".tmp")]
    assert leftovers == []


# ---------- hook ----------

def test_hook_auto_claims_when_free(root):
    code, out = run_hook(root, chrome_call("s1", cwd="/Users/amir/Desktop/BERLIN"))
    assert code == 0 and out == ""
    assert lock(root)["session"] == "s1" and lock(root)["title"] == "BERLIN"


def test_hook_allows_holder_and_touches(root):
    run_hook(root, chrome_call("s1"))
    code, out = run_hook(root, chrome_call("s1"), now=T0 + 500)
    assert code == 0 and out == ""
    assert lock(root)["last_touch"] == T0 + 500


def test_hook_records_profile_from_select_browser(root):
    run_hook(root, chrome_call("s1", tool="mcp__claude-in-chrome__select_browser",
                               tool_input={"deviceId": "a9ab2708"}))
    assert lock(root)["profile"] == "a9ab2708"


def test_hook_denies_second_session_with_reason(root):
    cli(root, "claim", "--session", "s1", "--title", "BERLIN invoice", "--profile", "Browser 1")
    code, out = run_hook(root, chrome_call("s2", cwd="/x/Radar", tool="mcp__Control_Chrome__open_url"),
                         now=T0 + 60)
    assert code == 0
    data = json.loads(out)["hookSpecificOutput"]
    assert data["hookEventName"] == "PreToolUse"
    assert data["permissionDecision"] == "deny"
    assert data["permissionDecisionReason"] == (
        "Chrome is held by BERLIN invoice since %s (profile Browser 1). You are number 1 in line. "
        "Wait, or ask Amir to say 'Chrome is free'." % cq.hhmm(T0))
    assert [e["session"] for e in queue(root)] == ["s2"]
    # a third chat is number 2
    out3 = run_hook(root, chrome_call("s3", cwd="/x/Other"), now=T0 + 61)[1]
    assert "You are number 2 in line" in out3


def test_hook_waiter_gets_chrome_after_release(root):
    run_hook(root, chrome_call("s1"))
    run_hook(root, chrome_call("s2", cwd="/x/Radar"), now=T0 + 1)
    cli(root, "release", "--force", now=T0 + 2)
    code, out = run_hook(root, chrome_call("s2", cwd="/x/Radar"), now=T0 + 3)
    assert out == "" and lock(root)["session"] == "s2"


def test_hook_ignores_non_chrome_tools(root):
    cli(root, "claim", "--session", "s1", "--title", "A", "--profile", "p")
    for tool in ("Bash", "Read", "mcp__Claude_Browser__navigate", "mcp__computer-use__computer_batch"):
        code, out = run_hook(root, chrome_call("s2", tool=tool))
        assert code == 0 and out == ""
    assert queue(root) == []


def test_hook_non_chrome_tool_touches_nothing(tmp_path):
    fresh = tmp_path / "never"
    run_hook(fresh, chrome_call("s1", tool="Bash"))
    assert not fresh.exists()


def test_hook_fails_open_on_broken_state(root):
    root.mkdir(parents=True)
    (root / "lock.json").write_text("{not json")
    code, out = run_hook(root, chrome_call("s2"))
    assert code == 0 and out == ""
    log = (root / "hook-errors.log").read_text()
    assert "JSONDecodeError" in log or "Error" in log


def test_hook_fails_open_on_bad_stdin(root):
    buf = io.StringIO()
    assert hook.main("not json at all", root=str(root), out=buf) == 0
    assert buf.getvalue() == ""
    assert (root / "hook-errors.log").exists()


def test_hook_session_end_releases_and_promotes(root):
    run_hook(root, chrome_call("s1"))
    run_hook(root, chrome_call("s2", cwd="/x/Radar"), now=T0 + 1)
    run_hook(root, chrome_call("s3", cwd="/x/Other"), now=T0 + 2)
    code, out = run_hook(root, {"session_id": "s3", "hook_event_name": "SessionEnd", "cwd": "/x"}, now=T0 + 3)
    assert code == 0 and out == ""
    assert [e["session"] for e in queue(root)] == ["s2"]  # waiter left the line
    run_hook(root, {"session_id": "s1", "hook_event_name": "SessionEnd", "reason": "exit"}, now=T0 + 4)
    assert lock(root)["session"] == "s2"


def test_hook_priority_from_cwd(root):
    run_hook(root, chrome_call("s1", cwd="/Users/amir/Desktop/BERLIN"))
    run_hook(root, chrome_call("s2", cwd="/x/Radar"), now=T0 + 1)
    out = run_hook(root, chrome_call("s3", cwd="/Users/amir/Desktop/Inch of Shadow"), now=T0 + 2)[1]
    assert "You are number 1 in line" in out


def test_hook_script_runs_as_subprocess(tmp_path):
    """The real entry point: stdin JSON in, deny JSON out, exit 0."""
    r = tmp_path / "sub"
    env = dict(os.environ, CHROME_QUEUE_ROOT=str(r))
    script = str(ROOT / "tools" / "chrome_queue_hook.py")
    first = subprocess.run([sys.executable, script], input=json.dumps(chrome_call("s1")),
                           capture_output=True, text=True, env=env)
    assert first.returncode == 0 and first.stdout == ""
    second = subprocess.run([sys.executable, script], input=json.dumps(chrome_call("s2", cwd="/x/Radar")),
                            capture_output=True, text=True, env=env)
    assert second.returncode == 0
    assert json.loads(second.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
