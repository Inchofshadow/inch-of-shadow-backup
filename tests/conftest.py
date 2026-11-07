"""Shared test setup."""

import pytest


@pytest.fixture(autouse=True)
def _claude_ledger_in_tmp(tmp_path, monkeypatch):
    """No test writes Claude or OpenAI API spend into the real monthly ledgers."""
    from release_manager import claude_api, openai_api
    monkeypatch.setattr(claude_api, "LEDGER", tmp_path / "claude_spend.json")
    monkeypatch.setattr(openai_api, "LEDGER", tmp_path / "openai_spend.json")
