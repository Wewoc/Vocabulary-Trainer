#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# paths.py
# Vokabeltrainer — sole source for base-directory resolution
# (Portable-Mode requirement, see requirements 9.2).
# Leaf-Node: no project imports.

import sys
from pathlib import Path


def base_dir() -> Path:
    """Instance base directory: the folder next to `Vocabulary_trainer.exe` in a
    PyInstaller build (frozen), otherwise the project root in dev mode.
    Every other module derives its paths (config, daten/, metadaten/,
    logs/) exclusively from this — never directly via __file__ or
    platform-typical mechanisms like %APPDATA%."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent
