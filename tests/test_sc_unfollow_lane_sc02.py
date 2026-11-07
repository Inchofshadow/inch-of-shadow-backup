"""SC-02 (2026-09-01): in-session unfollow lane (U2) guards.

Three promises, from the SC twin audit + Amir's 09-01 decisions:
1. FAIL CLOSED — a failed follower fetch returns None from
   update_follow_back_status, and None must never read as "no news".
2. keep_following is honored everywhere (sweep + planner). The inbox guard
   stamps keep_following="inbox_thread" for anyone Amir talks to in
   SoundCloud Messages; before SC-02 the sweep ignored the flag entirely.
3. A churned protected account is never cemented into permanently_unfollowed.
"""
import json
from datetime import date, timedelta

import pytest

import scene_intelligence.sc_engagement as sc


@pytest.fixture(autouse=True)
def _no_live_promo_log(monkeypatch):
    """Planner tests must not depend on the real promotion_log.json."""
    monkeypatch.setattr(sc, "_collect_active_promo_targets", lambda: [])
    # dated one-off pull-forwards in the live config must not leak into tests
    monkeypatch.setattr(sc, "UNFOLLOW_EARLY_DAYS", {})


def _entry(name, **kw):
    e = {
        "user_id": kw.pop("user_id", str(abs(hash(name)) % 10**8)),
        "name": name,
        "url": f"https://soundcloud.com/{name}",
        "followers": 100,
        "followed_back": False,
        "unfollow_after": "2020-01-01",  # long expired
    }
    e.update(kw)
    return e


# ---------------------------------------------------------------------------
# 1. fail closed
# ---------------------------------------------------------------------------

def test_followback_check_returns_none_on_fetch_failure(monkeypatch):
    monkeypatch.setattr(sc, "fetch_all_follower_ids", lambda: None)
    tracker = {"follows": [_entry("someone")], "stats": {}}
    assert sc.update_follow_back_status(tracker) is None


def test_followback_check_returns_zero_for_empty_tracker(monkeypatch):
    # No follows -> nothing to verify -> 0, NOT None (no fetch even attempted)
    monkeypatch.setattr(sc, "fetch_all_follower_ids",
                        lambda: (_ for _ in ()).throw(AssertionError("no fetch")))
    assert sc.update_follow_back_status({"follows": []}) == 0


def test_followback_check_counts_new_followbacks(monkeypatch):
    tracker = {"follows": [_entry("a", user_id="1"), _entry("b", user_id="2")],
               "stats": {}}
    monkeypatch.setattr(sc, "fetch_all_follower_ids", lambda: {"2"})
    assert sc.update_follow_back_status(tracker) == 1
    assert tracker["follows"][1]["followed_back"] is True


# ---------------------------------------------------------------------------
# 2. keep_following honored
# ---------------------------------------------------------------------------

def test_sweep_never_touches_keep_following():
    tracker = {"follows": [
        _entry("inbox-friend", keep_following="inbox_thread"),
        _entry("explicit-keep", keep_following=True),
        _entry("normal-expired"),
    ]}
    res = sc.run_unfollow_sweep(tracker, {"log": {}}, dry_run=True)
    kept = {k["name"]: k["reason"] for k in res["kept"]}
    assert kept["inbox-friend"] == "keep_following:inbox_thread"
    assert kept["explicit-keep"] == "keep_following:True"
    assert [u["name"] for u in res["unfollowed"]] == ["normal-expired"]


def test_planner_applies_every_guard():
    tracker = {"follows": [
        _entry("inbox-friend", keep_following="inbox_thread"),
        _entry("reciprocator", followed_back=True),
        _entry("released-on", no_longer_engage=True),
        _entry("drifted", no_longer_following=True),
        _entry("no-id", user_id=""),
        _entry("window-open",
               unfollow_after=(date.today() + timedelta(days=5)).isoformat()),
        _entry("due-oldest", unfollow_after="2026-01-01"),
        _entry("due-newer", unfollow_after="2026-02-01"),
    ]}
    plan = sc.plan_unfollow_batch(tracker, limit=12)
    names = [c["name"] for c in plan["batch"]]
    assert names == ["due-oldest", "due-newer"]  # oldest window first
    assert plan["excluded"]["keep_following:inbox_thread"] == 1
    assert plan["excluded"]["followed_back"] == 1
    assert plan["excluded"]["no_longer_engage"] == 1
    assert plan["excluded"]["no_longer_following"] == 1
    assert plan["excluded"]["missing_user_id"] == 1
    assert plan["excluded"]["window_open"] == 1


def test_planner_holds_active_promo_targets(monkeypatch):
    monkeypatch.setattr(sc, "_collect_active_promo_targets", lambda: [
        {"target": {"name": "Cultivated Electronics",
                    "soundcloud_url": "https://soundcloud.com/cultivated-electronics"}},
    ])
    tracker = {"follows": [
        _entry("Cultivated Electronics", user_id="1"),
        _entry("someone-else", user_id="2"),
    ]}
    plan = sc.plan_unfollow_batch(tracker, limit=12)
    assert [c["name"] for c in plan["batch"]] == ["someone-else"]
    assert plan["excluded"]["active_promo_target"] == 1


def test_planner_limit_and_deferred_count():
    tracker = {"follows": [_entry(f"u{i}", user_id=str(i),
                                  unfollow_after=f"2026-01-{i+1:02d}")
                           for i in range(20)]}
    plan = sc.plan_unfollow_batch(tracker, limit=12)
    assert len(plan["batch"]) == 12
    assert plan["excluded"]["deferred_beyond_batch"] == 8


def test_mark_keep_stamps_entry():
    tracker = {"follows": [_entry("talky", user_id="42")]}
    entry = sc.mark_keep(tracker, "42", "inbox_thread")
    assert entry["keep_following"] == "inbox_thread"
    assert entry["keep_marked_at"] == date.today().isoformat()
    assert sc.mark_keep(tracker, "999", "inbox_thread") is None


# ---------------------------------------------------------------------------
# 3. churn is not cemented
# ---------------------------------------------------------------------------

def test_remove_follow_record_permanent_flag():
    tracker = {"follows": [_entry("mistake", user_id="7")],
               "stats": {}, "permanently_unfollowed": []}
    sc.remove_follow_record("7", tracker, permanent=False)
    # 2026-10-01: marked, not deleted, so follow-back rates stay honest
    assert len(tracker["follows"]) == 1
    assert tracker["follows"][0]["no_longer_following"] is True
    assert tracker["follows"][0]["unfollowed_at"]
    assert tracker["permanently_unfollowed"] == []
    assert tracker["stats"]["total_unfollowed"] == 1

    tracker2 = {"follows": [_entry("normal", user_id="8")],
                "stats": {}, "permanently_unfollowed": []}
    sc.remove_follow_record("8", tracker2)  # default stays permanent
    assert tracker2["permanently_unfollowed"] == ["8"]


# ---------------------------------------------------------------------------
# staleness gate helper
# ---------------------------------------------------------------------------

def test_followback_age_reads_audit_stamp(tmp_path, monkeypatch):
    audit = tmp_path / "sc_following_audit.json"
    monkeypatch.setattr(sc, "AUDIT_FILE", audit)

    assert sc._followback_data_age_days() is None  # missing -> None (stale)

    audit.write_text(json.dumps({"fetched_at": date.today().isoformat()}))
    assert sc._followback_data_age_days() == 0

    old = (date.today() - timedelta(days=9)).isoformat()
    audit.write_text(json.dumps({"fetched_at": old}))
    assert sc._followback_data_age_days() == 9

    audit.write_text("{not json")
    assert sc._followback_data_age_days() is None

    # the OTHER writer's schema (check_sc_follows) has no fetched_at
    audit.write_text(json.dumps({"not_in_si": []}))
    assert sc._followback_data_age_days() is None


def test_manual_follows_are_never_swept_or_planned():
    """zaatar_music lesson (2026-09-03): Amir's own follows are untouchable."""
    tracker = {"follows": [
        _entry("amirs-own", source="manual"),
        _entry("machine-follow", source="discovery_v2"),
    ]}
    plan = sc.plan_unfollow_batch(tracker, limit=12)
    assert [c["name"] for c in plan["batch"]] == ["machine-follow"]
    assert plan["excluded"]["manual_follow_amirs_own"] == 1
    res = sc.run_unfollow_sweep(tracker, {"log": {}}, dry_run=True)
    kept = {k["name"]: k["reason"] for k in res["kept"]}
    assert kept["amirs-own"] == "manual_follow_amirs_own"


def test_refollow_replaces_marked_entry_without_duplicate():
    tracker = {"follows": [], "stats": {}, "permanently_unfollowed": []}
    sc.add_follow_record("9", "x", "u", 100, "discovery_v2", tracker)
    sc.remove_follow_record("9", tracker, permanent=False)
    sc.add_follow_record("9", "x", "u", 100, "discovery_v2", tracker)
    assert len(tracker["follows"]) == 1
    assert not tracker["follows"][0].get("no_longer_following")
