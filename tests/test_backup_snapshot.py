"""plans/cleanup/backup_snapshot.py: secrets never go up, unknown binaries lock (security review 2026-11-08)."""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "plans" / "cleanup"))
import backup_snapshot as b  # noqa: E402


@pytest.mark.parametrize("name,body,cat", [
    ("credentials.json.bak.1", "{}", "NEVER"),
    ("YouTube_Token.json", "{}", "NEVER"),
    ("cfg.json", '{"refresh_token": "1//abcdefghijklmnop"}', "NEVER"),
    ("notes.md", "the refresh_token cookie is named here", "PLAIN"),
])
def test_secrets_by_name_any_case_suffix_and_value(tmp_path, name, body, cat):
    p = tmp_path / name
    p.write_text(body)
    assert b.classify(name, str(p)) == cat


def test_unknown_binary_locks_but_media_and_fonts_stay_plain(tmp_path):
    blob = b"\x00\x01binary"
    for name in ("x.sqlite", "x.ttf"):
        (tmp_path / name).write_bytes(blob)
    assert b.has_people_data(str(tmp_path / "x.sqlite"), ".sqlite") is True
    assert b.has_people_data(str(tmp_path / "x.ttf"), ".ttf") is False


def test_build_refuses_a_key_inside_the_code_folder(tmp_path):
    key = os.path.join(b.ROOT, "pytest.ini")      # any existing file inside ROOT
    with pytest.raises(SystemExit) as e:
        b.build([], str(tmp_path / "dest"), key)
    assert "outside the code folder" in str(e.value)


def test_secret_values_come_from_env_and_token_files_and_block_a_plain_file(tmp_path):
    # Fable gate 2026-11-15: the last guard of a build. Values are made up for the test.
    (tmp_path / ".env").write_text("# c\nANTHROPIC_API_KEY=sk-test-ABCDEFGHIJKLMNOP\nGMAIL_ADDRESS=someone@example.org\n"
                                   "GOOGLE_CREDENTIALS_FILE=credentials.json\nSHORT=abc\n")
    (tmp_path / "youtube_token.json").write_text('{"refresh_token": "1//made-up-refresh-token-value", "expiry": "x"}')
    vals = b.secret_values(str(tmp_path))
    assert b"sk-test-ABCDEFGHIJKLMNOP" in vals and b"1//made-up-refresh-token-value" in vals
    assert b"someone@example.org" not in vals and b"credentials.json" not in vals and b"abc" not in vals
    note = tmp_path / "note.md"
    note.write_text("pasted by mistake: sk-test-ABCDEFGHIJKLMNOP")
    clean = tmp_path / "clean.py"
    clean.write_text("print('the key is read from .env')")
    assert b.leaked_secret(str(note), vals) is True
    assert b.leaked_secret(str(clean), vals) is False
    assert b.leaked_secret(str(note), set()) is False
