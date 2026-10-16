#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# start.py
# Vokabeltrainer — entry point.

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PyQt6.QtWidgets import QApplication  # noqa: E402

import app_logging  # noqa: E402
import config  # noqa: E402
import crash_handler  # noqa: E402
import theme  # noqa: E402
from gui.main_window import MainWindow  # noqa: E402
from version import APP_VERSION  # noqa: E402


def main() -> None:
    app_logging.setup()
    logging.getLogger("start").info("start version=%s", APP_VERSION)
    app = QApplication(sys.argv)
    crash_handler.install()
    app.setStyleSheet(theme.stylesheet(config.load_config()["theme"]))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
