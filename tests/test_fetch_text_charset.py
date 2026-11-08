"""Gate review 2026-11-07: UTF-8 pages without a header charset must not turn into mojibake."""
import fetch_text as ft


def test_page_charset_header_then_meta_then_utf8():
    assert ft.page_charset("text/html", b"<html>") == "utf-8"
    assert ft.page_charset("text/html; charset=windows-1252", b"") == "cp1252"
    assert ft.page_charset("text/html", b'<meta charset="iso-8859-1">') == "iso8859-1"
    assert ft.page_charset("text/html; charset=bogus", b"") == "utf-8"
    body = "Café Berghain".encode("utf-8")
    assert body.decode(ft.page_charset("text/html", body)) == "Café Berghain"
