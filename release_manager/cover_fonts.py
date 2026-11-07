"""The font arsenal for the cover ideas on the Shoot photo page: faces that exist on this Mac,
either as files under docs/brand/fonts (free and TRIAL files, for looking only) or as system
fonts. Each face carries the tags the assignment goes by. Nothing here is licensed for public
use unless font-sources.md says so (Marcellus, Jost, Mohave, OCR-B are free)."""
from __future__ import annotations

from pathlib import Path

FONTS_DIR = Path(__file__).resolve().parent.parent / "docs" / "brand" / "fonts"
T = "trials"

# key: label, group (font-library.md), css family, file (glob under docs/brand/fonts) or local
# system name, caps (set the title in capitals), scale (size factor for the 300 px mock), tags
FONTS = {
    "impact":      dict(label="Impact", group="J", local="Impact", caps=True, scale=1.0, tags="noir rock punk loud flash defiant tough dramatic"),
    "futura_xb":   dict(label="Futura Condensed ExtraBold", group="J", local="Futura-CondensedExtraBold", caps=True, scale=1.05, tags="noir rock loud stark flash street edgy"),
    "mohave":      dict(label="Mohave Bold", group="F", file="free/Mohave-700.ttf", caps=True, scale=1.0, tags="rock street flash tough night cool"),
    "din_cond":    dict(label="DIN Condensed Bold", group="F", local="DINCondensed-Bold", caps=True, scale=1.05, tags="snapshot street flash cool alert"),
    "jost":        dict(label="Jost Light", group="F", file="free/Jost-300.ttf", caps=True, scale=0.95, tags="calm distant quiet small formal meadow"),
    "ocrb":        dict(label="OCR-B", group="H", file="free/OCR-B-Regular.otf", caps=True, scale=0.9, tags="snapshot night flash machine caught"),
    "marcellus":   dict(label="Marcellus", group="D", file="Marcellus-Regular.ttf", caps=False, scale=1.0, tags="formal cinematic symmetric monumental classic"),
    "copperplate": dict(label="Copperplate", group="D", local="Copperplate", caps=True, scale=0.9, tags="monumental stone formal untouchable stern"),
    "ogg":         dict(label="Ogg Italic", group="B", file=f"{T}/Sharp Trial Fonts/Ogg/OTF-Mac/Ogg-Italic-Trial.otf", caps=False, scale=1.15, tags="romantic dreamy soft warm intimate gentle"),
    "editorial_i": dict(label="Editorial New Italic", group="C", file=f"{T}/PPEditorialNew-Free for personal use/PPEditorialNew-Italic.otf", caps=False, scale=1.1, tags="elegant editorial luxury soft romantic"),
    "editorial_ub":dict(label="Editorial New Ultrabold", group="C", file=f"{T}/PPEditorialNew-Free for personal use/PPEditorialNew-Ultrabold.otf", caps=False, scale=1.0, tags="confident luxury untouchable dramatic"),
    "migra_xl":    dict(label="Migra Extralight Italic", group="C", file=f"{T}/Migra - Free for Personal Use/MigraItalic-ExtralightItalic.otf", caps=False, scale=1.25, tags="dreamy romantic vulnerable pensive quiet"),
    "reckless":    dict(label="Reckless Italic", group="C", file=f"{T}/Displaay Trial (Reckless)/Reckless/RecklessItalicCollectionVF-TRIAL.ttf", caps=False, scale=1.1, tags="yearning longing romantic cinematic pensive"),
    "apoc":        dict(label="Apoc Revelations Bold", group="C", file=f"{T}/Blaze Type-Trials/apoc-trial/Apoc-Revelations-Trial-Bold.otf", caps=False, scale=1.0, tags="gothic dramatic night mysterious caged trapped"),
    "saol":        dict(label="Saol Display", group="C", file=f"{T}/Schick Toikka Library Trial/Saol Collection Trial/Saol Display Trial/SaolDisplayTrial-Regular.otf", caps=False, scale=1.0, tags="elegant luxury calm classic tall"),
    "noe":         dict(label="Noe Display Bold", group="C", file=f"{T}/Schick Toikka Library Trial/Noe Collection Trial/Noe Display Trial/NoeDisplayTrial-Bold.otf", caps=False, scale=1.0, tags="confident editorial cool dramatic"),
    "lyyra":       dict(label="Lyyra Black", group="C", file=f"{T}/Schick Toikka Library Trial/Lyyra Collection Trial/Lyyra Standard Trial/LyyraStandardTrial-Black.otf", caps=False, scale=1.0, tags="luxury seductive confident"),
    "chap":        dict(label="Chap Medium", group="B", file=f"{T}/Schick Toikka Library Trial/Chap Trial/ChapTrial-Medium.otf", caps=False, scale=1.0, tags="playful cheeky warm friendly relaxed"),
    "krana":       dict(label="Krana Fat", group="B", file=f"{T}/Schick Toikka Library Trial/Krana Fat Trial/KranaFatTrial-A.otf", caps=False, scale=1.0, tags="playful cheeky mischievous rock"),
    "sectra":      dict(label="GT Sectra Display Bold", group="C", file=f"{T}/Grilli-Type-Trial-Fonts-2026-04/Desktop/GT-Sectra/GT-Sectra-Display-Bold-Trial.otf", caps=False, scale=1.0, tags="brooding stern intense sharp"),
    "alpina_c":    dict(label="GT Alpina Condensed Bold", group="A", file=f"{T}/Grilli-Type-Trial-Fonts-2026-04/Desktop/GT-Alpina/GT-Alpina-Condensed-Bold-Trial.otf", caps=True, scale=1.05, tags="tall narrow cinematic distant lonely"),
    "matthews":    dict(label="LHF Matthews Thin", group="A", file=f"{T}/Letterheadfonts - Letterhead Fonts Foundry Bundle/LHF Matthews Thin™/LHF Matthews Thin.otf", caps=True, scale=1.2, tags="tall deco elegant untouchable monumental"),
    "gloria":      dict(label="LHF Gloria", group="B", file=f"{T}/Letterheadfonts - Letterhead Fonts Foundry Bundle/LHF Gloria™/LHF Gloria.ttf", caps=False, scale=1.25, tags="warm vintage sunny cheeky playful"),
    "conclave":    dict(label="LHF Conclave Sharp", group="E", file=f"{T}/Letterheadfonts - Letterhead Fonts Foundry Bundle/LHF Conclave™/LHF Conclave Sharp.otf", caps=False, scale=1.3, tags="gothic corpse night mysterious hidden dark"),
    "stanford":    dict(label="LHF Stanford Script", group="G", file=f"{T}/Letterheadfonts - Letterhead Fonts Foundry Bundle/LHF Stanford Script™/LHF Stanford Script.otf", caps=False, scale=1.45, tags="romantic soft seductive open"),
    "henderson":   dict(label="LHF Henderson", group="H", file=f"{T}/Letterheadfonts - Letterhead Fonts Foundry Bundle/LHF Henderson/LHF Henderson.otf", caps=True, scale=0.95, tags="vintage sepia classic carved"),
    "didot":       dict(label="Didot", group="C", local="Didot", caps=False, scale=1.05, tags="luxury elegant fashion untouchable"),
    "bodoni":      dict(label="Bodoni 72 Bold", group="C", local="BodoniSvtyTwoITCTT-Bold", caps=False, scale=1.0, tags="dramatic intense classic reaching"),
    "baskerville": dict(label="Baskerville Italic", group="H", local="Baskerville-Italic", caps=False, scale=1.15, tags="quiet pensive classic lonely vintage"),
    "typewriter":  dict(label="American Typewriter", group="H", local="AmericanTypewriter", caps=False, scale=0.95, tags="vintage candid snapshot lost"),
    "avenir_c":    dict(label="Avenir Next Condensed Heavy", group="F", local="AvenirNextCondensed-Heavy", caps=True, scale=1.0, tags="cool aloof composed posed"),
    "optima":      dict(label="Optima", group="F", local="Optima-Regular", caps=True, scale=0.95, tags="calm soft quiet distant eerie"),
    "herculanum":  dict(label="Herculanum", group="E", local="Herculanum", caps=True, scale=1.1, tags="carved stone weathered ancient"),
    "snell":       dict(label="Snell Roundhand", group="G", local="SnellRoundhand-Bold", caps=False, scale=1.4, tags="romantic swash intimate"),
}


def font_path(key: str) -> Path | None:
    f = FONTS.get(key, {}).get("file")
    if not f:
        return None
    p = FONTS_DIR / f
    return p if p.is_file() else None


def css_family(key: str) -> str:
    return f"cover-{key}"
