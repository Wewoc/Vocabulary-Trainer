#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# test_konfigurator_panel.py
# Vokabeltrainer — Test-Konfigurator (requirements 4.1: language,
# direction, count, filters). Wired for real since v0.0.9.2 - every
# control is enabled, and TestTab reads the current selection through
# the getters below when "Test starten" is clicked (see
# gui/pages/test_tab.py, gui/dialogs/quiz_dialog.py). The getters only
# read widget state, no fachliche Entscheidung happens here (see
# the project invariants, GUI composition principle) - the
# selection is just handed to QuizPanel, which does the actual work.
#
# Direction only offers A->B/B->A, matching requirements 4.1 exactly - no
# "Mixed" option (an earlier v0.0.7.2 placeholder, dropped in v0.0.9.2:
# it was never actually specified, and mixing directions within one
# session would need tracking against two different UUID columns in
# the same pass, see gui/panels/quiz_panel.py).
#
# Filter "nur neueste" (requirements 4.1 names a fixed 10/25/50 choice) -
# built here as a free-form count field ("Testlänge") next to the
# checkbox instead, more flexible than three fixed options for the same
# amount of code.
#
# QGroupBox instead of plain QWidget (since v0.0.7.4) purely for the
# visible frame around its own fields - still a self-contained panel,
# not a page-level layout concern (see the project invariants,
# GUI composition principle). Since v0.0.10.3 the title is a QLabel as
# the first row inside the frame instead of the QGroupBox title: the
# theme's QGroupBox style reserves no room for the title line, so it
# overlapped the first control once the page stopped stretching rows.

from PyQt6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QVBoxLayout,
)

import config
import vocab
from gui import i18n
from gui.widgets.no_wheel import NoWheelComboBox
from gui.widgets.number_stepper import NumberStepper

_DEFAULT_FILTER_NEWEST_COUNT = 25
_ROW_SPACING = 12


class TestKonfiguratorPanel(QGroupBox):
    def __init__(self):
        cfg = config.load_config()
        ui_language = cfg["language"]
        super().__init__()
        self._title_label = QLabel(i18n.text("test_konfigurator_title", ui_language))
        sprache_a_name = cfg["sprache_a_name"]
        sprache_b_name = cfg["sprache_b_name"]

        self._language_combo = NoWheelComboBox()
        self._language_combo.addItems(vocab.list_languages())

        self._direction_a_to_b = QRadioButton(f"{sprache_a_name} → {sprache_b_name}")
        self._direction_a_to_b.setChecked(True)
        self._direction_b_to_a = QRadioButton(f"{sprache_b_name} → {sprache_a_name}")
        direction_row = QHBoxLayout()
        direction_row.addWidget(self._direction_a_to_b)
        direction_row.addWidget(self._direction_b_to_a)

        self._count_label = QLabel(i18n.text("count_label", ui_language))
        self._count_spinbox = NumberStepper()
        self._count_spinbox.setRange(1, 999)
        self._count_spinbox.setValue(20)
        count_row = QHBoxLayout()
        count_row.addWidget(self._count_label, 1)
        count_row.addWidget(self._count_spinbox, 1)

        self._filter_newest = QCheckBox(i18n.text("filter_newest", ui_language))
        self._filter_newest_count_spinbox = NumberStepper()
        self._filter_newest_count_spinbox.setRange(1, 500)
        self._filter_newest_count_spinbox.setValue(_DEFAULT_FILTER_NEWEST_COUNT)
        self._filter_newest_count_spinbox.setEnabled(False)
        self._filter_newest.toggled.connect(self._filter_newest_count_spinbox.setEnabled)
        filter_newest_row = QHBoxLayout()
        filter_newest_row.addWidget(self._filter_newest, 1)
        filter_newest_row.addWidget(self._filter_newest_count_spinbox, 1)

        self._filter_errors = QCheckBox(i18n.text("filter_errors", ui_language))

        layout = QVBoxLayout()
        layout.setSpacing(_ROW_SPACING)
        layout.addWidget(self._title_label)
        layout.addWidget(self._language_combo)
        layout.addLayout(direction_row)
        layout.addLayout(count_row)
        layout.addLayout(filter_newest_row)
        layout.addWidget(self._filter_errors)
        self.setLayout(layout)

    def refresh_languages(self) -> None:
        """Re-reads the available vocab lists into the language field
        (e.g. after the first list was created or imported). Keeps the
        current choice if that list still exists, otherwise falls back to
        the first one. Direction, count and filters are left alone."""
        current = self._language_combo.currentText()
        languages = vocab.list_languages()
        self._language_combo.clear()
        self._language_combo.addItems(languages)
        if current in languages:
            self._language_combo.setCurrentText(current)

    def selected_language(self) -> str | None:
        """None if no vocab list exists yet (empty combo) - callers fall
        back to vocab.pick_default_language()."""
        return self._language_combo.currentText() or None

    def selected_direction(self) -> str:
        return "A->B" if self._direction_a_to_b.isChecked() else "B->A"

    def selected_count(self) -> int:
        return self._count_spinbox.value()

    def selected_filter_newest(self) -> int | None:
        return self._filter_newest_count_spinbox.value() if self._filter_newest.isChecked() else None

    def selected_filter_errors_only(self) -> bool:
        return self._filter_errors.isChecked()
