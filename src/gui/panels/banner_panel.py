#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# banner_panel.py
# Vokabeltrainer — Test-tab banner: title + subtitle as plain text (with
# emoji), framed like the Test-Konfigurator. Text instead of an image so
# it follows the DE/EN switch (gui/i18n.py) and the theme colors
# (theme.py, via objectName) without extra assets. Self-contained widget,
# knows nothing about its own placement on a page. Title is a QLabel
# inside the frame, not a QGroupBox title (see the project invariants).

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QGroupBox, QLabel, QVBoxLayout

import config
from gui import i18n

_TITLE_POINT_SIZE = 24
_SUBTITLE_POINT_SIZE = 11


class BannerPanel(QGroupBox):
    def __init__(self):
        super().__init__()
        ui_language = config.load_config()["language"]

        title = QLabel(i18n.text("banner_title", ui_language))
        title.setObjectName("banner_title")
        title_font = QFont(title.font())
        title_font.setPointSize(_TITLE_POINT_SIZE)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel(i18n.text("banner_subtitle", ui_language))
        subtitle.setObjectName("banner_subtitle")
        subtitle_font = QFont(subtitle.font())
        subtitle_font.setPointSize(_SUBTITLE_POINT_SIZE)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        self.setLayout(layout)
