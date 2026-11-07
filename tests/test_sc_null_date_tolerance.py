"""2026-09-02: sc_engagement --dry-run crashed on 88 legacy IG log entries
whose `date` is null (CC-era merges). `e.get("date", "")` returns None when
the key EXISTS with a null value, so every `>= cutoff` comparison raised
TypeError. All date-window counters must tolerate null dates."""
import scene_intelligence.sc_engagement as sc


def _log():
    return {"log": {
        "a": [{"date": None, "platform": "instagram", "action": "ig_like"}],
        "b": [{"date": "2026-09-01", "platform": "soundcloud", "action": "sc_repost"}],
    }}


def test_week_counts_tolerate_null_dates():
    counts = sc.get_week_action_counts(_log())
    assert counts["sc_repost"] >= 0  # must not raise
