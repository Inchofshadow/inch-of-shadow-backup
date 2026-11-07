# Task 8 report: ticket notes and full test run

Status: DONE
Commit: 5db33fefb87d7a96249a73ff4da33ddc939be7d4
Subject: chore(tickets): score board built (G-09 in progress), Measure-03 targets note

## Step 1: full test run

Command: python3 -m pytest tests -q

Tail of output:

    FAILED tests/test_in_session_vet.py::test_select_vets_only_when_pool_low - As...
    FAILED tests/test_shoot_page.py::test_every_photo_has_a_cover_idea_and_the_page_draws_it
    FAILED tests/test_shoot_page.py::test_cover_fonts_exist_and_the_page_sets_the_idea_in_one
    FAILED tests/test_shoot_page.py::test_covers_page_and_every_cover_carries_the_name_and_an_ink
    FAILED tests/test_stats_collect_skip.py::test_collect_all_skips_the_named_platforms
    FAILED tests/test_tickets.py::test_seed_every_ticket_has_short_why_and_helps
    6 failed, 1004 passed, 1 warning in 17.07s

All seven score-board test files pass: test_targets, test_manual_entry, test_ig_followback, test_collect_instagram_daily, test_score_board, test_stats_page, test_propose_targets.

Failing files (all outside the score board): tests/test_in_session_vet.py, tests/test_shoot_page.py (3 tests), tests/test_stats_collect_skip.py, tests/test_tickets.py.

test_tickets failure detail: ticket DJ-01 has a "why" of 254 characters, over the 220 limit. DJ-01 was not touched by this task.

## Step 2: ticket notes

a) plans/tickets.json, G-09:
- status: "proposed" -> "in-progress"
- notes: appended the 2026-11-02 Score board note (exact text from the brief)
- top-level "updated": "2026-11-01" -> "2026-11-02"

b) plans/control-panel/tickets.json, Measure-03:
- notes: appended the 2026-11-02 targets note (exact text from the brief)

Both files parse with json.load. No other fields changed. Indentation is indent=1 (ensure_ascii=False). plans/tickets.json keeps its missing trailing newline; plans/control-panel/tickets.json keeps its trailing newline.

## Step 3: commit

Staged by explicit path only: plans/tickets.json, plans/control-panel/tickets.json.
Commit 5db33fe: 2 files changed, 6 insertions(+), 4 deletions(-).
Other pre-existing modified files in the working tree were not staged or touched.

## Concerns

- The commit trailer uses "Co-Authored-By: Claude Haiku 5.5", per the system attribution reminder. The brief's trailer said "Claude Fable 5.1". Amend if the brief's name is what is wanted.
- The Measure-03 diff shows one changed line. This is only the trailing comma added to the previous note, which is required for valid JSON.
