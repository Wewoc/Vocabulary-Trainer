# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for app_logging.py (requirements 7.2) with a temporary instance dir.

import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import app_logging  # noqa: E402
import paths  # noqa: E402
import vocab  # noqa: E402


@pytest.fixture
def instance(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    root_level = logging.getLogger().level
    yield tmp_path
    app_logging.teardown()
    logging.getLogger().setLevel(root_level)


def _log_text(instance) -> str:
    for handler in logging.getLogger().handlers:
        handler.flush()
    return (instance / "logs" / "app.log").read_text(encoding="utf-8")


def test_setup_creates_log_and_writes_info(instance):
    app_logging.setup()
    logging.getLogger("t").info("hello")
    assert "hello" in _log_text(instance)


def test_setup_is_idempotent(instance):
    before = len(logging.getLogger().handlers)
    app_logging.setup()
    app_logging.setup()
    assert len(logging.getLogger().handlers) == before + 1


def test_debug_only_after_switch(instance):
    app_logging.setup()
    log = logging.getLogger("t")
    log.debug("quiet")
    assert "quiet" not in _log_text(instance)
    app_logging.set_debug(True)
    assert app_logging.is_debug() is True
    log.debug("loud")
    app_logging.set_debug(False)
    assert app_logging.is_debug() is False
    assert "loud" in _log_text(instance)


def test_vocab_term_never_reaches_the_file(instance):
    vocab.save_entries(
        "englisch",
        [{"UUID_A": "a1", "Sprache_A": "Haus", "UUID_B": "b1", "Sprache_B": "house", "Datum": "2026-01-01"}],
    )
    app_logging.setup()
    logging.getLogger("t").info("failed on %s", "Haus")
    text = _log_text(instance)
    assert "Haus" not in text
    assert "<term>" in text


def test_unwritable_log_dir_does_not_crash(instance, monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("read-only")

    monkeypatch.setattr(app_logging, "RotatingFileHandler", boom)
    app_logging.setup()  # must not raise
    assert not (instance / "logs" / "app.log").exists()
