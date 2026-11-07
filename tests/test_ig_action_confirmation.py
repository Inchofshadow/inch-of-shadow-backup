"""Follows/unfollows must be confirmed by IG's response before recording
(audit P1-5, findings 4/5).

_friendship_confirmed is the single gate: friendships/create and
friendships/destroy answer {"status": "ok", "friendship_status": {...}};
only a confirming response returns True, and the engine records nothing
on False. Mirrors the already-fixed likes path.
"""
import scene_intelligence.ig_live_driver as ld


class _Resp:
    def __init__(self, status_code=200, payload=None, bad_json=False):
        self.status_code = status_code
        self._payload = payload
        self._bad_json = bad_json

    def json(self):
        if self._bad_json:
            raise ValueError("not json")
        return self._payload


_confirm = ld.RequestsBrowserDriver._friendship_confirmed


def test_follow_confirmed_by_following_true():
    r = _Resp(payload={"status": "ok",
                       "friendship_status": {"following": True}})
    assert _confirm(r, want_following=True) is True


def test_follow_confirmed_by_outgoing_request_private_account():
    r = _Resp(payload={"status": "ok",
                       "friendship_status": {"following": False,
                                             "outgoing_request": True}})
    assert _confirm(r, want_following=True) is True


def test_follow_denied_when_following_false():
    # 200 + status ok but IG did NOT register the follow
    r = _Resp(payload={"status": "ok",
                       "friendship_status": {"following": False}})
    assert _confirm(r, want_following=True) is False


def test_unfollow_confirmed_when_following_false():
    r = _Resp(payload={"status": "ok",
                       "friendship_status": {"following": False}})
    assert _confirm(r, want_following=False) is True


def test_unfollow_denied_when_still_following():
    r = _Resp(payload={"status": "ok",
                       "friendship_status": {"following": True}})
    assert _confirm(r, want_following=False) is False


def test_status_fail_denied():
    r = _Resp(payload={"status": "fail", "message": "feedback_required"})
    assert _confirm(r, want_following=True) is False


def test_none_response_denied():
    assert _confirm(None, want_following=True) is False


def test_http_error_denied():
    r = _Resp(status_code=429, payload={"status": "ok"})
    assert _confirm(r, want_following=True) is False


def test_missing_friendship_status_with_ok_is_lenient():
    # mirrors like_post: status ok without detail still counts
    r = _Resp(payload={"status": "ok"})
    assert _confirm(r, want_following=True) is True
    assert _confirm(r, want_following=False) is True


def test_unparseable_json_on_200_is_lenient():
    r = _Resp(bad_json=True)
    assert _confirm(r, want_following=True) is True


def test_stub_driver_returns_true_for_planning():
    import scene_intelligence.ig_engagement as eng
    d = eng.StubBrowserDriver(verbose=False)
    d.navigate_to_profile("x")
    assert d.follow_current_profile() is True
    assert d.unfollow_current_profile() is True
