# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for vocab.term_texts() (UUID -> word lookup for the report).

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import paths  # noqa: E402
import vocab  # noqa: E402


def _entry(uuid_a, text_a, uuid_b, text_b):
    return {"UUID_A": uuid_a, "Sprache_A": text_a, "UUID_B": uuid_b, "Sprache_B": text_b, "Datum": "2026-10-11"}


def test_term_texts_covers_both_columns_of_all_lists(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    vocab.save_entries("englisch", [_entry("a1", "Haus", "b1", "house")])
    vocab.save_entries("spanisch", [_entry("a2", "Tisch", "b2", "mesa")])
    assert vocab.term_texts() == {
        "a1": ("Haus", "A"),
        "b1": ("house", "B"),
        "a2": ("Tisch", "A"),
        "b2": ("mesa", "B"),
    }


def test_term_texts_without_any_list_is_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    assert vocab.term_texts() == {}


def test_term_in_several_rows_keeps_one_text(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    vocab.save_entries(
        "englisch",
        [_entry("a1", "Schloss", "b1", "castle"), _entry("a1", "Schloss", "b2", "lock")],
    )
    texts = vocab.term_texts()
    assert texts["a1"] == ("Schloss", "A")
    assert texts["b1"] == ("castle", "B") and texts["b2"] == ("lock", "B")
