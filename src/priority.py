#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# priority.py
# Vokabeltrainer — deterministic priority ordering and quiz-set
# selection (see requirements section 4).
# Leaf-Node: no project imports besides the standard library.

import random
from datetime import date as _date


def _date_ordinal(date_str: str) -> int:
    try:
        return _date.fromisoformat(date_str).toordinal()
    except (ValueError, TypeError):
        return 0


def _total_tests(stats: dict) -> int:
    return stats.get("correct_count", 0) + stats.get("wrong_count", 0) + stats.get("alt_count", 0)


def _priority_key(entry: dict, vocab_stats: dict, uuid_field: str) -> tuple:
    """Deterministic cascade, eindeutige Reihenfolge auch bei Gleichstand
    (requirements 4):
      1. noch nie getestet (never-tested entries sort first)
      2. juengstes Erfassungsdatum (newest first)
      3. Fehlerquote (highest first)
      4. Anzahl Fehler (highest first)
      5. zuletzt getestet (oldest first, to cycle through stale words)
    Descending criteria are negated so a single ascending tuple sort
    produces the full cascade in one pass.

    `uuid_field` ("UUID_A" or "UUID_B") picks which side's identity is
    tracked - the prompt side for the current quiz direction (A->B
    tracks UUID_A, B->A tracks UUID_B, see
    the project invariants)."""
    stats = vocab_stats.get(entry[uuid_field], {})
    total = _total_tests(stats)

    never_tested = 0 if total == 0 else 1
    newest_first = -_date_ordinal(entry.get("Datum", ""))
    wrong = stats.get("wrong_count", 0)
    error_rate_desc = -(wrong / total) if total else 0.0
    wrong_count_desc = -wrong
    last_tested_asc = stats.get("last_tested") or ""

    return (never_tested, newest_first, error_rate_desc, wrong_count_desc, last_tested_asc)


def prioritize(entries: list[dict], vocab_stats: dict, uuid_field: str = "UUID_A") -> list[dict]:
    """Sorts entries per the deterministic priority cascade above."""
    return sorted(entries, key=lambda e: _priority_key(e, vocab_stats, uuid_field))


def build_quiz_set(
    entries: list[dict], vocab_stats: dict, count: int = 20, uuid_field: str = "UUID_A"
) -> list[dict]:
    """Builds the quiz set: exactly the first `count` entries of the
    priority cascade (all of them if there are fewer), then shuffled so
    the presentation order isn't fixed. The number of questions is
    exactly what the user asked for - no contingent mix between new/
    error/rest pools (dropped in v0.0.10.11: the pools could run short
    and silently shrink the set, e.g. 20 requested -> 10 asked on
    all-new vocabulary)."""
    selected = prioritize(entries, vocab_stats, uuid_field)[:count]
    random.shuffle(selected)
    return selected
