### Task 6: Page, template and CSS

**Files:**
- Modify: `release_manager/webapp.py:5135-5140` (`stats_page`)
- Modify: `release_manager/templates/stats.html:18-21` (replace the `.st-score` block)
- Modify: `release_manager/static/style.css` (append a `/* Score board */` block after the Measure-03 block at ~6296), `release_manager/templates/base.html:9` (`v=73` to `v=74`)
- Test: `tests/test_stats_page.py` (extend), `tests/test_score_board.py` (one render test)

**Interfaces:**
- Consumes: Task 5 `score_board.build()`.
- Produces: `stats_page()` passes `board=score_board.build()`; the template renders, in order, the score line (`.sb-score`), the six cards (`.sb-grid` 3 columns, `.sb-card.sb-<light>`), the health row (`.sb-health`, dots `.sb-dot.ok|.fail|.unknown`, "7/8 pass"), the ladder charts (`.sb-ladders`, two per row), the three trend-only cards (`.sb-trends`, header "TREND ONLY, no target"), then everything the page already had from `{% if weekly %}` down, untouched.
- Copy, exact: page subtitle becomes "Growth against the written targets in plans/targets.json. A light compares today with the ladder: green on track, amber drifting, red behind, grey collecting."; card footer "as of {date}"; health header "HEALTH"; ladder header "LADDER" with the muted note "the line is reality, the steps are the plan".

- [ ] **Step 1: Write the failing tests**

```python
from release_manager.webapp import app

def test_stats_page_renders_the_score_board():
    html = app.test_client().get("/stats").get_data(as_text=True)
    assert 'class="sb-score"' in html and "IG followers" in html and "TikTok followers" in html
    assert "HEALTH" in html and "LADDER" in html and "the line is reality" in html and "TREND ONLY" in html
    assert "collecting" in html
    for track in ("Instagram", "SoundCloud", "YouTube", "Spotify", "Bandcamp"):   # the old grid is still there
        assert track in html
    assert "style.css?v=74" in html
```

Keep the existing `test_stats_page_renders_the_score_line_and_every_track` but change its first assertion from `"growing" in html` to `"GREEN" in html` (the old score line is gone).

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_stats_page.py -q`
Expected: FAIL on `sb-score`

- [ ] **Step 3: Implement the route, the template and the CSS**

Grid: `grid-template-columns: repeat(3, 1fr)`, one column under 900px. Card: big number in `var(--font-heading)` 30px like `.st-value`; light classes map to the existing status colours (`--color-done-text`, `--color-warning-text`, `--color-overdue-text`, grey `--text-muted` or the closest existing muted token); progress bar 3px with the light's colour; mono source key in 11px. SVG classes: `.sb-line` stroke `currentColor`, `.sb-ladder` stroke `var(--text-accent)` dashed 4 2, `.sb-base` dotted, `.sb-today` stroke `var(--color-warning-text)`.

- [ ] **Step 4: Run the page tests and look at it**

Run: `python3 -m pytest tests/test_stats_page.py tests/test_score_board.py -q`
Expected: all passed
Then ask Amir to reload the Release Manager and open `/stats`; take a screenshot in the built-in browser at `http://127.0.0.1:5001/stats` once he confirms the reload (Claude does not restart the server).

- [ ] **Step 5: Commit**

```bash
git add release_manager/webapp.py release_manager/templates/stats.html release_manager/templates/base.html release_manager/static/style.css tests/test_stats_page.py
git commit -m "feat(stats): score board on top of the Stats page"
```

---

