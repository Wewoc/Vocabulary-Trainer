# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for report.py (parent report, requirements 6.1) with fixed sample data.

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import csv_io  # noqa: E402
import paths  # noqa: E402
import report  # noqa: E402
import tracking  # noqa: E402
import vocab  # noqa: E402
from gui import i18n  # noqa: E402

LABELS = {key: f"<{key}>" for key in report.LABEL_KEYS}
NAMES = {"A": "Deutsch", "B": "Englisch"}

TERMS = {"u1": ("Haus", "A"), "u2": ("Bye", "B")}  # u3 is a deleted word

DATA = {
    "schema_version": 1,
    "vocab_stats": {
        "u1": {
            "correct_count": 3,
            "wrong_count": 1,
            "alt_count": 0,
            "last_tested": "2026-10-09T10:00:00",
            "history": [
                {"ts": "2026-10-07T10:00:00", "outcome": "wrong"},
                {"ts": "2026-10-08T10:00:00", "outcome": "correct"},
                {"ts": "2026-10-09T10:00:00", "outcome": "correct"},
                {"ts": "2026-10-09T10:01:00", "outcome": "correct"},
            ],
        },
        "u2": {
            "correct_count": 1,
            "wrong_count": 2,
            "alt_count": 1,
            "last_tested": "2026-10-10T10:00:00",
            "history": [
                {"ts": "2026-10-08T10:00:00", "outcome": "wrong"},
                {"ts": "2026-10-09T10:00:00", "outcome": "alt"},
                {"ts": "2026-10-10T10:00:00", "outcome": "wrong"},
                {"ts": "2026-10-10T10:01:00", "outcome": "correct"},
            ],
        },
        "u3": {
            "correct_count": 2,
            "wrong_count": 0,
            "alt_count": 0,
            "last_tested": "2026-10-09T10:00:00",
            "history": [{"ts": "2026-10-09T10:00:00", "outcome": "correct"}] * 2,
        },
    },
    "sessions": [
        {"started_at": "2026-10-08T17:00:00", "ended_at": "2026-10-08T17:05:00", "completed": True},
        {"started_at": "2026-10-10T18:00:00", "ended_at": "2026-10-10T18:10:30", "completed": True},
        {"started_at": "2026-10-09T09:00:00", "ended_at": "2026-10-09T09:20:00", "completed": False},
    ],
}


def test_overall_figures():
    r = report.build_report(DATA, TERMS)
    assert r["tests_completed"] == 2
    assert r["tests_aborted"] == 1
    assert (r["period_from"], r["period_to"]) == ("2026-10-08", "2026-10-10")
    assert r["answered"] == 10  # 4 + 4 + 2
    assert r["words_tested"] == 3
    assert r["wrong"] == 3
    assert r["accuracy"] == pytest.approx(70.0)  # 7 hits (correct + alt) of 10
    assert r["test_seconds"] == 5 * 60 + 10 * 60 + 30  # completed sessions only


def test_per_word_rows_are_sorted_most_mistakes_first():
    words = report.build_report(DATA, TERMS)["words"]
    assert [w["text"] for w in words] == ["Bye", "Haus", None]  # 2, 1, 0 mistakes
    bye = words[0]
    assert (bye["tests"], bye["wrong"], bye["side"]) == (4, 2, "B")
    assert bye["accuracy"] == pytest.approx(50.0)
    assert bye["last_wrong"] == "2026-10-10"
    assert words[1]["last_wrong"] == "2026-10-07"
    assert words[2]["last_wrong"] is None


def test_empty_tracking_gives_a_valid_zero_report():
    r = report.build_report({"schema_version": 1, "vocab_stats": {}, "sessions": []}, {})
    assert r["tests_completed"] == r["tests_aborted"] == r["answered"] == r["wrong"] == 0
    assert r["accuracy"] is None and r["period_from"] is None
    assert r["words"] == []
    rows = report.render_rows(r, LABELS, "en", NAMES)
    assert ["<period>", ""] in rows and ["<accuracy>", ""] in rows


def test_unreadable_timestamps_are_skipped_for_the_test_time():
    data = {
        "vocab_stats": {},
        "sessions": [
            {"started_at": "garbage", "ended_at": "2026-10-10T18:00:00", "completed": True},
            {"started_at": "2026-10-10T19:00:00", "ended_at": "2026-10-10T18:00:00", "completed": True},
            {"started_at": "2026-10-10T20:00:00", "ended_at": "2026-10-10T20:01:00", "completed": True},
        ],
    }
    assert report.build_report(data, {})["test_seconds"] == 60


def test_render_rows_layout_english():
    rows = report.render_rows(report.build_report(DATA, TERMS), LABELS, "en", NAMES)
    assert rows[0] == ["<section_total>"]
    assert ["<tests_completed>", "2"] in rows
    assert ["<period>", "2026-10-08 – 2026-10-10"] in rows
    assert ["<accuracy>", "70.0 %"] in rows
    assert ["<test_time>", "0:15:30"] in rows
    assert [] in rows  # blank row between the two sections
    header = rows.index(["<col_word>", "<col_language>", "<col_tests>", "<col_wrong>", "<col_accuracy>", "<col_last_wrong>"])
    assert rows[header + 1] == ["Bye", "Englisch", "4", "2", "50.0 %", "2026-10-10"]
    assert rows[header + 2] == ["Haus", "Deutsch", "4", "1", "75.0 %", "2026-10-07"]
    assert rows[header + 3] == ["<removed>", "", "2", "0", "100.0 %", ""]


def test_render_rows_uses_decimal_comma_in_german():
    rows = report.render_rows(report.build_report(DATA, TERMS), LABELS, "de", NAMES)
    assert ["<accuracy>", "70,0 %"] in rows


def test_delimiter_follows_the_language():
    assert report.delimiter_for("de") == ";"
    assert report.delimiter_for("en") == ","


def test_every_label_key_has_a_german_and_english_text():
    for key in report.LABEL_KEYS:
        for language in ("de", "en"):
            text = i18n.text(f"report_{key}", language)
            assert text != f"report_{key}", (key, language)


def test_write_report_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    vocab.save_entries(
        "englisch",
        [{"UUID_A": "u1", "Sprache_A": "Haus", "UUID_B": "u2", "Sprache_B": "Bye", "Datum": "2026-10-01"}],
    )
    tracking.save_tracking(DATA)
    target = tmp_path / "out" / "report.csv"
    report.write_report(target, LABELS, "de", NAMES)

    assert target.read_bytes().startswith(b"\xef\xbb\xbf")  # BOM for Excel
    parsed = csv_io.read_csv_file(target)  # sniffs ";" - the file must be readable back
    assert parsed  # at least the first section parsed
    text = target.read_text(encoding="utf-8-sig")
    assert "<tests_completed>;2" in text
    assert "Bye;Englisch;4;2;50,0 %;2026-10-10" in text
