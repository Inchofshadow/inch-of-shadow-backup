"""The video project starter writes the first page itself (Machine-09 rehearsal, 2026-09-21).

`hyperframes init` leaves a 1920x1080 page set in Inter. Almost everything Inch of Shadow
makes is 1080x1920, so every project began on the wrong canvas with an off-brand font.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "docs" / "brand" / "kit" / "scripts"


def load(name):
    import sys
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_first_page_is_on_brand_for_every_canvas():
    starter, tokens = load("start_video_project"), load("frame_tokens")
    css = tokens.css(tokens.load(), "M2")
    assert starter.CANVAS["reel"] == (1080, 1920)
    for canvas, (w, h) in starter.CANVAS.items():
        page = starter.INDEX.format(w=w, h=h, css=css)
        assert f'data-width="{w}" data-height="{h}"' in page
        assert "@font-face" in page and "--ground" in page and "--safe-top" in page
        assert "Inter" not in page and "{w}" not in page and "{{" not in page
        assert 'window.__timelines["main"]' in page and 'data-composition-id="main"' in page
        assert "1920px" not in page.split("</style>")[1]      # the root is sized by data-width, never hardcoded


def test_skill_copy_of_the_starter_is_the_same_file():
    skill = ROOT.parent / ".claude" / "skills" / "brand" / "scripts" / "start_video_project.py"
    if skill.is_file():
        assert skill.read_text() == (SCRIPTS / "start_video_project.py").read_text()
