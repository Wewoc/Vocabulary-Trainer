# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Offscreen tests for the import preview (v0.0.13): the dialog itself and
# its use by DataExchangePanel (file dialog replaced, preview dialog
# answered by the test).

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PyQt6.QtWidgets import QApplication, QDialog, QFileDialog  # noqa: E402

import paths  # noqa: E402
import vocab  # noqa: E402
from gui.dialogs.import_preview_dialog import ImportPreviewDialog  # noqa: E402
from gui.panels import data_exchange_panel  # noqa: E402
from gui.panels.data_exchange_panel import DataExchangePanel  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def instance(app, tmp_path, monkeypatch):
    (tmp_path / "instance").mkdir()  # config.json is written there on first load
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path / "instance")
    return tmp_path


def _csv(tmp_path, lines: list[str]) -> Path:
    path = tmp_path / "import.csv"
    path.write_text("\n".join(["Sprache_A,Sprache_B", *lines]) + "\n", encoding="utf-8-sig")
    return path


def _pick(monkeypatch, path: Path):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(path), ""))


def _answer_preview(monkeypatch, result):
    """Replaces the preview's exec(); returns the list of plans it was shown."""
    shown = []

    def fake_exec(self):
        shown.append(self._plan)
        return result

    monkeypatch.setattr(ImportPreviewDialog, "exec", fake_exec)
    return shown


def _plan(new=2, duplicates=1, invalid_rows=(3,)):
    return {
        "new": [{"UUID_A": f"a{i}", "Sprache_A": f"wort{i}", "UUID_B": f"b{i}", "Sprache_B": f"word{i}", "Datum": "2026-10-11"} for i in range(new)],
        "skipped_duplicate": duplicates,
        "skipped_invalid": len(invalid_rows),
        "invalid_rows": list(invalid_rows),
    }


# ---------------------------------------------------------------- dialog

def test_dialog_shows_the_new_entries_and_the_summary(app, instance):
    dialog = ImportPreviewDialog(None, _plan(new=3, duplicates=2, invalid_rows=(4,)))
    assert dialog._table.rowCount() == 3
    assert dialog._table.item(0, 0).text() == "wort0"
    assert dialog._table.item(2, 1).text() == "word2"
    assert not dialog._invalid_label.isHidden() and "4" in dialog._invalid_label.text()


def test_dialog_without_invalid_rows_has_no_invalid_hint(app, instance):
    assert ImportPreviewDialog(None, _plan(invalid_rows=()))._invalid_label.isHidden()


def test_dialog_shortens_a_long_list_of_invalid_rows(app, instance):
    dialog = ImportPreviewDialog(None, _plan(invalid_rows=tuple(range(1, 41))))
    text = dialog._invalid_label.text()
    listed, _, more = text.partition("…")
    assert "20" in listed and "21" not in listed  # only the first 20 rows are listed
    assert "20" in more  # "... and 20 more"


def test_dialog_table_is_read_only(app, instance):
    from PyQt6.QtWidgets import QAbstractItemView

    dialog = ImportPreviewDialog(None, _plan())  # keep a reference, Qt deletes the child table otherwise
    assert dialog._table.editTriggers() == QAbstractItemView.EditTrigger.NoEditTriggers


# ------------------------------------------------------------ panel flow

def test_confirmed_import_saves_and_signals(instance, monkeypatch):
    panel = DataExchangePanel("englisch")
    signals = []
    panel.vocab_changed.connect(lambda: signals.append(1))
    _pick(monkeypatch, _csv(instance, ["Hallo,Hello", "Danke,Thank you"]))
    shown = _answer_preview(monkeypatch, QDialog.DialogCode.Accepted)

    panel._on_import()
    assert len(shown) == 1 and len(shown[0]["new"]) == 2
    assert [e["Sprache_A"] for e in vocab.load_entries("englisch")] == ["Hallo", "Danke"]
    assert signals == [1]
    assert "2" in panel._feedback_label.text()


def test_cancelled_preview_saves_nothing_and_does_not_signal(instance, monkeypatch):
    panel = DataExchangePanel("englisch")
    signals = []
    panel.vocab_changed.connect(lambda: signals.append(1))
    _pick(monkeypatch, _csv(instance, ["Hallo,Hello"]))
    _answer_preview(monkeypatch, QDialog.DialogCode.Rejected)

    panel._on_import()
    assert vocab.load_entries("englisch") == []
    assert signals == []
    assert panel._feedback_label.text() == "Import cancelled." or "abgebrochen" in panel._feedback_label.text()


def test_nothing_new_opens_no_preview(instance, monkeypatch):
    vocab.save_entries(
        "englisch",
        [{"UUID_A": "a1", "Sprache_A": "Hallo", "UUID_B": "b1", "Sprache_B": "Hello", "Datum": "2026-10-11"}],
    )
    panel = DataExchangePanel("englisch")
    _pick(monkeypatch, _csv(instance, ["Hallo,Hello", ",Bye"]))
    shown = _answer_preview(monkeypatch, QDialog.DialogCode.Accepted)

    panel._on_import()
    assert shown == []  # no window
    assert len(vocab.load_entries("englisch")) == 1
    text = panel._feedback_label.text()
    assert "0" in text and "1" in text  # "0 added, 1 already existed, 1 invalid"


def test_unreadable_file_still_reports_the_read_error(instance, monkeypatch):
    panel = DataExchangePanel("englisch")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(instance / "missing.csv"), ""))
    shown = _answer_preview(monkeypatch, QDialog.DialogCode.Accepted)
    panel._on_import()
    assert shown == [] and panel._feedback_label.text() != ""


def test_panel_module_uses_the_preview_dialog():
    assert data_exchange_panel.ImportPreviewDialog is ImportPreviewDialog


# ------------------------------------------------ resolving (v0.0.16)

def _resolved_plan(pairs=(("pink", "pink"), ("pink", "rosa")), check_rows=(), source=(1, 1)):
    plan = _plan(new=0, duplicates=0, invalid_rows=())
    plan["new"] = [
        {"UUID_A": f"a{i}", "Sprache_A": a, "UUID_B": f"b{i}", "Sprache_B": b, "Datum": "2026-10-11"}
        for i, (a, b) in enumerate(pairs)
    ]
    plan.update(source_rows=list(source), resolved_rows=1, resolved_pairs=len(pairs), check_rows=list(check_rows))
    return plan


def test_dialog_shows_row_column_and_resolve_info(app, instance):
    dialog = ImportPreviewDialog(None, _resolved_plan())
    assert dialog._table.item(1, 2).text() == "1"
    assert not dialog._table.isColumnHidden(2)
    assert "1" in dialog._resolved_label.text() and "2" in dialog._resolved_label.text()
    assert dialog._check_label.isHidden()


def test_dialog_without_source_rows_hides_the_row_column(app, instance):
    dialog = ImportPreviewDialog(None, _plan())
    assert dialog._table.isColumnHidden(2) and dialog._resolved_label.isHidden()


def test_dialog_lists_the_rows_to_check(app, instance):
    dialog = ImportPreviewDialog(None, _resolved_plan(check_rows=(54,)))
    assert not dialog._check_label.isHidden() and "54" in dialog._check_label.text()


def test_tick_box_exists_only_with_a_replan_callable(app, instance):
    assert ImportPreviewDialog(None, _plan())._resolve_check is None
    dialog = ImportPreviewDialog(None, _plan(), lambda resolve: _plan())
    assert dialog._resolve_check.isChecked()


def test_toggling_the_tick_box_replans_and_redraws(app, instance):
    calls = []

    def replan(resolve):
        calls.append(resolve)
        return _plan(new=1, duplicates=0, invalid_rows=()) if not resolve else _resolved_plan()

    dialog = ImportPreviewDialog(None, _resolved_plan(), replan)
    assert dialog._table.rowCount() == 2
    dialog._resolve_check.setChecked(False)
    assert calls == [False] and dialog._table.rowCount() == 1 and dialog.plan["new"][0]["Sprache_A"] == "wort0"
    dialog._resolve_check.setChecked(True)
    assert calls == [False, True] and dialog._table.rowCount() == 2


def test_panel_resolves_by_default(instance, monkeypatch):
    panel = DataExchangePanel("englisch")
    path = instance / "import.csv"
    path.write_text('Sprache_A,Sprache_B\npink,"pink; rosa"\n', encoding="utf-8-sig")
    _pick(monkeypatch, path)
    shown = _answer_preview(monkeypatch, QDialog.DialogCode.Accepted)

    panel._on_import()
    assert [(e["Sprache_A"], e["Sprache_B"]) for e in shown[0]["new"]] == [("pink", "pink"), ("pink", "rosa")]
    assert len(vocab.load_entries("englisch")) == 2


def test_panel_commits_the_plan_on_screen_after_switching_resolve_off(instance, monkeypatch):
    panel = DataExchangePanel("englisch")
    path = instance / "import.csv"
    path.write_text('Sprache_A,Sprache_B\nmein/meine,my\n', encoding="utf-8-sig")
    _pick(monkeypatch, path)

    def switch_off_and_accept(self):
        self._resolve_check.setChecked(False)
        return QDialog.DialogCode.Accepted

    monkeypatch.setattr(ImportPreviewDialog, "exec", switch_off_and_accept)
    panel._on_import()
    assert [e["Sprache_A"] for e in vocab.load_entries("englisch")] == ["mein/meine"]  # as typed, not split
