"""
release_manager/reconcile.py
-----------------------------
Keep redundant fields in a release JSON in sync with each other.

Called from storage.save_release() so every write is reconciled --
whether it comes from the edit form, a checklist tick, or a script.

Rules are additive and non-destructive:
- Never demote distribution.status (e.g. approved -> submitted)
- Never uncheck checklist items
- Never overwrite a non-empty date with a different date
"""

from __future__ import annotations

from release_manager.checklist import _CHECKLIST_TO_TIMELINE


_STATUS_RANK = {"draft": 0, "submitted": 1, "approved": 2, "live": 3, "rejected": -1}


def _find_item(items: list[dict], item_id: str) -> dict | None:
    for it in items:
        if it.get("id") == item_id:
            return it
    return None


def _promote_status(dist: dict, new_status: str, changes: list[str]) -> None:
    """Set status only if it's a promotion (higher rank). Never demote."""
    current = dist.get("status", "draft")
    if _STATUS_RANK.get(new_status, -99) > _STATUS_RANK.get(current, -99):
        dist["status"] = new_status
        changes.append(f"distribution.status: {current} -> {new_status}")


def _fill_if_empty(obj: dict, key: str, value: str, label: str, changes: list[str]) -> None:
    if value and not obj.get(key):
        obj[key] = value
        changes.append(f"{label} -> {value}")


def reconcile_release(data: dict) -> list[str]:
    """Mirror data between checklist, distribution, spotify_pitch, and timeline.

    Returns a list of human-readable change descriptions (empty if nothing drifted).
    """
    changes: list[str] = []
    checklist = data.get("checklist", [])
    dist = data.setdefault("distribution", {})

    # --- release_submitted <-> distribution.submitted_date / status ---
    submitted_cl = _find_item(checklist, "release_submitted")
    if submitted_cl:
        if submitted_cl.get("done") and submitted_cl.get("done_date"):
            _fill_if_empty(dist, "submitted_date", submitted_cl["done_date"],
                           "distribution.submitted_date", changes)
            _promote_status(dist, "submitted", changes)
        elif dist.get("submitted_date") and not submitted_cl.get("done"):
            submitted_cl["done"] = True
            submitted_cl["done_date"] = dist["submitted_date"]
            changes.append("checklist.release_submitted: done (from distribution)")

    # --- distributor_approved <-> distribution.approved_date / status ---
    approved_cl = _find_item(checklist, "distributor_approved")
    if approved_cl:
        if approved_cl.get("done") and approved_cl.get("done_date"):
            _fill_if_empty(dist, "approved_date", approved_cl["done_date"],
                           "distribution.approved_date", changes)
            _promote_status(dist, "approved", changes)
        elif dist.get("approved_date") and not approved_cl.get("done"):
            approved_cl["done"] = True
            approved_cl["done_date"] = dist["approved_date"]
            changes.append("checklist.distributor_approved: done (from distribution)")

    # --- live_date -> status = live (always, live is terminal) ---
    if dist.get("live_date"):
        _promote_status(dist, "live", changes)

    # --- upc_code checkbox <-> distribution.upc present ---
    upc_cl = _find_item(checklist, "upc_code")
    if upc_cl:
        if dist.get("upc") and not upc_cl.get("done"):
            upc_cl["done"] = True
            # No done_date source -- leave empty rather than guessing today
            changes.append("checklist.upc_code: done (UPC present)")

    # --- isrc_codes checkbox <-> all tracks have isrc ---
    isrc_cl = _find_item(checklist, "isrc_codes")
    tracks = data.get("tracks", [])
    if isrc_cl and tracks:
        all_have_isrc = all(bool(t.get("isrc")) for t in tracks)
        if all_have_isrc and not isrc_cl.get("done"):
            isrc_cl["done"] = True
            changes.append("checklist.isrc_codes: done (all tracks have ISRC)")

    # --- spotify_pitch block <-> checklist.spotify_pitch ---
    pitch_cl = _find_item(checklist, "spotify_pitch")
    pitch_block = data.get("spotify_pitch")
    if pitch_cl and isinstance(pitch_block, dict):
        if pitch_cl.get("done") and pitch_cl.get("done_date"):
            _fill_if_empty(pitch_block, "submitted_date", pitch_cl["done_date"],
                           "spotify_pitch.submitted_date", changes)
        elif pitch_block.get("submitted_date") and not pitch_cl.get("done"):
            pitch_cl["done"] = True
            pitch_cl["done_date"] = pitch_block["submitted_date"]
            changes.append("checklist.spotify_pitch: done (from spotify_pitch block)")

    # --- mirror checklist.done to timeline.done ---
    # Multiple checklist items can map to one timeline milestone
    # (e.g. genre_tags + credits_confirmed -> metadata_filled).
    # A timeline milestone is done only when ALL mapped checklist items are done.
    timeline = data.get("timeline", [])
    by_timeline: dict[str, list[bool]] = {}
    for cl_item in checklist:
        tl_id = _CHECKLIST_TO_TIMELINE.get(cl_item["id"], cl_item["id"])
        by_timeline.setdefault(tl_id, []).append(bool(cl_item.get("done")))

    for tl_id, done_states in by_timeline.items():
        tl_item = _find_item(timeline, tl_id)
        if not tl_item:
            continue
        should_be_done = all(done_states)
        if tl_item.get("done") != should_be_done:
            tl_item["done"] = should_be_done
            changes.append(f"timeline.{tl_id}.done -> {should_be_done}")

    return changes
