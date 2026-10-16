#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# status_panel.py
# Vokabeltrainer — Test-tab status display: motivational statistics
# derived from tracking.enc (see data model, section 2,
# stats.py). Real as of v0.0.8 - the panel only loads the tracking
# data and formats stats.compute()'s result, all the actual
# computation lives in stats.py (see the project invariants, GUI
# composition principle). Self-contained widget, knows nothing about
# its own placement on a page.
#
# Since v0.0.11 the numbers can be refreshed in place: refresh() re-reads
# the tracking data and sets the label texts (the labels are built once).
# The page calls it after a quiz session ends - not on every tab switch,
# because load_tracking() costs ~230 ms (key derivation), which would make
# every click on the Test tab stutter. Event-driven refresh instead.

from PyQt6.QtWidgets import QGridLayout, QLabel, QWidget

_COLUMNS = 2
_ROW_SPACING = 12
_LABEL_COUNT = 7

import config
import stats
import tracking
from gui import i18n


class StatusPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._ui_language = config.load_config()["language"]
        self._labels = [QLabel() for _ in range(_LABEL_COUNT)]

        layout = QGridLayout()
        layout.setVerticalSpacing(_ROW_SPACING)
        for index, label in enumerate(self._labels):
            layout.addWidget(label, index // _COLUMNS, index % _COLUMNS)
        self.setLayout(layout)

        self.refresh()

    def refresh(self) -> None:
        """Re-reads the tracking data and updates all seven figures."""
        ui_language = self._ui_language
        computed = stats.compute(tracking.load_tracking())

        last_test = computed["last_test_date"] or i18n.text("status_never_tested", ui_language)

        texts = [
            i18n.text("status_tests_done", ui_language, count=computed["tests_completed"]),
            i18n.text(
                "status_correct", ui_language, correct=computed["correct"], total=computed["answered"]
            ),
            i18n.text("status_last_test", ui_language, date=last_test),
            i18n.text(
                "status_day_streak",
                ui_language,
                current=computed["day_streak_current"],
                longest=computed["day_streak_longest"],
            ),
            i18n.text(
                "status_correct_streak",
                ui_language,
                current=computed["correct_streak_current"],
                longest=computed["correct_streak_longest"],
            ),
            i18n.text("status_mastered", ui_language, count=computed["mastered_words"]),
            i18n.text(
                "status_week_comparison",
                ui_language,
                this_week=computed["tests_this_week"],
                last_week=computed["tests_last_week"],
            ),
        ]
        for label, text in zip(self._labels, texts):
            label.setText(text)
