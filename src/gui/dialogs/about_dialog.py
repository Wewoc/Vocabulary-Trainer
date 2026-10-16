#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# about_dialog.py
# Vokabeltrainer — "About" window (v0.0.17): app name, version, copyright,
# licence notice and the link to the source code. Display only, no decision
# logic; the texts are constants (version.py) and i18n strings. Self-contained
# widget, knows nothing about who opens it (see the project invariants).
#
# The link is the only place where the app touches the network world, and
# only on a click: the handler opens version.REPO_URL in the browser, never
# the address found in the label (so the label text can't redirect it), and
# never automatically. The text stays selectable so the address can be
# copied if no browser opens.
#
# Four buttons (since v0.0.18) name the shipped documents - README and user
# guide, German and English. A button only says "document X, please":
# document_requested(name) is emitted and whoever opened this window shows
# it (MainWindow -> DocViewerDialog); this dialog knows no viewer. A
# document that is missing makes its button grey instead of failing.

import logging

from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton, QVBoxLayout

import config
import doc_files
import theme
from gui import i18n
from version import APP_NAME, APP_VERSION, COPYRIGHT, REPO_URL

_log = logging.getLogger(__name__)


class AboutDialog(QDialog):
    # name of the document the user asked for (doc_files.DOCUMENTS[...]["name"])
    document_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        cfg = config.load_config()
        ui_language = cfg["language"]
        self.setWindowTitle(i18n.text("about_title", ui_language, name=APP_NAME))

        self._name_label = QLabel(APP_NAME)
        self._name_label.setObjectName("banner_title")  # same accent colour as the banner title
        self._version_label = QLabel(i18n.text("about_version", ui_language, version=APP_VERSION))
        self._copyright_label = QLabel(COPYRIGHT)
        self._license_label = QLabel(i18n.text("about_license", ui_language))
        self._license_label.setWordWrap(True)
        self._source_label = QLabel(i18n.text("about_source", ui_language))

        # The colour sits in the link itself: a palette colour loses against the
        # app stylesheet and the link would stay Qt's default dark blue, which
        # is unreadable on the dark theme.
        accent = theme.colors(cfg["theme"])["accent"]
        self._link_label = QLabel(f'<a href="{REPO_URL}" style="color:{accent}">{REPO_URL}</a>')
        self._link_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self._link_label.setOpenExternalLinks(False)  # our handler opens it, see _open_repo()
        self._link_label.linkActivated.connect(self._open_repo)

        self._docs_label = QLabel(i18n.text("about_docs", ui_language))
        self._doc_buttons = {}
        docs_grid = QGridLayout()
        for index, entry in enumerate(doc_files.DOCUMENTS):
            button = QPushButton(entry["label"])
            if doc_files.doc_path(entry["name"]) is None:
                button.setEnabled(False)
                button.setToolTip(i18n.text("doc_not_found", ui_language, name=entry["name"]))
            button.clicked.connect(lambda _checked=False, name=entry["name"]: self.document_requested.emit(name))
            self._doc_buttons[entry["name"]] = button
            docs_grid.addWidget(button, index // 2, index % 2)

        self._close_button = QPushButton(i18n.text("about_close", ui_language))
        self._close_button.setDefault(True)
        self._close_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self._name_label)
        layout.addWidget(self._version_label)
        layout.addWidget(self._copyright_label)
        layout.addWidget(self._license_label)
        layout.addWidget(self._source_label)
        layout.addWidget(self._link_label)
        layout.addWidget(self._docs_label)
        layout.addLayout(docs_grid)
        layout.addWidget(self._close_button)
        self.setLayout(layout)

    def _open_repo(self, _link: str = "") -> None:
        if QDesktopServices.openUrl(QUrl(REPO_URL)):
            _log.info("repo link opened")
        else:
            _log.warning("could not open repo link")
