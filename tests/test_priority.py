# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for priority.py: the quiz set has exactly the requested size
# (v0.0.10.11) and follows the priority cascade.

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import priority  # noqa: E402


def _entries(n: int) -> list[dict]:
    return [{"UUID_A": f"a{i}", "UUID_B": f"b{i}", "Datum": f"2026-10-{i + 1:02d}"} for i in range(n)]


@pytest.mark.parametrize("count", [1, 2, 3, 5, 20])
def test_all_new_vocab_gives_exactly_the_requested_size(count):
    assert len(priority.build_quiz_set(_entries(30), {}, count=count)) == count


def test_more_than_available_returns_everything():
    assert len(priority.build_quiz_set(_entries(4), {}, count=50)) == 4


def test_no_entries_gives_empty_set():
    assert priority.build_quiz_set([], {}, count=5) == []


def test_never_tested_first_then_newest_first():
    entries = _entries(5)
    stats = {"a4": {"correct_count": 3}}  # the newest word, but already tested
    chosen = priority.build_quiz_set(entries, stats, count=2)
    assert {e["UUID_A"] for e in chosen} == {"a3", "a2"}  # newest never-tested words


def test_tested_words_with_equal_date_follow_error_rate():
    # Cascade (requirements 4): never tested > newest date > error rate, so
    # the error rate only decides among words captured on the same date.
    entries = [{**e, "Datum": "2026-10-01"} for e in _entries(3)]
    stats = {
        "a0": {"correct_count": 5, "wrong_count": 0},
        "a1": {"correct_count": 1, "wrong_count": 4},
        "a2": {"correct_count": 3, "wrong_count": 2},
    }
    chosen = priority.build_quiz_set(entries, stats, count=1)
    assert chosen[0]["UUID_A"] == "a1"  # highest error rate


def test_uuid_field_selects_the_tracked_side():
    entries = _entries(2)
    stats = {"b1": {"correct_count": 9}}  # only the B side of entry 1 is tested
    chosen = priority.build_quiz_set(entries, stats, count=1, uuid_field="UUID_B")
    assert chosen[0]["UUID_B"] == "b0"


def test_order_is_shuffled_but_membership_is_not():
    entries = _entries(30)
    expected = {e["UUID_A"] for e in priority.prioritize(entries, {})[:10]}
    orders = set()
    for _ in range(20):
        chosen = priority.build_quiz_set(entries, {}, count=10)
        assert {e["UUID_A"] for e in chosen} == expected
        orders.add(tuple(e["UUID_A"] for e in chosen))
    assert len(orders) > 1
