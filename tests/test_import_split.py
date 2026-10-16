# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for import_split.split_cell() (v0.0.16): one CSV cell -> alternatives.
# The cases come from a real vocabulary list made from book photos.

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from import_split import split_cell  # noqa: E402


@pytest.mark.parametrize(
    "cell,expected",
    [
        ("pink; rosa", ["pink", "rosa"]),
        ("dein/deine; euer/eure; Ihr/Ihre", ["dein", "deine", "euer", "eure", "Ihr", "Ihre"]),
        ("der Schüler / die Schülerin; der Student / die Studentin",
         ["der Schüler", "die Schülerin", "der Student", "die Studentin"]),
        ("zuhören; anhören; hören", ["zuhören", "anhören", "hören"]),
    ],
)
def test_splits_at_semicolon_and_slash(cell, expected):
    assert split_cell(cell) == expected


@pytest.mark.parametrize(
    "cell,expected",
    [
        ("I'm (= I am)", ["I'm", "I am"]),
        ("what's (= what is)", ["what's", "what is"]),
        ("willkommen (bei/in)", ["willkommen"]),  # the slash inside the hint must not split
        ("welcome (to)", ["welcome"]),
        ("Herr (Anrede)", ["Herr"]),
        ("der; die (auch Pl.); das", ["der", "die", "das"]),
        ("(to) welcome", ["welcome"]),
    ],
)
def test_parentheses(cell, expected):
    assert split_cell(cell) == expected


def test_letters_attached_to_a_word_give_both_spellings():
    assert split_cell("Sei(d) still.; Rede(t) nicht.") == ["Sei still.", "Seid still.", "Rede nicht.", "Redet nicht."]
    assert split_cell("Schüler(in)") == ["Schüler", "Schülerin"]


def test_a_cell_without_separators_is_unchanged():
    for cell in ["Haus", "Thank you.", "Ich komme aus ...", "life, lives", "das Leben, die Leben"]:
        assert split_cell(cell) == [cell]  # the comma never splits


def test_whitespace_is_collapsed_and_empty_or_repeated_alternatives_disappear():
    assert split_cell("  a ;; b ;a;  ") == ["a", "b"]
    assert split_cell("hello   world") == ["hello world"]


def test_nothing_left_gives_an_empty_list():
    assert split_cell("") == []
    assert split_cell("   ") == []
    assert split_cell("(Anrede)") == []
    assert split_cell(" ; / ") == []


def test_unbalanced_parentheses_leave_the_cell_alone():
    assert split_cell("a (b; c") == ["a (b; c"]
    assert split_cell("a) b/c") == ["a) b/c"]


def test_long_form_in_the_middle_replaces_the_group():
    assert split_cell("it's (= it is) here") == ["it's here", "it is here"]
