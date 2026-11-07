"""One-off test (2026-11-06, Income +500): Perplexity Agent API vs our Claude crowding check.

Reruns the crowding check of one past report through Perplexity (same instructions, same
verdict rules, same URL vetting as crowding.py) and writes a side-by-side comparison.
Nothing in the radar changes. Hard stop when the Perplexity spend reaches --budget.

  python3 gap_radar/perplexity_test.py --dry-run     # show what would be sent, $0
  python3 gap_radar/perplexity_test.py               # run (needs PERPLEXITY_API_KEY in .env)

Docs used (2026-11-06): POST https://api.perplexity.ai/v1/agent, Bearer key, body
{effort|model, instructions, input, tools:[{type:web_search}], max_tool_calls,
max_output_tokens}; reply has output_text, output[] items (type "search_results"),
usage.cost.total_cost.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from crowding import SYSTEM, _gap_prompt, _norm, parse_verdict, vet  # noqa: E402

URL = "https://api.perplexity.ai/v1/agent"
REPORT = HERE / "reports" / "producer-tools" / "2026-11-06T0320.json"
OUT = HERE / "reports" / "perplexity-test"


def api_key() -> str:
    key = os.environ.get("PERPLEXITY_API_KEY")
    if not key:
        env = ROOT / ".env"
        for line in env.read_text().splitlines() if env.exists() else []:
            if line.strip().startswith("PERPLEXITY_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise SystemExit("PERPLEXITY_API_KEY missing in .env")
    return key


def body(g: dict, effort: str) -> dict:
    return {"effort": effort, "instructions": SYSTEM, "input": _gap_prompt(g),
            "tools": [{"type": "web_search"}], "max_tool_calls": 8, "max_output_tokens": 4000}


def urls_in(reply: dict) -> set[str]:
    """Every URL the search step really returned."""
    urls = set()
    for item in reply.get("output") or []:
        if item.get("type") == "search_results":
            for r in item.get("results") or []:
                urls.add(_norm(r.get("url", "")))
    urls.discard("")
    return urls


def check_one(session, key: str, g: dict, effort: str) -> dict:
    r = session.post(URL, json=body(g, effort), timeout=300,
                     headers={"Authorization": f"Bearer {key}"})
    if r.status_code != 200:
        return {"verdict": "unclear", "reason": f"HTTP {r.status_code}: {r.text[:200]}",
                "competitors": [], "pay_proof": [], "cost_usd": 0.0}
    reply = r.json()
    cost = float(((reply.get("usage") or {}).get("cost") or {}).get("total_cost") or 0.0)
    try:
        v = vet(parse_verdict(reply.get("output_text") or ""), urls_in(reply))
    except (ValueError, json.JSONDecodeError) as e:
        v = {"verdict": "unclear", "reason": f"check failed: {e}", "competitors": [], "pay_proof": []}
    v["cost_usd"] = round(cost, 4)
    v["searches"] = ((reply.get("usage") or {}).get("tool_calls_details") or {})
    return v


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--budget", type=float, default=1.0)
    ap.add_argument("--effort", default="fast")
    ap.add_argument("--report", default=str(REPORT))
    a = ap.parse_args()
    gaps = json.loads(Path(a.report).read_text())
    if a.dry_run:
        print(json.dumps(body(gaps[0], a.effort), indent=1)[:1500])
        print(f"\n{len(gaps)} gaps, budget ${a.budget:.2f}")
        return
    import requests
    key, s = api_key(), requests.Session()
    rows, spent = [], 0.0
    for n, g in enumerate(gaps, 1):
        if spent >= a.budget:
            print(f"budget ${a.budget:.2f} reached, stopping before gap {n}")
            break
        v = check_one(s, key, g, a.effort)
        spent += v["cost_usd"]
        old = g.get("crowding") or {}
        rows.append({"name": g.get("name", ""), "claude": old, "perplexity": v})
        print(f"  {n}. {g.get('name', '')[:55]}: claude {old.get('verdict')} "
              f"(${old.get('cost_usd', 0):.2f}) | perplexity {v['verdict']} (${v['cost_usd']:.3f})")
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{Path(a.report).stem}-{a.effort}.json"
    out.write_text(json.dumps({"report": a.report, "effort": a.effort, "spent_usd": round(spent, 4),
                               "rows": rows}, indent=1))
    same = sum(r["claude"].get("verdict") == r["perplexity"]["verdict"] for r in rows)
    print(f"\nsame verdict {same}/{len(rows)}, perplexity spent ${spent:.3f} -> {out}")


if __name__ == "__main__":
    main()
