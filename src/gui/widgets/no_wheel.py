#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# no_wheel.py
# Vokabeltrainer — combo box and spin box that ignore the mouse wheel.
# By default Qt changes the value of these fields on a wheel turn, even
# when the user only wants to scroll the page they sit on: one wheel
# notch over the language field switched en -> de and wrote config.json
# immediately (found in v0.0.10.11 testing). Ignoring the event hands it to
# the parent, so the surrounding scroll area scrolls instead. StrongFocus
# keeps the wheel from grabbing focus; Tab, click and arrow keys work as
# before. Small input building blocks, not panels: no knowledge of their
# placement.

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QSpinBox


class NoWheelComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event) -> None:
        event.ignore()


class NoWheelSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event) -> None:
        event.ignore()
