"""Fetch Inch of Shadow's own Instagram media + per-post insights via the
Instagram API with Instagram Login (graph.instagram.com).

Read-only. Own account only. Writes scene_intelligence/ig_insights.json for the
ig-expert agent to read. Requires a valid META_IG_ACCESS_TOKEN in .env.

API-call accounting (HARD RULE): the run makes 1 media-list call + 1 insights call
per media (1 + N). Use --dry-run to see the planned count without making insights calls,
and --limit to bound N.
"""
import os
import json
import argparse
import datetime
import urllib.request
import urllib.parse
import urllib.error

from dotenv import load_dotenv

BASE = "https://graph.instagram.com/"
OUT = "scene_intelligence/ig_insights.json"

# Per-post insight metrics differ by media product type. Keep to broadly-supported
# metrics; the API rejects unsupported ones, so we fall back to a minimal set on error.
METRICS_BY_TYPE = {
    "REELS": ["reach", "likes", "comments", "saved", "shares", "views"],
    "FEED": ["reach", "likes", "comments", "saved", "shares"],
    "STORY": ["reach", "replies"],
}
MINIMAL_METRICS = ["reach"]


def metrics_for_type(media_product_type):
    """Return the metric list to request for a given media_product_type."""
    return METRICS_BY_TYPE.get(media_product_type, METRICS_BY_TYPE["FEED"])


def parse_insights(payload):
    """Flatten a /{media}/insights response into {metric_name: value}."""
    out = {}
    for row in payload.get("data", []) if isinstance(payload, dict) else []:
        values = row.get("values") or [{}]
        out[row.get("name")] = values[0].get("value")
    return out


def _get(path, params, token):
    params = dict(params)
    params["access_token"] = token
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def fetch_account_counts(token):
    """T-007 (2026-08-31): one extra call for followers/following counts —
    the monthly KPI ratio was stuck on manual reads (last live count 08-16).
    Guarded: any failure returns None and the media pull proceeds unharmed."""
    try:
        status, resp = _get(
            "me", {"fields": "followers_count,follows_count,media_count"}, token)
        if status == 200 and isinstance(resp, dict):
            return {"followers_count": resp.get("followers_count"),
                    "follows_count": resp.get("follows_count"),
                    "media_count": resp.get("media_count")}
    except Exception:
        pass
    return None


def fetch(token, limit, dry_run=False):
    calls = 0
    status, media_resp = _get(
        "me/media",
        {"fields": "id,caption,media_type,media_product_type,timestamp,permalink", "limit": str(limit)},
        token,
    )
    calls += 1
    if status != 200:
        err = media_resp.get("error", {}) if isinstance(media_resp, dict) else {}
        if err.get("code") == 190:
            raise SystemExit("Token expired/invalid (code 190). Re-auth via the Meta dashboard "
                             "(API setup with Instagram login -> Generate token) and update META_IG_ACCESS_TOKEN in .env.")
        raise SystemExit(f"media list failed (HTTP {status}): {json.dumps(media_resp)[:300]}")

    media = media_resp.get("data", [])
    if dry_run:
        print(f"DRY RUN: would make 1 + {len(media)} + 1 (account counts) = "
              f"{len(media) + 2} API calls (no insights fetched).")
        return None, calls

    account = fetch_account_counts(token)
    calls += 1

    enriched = []
    for m in media:
        mid = m["id"]
        mtype = m.get("media_product_type")
        s, payload = _get(f"{mid}/insights", {"metric": ",".join(metrics_for_type(mtype))}, token)
        calls += 1
        if s != 200:
            # retry once with the minimal metric set before giving up on this item
            s, payload = _get(f"{mid}/insights", {"metric": ",".join(MINIMAL_METRICS)}, token)
            calls += 1
        m["insights"] = parse_insights(payload) if s == 200 else {"error": payload.get("error", {}).get("message", "n/a")}
        if m.get("caption"):
            m["caption"] = m["caption"][:200]
        enriched.append(m)

    result = {
        "fetched_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "media_count": len(enriched),
        "media": enriched,
    }
    if account:
        result["account"] = account  # followers_count / follows_count / media_count
    return result, calls


def main():
    ap = argparse.ArgumentParser(description="Fetch own IG media + per-post insights")
    ap.add_argument("--limit", type=int, default=12, help="Max media to fetch (default 12)")
    ap.add_argument("--dry-run", action="store_true", help="Show planned API-call count, fetch nothing")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    load_dotenv(override=True)
    token = os.getenv("META_IG_ACCESS_TOKEN")
    if not token:
        raise SystemExit("META_IG_ACCESS_TOKEN not set in .env")

    result, calls = fetch(token, args.limit, dry_run=args.dry_run)
    if result is None:
        return
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Made {calls} API calls. Wrote {args.out}: {result['media_count']} media with insights.")


if __name__ == "__main__":
    main()
