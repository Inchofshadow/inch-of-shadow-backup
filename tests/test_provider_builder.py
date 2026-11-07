"""Builder in provider mode (2026-09-14): seed followers via the provider,
overlap map built exactly as before, no Instagram session."""
import json
import scene_intelligence.ig_queue_builder as qb


class _FakeProvider:
    def __init__(self):
        self.calls = 0
    def profile(self, username):
        self.calls += 1
        return {"id": {"seedA": "100", "seedB": "200"}[username], "username": username}
    def followers_page(self, uid, max_id=None):
        self.calls += 1
        if uid == "100":
            return ([{"pk": "1", "username": "both", "is_private": False},
                     {"pk": "2", "username": "onlya", "is_private": False}], None)
        return ([{"pk": "1", "username": "both", "is_private": False},
                 {"pk": "3", "username": "priv", "is_private": True}], None)


def test_overlap_map_from_provider(tmp_path, monkeypatch):
    fake = _FakeProvider()
    monkeypatch.setattr(qb, "_PROVIDER", fake)
    monkeypatch.setattr(qb, "_load_seed_ids", lambda: {})
    monkeypatch.setattr(qb, "_save_seed_id", lambda h, u: None)
    overlap = qb.build_overlap_map(None, ["seedA", "seedB"], max_per_seed=50, delay_seconds=0)
    assert overlap["both"]["seed_count"] == 2 and sorted(overlap["both"]["seeds"]) == ["seedA", "seedB"]
    assert overlap["both"]["user_id"] == "1" and overlap["both"]["ig_followers"] == 0  # counts come from the audit
    assert overlap["priv"]["ig_is_private"] is True
    assert fake.calls == 4  # 2 resolves + 2 pages
