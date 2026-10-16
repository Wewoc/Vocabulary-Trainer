#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# evaluation.py
# Vokabeltrainer — answer evaluation (see requirements
# 3.2). Reads the `bewertung` settings documented in
# data model, section 3; those field names stay as
# specified, not translated. Leaf-Node: no project imports.

import re
import unicodedata

# Leading articles to optionally strip before comparing, anchored at the
# start only (never a mid-word replace — "der" inside "Widerstand" stays
# untouched). Fixed per currently used language, not a generic
# multi-language module (requirements 3.2).
_ARTICLES = {
    "en": ["the"],
    "de": ["der", "die", "das"],
    "es": ["el", "la", "los", "las"],
    "fr": ["le", "la", "les"],
}


def article_languages() -> list[str]:
    """Language codes that have an article list (for the settings
    dropdown). A code not in here - e.g. "" - simply ignores no article."""
    return sorted(_ARTICLES)


def _normalize_whitespace(text: str) -> str:
    """Always applied, not configurable: trim + collapse multiple spaces."""
    return " ".join(text.split())


def strip_accents(text: str) -> str:
    """Unicode NFD normalization, dropping combining diacritical marks."""
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _strip_leading_article(text: str, language: str) -> str:
    """Removes a leading article if present, anchored at the string start."""
    for article in _ARTICLES.get(language, []):
        pattern = rf"^{re.escape(article)}\s+"
        stripped = re.sub(pattern, "", text, flags=re.IGNORECASE)
        if stripped != text:
            return stripped
    return text


def is_correct(given: str, expected: str, settings: dict, language: str = "en") -> bool:
    """Evaluates a typed answer against the expected term, per the
    `bewertung` settings (requirements 3.2):
      - whitespace: always normalized, not configurable
      - case_sensitiv (default False): if False, compared case-insensitively
      - akzente_streng (default True): if False, diacritics are stripped
        before comparing
      - artikel_ignorieren (default False): if True, a leading article is
        stripped first

    `language` picks the article list for artikel_ignorieren: the code of
    the language being typed (QuizPanel passes sprache_a_code/
    sprache_b_code from the config, v0.0.15). Defaults to "en"; an unknown
    or empty code ignores no article.

    Only compares against the single expected answer passed in — see
    evaluate_with_cluster() for ambiguity-cluster-aware evaluation."""
    a = _normalize_whitespace(given)
    b = _normalize_whitespace(expected)

    if settings.get("artikel_ignorieren"):
        a = _strip_leading_article(a, language)
        b = _strip_leading_article(b, language)

    if not settings.get("akzente_streng", True):
        a = strip_accents(a)
        b = strip_accents(b)

    if not settings.get("case_sensitiv", False):
        a = a.casefold()
        b = b.casefold()

    return a == b


def evaluate_with_cluster(
    given: str,
    expected: str,
    alternates: list[str],
    settings: dict,
    language: str = "en",
) -> str:
    """Ambiguity-cluster-aware evaluation (requirements 3.3). Returns one
    of three outcomes instead of a bool:
      - "correct": matches the specific expected answer
      - "alt": matches a different answer from the same term's cluster
        (`alternates`, from vocab.find_entries_by_uuid()) but not the
        one being tested — triggers the Nachhaken follow-up in the GUI,
        tracked as its own outcome (data model, section 2),
        never silently counted as correct
      - "wrong": matches neither"""
    if is_correct(given, expected, settings, language):
        return "correct"
    for alternate in alternates:
        if alternate == expected:
            continue
        if is_correct(given, alternate, settings, language):
            return "alt"
    return "wrong"


# A recognized synonym ("alt") counts as a hit, same as "correct" - only
# "wrong" doesn't (maintainer decision, see data model,
# section 2). Single source of truth for this rule - stats.py and
# gui/dialogs/evaluation_dialog.py both read it from here rather than
# each deciding independently what counts as a hit.
_HIT_OUTCOMES = {"correct", "alt"}


def is_hit(outcome: str) -> bool:
    """True for an outcome ("correct"/"wrong"/"alt") that counts as the
    child having gotten the term right."""
    return outcome in _HIT_OUTCOMES
