#!/usr/bin/env python3
"""System 67: one spend page with early warnings (strategy review 2026-11-05, section 1 + rec 4).

Read-only over the ledgers that exist. Where a ledger is missing the row says "not logged";
nothing is estimated.

  python3 stats/spend.py          # print the table
  python3 stats/spend.py --json   # also write stats_snapshots/spend_latest.json (previous -> .bak)

Ledgers read:
  Claude API      stats_snapshots/claude_spend.json      monthly totals + per-job "by" (release_manager/claude_api.py)
  OpenAI text     stats_snapshots/openai_spend.json      same shape (release_manager/openai_api.py)
  Image renders   generated_images/imagine/*.json        one record per render with cost_usd (release_manager/imagine.py)
  Raw renders     generated_images/pinocchio-single/     files only, no cost record (artwork/edits/half-the-night-build/raw_render.py)
  HikerAPI        stats_snapshots/snapshot_*.json        platforms.hikerapi.balance (stats/collectors.py, since 2026-11-02)
  Gero key        GERO_LEDGER (does not exist yet)       same Claude credit; point this at the Gero ledger once one is written

Caps: Claude credit $200/month, warn at 70% (Inch of Shadow + Gero together); OpenAI image renders
$15/month; HikerAPI balance under $10. The monthly ledgers hold no per-call dates, so their
last-30-day column reads "months only" instead of a number.
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS = ROOT / "stats_snapshots"
CLAUDE_LEDGER = SNAPSHOTS / "claude_spend.json"
OPENAI_LEDGER = SNAPSHOTS / "openai_spend.json"
IMAGINE_DIR = ROOT / "generated_images" / "imagine"
RAW_RENDER_DIR = ROOT / "generated_images" / "pinocchio-single"
GERO_LEDGER = Path("/Users/amir/Desktop/Gero/CPcode/gero-control-panel/data/claude_spend.json")  # not written yet
OUT_FILE = SNAPSHOTS / "spend_latest.json"

CLAUDE_CREDIT_USD = 200.0
CLAUDE_WARN_PCT = 70
IMAGES_MONTH_USD = 15.0
HIKERAPI_MIN_BALANCE_USD = 10.0
HIKERAPI_USD_PER_REQUEST = 0.001
STALE_DAYS = 3

COLUMNS = ("service", "mtd", "last30", "calls", "biggest", "status")
HEADERS = ("Service", "Month to date", "Last 30 days", "Calls", "Biggest line item", "Status")


# ---------------------------------------------------------------- helpers

def _load(p: Path) -> Optional[dict]:
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return None


def _row(service: str, **kw) -> dict:
    row = {"service": service, "mtd_usd": None, "last30_usd": None, "last30_note": "", "calls": None,
           "biggest": "", "status": "not logged", "source": ""}
    row.update(kw)
    return row


def _usd(v: Optional[float]) -> str:
    return "not logged" if v is None else f"${v:,.2f}"


def _biggest_from_by(by: dict) -> str:
    if not by:
        return ""
    name, item = max(by.items(), key=lambda kv: float((kv[1] or {}).get("usd") or 0))
    return f"{name} ${float(item.get('usd') or 0):.2f} ({int(item.get('calls') or 0)} calls)"


def _monthly_ledger_row(service: str, ledger: Path, now: datetime) -> dict:
    """Claude-shaped ledger: {"months": {"YYYY-MM": {"usd", "calls", "by": {...}}}}."""
    data = _load(ledger)
    if not data or "months" not in data:
        return _row(service, source=str(ledger))
    m = data["months"].get(now.strftime("%Y-%m")) or {}
    return _row(service, mtd_usd=round(float(m.get("usd") or 0), 5), last30_usd=None, last30_note="months only",
                calls=int(m.get("calls") or 0), biggest=_biggest_from_by(m.get("by") or {}), status="ok",
                source=str(ledger))


# ---------------------------------------------------------------- rows

def claude_row(now: datetime, gero_mtd: Optional[float] = None) -> dict:
    row = _monthly_ledger_row("Claude API", CLAUDE_LEDGER, now)
    if row["mtd_usd"] is None:
        return row
    total = row["mtd_usd"] + (gero_mtd or 0)
    pct = 100 * total / CLAUDE_CREDIT_USD
    if pct >= CLAUDE_WARN_PCT:
        row["status"] = f"warn: {pct:.0f}% of ${CLAUDE_CREDIT_USD:.0f} credit (cap {CLAUDE_WARN_PCT}%)"
    return row


def gero_row(now: datetime) -> dict:
    row = _monthly_ledger_row("Gero key", GERO_LEDGER, now)
    if row["mtd_usd"] is None:
        row["biggest"] = "same Claude credit, no ledger yet"
    return row


def openai_text_row(now: datetime) -> dict:
    return _monthly_ledger_row("OpenAI text", OPENAI_LEDGER, now)


def _image_records() -> list:
    if not IMAGINE_DIR.is_dir():
        return []
    out = []
    for f in IMAGINE_DIR.glob("*.json"):
        r = _load(f)
        if isinstance(r, dict) and (IMAGINE_DIR / str(r.get("file") or "")).is_file():
            out.append(r)
    return out


def images_row(now: datetime) -> dict:
    recs = _image_records()
    if not IMAGINE_DIR.is_dir():
        return _row("Image renders", source=str(IMAGINE_DIR))
    ym = now.strftime("%Y-%m")
    since = (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
    month = [r for r in recs if str(r.get("made", "")).startswith(ym)]
    last30 = [r for r in recs if since <= str(r.get("made", "")) <= now.strftime("%Y-%m-%dT%H:%M:%S")]
    mtd = round(sum(float(r.get("cost_usd") or 0) for r in month), 5)
    big = max(month, key=lambda r: float(r.get("cost_usd") or 0), default=None)
    biggest = f"{big.get('model')} {big.get('quality')} ${float(big.get('cost_usd') or 0):.2f}" if big else ""
    status = "ok"
    if mtd >= IMAGES_MONTH_USD:
        status = f"warn: ${mtd:.2f} over the ${IMAGES_MONTH_USD:.0f}/month cap"
    return _row("Image renders", mtd_usd=mtd, last30_usd=round(sum(float(r.get("cost_usd") or 0) for r in last30), 5),
                calls=len(month), biggest=biggest, status=status, source=str(IMAGINE_DIR))


def raw_renders_row(now: datetime) -> dict:
    files = [p for p in RAW_RENDER_DIR.glob("*.png")] if RAW_RENDER_DIR.is_dir() else []
    return _row("Raw renders", calls=len(files), biggest=f"{len(files)} files, no cost record",
                status="not logged", source=str(RAW_RENDER_DIR))


def _parse_stamp(stamp: str) -> Optional[datetime]:
    for fmt in ("%Y-%m-%dT%H-%M-%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(stamp[:19], fmt)
        except ValueError:
            continue
    return None


def _hikerapi_points() -> list:
    """(timestamp, requests) from every snapshot that holds a HikerAPI balance, oldest first."""
    pts = []
    if not SNAPSHOTS.is_dir():
        return pts
    for f in sorted(SNAPSHOTS.glob("snapshot_*.json")):
        d = _load(f)
        if not isinstance(d, dict):
            continue
        h = (d.get("platforms") or {}).get("hikerapi") or {}
        req = h.get("requests", (h.get("balance") or {}).get("requests"))
        if req is None:
            continue
        stamp = str(d.get("timestamp") or f.stem.replace("snapshot_", ""))
        t = _parse_stamp(stamp) or _parse_stamp(f.stem.replace("snapshot_", ""))
        if t is not None:
            pts.append((t, int(req)))
    return sorted(pts)


def hikerapi_row(now: datetime) -> dict:
    pts = _hikerapi_points()
    if not pts:
        return _row("HikerAPI", balance_usd=None, source=str(SNAPSHOTS / "snapshot_*.json platforms.hikerapi"))
    last_t, last_req = pts[-1]
    balance = round(last_req * HIKERAPI_USD_PER_REQUEST, 3)
    drops = []    # (day_of_drop, requests used) between consecutive snapshots; top-ups (increases) are not spend
    for (t0, r0), (t1, r1) in zip(pts, pts[1:]):
        if r1 < r0:
            drops.append((t1, r0 - r1))
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    since30 = now - timedelta(days=30)
    mtd_req = sum(n for t, n in drops if month_start <= t <= now)
    last30_req = sum(n for t, n in drops if since30 <= t <= now)
    big = max((d for d in drops if since30 <= d[0] <= now), key=lambda d: d[1], default=None)
    biggest = f"{big[0].strftime('%m-%d')}: {big[1]} requests" if big else ""
    status = "ok"
    if balance < HIKERAPI_MIN_BALANCE_USD:
        status = f"warn: balance ${balance:.2f} under ${HIKERAPI_MIN_BALANCE_USD:.0f}"
    if (now - last_t).days > STALE_DAYS:
        status += f"{'; ' if status != 'ok' else ''}stale: last balance {last_t.strftime('%Y-%m-%d')}"
        if status.startswith("ok; "):
            status = status[4:]
    return _row("HikerAPI", mtd_usd=round(mtd_req * HIKERAPI_USD_PER_REQUEST, 5),
                last30_usd=round(last30_req * HIKERAPI_USD_PER_REQUEST, 5), calls=last30_req, biggest=biggest,
                status=status, balance_usd=balance, balance_requests=last_req,
                balance_read=last_t.strftime("%Y-%m-%dT%H:%M:%S"), source=str(SNAPSHOTS / "snapshot_*.json"))


# ---------------------------------------------------------------- report

def build(now: Optional[datetime] = None) -> dict:
    now = now or datetime.now()
    gero = gero_row(now)
    rows = [claude_row(now, gero["mtd_usd"]), gero, openai_text_row(now), images_row(now), raw_renders_row(now),
            hikerapi_row(now)]
    warnings = [f"{r['service']}: {r['status']}" for r in rows if r["status"].startswith("warn")]
    return {"made": now.strftime("%Y-%m-%dT%H:%M:%S"), "month": now.strftime("%Y-%m"),
            "caps": {"claude_credit_usd": CLAUDE_CREDIT_USD, "claude_warn_pct": CLAUDE_WARN_PCT,
                     "openai_images_month_usd": IMAGES_MONTH_USD, "hikerapi_min_balance_usd": HIKERAPI_MIN_BALANCE_USD},
            "rows": rows, "warnings": warnings,
            "gaps": [f"{r['service']}: not logged ({r['source']})" for r in rows if r["status"] == "not logged"]}


def _cells(r: dict) -> tuple:
    last30 = r["last30_note"] or _usd(r["last30_usd"])
    status = r["status"]
    if r.get("balance_usd") is not None:
        status = f"balance ${r['balance_usd']:.2f}; {status}"
    return (r["service"], _usd(r["mtd_usd"]), last30, "not logged" if r["calls"] is None else str(r["calls"]),
            r["biggest"] or "none", status)


def render(report: dict) -> str:
    table = [HEADERS] + [_cells(r) for r in report["rows"]]
    widths = [max(len(row[i]) for row in table) for i in range(len(HEADERS))]
    lines = [f"Spend {report['month']} (read {report['made'][:16]})"]
    for n, row in enumerate(table):
        lines.append("  ".join(c.ljust(w) for c, w in zip(row, widths)).rstrip())
        if n == 0:
            lines.append("  ".join("-" * w for w in widths))
    caps = report["caps"]
    lines.append(f"Caps: Claude {caps['claude_warn_pct']}% of ${caps['claude_credit_usd']:.0f}/month "
                 f"(Inch of Shadow + Gero), image renders ${caps['openai_images_month_usd']:.0f}/month, "
                 f"HikerAPI balance under ${caps['hikerapi_min_balance_usd']:.0f}.")
    lines.append("Warnings: " + ("; ".join(report["warnings"]) if report["warnings"] else "none"))
    return "\n".join(lines)


def write_json(report: dict) -> Path:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if OUT_FILE.exists():
        shutil.copy2(OUT_FILE, OUT_FILE.with_suffix(".json.bak"))
    OUT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    return OUT_FILE


def main(argv: list, now: Optional[datetime] = None) -> int:
    report = build(now)
    print(render(report))
    if "--json" in argv:
        print(f"Written: {write_json(report)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
