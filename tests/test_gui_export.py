# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Offscreen tests for the export area of DataExchangePanel (v0.0.12):
# ticked items become separate files in a chosen folder.

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PyQt6.QtCore import QUrl  # noqa: E402
from PyQt6.QtGui import QDesktopServices  # noqa: E402
from PyQt6.QtWidgets import QApplication, QFileDialog  # noqa: E402

import paths  # noqa: E402
import tracking  # noqa: E402
import vocab  # noqa: E402
from gui.panels import data_exchange_panel  # noqa: E402
from gui.panels.data_exchange_panel import DataExchangePanel  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def opened_folders(monkeypatch):
    """Records the folders the export tries to open - and keeps every test
    from starting a real file manager window."""
    opened = []

    def fake_open(url: QUrl) -> bool:
        opened.append(Path(url.toLocalFile()))
        return True

    monkeypatch.setattr(QDesktopServices, "openUrl", fake_open)
    return opened


@pytest.fixture
def panel(app, tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path / "instance")
    vocab.save_entries(
        "englisch",
        [{"UUID_A": "u1", "Sprache_A": "Haus", "UUID_B": "u2", "Sprache_B": "house", "Datum": "2026-10-11"}],
    )
    data = tracking.load_tracking()
    data["vocab_stats"]["u1"] = {
        "correct_count": 1,
        "wrong_count": 1,
        "alt_count": 0,
        "last_tested": "2026-10-11T10:00:00",
        "history": [{"ts": "2026-10-11T10:00:00", "outcome": "wrong"}],
    }
    tracking.record_session(data, "2026-10-11T10:00:00", "2026-10-11T10:02:00", True)
    tracking.save_tracking(data)
    return DataExchangePanel("englisch")


def _choose_folder(monkeypatch, folder):
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: str(folder))


def _files(folder: Path) -> list[str]:
    return sorted(p.name for p in folder.iterdir())


def test_both_ticked_writes_two_files(panel, tmp_path, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    _choose_folder(monkeypatch, out)
    panel._on_export()
    names = _files(out)
    assert len(names) == 2
    assert any(n.startswith("wortliste_englisch_") for n in names)
    assert any(n.startswith("report_") for n in names)
    assert "2" in panel._feedback_label.text()


def test_only_wordlist(panel, tmp_path, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    _choose_folder(monkeypatch, out)
    panel._export_report_check.setChecked(False)
    panel._on_export()
    assert [n.split("_")[0] for n in _files(out)] == ["wortliste"]


def test_only_report_has_the_overall_and_per_word_sections(panel, tmp_path, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    _choose_folder(monkeypatch, out)
    panel._export_wordlist_check.setChecked(False)
    panel._on_export()
    (report_file,) = list(out.iterdir())
    text = report_file.read_text(encoding="utf-8-sig")
    assert report_file.name.startswith("report_")
    assert "Haus" in text  # the clear-text word is in the parent report on purpose
    assert text.count("\n\n") >= 1 or "\r\n\r\n" in text  # blank row between the sections


def test_nothing_ticked_shows_a_hint_and_writes_nothing(panel, tmp_path, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    calls = []
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: calls.append(1) or str(out))
    panel._export_wordlist_check.setChecked(False)
    panel._export_report_check.setChecked(False)
    panel._on_export()
    assert calls == []  # no dialog at all
    assert _files(out) == []
    assert panel._feedback_label.text() != ""


def test_cancelled_dialog_writes_nothing(panel, tmp_path, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: "")
    panel._feedback_label.setText("untouched")
    panel._on_export()
    assert panel._feedback_label.text() == "untouched"


def test_write_error_is_reported_not_raised(panel, tmp_path, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    _choose_folder(monkeypatch, out)

    def boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(data_exchange_panel.csv_io, "write_csv_file", boom)
    panel._on_export()  # must not raise
    assert panel._feedback_label.text() != ""
    assert _files(out) == []


def test_successful_export_opens_the_folder_once(panel, tmp_path, monkeypatch, opened_folders):
    out = tmp_path / "out"
    out.mkdir()
    _choose_folder(monkeypatch, out)
    panel._on_export()  # word list and report
    assert opened_folders == [out]


def test_each_single_export_opens_the_folder(panel, tmp_path, monkeypatch, opened_folders):
    out = tmp_path / "out"
    out.mkdir()
    _choose_folder(monkeypatch, out)
    panel._export_report_check.setChecked(False)
    panel._on_export()  # word list only
    panel._export_report_check.setChecked(True)
    panel._export_wordlist_check.setChecked(False)
    panel._on_export()  # report only
    assert opened_folders == [out, out]


def test_nothing_is_opened_without_a_successful_export(panel, tmp_path, monkeypatch, opened_folders):
    out = tmp_path / "out"
    out.mkdir()

    # nothing ticked
    _choose_folder(monkeypatch, out)
    panel._export_wordlist_check.setChecked(False)
    panel._export_report_check.setChecked(False)
    panel._on_export()

    # dialog cancelled
    panel._export_wordlist_check.setChecked(True)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: "")
    panel._on_export()

    # write error
    _choose_folder(monkeypatch, out)

    def boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(data_exchange_panel.csv_io, "write_csv_file", boom)
    panel._on_export()

    assert opened_folders == []


def test_failing_folder_open_keeps_the_success_message(panel, tmp_path, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    _choose_folder(monkeypatch, out)
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: False)
    panel._on_export()  # must not raise
    assert "2" in panel._feedback_label.text()
    assert len(_files(out)) == 2
