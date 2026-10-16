#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# test_tab.py
# Vokabeltrainer — "Test" tab: thin page that places the status panel
# and the Test-Konfigurator shell above a "Start" button, which opens
# the quiz session as a popup (QuizDialog, since v0.0.7.4 -
# the quiz used to run inline in this tab, see git history). Knows
# nothing about what any panel/dialog does internally (see
# the project invariants, GUI composition principle) — only
# assembles/opens them and, since v0.0.9.2, reads the Konfigurator's
# current selection to pass along when opening QuizDialog - reading a
# widget's own state and forwarding it is still composition, not a
# fachliche Entscheidung (the Konfigurator's getters do the reading,
# QuizPanel does the deciding).

from PyQt6.QtWidgets import QFrame, QPushButton, QScrollArea, QVBoxLayout, QWidget

import config
from gui import i18n
from gui.dialogs.quiz_dialog import QuizDialog
from gui.panels.banner_panel import BannerPanel
from gui.panels.status_panel import StatusPanel
from gui.panels.test_konfigurator_panel import TestKonfiguratorPanel


class TestTab(QScrollArea):
    def __init__(self):
        super().__init__()
        ui_language = config.load_config()["language"]

        self._konfigurator = TestKonfiguratorPanel()
        self._status = StatusPanel()
        self._start_button = QPushButton(i18n.text("start_test", ui_language))
        self._start_button.clicked.connect(self._on_start)

        layout = QVBoxLayout()
        layout.addWidget(BannerPanel())
        layout.addWidget(self._status)
        layout.addWidget(self._konfigurator)
        layout.addWidget(self._start_button)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)
        self.setWidget(container)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

    def refresh_languages(self) -> None:
        """Re-reads the vocab lists into the Konfigurator (wired by
        MainWindow to the Verwaltung page's vocab_changed signal)."""
        self._konfigurator.refresh_languages()

    def _on_start(self) -> None:
        QuizDialog(
            self,
            vocab_language=self._konfigurator.selected_language(),
            direction=self._konfigurator.selected_direction(),
            count=self._konfigurator.selected_count(),
            filter_newest=self._konfigurator.selected_filter_newest(),
            filter_errors_only=self._konfigurator.selected_filter_errors_only(),
        ).exec()
        self._status.refresh()  # the session just written is now in the tracking
