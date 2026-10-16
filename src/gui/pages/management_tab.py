#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# management_tab.py
# Vokabeltrainer — "Verwaltung" tab: thin page that places direct entry,
# the vocab table, data exchange, and settings panels together. Knows
# nothing about what any panel does internally (see
# the project invariants, GUI composition principle) — only
# assembles them.
#
# PIN-protected, but not here: the gate lives in MainWindow (v0.0.10.8),
# this page knows nothing about it.

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget

from gui.panels.data_exchange_panel import DataExchangePanel
from gui.panels.direct_entry_panel import DirectEntryPanel
from gui.panels.settings_panel import SettingsPanel
from gui.panels.vocab_table_panel import VocabTablePanel

_TABLE_MIN_HEIGHT = 260


class ManagementTab(QScrollArea):
    # Collects every change to the vocab bestand made on this page (direct
    # entry, import, edit, delete) into one signal, so MainWindow can wire
    # it to the Test tab without knowing which panel caused it (v0.0.11).
    vocab_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._direct_entry = DirectEntryPanel()
        self._vocab_table = VocabTablePanel()
        self._data_exchange = DataExchangePanel()
        self._direct_entry.word_added.connect(self._vocab_table.reload)
        self._data_exchange.vocab_changed.connect(self._vocab_table.reload)
        self._direct_entry.word_added.connect(self.vocab_changed)
        self._data_exchange.vocab_changed.connect(self.vocab_changed)
        self._vocab_table.vocab_changed.connect(self.vocab_changed)
        self._vocab_table.setMinimumHeight(_TABLE_MIN_HEIGHT)

        layout = QVBoxLayout()
        layout.addWidget(self._direct_entry)
        layout.addWidget(self._vocab_table, 1)
        layout.addWidget(self._data_exchange)
        layout.addWidget(SettingsPanel())

        container = QWidget()
        container.setLayout(layout)
        self.setWidget(container)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
