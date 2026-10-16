#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# evaluation_dialog.py
# Vokabeltrainer — end-of-session evaluation popup (requirements 4,
# mockup). Shows the real per-task results of the session that was
# just played since v0.0.9.3 - QuizDialog passes QuizPanel.session_results()
# in. Self-contained widget, knows nothing about who opens it (see
# the project invariants, GUI composition principle) - it only
# renders the `results` it's handed, it doesn't know how they were
# produced or what "hit" means (that's evaluation.is_hit(), the same
# definition stats.py uses for its own streak/accuracy numbers).
#
# The closing button reads "Beenden - Erfolge übernehmen" (finish_early
# i18n key, reused from the now-removed mid-session button - a maintainer
# decision, see git history), not a plain "Schließen" - closing
# this dialog IS the moment the session is accepted as completed
# (QuizDialog.finalize_session() runs right after .exec() returns), so
# the label should say what actually happens, not just "close".

from PyQt6.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton, QVBoxLayout

import config
import evaluation
from gui import i18n

_SMILEY_CORRECT = "\U0001F642"  # slightly smiling face
_SMILEY_WRONG = "\U0001F622"  # crying face


class EvaluationDialog(QDialog):
    def __init__(self, parent=None, results: list[dict] | None = None):
        super().__init__(parent)
        ui_language = config.load_config()["language"]
        self.setWindowTitle(i18n.text("evaluation_dialog_title", ui_language))
        results = results or []

        grid = QGridLayout()
        correct_count = 0
        row = 0
        for result in results:
            was_hit = evaluation.is_hit(result["outcome"])
            soll_ist = f"{result['expected']} / {result['given']}"
            grid.addWidget(QLabel(result["prompt"]), row, 0)
            grid.addWidget(QLabel(soll_ist), row, 1)
            grid.addWidget(QLabel(_SMILEY_CORRECT if was_hit else _SMILEY_WRONG), row, 2)
            correct_count += was_hit
            row += 1

        total = len(results)
        grid.addWidget(
            QLabel(i18n.text("evaluation_total", ui_language, correct=correct_count, total=total)),
            row,
            0,
        )
        grid.addWidget(
            QLabel(_SMILEY_CORRECT if correct_count == total else _SMILEY_WRONG), row, 2
        )

        self._finish_button = QPushButton(i18n.text("finish_early", ui_language))
        self._finish_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addLayout(grid)
        layout.addWidget(self._finish_button)
        self.setLayout(layout)
