# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for crash_handler.py (reports outside the instance folder, scrubbed
# message, rolling cap, hook never raises) with temporary directories.

import os
import sys
import threading
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import crash_handler  # noqa: E402
import log_scrub  # noqa: E402
import paths  # noqa: E402
import vocab  # noqa: E402


_REAL_SHOW_NOTICE = crash_handler._show_notice


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path / "instance")
    local = tmp_path / "local"
    temp = tmp_path / "temp"
    monkeypatch.setenv("LOCALAPPDATA", str(local))
    monkeypatch.setenv("TEMP", str(temp))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(crash_handler, "_show_notice", lambda path: None)
    vocab.save_entries(
        "englisch",
        [{"UUID_A": "a1", "Sprache_A": "Haus", "UUID_B": "b1", "Sprache_B": "house", "Datum": "2026-01-01"}],
    )
    yield tmp_path
    crash_handler.uninstall()


def _raise(message: str) -> BaseException:
    try:
        raise KeyError(message)
    except KeyError as exc:
        return exc


def _reports(env_dir: Path) -> list[Path]:
    return sorted((env_dir / "local" / "Vokabeltrainer" / "crash").glob("crash_*.log"))


def test_report_goes_to_localappdata_first(env):
    crash_handler._report(_raise("boom"), "MainThread")
    assert len(_reports(env)) == 1
    assert not (env / "instance").exists() or not list((env / "instance").rglob("crash_*"))


def test_falls_back_to_temp_then_cwd(env, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(env / "blocked" / "x"))
    (env / "blocked").write_text("a file, not a directory")  # mkdir below it fails
    crash_handler._report(_raise("boom"), "MainThread")
    assert list((env / "temp" / "Vokabeltrainer" / "crash").glob("crash_*.log"))

    monkeypatch.setenv("TEMP", str(env / "blocked" / "y"))
    crash_handler._report(_raise("boom"), "MainThread")
    assert list((env / "crash").glob("crash_*.log"))


def test_report_keeps_frames_but_scrubs_the_message(env):
    crash_handler._report(_raise("Haus"), "worker-1")
    text = _reports(env)[0].read_text(encoding="utf-8")
    assert "Haus" not in text
    assert "<term>" in text
    assert "KeyError" in text
    assert "_raise" in text  # stack frame stays readable
    assert "thread: worker-1" in text
    assert "version:" in text


def test_scrubber_failure_only_blanks_the_message(env, monkeypatch):
    monkeypatch.setattr(vocab, "load_entries", lambda language: (_ for _ in ()).throw(OSError("gone")))
    crash_handler._report(_raise("Haus"), "MainThread")
    text = _reports(env)[0].read_text(encoding="utf-8")
    assert "Haus" not in text
    assert log_scrub.UNAVAILABLE in text
    assert "_raise" in text


def test_chained_exception_is_scrubbed_too(env):
    word = "Ha" + "us"  # not a literal: source lines are not scrubbed
    try:
        try:
            raise KeyError(word)
        except KeyError as inner:
            raise RuntimeError(f"wrapped {word}") from inner
    except RuntimeError as exc:
        crash_handler._report(exc, "MainThread")
    text = _reports(env)[0].read_text(encoding="utf-8")
    assert "Haus" not in text
    assert "direct cause" in text


def test_rolling_cap_keeps_the_newest_ten(env):
    for _ in range(12):
        crash_handler._report(_raise("boom"), "MainThread")
    files = _reports(env)
    assert len(files) == 10
    assert files == sorted(files)


def test_hook_never_raises_even_if_everything_fails(env, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("handler broke")

    monkeypatch.setattr(crash_handler, "_build_report", boom)
    monkeypatch.setattr(crash_handler, "_write_report", boom)
    monkeypatch.setattr(crash_handler._log, "error", boom)
    crash_handler._report(_raise("x"), "MainThread")  # must not raise


def test_notice_failure_is_swallowed(env, monkeypatch):
    from PyQt6.QtWidgets import QApplication, QMessageBox

    QApplication.instance() or QApplication([])
    monkeypatch.setattr(crash_handler, "_show_notice", _REAL_SHOW_NOTICE)
    monkeypatch.setattr(crash_handler, "_ui_language", lambda: "en")
    monkeypatch.setattr(QMessageBox, "critical", lambda *a, **k: (_ for _ in ()).throw(OSError()))
    crash_handler._show_notice(None)  # must not raise, flag must be reset
    assert crash_handler._notice_open is False


def test_install_is_idempotent_and_sets_both_hooks(env):
    original = sys.excepthook
    crash_handler.install()
    crash_handler.install()
    assert sys.excepthook is crash_handler._excepthook
    assert threading.excepthook is crash_handler._thread_excepthook
    crash_handler.uninstall()
    assert sys.excepthook is original


def test_thread_exception_is_reported(env):
    crash_handler.install()

    def work():
        raise ValueError("in thread")

    thread = threading.Thread(target=work, name="worker-x")
    thread.start()
    thread.join()
    text = _reports(env)[0].read_text(encoding="utf-8")
    assert "ValueError" in text
    assert "thread: worker-x" in text


def test_slot_error_with_hook_does_not_kill_the_process(env):
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import QApplication, QPushButton

    app = QApplication.instance() or QApplication([])
    crash_handler.install()
    button = QPushButton()

    def failing_slot():
        raise ValueError("slot error")

    button.clicked.connect(failing_slot)
    QTimer.singleShot(20, button.click)
    QTimer.singleShot(150, app.quit)
    app.exec()
    assert len(_reports(env)) == 1
