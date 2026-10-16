# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for vocab.search_entries() (list search, v0.0.10.13).

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import vocab  # noqa: E402

ENTRIES = [
    {"UUID_A": "a1", "Sprache_A": "Hallo", "UUID_B": "b1", "Sprache_B": "Hello", "Datum": "2026-10-11"},
    {"UUID_A": "a2", "Sprache_A": "Tschüss", "UUID_B": "b2", "Sprache_B": "Bye", "Datum": "2026-10-11"},
    {"UUID_A": "a3", "Sprache_A": "Danke", "UUID_B": "b3", "Sprache_B": "Thank you", "Datum": "2026-10-11"},
    {"UUID_A": "a4", "Sprache_A": "Haus", "UUID_B": "b4", "Sprache_B": "house", "Datum": "2026-10-11"},
]


def _uuids(result):
    return [e["UUID_A"] for e in result]


def test_empty_query_returns_everything():
    assert _uuids(vocab.search_entries(ENTRIES, "")) == ["a1", "a2", "a3", "a4"]
    assert _uuids(vocab.search_entries(ENTRIES, "   ")) == ["a1", "a2", "a3", "a4"]


def test_matches_either_language_column():
    assert _uuids(vocab.search_entries(ENTRIES, "bye")) == ["a2"]  # English column
    assert _uuids(vocab.search_entries(ENTRIES, "danke")) == ["a3"]  # German column


def test_ignores_case():
    assert _uuids(vocab.search_entries(ENTRIES, "HALLO")) == ["a1"]


def test_ignores_accents():
    assert _uuids(vocab.search_entries(ENTRIES, "tschuss")) == ["a2"]
    assert _uuids(vocab.search_entries(ENTRIES, "TSCHÜSS")) == ["a2"]


def test_substring_not_only_word_start():
    assert _uuids(vocab.search_entries(ENTRIES, "ank")) == ["a3"]  # Danke / Thank you


def test_matches_in_both_columns_of_different_entries_keeps_order():
    assert _uuids(vocab.search_entries(ENTRIES, "ha")) == ["a1", "a3", "a4"]  # Hallo, Thank, Haus


def test_whitespace_is_normalized():
    assert _uuids(vocab.search_entries(ENTRIES, "  thank   you ")) == ["a3"]


def test_no_match_returns_empty_list():
    assert vocab.search_entries(ENTRIES, "xyz") == []


def test_returns_the_original_entries_not_copies():
    result = vocab.search_entries(ENTRIES, "haus")
    assert result[0] is ENTRIES[3]
