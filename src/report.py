#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# report.py
# Vokabeltrainer — the readable parent report (requirements 6.1, Export
# option C): overall figures plus one row per tested word, as a CSV the
# parents can open in Excel without touching the encrypted tracking.enc.
#
# build_report() and render_rows() are pure (no file access, no GUI): the
# captions come in as a parameter, so this module knows nothing about
# gui/i18n. write_report() is the one function that reads tracking and
# vocab and writes the file - the export panel only calls it.
#
# Decisions (maintainer, v0.0.12): one file with two sections (overall on top, a
# blank row, then the per-word table); the delimiter and decimal separator
# follow the UI language (de: ";" and ",", otherwise "," and ".") so Excel
# opens it correctly either way; test time and period count completed
# sessions only (aborted ones are only counted); words deleted from the
# vocab since being tested stay in the table as "(removed)" so the sums
# still match; the per-word table lists the most mistakes first.
#
# The report contains clear-text vocabulary on purpose - it is meant for
# the parents and goes where they choose, never into the debug log.

import logging
from datetime import datetime
from pathlib import Path

import csv_io
import evaluation
import stats
import tracking
import vocab

_log = logging.getLogger(__name__)

LABEL_KEYS = (
    "section_total",
    "section_words",
    "tests_completed",
    "tests_aborted",
    "period",
    "answered",
    "words_tested",
    "wrong",
    "accuracy",
    "test_time",
    "col_word",
    "col_language",
    "col_tests",
    "col_wrong",
    "col_accuracy",
    "col_last_wrong",
    "removed",
)


def _parse(timestamp):
    try:
        return datetime.fromisoformat(timestamp)
    except (ValueError, TypeError):
        return None


def _test_seconds(completed: list[dict]) -> int:
    """Sum of start->end over completed sessions; a session with an
    unreadable or backwards timestamp pair is skipped, not fatal."""
    total = 0
    for session in completed:
        start, end = _parse(session.get("started_at")), _parse(session.get("ended_at"))
        if start and end and end >= start:
            total += int((end - start).total_seconds())
    return total


def _last_wrong_date(history: list[dict]) -> str | None:
    for entry in reversed(history):
        if entry.get("outcome") == "wrong":
            return str(entry.get("ts", ""))[:10] or None
    return None


def build_report(data: dict, term_texts: dict[str, tuple[str, str]]) -> dict:
    """Overall figures and per-word rows from decrypted tracking data.
    `term_texts` maps a term UUID to (text, "A"|"B"); a UUID missing from
    it (word deleted since) gets text None."""
    sessions = data.get("sessions", [])
    completed = stats.completed_sessions(data)
    vocab_stats = data.get("vocab_stats", {})
    hits, answered = stats.overall_accuracy(vocab_stats)

    words = []
    wrong_total = 0
    for uuid, entry in vocab_stats.items():
        wrong = entry.get("wrong_count", 0)
        tests = entry.get("correct_count", 0) + wrong + entry.get("alt_count", 0)
        wrong_total += wrong
        text, side = term_texts.get(uuid, (None, None))
        hit_count = entry.get("correct_count", 0) + entry.get("alt_count", 0)
        words.append(
            {
                "text": text,
                "side": side,
                "tests": tests,
                "wrong": wrong,
                "accuracy": (hit_count / tests * 100) if tests else None,
                "last_wrong": _last_wrong_date(entry.get("history", [])),
                "_uuid": uuid,
            }
        )
    words.sort(key=lambda w: (-w["wrong"], w["text"] is None, (w["text"] or "").casefold(), w["_uuid"]))

    return {
        "tests_completed": len(completed),
        "tests_aborted": len(sessions) - len(completed),
        "period_from": min((s["started_at"][:10] for s in completed), default=None),
        "period_to": max((s["ended_at"][:10] for s in completed), default=None),
        "answered": answered,
        "words_tested": len(vocab_stats),
        "wrong": wrong_total,
        "accuracy": (hits / answered * 100) if answered else None,
        "test_seconds": _test_seconds(completed),
        "words": words,
    }


def delimiter_for(language: str) -> str:
    return ";" if language == "de" else ","


def render_rows(report: dict, labels: dict[str, str], language: str, language_names: dict[str, str]) -> list[list[str]]:
    """The report as table rows for csv_io.write_table_file(): overall
    section, a blank row, then the per-word table (header row included)."""
    decimal = "," if language == "de" else "."

    def percent(value) -> str:
        return "" if value is None else f"{value:.1f}".replace(".", decimal) + " %"

    hours, rest = divmod(report["test_seconds"], 3600)
    minutes, seconds = divmod(rest, 60)
    period = (
        f"{report['period_from']} – {report['period_to']}" if report["period_from"] else ""
    )

    rows: list[list[str]] = [
        [labels["section_total"]],
        [labels["tests_completed"], str(report["tests_completed"])],
        [labels["tests_aborted"], str(report["tests_aborted"])],
        [labels["period"], period],
        [labels["answered"], str(report["answered"])],
        [labels["words_tested"], str(report["words_tested"])],
        [labels["wrong"], str(report["wrong"])],
        [labels["accuracy"], percent(report["accuracy"])],
        [labels["test_time"], f"{hours}:{minutes:02d}:{seconds:02d}"],
        [],
        [labels["section_words"]],
        [
            labels["col_word"],
            labels["col_language"],
            labels["col_tests"],
            labels["col_wrong"],
            labels["col_accuracy"],
            labels["col_last_wrong"],
        ],
    ]
    for word in report["words"]:
        rows.append(
            [
                word["text"] if word["text"] is not None else labels["removed"],
                language_names.get(word["side"], "") if word["side"] else "",
                str(word["tests"]),
                str(word["wrong"]),
                percent(word["accuracy"]),
                word["last_wrong"] or "",
            ]
        )
    return rows


def write_report(path: Path, labels: dict[str, str], language: str, language_names: dict[str, str]) -> None:
    """Reads the tracking and the vocab lists, builds the report and
    writes it to `path` (UTF-8 with BOM, atomic). Raises OSError if the
    file can't be written."""
    report = build_report(tracking.load_tracking(), vocab.term_texts())
    csv_io.write_table_file(path, render_rows(report, labels, language, language_names), delimiter_for(language))
    _log.info("report exported words=%d tests_completed=%d", len(report["words"]), report["tests_completed"])
