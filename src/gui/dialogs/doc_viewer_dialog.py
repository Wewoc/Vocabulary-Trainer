#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# doc_viewer_dialog.py
# Vokabeltrainer — shows one of the shipped documents (README, user guide;
# v0.0.18) inside the app: Markdown rendered by Qt, tables and screenshots
# included, text selectable (the AI prompt can be copied). No decision
# logic: which file, and what a click on a link does, is doc_files.py's job
# (resolve_link); this dialog only carries it out.
#
# Qt colours links in its own blue regardless of the stylesheet and makes no
# anchors for headings, so after loading every link is coloured with the
# theme's accent colour and "#section" links are scrolled to by heading text
# (doc_files.heading_slug). Screenshots are scaled down to the window width
# (again on every resize), otherwise the page would get a horizontal scroll
# bar. A click on a web link opens the browser - the only way this window
# touches the network, and only for project pages.

import logging

from PyQt6.QtCore import QEvent, QUrl
from PyQt6.QtGui import QBrush, QColor, QDesktopServices, QImage, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QTextBrowser, QVBoxLayout

import config
import doc_files
import theme
from gui import i18n

_log = logging.getLogger(__name__)


class DocViewerDialog(QDialog):
    def __init__(self, parent, name: str):
        super().__init__(parent)
        cfg = config.load_config()
        self._ui_language = cfg["language"]
        self._accent = theme.colors(cfg["theme"])["accent"]
        self._name = name
        self._doc_dir = None
        self._fitting = False

        self._message_label = QLabel()
        self._message_label.setWordWrap(True)
        self._browser = QTextBrowser()
        self._browser.setOpenLinks(False)  # every click goes through _on_link()
        self._browser.anchorClicked.connect(self._on_link)
        self._browser.viewport().installEventFilter(self)  # re-fit screenshots when it is resized

        self._close_button = QPushButton(i18n.text("doc_close", self._ui_language))
        self._close_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self._message_label)
        layout.addWidget(self._browser, 1)
        layout.addWidget(self._close_button)
        self.setLayout(layout)
        self.resize(760, 640)
        self._show_document(name)

    @property
    def current_name(self) -> str:
        return self._name

    def _show_document(self, name: str, fragment: str = "") -> None:
        entry = doc_files.document(name)
        path = doc_files.doc_path(name)
        if entry is None or path is None:
            self._message_label.setText(i18n.text("doc_not_found", self._ui_language, name=name))
            self._message_label.setVisible(True)
            self._browser.clear()
            return
        self._name = name
        self._doc_dir = path.parent
        self._message_label.setVisible(False)
        self.setWindowTitle(entry["label"])
        self._browser.setSearchPaths([str(path.parent)])  # screenshots: bilder/...
        self._browser.setMarkdown(path.read_text(encoding="utf-8"))
        self._colour_links()
        self._fit_images()
        self._browser.verticalScrollBar().setValue(0)
        if fragment:
            self._scroll_to(fragment)
        _log.info("doc opened name=%s", name)

    def _colour_links(self) -> None:
        document = self._browser.document()
        ranges = []
        block = document.begin()
        while block.isValid():
            iterator = block.begin()
            while not iterator.atEnd():
                fragment = iterator.fragment()
                if fragment.charFormat().isAnchor():
                    ranges.append((fragment.position(), fragment.position() + fragment.length()))
                iterator += 1
            block = block.next()
        cursor = QTextCursor(document)
        for start, end in ranges:
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            char_format = QTextCharFormat()
            char_format.setForeground(QBrush(QColor(self._accent)))
            cursor.mergeCharFormat(char_format)

    def _fit_images(self) -> None:
        if self._doc_dir is None or self._fitting:
            return
        self._fitting = True
        try:
            self._scale_images()
        finally:
            self._fitting = False

    def _scale_images(self) -> None:
        document = self._browser.document()
        # the vertical scroll bar takes room once the page is long, so keep it free
        bar = self._browser.verticalScrollBar()
        reserve = 0 if bar.isVisible() else bar.sizeHint().width()
        available = self._browser.viewport().width() - reserve - 2 * int(document.documentMargin()) - 4
        found = []
        block = document.begin()
        while block.isValid():
            iterator = block.begin()
            while not iterator.atEnd():
                fragment = iterator.fragment()
                if fragment.charFormat().isImageFormat():
                    found.append((fragment.position(), fragment.length(), fragment.charFormat().toImageFormat()))
                iterator += 1
            block = block.next()
        cursor = QTextCursor(document)
        for position, length, image_format in found:
            image = QImage(str(self._doc_dir / image_format.name()))
            if image.isNull() or available <= 0:
                continue
            width = min(image.width(), available)
            image_format.setWidth(width)
            image_format.setHeight(round(image.height() * width / image.width()))
            cursor.setPosition(position)
            cursor.setPosition(position + length, QTextCursor.MoveMode.KeepAnchor)
            cursor.setCharFormat(image_format)

    def eventFilter(self, watched, event) -> bool:
        if watched is self._browser.viewport() and event.type() == QEvent.Type.Resize:
            self._fit_images()
        return super().eventFilter(watched, event)

    def _headings(self) -> list:
        blocks = []
        block = self._browser.document().begin()
        while block.isValid():
            if block.blockFormat().headingLevel() > 0:
                blocks.append(block)
            block = block.next()
        return blocks

    def _scroll_to(self, fragment: str) -> bool:
        blocks = self._headings()
        slugs = doc_files.unique_slugs([b.text() for b in blocks])
        if fragment not in slugs:
            return False
        block = blocks[slugs.index(fragment)]
        top = self._browser.document().documentLayout().blockBoundingRect(block).top()
        self._browser.verticalScrollBar().setValue(int(top))
        return True

    def _on_link(self, url: QUrl) -> None:
        link = url.toString(QUrl.ComponentFormattingOption.FullyDecoded)
        action = doc_files.resolve_link(self._name, link)
        if action[0] == "anchor":
            self._scroll_to(action[1])
        elif action[0] == "doc":
            self._show_document(action[1], action[2])
        elif action[0] == "web":
            if QDesktopServices.openUrl(QUrl(action[1])):
                _log.info("doc link opened")
            else:
                _log.warning("could not open doc link")
        else:
            _log.info("doc link ignored")
