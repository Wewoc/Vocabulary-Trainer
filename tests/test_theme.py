# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Offscreen tests: table selection colour comes from the theme, and the
# vocab table is read-only.

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PyQt6.QtWidgets import QAbstractItemView, QApplication  # noqa: E402

import paths  # noqa: E402
import theme  # noqa: E402
import vocab  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize("name", theme.theme_names())
def test_selected_table_row_uses_theme_tokens(name):
    colors = theme.colors(name)
    sheet = " ".join(theme.stylesheet(name).split())
    rule = (
        "QTableWidget::item:selected { "
        f"background-color: {colors['accent2']}; color: {colors['bg2']}; }}"
    )
    assert rule in sheet


def test_vocab_table_is_read_only(app, tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    vocab.save_entries(
        "englisch",
        [{"UUID_A": "a1", "Sprache_A": "Haus", "UUID_B": "b1", "Sprache_B": "house", "Datum": "2026-10-11"}],
    )
    from gui.panels.vocab_table_panel import VocabTablePanel

    panel = VocabTablePanel("englisch")
    table = panel._table
    assert table.editTriggers() == QAbstractItemView.EditTrigger.NoEditTriggers
    # AllEditTriggers is Qt's programmatic "force" value, so check the real user triggers
    index = table.model().index(0, 1)
    for trigger in (
        QAbstractItemView.EditTrigger.DoubleClicked,
        QAbstractItemView.EditTrigger.EditKeyPressed,
        QAbstractItemView.EditTrigger.AnyKeyPressed,
    ):
        assert not table.edit(index, trigger, None)
    assert table.item(0, 1).text() == "Haus"
