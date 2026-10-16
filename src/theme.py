#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# theme.py
# Vokabeltrainer — central theme color tokens and the Qt stylesheet
# built from them (see the project invariants: color values come
# only from here, never as hardcoded hex scattered through GUI code).
# Pattern and color-token roles taken from GLA's theme.py (see
# data model, section 7) - a numbered/named gallery of
# full color schemes, not a light/dark split, since "just light/dark"
# didn't feel exciting enough for the target audience (kids). Unlike
# GLA, this module stays a pure Leaf-Node: colors()/stylesheet() take a
# theme name as a parameter rather than reading config themselves, so
# the app can re-apply a theme live (see gui/panels/settings_panel.py)
# instead of requiring a restart like GLA does.
#
# Color roles (same meaning in every theme, matching GLA):
#   bg0      - deepest background, for inset/recessed elements
#   bg       - main background (window)
#   bg2      - raised surface (cards, group boxes)
#   bg3      - dividers, borders
#   accent   - primary: active tab, primary button, focus
#   accent2  - secondary: hover state of accent
#   text     - main text
#   text2    - secondary/muted text
# green/yellow/red are fixed across every theme (not per-theme tokens)
# - they carry domain meaning (correct/warning/wrong), not aesthetics,
# so they look the same regardless of the chosen theme (same reasoning
# GLA uses for its function-specific colors).

GREEN = "#2fae5f"
YELLOW = "#f5b400"
RED = "#e4432f"

_THEMES = {
    "ozean": {
        "bg0": "#8fd4e8",
        "bg": "#bce8f2",
        "bg2": "#ffffff",
        "bg3": "#6cc3dd",
        "accent": "#047a9e",
        "accent2": "#035c78",
        "text": "#06313e",
        "text2": "#3d6b78",
    },
    "sonne": {
        "bg0": "#ffcf66",
        "bg": "#ffe08a",
        "bg2": "#ffffff",
        "bg3": "#ffbf3d",
        "accent": "#cc7400",
        "accent2": "#a65e00",
        "text": "#4a2e00",
        "text2": "#7a5a1f",
    },
    "dschungel": {
        "bg0": "#8fd48a",
        "bg": "#b8e8b2",
        "bg2": "#ffffff",
        "bg3": "#6bc364",
        "accent": "#1f7a36",
        "accent2": "#175c29",
        "text": "#132e16",
        "text2": "#3d5c3f",
    },
    "beere": {
        "bg0": "#c79af2",
        "bg": "#dcbdf7",
        "bg2": "#ffffff",
        "bg3": "#b57aed",
        "accent": "#6a1fb8",
        "accent2": "#511590",
        "text": "#2a0f45",
        "text2": "#5c4473",
    },
    "pink": {
        "bg0": "#f2a6cf",
        "bg": "#f7bedd",
        "bg2": "#ffffff",
        "bg3": "#e685bd",
        "accent": "#d6177e",
        "accent2": "#ad1366",
        "text": "#4a0e30",
        "text2": "#8a4068",
    },
    "nacht": {
        "bg0": "#0e0f14",
        "bg": "#15171d",
        "bg2": "#1f232b",
        "bg3": "#2a2f38",
        "accent": "#6aa9ff",
        "accent2": "#4a84db",
        "text": "#e7eaef",
        "text2": "#9aa3b2",
    },
}

_DEFAULT_THEME = "ozean"


def theme_names() -> list[str]:
    """All available theme keys, for a theme-selection dropdown - no
    limit on how many, a new entry in _THEMES appears automatically
    (same "just add a dict" extension pattern as GLA)."""
    return list(_THEMES.keys())


def colors(name: str) -> dict:
    """Returns the flat color-token dict for a theme name, falling back
    to the default theme for an unknown name (e.g. a stale config
    value) rather than raising."""
    return _THEMES.get(name, _THEMES[_DEFAULT_THEME])


def stylesheet(name: str) -> str:
    """Builds a Qt stylesheet string from a theme's color tokens - the
    only place hex values appear; every widget just inherits this.

    Sub-controls (QTabBar::tab, QHeaderView::section, ...) do NOT pick
    up the plain `QWidget { color: ... }` rule - Qt paints them through
    the style engine, not the normal widget cascade, so each one needs
    its own explicit color or it silently falls back to the native
    palette (on a Windows dark-mode system, that's white-on-white
    against a light theme - the bug a real screenshot caught). Every
    rule below exists because of that, not for extra polish."""
    c = colors(name)
    return f"""
        QWidget {{
            background-color: {c["bg"]};
            color: {c["text"]};
        }}
        QGroupBox {{
            border: 1px solid {c["bg3"]};
            margin-top: 8px;
            background-color: {c["bg2"]};
            color: {c["text"]};
        }}
        QGroupBox::title {{
            color: {c["text2"]};
        }}
        QLabel {{
            color: {c["text"]};
            background-color: transparent;
        }}
        QLabel#banner_title {{
            color: {c["accent"]};
        }}
        QLabel#banner_subtitle {{
            color: {c["text2"]};
        }}
        QPushButton {{
            background-color: {c["bg2"]};
            color: {c["text"]};
            border: 1px solid {c["bg3"]};
            padding: 4px 8px;
        }}
        QPushButton:disabled {{
            color: {c["text2"]};
        }}
        QLineEdit, QComboBox, QSpinBox, QTableWidget {{
            background-color: {c["bg2"]};
            color: {c["text"]};
            border: 1px solid {c["bg3"]};
        }}
        QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {{
            color: {c["text2"]};
        }}
        QCheckBox, QRadioButton {{
            color: {c["text"]};
        }}
        QCheckBox:disabled, QRadioButton:disabled {{
            color: {c["text2"]};
        }}
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 14px;
            height: 14px;
            border: 2px solid {c["text2"]};
            background-color: {c["bg2"]};
        }}
        QRadioButton::indicator {{
            border-radius: 8px;
        }}
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background-color: {c["accent"]};
            border: 2px solid {c["accent"]};
        }}
        QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {{
            border: 2px solid {c["bg3"]};
        }}
        QTableWidget::item:selected {{
            background-color: {c["accent2"]};
            color: {c["bg2"]};
        }}
        QHeaderView::section {{
            background-color: {c["bg2"]};
            color: {c["text"]};
            border: 1px solid {c["bg3"]};
        }}
        QTabWidget::pane {{
            border: 1px solid {c["bg3"]};
        }}
        QTabBar::tab {{
            background: {c["bg2"]};
            color: {c["text"]};
            padding: 6px 12px;
        }}
        QTabBar::tab:selected {{
            background: {c["bg"]};
            color: {c["accent"]};
        }}
    """
