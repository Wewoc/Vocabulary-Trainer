# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Offscreen tests for the vocab list search in VocabTablePanel (v0.0.10.13).

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PyQt6.QtWidgets import QApplication, QMessageBox  # noqa: E402

import paths  # noqa: E402
import vocab  # noqa: E402
from gui.panels.vocab_table_panel import VocabTablePanel  # noqa: E402

_PAIRS = [("Hallo", "Hello"), ("Tschüss", "Bye"), ("Danke", "Thank you"), ("Haus", "house")]


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def panel(app, tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    vocab.save_entries(
        "englisch",
        [
            {"UUID_A": f"a{i}", "Sprache_A": a, "UUID_B": f"b{i}", "Sprache_B": b, "Datum": "2026-10-11"}
            for i, (a, b) in enumerate(_PAIRS)
        ],
    )
    return VocabTablePanel("englisch")


def _texts(panel, column=1):
    return [panel._table.item(r, column).text() for r in range(panel._table.rowCount())]


def test_all_rows_and_entry_count_without_search(panel):
    assert panel._table.rowCount() == 4
    assert panel._count_label.text() == "4 entries" or panel._count_label.text() == "4 Einträge"


def test_typing_hides_non_matches_and_shows_counter(panel):
    panel._search_input.setText("ha")
    assert _texts(panel) == ["Hallo", "Danke", "Haus"]
    assert "3" in panel._count_label.text() and "4" in panel._count_label.text()


def test_accent_insensitive_search_in_the_widget(panel):
    panel._search_input.setText("tschuss")
    assert _texts(panel) == ["Tschüss"]


def test_clearing_the_search_shows_everything_again(panel):
    panel._search_input.setText("xyz")
    assert panel._table.rowCount() == 0
    panel._search_input.setText("")
    assert panel._table.rowCount() == 4


def test_search_text_survives_reload(panel):
    panel._search_input.setText("ha")
    panel.reload()
    assert _texts(panel) == ["Hallo", "Danke", "Haus"]


def test_delete_in_filtered_list_removes_the_right_entry(panel, monkeypatch):
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)
    panel._search_input.setText("ha")
    panel._table.selectRow(2)  # "Haus" in the filtered list (3rd row)
    panel._on_delete()
    remaining = [e["Sprache_A"] for e in vocab.load_entries("englisch")]
    assert remaining == ["Hallo", "Tschüss", "Danke"]
    assert panel._search_input.text() == "ha"  # filter kept
    assert _texts(panel) == ["Hallo", "Danke"]


def test_typing_does_not_reread_the_file(panel, monkeypatch):
    calls = []
    original = vocab.load_entries
    monkeypatch.setattr(vocab, "load_entries", lambda language: calls.append(language) or original(language))
    panel._search_input.setText("h")
    panel._search_input.setText("ha")
    assert calls == []
