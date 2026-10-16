# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Offscreen tests for the document viewer (v0.0.18) and for the shipped
# documents themselves: every link and screenshot in the four files must
# lead somewhere, so a renamed heading or file can't silently break them.
# QDesktopServices.openUrl is always replaced, no browser ever opens.

import os
import re
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PyQt6.QtCore import QUrl  # noqa: E402
from PyQt6.QtGui import QDesktopServices, QTextDocument  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

import config  # noqa: E402
import doc_files  # noqa: E402
import paths  # noqa: E402
import theme  # noqa: E402
from gui.dialogs.doc_viewer_dialog import DocViewerDialog  # noqa: E402
from version import REPO_URL  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
NAMES = [d["name"] for d in doc_files.DOCUMENTS]


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def instance(app, tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    return tmp_path


def _spy_open_url(monkeypatch):
    opened = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: opened.append(url.toString()) or True)
    return opened


def _raw(name: str) -> str:
    return doc_files.doc_path(name).read_text(encoding="utf-8")


def _raw_headings(text: str) -> list[str]:
    headings, in_code = [], False
    for line in text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        elif not in_code:
            match = re.match(r"^#{1,6}\s+(.*?)\s*$", line)
            if match:
                headings.append(match.group(1).replace("`", "").replace("*", ""))
    return headings


def _raw_links(text: str) -> list[tuple[bool, str]]:
    """(is_image, target) for every Markdown link, image and <autolink>."""
    found = [(bool(m.group(1)), m.group(2)) for m in re.finditer(r"(!?)\[[^\]]*\]\(([^)\s]+)\)", text)]
    found += [(False, m.group(1)) for m in re.finditer(r"<(https?://[^>]+)>", text)]
    return found


# ---------------------------------------------- the documents themselves

@pytest.mark.parametrize("name", NAMES)
def test_every_link_and_image_in_a_shipped_document_leads_somewhere(name):
    text = _raw(name)
    slugs = doc_files.unique_slugs(_raw_headings(text))
    for is_image, target in _raw_links(text):
        if is_image:
            assert (doc_files.doc_path(name).parent / target).is_file(), f"{name}: missing image {target}"
            continue
        action = doc_files.resolve_link(name, target)
        assert action[0] != "ignore", f"{name}: link {target!r} would do nothing"
        if action[0] == "anchor":
            assert action[1] in slugs, f"{name}: no heading for #{action[1]}"
        elif action[0] == "doc":
            assert doc_files.doc_path(action[1]) is not None, f"{name}: {action[1]} not shipped"
            if action[2]:
                other = doc_files.unique_slugs(_raw_headings(_raw(action[1])))
                assert action[2] in other, f"{name}: no heading for {action[1]}#{action[2]}"
        elif action[0] == "web" and action[1].startswith(f"{REPO_URL}/blob/main/"):
            repo_file = action[1].split("/blob/main/", 1)[1].split("#")[0]
            assert (REPO_ROOT / repo_file).exists(), f"{name}: {repo_file} does not exist in the repository"


# --------------------------------------------------------------- viewer

@pytest.mark.parametrize("name", NAMES)
def test_each_document_renders(instance, name):
    dialog = DocViewerDialog(None, name)
    assert len(dialog._browser.toPlainText()) > 500
    assert dialog.windowTitle() == doc_files.document(name)["label"]
    assert dialog._message_label.isHidden()


@pytest.mark.parametrize("name", ["Bedienungsanleitung.md", "User_Guide.md"])
def test_guides_show_tables_and_every_screenshot(instance, name):
    dialog = DocViewerDialog(None, name)
    document = dialog._browser.document()
    assert len(document.rootFrame().childFrames()) >= 5  # the tables
    images = []
    block = document.begin()
    while block.isValid():
        iterator = block.begin()
        while not iterator.atEnd():
            fmt = iterator.fragment().charFormat()
            if fmt.isImageFormat():
                images.append(fmt.toImageFormat().name())
            iterator += 1
        block = block.next()
    assert len(images) == 6
    for image in images:
        resource = dialog._browser.loadResource(QTextDocument.ResourceType.ImageResource.value, QUrl(image))
        assert resource is not None and not resource.isNull(), image


@pytest.mark.parametrize("name", ["Bedienungsanleitung.md", "User_Guide.md"])
@pytest.mark.parametrize("width", [760, 480])
def test_screenshots_fit_the_window_so_there_is_no_horizontal_scroll(instance, app, name, width):
    dialog = DocViewerDialog(None, name)
    dialog.resize(width, 600)
    dialog.show()
    app.processEvents()
    assert dialog._browser.horizontalScrollBar().maximum() == 0


def test_a_screenshot_keeps_its_proportions_when_scaled(instance, app):
    from PyQt6.QtGui import QImage

    dialog = DocViewerDialog(None, "User_Guide.md")
    dialog.resize(480, 600)
    dialog.show()
    app.processEvents()
    document = dialog._browser.document()
    block = document.begin()
    checked = 0
    while block.isValid():
        iterator = block.begin()
        while not iterator.atEnd():
            fmt = iterator.fragment().charFormat()
            if fmt.isImageFormat():
                image_format = fmt.toImageFormat()
                original = QImage(str(doc_files.doc_path("User_Guide.md").parent / image_format.name()))
                assert 0 < image_format.width() <= original.width()
                assert abs(image_format.height() / image_format.width() - original.height() / original.width()) < 0.01
                checked += 1
            iterator += 1
        block = block.next()
    assert checked == 6


def test_a_missing_document_shows_a_message_instead_of_failing(instance, monkeypatch):
    monkeypatch.setattr(doc_files, "doc_path", lambda name: None)
    dialog = DocViewerDialog(None, "README.md")
    assert not dialog._message_label.isHidden() and "README.md" in dialog._message_label.text()
    assert dialog._browser.toPlainText() == ""


def test_links_are_drawn_in_the_theme_colour_in_every_theme(instance, app):
    # Qt's own link blue loses on dark themes; look at the painted pixels.
    cfg = config.load_config()
    try:
        for theme_name in theme.theme_names():
            cfg["theme"] = theme_name
            config.save_config(cfg)
            app.setStyleSheet(theme.stylesheet(theme_name))
            dialog = DocViewerDialog(None, "Bedienungsanleitung.md")
            dialog.show()
            app.processEvents()
            image = dialog._browser.viewport().grab().toImage()
            painted = {image.pixelColor(x, y).name() for x in range(image.width()) for y in range(image.height())}
            assert theme.colors(theme_name)["accent"].lower() in painted, theme_name
            assert "#0000ff" not in painted, theme_name
            dialog.close()
    finally:
        app.setStyleSheet("")


def test_the_dialog_text_is_selectable_for_copying_the_prompt(instance):
    from PyQt6.QtCore import Qt

    dialog = DocViewerDialog(None, "User_Guide.md")  # keep a reference, Qt deletes the child otherwise
    flags = dialog._browser.textInteractionFlags()
    assert flags & Qt.TextInteractionFlag.TextSelectableByMouse


# ----------------------------------------------------------- link clicks

def test_a_link_to_another_shipped_document_switches_the_view(instance, monkeypatch):
    opened = _spy_open_url(monkeypatch)
    dialog = DocViewerDialog(None, "README.md")
    dialog._on_link(QUrl("README.de.md"))
    assert dialog.current_name == "README.de.md" and dialog.windowTitle() == "README (Deutsch)"
    dialog._on_link(QUrl("docs/User_Guide.md"))
    assert dialog.current_name == "User_Guide.md"
    assert opened == []


def test_a_project_web_link_opens_the_browser_and_others_do_not(instance, monkeypatch):
    opened = _spy_open_url(monkeypatch)
    dialog = DocViewerDialog(None, "README.md")
    dialog._on_link(QUrl("https://github.com/Wewoc/Vocabulary-Trainer/issues"))
    dialog._on_link(QUrl("https://example.com/"))
    dialog._on_link(QUrl("mailto:someone@example.com"))
    assert opened == ["https://github.com/Wewoc/Vocabulary-Trainer/issues"]


def test_a_link_to_a_file_that_is_not_shipped_opens_it_on_github(instance, monkeypatch):
    opened = _spy_open_url(monkeypatch)
    dialog = DocViewerDialog(None, "README.md")
    dialog._on_link(QUrl("docs/DEVELOPMENT.md"))
    assert opened == [f"{REPO_URL}/blob/main/docs/DEVELOPMENT.md"]


def test_nothing_opens_without_a_click(instance, monkeypatch):
    opened = _spy_open_url(monkeypatch)
    DocViewerDialog(None, "README.md")
    assert opened == []


@pytest.mark.parametrize("name", ["Bedienungsanleitung.md", "User_Guide.md"])
def test_every_table_of_contents_link_scrolls_to_its_heading(instance, app, name):
    dialog = DocViewerDialog(None, name)
    dialog.show()
    app.processEvents()
    targets = [t for _, t in _raw_links(_raw(name)) if t.startswith("#")]
    assert len(targets) >= 12
    for target in targets:
        assert dialog._scroll_to(target[1:]), target


def test_a_contents_link_moves_the_view_and_an_unknown_one_does_not(instance, app):
    dialog = DocViewerDialog(None, "Bedienungsanleitung.md")
    dialog.show()
    app.processEvents()
    bar = dialog._browser.verticalScrollBar()
    assert bar.value() == 0
    dialog._on_link(QUrl("#10-pin-datenschutz-und-sicherheit"))
    moved = bar.value()
    assert moved > 0
    dialog._on_link(QUrl("#gibt-es-nicht"))
    assert bar.value() == moved
