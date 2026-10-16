#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# stats.py
# Vokabeltrainer — derived motivational statistics for the Test-tab
# status display (see data model, section 2). Pure
# computation over an already-decrypted tracking dict (vocab_stats +
# sessions) - no file I/O, no encryption, that's tracking.py's job.
# GUI panels call compute() and display the result; no panel computes
# any of this itself (see the project invariants, GUI composition
# principle). Only project import is evaluation.py (also a Leaf-Node),
# for the shared is_hit() definition - see its docstring.
#
# Business rules fixed here, decided with the maintainer (see git history):
#   - A "hit" is `correct` OR `alt` (a recognized synonym counts, see
#     requirements 3.3's Nachhaken-Mechanismus) - only `wrong` breaks a
#     streak or lowers accuracy. Defined once in evaluation.is_hit(),
#     not redefined here (gui/dialogs/evaluation_dialog.py reads the
#     same definition since v0.0.9.3).
#   - Mastery threshold: 10 hits in a row for a single term.
#   - Day-streak / weekly comparison only count sessions with
#     completed=True - an aborted session (Abbrechen or the dialog's
#     close button) never counts, see gui/dialogs/quiz_dialog.py.

from datetime import date, timedelta

import evaluation

MASTERY_THRESHOLD = 10


def overall_accuracy(vocab_stats: dict) -> tuple[int, int]:
    """Returns (hits, answered) summed across every term ever tested."""
    correct = sum(s.get("correct_count", 0) + s.get("alt_count", 0) for s in vocab_stats.values())
    total = sum(
        s.get("correct_count", 0) + s.get("wrong_count", 0) + s.get("alt_count", 0)
        for s in vocab_stats.values()
    )
    return correct, total


def mastered_word_count(vocab_stats: dict, threshold: int = MASTERY_THRESHOLD) -> int:
    """Terms whose most recent `threshold` answers are all hits (needs
    at least `threshold` answers total - a term with fewer attempts
    can't be mastered yet, regardless of how many were correct)."""
    count = 0
    for s in vocab_stats.values():
        history = s.get("history", [])
        if len(history) < threshold:
            continue
        if all(evaluation.is_hit(h["outcome"]) for h in history[-threshold:]):
            count += 1
    return count


def _merged_outcomes(vocab_stats: dict) -> list[str]:
    """Every outcome ever recorded, across all terms, in chronological
    order - streaks run across terms, not per term."""
    entries = [h for s in vocab_stats.values() for h in s.get("history", [])]
    entries.sort(key=lambda h: h["ts"])
    return [h["outcome"] for h in entries]


def correct_streaks(vocab_stats: dict) -> tuple[int, int]:
    """Returns (current, longest) run of hits across every answer ever
    given. A single `wrong` anywhere breaks the streak, regardless of
    which term it was for - deliberately global, not per-term."""
    longest = current = 0
    for outcome in _merged_outcomes(vocab_stats):
        if evaluation.is_hit(outcome):
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return current, longest


def completed_sessions(data: dict) -> list[dict]:
    return [s for s in data.get("sessions", []) if s.get("completed")]


def tests_completed(data: dict) -> int:
    return len(completed_sessions(data))


def last_test_date(data: dict) -> str | None:
    """ISO date (not datetime) of the most recent completed session, or
    None if there isn't one yet."""
    sessions = completed_sessions(data)
    if not sessions:
        return None
    return max(s["ended_at"] for s in sessions)[:10]


def _completed_session_dates(data: dict) -> set[str]:
    return {s["ended_at"][:10] for s in completed_sessions(data)}


def day_streaks(data: dict, today: date | None = None) -> tuple[int, int]:
    """Returns (current, longest) run of consecutive calendar days with
    at least one completed session. `current` is 0 once more than a day
    has passed since the last completed session - `today` is
    overridable for testing, defaults to the real current date."""
    dates = sorted(date.fromisoformat(d) for d in _completed_session_dates(data))
    if not dates:
        return 0, 0

    longest = run = 1
    for i in range(1, len(dates)):
        run = run + 1 if (dates[i] - dates[i - 1]).days == 1 else 1
        longest = max(longest, run)

    today = today or date.today()
    current = run if (today - dates[-1]).days <= 1 else 0
    return current, longest


def week_comparison(data: dict, today: date | None = None) -> tuple[int, int]:
    """Returns (tests this ISO week, tests last ISO week), counted from
    completed sessions' end date. Week runs Monday-Sunday."""
    today = today or date.today()
    this_monday = today - timedelta(days=today.weekday())
    last_monday = this_monday - timedelta(days=7)

    this_week = last_week = 0
    for s in completed_sessions(data):
        d = date.fromisoformat(s["ended_at"][:10])
        if this_monday <= d <= today:
            this_week += 1
        elif last_monday <= d < this_monday:
            last_week += 1
    return this_week, last_week


def compute(data: dict, today: date | None = None) -> dict:
    """Single entry point bundling every derived statistic the
    Test-tab status display needs, so a caller doesn't have to know
    which raw tracking.enc field each one comes from."""
    vocab_stats = data.get("vocab_stats", {})
    correct, answered = overall_accuracy(vocab_stats)
    correct_streak_current, correct_streak_longest = correct_streaks(vocab_stats)
    day_streak_current, day_streak_longest = day_streaks(data, today)
    tests_this_week, tests_last_week = week_comparison(data, today)
    return {
        "tests_completed": tests_completed(data),
        "correct": correct,
        "answered": answered,
        "last_test_date": last_test_date(data),
        "day_streak_current": day_streak_current,
        "day_streak_longest": day_streak_longest,
        "correct_streak_current": correct_streak_current,
        "correct_streak_longest": correct_streak_longest,
        "mastered_words": mastered_word_count(vocab_stats),
        "tests_this_week": tests_this_week,
        "tests_last_week": tests_last_week,
    }
