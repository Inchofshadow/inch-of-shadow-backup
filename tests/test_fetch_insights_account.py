"""T-007: the insights pull adds one guarded account-counts call
(followers/follows) so the monthly ratio KPI stops depending on manual reads."""
import scene_intelligence.ig_fetch_insights as fi


def test_account_counts_attached(monkeypatch):
    def fake_get(path, params, token):
        if path == "me/media":
            return 200, {"data": [{"id": "1", "media_product_type": "FEED"}]}
        if path == "me":
            return 200, {"followers_count": 925, "follows_count": 921,
                         "media_count": 82}
        return 200, {"data": [{"name": "reach", "values": [{"value": 5}]}]}
    monkeypatch.setattr(fi, "_get", fake_get)
    result, calls = fi.fetch("tok", 12)
    assert result["account"]["followers_count"] == 925
    assert result["account"]["follows_count"] == 921
    assert calls == 3  # media list + account + 1 insights


def test_account_counts_failure_degrades_gracefully(monkeypatch):
    def fake_get(path, params, token):
        if path == "me/media":
            return 200, {"data": []}
        if path == "me":
            return 400, {"error": {"message": "nope"}}
        return 200, {}
    monkeypatch.setattr(fi, "_get", fake_get)
    result, calls = fi.fetch("tok", 12)
    assert "account" not in result
    assert result["media_count"] == 0


def test_dry_run_reports_extra_call(monkeypatch, capsys):
    monkeypatch.setattr(fi, "_get", lambda p, q, t: (200, {"data": [{}, {}]}))
    result, calls = fi.fetch("tok", 12, dry_run=True)
    assert result is None
    assert "1 + 2 + 1 (account counts) = 4" in capsys.readouterr().out
