#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# version.py
# Vokabeltrainer — single source of truth for APP_VERSION
# Leaf-Node: no project imports.

APP_VERSION = "0.0.18"

# Shown in the About window (gui/dialogs/about_dialog.py). REPO_URL is the one
# address the app ever opens, and only when the user clicks the link there.
APP_NAME = "Vocabulary-Trainer"
REPO_URL = "https://github.com/Wewoc/Vocabulary-Trainer"
COPYRIGHT = "Copyright (C) 2026 Wewoc"


def is_newer(latest: str, current: str) -> bool:
    """True only if `latest` is a well-formed, strictly higher version than
    `current`. Unparseable input is never treated as "newer" (pattern
    carried over from Garmin Local Archive, see the data model)."""
    try:
        latest_tuple = tuple(int(p) for p in latest.lstrip("vV").split("."))
        current_tuple = tuple(int(p) for p in current.lstrip("vV").split("."))
    except ValueError:
        return False
    return latest_tuple > current_tuple
