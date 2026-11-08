"""Gate review 2026-11-07: an IG handle with no check recorded must show as unverified."""
from release_manager import outreach


def _ig(t):
    return next(l for l in outreach._links(t) if l["label"].startswith("instagram"))


def test_missing_instagram_check_is_unverified():
    assert _ig({"instagram": "@somebar"})["unverified"] is True
    assert _ig({"instagram": "@somebar", "instagram_verified": False})["unverified"] is True
    assert _ig({"instagram": "@somebar", "instagram_verified": True})["unverified"] is False
