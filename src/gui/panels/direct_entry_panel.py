#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# direct_entry_panel.py
# Vokabeltrainer — Option A, direct entry (see
# requirements 5.1): two fields, adds a word pair
# via vocab.add_entry(). Self-contained widget, knows nothing about its
# own placement on a page (see the project invariants, GUI
# composition principle).
#
# Since v0.0.10.1: the two fields show the configured sprache_a_name/
# sprache_b_name (e.g. "Deutsch"/"Englisch") as placeholder text
# instead of staying unlabeled - cheaper than a separate QLabel per
# field and disappears once something is typed anyway.

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

import config
import vocab
from gui import i18n


class DirectEntryPanel(QWidget):
    # Emitted after a genuinely new word was added (not on a duplicate).
    # A containing page can connect this to refresh other panels (e.g.
    # VocabTablePanel) without either panel knowing the other exists.
    word_added = pyqtSignal()

    def __init__(self, vocab_language: str | None = None):
        super().__init__()
        self._vocab_language = vocab_language or vocab.pick_default_language()
        cfg = config.load_config()
        self._ui_language = cfg["language"]

        self._text_a_input = QLineEdit()
        self._text_a_input.setPlaceholderText(cfg["sprache_a_name"])
        self._text_b_input = QLineEdit()
        self._text_b_input.setPlaceholderText(cfg["sprache_b_name"])
        self._add_button = QPushButton(i18n.text("add_word", self._ui_language))
        self._feedback_label = QLabel()

        field_row = QHBoxLayout()
        field_row.addWidget(self._text_a_input)
        field_row.addWidget(self._text_b_input)

        layout = QVBoxLayout()
        layout.addLayout(field_row)
        layout.addWidget(self._add_button)
        layout.addWidget(self._feedback_label)
        self.setLayout(layout)

        self._add_button.clicked.connect(self._on_add)
        self._text_a_input.returnPressed.connect(self._on_add)
        self._text_b_input.returnPressed.connect(self._on_add)

    def _on_add(self) -> None:
        text_a = self._text_a_input.text().strip()
        text_b = self._text_b_input.text().strip()
        if not text_a or not text_b:
            self._feedback_label.setText(i18n.text("missing_fields", self._ui_language))
            return

        entry, was_added = vocab.add_entry(self._vocab_language, text_a, text_b)
        key = "added" if was_added else "added_duplicate"
        self._feedback_label.setText(
            i18n.text(key, self._ui_language, a=entry["Sprache_A"], b=entry["Sprache_B"])
        )
        if was_added:
            self.word_added.emit()
        self._text_a_input.clear()
        self._text_b_input.clear()
        self._text_a_input.setFocus()
