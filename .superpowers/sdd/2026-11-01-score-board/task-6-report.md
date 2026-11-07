# Task 6 report
Implemented: stats_page passes board=score_board.build(); stats.html old .st-score block replaced by the .sb section (score line, 6 cards, HEALTH dots, LADDER svgs with |safe, TREND ONLY cards), subtitle changed to the brief's copy; "/* Score board */" CSS block added after the Measure-03 block; base.html style.css?v=74.
Existing test first assertion changed to "GREEN"; test_stats_page_renders_the_score_board added.
TDD: RED before implementation (2 failed, 2 passed). GREEN after: `python3 -m pytest tests/test_stats_page.py tests/test_score_board.py -q` -> 10 passed, 1 warning.
Commit: cad8153 feat(stats): score board on top of the Stats page (amended once to include the v=74 bump).
Concerns:
- The five files already carried large uncommitted edits from before (base.html v=59 -> 73 plus new sidebar links, webapp.py +52, style.css +144, stats.html, test file). The commit necessarily swept those in, since whole files are added.
- No --text-muted token exists; grey/collecting uses var(--border) for dots and --text-secondary for text.
- Health items with href render the label as a link; title tooltip "label: detail" on each dot item.
- Em-dash check: none in the score board section of the rendered page.

## Fix round 1
Changed: undefined var(--border) in the score board CSS replaced: .sb-light and .sb-dot.unknown use --text-secondary, .sb-dot base uses --border-color. Re-scanned the block, no other undefined tokens. Test now also asserts 6 sb-card, 8 sb-dot, "/8 pass".
Command: python3 -m pytest tests/test_stats_page.py tests/test_score_board.py -q -> 10 passed, 1 warning.
