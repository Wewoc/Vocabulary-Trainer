#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# quiz_dialog.py
# Vokabeltrainer — popup window hosting a quiz session (requirements 4,
# mockup). Thin container around QuizPanel, same composition principle
# as a page (see the project invariants): wraps the panel without
# touching its internals. QuizPanel's own logic is unchanged - only its
# placement moved from inline-in-tab (v0.0.7.2) to this popup
# (v0.0.7.4). A side effect: a fresh QuizPanel (and
# thus a freshly built quiz queue) is created each time this dialog
# opens, so multiple sessions can now be run without restarting the
# app - previously impossible since QuizPanel was built once for the
# app's lifetime.
#
# Session recording (v0.0.8, see data model, section 2):
# this dialog decides completed vs. not, QuizPanel only records what
# it's told.
#   - "Abbrechen" or closing the window (X button - treated the same,
#     see closeEvent()) -> cancel_session(), never counts. There is no
#     mid-session way to end early and still count - an earlier
#     "Finish - Keep Progress" button here was dropped (maintainer decision,
#     see git history): that action now only exists as the evaluation
#     popup's own close button (see evaluation_dialog.py).
#   - A session only counts as completed once its evaluation popup has
#     been closed - not when the last question was answered.
#     EvaluationDialog shows this session's real per-task results since
#     v0.0.9.3 (QuizPanel.session_results()), not a placeholder shell.
# `_resolved` guards against double-recording: closeEvent() only
# cancels if nothing else already decided the session's outcome.

from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout

import config
from gui import i18n
from gui.dialogs.evaluation_dialog import EvaluationDialog
from gui.panels.quiz_panel import QuizPanel


class QuizDialog(QDialog):
    def __init__(
        self,
        parent=None,
        vocab_language: str | None = None,
        direction: str = "A->B",
        count: int | None = None,
        filter_newest: int | None = None,
        filter_errors_only: bool = False,
    ):
        super().__init__(parent)
        ui_language = config.load_config()["language"]
        self.setWindowTitle(i18n.text("quiz_dialog_title", ui_language))
        self._resolved = False

        self._quiz_panel = QuizPanel(
            vocab_language=vocab_language,
            direction=direction,
            count=count,
            filter_newest=filter_newest,
            filter_errors_only=filter_errors_only,
        )
        self._quiz_panel.session_finished.connect(self._on_session_finished)

        self._cancel_button = QPushButton(i18n.text("cancel", ui_language))
        self._cancel_button.clicked.connect(self._on_cancel)

        layout = QVBoxLayout()
        layout.addWidget(self._quiz_panel)
        layout.addWidget(self._cancel_button)
        self.setLayout(layout)

    def _on_cancel(self) -> None:
        self._resolved = True
        self._quiz_panel.cancel_session()
        self.reject()

    def _on_session_finished(self) -> None:
        self._resolved = True
        EvaluationDialog(self, results=self._quiz_panel.session_results()).exec()
        self._quiz_panel.finalize_session()
        self.accept()

    def closeEvent(self, event) -> None:
        if not self._resolved:
            self._resolved = True
            self._quiz_panel.cancel_session()
        super().closeEvent(event)
