#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# compiler/build_manifest.py — single source of truth for the PyInstaller build
#
# No logic, no imports beyond stdlib types — pure data. build.py reads this;
# nothing else needs to duplicate these values.

APP_NAME = "Vocabulary_trainer"  # EXE name fixed by requirements 9.1

ENTRY_POINT = "src/start.py"

# Added to PyInstaller's analysis search path (--paths) so its static
# import resolution finds the flat modules (config, theme, gui.main_window,
# ...) the same way start.py's own runtime sys.path.insert() does — see
# src/start.py. Without this, the build succeeds but the frozen exe fails
# on the first `import config` with ModuleNotFoundError.
EXTRA_PATHS = ["src"]

# Read-only assets bundled into the build via PyInstaller --add-data.
# Empty: unlike local_translator, there's no web frontend or external data
# file — theme.py/gui/i18n.py are plain Python dicts, already part of the
# analyzed source.
DATA_FILES: list[tuple[str, str]] = []

# Extra modules PyInstaller's static analysis might miss. Empty: PyQt6 and
# cryptography ship their own PyInstaller hooks (keyring, used in
# v0.0.10.6 only, was removed again in v0.0.10.7).
HIDDEN_IMPORTS: list[str] = []

# User-editable files to copy next to the built exe. Deliberately empty:
# config.py creates config.json itself on first run, including a fresh
# instance_id (see src/config.py). Copying a pre-built config.json here
# would give every child instance the build machine's own instance_id —
# breaking the requirement that every instance gets its own instance_id
# (requirements 9.1).
EXTERNAL_DEFAULTS: list[str] = []

# Second EXE, built alongside the app and placed directly in dist/<APP_NAME>/
# (not a subfolder, unlike local_translator's tester) so it ships inside the
# same release ZIP, next to the app's own files — see
# requirements 9 (the update script replaces only the program folder).
# --onefile, not --onedir: it's a
# one-shot installer/updater, not launched repeatedly.
UPDATER_NAME = "update"
UPDATER_ENTRY_POINT = "compiler/update_installer.py"

# Documentation that ships with the app (v0.0.18): README and user guide in
# German and English. build.py copies the files flat into info/ next to the
# exe, the screenshots into info/bilder/ (the guides refer to them as
# bilder/...), and LICENSE next to the exe. The in-app viewer finds them
# there (src/doc_files.py - keep its DOCUMENTS list and INFO_FILES in step,
# tests/test_build_manifest.py checks it). Paths are relative to the repo root.
INFO_DIR = "info"
INFO_FILES = [
    "README.md",
    "README.de.md",
    "docs/Bedienungsanleitung.md",
    "docs/User_Guide.md",
]
INFO_IMAGES = "docs/bilder"
LICENSE_FILE = "LICENSE"

# What a PyInstaller --onedir build of the app actually produces next to
# the EXE (see screenshot: Vocabulary_trainer.exe + _internal/), plus the
# documentation. This is everything update_installer.py copies into a chosen
# target folder — the single source of truth both build.py's ZIP and
# update_installer.py's copy logic read, so they can never drift apart.
ONEDIR_ITEMS = [f"{APP_NAME}.exe", "_internal", INFO_DIR, LICENSE_FILE]
