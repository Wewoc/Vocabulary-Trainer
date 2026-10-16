# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for log_scrub.py (requirements 7.2: no clear-text vocabulary in logs).

import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import log_scrub  # noqa: E402
import paths  # noqa: E402
import vocab  # noqa: E402


@pytest.fixture
def instance(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    vocab.save_entries(
        "englisch",
        [
            {"UUID_A": "a1", "Sprache_A": "Haus", "UUID_B": "b1", "Sprache_B": "house", "Datum": "2026-01-01"},
            {"UUID_A": "a2", "Sprache_A": "ab", "UUID_B": "b2", "Sprache_B": "up", "Datum": "2026-01-01"},
        ],
    )
    return tmp_path


def test_term_is_replaced_both_columns(instance):
    assert log_scrub.scrub("lookup Haus -> house failed") == "lookup <term> -> <term> failed"


def test_case_insensitive(instance):
    assert log_scrub.scrub("HAUS and House") == "<term> and <term>"


def test_only_whole_words(instance):
    assert log_scrub.scrub("Hausmeister housekeeping") == "Hausmeister housekeeping"


def test_short_terms_are_left_alone(instance):
    assert log_scrub.scrub("ab up") == "ab up"


def test_no_vocab_returns_text_unchanged(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    assert log_scrub.scrub("nothing to hide") == "nothing to hide"


def test_fail_closed_when_vocab_unreadable(instance, monkeypatch):
    def boom(language):
        raise OSError("disk gone")

    monkeypatch.setattr(vocab, "load_entries", boom)
    assert log_scrub.scrub("Haus") == log_scrub.UNAVAILABLE


def _record(msg, args=(), exc_info=None):
    return logging.LogRecord("t", logging.INFO, __file__, 1, msg, args, exc_info)


def test_filter_scrubs_message_and_args(instance):
    record = _record("added %s", ("Haus",))
    assert log_scrub.ScrubFilter().filter(record) is True
    assert record.getMessage() == "added <term>"


def test_filter_scrubs_exception_text(instance):
    try:
        raise KeyError("Haus")
    except KeyError:
        exc_info = sys.exc_info()
    record = _record("failed", exc_info=exc_info)
    log_scrub.ScrubFilter().filter(record)
    assert "Haus" not in record.exc_text
    assert "KeyError" in record.exc_text
    assert record.exc_info is None
