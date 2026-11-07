import scene_intelligence.ig_fetch_insights as fi


def test_metrics_for_type_reels_includes_views():
    m = fi.metrics_for_type("REELS")
    assert "views" in m and "reach" in m and "saved" in m


def test_metrics_for_type_unknown_falls_back_to_feed():
    assert fi.metrics_for_type("SOMETHING_NEW") == fi.METRICS_BY_TYPE["FEED"]


def test_parse_insights_flattens_values():
    payload = {"data": [
        {"name": "reach", "values": [{"value": 502}]},
        {"name": "views", "values": [{"value": 757}]},
    ]}
    assert fi.parse_insights(payload) == {"reach": 502, "views": 757}


def test_parse_insights_handles_empty():
    assert fi.parse_insights({}) == {}
    assert fi.parse_insights({"data": []}) == {}
