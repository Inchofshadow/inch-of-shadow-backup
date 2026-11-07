"""Audit in provider mode (2026-09-14): a queue entry gets the same fields the
direct-API audit wrote, with zero Instagram contact."""
import json, time
import scene_intelligence.ig_audit_queue_freshness as audit


class _FakeProvider:
    def __init__(self, profiles, newest):
        self.profiles, self.newest, self.calls = profiles, newest, 0
    def profile(self, username):
        self.calls += 1; return self.profiles.get(username)
    def newest_post_epoch(self, user_id, amount=3):
        self.calls += 1; return self.newest.get(str(user_id))


def test_provider_audit_vets_fresh_and_marks_stale(tmp_path, monkeypatch):
    q = tmp_path / "ig_target_list.json"
    q.write_text(json.dumps({"_meta": {}, "queue": [
        {"username": "fresh1", "status": "pending", "seed_count": 2},
        {"username": "old1", "status": "pending", "seed_count": 1},
        {"username": "gone1", "status": "pending"}]}))
    monkeypatch.setattr(audit, "QUEUE_FILE", q)
    now = int(time.time())
    prof = {"fresh1": {"id": "11", "username": "fresh1", "full_name": "F", "biography": "italo producer berlin",
                       "category_name": "Musician", "is_private": False, "is_verified": False,
                       "follower_count": 800, "following_count": 600, "media_count": 40,
                       "external_url": "", "city_name": ""},
            "old1": {"id": "22", "username": "old1", "full_name": "O", "biography": "coldwave dj",
                     "category_name": "Musician", "is_private": False, "is_verified": False,
                     "follower_count": 900, "following_count": 500, "media_count": 30,
                     "external_url": "", "city_name": ""}}
    fake = _FakeProvider(prof, {"11": now - 5 * 86400, "22": now - 200 * 86400})
    monkeypatch.setattr(audit, "_PROVIDER", fake)
    audit.audit(count=3, dry_run=False, max_age=60)
    by = {e["username"]: e for e in json.loads(q.read_text())["queue"]}
    assert by["fresh1"]["status"] == "pending" and by["fresh1"]["audit_date"]
    assert by["fresh1"]["ig_followers"] == 800 and by["fresh1"]["ig_bio"] == "italo producer berlin"
    assert by["fresh1"]["ig_last_post_age_days"] == 5
    assert by["old1"]["status"] == "skipped_stale" and by["old1"]["skipped_reason"].startswith("last_post_too_old")
    assert by["gone1"].get("fetch_fail_count") == 1
    assert fake.calls == 5  # 3 profiles + 2 feeds (none for the missing one); no Instagram session anywhere
