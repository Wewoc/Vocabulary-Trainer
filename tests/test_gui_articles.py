# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Offscreen tests for the article language (v0.0.15): config defaults, the
# settings dropdowns, and which language the quiz hands to the evaluation.

import json
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PyQt6.QtWidgets import QApplication  # noqa: E402

import config  # noqa: E402
import evaluation  # noqa: E402
import paths  # noqa: E402
import vocab  # noqa: E402
from gui.panels import quiz_panel  # noqa: E402
from gui.panels.settings_panel import SettingsPanel  # noqa: E402
from gui.widgets.no_wheel import NoWheelComboBox  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def instance(app, tmp_path, monkeypatch):
    (tmp_path / "instance").mkdir()
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path / "instance")
    return tmp_path / "instance"


def _select(combo, code):
    combo.setCurrentIndex(combo.findData(code))


# ----------------------------------------------------------------- config

def test_defaults_match_the_default_language_names(instance):
    cfg = config.load_config()
    assert (cfg["sprache_a_name"], cfg["sprache_b_name"]) == ("Deutsch", "Englisch")
    assert (cfg["sprache_a_code"], cfg["sprache_b_code"]) == ("de", "en")


def test_an_old_config_without_the_codes_gets_them(instance):
    (instance / "config.json").write_text(
        json.dumps({"instance_id": "keep-me", "language": "de", "sprache_b_name": "Spanisch"}),
        encoding="utf-8",
    )
    cfg = config.load_config()
    assert (cfg["sprache_a_code"], cfg["sprache_b_code"]) == ("de", "en")
    assert cfg["instance_id"] == "keep-me" and cfg["sprache_b_name"] == "Spanisch"
    assert json.loads((instance / "config.json").read_text(encoding="utf-8"))["sprache_a_code"] == "de"


# --------------------------------------------------------- settings panel

def test_dropdowns_show_the_stored_codes_plus_none(instance):
    cfg = config.load_config()
    cfg["sprache_a_code"], cfg["sprache_b_code"] = "es", "fr"
    config.save_config(cfg)
    panel = SettingsPanel()
    assert panel._article_a_combo.currentData() == "es"
    assert panel._article_b_combo.currentData() == "fr"
    codes = [panel._article_a_combo.itemData(i) for i in range(panel._article_a_combo.count())]
    assert codes == [*evaluation.article_languages(), ""]  # all article languages, then "none"


def test_changing_a_dropdown_writes_the_config(instance):
    panel = SettingsPanel()
    _select(panel._article_a_combo, "es")
    _select(panel._article_b_combo, "")
    cfg = config.load_config()
    assert (cfg["sprache_a_code"], cfg["sprache_b_code"]) == ("es", "")


def test_an_unknown_stored_code_is_shown_as_none(instance):
    cfg = config.load_config()
    cfg["sprache_b_code"] = "klingon"
    config.save_config(cfg)
    assert SettingsPanel()._article_b_combo.currentData() == ""


def test_dropdowns_ignore_the_mouse_wheel(instance):
    panel = SettingsPanel()
    assert isinstance(panel._article_a_combo, NoWheelComboBox)
    assert isinstance(panel._article_b_combo, NoWheelComboBox)


# ------------------------------------------------------------------- quiz

def _seed_quiz(instance):
    vocab.save_entries(
        "englisch",
        [{"UUID_A": "a1", "Sprache_A": "Haus", "UUID_B": "b1", "Sprache_B": "house", "Datum": "2026-10-11"}],
    )
    cfg = config.load_config()
    cfg["sprache_a_code"], cfg["sprache_b_code"] = "es", "fr"  # distinct, to see which side is used
    config.save_config(cfg)


def _spy(monkeypatch):
    seen = []
    real = evaluation.evaluate_with_cluster

    def spy(given, expected, alternates, settings, language="en"):
        seen.append(language)
        return real(given, expected, alternates, settings, language)

    monkeypatch.setattr(quiz_panel.evaluation, "evaluate_with_cluster", spy)
    return seen


def test_quiz_a_to_b_uses_the_b_code(instance, monkeypatch):
    _seed_quiz(instance)
    seen = _spy(monkeypatch)
    panel = quiz_panel.QuizPanel(vocab_language="englisch", direction="A->B", count=1)
    panel._answer_input.setText("house")
    panel._check_answer()
    assert seen == ["fr"]  # A->B: the child types language B


def test_quiz_b_to_a_uses_the_a_code(instance, monkeypatch):
    _seed_quiz(instance)
    seen = _spy(monkeypatch)
    panel = quiz_panel.QuizPanel(vocab_language="englisch", direction="B->A", count=1)
    panel._answer_input.setText("Haus")
    panel._check_answer()
    assert seen == ["es"]  # B->A: the child types language A


def test_quiz_ignores_a_german_article_end_to_end(instance):
    vocab.save_entries(
        "englisch",
        [{"UUID_A": "a1", "Sprache_A": "das Haus", "UUID_B": "b1", "Sprache_B": "house", "Datum": "2026-10-11"}],
    )
    cfg = config.load_config()
    cfg["bewertung"]["artikel_ignorieren"] = True
    config.save_config(cfg)  # defaults: A = de, B = en

    panel = quiz_panel.QuizPanel(vocab_language="englisch", direction="B->A", count=1)
    panel._answer_input.setText("Haus")  # Englisch -> Deutsch, article left out
    panel._check_answer()
    assert panel.session_results()[0]["outcome"] == "correct"


def test_quiz_with_code_none_ignores_no_article(instance):
    vocab.save_entries(
        "englisch",
        [{"UUID_A": "a1", "Sprache_A": "das Haus", "UUID_B": "b1", "Sprache_B": "house", "Datum": "2026-10-11"}],
    )
    cfg = config.load_config()
    cfg["bewertung"]["artikel_ignorieren"] = True
    cfg["sprache_a_code"] = ""
    config.save_config(cfg)

    panel = quiz_panel.QuizPanel(vocab_language="englisch", direction="B->A", count=1)
    panel._answer_input.setText("Haus")
    panel._check_answer()
    assert panel.session_results()[0]["outcome"] == "wrong"
