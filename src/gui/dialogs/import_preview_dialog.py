#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# import_preview_dialog.py
# Vokabeltrainer — preview before an import (requirements 5.1, Option B):
# shows the entries an import would add, the counts of skipped rows and
# the data row numbers of invalid ones, and asks for confirmation. Holds
# no decision logic - the plan comes from vocab.plan_import(), this dialog
# only displays it and accepts or rejects. All-or-nothing: rows can't be
# deselected one by one. Self-contained widget, knows nothing about who
# opens it (see the project invariants).
#
# Since v0.0.16 the opener may pass `replan(resolve) -> plan`. The dialog
# then offers a tick box "resolve brackets and separators" (on by default,
# the plan it was given is expected to be the resolved one); toggling it
# asks the opener for a fresh plan and redraws. `plan` is always the plan
# currently shown - that is the one to commit.

from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

import config
from gui import i18n

_MAX_LISTED_INVALID_ROWS = 20


class ImportPreviewDialog(QDialog):
    def __init__(self, parent, plan: dict, replan=None):
        super().__init__(parent)
        self._plan = plan
        self._replan = replan
        cfg = config.load_config()
        self._ui_language = ui_language = cfg["language"]
        self.setWindowTitle(i18n.text("import_preview_title", ui_language))

        self._summary_label = QLabel()
        self._resolved_label = QLabel()
        self._check_label = QLabel()
        self._check_label.setWordWrap(True)
        self._invalid_label = QLabel()
        self._invalid_label.setWordWrap(True)

        self._resolve_check = None
        if replan is not None:
            self._resolve_check = QCheckBox(i18n.text("import_preview_resolve_option", ui_language))
            self._resolve_check.setChecked(True)
            self._resolve_check.toggled.connect(self._on_resolve_toggled)

        table = QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(
            [cfg["sprache_a_name"], cfg["sprache_b_name"], i18n.text("import_preview_row_column", ui_language)]
        )
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._table = table

        confirm_button = QPushButton(i18n.text("import_preview_confirm", ui_language))
        confirm_button.clicked.connect(self.accept)
        cancel_button = QPushButton(i18n.text("cancel", ui_language))
        cancel_button.clicked.connect(self.reject)
        button_row = QHBoxLayout()
        button_row.addWidget(confirm_button)
        button_row.addWidget(cancel_button)

        layout = QVBoxLayout()
        layout.addWidget(self._summary_label)
        if self._resolve_check is not None:
            layout.addWidget(self._resolve_check)
        layout.addWidget(self._resolved_label)
        layout.addWidget(self._check_label)
        layout.addWidget(self._invalid_label)
        layout.addWidget(table)
        layout.addLayout(button_row)
        self.setLayout(layout)
        self.resize(560, 460)
        self._show_plan()

    @property
    def plan(self) -> dict:
        """The plan currently shown - what the opener should commit."""
        return self._plan

    def _on_resolve_toggled(self, checked: bool) -> None:
        self._plan = self._replan(checked)
        self._show_plan()

    def _show_plan(self) -> None:
        plan, ui_language = self._plan, self._ui_language
        self._summary_label.setText(
            i18n.text(
                "import_preview_summary",
                ui_language,
                new=len(plan["new"]),
                skipped_duplicate=plan["skipped_duplicate"],
                skipped_invalid=plan["skipped_invalid"],
            )
        )

        resolved_rows = plan.get("resolved_rows", 0)
        self._resolved_label.setText(
            i18n.text(
                "import_preview_resolved", ui_language, rows=resolved_rows, pairs=plan.get("resolved_pairs", 0)
            )
            if resolved_rows
            else ""
        )
        self._resolved_label.setVisible(bool(resolved_rows))

        check_rows = plan.get("check_rows", [])
        self._check_label.setText(
            i18n.text("import_preview_check", ui_language, rows=self._listed(check_rows, ui_language))
            if check_rows
            else ""
        )
        self._check_label.setVisible(bool(check_rows))

        self._invalid_label.setText(
            i18n.text("import_preview_invalid", ui_language, rows=self._listed(plan["invalid_rows"], ui_language))
            if plan["invalid_rows"]
            else ""
        )
        self._invalid_label.setVisible(bool(plan["invalid_rows"]))

        source_rows = plan.get("source_rows") or []
        table = self._table
        table.setRowCount(len(plan["new"]))
        for row, entry in enumerate(plan["new"]):
            table.setItem(row, 0, QTableWidgetItem(entry["Sprache_A"]))
            table.setItem(row, 1, QTableWidgetItem(entry["Sprache_B"]))
            if row < len(source_rows):
                table.setItem(row, 2, QTableWidgetItem(str(source_rows[row])))
        table.setColumnHidden(2, not source_rows)

    @staticmethod
    def _listed(rows: list[int], ui_language: str) -> str:
        listed = ", ".join(str(n) for n in rows[:_MAX_LISTED_INVALID_ROWS])
        if len(rows) > _MAX_LISTED_INVALID_ROWS:
            listed += " " + i18n.text(
                "import_preview_more", ui_language, count=len(rows) - _MAX_LISTED_INVALID_ROWS
            )
        return listed
