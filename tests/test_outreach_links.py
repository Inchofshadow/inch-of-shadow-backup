"""Gate review 2026-11-07: an IG handle with no check recorded must show as unverified."""
from release_manager import outreach


def _ig(t):
    return next(l for l in outreach._links(t) if l["label"].startswith("instagram"))


def test_missing_instagram_check_is_unverified():
    assert _ig({"instagram": "@somebar"})["unverified"] is True
    assert _ig({"instagram": "@somebar", "instagram_verified": False})["unverified"] is True
    assert _ig({"instagram": "@somebar", "instagram_verified": True})["unverified"] is False


def test_outreach_css_keeps_the_13px_floor():
    """RM check 2026-11-08: 15 outreach styles were 10 to 12.5 px; the app floor is --text-xs (13 px)."""
    import re
    from pathlib import Path
    css = (Path(__file__).resolve().parent.parent / "release_manager" / "static" / "style.css").read_text(encoding="utf-8")
    small = [l for l in css.splitlines() if l.startswith(".outreach-page")
             and re.search(r"font-size:\s*(\d+(?:\.\d+)?)px", l)
             and float(re.search(r"font-size:\s*(\d+(?:\.\d+)?)px", l).group(1)) < 13]
    assert small == [], small
