"""What the copy writers (SEO Copy, Bio Manager) know about Inch of Shadow, read from the brand
files at call time so the words can never drift from them: facts from docs/brand/proof.md, voice
from docs/brand/voice.md, and for the songs lane the QUICK PULL of docs/brand/positioning.md.

Two lanes (bridge plan v2): a release with lane "full" is a song; everything else, "light"
included, is the electronic lane, which is the public identity today: a Berlin producer and DJ,
dance music. Pinocchio (2026-11-06) is on that lane.
"""
from __future__ import annotations

import re
from pathlib import Path

BRAND = Path(__file__).resolve().parent.parent / "docs" / "brand"

ELECTRONIC_FACTS = ("Identity", "The sound: the electronic lane", "Labels", "Live", "Collective",
                    "Curation", "Collaborators and past projects", "Signature descriptor")
VOICE = ("Voice in one line", "Two registers", "The song's meaning", "Never")
ELECTRONIC_TAGS = "dark disco, EBM, coldwave, acid, electro, techno"


def section(text: str, heading: str) -> str:
    """The body of '## <heading...>' up to the next '## '."""
    m = re.search(r"^## " + re.escape(heading) + r".*?$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def _read(name: str) -> str:
    p = BRAND / name
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def lane_of(release: dict | None) -> str:
    return "songs" if (release or {}).get("lane") == "full" else "electronic"


def songs_public() -> bool:
    """False while positioning.md still carries its PUBLIC STATUS block (the songs are not out)."""
    return "## PUBLIC STATUS" not in _read("positioning.md")


def facts(lane: str = "electronic") -> str:
    proof = _read("proof.md")
    names = ELECTRONIC_FACTS if lane == "electronic" else ELECTRONIC_FACTS[:1] + ("The sound: the songs",) + ELECTRONIC_FACTS[2:]
    parts = []
    for n in names:
        body = section(proof, n)
        if not body:
            continue
        if lane == "electronic":                      # the songs-era identity is not public: keep it out
            bullets = ["- " + b if i else b for i, b in enumerate(body.split("\n- "))]
            body = "\n".join(b for b in bullets if "bio switch" not in b and "sings" not in b)
        parts.append(f"### {n}\n{body}")
    return "\n\n".join(parts)


def voice() -> str:
    v = _read("voice.md")
    return "\n\n".join(f"### {n}\n{section(v, n)}" for n in VOICE if section(v, n))


def lane_rules(release: dict | None) -> str:
    """The lane paragraph every writer gets first."""
    meta = (release or {}).get("metadata", {})
    genres = " / ".join(g for g in (meta.get("genre_primary"), meta.get("genre_secondary")) if g)
    if lane_of(release) == "electronic":
        return (
            "LANE: ELECTRONIC. Inch of Shadow is presented here as he is publicly today: a Berlin producer "
            "and DJ, a solo electronic act, and this is DANCE MUSIC. "
            + (f"Lead with this release's own genres ({genres}), then the electronic-lane tags that fit it "
               f"(from: {ELECTRONIC_TAGS}). " if genres else f"Use the electronic-lane tags that fit ({ELECTRONIC_TAGS}). ")
            + "'Dark dance wave' is his coined descriptor: use it inside sentences, on top of the real genre "
            "words, never instead of them. Do NOT mention songs, singing, vocals, lyrics, guitars or a new era: "
            "that direction is not public. Name only the venues, labels, collective and collaborators listed in "
            "the brand facts below; no other clubs, festivals or names."
        )
    status = "" if songs_public() else (" NOT PUBLIC YET: the songs are unannounced, so this copy is prepared "
                                         "ahead and must not be published before the bio switch.")
    return ("LANE: SONGS. Use the songs-lane identity and tags from the positioning quick pull below." + status)


def brief(release: dict | None) -> str:
    """Everything a writer needs: the lane, the facts, the voice (and for songs, the quick pull)."""
    lane = lane_of(release)
    parts = [lane_rules(release), "BRAND FACTS (proof.md; never claim anything that is not here):\n" + facts(lane),
             "VOICE (voice.md):\n" + voice()]
    if lane == "songs":
        parts.append("POSITIONING QUICK PULL (positioning.md):\n" + section(_read("positioning.md"), "QUICK PULL"))
    return "\n\n".join(parts)
