### Task 4: Daily Instagram sample and HikerAPI balance in the sync

**Files:**
- Modify: `stats/collectors.py:460-470` (token constants) and `:667-690` (`collect_all`)
- Modify: `stats/daily_sync.py` (docstring only: the scheduled run no longer skips Instagram)
- Modify: `plans/control-panel/launchd-stats-sync.plist.draft` (drop `--skip instagram`); the live plist `~/Library/LaunchAgents/com.inchofshadow.stats-sync.plist` is Amir's file: change it only after his go, then `launchctl unload` + `load`.
- Test: `tests/test_collect_instagram_daily.py`

**Interfaces:**
- Produces: `IG_DAILY_SOURCE = os.getenv("IG_DAILY_SOURCE", "graph")` ("graph" or "hikerapi", set in `.env` once the probe decides); `collect_instagram_daily() -> dict | None` returning `{"followers": int, "following": int, "media_count": int, "reach_30d": int | None, "source": "graph" | "hikerapi"}`; `collect_hikerapi_balance() -> dict | None` returning `{"requests": int | None, "balance": <raw>}`; `collect_all` runs `("instagram", collect_instagram_daily)` in place of `collect_instagram` and adds `("hikerapi", collect_hikerapi_balance)`.
- Graph variant: one ledger claim `check_and_claim(script="stats_daily_sync", kind="api", est_calls=2, endpoint="graph_insights")`, then `GET https://graph.instagram.com/v21.0/me?fields=id,username,media_count,followers_count,follows_count` and `GET .../me/insights?metric=reach&period=days_28&metric_type=total_value` (reach_30d = that total; `None` if the insights call fails). Falls back to the HikerAPI variant if the Graph profile call is not 200.
- HikerAPI variant: `check_and_claim(script="stats_daily_sync", kind="provider", est_calls=1, endpoint="user_by_username")`, then `Provider().profile("inch_of_shadow")` normalised with `normalise_profile`; `reach_30d` is `None` (the manual entry covers it).
- `LedgerRefused` (a `SystemExit`) is caught in both variants and returns `None`. Any other exception also returns `None` (`collect_all` already records the platform in `errors`).
- `collect_instagram()` stays in the file untouched (other callers), it is just no longer in `collect_all`.

- [ ] **Step 1: Write the failing tests**

```python
import stats.collectors as c

class R:  # minimal requests.Response stand-in
    def __init__(self, code, data): self.status_code, self._d = code, data
    def json(self): return self._d

def test_graph_variant_reads_profile_and_reach(monkeypatch):
    monkeypatch.setattr(c, "IG_DAILY_SOURCE", "graph"); monkeypatch.setattr(c, "META_IG_ACCESS_TOKEN", "t")
    monkeypatch.setattr(c, "_claim", lambda **kw: None)
    calls = []
    def fake_get(url, params=None, timeout=None):
        calls.append(url)
        if url.endswith("/me"): return R(200, {"followers_count": 951, "follows_count": 970, "media_count": 85})
        return R(200, {"data": [{"name": "reach", "total_value": {"value": 2310}}]})
    monkeypatch.setattr(c.requests, "get", fake_get)
    assert c.collect_instagram_daily() == {"followers": 951, "following": 970, "media_count": 85, "reach_30d": 2310, "source": "graph"}
    assert len(calls) == 2

def test_ledger_refusal_returns_none_and_sync_keeps_other_platforms(monkeypatch):
    from scene_intelligence.ig_daily_ledger import LedgerRefused
    def refuse(**kw): raise LedgerRefused(4)
    monkeypatch.setattr(c, "_claim", refuse)
    assert c.collect_instagram_daily() is None
    monkeypatch.setattr(c, "collect_spotify", lambda: {"ok": 1}); monkeypatch.setattr(c, "collect_soundcloud", lambda: None)
    monkeypatch.setattr(c, "collect_youtube", lambda: None); monkeypatch.setattr(c, "collect_hikerapi_balance", lambda: {"requests": 83000})
    out = c.collect_all()
    assert out["platforms"]["spotify"] == {"ok": 1} and "instagram" in out["errors"] and out["platforms"]["hikerapi"]["requests"] == 83000

def test_hikerapi_variant(monkeypatch):
    monkeypatch.setattr(c, "IG_DAILY_SOURCE", "hikerapi"); monkeypatch.setattr(c, "_claim", lambda **kw: None)
    class P:
        def profile(self, u): return {"username": u, "follower_count": 952, "following_count": 971, "media_count": 85}
    monkeypatch.setattr(c, "_provider", lambda: P())
    out = c.collect_instagram_daily()
    assert out["followers"] == 952 and out["reach_30d"] is None and out["source"] == "hikerapi"
```

`_claim(**kw)` is a one-line wrapper around `check_and_claim` and `_provider()` returns `Provider()`, both module-level so tests can patch them. Check `normalise_profile` in `ig_data_provider.py` for the real key names and use them in the fake.

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest tests/test_collect_instagram_daily.py -q`
Expected: FAIL, `collect_instagram_daily` missing

- [ ] **Step 3: Implement in `stats/collectors.py`**

Imports of the ledger and provider are inside the functions (they live in `scene_intelligence/`, which the sync must not import at module load if it is missing). `collect_hikerapi_balance` calls `Provider().balance()` and returns `{"requests": bal.get("requests"), "balance": bal}`; no ledger claim (it is not an Instagram read; the dispatcher makes the same call).

- [ ] **Step 4: Run the tests and the whole stats suite**

Run: `python3 -m pytest tests/test_collect_instagram_daily.py tests/test_stats_page.py tests/test_weekly_summary.py -q`
Expected: all passed

- [ ] **Step 5: Update the docstring and the plist draft, commit**

In `daily_sync.py` replace the `--skip instagram` usage line with "`--skip instagram` is no longer the scheduled default (score board, 2026-11)". In the plist draft remove the two `<string>` lines `--skip` and `instagram`.

```bash
git add stats/collectors.py stats/daily_sync.py plans/control-panel/launchd-stats-sync.plist.draft tests/test_collect_instagram_daily.py
git commit -m "feat(stats): daily Instagram sample (Graph or HikerAPI, ledger-claimed) and HikerAPI balance in the sync"
```

- [ ] **Step 6: Live plist (after Amir's go, in the 09:00-21:00 window)**

Edit `~/Library/LaunchAgents/com.inchofshadow.stats-sync.plist` the same way, then:
Run: `launchctl unload ~/Library/LaunchAgents/com.inchofshadow.stats-sync.plist && launchctl load ~/Library/LaunchAgents/com.inchofshadow.stats-sync.plist && launchctl list | grep stats-sync`
Expected: one line with the label and exit status 0 or "-".

---

