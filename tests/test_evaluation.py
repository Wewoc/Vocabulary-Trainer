# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for evaluation.py: answer comparison, with the article language
# (v0.0.15) picked per call instead of the old fixed "en".

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import evaluation  # noqa: E402

ARTICLES_ON = {"artikel_ignorieren": True}


@pytest.mark.parametrize(
    "language,given,expected",
    [
        ("en", "house", "the house"),
        ("de", "Haus", "das Haus"),
        ("de", "Tisch", "der Tisch"),
        ("de", "Katze", "die Katze"),
        ("es", "agua", "el agua"),
        ("es", "casa", "la casa"),
        ("fr", "maison", "la maison"),
        ("fr", "livre", "le livre"),
    ],
)
def test_leading_article_is_ignored_in_the_right_language(language, given, expected):
    assert evaluation.is_correct(given, expected, ARTICLES_ON, language) is True


def test_regression_german_answer_side_used_to_fail():
    # v0.0.15: QuizPanel never passed a language, so "en" applied and the
    # German article of the expected answer was never stripped.
    assert evaluation.is_correct("Haus", "das Haus", ARTICLES_ON) is False  # default "en"
    assert evaluation.is_correct("Haus", "das Haus", ARTICLES_ON, "de") is True


def test_article_of_the_wrong_language_is_not_stripped():
    assert evaluation.is_correct("Haus", "the Haus", ARTICLES_ON, "de") is False
    assert evaluation.is_correct("house", "das house", ARTICLES_ON, "en") is False


def test_only_a_leading_article_is_stripped():
    assert evaluation.is_correct("Widerstand", "Wi" + "der" + "stand", ARTICLES_ON, "de") is True
    assert evaluation.is_correct("stand", "Widerstand", ARTICLES_ON, "de") is False  # "der" inside a word stays


def test_article_inside_the_answer_is_not_stripped():
    assert evaluation.is_correct("Haus das", "Haus", ARTICLES_ON, "de") is False


@pytest.mark.parametrize("language", ["", "xx", None])
def test_unknown_or_empty_language_ignores_no_article(language):
    assert evaluation.is_correct("Haus", "das Haus", ARTICLES_ON, language) is False
    assert evaluation.is_correct("das Haus", "das Haus", ARTICLES_ON, language) is True


def test_option_off_ignores_no_article():
    assert evaluation.is_correct("Haus", "das Haus", {}, "de") is False
    assert evaluation.is_correct("Haus", "das Haus", {"artikel_ignorieren": False}, "de") is False


def test_article_is_compared_case_insensitively_by_default():
    assert evaluation.is_correct("haus", "Das Haus", ARTICLES_ON, "de") is True


def test_cluster_evaluation_uses_the_language_too():
    outcome = evaluation.evaluate_with_cluster("Burg", "das Schloss", ["das Schloss", "die Burg"], ARTICLES_ON, "de")
    assert outcome == "alt"  # matches the alternative "die Burg" once the article is ignored
    assert evaluation.evaluate_with_cluster("Schloss", "das Schloss", ["das Schloss"], ARTICLES_ON, "de") == "correct"
    assert evaluation.evaluate_with_cluster("Haus", "das Schloss", ["das Schloss"], ARTICLES_ON, "de") == "wrong"


def test_article_languages_lists_the_available_codes():
    assert evaluation.article_languages() == ["de", "en", "es", "fr"]


def test_other_settings_still_work():
    assert evaluation.is_correct("CAFE", "café", {"case_sensitiv": False, "akzente_streng": False}) is True
    assert evaluation.is_correct("cafe", "café", {}) is False  # accents strict by default
    assert evaluation.is_correct("  Haus   ", "Haus", {}) is True  # whitespace always normalized
    assert evaluation.is_correct("haus", "Haus", {"case_sensitiv": True}) is False
