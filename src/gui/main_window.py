#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# main_window.py
# Vokabeltrainer — main window: a thin tabbed frame that places pages.
# Knows nothing about what a page/panel does internally (see
# the project invariants, GUI composition principle) — moving a
# page to a different tab means changing this file, not the page.
#
# PIN gate (since v0.0.10.8, requirements 7.1): the first time the
# "Verwaltung" tab is selected in an app run, the parent PIN is asked.
# Once entered correctly the tab stays open until the app is closed. The
# window flips back to the previous tab *before* asking, so the tab's
# content is never visible behind the dialog. Whether a PIN is right is
# pin_store's decision; the "unlocked" flag here is only UI state.
#
# Refresh (since v0.0.11): event-driven, not on every tab switch. The
# Verwaltung page's vocab_changed signal (direct entry, import, edit,
# delete) refreshes the Test tab's language list; the Test tab refreshes
# its own status panel after a quiz session (see TestTab). MainWindow is
# the only place that knows both pages, so it makes this one connection.
#
# Info button (since v0.0.17): top right of the tab bar, opens the About
# window. No PIN - child and parents may look at it; it only shows version,
# copyright and the source link. Since v0.0.18 that window can ask for one of
# the shipped documents (README, user guide); MainWindow is the one place that
# knows both dialogs, so it connects the request to the document viewer.

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QPushButton, QTabWidget

import config
import pin_store
from gui import i18n
from gui.dialogs.about_dialog import AboutDialog
from gui.dialogs.doc_viewer_dialog import DocViewerDialog
from gui.dialogs.pin_prompt_dialog import PinPromptDialog
from gui.pages.management_tab import ManagementTab
from gui.pages.test_tab import TestTab

_MIN_SIZE = (480, 360)
_START_SIZE = (800, 600)


class MainWindow(QTabWidget):
    def __init__(self):
        super().__init__()
        ui_language = config.load_config()["language"]
        self.setWindowTitle("Vokabeltrainer")
        self.setMinimumSize(*_MIN_SIZE)
        self.resize(*_START_SIZE)
        self._test_tab = TestTab()
        self._management_tab = ManagementTab()
        self._management_tab.vocab_changed.connect(self._test_tab.refresh_languages)
        self.addTab(self._test_tab, i18n.text("tab_test", ui_language))
        self._management_index = self.addTab(
            self._management_tab, i18n.text("tab_verwaltung", ui_language)
        )
        self._about_button = QPushButton(i18n.text("about_button", ui_language))
        self._about_button.clicked.connect(self._on_about)
        self.setCornerWidget(self._about_button, Qt.Corner.TopRightCorner)
        self._management_unlocked = False
        self._previous_index = self.currentIndex()
        self.currentChanged.connect(self._on_tab_changed)

    def _on_about(self) -> None:
        dialog = AboutDialog(self)
        dialog.document_requested.connect(self._open_document)
        dialog.exec()

    def _open_document(self, name: str) -> None:
        DocViewerDialog(self, name).exec()

    def _on_tab_changed(self, index: int) -> None:
        if index == self._management_index and not self._management_unlocked:
            self.setCurrentIndex(self._previous_index)
            if PinPromptDialog(pin_store.verify_pin, self).exec() == QDialog.DialogCode.Accepted:
                self._management_unlocked = True
                self.setCurrentIndex(self._management_index)
            return
        self._previous_index = index
