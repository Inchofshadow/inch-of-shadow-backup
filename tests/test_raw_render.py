"""artwork/edits/half-the-night-build/raw_render.py: the --size option (System 96, 2026-11-10). No API call."""
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "artwork" / "edits" / "half-the-night-build" / "raw_render.py"


def _load():
    spec = importlib.util.spec_from_file_location("raw_render", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # the script only runs under __main__
    return mod


@pytest.mark.parametrize("value,size", [
    (None, "1024x1024"), ("square", "1024x1024"), ("Portrait", "1024x1536"),
    ("landscape", "1536x1024"), ("1536x1024", "1536x1024"),
])
def test_known_sizes(value, size):
    assert _load().parse_size(value) == size


@pytest.mark.parametrize("value", ["4000x4000", "2048x2048", "huge", "1024x1792"])
def test_unknown_sizes_are_refused_before_any_call(value):
    with pytest.raises(ValueError):
        _load().parse_size(value)


def test_bad_size_stops_before_the_client(monkeypatch):
    mod = _load()
    monkeypatch.setattr(mod.ig, "get_client", lambda: (_ for _ in ()).throw(AssertionError("no call")))
    assert mod.main(["raw_render.py", "a moon", "--size", "4000x4000"]) == 2
    assert mod.main(["raw_render.py"]) == 2
