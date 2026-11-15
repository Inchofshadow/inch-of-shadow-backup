"""Profile pictures for the picks page (Amir 11-12: "maybe I need to see image").
One pass over our own following list on HikerAPI (~40 calls) gives each account's picture URL; the
pictures themselves come from Instagram's public image CDN (no HikerAPI cost), shrunk to 96 px and
kept in pics/ so the page can embed them. Read-only on Instagram and on engine files.
    python3 plans/ig-sweep-2026-11/get_pics.py
"""
import io, json, sys, time
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
SI = HERE.parents[1] / "scene_intelligence"
sys.path.insert(0, str(SI))
PICS = HERE / "pics"
MAX_CALLS = 45


def main():
    import requests
    from PIL import Image
    import ig_daily_ledger as L, ig_data_provider as P
    want = {r["username"] for r in json.loads((HERE / "candidates.json").read_text())["candidates"]}
    snap = HERE / "picks_snapshot.json"
    if snap.exists():  # Amir 11-12: accounts he already picked need no picture
        want -= set(json.loads(snap.read_text()))
    PICS.mkdir(exist_ok=True)
    missing = {u for u in want if not (PICS / f"{u}.jpg").exists()}
    if not missing:
        print("all pictures present"); return 0
    L.check_and_claim("ig_sweep_pics", kind="provider", est_calls=MAX_CALLS, endpoint="provider_lists")
    p = P.Provider(sleep=0.3)
    me = p.profile("inch_of_shadow")
    urls, page_id = {}, None
    while p.calls < MAX_CALLS and missing - set(urls):
        params = {"user_id": me["id"]}
        if page_id: params["page_id"] = page_id
        data = p._get("/g2/user/following", **params) or {}
        users = (data.get("response") or {}).get("users") or []
        page_id = data.get("next_page_id")
        for u in users:
            name = str(u.get("username") or "").lower()
            if name in missing and u.get("profile_pic_url"):
                urls[name] = u["profile_pic_url"]
        if not page_id or not users: break
    ok = 0
    for name, url in urls.items():
        host = urlparse(url).hostname or ""
        if urlparse(url).scheme != "https" or not (host.endswith(".cdninstagram.com") or host.endswith(".fbcdn.net")):
            continue  # only Instagram's own image CDN
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            img = Image.open(io.BytesIO(r.content)).convert("RGB")
            img.thumbnail((96, 96))
            img.save(PICS / f"{name}.jpg", "JPEG", quality=72)
            ok += 1
        except Exception as exc:  # one bad picture never stops the run
            print("pic failed", name, str(exc)[:60])
        time.sleep(0.2)
    print(f"calls {p.calls}, urls {len(urls)}, pictures saved {ok}, still missing {len(missing) - ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
