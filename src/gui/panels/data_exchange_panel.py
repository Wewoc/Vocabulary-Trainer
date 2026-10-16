#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# data_exchange_panel.py
# Vokabeltrainer — Import/Export buttons (requirements 5.1, Optionen B/C).
# Wired for real since v0.0.9.5: file-picker dialogs (QFileDialog)
# around the already-existing data-layer functions
# (vocab.import_file()/export_rows(), csv_io.py). This file only reads
# a path from the user and a file from disk, then delegates the actual
# decision-making (dedup, instance-id trust) to vocab.py - no fachliche
# logic here (see the project invariants, GUI composition
# principle). Self-contained widget, knows nothing about its own
# placement on a page.
#
# Reading an externally-sourced file is a real system boundary (unlike
# the app's own CSVs) - wrapped in a try/except so a malformed/
# unreadable file shows a message instead of crashing the app.
#
# Since v0.0.13 an import shows a preview first: vocab.plan_import()
# decides (nothing is saved yet), ImportPreviewDialog shows the new
# entries, and only "Import" calls vocab.commit_import(). Nothing new to
# import -> no window, just the result line as before. The panel makes no
# decision itself - plan and commit are the same code path as the old
# one-step import_file().
#
# Since v0.0.16 the plan is made with resolve=True (cells with several
# meanings become one entry each) and the preview can switch that off again
# by asking plan_for(False); what gets committed is dialog.plan.
#
# Since v0.0.12.1 a successful export opens the target folder in the
# file manager (QDesktopServices) - always, no switch: whoever exports
# wants to see the file. Cancelled dialog, nothing ticked and write
# errors open nothing.
#
# Since v0.0.10.1: import first runs vocab.normalize_import_headers() so
# a Handarbeits-CSV using the configured display names (e.g.
# "Deutsch"/"Englisch") as column headers maps onto Sprache_A/Sprache_B
# automatically - see that function's docstring.

import logging
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import config
import csv_io
import report
import vocab
from gui import i18n
from gui.dialogs.import_preview_dialog import ImportPreviewDialog

_log = logging.getLogger(__name__)

_EXPORT_FIELDNAMES = ["quelle_instance_id", "UUID_A", "Sprache_A", "UUID_B", "Sprache_B", "Datum"]
_CSV_FILTER = "CSV (*.csv)"


class DataExchangePanel(QWidget):
    # Emitted after an import actually added at least one entry. A
    # containing page can connect this to refresh other panels (e.g.
    # VocabTablePanel) without either panel knowing the other exists -
    # same pattern as DirectEntryPanel.word_added.
    vocab_changed = pyqtSignal()

    def __init__(self, vocab_language: str | None = None):
        super().__init__()
        self._vocab_language = vocab_language or vocab.pick_default_language()
        self._ui_language = config.load_config()["language"]

        self._import_button = QPushButton(i18n.text("import_csv", self._ui_language))
        self._import_button.clicked.connect(self._on_import)
        self._export_button = QPushButton(i18n.text("export", self._ui_language))
        self._export_button.clicked.connect(self._on_export)
        self._export_wordlist_check = QCheckBox(i18n.text("export_wordlist_option", self._ui_language))
        self._export_wordlist_check.setChecked(True)
        self._export_report_check = QCheckBox(i18n.text("export_report_option", self._ui_language))
        self._export_report_check.setChecked(True)
        self._feedback_label = QLabel()

        button_row = QHBoxLayout()
        button_row.addWidget(self._import_button)
        button_row.addWidget(self._export_button)

        export_options_row = QHBoxLayout()
        export_options_row.addWidget(QLabel(i18n.text("export_includes", self._ui_language)))
        export_options_row.addWidget(self._export_wordlist_check)
        export_options_row.addWidget(self._export_report_check)
        export_options_row.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(button_row)
        layout.addLayout(export_options_row)
        layout.addWidget(self._feedback_label)
        self.setLayout(layout)

    def _on_import(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self, i18n.text("import_csv", self._ui_language), "", _CSV_FILTER
        )
        if not path_str:
            return  # dialog cancelled

        try:
            rows = csv_io.read_csv_file(Path(path_str))
        except (OSError, UnicodeDecodeError) as exc:
            _log.warning("import read error: %s", type(exc).__name__)
            self._feedback_label.setText(i18n.text("import_read_error", self._ui_language))
            return

        cfg = config.load_config()
        rows = vocab.normalize_import_headers(rows, cfg["sprache_a_name"], cfg["sprache_b_name"])

        def plan_for(resolve: bool) -> dict:
            return vocab.plan_import(self._vocab_language, rows, cfg["instance_id"], resolve)

        plan = plan_for(True)  # the preview offers a tick box to switch resolving off
        if plan["new"]:
            dialog = ImportPreviewDialog(self, plan, plan_for)
            accepted = dialog.exec() == QDialog.DialogCode.Accepted
            plan = dialog.plan  # the plan that was on screen when the user answered
            if not accepted:
                _log.info("import cancelled new=%d", len(plan["new"]))
                self._feedback_label.setText(i18n.text("import_cancelled", self._ui_language))
                return
        result = vocab.commit_import(self._vocab_language, plan)
        self._feedback_label.setText(i18n.text("import_result", self._ui_language, **result))
        if result["added"]:
            self.vocab_changed.emit()

    def _on_export(self) -> None:
        """Option C: exports the ticked items (word list, report) as
        separate files into a folder the user picks, named with date and
        time so nothing gets overwritten."""
        wordlist = self._export_wordlist_check.isChecked()
        with_report = self._export_report_check.isChecked()
        if not (wordlist or with_report):
            self._feedback_label.setText(i18n.text("export_nothing_selected", self._ui_language))
            return

        folder_str = QFileDialog.getExistingDirectory(
            self, i18n.text("export", self._ui_language), ""
        )
        if not folder_str:
            return  # dialog cancelled

        folder = Path(folder_str)
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        cfg = config.load_config()
        written = []
        try:
            if wordlist:
                path = folder / f"wortliste_{self._vocab_language}_{stamp}.csv"
                rows = vocab.export_rows(self._vocab_language, cfg["instance_id"])
                csv_io.write_csv_file(path, rows, _EXPORT_FIELDNAMES)
                written.append(path.name)
            if with_report:
                path = folder / f"report_{stamp}.csv"
                labels = {key: i18n.text(f"report_{key}", self._ui_language) for key in report.LABEL_KEYS}
                names = {"A": cfg["sprache_a_name"], "B": cfg["sprache_b_name"]}
                report.write_report(path, labels, self._ui_language, names)
                written.append(path.name)
        except OSError as exc:
            _log.warning("export write error: %s", type(exc).__name__)
            self._feedback_label.setText(i18n.text("export_write_error", self._ui_language))
            return

        self._feedback_label.setText(
            i18n.text("export_files_result", self._ui_language, count=len(written), names=", ".join(written))
        )
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder))):
            _log.warning("could not open export folder")
