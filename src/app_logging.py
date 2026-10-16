#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# app_logging.py
# Vokabeltrainer — technical debug log (requirements 7.2): logs/app.log in
# the instance folder (portable, via paths.base_dir()), rotating with a
# fixed size cap, unencrypted - which is why log_scrub.ScrubFilter is
# attached to the handler (no clear-text vocabulary, UUIDs only).
#
# Standard level INFO (or DEBUG if config.json says so). set_debug()
# switches at runtime and is deliberately not written to the config: the
# app never runs permanently on DEBUG (requirements 7.2).
#
# A log file that can't be created must never stop the app - setup()
# then just leaves logging without a handler.

import logging
from logging.handlers import RotatingFileHandler

import config
import log_scrub
import paths

_LOG_DIR = "logs"
_LOG_FILE = "app.log"
_MAX_BYTES = 2_500_000
_BACKUP_COUNT = 1  # 2 x 2.5 MB = at most 5 MB in total (requirements 7.2)
_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

_handler: RotatingFileHandler | None = None


def setup() -> None:
    """Attaches the rotating file handler to the root logger. Idempotent."""
    global _handler
    if _handler is not None:
        return
    try:
        log_dir = paths.base_dir() / _LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            log_dir / _LOG_FILE, maxBytes=_MAX_BYTES, backupCount=_BACKUP_COUNT, encoding="utf-8"
        )
    except OSError:
        return
    handler.setFormatter(logging.Formatter(_FORMAT))
    handler.addFilter(log_scrub.ScrubFilter())
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if config.load_config()["debug_log_level"] == "DEBUG" else logging.INFO)
    _handler = handler


def set_debug(enabled: bool) -> None:
    logging.getLogger().setLevel(logging.DEBUG if enabled else logging.INFO)


def is_debug() -> bool:
    return logging.getLogger().getEffectiveLevel() <= logging.DEBUG


def teardown() -> None:
    """Detaches and closes the handler (tests, clean shutdown)."""
    global _handler
    if _handler is None:
        return
    logging.getLogger().removeHandler(_handler)
    _handler.close()
    _handler = None
