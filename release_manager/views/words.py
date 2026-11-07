"""
release_manager/views/words.py
------------------------------
Words area module (RM 2.0 slice 3, plans/strategy/rm2-dry-run-2026-11-06.md): the Words page (SEO copy
and Bios as two tabs) and their JSON API. Routes register on the shared app from core.py, so the
endpoint names (seo_copy_page, bios_page, api_seo_copy_generate, ...) are unchanged; /words is new.
webapp.py imports this module. Tests that patch load_release / save_release / list_releases for these
routes patch this module, since the routes read its globals.
"""

from __future__ import annotations

from datetime import datetime

from flask import render_template, request, jsonify

from release_manager.core import app, _limit_note
from release_manager.storage import load_release, save_release, list_releases


# ---------------------------------------------------------------------------
# SEO Copy Generator
# ---------------------------------------------------------------------------

@app.route("/words")
def words_page():
    """Words: SEO copy and Bios on one page, opened on the SEO copy tab."""
    return _words_page("seo")


@app.route("/seo-copy")
def seo_copy_page():
    """Words, opened on the SEO copy tab (?release= preselects the release; release_detail links it)."""
    return _words_page("seo")


def _words_page(tab: str):
    """Words (RM 2.0 slice 3): the SEO copy tab (was seo_copy.html) and the Bios tab (was bios.html)
    on one page. /words, /seo-copy and /bios all render it; `tab` is the one that opens."""
    from release_manager.seo_copy_generator import PLATFORMS, TONES
    from release_manager.bio_manager import load_profile, PLATFORM_ORDER, PLATFORM_LABELS
    release_slug = request.args.get("release", "")
    release_options = [
        {"slug": r["slug"], "title": r["metadata"]["title"], "type": r["metadata"]["release_type"]}
        for r in list_releases()
    ]
    return render_template(
        "words.html",
        tab=tab,
        platforms=PLATFORMS,
        tones=TONES,
        release_options=release_options,
        preselected_release=release_slug,
        profile=load_profile(),
        platform_order=PLATFORM_ORDER,
        platform_labels=PLATFORM_LABELS,
    )


# Flat writer keys -> release seo_copy[platform][field] (used by generate, and by pick for "Write with both")
SEO_FIELD_MAP = {
    "soundcloud": {"description": "soundcloud_description"},
    "instagram": {"caption": "instagram_caption", "hashtags": "instagram_hashtags"},
    "youtube": {"titles": "youtube_titles", "description": "youtube_description"},
    "bandcamp": {"about": "bandcamp_about", "tags": "bandcamp_tags"},
    "beatport": {"description": "beatport_description"},
    "spotify": {"pitch": "spotify_pitch", "artist_pick": "spotify_artist_pick"},
    "apple_music": {"bio": "apple_music_bio"},
}


def _write_both(job):
    """Machine-27: run one writer job for Claude and for GPT at the same time. Nothing is saved here.
    Returns ({provider: result}, {provider: error})."""
    from concurrent.futures import ThreadPoolExecutor
    from release_manager.writers_ai import LABELS, PROVIDERS
    out, errors = {}, {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {p: pool.submit(job, p) for p in PROVIDERS}
        for p, fut in futures.items():
            try:
                out[p] = fut.result()
            except ValueError as e:
                errors[p] = str(e)
            except Exception as e:                           # the API's own message (credit, quota, key)
                app.logger.exception("write with both: %s failed", p)
                errors[p] = f"{LABELS[p]} failed: {' '.join(str(getattr(e, 'message', e)).split())[:200]}"
    return out, errors


@app.route("/api/seo-copy/generate", methods=["POST"])
def api_seo_copy_generate():
    """Generate SEO copy for a release via Claude API."""
    data = request.get_json(silent=True) or {}

    slug = data.get("slug", "").strip()
    platforms = data.get("platforms", [])
    tone = data.get("tone", "authentic")

    if not slug:
        return jsonify({"error": "No release selected."}), 400
    if not platforms or not isinstance(platforms, list):
        return jsonify({"error": "No platforms selected."}), 400

    from release_manager.seo_copy_generator import PLATFORMS as VALID_PLATFORMS
    valid_ids = {p["id"] for p in VALID_PLATFORMS}
    platforms = [p for p in platforms if isinstance(p, str) and p in valid_ids]
    if not platforms:
        return jsonify({"error": "No valid platforms selected."}), 400

    if tone not in {"authentic", "professional", "hype"}:
        tone = "authentic"

    rel = load_release(slug)
    if not rel:
        return jsonify({"error": f"Release '{slug}' not found."}), 404

    try:
        from release_manager.seo_copy_generator import generate_copy
        result = generate_copy(rel, platforms, tone)

        # Save generated copy to release JSON
        seo_copy = rel.get("seo_copy", {})
        seo_copy["generated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        seo_copy["tone"] = tone

        # Map flat API response keys to platform-grouped structure
        platform_map = SEO_FIELD_MAP
        for platform_id, field_map in platform_map.items():
            for dest_key, src_key in field_map.items():
                if src_key in result:
                    seo_copy.setdefault(platform_id, {})[dest_key] = result[src_key]

        rel["seo_copy"] = seo_copy
        save_release(rel)

        return jsonify({"ok": True, "copy": result, "limit_note": _limit_note()})
    except ValueError as e:
        return jsonify({"error": str(e), "limit_note": _limit_note()}), 500
    except Exception as e:
        return jsonify({"error": f"Generation failed: {str(e)[:200]}"}), 500


@app.route("/api/seo-copy/generate-both", methods=["POST"])
def api_seo_copy_generate_both():
    """Machine-27: the same SEO copy from Claude and from GPT, side by side. Saves nothing: Amir picks
    per field with /api/seo-copy/pick."""
    data = request.get_json(silent=True) or {}
    slug = data.get("slug", "").strip()
    from release_manager.seo_copy_generator import PLATFORMS as VALID_PLATFORMS, generate_copy
    valid_ids = {p["id"] for p in VALID_PLATFORMS}
    platforms = [p for p in (data.get("platforms") or []) if isinstance(p, str) and p in valid_ids]
    tone = data.get("tone") if data.get("tone") in {"authentic", "professional", "hype"} else "authentic"
    if not slug or not platforms:
        return jsonify({"error": "Pick a release and at least one platform."}), 400
    rel = load_release(slug)
    if not rel:
        return jsonify({"error": f"Release '{slug}' not found."}), 404
    out, errors = _write_both(lambda provider: generate_copy(rel, platforms, tone, provider=provider))
    if not out:
        return jsonify({"error": " / ".join(errors.values()), "limit_note": _limit_note()}), 502
    return jsonify({"ok": True, "copies": out, "errors": errors, "limit_note": _limit_note()})


@app.route("/api/seo-copy/pick", methods=["POST"])
def api_seo_copy_pick():
    """Machine-27: save one picked field into the release's seo_copy, with who wrote it."""
    data = request.get_json(silent=True) or {}
    slug, key, value = data.get("slug", "").strip(), data.get("key", ""), data.get("value")
    written_by = data.get("written_by") if data.get("written_by") in ("claude", "openai") else "edit"
    target = next(((pid, dest) for pid, fields in SEO_FIELD_MAP.items() for dest, src in fields.items() if src == key), None)
    if target is None:
        return jsonify({"error": "Unknown field."}), 400
    if not (isinstance(value, str) or (isinstance(value, list) and all(isinstance(v, str) for v in value))):
        return jsonify({"error": "The text must be a string or a list of strings."}), 400
    rel = load_release(slug)
    if not rel:
        return jsonify({"error": f"Release '{slug}' not found."}), 404
    seo_copy = rel.get("seo_copy", {})
    seo_copy.setdefault(target[0], {})[target[1]] = value
    seo_copy.setdefault("written_by", {})[key] = written_by
    seo_copy["generated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    rel["seo_copy"] = seo_copy
    save_release(rel)
    return jsonify({"ok": True})

# ---------------------------------------------------------------------------
# Bio Manager
# ---------------------------------------------------------------------------

@app.route("/bios")
def bios_page():
    """Words, opened on the Bios tab (two docs name localhost:5001/bios)."""
    return _words_page("bios")


@app.route("/api/bios/generate", methods=["POST"])
def api_bios_generate():
    """Generate bios for all platforms via Claude API."""
    from release_manager.bio_manager import load_profile, generate_bios
    profile = load_profile()
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404
    releases = list_releases()
    latest = releases[-1] if releases else None
    try:
        result = generate_bios(profile, latest)
        return jsonify({"ok": True, "bios": result})
    except ValueError as e:
        return jsonify({"error": str(e), "limit_note": _limit_note()}), 500
    except Exception as e:
        return jsonify({"error": f"Generation failed: {str(e)[:200]}"}), 500


@app.route("/api/bios/generate-both", methods=["POST"])
def api_bios_generate_both():
    """Machine-27: bios from Claude and from GPT, side by side. Saves nothing: 'Use This' on either
    side saves that one through /api/bios/save with written_by."""
    from release_manager.bio_manager import load_profile, generate_bios
    profile = load_profile()
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404
    releases = list_releases()
    latest = releases[-1] if releases else None
    out, errors = _write_both(lambda provider: generate_bios(profile, latest, provider=provider))
    if not out:
        return jsonify({"error": " / ".join(errors.values()), "limit_note": _limit_note()}), 502
    return jsonify({"ok": True, "bios": out, "errors": errors, "limit_note": _limit_note()})


@app.route("/api/bios/save", methods=["PUT"])
def api_bios_save():
    """Save a bio for a specific platform."""
    from release_manager.bio_manager import load_profile, save_profile
    data = request.get_json(silent=True) or {}
    platform = data.get("platform", "").strip()
    bio = data.get("bio", "")
    source = data.get("source", "edit")
    if not platform:
        return jsonify({"error": "No platform specified."}), 400
    if not isinstance(bio, str):
        return jsonify({"error": "Bio must be a string."}), 400
    profile = load_profile()
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404
    bios = profile.get("bios", {})
    if platform not in bios:
        return jsonify({"error": f"Unknown platform: {platform}"}), 400
    if source == "generate":
        bios[platform]["previous"] = bios[platform].get("current", "")
        bios[platform]["current"] = bio
        if data.get("written_by") in ("claude", "openai"):          # Machine-27: who wrote the accepted bio
            bios[platform]["written_by"] = data["written_by"]
        bios[platform]["applied"] = False
        bios[platform]["applied_date"] = None
    else:
        bios[platform]["current"] = bio
        bios[platform]["applied"] = False
        bios[platform]["applied_date"] = None
    profile["bios"] = bios
    save_profile(profile)
    return jsonify({"ok": True})


@app.route("/api/bios/undo", methods=["PUT"])
def api_bios_undo():
    """Undo a bio change for a specific platform."""
    from release_manager.bio_manager import load_profile, save_profile
    data = request.get_json(silent=True) or {}
    platform = data.get("platform", "").strip()
    if not platform:
        return jsonify({"error": "No platform specified."}), 400
    profile = load_profile()
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404
    bios = profile.get("bios", {})
    if platform not in bios:
        return jsonify({"error": f"Unknown platform: {platform}"}), 400
    prev = bios[platform].get("previous")
    if prev is None:
        return jsonify({"error": "Nothing to undo."}), 400
    bios[platform]["previous"] = bios[platform]["current"]
    bios[platform]["current"] = prev
    bios[platform]["applied"] = False
    bios[platform]["applied_date"] = None
    profile["bios"] = bios
    save_profile(profile)
    return jsonify({"ok": True})


@app.route("/api/bios/applied", methods=["PUT"])
def api_bios_applied():
    """Mark a bio as applied on the platform."""
    from release_manager.bio_manager import load_profile, save_profile
    data = request.get_json(silent=True) or {}
    platform = data.get("platform", "").strip()
    if not platform:
        return jsonify({"error": "No platform specified."}), 400
    profile = load_profile()
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404
    bios = profile.get("bios", {})
    if platform not in bios:
        return jsonify({"error": f"Unknown platform: {platform}"}), 400
    bios[platform]["applied"] = True
    bios[platform]["applied_date"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    profile["bios"] = bios
    save_profile(profile)
    return jsonify({"ok": True})


@app.route("/api/bios/profile", methods=["PUT"])
def api_bios_profile():
    """Update artist profile variables (not bios)."""
    from release_manager.bio_manager import load_profile, save_profile
    data = request.get_json(silent=True) or {}
    profile = load_profile()
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404
    for field in ["keywords", "labels", "venues", "collaborators"]:
        if field in data:
            val = data[field]
            if isinstance(val, list) and all(isinstance(x, str) for x in val):
                profile[field] = [x.strip() for x in val if x.strip()]
    if "booking_email" in data and isinstance(data["booking_email"], str):
        profile["booking_email"] = data["booking_email"].strip()
    if "links" in data and isinstance(data["links"], dict):
        profile["links"] = {
            k: v for k, v in data["links"].items()
            if isinstance(k, str) and isinstance(v, str)
        }
    save_profile(profile)
    return jsonify({"ok": True})
