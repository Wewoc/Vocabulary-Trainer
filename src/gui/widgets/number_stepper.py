#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# number_stepper.py
# Vokabeltrainer — number field with separate "+" / "-" buttons next to
# it, instead of QSpinBox's built-in arrow buttons. Under the theme
# stylesheet the built-in buttons are laid out by Qt's own guess of the
# style's button width, which lets the inner QLineEdit overlap the "up"
# button: real mouse clicks land on the line edit, so "up" did nothing
# (see the project invariants). Plain QPushButtons
# take their look from the existing QPushButton theme rule - no extra
# colors or assets. Small input building block, not a panel: knows
# nothing about its placement, and sizes only its own buttons.
#
# Exposes the subset of QSpinBox that callers use (setRange, setValue,
# value) so a caller can swap QSpinBox -> NumberStepper unchanged.

from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QSpinBox, QWidget

from gui.widgets.no_wheel import NoWheelSpinBox

_BUTTON_WIDTH = 28


class NumberStepper(QWidget):
    def __init__(self):
        super().__init__()
        self._spinbox = NoWheelSpinBox()
        self._spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self._plus = QPushButton("+")
        self._plus.setFixedWidth(_BUTTON_WIDTH)
        self._plus.clicked.connect(self._spinbox.stepUp)
        self._minus = QPushButton("−")
        self._minus.setFixedWidth(_BUTTON_WIDTH)
        self._minus.clicked.connect(self._spinbox.stepDown)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._spinbox, 1)
        layout.addWidget(self._plus)
        layout.addWidget(self._minus)
        self.setLayout(layout)

    def setRange(self, minimum: int, maximum: int) -> None:
        self._spinbox.setRange(minimum, maximum)

    def setValue(self, value: int) -> None:
        self._spinbox.setValue(value)

    def value(self) -> int:
        return self._spinbox.value()
