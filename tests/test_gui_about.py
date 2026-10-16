# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Offscreen tests for the About window (v0.0.17): what it shows, and that a
# click on the link opens exactly version.REPO_URL. QDesktopServices.openUrl
# is always replaced, so no browser ever opens.

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PyQt6.QtCore import Qt  # noqa: E402
from PyQt6.QtGui import QDesktopServices  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

import config  # noqa: E402
import paths  # noqa: E402
import theme  # noqa: E402
import version  # noqa: E402
from gui import i18n  # noqa: E402
from gui.dialogs.about_dialog import AboutDialog  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def instance(app, tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    return tmp_path


def _spy_open_url(monkeypatch, result=True):
    opened = []

    def fake_open(url):
        opened.append(url.toString())
        return result

    monkeypatch.setattr(QDesktopServices, "openUrl", fake_open)
    return opened


def test_constants_name_the_renamed_repository():
    assert version.APP_NAME == "Vocabulary-Trainer"
    assert version.REPO_URL == "https://github.com/Wewoc/Vocabulary-Trainer"
    assert version.COPYRIGHT.startswith("Copyright (C) 2026")


def test_dialog_shows_name_version_copyright_and_licence(instance):
    dialog = AboutDialog()
    assert dialog._name_label.text() == version.APP_NAME
    assert version.APP_VERSION in dialog._version_label.text()
    assert dialog._copyright_label.text() == version.COPYRIGHT
    assert "GPL-3.0-or-later" in dialog._license_label.text()
    assert version.APP_NAME in dialog.windowTitle()


def test_dialog_shows_the_link_as_selectable_text(instance):
    dialog = AboutDialog()
    assert version.REPO_URL in dialog._link_label.text()
    flags = dialog._link_label.textInteractionFlags()
    assert flags & Qt.TextInteractionFlag.TextSelectableByMouse
    assert not dialog._link_label.openExternalLinks()  # our handler opens it, not Qt


def test_link_is_drawn_in_the_theme_colour(instance, app):
    # Looks at the painted pixels with the app stylesheet applied: a palette
    # colour alone loses against the stylesheet and the link stays Qt's blue.
    cfg = config.load_config()
    try:
        for name in theme.theme_names():
            cfg["theme"] = name
            config.save_config(cfg)
            app.setStyleSheet(theme.stylesheet(name))
            dialog = AboutDialog()  # keep a reference, Qt deletes the child label otherwise
            dialog.show()
            app.processEvents()
            image = dialog._link_label.grab().toImage()
            accent = theme.colors(name)["accent"].lower()
            painted = {image.pixelColor(x, y).name() for x in range(image.width()) for y in range(image.height())}
            assert accent in painted, name
            assert "#0000ff" not in painted, name
            dialog.close()
    finally:
        app.setStyleSheet("")


def test_clicking_the_link_opens_exactly_the_repo_url(instance, monkeypatch):
    opened = _spy_open_url(monkeypatch)
    dialog = AboutDialog()
    dialog._link_label.linkActivated.emit(version.REPO_URL)
    assert opened == [version.REPO_URL]


def test_the_address_in_the_label_cannot_redirect_the_click(instance, monkeypatch):
    opened = _spy_open_url(monkeypatch)
    dialog = AboutDialog()
    dialog._link_label.linkActivated.emit("https://evil.example/")
    assert opened == [version.REPO_URL]


def test_nothing_is_opened_without_a_click(instance, monkeypatch):
    opened = _spy_open_url(monkeypatch)
    AboutDialog()
    assert opened == []


def test_a_failing_browser_does_not_raise(instance, monkeypatch):
    opened = _spy_open_url(monkeypatch, result=False)
    AboutDialog()._open_repo()
    assert opened == [version.REPO_URL]


def test_texts_exist_in_both_languages():
    for key in ["about_button", "about_title", "about_version", "about_license", "about_source", "about_close"]:
        for language in ("de", "en"):
            text = i18n.text(key, language, name="X", version="1")
            assert text and text != key


def test_close_button_closes_the_dialog(instance):
    dialog = AboutDialog()
    dialog.show()
    assert dialog.isVisible()
    dialog._close_button.click()
    assert not dialog.isVisible()


# ------------------------------------------------- button in the main window

def _main_window(monkeypatch):
    from gui import main_window

    shown = []
    created = []

    class _Signal:
        def __init__(self):
            self.slots = []

        def connect(self, slot):
            self.slots.append(slot)

        def emit(self, *args):
            for slot in self.slots:
                slot(*args)

    class _FakeAbout:
        def __init__(self, parent=None):
            shown.append(parent)
            self.document_requested = _Signal()
            created.append(self)

        def exec(self):
            return 0

    monkeypatch.setattr(main_window, "AboutDialog", _FakeAbout)
    window = main_window.MainWindow()
    window._fake_dialogs = created  # for the tests below
    return window, shown


def test_main_window_has_an_info_button_in_the_tab_bar_corner(instance, monkeypatch):
    window, _ = _main_window(monkeypatch)
    assert window._about_button.text() == i18n.text("about_button", config.load_config()["language"])
    assert window.cornerWidget(Qt.Corner.TopRightCorner) is window._about_button


def test_clicking_info_opens_the_about_window_without_a_pin(instance, monkeypatch):
    from gui import main_window

    pin_asked = []
    monkeypatch.setattr(
        main_window, "PinPromptDialog", lambda *a, **k: pin_asked.append(1) or (_ for _ in ()).throw(AssertionError)
    )
    window, shown = _main_window(monkeypatch)
    window._about_button.click()
    assert shown == [window] and pin_asked == []


def test_info_button_stays_visible_at_the_minimum_window_size(instance, app, monkeypatch):
    window, _ = _main_window(monkeypatch)
    try:
        for name in theme.theme_names():
            app.setStyleSheet(theme.stylesheet(name))
            window.resize(window.minimumSize())
            window.show()
            app.processEvents()
            button = window._about_button.geometry()
            assert button.right() <= window.width(), name
            assert button.left() >= window.tabBar().geometry().right(), name  # not on top of the tabs
    finally:
        app.setStyleSheet("")
        window.close()


def test_the_real_about_dialog_opens_from_the_button(instance, monkeypatch):
    from gui import main_window

    opened = []
    monkeypatch.setattr(AboutDialog, "exec", lambda self: opened.append(self.windowTitle()) or 0)
    window = main_window.MainWindow()
    window._about_button.click()
    assert len(opened) == 1 and version.APP_NAME in opened[0]


# ----------------------------------------------- shipped documents (v0.0.18)

def test_about_window_has_four_document_buttons_in_a_fixed_order(instance):
    import doc_files

    dialog = AboutDialog()
    names = list(dialog._doc_buttons)
    assert names == [d["name"] for d in doc_files.DOCUMENTS]
    assert [dialog._doc_buttons[n].text() for n in names] == [
        "README (Deutsch)", "README (English)", "Anleitung (Deutsch)", "User Guide (English)",
    ]
    assert all(button.isEnabled() for button in dialog._doc_buttons.values())  # from source: all present


def test_button_labels_do_not_depend_on_the_app_language(instance):
    cfg = config.load_config()
    labels = {}
    for language in ("de", "en"):
        cfg["language"] = language
        config.save_config(cfg)
        dialog = AboutDialog()
        labels[language] = [b.text() for b in dialog._doc_buttons.values()]
    assert labels["de"] == labels["en"]


def test_clicking_a_document_button_asks_for_that_document(instance):
    dialog = AboutDialog()
    asked = []
    dialog.document_requested.connect(asked.append)
    dialog._doc_buttons["User_Guide.md"].click()
    dialog._doc_buttons["README.de.md"].click()
    assert asked == ["User_Guide.md", "README.de.md"]


def test_a_missing_document_makes_its_button_grey_with_a_hint(instance, monkeypatch):
    import doc_files

    real = doc_files.doc_path
    monkeypatch.setattr(doc_files, "doc_path", lambda name: None if name == "User_Guide.md" else real(name))
    dialog = AboutDialog()
    missing = dialog._doc_buttons["User_Guide.md"]
    assert not missing.isEnabled() and "User_Guide.md" in missing.toolTip()
    assert dialog._doc_buttons["README.md"].isEnabled()
    asked = []
    dialog.document_requested.connect(asked.append)
    missing.click()  # a disabled button does nothing
    assert asked == []


def test_the_about_window_itself_opens_no_viewer_and_no_browser(instance, monkeypatch):
    opened = _spy_open_url(monkeypatch)
    AboutDialog()
    assert opened == []


def test_main_window_shows_the_requested_document_in_the_viewer(instance, monkeypatch):
    from gui import main_window

    viewers = []

    class _FakeViewer:
        def __init__(self, parent, name):
            viewers.append((parent, name))

        def exec(self):
            return 0

    monkeypatch.setattr(main_window, "DocViewerDialog", _FakeViewer)
    window, _ = _main_window(monkeypatch)
    window._about_button.click()
    window._fake_dialogs[0].document_requested.emit("User_Guide.md")
    assert viewers == [(window, "User_Guide.md")]


def test_the_real_chain_button_to_viewer_works(instance, monkeypatch):
    from gui import main_window
    from gui.dialogs.doc_viewer_dialog import DocViewerDialog

    shown = []
    monkeypatch.setattr(
        DocViewerDialog, "exec", lambda self: shown.append((self.current_name, self.windowTitle())) or 0
    )

    def about_exec(self):
        self._doc_buttons["README.de.md"].click()
        return 0

    monkeypatch.setattr(AboutDialog, "exec", about_exec)
    window = main_window.MainWindow()
    window._about_button.click()
    assert shown == [("README.de.md", "README (Deutsch)")]
