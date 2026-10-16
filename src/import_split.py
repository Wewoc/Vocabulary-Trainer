#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# import_split.py
# Vokabeltrainer — resolves one cell of a hand-made vocabulary CSV into its
# alternatives (see requirements 5.1, v0.0.16). Books
# and AI-made lists squeeze several meanings into one cell ("dein/deine;
# euer/eure"), add hints ("Herr (Anrede)") or a long form ("I'm (= I am)").
# The trainer wants one meaning per entry - the same term appearing in
# several entries is what makes an ambiguity cluster (requirements 3.3).
# Pure text function, Leaf-Node: no project imports. Which rows may be
# resolved at all is vocab.plan_import()'s decision, not this module's.

import re

# "(= I am)": the long form of an abbreviation - becomes a second variant.
_LONG_FORM = re.compile(r"\s*\(\s*=\s*([^()]*?)\s*\)")
# "(Anrede)", "(to)": a hint, set off by a space (or at the start) - dropped.
_HINT = re.compile(r"(?:^|(?<=\s))\([^()]*\)")
# "Sei(d)": letters attached to the word - variants with and without.
_ATTACHED = re.compile(r"(?<=\w)\(([^()]*)\)")


def _top_level_parts(text: str) -> list[str] | None:
    """Splits at ';' and '/' outside parentheses. None if the parentheses
    don't balance - such a cell is left alone."""
    parts: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                return None
        elif char in ";/" and depth == 0:
            parts.append(text[start:index])
            start = index + 1
    if depth != 0:
        return None
    parts.append(text[start:])
    return parts


def _expand(part: str) -> list[str]:
    match = _LONG_FORM.search(part)
    if match:
        before, after = part[: match.start()], part[match.end():]
        # The long form replaces the word it follows ("I'm (= I am)").
        head = before.rsplit(None, 1)[0] + " " if len(before.split()) > 1 else ""
        return _expand(before + after) + _expand(head + match.group(1) + after)
    part = _HINT.sub("", part)
    match = _ATTACHED.search(part)
    if match:
        without = part[: match.start()] + part[match.end():]
        with_letters = part[: match.start()] + match.group(1) + part[match.end():]
        return _expand(without) + _expand(with_letters)
    return [part]


def split_cell(text: str) -> list[str]:
    """Returns the alternatives of one cell: split at ';' and '/' (not
    inside parentheses), "(= long form)" as an extra variant, spaced
    "(hint)" dropped, attached "w(xy)" as both spellings. Whitespace is
    collapsed, empty and repeated alternatives disappear, order is kept.
    A cell with nothing left returns []; unbalanced parentheses return the
    cell unchanged as the only alternative."""
    text = " ".join(text.split())
    if not text:
        return []
    parts = _top_level_parts(text)
    if parts is None:
        return [text]
    alternatives: list[str] = []
    for part in parts:
        for variant in _expand(part):
            variant = " ".join(variant.split())
            if variant and variant not in alternatives:
                alternatives.append(variant)
    return alternatives
