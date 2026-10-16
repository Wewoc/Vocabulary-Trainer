#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# settings_panel.py
# Vokabeltrainer — PIN change + Bewertung (answer evaluation) settings,
# the Sprache-A/B display names, the DE/EN UI language switch and the
# theme switch (requirements 3.2, 7.1, 8). The config fields already
# exist (config.py's "bewertung"/"sprache_a_name"/"sprache_b_name"/
# "language"/"theme" keys) and evaluation.py/vocab_table_panel.py/
# theme.py already read them. PIN change is wired (since v0.0.10.8): the
# button opens PinChangeDialog, the actual check/saving is pin_store.
#
# Everything else is wired and real:
#   - Bewertung checkboxes (since v0.0.10.1): save on toggle directly
#     into config.json's "bewertung" dict - evaluation.py already reads
#     it on every answer check, no restart needed (unlike language/
#     Sprache-A/B below, a boolean flip has no stale-text problem).
#   - Sprache-A/B names (since v0.0.10.1): same restart-required tradeoff
#     as the language switch - these feed table headers/field labels
#     built once when a panel is constructed (VocabTablePanel,
#     DirectEntryPanel, EditEntryDialog, TestKonfiguratorPanel), no
#     live re-render.
#   - Language (since v0.0.7.3): saves to config.json immediately, but
#     relies on an app restart to take effect - no live re-render of
#     already-visible text (matches the already-decided "a one-time
#     switch cost is acceptable" tradeoff, see
#     the project invariants).
#   - Theme (since v0.0.9.1): applies live via
#     QApplication.instance().setStyleSheet() - unlike the language
#     switch, a stylesheet swap is cheap and instant, so there's no
#     reason to also defer this one to a restart.
# Self-contained widget, knows nothing about its own placement on a page
# (see the project invariants).

from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QWidget,
)

import app_logging
import config
import evaluation
import theme
from gui import i18n
from gui.dialogs.pin_change_dialog import PinChangeDialog
from gui.widgets.no_wheel import NoWheelComboBox


class SettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        ui_language = config.load_config()["language"]
        bewertung = config.load_config()["bewertung"]

        self._pin_button = QPushButton(i18n.text("change_pin", ui_language))
        self._pin_button.clicked.connect(self._on_change_pin)

        self._case_sensitive_checkbox = QCheckBox(
            i18n.text("case_sensitive_option", ui_language)
        )
        self._case_sensitive_checkbox.setChecked(bewertung["case_sensitiv"])
        self._case_sensitive_checkbox.toggled.connect(
            lambda checked: self._on_bewertung_changed("case_sensitiv", checked)
        )

        self._strict_accents_checkbox = QCheckBox(
            i18n.text("strict_accents_option", ui_language)
        )
        self._strict_accents_checkbox.setChecked(bewertung["akzente_streng"])
        self._strict_accents_checkbox.toggled.connect(
            lambda checked: self._on_bewertung_changed("akzente_streng", checked)
        )

        self._ignore_articles_checkbox = QCheckBox(
            i18n.text("ignore_articles_option", ui_language)
        )
        self._ignore_articles_checkbox.setChecked(bewertung["artikel_ignorieren"])
        self._ignore_articles_checkbox.toggled.connect(
            lambda checked: self._on_bewertung_changed("artikel_ignorieren", checked)
        )

        self._theme_label = QLabel(i18n.text("theme_label", ui_language))
        self._theme_combo = NoWheelComboBox()
        self._theme_combo.addItems(theme.theme_names())
        self._theme_combo.setCurrentText(config.load_config()["theme"])
        self._theme_combo.currentTextChanged.connect(self._on_theme_changed)

        self._language_label = QLabel(i18n.text("language_label", ui_language))
        self._language_combo = NoWheelComboBox()
        self._language_combo.addItems(["en", "de"])
        self._language_combo.setCurrentText(ui_language)
        self._language_combo.currentTextChanged.connect(self._on_language_changed)
        self._language_hint = QLabel(i18n.text("language_restart_hint", ui_language))

        sprache_a_name = config.load_config()["sprache_a_name"]
        sprache_b_name = config.load_config()["sprache_b_name"]
        self._sprache_a_name_label = QLabel(i18n.text("sprache_a_name_label", ui_language))
        self._sprache_a_name_input = QLineEdit(sprache_a_name)
        self._sprache_a_name_input.editingFinished.connect(self._on_sprache_a_name_changed)
        self._sprache_b_name_label = QLabel(i18n.text("sprache_b_name_label", ui_language))
        self._sprache_b_name_input = QLineEdit(sprache_b_name)
        self._sprache_b_name_input.editingFinished.connect(self._on_sprache_b_name_changed)
        self._sprache_name_hint = QLabel(i18n.text("sprache_name_restart_hint", ui_language))

        article_cfg = config.load_config()
        self._article_a_label = QLabel(i18n.text("article_language_a_label", ui_language))
        self._article_a_combo = self._article_language_combo(
            "sprache_a_code", article_cfg["sprache_a_code"], ui_language
        )
        self._article_b_label = QLabel(i18n.text("article_language_b_label", ui_language))
        self._article_b_combo = self._article_language_combo(
            "sprache_b_code", article_cfg["sprache_b_code"], ui_language
        )
        self._article_hint = QLabel(i18n.text("article_language_hint", ui_language))

        self._debug_checkbox = QCheckBox(i18n.text("debug_log_option", ui_language))
        self._debug_checkbox.setChecked(app_logging.is_debug())
        self._debug_checkbox.toggled.connect(app_logging.set_debug)

        layout = QGridLayout()
        layout.setColumnStretch(1, 1)
        layout.addWidget(self._pin_button, 0, 0, 1, 2)
        layout.addWidget(self._case_sensitive_checkbox, 1, 0, 1, 2)
        layout.addWidget(self._strict_accents_checkbox, 2, 0, 1, 2)
        layout.addWidget(self._ignore_articles_checkbox, 3, 0, 1, 2)
        layout.addWidget(self._theme_label, 4, 0)
        layout.addWidget(self._theme_combo, 4, 1)
        layout.addWidget(self._language_label, 5, 0)
        layout.addWidget(self._language_combo, 5, 1)
        layout.addWidget(self._language_hint, 6, 0, 1, 2)
        layout.addWidget(self._sprache_a_name_label, 7, 0)
        layout.addWidget(self._sprache_a_name_input, 7, 1)
        layout.addWidget(self._sprache_b_name_label, 8, 0)
        layout.addWidget(self._sprache_b_name_input, 8, 1)
        layout.addWidget(self._sprache_name_hint, 9, 0, 1, 2)
        layout.addWidget(self._article_a_label, 10, 0)
        layout.addWidget(self._article_a_combo, 10, 1)
        layout.addWidget(self._article_b_label, 11, 0)
        layout.addWidget(self._article_b_combo, 11, 1)
        layout.addWidget(self._article_hint, 12, 0, 1, 2)
        layout.addWidget(self._debug_checkbox, 13, 0, 1, 2)
        self.setLayout(layout)

    def _article_language_combo(self, config_key: str, current: str, ui_language: str) -> NoWheelComboBox:
        """Dropdown over the languages that have an article list, plus
        "none" (empty code). Saves to config.json on every change."""
        combo = NoWheelComboBox()
        for code in evaluation.article_languages():
            combo.addItem(i18n.text(f"lang_{code}", ui_language), code)
        combo.addItem(i18n.text("lang_none", ui_language), "")
        index = combo.findData(current)
        combo.setCurrentIndex(index if index >= 0 else combo.count() - 1)  # unknown code = none
        combo.currentIndexChanged.connect(
            lambda _index, key=config_key, box=combo: self._on_article_language_changed(key, box.currentData())
        )
        return combo

    def _on_article_language_changed(self, config_key: str, code: str) -> None:
        cfg = config.load_config()
        cfg[config_key] = code
        config.save_config(cfg)

    def _on_change_pin(self) -> None:
        if PinChangeDialog(self).exec() == QDialog.DialogCode.Accepted:
            ui_language = config.load_config()["language"]
            QMessageBox.information(
                self, i18n.text("pin_change_title", ui_language), i18n.text("pin_changed", ui_language)
            )

    def _on_language_changed(self, new_language: str) -> None:
        cfg = config.load_config()
        cfg["language"] = new_language
        config.save_config(cfg)

    def _on_bewertung_changed(self, key: str, value: bool) -> None:
        cfg = config.load_config()
        cfg["bewertung"][key] = value
        config.save_config(cfg)

    def _on_sprache_a_name_changed(self) -> None:
        cfg = config.load_config()
        cfg["sprache_a_name"] = self._sprache_a_name_input.text().strip() or cfg["sprache_a_name"]
        config.save_config(cfg)

    def _on_sprache_b_name_changed(self) -> None:
        cfg = config.load_config()
        cfg["sprache_b_name"] = self._sprache_b_name_input.text().strip() or cfg["sprache_b_name"]
        config.save_config(cfg)

    def _on_theme_changed(self, new_theme: str) -> None:
        cfg = config.load_config()
        cfg["theme"] = new_theme
        config.save_config(cfg)
        QApplication.instance().setStyleSheet(theme.stylesheet(new_theme))
