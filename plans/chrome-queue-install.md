# Chrome queue: install, switch off, limits (⚙️ System 67)

Built, NOT installed. Nothing below is active until Amir says yes and the block goes into
`~/.claude/settings.json`.

Files: `tools/chrome_queue.py` (helper), `tools/chrome_queue_hook.py` (hook),
`tests/test_chrome_queue.py`. State: `~/.claude/chrome-queue/lock.json`, `queue.json`,
errors in `hook-errors.log`.

## The block to add under "hooks" in ~/.claude/settings.json

No global hooks exist yet, so add this as a top-level `"hooks"` key (if a `"hooks"` key exists
by then, merge the two lists into it instead):

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "mcp__claude-in-chrome__.*|mcp__Control_Chrome__.*",
      "hooks": [
        {
          "type": "command",
          "command": "python3 \"/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode/tools/chrome_queue_hook.py\"",
          "timeout": 10
        }
      ]
    }
  ],
  "SessionEnd": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python3 \"/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode/tools/chrome_queue_hook.py\"",
          "timeout": 10
        }
      ]
    }
  ]
}
```

## What it changes

- Every Chrome tool call (Claude in Chrome, Control Chrome) in every chat runs the hook first.
- Nobody holds Chrome: the calling chat gets it automatically (title = its folder name,
  profile "not named yet" until it calls select_browser, then the deviceId is recorded).
- The holder's calls go through and count as a heartbeat.
- Another chat holds it: the call is refused with "Chrome is held by <title> since <HH:MM>
  (profile <p>). You are number <n> in line. Wait, or ask Amir to say 'Chrome is free'."
  The refused chat is put in line.
- A holder with no Chrome call for 20 minutes is released on the next command; the first in
  line then holds Chrome.
- A chat that closes (SessionEnd) releases Chrome and leaves the line.
- Inch of Shadow chats (title or folder contains "Inch of Shadow" / "inchofshadow") go ahead of
  other chats in the line. They never push out the current holder.
- The allow path prints nothing, so the normal permission prompts are unchanged.
- Fails open: if the hook breaks (bad state file, bug), the call is allowed and the error goes
  to `~/.claude/chrome-queue/hook-errors.log`.

## Commands

```
python3 tools/chrome_queue.py status
python3 tools/chrome_queue.py claim --session <id> --title "<chat>" --profile a9ab2708 [--note "..."]
python3 tools/chrome_queue.py wait --session <id> --title "<chat>"
python3 tools/chrome_queue.py touch --session <id>
python3 tools/chrome_queue.py release --session <id>
```

Amir's "Chrome is free" (from any chat, or his terminal in the repo folder):

```
python3 tools/chrome_queue.py release --force
```

This frees the holder; the first chat in line then holds Chrome. Running it twice frees that
one too.

## Switch it off

Remove the `"PreToolUse"` and `"SessionEnd"` entries above from `~/.claude/settings.json`
(or the whole `"hooks"` key if nothing else is in it). The folder `~/.claude/chrome-queue/`
can stay; nothing reads it once the hook is gone.

## Honest limits

- It does not stop the browser pick from jumping inside one chat. The pick is session-local
  and does not stick, so the deviceId pin (select_browser a9ab2708) before every call stays.
  The queue only stops two chats from working in Chrome at the same time.
- It does not cover the apartment bot's own Chrome (port 9333, no extension) or the SC engine's
  AppleScript driving of Chrome. Those never call the MCP tools, so the hook never sees them.
- It does not cover the built-in Browser pane (`mcp__Claude_Browser__*`) or computer-use;
  those are not Chrome profiles.
- A chat that holds Chrome but stops working keeps it up to 20 minutes, unless Amir frees it.
- The rule text for chats ("claim before Chrome work") is not written into any CLAUDE.md by
  this build.
