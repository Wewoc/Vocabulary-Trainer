#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# crash_handler.py
# Vokabeltrainer — global exception handling (pattern from GLA's
# crash_handler.py, data model, section 7): sys.excepthook
# + threading.excepthook write a crash report, log an ERROR and show a
# notice. Installed after the QApplication exists (start.py), so the
# notice is possible; an error before that point is not covered.
#
# Crash reports live at a fixed path OUTSIDE the portable instance folder
# (a deliberate exception to the portable-mode rule): %LOCALAPPDATA%\Vokabeltrainer\
# crash, falling back to %TEMP%, then ./crash - an unreachable instance
# folder can itself be the cause of a crash. Rolling cap on the number of
# files, oldest first.
#
# Only the exception *message* goes through log_scrub.scrub(): the stack
# frames (file, function, source line) are code, not data, so a report
# stays useful even when the scrubber fails (then just the message
# becomes <unavailable>). Local variables are never written.
#
# The hook never raises: every step is guarded on its own, a failing
# handler must not mask the original error.
#
# With a custom sys.excepthook PyQt6 no longer aborts the process on an
# unhandled exception in a slot - the app keeps running (decision:
# v0.0.10.10, the tracking is written atomically, so continuing is safe).

import logging
import os
import platform
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path

import log_scrub
from gui import i18n
from version import APP_VERSION

_log = logging.getLogger(__name__)

_MAX_FILES = 10
_FILE_GLOB = "crash_*.log"

_previous_hooks: tuple | None = None
_notice_open = False


def _candidate_dirs() -> list[Path]:
    dirs = []
    for variable in ("LOCALAPPDATA", "TEMP"):
        base = os.environ.get(variable)
        if base:
            dirs.append(Path(base) / "Vokabeltrainer" / "crash")
    dirs.append(Path.cwd() / "crash")
    return dirs


def _scrubbed_message(exc: BaseException) -> str:
    try:
        return log_scrub.scrub(str(exc))
    except Exception:  # noqa: BLE001
        return log_scrub.UNAVAILABLE


def _format_exception(exc: BaseException, seen: set[int]) -> list[str]:
    """Like traceback.format_exception(), but with the message scrubbed
    and the frames untouched. Chained exceptions come first, as in Python."""
    seen.add(id(exc))
    lines: list[str] = []
    cause, context = exc.__cause__, exc.__context__
    if cause is not None and id(cause) not in seen:
        lines += _format_exception(cause, seen)
        lines.append("\nThe above exception was the direct cause of the following exception:\n\n")
    elif context is not None and not exc.__suppress_context__ and id(context) not in seen:
        lines += _format_exception(context, seen)
        lines.append("\nDuring handling of the above exception, another exception occurred:\n\n")

    lines.append("Traceback (most recent call last):\n")
    lines += traceback.format_list(traceback.extract_tb(exc.__traceback__))
    type_name = f"{type(exc).__module__}.{type(exc).__qualname__}"
    message = _scrubbed_message(exc)
    lines.append(f"{type_name}: {message}\n" if message else f"{type_name}\n")
    return lines


def _build_report(exc: BaseException, thread_name: str) -> str:
    header = [
        f"time: {datetime.now().isoformat(timespec='seconds')}",
        f"version: {APP_VERSION}",
        f"python: {platform.python_version()}",
        f"platform: {platform.platform()}",
        f"thread: {thread_name}",
        "",
    ]
    return "\n".join(header) + "".join(_format_exception(exc, set()))


def _write_report(text: str) -> Path | None:
    """Writes the report into the first usable directory, then trims the
    directory to _MAX_FILES. Returns the file path, or None if no
    directory worked."""
    name = f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.log"
    for directory in _candidate_dirs():
        try:
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / name
            path.write_text(text, encoding="utf-8")
        except OSError:
            continue
        _trim(directory)
        return path
    return None


def _trim(directory: Path) -> None:
    try:
        files = sorted(directory.glob(_FILE_GLOB))
        for old in files[:-_MAX_FILES]:
            old.unlink()
    except OSError:
        pass


def _ui_language() -> str:
    try:
        import config

        return config.load_config()["language"]
    except Exception:  # noqa: BLE001
        return "en"


def _show_notice(path: Path | None) -> None:
    """Notice window, main thread only and only while a QApplication
    exists. A flag stops windows from stacking when the same error
    repeats on every click."""
    global _notice_open
    if _notice_open or threading.current_thread() is not threading.main_thread():
        return
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox

        if QApplication.instance() is None:
            return
        language = _ui_language()
        _notice_open = True
        QMessageBox.critical(
            None,
            i18n.text("crash_title", language),
            i18n.text("crash_message", language, path=str(path) if path else "-"),
        )
    except Exception:  # noqa: BLE001
        pass
    finally:
        _notice_open = False


def _report(exc: BaseException, thread_name: str) -> None:
    path = None
    try:
        path = _write_report(_build_report(exc, thread_name))
    except Exception:  # noqa: BLE001
        pass
    try:
        _log.error(
            "unhandled exception thread=%s report=%s",
            thread_name,
            path or "unavailable",
            exc_info=(type(exc), exc, exc.__traceback__),
        )
    except Exception:  # noqa: BLE001
        pass
    _show_notice(path)


def _excepthook(exc_type, exc, tb) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc, tb)
        return
    if exc.__traceback__ is None:
        exc = exc.with_traceback(tb)
    _report(exc, threading.current_thread().name)


def _thread_excepthook(args) -> None:
    if args.exc_type is SystemExit or args.exc_value is None:
        return
    name = args.thread.name if args.thread is not None else "unknown"
    _report(args.exc_value, name)


def install() -> None:
    """Installs sys.excepthook and threading.excepthook. Idempotent."""
    global _previous_hooks
    if _previous_hooks is not None:
        return
    _previous_hooks = (sys.excepthook, threading.excepthook)
    sys.excepthook = _excepthook
    threading.excepthook = _thread_excepthook


def uninstall() -> None:
    """Restores the previous hooks (tests)."""
    global _previous_hooks
    if _previous_hooks is None:
        return
    sys.excepthook, threading.excepthook = _previous_hooks
    _previous_hooks = None
