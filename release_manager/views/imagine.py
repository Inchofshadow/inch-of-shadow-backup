"""
release_manager/views/imagine.py
--------------------------------
Studio area module, part 2b (RM 2.0 slice 6, plans/strategy/rm2-dry-run-2026-11-06.md): Imagine, the
AI images on brand. The free prompt preview and the PAID routes (generate, round, test-set) moved as
they were: nothing is sent without Amir's confirmed click. Routes register on the shared app from
core.py, so the endpoint names are unchanged. webapp.py imports this module and re-exports the names.
Tests that patch load_release / save_release / _shoot_photos / _shoot_tools / SHOOT_EDIT_PREVIEWS for
these routes patch this module, since the routes read its globals.
"""

from __future__ import annotations

from datetime import datetime

from flask import render_template, request, url_for, jsonify, abort, send_from_directory

from release_manager.core import app, _safe_existing_path, _limit_note
from release_manager.storage import load_release, save_release, list_releases
from release_manager.views.studio import _frame_tokens
from release_manager.views.shoot import _shoot_photos, _shoot_tools, SHOOT_EDIT_PREVIEWS

# ---------------------------------------------------------------------------
# Imagine (Machine-17): AI images on brand. Prompt built from the four layers
# (release_manager/imagine.py); nothing is sent without Amir's click on Generate.
# ---------------------------------------------------------------------------

def _imagine_moods() -> dict:
    try:
        return _frame_tokens().get("moods", {})
    except Exception:
        return {}


def _imagine_request(data: dict) -> dict:
    """Everything a prompt or a render needs, from the page's JSON, checked."""
    from release_manager import imagine as im
    slug = (data.get("release") or "").strip()
    release = load_release(slug) if slug else None
    choice = {k: (data.get("choice") or {}).get(k) or "" for k in im.OPTION_KINDS}
    choice["motif"] = [m for m in ((data.get("choice") or {}).get("motif") or []) if m in im.options("motif")][:2]
    choice["mood"] = (data.get("choice") or {}).get("mood") or ""
    ref_items = []
    for r in data.get("refs") or []:
        found = next((x for x in im.refs(r.get("scope", "")) if x["file"] == r.get("file")), None)
        if found:
            ref_items.append(found)
    preset = im.PRESETS.get(data.get("preset") or "draft")
    model, quality = (data.get("model"), data.get("quality")) if data.get("preset") == "custom" else preset
    size = im.SIZES.get(data.get("size") or "square", im.SIZES["square"])[1]
    n = max(1, min(int(data.get("n") or 1), 4))
    prompt = im.build_prompt(data.get("kind") or "cover", data.get("subject") or "", choice, release, _imagine_moods(),
                             data.get("title_area") or "top", data.get("light_direction") or "", ref_items)
    return {"prompt": prompt, "refs": ref_items, "model": model, "quality": quality, "size": size, "n": n,
            "meta": {"release": slug or None, "kind": data.get("kind") or "cover", "subject": data.get("subject") or "",
                     "choice": choice, "title_area": data.get("title_area") or "top"}}


def _imagine_view(rec: dict) -> dict:
    return {**rec, "url": url_for("imagine_image", filename=rec["file"]),
            "edit": url_for("photo_editor", src=f"imagine:{rec['file']}")}


@app.route("/imagine")
def imagine_page():
    from release_manager import imagine as im
    releases = sorted(list_releases(), key=lambda r: r.get("release_date") or "", reverse=True)
    slug = request.args["release"] if "release" in request.args else (releases[0]["slug"] if releases else "")
    release = load_release(slug) if slug else None
    brief = im.brief_of(release)
    opts = {k: im.options(k) for k in im.OPTION_KINDS + im.MULTI_KINDS}
    ref_sets = {"brand": im.refs("brand")}
    if slug:
        ref_sets[slug] = im.refs(slug)
    return render_template("imagine.html", im=im, releases=releases, slug=slug, release=release, brief=brief,
                           opts=opts, moods=_imagine_moods(), ref_sets=ref_sets,
                           images=[_imagine_view(r) for r in im.images(slug or None)][:60],
                           spend=im.month_spend(), stats=im.option_stats()[:8],
                           test_runs=[{**r, "images": [_imagine_view(x) for x in r["images"]]} for r in im.test_runs()[:2]],
                           test_estimate=im.estimate(*im.PRESETS["draft"], "1024x1024", len(im.test_set())))


@app.route("/imagine/prompt", methods=["POST"])
def imagine_prompt():
    """Free: the exact prompt that would be sent, and the estimated cost."""
    from release_manager import imagine as im
    try:
        req = _imagine_request(request.get_json(silent=True) or {})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    return jsonify({"ok": True, "prompt": req["prompt"], "model": req["model"], "quality": req["quality"],
                    "size": req["size"], "n": req["n"], "sent_refs": sum(1 for r in req["refs"] if r.get("send")),
                    "estimate": im.estimate(req["model"], req["quality"], req["size"], req["n"])})


@app.route("/imagine/generate", methods=["POST"])
def imagine_generate():
    """PAID: runs only when Amir presses Generate and confirms the cost."""
    from release_manager import imagine as im
    data = request.get_json(silent=True) or {}
    if not data.get("confirmed"):
        return jsonify({"ok": False, "error": "Not confirmed."}), 400
    try:
        req = _imagine_request(data)
        recs = im.generate(req["prompt"], req["model"], req["quality"], req["size"], req["n"], req["refs"], req["meta"])
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:                                   # the API's own message (quota, moderation, key)
        return jsonify({"ok": False, "error": f"OpenAI: {e}"}), 502
    return jsonify({"ok": True, "images": [_imagine_view(r) for r in recs], "spend": im.month_spend()})


@app.route("/imagine/round", methods=["POST"])
def imagine_round():
    """Machine-25: one more draft from a review's prompt fix. Without `confirmed` it only returns the
    exact prompt and the estimate (free); with it, the PAID render, same as Generate."""
    from release_manager import imagine as im
    data = request.get_json(silent=True) or {}
    try:
        nxt = im.next_round(str(data.get("id", "")), data.get("fix") or "", data.get("closeness") or "mostly")
        model, quality = im.PRESETS["final" if data.get("preset") == "final" else "draft"]
        n = max(1, min(int(data.get("n") or 1), 4))
        if not data.get("confirmed"):
            return jsonify({"ok": True, "prompt": nxt["prompt"], "model": model, "quality": quality, "size": nxt["size"],
                            "n": n, "sent_refs": len(nxt["refs"]), "estimate": im.estimate(model, quality, nxt["size"], n)})
        recs = im.generate(nxt["prompt"], model, quality, nxt["size"], n, nxt["refs"], nxt["meta"])
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:                                   # the API's own message (quota, moderation, key)
        return jsonify({"ok": False, "error": f"OpenAI: {e}"}), 502
    return jsonify({"ok": True, "images": [_imagine_view(r) for r in recs], "spend": im.month_spend()})


@app.route("/imagine/decision", methods=["POST"])
def imagine_decision():
    from release_manager import imagine as im
    data = request.get_json(silent=True) or {}
    try:
        rec = im.set_decision(data.get("id", ""), data.get("decision", ""))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    if rec.get("decision") == "anchor" and rec.get("release"):
        rel = load_release(rec["release"])
        if rel:
            rel.setdefault("image_brief", {})["anchor"] = rec["file"]
            save_release(rel)
    return jsonify({"ok": True, "decision": rec.get("decision")})


def _claude_failure(what: str, e: Exception):
    """A Claude API failure as the page should see it: the API's own status and reason (no key,
    no path) so 'out of credit' or 'rate limited' reads as what it is; anything else stays generic."""
    import anthropic
    app.logger.exception("%s failed", what)
    if isinstance(e, anthropic.APIStatusError):
        reason = " ".join(str(getattr(e, "message", "") or "").split())[:200]
        return jsonify({"ok": False, "error": f"Claude API error {e.status_code}: {reason}"}), 502
    if isinstance(e, anthropic.APIConnectionError):
        return jsonify({"ok": False, "error": "Could not reach the Claude API. Check the connection and try again."}), 502
    return jsonify({"ok": False, "error": f"{what} failed. Try again in a minute."}), 502


@app.route("/imagine/review", methods=["POST"])
def imagine_review():
    """Machine-22: Claude reviews a generated draft against its own prompt (no re-render)."""
    from release_manager import imagine_review as rv
    data = request.get_json(silent=True) or {}
    if data.get("who") == "openai":                          # Machine-26: the second reviewer
        try:
            rec = rv.review_openai(str(data.get("id", "")))
        except ValueError as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        except Exception as e:                               # the API's own message (quota, key)
            app.logger.exception("imagine review (openai) failed")
            return jsonify({"ok": False, "error": f"OpenAI: {str(e)[:200]}"}), 502
        return jsonify({"ok": True, "review": rec["review_openai"]})
    try:
        rec = rv.review(str(data.get("id", "")))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e), "limit_note": _limit_note()}), 400
    except Exception as e:
        return _claude_failure("imagine review", e)
    return jsonify({"ok": True, "review": rec["review"], "limit_note": _limit_note()})


@app.route("/imagine/sharpen", methods=["POST"])
def imagine_sharpen():
    """Machine-23: Claude rewrites the subject as one precise visual sentence (suggestion only)."""
    from release_manager import imagine_subject as sh
    data = request.get_json(silent=True) or {}
    try:
        req = _imagine_request(data)
        out = sh.sharpen(data.get("subject") or "", req["prompt"], data.get("kind") or "")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e), "limit_note": _limit_note()}), 400
    except Exception as e:
        return _claude_failure("imagine sharpen", e)
    return jsonify({"ok": True, "subject": out["subject"], "why": out["why"], "limit_note": _limit_note()})


@app.route("/imagine/brief", methods=["POST"])
def imagine_brief():
    """The release brief (layer 2): mood pair, motifs, concept, the release's own never list."""
    from release_manager import imagine as im
    data = request.get_json(silent=True) or {}
    rel = load_release(data.get("release") or "")
    if rel is None:
        return jsonify({"ok": False, "error": "Unknown release."}), 404
    b = rel.setdefault("image_brief", {})
    b["mood"] = data.get("mood") if data.get("mood") in _imagine_moods() else ""
    b["motifs"] = [m for m in (data.get("motifs") or []) if m in im.options("motif")][:2]
    b["concept"] = (data.get("concept") or "").strip()[:400]
    b["never"] = (data.get("never") or "").strip()[:800]
    save_release(rel)
    return jsonify({"ok": True, "brief": b})


@app.route("/imagine/reference", methods=["POST"])
def imagine_reference():
    """Add a reference: 'mine' / 'approved' may be sent as an image; 'other' is used as words only."""
    from release_manager import imagine as im
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify({"ok": False, "error": "No file."}), 400
    try:
        item = im.add_ref(request.form.get("scope", "brand"), f.filename, f.read(), request.form.get("role", "style"),
                          request.form.get("note", ""), request.form.get("owner") in ("mine", "approved"),
                          request.form.get("owner", "other"))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    return jsonify({"ok": True, "ref": item})


@app.route("/imagine/as-reference", methods=["POST"])
def imagine_as_reference():
    """Make one of our generated images a reference (it is ours: it may be sent as an image)."""
    from release_manager import imagine as im
    data = request.get_json(silent=True) or {}
    rec = im.record(data.get("id", ""))
    if rec is None:
        return jsonify({"ok": False, "error": "Unknown image."}), 404
    try:
        item = im.add_ref(data.get("scope") or rec.get("release") or "brand", rec["file"], (im.OUT / rec["file"]).read_bytes(),
                          data.get("role") or "style", data.get("note") or f"our image {rec['id']}", True, "approved")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    return jsonify({"ok": True, "ref": item})


@app.route("/imagine/test-set", methods=["POST"])
def imagine_test_set():
    """PAID, on Amir's confirmed click: the five fixed prompts of docs/brand/ai-test-set.json, one
    image each, so a new model can be compared with the look we know."""
    from release_manager import imagine as im
    data = request.get_json(silent=True) or {}
    if not data.get("confirmed"):
        return jsonify({"ok": False, "error": "Not confirmed."}), 400
    model, quality = im.PRESETS.get(data.get("preset") or "draft", im.PRESETS["draft"])
    run = datetime.now().strftime("%Y%m%d-%H%M%S")
    made = []
    try:
        for t in im.test_set():
            choice = {k: t.get("options", {}).get(k, "") for k in im.OPTION_KINDS}
            choice["motif"], choice["mood"] = [], ""
            prompt = im.build_prompt(t["kind"], t["subject"], choice, None, _imagine_moods(),
                                     "none" if t["kind"] == "texture" else "top",
                                     "above" if t["kind"] == "background" else "")
            made += im.generate(prompt, model, quality, "1024x1024", 1, [],
                                {"release": "testset", "test_run": run, "test_key": t["key"], "kind": t["kind"],
                                 "subject": t["subject"], "choice": choice})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Stopped after {len(made)} image(s): {e}"}), 502
    return jsonify({"ok": True, "run": run, "images": [_imagine_view(r) for r in made], "spend": im.month_spend()})


@app.route("/imagine/composite", methods=["POST"])
def imagine_composite():
    """LOCAL and free: one of our background plates with Amir's shoot photo cut out onto it."""
    from release_manager import imagine as im
    data = request.get_json(silent=True) or {}
    _, photos = _shoot_photos()
    p = next((x for x in photos if x["id"] == (data.get("photo") or "").strip()), None)
    if p is None:
        return jsonify({"ok": False, "error": "Unknown shoot photo (use its number, like out-152)."}), 404
    sc, _ = _shoot_tools()
    src = sc.DRIVE / p["edit"]
    if not src.is_file():
        src = SHOOT_EDIT_PREVIEWS / f"{p['id']}.jpg"            # without the drive: her edit's preview
    if not src.is_file():
        return jsonify({"ok": False, "error": "Her edit is not available: connect the Intenso."}), 409
    try:
        rec = im.composite(data.get("id", ""), src, float(data.get("scale") or 0.78), data.get("position") or "center")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    return jsonify({"ok": True, "image": _imagine_view(rec)})


@app.route("/imagine/img/<path:filename>")
def imagine_image(filename):
    from release_manager import imagine as im
    f = _safe_existing_path(im.OUT, filename)
    if f is None:
        abort(404)
    return send_from_directory(str(f.parent), f.name)


@app.route("/imagine/ref/<scope>/<path:filename>")
def imagine_ref_file(scope, filename):
    from release_manager import imagine as im
    try:
        base = im._scope_dir(scope)
    except ValueError:
        abort(404)
    f = _safe_existing_path(base, filename)
    if f is None:
        abort(404)
    return send_from_directory(str(f.parent), f.name)
