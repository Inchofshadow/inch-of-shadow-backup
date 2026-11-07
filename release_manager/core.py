"""
release_manager/core.py
-----------------------
The shared app of the Release Manager (RM 2.0 slice 2, plans/strategy/rm2-dry-run-2026-11-06.md):
the Flask `app`, CSRF, the context processor, the template filters, the shared constants and the
app-level file routes (artwork, resized, resized video, favicon, 404), and the presets and picked
sizes the two resizer pages share (RM 2.0 slice 5).

Area modules (release_manager/views/*.py) import `app` from here and decorate with `@app.route`,
so every endpoint name stays the same. webapp.py imports and re-exports these names.
"""

from __future__ import annotations

import json
import os
import secrets
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from release_manager.paths import repo_root

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, abort, send_from_directory, send_file,
)

try:
    from flask_wtf.csrf import CSRFProtect, CSRFError
    _CSRF_AVAILABLE = True
except ImportError:
    _CSRF_AVAILABLE = False


def _safe_existing_path(base_dir: Path, raw: str) -> Path | None:
    """Resolve a user-supplied filename against base_dir, blocking traversal.

    Returns None if the resolved path escapes base_dir or the file is missing.
    Only the basename of `raw` is considered -- directory components are stripped.
    """
    name = Path(raw).name
    if not name:
        return None
    candidate = (base_dir / name).resolve()
    try:
        candidate.relative_to(base_dir.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None

from release_manager.models import (
    RELEASE_TYPES, ALL_PLATFORMS, VALID_KEYS, DISTRIBUTION_STATUSES,
)
from release_manager.storage import list_releases


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True   # page changes show on reload, no RM restart needed (Amir 11-06: fewer approval prompts)

def _load_secret_key() -> str:
    env_key = os.getenv("FLASK_SECRET_KEY")
    if env_key:
        return env_key
    secret_file = repo_root() / ".flask_secret"
    if secret_file.exists():
        return secret_file.read_text().strip()
    key = secrets.token_hex(32)
    secret_file.write_text(key)
    try:
        os.chmod(secret_file, 0o600)
    except OSError:
        pass
    return key

app.secret_key = _load_secret_key()

if _CSRF_AVAILABLE:
    app.config.setdefault("WTF_CSRF_TIME_LIMIT", None)  # token valid for session lifetime
    csrf = CSRFProtect(app)

    @app.errorhandler(CSRFError)
    def _handle_csrf_error(e):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"error": "CSRF token missing or invalid"}), 400
        flash("Session expired. Please refresh the page and try again.", "error")
        return redirect(request.referrer or url_for("dashboard"))
else:
    csrf = None

PROJECT_ROOT = repo_root()   # canonical main repo root (robust to git worktrees)
ARTWORK_DIR = PROJECT_ROOT / "artwork"
RESIZED_DIR = PROJECT_ROOT / "resized"
VIDEO_DIR = PROJECT_ROOT / "videos"
RESIZED_VIDEO_DIR = PROJECT_ROOT / "resized_video"
THEME_FILE = PROJECT_ROOT / "theme.json"
GENRES_FILE = PROJECT_ROOT / "genres.json"

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
VIDEO_PLATFORMS = ["instagram", "youtube", "spotify", "tiktok"]

SEED_GENRES = [
    "Acid", "Cinematic", "Dark Disco", "Downtempo", "EBM",
    "Electro", "Exotic", "Melancholic", "Slowmo", "Techno", "Trance",
]

SOCIAL_LINKS = [
    ("Instagram", "https://www.instagram.com/inch_of_shadow/"),
    ("Spotify", "https://open.spotify.com/artist/5k4SyH7JRPMJe1RHYMI2CT"),
    ("Apple Music", "https://music.apple.com/us/artist/inch-of-shadow/1784503341"),
    ("Bandcamp", "https://inchofshadow.bandcamp.com"),
    ("Beatport", "https://www.beatport.com/artist/inch-of-shadow/1276949"),
    ("YouTube", "https://www.youtube.com/@InchofShadow"),
    ("SoundCloud", "https://soundcloud.com/inch-of-shadow"),
    ("Resident Advisor", "https://ra.co/dj/inchofshadow"),
]


# ---------------------------------------------------------------------------
# Theme color configuration
# ---------------------------------------------------------------------------

def load_theme() -> dict:
    """Load custom theme overrides from theme.json."""
    if THEME_FILE.exists():
        try:
            with open(THEME_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            app.logger.warning("theme.json unreadable, using defaults: %s", e)
    return {}


def load_genres() -> list[str]:
    """Load saved genres. Seeds with defaults on first run."""
    if GENRES_FILE.exists():
        try:
            with open(GENRES_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            app.logger.warning("genres.json unreadable, using seed genres: %s", e)
            return sorted(SEED_GENRES, key=str.lower)
    # First run: seed and also scan existing releases
    seen_lower: dict[str, str] = {}
    for g in SEED_GENRES:
        seen_lower[g.lower()] = g
    for rel in list_releases():
        meta = rel.get("metadata", {})
        for field in ("genre_primary", "genre_secondary"):
            g = meta.get(field, "").strip()
            if g and g.lower() not in seen_lower:
                seen_lower[g.lower()] = g
        for t in rel.get("tracks", []):
            for field in ("genre_primary", "genre_secondary"):
                g = t.get(field, "").strip()
                if g and g.lower() not in seen_lower:
                    seen_lower[g.lower()] = g
    result = sorted(seen_lower.values(), key=str.lower)
    with open(GENRES_FILE, "w") as f:
        json.dump(result, f, indent=2)
    return result


def save_genre(genre: str):
    """Add a genre to the saved list if it's new (case-insensitive check)."""
    if not genre or not genre.strip():
        return
    genre = genre.strip()
    genres = load_genres()
    existing_lower = {g.lower() for g in genres}
    if genre.lower() not in existing_lower:
        genres.append(genre)
        genres.sort(key=str.lower)
        with open(GENRES_FILE, "w") as f:
            json.dump(genres, f, indent=2)


# ---------------------------------------------------------------------------
# Template helpers
# ---------------------------------------------------------------------------

@app.context_processor
def inject_globals():
    return {
        "today": datetime.now().strftime("%Y-%m-%d"),
        "RELEASE_TYPES": RELEASE_TYPES,
        "VALID_KEYS": VALID_KEYS,
        "ALL_PLATFORMS": ALL_PLATFORMS,
        "DISTRIBUTION_STATUSES": DISTRIBUTION_STATUSES,
        "theme_overrides": load_theme(),
        "saved_genres": load_genres(),
    }


@app.template_filter("days_until")
def days_until_filter(date_str):
    if not date_str:
        return ""
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return ""
    delta = (target.date() - datetime.now().date()).days     # calendar days, not hours: 11-06 seen on 11-04 at 02:30 is 2
    if delta == 0:
        return "today"
    elif delta == 1:
        return "tomorrow"
    elif delta > 0:
        return f"in {delta} days"
    else:
        return f"{abs(delta)} days ago"


@app.template_filter("platform_label")
def platform_label_filter(key):
    return key.replace("_", " ").title()


# ---------------------------------------------------------------------------
# Artwork helpers
# ---------------------------------------------------------------------------

ARTWORK_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".webp", ".heic", ".heif"}


def find_artwork(slug: str) -> str | None:
    """Find artwork for a release. Checks artwork/{slug}.* first, then scans."""
    if not ARTWORK_DIR.exists():
        return None
    for ext in ARTWORK_EXTENSIONS:
        path = ARTWORK_DIR / f"{slug}{ext}"
        if path.exists():
            return path.name
    # Scan for any image containing the slug
    for path in ARTWORK_DIR.iterdir():
        if path.suffix.lower() in ARTWORK_EXTENSIONS and slug in path.stem.lower():
            return path.name
    return None


def artwork_url_for(slug: str) -> str | None:
    """Return URL to artwork image for a release, or None."""
    name = find_artwork(slug)
    if name:
        return url_for("serve_artwork", filename=name)
    return None


@app.route("/artwork/<path:filename>")
def serve_artwork(filename):
    """Serve artwork images from the artwork/ folder."""
    if not ARTWORK_DIR.exists():
        abort(404)
    return send_from_directory(str(ARTWORK_DIR), filename)


@app.route("/resized/<filename>")
def serve_resized(filename):
    """Serve resized images from the resized/ folder."""
    if not RESIZED_DIR.exists():
        abort(404)
    return send_from_directory(str(RESIZED_DIR), filename)


# Favicon: serves the sidebar avatar as a 32x32 icon so tab icon stays in sync
FAVICON_SOURCE = "avatar.jpg"


@app.route("/favicon.ico")
def favicon():
    from PIL import Image
    img_path = Path(app.static_folder) / FAVICON_SOURCE   # kept in static/ so cleaning resized/ cannot break it
    if not img_path.exists():
        abort(404)
    img = Image.open(img_path)
    img = img.resize((32, 32), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template("base.html", error_title="404", error_msg="Page not found."), 404


@app.template_filter("overlaps")
def _overlaps(picked, ids):
    """True when any of `ids` is among the picked sizes (resizer pages keep their ticks)."""
    return bool(set(picked or ()) & set(ids or ()))


def _picked_templates() -> set:
    """The sizes ticked in the last POST, so a re-rendered page keeps them."""
    out = set()
    if request.method == "POST":
        for t in request.form.getlist("templates"):
            out.update(t.split(","))
    return out


# One-click sets for the resizer pages. "cover": the square release cover is never cropped
# (artwork_resizer.py --cover): every non-square size gets the whole cover on blurred bands.
ARTWORK_PRESETS = [
    {"key": "cover", "label": "Release cover", "cover": True,
     "hint": "Every store size, the YouTube and Instagram sizes, the whole cover, never cropped",
     "templates": ["release_spotify", "release_applemusic", "release_bandcamp", "release_beatport", "release_soundcloud",
                   "release_web_thumb", "thumb_youtube", "thumb_youtube_4k", "thumb_youtube_shorts",
                   "social_instagram_post", "social_instagram_story", "social_instagram_portrait",
                   "social_instagram_grid", "social_instagram_reel_cover"]},
    {"key": "instagram", "label": "Instagram", "hint": "Post, 4:5, 3:4 grid, story, reel cover",
     "templates": ["social_instagram_post", "social_instagram_portrait", "social_instagram_grid",
                   "social_instagram_story", "social_instagram_reel_cover"]},
    {"key": "youtube", "label": "YouTube", "hint": "Thumbnails, Shorts thumbnail, banner, avatar",
     "templates": ["thumb_youtube", "thumb_youtube_4k", "thumb_youtube_shorts", "profile_youtube_banner", "profile_youtube_avatar"]},
    {"key": "profiles", "label": "Profiles and banners", "hint": "Avatars and banners on every platform",
     "templates": ["profile_beatport", "profile_spotify_avatar", "profile_spotify_banner", "profile_applemusic",
                   "profile_youtube_banner", "profile_youtube_avatar", "profile_bandcamp_avatar", "profile_bandcamp_header",
                   "profile_soundcloud_banner", "profile_soundcloud_avatar"]},
    {"key": "all", "label": "Everything", "hint": "Every size", "templates": ["*"]},
]
VIDEO_PRESETS = [
    {"key": "reel", "label": "Reel set", "hint": "One piece, three platforms: Instagram Reel, YouTube Shorts, TikTok",
     "templates": ["reel_instagram", "shorts_youtube", "video_tiktok"]},
    {"key": "canvas", "label": "Spotify Canvas", "hint": "9:16, 3 to 8 seconds, no audio",
     "templates": ["canvas_vertical_spotify"]},
    {"key": "youtube", "label": "YouTube video", "hint": "1080p, and 1440p and 4K when the source is that large",
     "templates": ["video_youtube", "video_youtube_1440", "video_youtube_4k"]},
    {"key": "instagram", "label": "Instagram", "hint": "Reel, story, square and portrait posts",
     "templates": ["reel_instagram", "story_instagram", "post_square_instagram", "post_portrait_instagram"]},
    {"key": "all", "label": "Everything", "hint": "All video sizes", "templates": ["*"]},
]


@app.route("/resized_video/<filename>")
def serve_resized_video(filename):
    """Serve resized videos from the resized_video/ folder."""
    if not RESIZED_VIDEO_DIR.exists():
        abort(404)
    return send_from_directory(str(RESIZED_VIDEO_DIR), filename)


def _limit_note() -> str:
    """The monthly Claude API limit pop-up text once it is reached, else '' (claude_api.LIMIT_USD).
    Shared by the Imagine routes (views/imagine.py) and the Words routes (views/words.py)."""
    from release_manager import claude_api
    return claude_api.limit_note()
