# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for the import (requirements 5.1, Option B): plan_import() decides
# without saving, commit_import() saves exactly that, import_file() is both
# in one go. LEGACY_IMPORT below is the one-step implementation from before
# the preview existed (v0.0.9.5) - the new two-step path must give the same
# result as that oracle.

import sys
import uuid
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import paths  # noqa: E402
import vocab  # noqa: E402

OWN = "own-instance"
TODAY = date.today().isoformat()


def _entry(i, a=None, b=None, datum="2026-01-01"):
    return {"UUID_A": f"a{i}", "Sprache_A": a or f"wort{i}", "UUID_B": f"b{i}", "Sprache_B": b or f"word{i}", "Datum": datum}


@pytest.fixture
def instance(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    return tmp_path


def LEGACY_IMPORT(language, rows, own_instance_id):
    """The old one-step import, kept verbatim as the reference."""
    entries = vocab.load_entries(language)
    added = skipped_duplicate = skipped_invalid = 0
    for row in rows:
        text_a = (row.get("Sprache_A") or "").strip()
        text_b = (row.get("Sprache_B") or "").strip()
        if not text_a or not text_b:
            skipped_invalid += 1
            continue
        trust_uuids = row.get("quelle_instance_id") == own_instance_id
        if trust_uuids and row.get("UUID_A") and row.get("UUID_B"):
            uuid_a, uuid_b = row["UUID_A"], row["UUID_B"]
            datum = (row.get("Datum") or "").strip() or date.today().isoformat()
        else:
            uuid_a = vocab._find_term_uuid(entries, "A", text_a) or str(uuid.uuid4())
            uuid_b = vocab._find_term_uuid(entries, "B", text_b) or str(uuid.uuid4())
            datum = date.today().isoformat()
        if any(e["UUID_A"] == uuid_a and e["UUID_B"] == uuid_b for e in entries):
            skipped_duplicate += 1
            continue
        entries.append({"UUID_A": uuid_a, "Sprache_A": text_a, "UUID_B": uuid_b, "Sprache_B": text_b, "Datum": datum})
        added += 1
    if added:
        vocab.save_entries(language, entries)
    return {"added": added, "skipped_duplicate": skipped_duplicate, "skipped_invalid": skipped_invalid}


def _comparable(language):
    """The saved list without the random UUIDs of new terms."""
    return [(e["Sprache_A"], e["Sprache_B"], e["Datum"]) for e in vocab.load_entries(language)]


ROWS = [
    {"Sprache_A": "Hallo", "Sprache_B": "Hello"},
    {"Sprache_A": "Tschüss", "Sprache_B": ""},  # invalid (row 2)
    {"Sprache_A": "Haus", "Sprache_B": "house"},  # already in the list
    {"Sprache_A": "Danke", "Sprache_B": "Thank you"},
    {"Sprache_A": "Danke", "Sprache_B": "Thank you"},  # repeats row 4 of the same file
    {"Sprache_A": "", "Sprache_B": "Bye"},  # invalid (row 6)
]


def _seed(instance):
    vocab.save_entries("englisch", [_entry(1, "Haus", "house")])


def test_plan_classifies_rows_and_does_not_save(instance):
    _seed(instance)
    before = (instance / "daten" / "vokabeln" / "englisch.csv").read_bytes()
    plan = vocab.plan_import("englisch", ROWS, OWN)
    assert [(e["Sprache_A"], e["Sprache_B"]) for e in plan["new"]] == [("Hallo", "Hello"), ("Danke", "Thank you")]
    assert plan["skipped_duplicate"] == 2  # "Haus" and the in-file repeat of "Danke"
    assert plan["skipped_invalid"] == 2
    assert plan["invalid_rows"] == [2, 6]
    assert (instance / "daten" / "vokabeln" / "englisch.csv").read_bytes() == before


def test_plan_followed_by_commit_equals_the_legacy_one_step_import(instance):
    _seed(instance)
    legacy_result = LEGACY_IMPORT("englisch", ROWS, OWN)
    legacy_list = _comparable("englisch")

    vocab.save_entries("englisch", [_entry(1, "Haus", "house")])  # reset to the seed
    new_result = vocab.commit_import("englisch", vocab.plan_import("englisch", ROWS, OWN))
    assert new_result == legacy_result
    assert _comparable("englisch") == legacy_list


def test_import_file_still_works_as_one_step(instance):
    _seed(instance)
    result = vocab.import_file("englisch", ROWS, OWN)
    assert result == {"added": 2, "skipped_duplicate": 2, "skipped_invalid": 2}
    assert [e["Sprache_A"] for e in vocab.load_entries("englisch")] == ["Haus", "Hallo", "Danke"]


def test_commit_saves_exactly_the_planned_uuids(instance):
    _seed(instance)
    plan = vocab.plan_import("englisch", ROWS, OWN)
    planned = [(e["UUID_A"], e["UUID_B"]) for e in plan["new"]]
    vocab.commit_import("englisch", plan)
    saved = [(e["UUID_A"], e["UUID_B"]) for e in vocab.load_entries("englisch")]
    assert saved[1:] == planned  # what the preview showed is what got saved


def test_commit_never_adds_a_pair_that_appeared_in_between(instance):
    _seed(instance)
    plan = vocab.plan_import("englisch", [{"Sprache_A": "Hallo", "Sprache_B": "Hello"}], OWN)
    planned = plan["new"][0]
    entries = vocab.load_entries("englisch")
    entries.append(dict(planned))  # the same pair lands in the list before the commit
    vocab.save_entries("englisch", entries)

    result = vocab.commit_import("englisch", plan)
    assert result["added"] == 0 and result["skipped_duplicate"] == 1
    assert len(vocab.load_entries("englisch")) == 2


def test_own_instance_uuids_and_datum_are_trusted(instance):
    rows = [{
        "quelle_instance_id": OWN, "UUID_A": "keep-a", "Sprache_A": "Katze",
        "UUID_B": "keep-b", "Sprache_B": "cat", "Datum": "2025-05-05",
    }]
    entry = vocab.plan_import("englisch", rows, OWN)["new"][0]
    assert (entry["UUID_A"], entry["UUID_B"], entry["Datum"]) == ("keep-a", "keep-b", "2025-05-05")


def test_foreign_instance_uuids_are_not_trusted_and_datum_is_today(instance):
    rows = [{
        "quelle_instance_id": "someone-else", "UUID_A": "x-a", "Sprache_A": "Katze",
        "UUID_B": "x-b", "Sprache_B": "cat", "Datum": "2025-05-05",
    }]
    entry = vocab.plan_import("englisch", rows, OWN)["new"][0]
    assert entry["UUID_A"] != "x-a" and entry["UUID_B"] != "x-b"
    assert entry["Datum"] == TODAY


def test_untrusted_row_reuses_the_uuid_of_an_existing_term(instance):
    vocab.save_entries("englisch", [_entry(1, "Schloss", "castle")])
    plan = vocab.plan_import("englisch", [{"Sprache_A": "Schloss", "Sprache_B": "lock"}], OWN)
    assert plan["new"][0]["UUID_A"] == "a1"  # same German term -> same term UUID (ambiguity cluster)


def test_empty_import_plans_nothing(instance):
    plan = vocab.plan_import("englisch", [], OWN)
    assert plan == {
        "new": [], "skipped_duplicate": 0, "skipped_invalid": 0, "invalid_rows": [],
        "source_rows": [], "resolved_rows": 0, "resolved_pairs": 0, "check_rows": [],
    }
    assert vocab.commit_import("englisch", plan)["added"] == 0


# ------------------------------------------------- resolving cells (v0.0.16)

def _pairs(plan):
    return [(e["Sprache_A"], e["Sprache_B"]) for e in plan["new"]]


def test_resolve_off_is_exactly_the_old_result(instance):
    rows = [{"Sprache_A": "pink; rosa", "Sprache_B": "welcome (to)"}]
    plan = vocab.plan_import("englisch", rows, OWN)
    assert _pairs(plan) == [("pink; rosa", "welcome (to)")]
    assert plan["resolved_rows"] == 0 and plan["check_rows"] == []


def test_resolve_pairs_every_alternative_and_links_the_shared_term(instance):
    rows = [{"Sprache_A": "pink", "Sprache_B": "pink; rosa"}]
    plan = vocab.plan_import("englisch", rows, OWN, resolve=True)
    assert _pairs(plan) == [("pink", "pink"), ("pink", "rosa")]
    assert plan["new"][0]["UUID_A"] == plan["new"][1]["UUID_A"]  # same term -> ambiguity cluster
    assert plan["new"][0]["UUID_B"] != plan["new"][1]["UUID_B"]
    assert plan["source_rows"] == [1, 1]
    assert (plan["resolved_rows"], plan["resolved_pairs"]) == (1, 2)


def test_resolve_counts_only_rows_it_changed(instance):
    rows = [
        {"Sprache_A": "Hallo", "Sprache_B": "Hello"},
        {"Sprache_A": "to say", "Sprache_B": "sagen; sprechen"},
    ]
    plan = vocab.plan_import("englisch", rows, OWN, resolve=True)
    assert plan["source_rows"] == [1, 2, 2]
    assert (plan["resolved_rows"], plan["resolved_pairs"]) == (1, 2)


def test_resolve_marks_rows_with_alternatives_on_both_sides(instance):
    rows = [
        {"Sprache_A": "pink", "Sprache_B": "pink; rosa"},
        {"Sprache_A": "it's (= it is)", "Sprache_B": "er/sie/es ist"},
    ]
    plan = vocab.plan_import("englisch", rows, OWN, resolve=True)
    assert plan["check_rows"] == [2]
    assert len(plan["new"]) == 2 + 6


def test_resolve_never_splits_rows_with_trusted_uuids(instance):
    rows = [{
        "quelle_instance_id": OWN, "UUID_A": "keep-a", "Sprache_A": "und/oder",
        "UUID_B": "keep-b", "Sprache_B": "and/or", "Datum": "2025-05-05",
    }]
    plan = vocab.plan_import("englisch", rows, OWN, resolve=True)
    assert _pairs(plan) == [("und/oder", "and/or")]
    assert plan["resolved_rows"] == 0


def test_resolve_splits_a_foreign_export_row(instance):
    rows = [{"quelle_instance_id": "someone-else", "UUID_A": "x", "Sprache_A": "a/b", "UUID_B": "y", "Sprache_B": "c"}]
    assert _pairs(vocab.plan_import("englisch", rows, OWN, resolve=True)) == [("a", "c"), ("b", "c")]


def test_resolve_row_with_nothing_left_is_invalid(instance):
    rows = [{"Sprache_A": "(Anrede)", "Sprache_B": "Herr"}, {"Sprache_A": "Mr", "Sprache_B": "Herr (Anrede)"}]
    plan = vocab.plan_import("englisch", rows, OWN, resolve=True)
    assert plan["invalid_rows"] == [1] and plan["skipped_invalid"] == 1
    assert _pairs(plan) == [("Mr", "Herr")]


def test_resolve_dedups_pairs_inside_one_file_and_against_the_list(instance):
    vocab.save_entries("englisch", [_entry(1, "Haus", "house")])
    rows = [
        {"Sprache_A": "Haus", "Sprache_B": "house; home"},  # house exists, home is new
        {"Sprache_A": "Haus", "Sprache_B": "home"},  # repeats the pair from row 1
    ]
    plan = vocab.plan_import("englisch", rows, OWN, resolve=True)
    assert _pairs(plan) == [("Haus", "home")]
    assert plan["skipped_duplicate"] == 2


def test_resolve_commit_saves_exactly_the_previewed_pairs(instance):
    rows = [{"Sprache_A": "mein/meine", "Sprache_B": "my"}]
    plan = vocab.plan_import("englisch", rows, OWN, resolve=True)
    assert vocab.commit_import("englisch", plan)["added"] == 2
    assert [(e["Sprache_A"], e["Sprache_B"]) for e in vocab.load_entries("englisch")] == _pairs(plan)
