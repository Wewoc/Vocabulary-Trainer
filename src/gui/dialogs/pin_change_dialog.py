#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# pin_change_dialog.py
# Vokabeltrainer — change the parent PIN (requirements 7.1): old PIN, new
# PIN, repeat. Holds no decision logic: everything is checked inside
# pin_store.change_pin(); this dialog only maps its result to a message
# and closes on success. Self-contained widget, knows nothing about who
# opens it (see the project invariants).

from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

import config
import pin_store
from gui import i18n

_RESULT_MESSAGE_KEYS = {
    pin_store.RESULT_WRONG_PIN: "pin_wrong",
    pin_store.RESULT_MISMATCH: "pin_mismatch",
    pin_store.RESULT_TOO_SHORT: "pin_too_short",
}


def _password_field() -> QLineEdit:
    field = QLineEdit()
    field.setEchoMode(QLineEdit.EchoMode.Password)
    return field


class PinChangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui_language = config.load_config()["language"]
        self.setWindowTitle(i18n.text("pin_change_title", self._ui_language))

        self._old_input = _password_field()
        self._new_input = _password_field()
        self._repeat_input = _password_field()
        self._feedback_label = QLabel()

        form = QFormLayout()
        form.addRow(i18n.text("pin_old_label", self._ui_language), self._old_input)
        form.addRow(i18n.text("pin_new_label", self._ui_language), self._new_input)
        form.addRow(i18n.text("pin_repeat_label", self._ui_language), self._repeat_input)

        self._save_button = QPushButton(i18n.text("save", self._ui_language))
        self._save_button.clicked.connect(self._on_save)
        self._cancel_button = QPushButton(i18n.text("cancel", self._ui_language))
        self._cancel_button.clicked.connect(self.reject)

        button_row = QHBoxLayout()
        button_row.addWidget(self._save_button)
        button_row.addWidget(self._cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self._feedback_label)
        layout.addLayout(button_row)
        self.setLayout(layout)

    def _on_save(self) -> None:
        result = pin_store.change_pin(
            self._old_input.text(), self._new_input.text(), self._repeat_input.text()
        )
        if result == pin_store.RESULT_OK:
            self.accept()
            return
        self._feedback_label.setText(i18n.text(_RESULT_MESSAGE_KEYS[result], self._ui_language))
