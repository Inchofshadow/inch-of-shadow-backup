"""
release_manager/webapp.py
--------------------------
Flask web UI for the Release Manager.

Runs locally at http://localhost:5001.
No database — reads/writes the same JSON files as the CLI.

Usage:
    python3 release_manager/webapp.py
"""

from __future__ import annotations

import json
import os
import random
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Ensure the project root is on sys.path so imports work
# whether run as `python3 release_manager/webapp.py` or as a module.
# NOTE: this is the CODE location (for imports). DATA roots below use repo_root()
# so data always lands in the main repo even if the server runs from a worktree.
_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from release_manager.paths import repo_root

import subprocess
from io import BytesIO

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, abort, send_from_directory, send_file,
)
from werkzeug.utils import secure_filename

from release_manager.models import (
    RELEASE_TYPES, ALL_PLATFORMS, VALID_KEYS, DEFAULT_ARTIST,
    DISTRIBUTION_STATUSES,
    make_slug, validate_date, validate_duration, validate_bpm,
    new_release_dict, new_track_dict, validate_release,
)
from release_manager.storage import (
    ensure_releases_dir, load_release, save_release,
    list_releases, release_exists, unique_slug, delete_release,
)
from release_manager.timeline import (
    compute_timeline, recompute_dates, next_deadline, overdue_milestones,
    migrate_timeline, nearest_bandcamp_friday, calendar_grid_data, is_finished,
)
from release_manager.checklist import (
    generate_checklist, mark_done, mark_undone, migrate_checklist,
    checklist_progress, overdue_items, _CHECKLIST_TO_TIMELINE,
    CHECKLIST_TOOLTIPS,
)
from release_manager import clips as _clips

# ---------------------------------------------------------------------------
# App setup: the app, CSRF, context processor, filters, constants and the
# app-level file routes live in core.py (RM 2.0 slice 2). Re-exported here.
# ---------------------------------------------------------------------------

from release_manager.core import (  # noqa: F401  re-exports: tests import these from webapp
    app, csrf, _CSRF_AVAILABLE, _load_secret_key, _safe_existing_path,
    PROJECT_ROOT, ARTWORK_DIR, RESIZED_DIR, VIDEO_DIR, RESIZED_VIDEO_DIR,
    THEME_FILE, GENRES_FILE, VIDEO_EXTENSIONS, VIDEO_PLATFORMS, SEED_GENRES, SOCIAL_LINKS,
    load_theme, load_genres, save_genre,
    inject_globals, days_until_filter, platform_label_filter, _overlaps,
    ARTWORK_EXTENSIONS, find_artwork, artwork_url_for,
    serve_artwork, serve_resized, FAVICON_SOURCE, favicon, page_not_found, serve_resized_video,
    _limit_note, ARTWORK_PRESETS, VIDEO_PRESETS, _picked_templates,
)


# ---------------------------------------------------------------------------
# Work (tickets, board, outreach, SC status): routes live in views/work.py (RM 2.0 slice 4)
# ---------------------------------------------------------------------------

import release_manager.views.work  # noqa: E402,F401  registers the work routes on the shared app
from release_manager.views.work import (  # noqa: E402,F401  re-exports (_dashboard_lines reads CONTROL_PANEL_FILE)
    CONTROL_PANEL_FILE, TICKETS_FILE, OUTREACH_FILE, BOOKING_TARGETS_FILE,
    tickets_page, _work_page, _tickets_by_metric, board_page, api_board_cards,
    outreach_page, outreach_tick,
    _sc_engagement_import, sc_automation_page, api_sc_status,
)


# ---------------------------------------------------------------------------
# Studio part 1 (archive, effects, fonts, video + resizer): routes live in views/studio.py
# (RM 2.0 slice 5)
# ---------------------------------------------------------------------------

import release_manager.views.studio  # noqa: E402,F401  registers the studio routes on the shared app
from release_manager.views.studio import (  # noqa: E402,F401  re-exports (release page, playground, Imagine, Shoot use some)
    _archive, _archive_index, _archive_file_url, archive_page, archive_detail, _archive_examples,
    archive_example, archive_thumb, archive_file,
    _effects, _effects_index, _release_choices, effects_page_view, effect_detail, effect_example,
    effect_flag, release_effect_set, _effects_for_release,
    _fonts, FONT_PREVIEW_STYLES, _fonts_index, _font_file_url, fonts_page_view, font_detail, font_file,
    _frame_tokens, VIDEOS_DIR, _PROJECT_NAME, _video_projects,
    VIDEO_FOCAL_POINTS, _build_video_export_groups, VIDEO_SHAPES, _video_frames, _render_video,
    video_resizer_page, video_page, video_start, video_render, video_resizer_source,
)


# ---------------------------------------------------------------------------
# Studio part 2 (shoot + photo editor, Imagine): routes live in views/shoot.py and
# views/imagine.py (RM 2.0 slice 6)
# ---------------------------------------------------------------------------

import release_manager.views.shoot  # noqa: E402,F401  registers the shoot and /edit routes on the shared app
from release_manager.views.shoot import (  # noqa: E402,F401  re-exports (tests import SHOOT_CATALOGUE; the resizer reads EDITS_DIR)
    SHOOT_CATALOGUE, SHOOT_OUT, _shoot_tools, _shoot_photos, _shoot_filter, _shoot_groups,
    shoot_page, SHOOT_EDIT_PREVIEWS, _shoot_preview, SHOOT_GRADES, GRADE_LABELS, _edit_recipe,
    _GRADE_LOCKS, _GRADE_LOCKS_GUARD, _GRADE_QUEUE, _grade_lock, _warm_grades, _shoot_grade,
    _make_grade, shoot_thumb, IG_GRID_CACHE, IG_PROFILE_PIC, _ig_grid_tiles, _shoot_sims,
    _cover_idea_colour, _cover_font, shoot_covers, shoot_font, shoot_photo, shoot_full,
    shoot_grid_tile, shoot_pfp, shoot_pull_route, shoot_out, EDITS_DIR, EDIT_TAGS, _edit_copies,
    EDIT_PREVIEWS, EDIT_PREVIEW_EDGE, _edit_source, photo_editor, photo_editor_preview,
    photo_editor_save, photo_editor_reveal, photo_editor_delete,
)
import release_manager.views.imagine  # noqa: E402,F401  registers the imagine routes on the shared app
from release_manager.views.imagine import (  # noqa: E402,F401  re-exports
    _imagine_moods, _imagine_request, _imagine_view, imagine_page, imagine_prompt,
    imagine_generate, imagine_round, imagine_decision, _claude_failure, imagine_review,
    imagine_sharpen, imagine_brief, imagine_reference, imagine_as_reference, imagine_test_set,
    imagine_composite, imagine_image, imagine_ref_file,
)


# ---------------------------------------------------------------------------
# Release (Home, release pages, release API, artwork resizer): routes live in
# views/release.py (RM 2.0 slice 7)
# ---------------------------------------------------------------------------

import release_manager.views.release  # noqa: E402,F401  registers the release routes on the shared app
from release_manager.views.release import (  # noqa: E402,F401  re-exports (tests import _dashboard_lines, _make_block)
    _dashboard_lines, dashboard, release_new, release_detail, _title_font_for, _archive_refs_for,
    api_release_delete, release_edit, track_new, track_edit, track_delete, release_links,
    release_clips, release_artwork, FOCAL_POINTS, _build_artwork_export_groups,
    artwork_resizer_page, api_check, api_uncheck, api_validate, api_release_metadata,
    _daily_briefing, _MAKE, _make_block,
    _home_verdict, _home_tickets, _home_review_count,
)


# ---------------------------------------------------------------------------
# Review (System 82, card M10): routes live in views/review.py (RM 2.0 slice 9)
# ---------------------------------------------------------------------------

import release_manager.views.review  # noqa: E402,F401  registers the review routes on the shared app
from release_manager.views.review import (  # noqa: E402,F401  re-exports
    _REVIEW_DEMO, _review_demo_release, review_page, review_thumb, review_tick,
)


# ---------------------------------------------------------------------------
# Words (SEO copy + Bios): routes live in views/words.py (RM 2.0 slice 3)
# ---------------------------------------------------------------------------

import release_manager.views.words  # noqa: E402,F401  registers the words routes on the shared app
from release_manager.views.words import (  # noqa: E402,F401  re-exports
    words_page, seo_copy_page, _words_page, SEO_FIELD_MAP, _write_both,
    api_seo_copy_generate, api_seo_copy_generate_both, api_seo_copy_pick,
    bios_page, api_bios_generate, api_bios_generate_both, api_bios_save,
    api_bios_undo, api_bios_applied, api_bios_profile,
)


# ---------------------------------------------------------------------------
# Studio part 3 (artwork playground, Half the Night cover stages): routes live in
# views/playground.py (RM 2.0 slice 8)
# ---------------------------------------------------------------------------

import release_manager.views.playground  # noqa: E402,F401  registers the playground routes on the shared app
from release_manager.views.playground import (  # noqa: E402,F401  re-exports
    _pg, playground_index, playground_page, playground_image, playground_overlay, playground_wall,
    playground_wall_kept, playground_elements, playground_element_img, playground_iggrid,
    playground_iggrid_img, playground_layout, playground_layout_font, playground_layout_fx,
    playground_layout_snap, playground_layout_extra, playground_layouts_kept,
    playground_elements_kept, playground_colours, playground_colour_file, playground_colours_kept,
    playground_wall_hidden, playground_fonts_hidden, playground_accent, playground_versions,
    playground_version_delete,
)


# ---------------------------------------------------------------------------
# Stats Dashboard (Tool 5): routes live in views/stats.py (RM 2.0 slice 2)
# ---------------------------------------------------------------------------

import release_manager.views.stats  # noqa: E402,F401  registers the stats routes on the shared app
from release_manager.views.stats import (  # noqa: E402,F401  re-exports
    stats_page, stats_thumb, stats_sync_form, stats_manual_form,
    api_stats_sync, api_stats_overview, api_stats_time_series,
    api_stats_manual_entry, api_stats_snapshots, api_stats_bandcamp,
)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ensure_releases_dir()
    debug_flag = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_flag, host="127.0.0.1", port=5001)
