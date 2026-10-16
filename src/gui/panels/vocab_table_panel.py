#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# vocab_table_panel.py
# Vokabeltrainer — display of the current vocab bestand
# (daten/vokabeln/<language>.csv), plus Edit/Delete for requirements
# 5.1's Edit function. Self-contained widget, knows nothing about its
# own placement on a page (see the project invariants).
#
# Edit/Delete wired for real since v0.0.9.4: row selection enables both
# buttons, Edit opens EditEntryDialog (gui/dialogs/), Delete asks for
# confirmation (QMessageBox) before calling vocab.delete_entry() - no
# custom confirm dialog needed for a plain yes/no. Both reload() the
# table afterward; selection is lost on reload (QTableWidget rebuilds
# its rows), which re-disables the buttons until a row is picked again
# - acceptable, not worth preserving selection across a rebuild for
# this.
#
# Since v0.0.10.13 a search field above the table filters the rows live
# (vocab.search_entries(): substring in either language column, ignoring
# case and accents); non-matching rows are hidden, not deleted, and a
# counter shows "x of y" so the filtering is never silent. reload() still
# re-reads the file (and keeps the search text); typing only re-applies
# the filter to the entries already in memory - no disk access per
# keystroke. Edit/Delete keep working on the filtered list: the real
# UUIDs sit in the hidden table columns.
#
# Since v0.0.10.12 the table is read-only (NoEditTriggers): cells used to
# be editable in place by double-click or typing, which only changed the
# displayed text (never the CSV) - and Edit's dialog reads its prefill
# from the table. Editing happens exclusively through EditEntryDialog.
#
# Since v0.0.10.1: UUID_A/UUID_B columns stay in the underlying table
# (still needed by _selected_entry() to read the real UUIDs for Edit/
# Delete) but are hidden via setColumnHidden() - showing raw UUIDs
# confused more than it helped (maintainer decision). Sprache_A/Sprache_B column
# headers show the configured display names (sprache_a_name/
# sprache_b_name) instead of the technical field names - _COLUMNS
# (the data field keys) and the header labels shown to the user are
# now two separate lists.

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import config
import vocab
from gui import i18n
from gui.dialogs.edit_entry_dialog import EditEntryDialog

_COLUMNS = ["UUID_A", "Sprache_A", "UUID_B", "Sprache_B", "Datum"]
_HIDDEN_COLUMNS = ("UUID_A", "UUID_B")


class VocabTablePanel(QWidget):
    # Emitted after an entry was edited or deleted (v0.0.11) - same pattern
    # as DataExchangePanel.vocab_changed, so a page can pass the news on
    # without panels knowing each other.
    vocab_changed = pyqtSignal()

    def __init__(self, vocab_language: str | None = None):
        super().__init__()
        self._vocab_language = vocab_language or vocab.pick_default_language()
        cfg = config.load_config()
        self._ui_language = cfg["language"]

        header_labels = {
            "UUID_A": "UUID_A",
            "Sprache_A": cfg["sprache_a_name"],
            "UUID_B": "UUID_B",
            "Sprache_B": cfg["sprache_b_name"],
            "Datum": i18n.text("date_label", self._ui_language),
        }

        self._entries: list[dict] = []
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(i18n.text("search_placeholder", self._ui_language))
        self._search_input.setClearButtonEnabled(True)
        self._search_input.textChanged.connect(self._show)
        self._count_label = QLabel()

        search_row = QHBoxLayout()
        search_row.addWidget(self._search_input, 1)
        search_row.addWidget(self._count_label)

        self._table = QTableWidget()
        self._table.setColumnCount(len(_COLUMNS))
        self._table.setHorizontalHeaderLabels([header_labels[field] for field in _COLUMNS])
        for col, field in enumerate(_COLUMNS):
            self._table.setColumnHidden(col, field in _HIDDEN_COLUMNS)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)

        self._edit_button = QPushButton(i18n.text("edit", self._ui_language))
        self._edit_button.setEnabled(False)
        self._edit_button.clicked.connect(self._on_edit)
        self._delete_button = QPushButton(i18n.text("delete", self._ui_language))
        self._delete_button.setEnabled(False)
        self._delete_button.clicked.connect(self._on_delete)

        button_row = QHBoxLayout()
        button_row.addWidget(self._edit_button)
        button_row.addWidget(self._delete_button)

        layout = QVBoxLayout()
        layout.addLayout(search_row)
        layout.addWidget(self._table)
        layout.addLayout(button_row)
        self.setLayout(layout)

        self.reload()

    def reload(self) -> None:
        """Re-reads the vocab bestand and refreshes the table (keeping the
        search text). Public so a containing page can call it after a
        change elsewhere (e.g. direct entry) - ManagementTab wires that."""
        self._entries = vocab.load_entries(self._vocab_language)
        self._show()

    def _show(self) -> None:
        """Applies the current search text to the entries in memory and
        rebuilds the table rows (selection is lost, like on reload())."""
        query = self._search_input.text()
        shown = vocab.search_entries(self._entries, query)
        self._table.setRowCount(len(shown))
        for row, entry in enumerate(shown):
            for col, field in enumerate(_COLUMNS):
                self._table.setItem(row, col, QTableWidgetItem(entry[field]))
        total = len(self._entries)
        if query.strip():
            text = i18n.text("search_count", self._ui_language, shown=len(shown), total=total)
        else:
            text = i18n.text("entry_count", self._ui_language, total=total)
        self._count_label.setText(text)

    def _selected_entry(self) -> dict | None:
        row = self._table.currentRow()
        if row < 0:
            return None
        return {field: self._table.item(row, col).text() for col, field in enumerate(_COLUMNS)}

    def _on_selection_changed(self) -> None:
        has_selection = self._table.currentRow() >= 0
        self._edit_button.setEnabled(has_selection)
        self._delete_button.setEnabled(has_selection)

    def _on_edit(self) -> None:
        entry = self._selected_entry()
        if entry is None:
            return
        dialog = EditEntryDialog(self, self._vocab_language, entry)
        if dialog.exec():
            self.reload()
            self.vocab_changed.emit()

    def _on_delete(self) -> None:
        entry = self._selected_entry()
        if entry is None:
            return
        reply = QMessageBox.question(
            self,
            i18n.text("confirm_delete_title", self._ui_language),
            i18n.text("confirm_delete_message", self._ui_language),
        )
        if reply == QMessageBox.StandardButton.Yes:
            vocab.delete_entry(self._vocab_language, entry["UUID_A"], entry["UUID_B"])
            self.reload()
            self.vocab_changed.emit()
