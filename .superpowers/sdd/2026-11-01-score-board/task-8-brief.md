### Task 8: Monday habit line (variant b only) and the ticket close

**Files:**
- Modify (variant b only): `~/.claude/scheduled-tasks/spotify-s4a-weekly-read/SKILL.md`, the closing report section: add the line "Instagram Insights: send the Accounts reached (30 days) screenshot in chat; it is stored with `python3 stats/manual_entry.py instagram_insights reach_30d <n> --date <today>`."
- Modify: `plans/tickets.json`: G-09 status "done" with a note pointing at the spec, the plan and the page; `plans/control-panel/tickets.json` Measure-03: note "targets per metric added 2026-11, see Score board".

- [ ] **Step 1: Full test run**

Run: `python3 -m pytest tests -q`
Expected: the 5 pre-existing failures (watchdog red, non-stats) and nothing new; every test from Tasks 1 to 7 passing.

- [ ] **Step 2: Ticket notes and commit**

```bash
git add plans/tickets.json plans/control-panel/tickets.json
git commit -m "chore(tickets): score board shipped (G-09), Measure-03 targets note"
```
