# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Offscreen tests: the mouse wheel must not change combo/spin box values
# (it used to switch the UI language and write config.json), and the
# wheel is passed on to the surrounding scroll area instead.

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PyQt6.QtCore import QPoint, QPointF, Qt  # noqa: E402
from PyQt6.QtGui import QWheelEvent  # noqa: E402
from PyQt6.QtTest import QTest  # noqa: E402
from PyQt6.QtWidgets import QApplication, QComboBox  # noqa: E402

import config  # noqa: E402
import paths  # noqa: E402
import vocab  # noqa: E402
from gui.panels.settings_panel import SettingsPanel  # noqa: E402
from gui.panels import test_konfigurator_panel as konfigurator  # noqa: E402
from gui.widgets.no_wheel import NoWheelComboBox, NoWheelSpinBox  # noqa: E402
from gui.widgets.number_stepper import NumberStepper  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def instance(app, tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    vocab.save_entries(
        "englisch",
        [{"UUID_A": "a1", "Sprache_A": "Haus", "UUID_B": "b1", "Sprache_B": "house", "Datum": "2026-10-11"}],
    )
    return tmp_path


def _wheel(widget, delta: int = -120) -> QWheelEvent:
    pos = QPointF(widget.width() / 2, widget.height() / 2)
    event = QWheelEvent(
        pos,
        widget.mapToGlobal(pos),
        QPoint(0, 0),
        QPoint(0, delta),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    QApplication.sendEvent(widget, event)
    return event


def test_wheel_over_settings_combos_changes_nothing(instance):
    panel = SettingsPanel()
    panel.show()
    before = config.load_config()
    _wheel(panel._language_combo)
    _wheel(panel._theme_combo)
    after = config.load_config()
    assert panel._language_combo.currentText() == before["language"]
    assert panel._theme_combo.currentText() == before["theme"]
    assert (after["language"], after["theme"]) == (before["language"], before["theme"])


def test_wheel_over_konfigurator_list_and_counts_changes_nothing(instance):
    panel = konfigurator.TestKonfiguratorPanel()
    panel.show()
    count_before = panel.selected_count()
    _wheel(panel._language_combo)
    _wheel(panel._count_spinbox._spinbox)
    _wheel(panel._filter_newest_count_spinbox._spinbox, delta=120)
    assert panel._language_combo.currentText() == "englisch"
    assert panel.selected_count() == count_before


def test_stepper_buttons_still_work(app):
    stepper = NumberStepper()
    stepper.setRange(1, 999)
    stepper.setValue(5)
    stepper._plus.click()
    stepper._plus.click()
    stepper._minus.click()
    assert stepper.value() == 6


def test_arrow_keys_still_work_when_focused(app):
    combo = NoWheelComboBox()
    combo.addItems(["en", "de"])
    combo.show()
    combo.setFocus()
    QTest.keyClick(combo, Qt.Key.Key_Down)
    assert combo.currentText() == "de"

    spin = NoWheelSpinBox()
    spin.setRange(1, 10)
    spin.setValue(3)
    spin.show()
    spin.setFocus()
    QTest.keyClick(spin, Qt.Key.Key_Up)
    assert spin.value() == 4


def test_wheel_event_is_left_unaccepted_for_the_parent(app):
    # An ignored wheel event is handed up to the parent (the scroll area) by
    # Qt for real window-system events. Synthetic sendEvent() calls are not
    # propagated, so the contract that can be tested here is: the field
    # leaves the event unaccepted and keeps its value. (Scrolling itself is
    # checked by hand, see Protokoll.)
    combo = NoWheelComboBox()
    combo.addItems(["en", "de"])
    combo.show()
    event = _wheel(combo, delta=-120)
    assert event.isAccepted() is False
    assert combo.currentText() == "en"

    plain = QComboBox()  # the old behaviour, to show the test can fail
    plain.addItems(["en", "de"])
    plain.show()
    assert _wheel(plain, delta=-120).isAccepted() is True
    assert plain.currentText() == "de"
