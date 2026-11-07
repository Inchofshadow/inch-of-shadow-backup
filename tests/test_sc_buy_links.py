"""sc_buy_links.py (BC-02): title and tracklist mapping to Bandcamp, change-list split. Local only."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scene_intelligence"))

import sc_buy_links as sbl  # noqa: E402

BC = "https://inchofshadow.bandcamp.com"


def item(title, purchase_url="", description="", kind="track"):
    return {"kind": kind, "id": 1, "title": title, "permalink_url": "", "sharing": "public",
            "purchase_url": purchase_url, "purchase_title": "", "downloadable": False,
            "description": description}


def test_title_mapping():
    assert sbl.bandcamp_key_for("Inch of Shadow & Status Zero – The Cure (Meltscape EP)") == "meltscape"
    assert sbl.bandcamp_key_for("The Tour - Inch of Shadow Remix") == "the-tour-remix"
    assert sbl.bandcamp_key_for("Inch of Shadow - Insomnia DJ Set") == ""


def test_tracklist_needs_own_credit_and_picks_newest():
    desc = "01. The Cure - A Forest\n02. La Groove Machine - The Tour (Inch of Shadow Remix)\n" \
           "03. Inch of Shadow - The Deceiver [Unreleased]"
    key, line = sbl.tracklist_key(desc)
    assert key == "the-deceiver" and "Deceiver" in line
    assert sbl.tracklist_key("01. The Cure - A Forest") == ("", "")


def test_plan_split_and_channels():
    plan = sbl.build_plan([
        item("Inch of Shadow - The Deceiver", BC + "/track/the-deceiver%20%C2%B7"),
        item("Inch of Shadow - Farewell", BC + "/track/farewell?campaign=sc-buy"),
        item("Some DJ Set", description="La Groove Machine - The Tour (Inch of Shadow Remix)"),
        item("Other DJ Set", description="Someone - Something"),
    ])
    assert [r["title"] for r in plan["change"]] == ["Inch of Shadow - The Deceiver", "Some DJ Set"]
    assert plan["change"][0]["new_purchase_url"] == BC + "/track/the-deceiver?campaign=sc-buy"
    assert plan["change"][1]["new_purchase_url"] == BC + "/album/the-tour-remix?campaign=sc-mix"
    assert [r["title"] for r in plan["unchanged"]] == ["Inch of Shadow - Farewell"]
    assert [r["title"] for r in plan["review"]] == ["Other DJ Set"]
