"""Growth headline + followable pool count (2026-09-21).

09-21 scored 9/10 at 4/12 follows: the score is execution vs the plan, and
the plan offered 0 because the "16 vetted" were not followable (11 SI
contacts routed to Scene, 7 no bio, 2 over the following caps). These pin
the growth line and that every pool counter uses the engine's real filter.
"""
import json

import scene_intelligence.close_loops as cl
import scene_intelligence.ig_engagement as eng
import scene_intelligence.ig_dispatcher as disp


def test_growth_target_reads_plan_meta(tmp_path, monkeypatch):
    monkeypatch.setattr(cl, "SI_DIR", tmp_path)
    (tmp_path / "session_plan_2026-09-21.json").write_text(
        json.dumps({"_meta": {"follows_target": 12}, "reach_follows": []}))
    assert cl._growth_target("2026-09-21") == 12
    assert cl._growth_target("2026-09-22") is None  # no plan -> no line


def test_followable_excludes_si_contacts_and_no_bio(monkeypatch):
    cfg = eng._import_config()
    good = {"username": "goodone", "status": "pending", "audit_date": "2026-09-17",
            "ig_followers": 900, "ig_following": 800, "ig_posts": 50,
            "ig_bio": "techno producer berlin", "seeds": ["a", "b"], "seed_count": 2}
    si = dict(good, username="sicontact")
    nobio = dict(good, username="nobio", ig_bio="")
    tl = {"queue": [good, si, nobio]}
    monkeypatch.setattr(eng, "load_target_list", lambda c: tl)
    monkeypatch.setattr(eng, "load_enriched_contacts",
                        lambda c: [{"ig_username": "sicontact"}])
    monkeypatch.setattr(eng, "load_blocked_accounts", lambda c: set())
    monkeypatch.setattr(eng, "load_personal_network", lambda c: (set(), set()))
    monkeypatch.setattr(eng, "load_follow_tracker",
                        lambda c: {"active_follows": [], "unfollowed_history": []})
    assert eng.vetted_pool_size(tl) == 3          # the old, inflated count
    assert eng.followable_handles(cfg) == {"goodone"}
    assert eng.followable_pool_size(cfg) == 1


def test_vet_gate_uses_followable_size(monkeypatch):
    cfg = eng._import_config()
    rule = getattr(cfg, "IN_SESSION_VET", {})
    floor = int(rule.get("only_when_pool_below", 30))
    raw_full = {"queue": [{"status": "pending", "audit_date": "x"}] * (floor + 5)}
    unv = [type("E", (), {"handle": "u", "raw": {}})()]
    # raw count says "full" but the followable pool is 0 -> vets still offered
    monkeypatch.setattr(cfg, "IN_SESSION_VET", dict(cfg.IN_SESSION_VET, enabled=True))  # paused live since 2026-09-26
    assert eng.select_vet_candidates(cfg, raw_full, unv, pool_size=0)


def test_dispatcher_uses_followable(monkeypatch):
    monkeypatch.setattr(eng, "followable_pool_size", lambda cfg=None: 7)
    assert disp.vetted_pool_depth() == 7


def test_jitter_never_revives_a_paused_lane():
    """2026-09-26: follows paused at 0 must stay 0 through session jitter."""
    cfg = eng._import_config()
    for _ in range(50):
        out = eng.apply_session_jitter(cfg, {"follows_per_session": 0, "likes_per_session": 6})
        assert out["follows_per_session"] == 0
        assert out["likes_per_session"] >= 0


def test_wrong_account_skip_reasons():
    import scene_intelligence.ig_merge_session_log as m
    for r in ("handle_mismatch_profile_not_music", "handle_mismatch_not_music_profile",
              "wrong_entity_handle_mismatch"):
        assert m._is_wrong_account_skip(r), r
    for r in ("all_recent_sponsored_or_already_liked", "no_post_within_90d",
              "private_account", "", None):
        assert not m._is_wrong_account_skip(r), r
