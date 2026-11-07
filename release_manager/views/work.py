"""
release_manager/views/work.py
-----------------------------
Work area module (RM 2.0 slice 4, plans/strategy/rm2-dry-run-2026-11-06.md): the Work page
(/tickets and /board, tickets + Control Panel board + By number), the board cards JSON, Outreach
and the read-only SC status page. Routes register on the shared app from core.py, so the endpoint
names are unchanged. webapp.py imports this module and re-exports the names. Tests that patch
CONTROL_PANEL_FILE for these routes patch this module.
"""

from __future__ import annotations

from flask import render_template, request, jsonify

from release_manager.core import app, PROJECT_ROOT


# ---------------------------------------------------------------------------
# Work: tickets, board, By number
# ---------------------------------------------------------------------------

CONTROL_PANEL_FILE = PROJECT_ROOT / "plans" / "control-panel" / "tickets.json"
TICKETS_FILE = PROJECT_ROOT / "plans" / "tickets.json"


@app.route("/tickets")
def tickets_page():
    """Work, opened on the tickets (plans/tickets.json); ?group=metric is the By number view."""
    return _work_page("tickets")


def _work_page(focus: str):
    """Work (RM 2.0 slice 1b): tickets on top, By area or By number (?group=metric), and the
    Control Panel board below. /tickets and /board both render it. A broken file shows its error
    in its own section; the page answers 500 only when the file of the opened section is broken."""
    from release_manager.tickets import TicketsError, build_view, load_tickets
    from release_manager import board as cp
    by_number = request.args.get("group") == "metric"
    ctx = {"focus": focus, "by_number": by_number, "view": None, "mview": None, "cards_json": [],
           "tickets_error": None, "board": None, "board_error": None, "cp": None}
    board_data = None
    try:
        board_data = cp.load_board(CONTROL_PANEL_FILE)
        ctx["board"] = cp.build_view(board_data)
        ctx["cp"] = {
            "open": sum(v for k, v in ctx["board"]["counts"].items() if k != "done"),
            "waiting": ctx["board"]["waiting_on_amir"],
            "floor": ctx["board"]["current_floor"],
            "deadline": (ctx["board"]["deadline"] or {}).get("date", ""),
        }
    except cp.BoardError as e:
        board_data, ctx["board"], ctx["board_error"] = None, None, str(e)
    try:
        data = load_tickets(TICKETS_FILE)
        if by_number:
            ctx["mview"] = _tickets_by_metric(data, board_data)
            ctx["cards_json"] = [c for g in ctx["mview"]["groups"] for c in g["tickets"]]
        else:
            ctx["view"] = build_view(data)
            ctx["cards_json"] = [c for sec in ctx["view"]["sections"] for c in sec["tickets"]]
    except TicketsError as e:
        ctx["tickets_error"] = str(e)
    failed = ctx["tickets_error"] if focus == "tickets" else ctx["board_error"]
    return render_template("work.html", **ctx), (500 if failed else 200)


def _tickets_by_metric(data: dict, board_data: dict | None) -> dict:
    """The By number view: open tickets of both boards under the number they move."""
    from release_manager.tickets import build_metric_view, control_panel_cards, metric_readings
    try:
        from stats.targets import load_targets
        readings = metric_readings(load_targets())
    except Exception:          # targets file missing or broken: group headers without numbers
        readings = {}
    extra = control_panel_cards(board_data) if board_data is not None else []
    return build_metric_view(data, readings, extra)


OUTREACH_FILE = PROJECT_ROOT / "plans" / "outreach-batches.json"
BOOKING_TARGETS_FILE = PROJECT_ROOT / "scene_intelligence" / "booking_targets.json"


@app.route("/outreach")
def outreach_page():
    """Outreach: read-only batches of contacts with info, links, scene score and draft."""
    from release_manager.outreach import OutreachError, build_view, load
    try:
        data, by_name = load(OUTREACH_FILE, BOOKING_TARGETS_FILE)
        view = build_view(data, by_name)
    except OutreachError as e:
        return render_template("outreach.html", view=None, error=str(e)), 500
    return render_template("outreach.html", view=view, error=None)


@app.route("/outreach/tick", methods=["POST"])
def outreach_tick():
    """Save Amir's review tick for one contact (try: true / false / null)."""
    from release_manager.outreach import OutreachError, set_try
    payload = request.get_json(silent=True) or {}
    batch_id = str(payload.get("batch", ""))[:80]
    name = str(payload.get("name", ""))[:200]
    value = payload.get("try")
    if value not in (True, False, None) or not batch_id or not name:
        return jsonify({"ok": False, "error": "bad request"}), 400
    try:
        return jsonify({"ok": True, **set_try(OUTREACH_FILE, batch_id, name, value)})
    except OutreachError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/board")
def board_page():
    """Work, opened on the Control Panel board (read-only tower of plans/control-panel/tickets.json)."""
    return _work_page("board")


@app.route("/api/board/cards")
def api_board_cards():
    """The board's cards as JSON; the page fetches them instead of carrying 187 KB inline."""
    from release_manager.board import BoardError, build_view, load_board
    try:
        view = build_view(load_board(CONTROL_PANEL_FILE))
    except BoardError as e:
        return jsonify({"error": str(e)}), 500
    return jsonify([c for f in view["floors"] for c in f["tickets"]])


# ---------------------------------------------------------------------------
# SC status: read-only (SC chat answer for slice 4, 2026-11-06). The run and test-auth
# routes are gone; get_status() reads local files only, nothing here calls the SC API.
# ---------------------------------------------------------------------------

def _sc_engagement_import():
    """Lazy import of sc_engagement to avoid slowing down app start."""
    try:
        import scene_intelligence.sc_engagement as sce
        return sce
    except ImportError:
        return None


@app.route("/sc-automation")
def sc_automation_page():
    """SC status: budgets, follow tracker and recent activity from local files, read-only."""
    sce = _sc_engagement_import()
    if sce is None:
        return render_template(
            "base.html",
            error_title="Module Error",
            error_msg="scene_intelligence.sc_engagement could not be loaded.",
        )
    status = sce.get_status()
    return render_template("sc_automation.html", status=status)


@app.route("/api/sc-automation/status")
def api_sc_status():
    """Return current SC engagement state as JSON."""
    sce = _sc_engagement_import()
    if sce is None:
        return jsonify({"error": "sc_engagement module not found"}), 500
    return jsonify(sce.get_status())
