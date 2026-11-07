"""Gap Radar crowding check (GR-02, 2026-11-05).

One Claude call per gap with Anthropic's server-side web search on. Claude looks for
products that already solve the gap, what they cost, and proof that people pay. Verdict:
open / crowded / unclear, plus competitors (name, price, URL), pay proof with sources and
a one-line reason.

Never invent: every URL Claude gives is checked against the URLs the search tool really
returned in that call. A URL that never came back from a search is kept but marked
unverified. An "open" verdict with no verified pay proof is lowered to "unclear".

  from crowding import check
  gaps = check(gaps)          # each gap gets a "crowding" dict; cost in the ledger
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "release_manager"))

SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search", "max_uses": 8}
MAX_CONTINUES = 3                    # pause_turn resumes per gap (each one a ledger entry)
VERDICTS = ("open", "crowded", "unclear")

SYSTEM = """You check whether a product gap is already crowded. The team is two people
(a musician-producer who builds software with Claude Code) looking for a small self-serve
product they own. Use web search. Find:
1. Existing products that already solve this exact need: name, current price, URL.
2. Proof that people pay for a solution to this need (paid apps, pricing pages, reviews
   that mention price, revenue posts), each with its source URL.

Verdict rules:
- crowded: three or more established, decently reviewed products already do this well at
  a price the buyers accept, or one dominant free option.
- open: few or weak competitors, or the incumbents clearly fail the pain described, AND
  there is sourced proof that people pay.
- unclear: you could not confirm either way.

Never invent names, prices, numbers or URLs. Only give URLs you saw in search results. If
a price or claim is not on a page you saw, write it and set verified to false. If you
cannot find a price, write "unknown".

End your answer with ONE JSON object in a ```json fenced block, nothing after it:
{"verdict": "open|crowded|unclear",
 "reason": "one line",
 "competitors": [{"name": "", "price": "", "url": "", "verified": true}],
 "pay_proof": [{"claim": "", "url": "", "verified": true}]}"""


def _gap_prompt(g: dict) -> str:
    return (f"Gap: {g.get('name', '')}\n"
            f"Pain: {g.get('pain', '')}\n"
            f"Who pays: {g.get('who_pays', '')}\n"
            f"Pay signal from forum posts: {g.get('pay_signal', '')}\n"
            f"Product idea: {g.get('product_idea', '')}\n"
            f"First-guess competitors (unchecked): {g.get('known_competitors', '')}\n\n"
            "Run the crowding check.")


def _norm(url: str) -> str:
    return (url or "").strip().rstrip("/").split("#")[0].lower().replace("://www.", "://")


def seen_urls(content) -> set[str]:
    """Every URL the web search tool returned, plus every URL cited in text blocks."""
    urls = set()
    for b in content:
        t = getattr(b, "type", "")
        if t == "web_search_tool_result" and isinstance(getattr(b, "content", None), list):
            urls |= {_norm(getattr(r, "url", "")) for r in b.content}
        elif t == "text":
            urls |= {_norm(getattr(c, "url", "")) for c in (getattr(b, "citations", None) or [])}
    urls.discard("")
    return urls


def parse_verdict(text: str) -> dict:
    """The last ```json block (or the last {...} object) in the reply."""
    blocks = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if blocks:
        return json.loads(blocks[-1])
    start = text.rfind('{"verdict"')
    if start < 0:
        raise ValueError("no verdict JSON in the reply")
    return json.JSONDecoder().raw_decode(text[start:])[0]


def vet(v: dict, urls: set[str]) -> dict:
    """Clean the verdict and mark every URL the search did not really return as unverified."""
    out = {"verdict": v.get("verdict") if v.get("verdict") in VERDICTS else "unclear",
           "reason": str(v.get("reason") or "").strip(), "competitors": [], "pay_proof": []}
    for c in v.get("competitors") or []:
        url = str(c.get("url") or "")
        ok = bool(c.get("verified")) and _norm(url) in urls
        out["competitors"].append({"name": str(c.get("name") or ""), "price": str(c.get("price") or "unknown"),
                                   "url": url, "verified": ok})
    for p in v.get("pay_proof") or []:
        url = str(p.get("url") or "")
        ok = bool(p.get("verified")) and _norm(url) in urls
        out["pay_proof"].append({"claim": str(p.get("claim") or ""), "url": url, "verified": ok})
    if out["verdict"] == "open" and not any(p["verified"] for p in out["pay_proof"]):
        out["verdict"] = "unclear"
        out["reason"] = (out["reason"] + " (lowered from open: no verified pay proof)").strip()
    return out


def check_one(client, g: dict) -> dict:
    import claude_api
    messages = [{"role": "user", "content": _gap_prompt(g)}]
    content, cost, searches = [], 0.0, 0
    for _ in range(MAX_CONTINUES + 1):
        msg = claude_api.ask(client, max_tokens=16000, system=SYSTEM, messages=messages,
                             effort="high", tools=[SEARCH_TOOL], what="gap_radar_crowding")
        u = claude_api.usage_of(msg)
        cost += u["cost_usd"]
        searches += u.get("web_searches", 0)
        content += list(msg.content)
        if msg.stop_reason != "pause_turn":
            break
        messages = messages + [{"role": "assistant", "content": msg.content}]
    text = "".join(getattr(b, "text", "") for b in content if getattr(b, "type", "") == "text")
    try:
        verdict = vet(parse_verdict(text), seen_urls(content))
    except (ValueError, json.JSONDecodeError) as e:
        verdict = {"verdict": "unclear", "reason": f"check failed: {e}", "competitors": [], "pay_proof": []}
    verdict.update({"cost_usd": round(cost, 4), "web_searches": searches})
    return verdict


def check(gaps: list[dict], client=None) -> list[dict]:
    """Each gap gets a "crowding" dict (verdict, reason, competitors, pay_proof, cost_usd)."""
    import claude_api
    client = client or claude_api.client()
    out = []
    for n, g in enumerate(gaps, 1):
        try:
            v = check_one(client, g)
        except claude_api.LimitReached:
            raise
        except claude_api.ClaudeError as e:
            v = {"verdict": "unclear", "reason": f"check failed: {e}", "competitors": [], "pay_proof": [],
                 "cost_usd": 0.0, "web_searches": 0}
        print(f"  {n}. {g.get('name', '')[:60]}: {v['verdict']} (${v['cost_usd']:.2f})")
        out.append({**g, "crowding": v})
    return out
