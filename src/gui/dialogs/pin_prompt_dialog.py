#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# pin_prompt_dialog.py
# Vokabeltrainer — asks for the parent PIN (access gate for the Verwaltung
# tab, wired in v0.0.10.8). Holds no decision logic: the entered text
# goes to the `check` function the caller passes in (pin_store.verify_pin),
# which decides whether it is right. Accepts only on a correct PIN.

from collections.abc import Callable

from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

import config
from gui import i18n


class PinPromptDialog(QDialog):
    def __init__(self, check: Callable[[str], bool], parent=None):
        super().__init__(parent)
        self._check = check
        self._ui_language = config.load_config()["language"]
        self.setWindowTitle(i18n.text("pin_prompt_title", self._ui_language))

        self._pin_input = QLineEdit()
        self._pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._feedback_label = QLabel()

        self._ok_button = QPushButton("OK")
        self._ok_button.setDefault(True)  # Enter triggers this button; no extra returnPressed
        self._ok_button.clicked.connect(self._on_ok)
        self._cancel_button = QPushButton(i18n.text("cancel", self._ui_language))
        self._cancel_button.clicked.connect(self.reject)

        button_row = QHBoxLayout()
        button_row.addWidget(self._ok_button)
        button_row.addWidget(self._cancel_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(i18n.text("pin_prompt_hint", self._ui_language)))
        layout.addWidget(self._pin_input)
        layout.addWidget(self._feedback_label)
        layout.addLayout(button_row)
        self.setLayout(layout)

    def _on_ok(self) -> None:
        if self._check(self._pin_input.text()):
            self.accept()
            return
        self._feedback_label.setText(i18n.text("pin_wrong", self._ui_language))
        self._pin_input.clear()
