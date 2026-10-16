# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Offscreen tests for the PIN gate in MainWindow and PinChangeDialog, with
# a temporary instance directory (never touches the real config.json).

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PyQt6.QtWidgets import QApplication, QDialog  # noqa: E402

import config  # noqa: E402
import paths  # noqa: E402
import pin_store  # noqa: E402
from gui import main_window  # noqa: E402
from gui.dialogs.pin_change_dialog import PinChangeDialog  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def instance(tmp_path, monkeypatch, app):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    return tmp_path


def _fake_prompt(results: list, calls: list):
    class _FakePrompt:
        def __init__(self, check, parent=None):
            calls.append(check)

        def exec(self):
            return results.pop(0)

    return _FakePrompt


def test_gate_rejected_stays_on_test_tab(instance, monkeypatch):
    calls = []
    monkeypatch.setattr(
        main_window, "PinPromptDialog", _fake_prompt([QDialog.DialogCode.Rejected], calls)
    )
    window = main_window.MainWindow()
    window.setCurrentIndex(1)
    assert window.currentIndex() == 0
    assert len(calls) == 1
    assert calls[0] is pin_store.verify_pin


def test_gate_accepted_opens_management_tab_once(instance, monkeypatch):
    calls = []
    monkeypatch.setattr(
        main_window, "PinPromptDialog", _fake_prompt([QDialog.DialogCode.Accepted], calls)
    )
    window = main_window.MainWindow()
    window.setCurrentIndex(1)
    assert window.currentIndex() == 1
    window.setCurrentIndex(0)
    window.setCurrentIndex(1)
    assert window.currentIndex() == 1
    assert len(calls) == 1


def test_gate_asks_again_after_rejection(instance, monkeypatch):
    calls = []
    results = [QDialog.DialogCode.Rejected, QDialog.DialogCode.Accepted]
    monkeypatch.setattr(main_window, "PinPromptDialog", _fake_prompt(results, calls))
    window = main_window.MainWindow()
    window.setCurrentIndex(1)
    assert window.currentIndex() == 0
    window.setCurrentIndex(1)
    assert window.currentIndex() == 1
    assert len(calls) == 2


def _fill(dialog, old, new, repeat):
    dialog._old_input.setText(old)
    dialog._new_input.setText(new)
    dialog._repeat_input.setText(repeat)
    dialog._on_save()


def test_change_dialog_success_writes_hash(instance):
    dialog = PinChangeDialog()
    _fill(dialog, "1234", "secret", "secret")
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert config.load_config()["pin_hash"] is not None
    assert pin_store.verify_pin("secret") is True


@pytest.mark.parametrize(
    "old,new,repeat",
    [("0000", "secret", "secret"), ("1234", "secret", "secreT"), ("1234", "abc", "abc")],
)
def test_change_dialog_errors_write_nothing(instance, old, new, repeat):
    dialog = PinChangeDialog()
    _fill(dialog, old, new, repeat)
    assert dialog._feedback_label.text() != ""
    assert dialog.result() != QDialog.DialogCode.Accepted
    assert config.load_config()["pin_hash"] is None


def test_prompt_dialog_enter_checks_exactly_once(instance):
    from PyQt6.QtCore import Qt
    from PyQt6.QtTest import QTest

    from gui.dialogs.pin_prompt_dialog import PinPromptDialog

    calls = []
    dialog = PinPromptDialog(lambda pin: calls.append(pin) or False)
    dialog.show()
    dialog._pin_input.setFocus()
    QTest.keyClicks(dialog._pin_input, "0000")
    QTest.keyClick(dialog._pin_input, Qt.Key.Key_Return)
    assert calls == ["0000"]
