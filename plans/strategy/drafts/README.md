# Ready-to-apply drafts (strategy review, 2026-11-05)

Nothing in this folder is live. Each draft waits for Amir's yes in step 2. When he says yes,
⚙️ System applies it with a backup and an undo step, then reports "✅ done".

| Draft | Applies | Fixes | Undo |
|---|---|---|---|
| `parent-CLAUDE.md.draft` | becomes `Inch of Shadow/CLAUDE.md` (46 lines) | chats start with no rules file | delete the file |
| `MEMORY-index-slim.draft.md` | replaces the memory index | 28 KB → 16.5 KB, under the 25 KB load limit, so the newest rules load again. Hooks are shortened mechanically: Amir or Claude reads it once before it goes live | keep `MEMORY.md.bak-<date>` |
| `old-memory-merge.md` | moves the few still-valid rules from the July code-folder memory into the current one, then points the old memory at the current one | side chats reading July rules | backup folder of the old memory |
| `daily-brief-spec.draft.md` | one 20:00 brief replaces ~6 reports + popups (extends the 🎬 Socials digest, with that chat) | too many messages | turn the old tasks back on |
| `settings-enforced-rules.draft.json` | adds deny/ask rules to `Inch of Shadow/.claude/settings.local.json` | 4 hard rules enforced by the app, not by text | remove the added lines (backup kept) |
