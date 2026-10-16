# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Offscreen tests for the event-driven refresh (v0.0.11): status panel
# after a session, language list after vocab changes.

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PyQt6.QtWidgets import QApplication, QMessageBox  # noqa: E402

import paths  # noqa: E402
import tracking  # noqa: E402
import vocab  # noqa: E402
from gui import main_window  # noqa: E402
from gui.pages import management_tab as management_module  # noqa: E402
from gui.pages import test_tab as test_tab_module  # noqa: E402
from gui.panels import test_konfigurator_panel as konfigurator  # noqa: E402
from gui.panels import vocab_table_panel  # noqa: E402
from gui.panels.status_panel import StatusPanel  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def instance(app, tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    return tmp_path


def _entry(i: int) -> dict:
    return {"UUID_A": f"a{i}", "Sprache_A": f"wort{i}", "UUID_B": f"b{i}", "Sprache_B": f"word{i}", "Datum": "2026-10-11"}


def _write_completed_session():
    data = tracking.load_tracking()
    tracking.record_session(data, "2026-10-11T10:00:00", "2026-10-11T10:05:00", True)
    tracking.save_tracking(data)


def test_status_panel_refresh_shows_the_new_session(instance):
    panel = StatusPanel()
    before = panel._labels[0].text()
    assert before.endswith("0")
    _write_completed_session()
    assert panel._labels[0].text() == before  # nothing changes by itself
    panel.refresh()
    assert panel._labels[0].text().endswith("1")


def test_refresh_languages_fills_the_empty_field(instance):
    panel = konfigurator.TestKonfiguratorPanel()
    assert panel.selected_language() is None
    vocab.save_entries("englisch", [_entry(1)])
    panel.refresh_languages()
    assert panel.selected_language() == "englisch"


def test_refresh_languages_keeps_the_current_choice(instance):
    vocab.save_entries("englisch", [_entry(1)])
    vocab.save_entries("spanisch", [_entry(2)])
    panel = konfigurator.TestKonfiguratorPanel()
    panel._language_combo.setCurrentText("spanisch")
    vocab.save_entries("franzoesisch", [_entry(3)])
    panel.refresh_languages()
    assert panel.selected_language() == "spanisch"


def test_refresh_languages_falls_back_when_the_choice_is_gone(instance):
    vocab.save_entries("englisch", [_entry(1)])
    vocab.save_entries("spanisch", [_entry(2)])
    panel = konfigurator.TestKonfiguratorPanel()
    panel._language_combo.setCurrentText("spanisch")
    (instance / "daten" / "vokabeln" / "spanisch.csv").unlink()
    panel.refresh_languages()
    assert panel.selected_language() == "englisch"


def test_refresh_languages_leaves_other_settings_alone(instance):
    vocab.save_entries("englisch", [_entry(1)])
    panel = konfigurator.TestKonfiguratorPanel()
    panel._count_spinbox.setValue(7)
    panel._direction_b_to_a.setChecked(True)
    panel.refresh_languages()
    assert panel.selected_count() == 7
    assert panel.selected_direction() == "B->A"


def _count(signal) -> list:
    calls = []
    signal.connect(lambda: calls.append(1))
    return calls


def test_management_tab_collects_every_vocab_change(instance, monkeypatch):
    vocab.save_entries("englisch", [_entry(1), _entry(2)])
    tab = management_module.ManagementTab()
    calls = _count(tab.vocab_changed)

    tab._direct_entry.word_added.emit()
    tab._data_exchange.vocab_changed.emit()
    assert len(calls) == 2

    class _AcceptingDialog:
        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            return 1

    monkeypatch.setattr(vocab_table_panel, "EditEntryDialog", _AcceptingDialog)
    tab._vocab_table._table.selectRow(0)
    tab._vocab_table._on_edit()
    assert len(calls) == 3

    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)
    tab._vocab_table._table.selectRow(0)
    tab._vocab_table._on_delete()
    assert len(calls) == 4


def test_cancelled_edit_does_not_signal(instance, monkeypatch):
    vocab.save_entries("englisch", [_entry(1)])
    tab = management_module.ManagementTab()
    calls = _count(tab.vocab_changed)

    class _RejectingDialog:
        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            return 0

    monkeypatch.setattr(vocab_table_panel, "EditEntryDialog", _RejectingDialog)
    tab._vocab_table._table.selectRow(0)
    tab._vocab_table._on_edit()
    assert calls == []


def test_main_window_refreshes_the_test_tab_after_a_vocab_change(instance):
    window = main_window.MainWindow()
    assert window._test_tab._konfigurator.selected_language() is None
    vocab.save_entries("englisch", [_entry(1)])
    window._management_tab.vocab_changed.emit()
    assert window._test_tab._konfigurator.selected_language() == "englisch"


def test_test_tab_refreshes_the_status_after_a_session(instance, monkeypatch):
    class _FakeQuizDialog:
        def __init__(self, parent=None, **kwargs):
            pass

        def exec(self):
            _write_completed_session()  # what QuizPanel does when a session ends

    monkeypatch.setattr(test_tab_module, "QuizDialog", _FakeQuizDialog)
    tab = test_tab_module.TestTab()
    assert tab._status._labels[0].text().endswith("0")
    tab._on_start()
    assert tab._status._labels[0].text().endswith("1")
