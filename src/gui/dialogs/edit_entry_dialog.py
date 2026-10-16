#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# edit_entry_dialog.py
# Vokabeltrainer — edit popup for a single vocab row (requirements 5.1).
# Pre-filled with the row's current Sprache_A/Sprache_B text. On save,
# calls vocab.edit_term() once per changed side — A and B are separate
# term-spaces (requirements 3.1), each edit_term() call updates every row
# sharing that UUID (ambiguity cluster), not just this one. Leaving a
# field empty is treated as "no change" there, never saved as an empty
# term. Self-contained widget, knows nothing about who opens it (see
# the project invariants, GUI composition principle) — the only
# fachliche decision (which rows to update) happens in vocab.edit_term().

from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

import config
import vocab
from gui import i18n


class EditEntryDialog(QDialog):
    def __init__(self, parent, vocab_language: str, entry: dict):
        super().__init__(parent)
        cfg = config.load_config()
        ui_language = cfg["language"]
        self.setWindowTitle(i18n.text("edit", ui_language))
        self._ui_language = ui_language
        self._vocab_language = vocab_language
        self._entry = entry

        self._text_a_input = QLineEdit(entry["Sprache_A"])
        self._text_a_input.setPlaceholderText(cfg["sprache_a_name"])
        self._text_b_input = QLineEdit(entry["Sprache_B"])
        self._text_b_input.setPlaceholderText(cfg["sprache_b_name"])
        self._feedback_label = QLabel()

        field_row = QHBoxLayout()
        field_row.addWidget(self._text_a_input)
        field_row.addWidget(self._text_b_input)

        self._save_button = QPushButton(i18n.text("save", ui_language))
        self._save_button.clicked.connect(self._on_save)
        self._cancel_button = QPushButton(i18n.text("cancel", ui_language))
        self._cancel_button.clicked.connect(self.reject)

        button_row = QHBoxLayout()
        button_row.addWidget(self._save_button)
        button_row.addWidget(self._cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(field_row)
        layout.addWidget(self._feedback_label)
        layout.addLayout(button_row)
        self.setLayout(layout)

    def _on_save(self) -> None:
        new_text_a = self._text_a_input.text().strip()
        new_text_b = self._text_b_input.text().strip()
        if not new_text_a or not new_text_b:
            self._feedback_label.setText(i18n.text("missing_fields", self._ui_language))
            return

        if new_text_a != self._entry["Sprache_A"]:
            vocab.edit_term(self._vocab_language, self._entry["UUID_A"], new_text_a)
        if new_text_b != self._entry["Sprache_B"]:
            vocab.edit_term(self._vocab_language, self._entry["UUID_B"], new_text_b)
        self.accept()
