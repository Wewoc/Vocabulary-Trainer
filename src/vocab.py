#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# vocab.py
# Vokabeltrainer — vocab storage, per-term UUID model
# (see data model, section 1, requirements
# 3.1/3.3). Sole owner of daten/vokabeln/*.csv.
#
# Field/column names (UUID_A, Sprache_A, ...) and the directory path
# match the data contract documented in the data model — not
# translated, even though code comments are English.

import csv
import logging
import uuid
from datetime import date
from pathlib import Path

import evaluation
import import_split
import paths

_log = logging.getLogger(__name__)

_VOCAB_DIR = "daten/vokabeln"
_FIELDNAMES = ["UUID_A", "Sprache_A", "UUID_B", "Sprache_B", "Datum"]


def _csv_path(language: str) -> Path:
    return paths.base_dir() / _VOCAB_DIR / f"{language}.csv"


def list_languages() -> list[str]:
    """Returns all vocab language names (CSV filename stems) currently
    present in daten/vokabeln/, sorted. Empty list if the directory
    doesn't exist yet or holds no CSV files. No selection UI yet — the
    full Test-Konfigurator (language choice, direction, filters) arrives
    at v0.0.9."""
    vocab_dir = paths.base_dir() / _VOCAB_DIR
    if not vocab_dir.is_dir():
        return []
    return sorted(p.stem for p in vocab_dir.glob("*.csv"))


def pick_default_language(default: str = "englisch") -> str:
    """Returns the first available vocab language, or `default` if none
    exist yet. Shared helper for GUI panels that need *some* concrete
    language to operate on even before any list exists (e.g. direct
    entry must work to create the very first list) — real language
    selection arrives with the Test-Konfigurator (v0.0.9)."""
    languages = list_languages()
    return languages[0] if languages else default


def _normalize(text: str) -> str:
    """Normalization for term matching on import/direct entry: trimmed,
    case-insensitive. Fixed, NOT the same as the configurable answer
    evaluation from requirements 3.2 (which scores a child's answer during
    a test, unrelated to this)."""
    return " ".join(text.split()).casefold()


def _search_key(text: str) -> str:
    """Search normalization: accents dropped, whitespace collapsed,
    case-insensitive - so "tschuss" finds "Tschüss"."""
    return " ".join(evaluation.strip_accents(text).split()).casefold()


def search_entries(entries: list[dict], query: str) -> list[dict]:
    """List search: the entries whose Sprache_A or Sprache_B contains
    `query` (substring, ignoring case, accents and extra whitespace), in
    their original order. An empty (or whitespace-only) query returns
    everything. Pure filtering - the data on disk is never touched."""
    needle = _search_key(query)
    if not needle:
        return list(entries)
    return [
        e
        for e in entries
        if needle in _search_key(e["Sprache_A"]) or needle in _search_key(e["Sprache_B"])
    ]


def term_texts() -> dict[str, tuple[str, str]]:
    """UUID -> (text, "A" or "B") over every vocab list - lets the report
    turn the term UUIDs in the tracking back into words. Tracking is keyed
    by the UUID of the prompt side (UUID_A for A->B, UUID_B for B->A), so
    both columns are included."""
    texts: dict[str, tuple[str, str]] = {}
    for language in list_languages():
        for entry in load_entries(language):
            texts.setdefault(entry["UUID_A"], (entry["Sprache_A"], "A"))
            texts.setdefault(entry["UUID_B"], (entry["Sprache_B"], "B"))
    return texts


def load_entries(language: str) -> list[dict]:
    """Reads the canonical vocab list. Empty list if the file doesn't
    exist yet (first run for this language)."""
    path = _csv_path(language)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save_entries(language: str, entries: list[dict]) -> None:
    """Writes the canonical vocab list atomically (temp file + rename)."""
    path = _csv_path(language)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
        writer.writeheader()
        writer.writerows(entries)
    tmp_path.replace(path)


def find_entries_by_uuid(entries: list[dict], column: str, uuid: str) -> list[dict]:
    """Returns all rows sharing this term — the ambiguity cluster for a
    given prompt (requirements 3.3). `column` is "A" or "B": which side is
    the prompt depends on the quiz direction (see
    the project invariants, B->A tracking). Takes an
    already-loaded entries list rather than a language, since callers
    (priority.py, evaluation integration) typically already hold it."""
    uuid_key = f"UUID_{column}"
    return [e for e in entries if e[uuid_key] == uuid]


def _find_term_uuid(entries: list[dict], column: str, text: str) -> str | None:
    """Looks up an existing term **within the same column only** (column
    is 'A' or 'B') via normalized text comparison. Sprache_A and
    Sprache_B are separate term spaces, never matched against each
    other. Returns the existing UUID if found, else None."""
    norm = _normalize(text)
    uuid_key = f"UUID_{column}"
    text_key = f"Sprache_{column}"
    for entry in entries:
        if _normalize(entry[text_key]) == norm:
            return entry[uuid_key]
    return None


def add_entry(
    language: str, text_a: str, text_b: str, date_str: str | None = None
) -> tuple[dict, bool]:
    """Option A — direct entry: adds a word pair additively. Term UUIDs
    are reused if the same text already exists in the respective column
    (automatically creates ambiguity clusters for synonyms, see
    requirements 3.3). If the same (UUID_A, UUID_B) pairing already
    exists, it is returned unchanged instead of being added again
    (additive, never overwriting). Returns (entry, was_added) — callers
    that need to tell "newly added" from "already existed" (e.g. GUI
    feedback) don't have to duplicate the dedup check themselves."""
    entries = load_entries(language)

    uuid_a = _find_term_uuid(entries, "A", text_a) or str(uuid.uuid4())
    uuid_b = _find_term_uuid(entries, "B", text_b) or str(uuid.uuid4())

    for entry in entries:
        if entry["UUID_A"] == uuid_a and entry["UUID_B"] == uuid_b:
            return entry, False

    new_entry = {
        "UUID_A": uuid_a,
        "Sprache_A": text_a,
        "UUID_B": uuid_b,
        "Sprache_B": text_b,
        "Datum": date_str or date.today().isoformat(),
    }
    entries.append(new_entry)
    save_entries(language, entries)
    return new_entry, True


def normalize_import_headers(rows: list[dict], sprache_a_name: str, sprache_b_name: str) -> list[dict]:
    """A Handarbeits-CSV (Option A, hand-maintained by a parent in
    Excel) naturally uses the configured display names as column
    headers (e.g. "Deutsch"/"Englisch", see config.py's
    sprache_a_name/sprache_b_name) rather than the internal
    "Sprache_A"/"Sprache_B" field names - a parent types real language
    names, not technical ones. Renames those columns to the
    Sprache_A/Sprache_B contract if present. Rows already using the
    technical names (e.g. the app's own Export-Datei, Option C) pass
    through unchanged - that machine-to-machine contract is
    independent of the display names, see the data model
    section 1."""
    if not rows or "Sprache_A" in rows[0] or "Sprache_B" in rows[0]:
        return rows
    rename = {}
    if sprache_a_name in rows[0]:
        rename[sprache_a_name] = "Sprache_A"
    if sprache_b_name in rows[0]:
        rename[sprache_b_name] = "Sprache_B"
    if not rename:
        return rows
    return [{rename.get(key, key): value for key, value in row.items()} for row in rows]


def plan_import(language: str, rows: list[dict], own_instance_id: str, resolve: bool = False) -> dict:
    """Option B, step 1 - decides what an import would do WITHOUT saving
    anything, so the user can look at it first (preview, v0.0.13). Works on
    rows already parsed from a CSV file via csv_io.read_csv_file().

    A row's UUID_A/UUID_B are trusted only if its `quelle_instance_id`
    matches `own_instance_id` - a foreign or missing instance_id falls back
    to the same text-based term matching as a first, ID-less direct entry
    (requirements 3.1 correction: a foreign instance's UUIDs must never be
    trusted, or re-importing another instance's export would create
    duplicate terms instead of reusing the local ones). Rows missing
    Sprache_A or Sprache_B are skipped rather than aborting the whole
    import.

    `Datum` handling depends on the same trust decision: a trusted
    (own-instance) row's Datum is preserved (falling back to today's
    date only if missing) - re-importing your own export should keep
    the original Erfassungsdatum (requirements 4's priority cascade reads
    it). An untrusted row (Handarbeits-CSV or a foreign export) always
    gets today's date instead, ignoring whatever Datum the file
    carries (maintainer decision) - that column isn't an authoritative
    Erfassungsdatum coming from a hand-maintained spreadsheet or
    another instance, so it shouldn't drive this instance's own
    newest-first prioritization.

    `resolve=True` (v0.0.16) splits the cells of UNTRUSTED rows into their
    alternatives with import_split.split_cell() and pairs every A
    alternative with every B alternative; the term matching below then
    reuses the UUID of a term that already appeared, which is what makes
    the ambiguity cluster. Trusted rows are never split - their UUIDs name
    exactly one pair. A cell with nothing left after resolving makes the
    row invalid. With resolve=False the result is exactly the pre-0.0.16
    one.

    Returns {"new": [entry dicts, UUIDs and Datum already filled in],
    "skipped_duplicate": int, "skipped_invalid": int, "invalid_rows":
    [data row numbers]} - row 1 is the first row under the header - plus
    "source_rows" (the data row of each entry in "new", same order),
    "resolved_rows"/"resolved_pairs" (rows that resolving changed, and how
    many new entries they gave) and "check_rows" (rows with several
    alternatives on BOTH sides: the cross product may pair things that
    don't belong together, e.g. "it's (= it is)" with "er/sie/es ist").
    A pair that repeats an earlier one of the same file counts as a
    duplicate, exactly as if the earlier one had already been saved."""
    known = load_entries(language)  # working copy: grows as rows are accepted
    new_entries: list[dict] = []
    source_rows: list[int] = []
    check_rows: list[int] = []
    skipped_duplicate = skipped_invalid = 0
    invalid_rows: list[int] = []
    resolved_rows = resolved_pairs = 0

    for row_number, row in enumerate(rows, start=1):
        text_a = (row.get("Sprache_A") or "").strip()
        text_b = (row.get("Sprache_B") or "").strip()
        if not text_a or not text_b:
            skipped_invalid += 1
            invalid_rows.append(row_number)
            continue

        trust_uuids = row.get("quelle_instance_id") == own_instance_id
        changed = False
        if trust_uuids and row.get("UUID_A") and row.get("UUID_B"):
            candidates = [(row["UUID_A"], text_a, row["UUID_B"], text_b)]
            datum = (row.get("Datum") or "").strip() or date.today().isoformat()
        else:
            datum = date.today().isoformat()
            alternatives_a, alternatives_b = [text_a], [text_b]
            if resolve:
                alternatives_a = import_split.split_cell(text_a)
                alternatives_b = import_split.split_cell(text_b)
                if not alternatives_a or not alternatives_b:
                    skipped_invalid += 1
                    invalid_rows.append(row_number)
                    continue
                changed = (alternatives_a, alternatives_b) != (
                    [" ".join(text_a.split())],
                    [" ".join(text_b.split())],
                )
                if len(alternatives_a) > 1 and len(alternatives_b) > 1:
                    check_rows.append(row_number)
            candidates = [(None, a, None, b) for a in alternatives_a for b in alternatives_b]

        produced = 0
        for fixed_a, a, fixed_b, b in candidates:
            uuid_a = fixed_a or _find_term_uuid(known, "A", a) or str(uuid.uuid4())
            uuid_b = fixed_b or _find_term_uuid(known, "B", b) or str(uuid.uuid4())

            if any(e["UUID_A"] == uuid_a and e["UUID_B"] == uuid_b for e in known):
                skipped_duplicate += 1
                continue

            entry = {
                "UUID_A": uuid_a,
                "Sprache_A": a,
                "UUID_B": uuid_b,
                "Sprache_B": b,
                "Datum": datum,
            }
            known.append(entry)
            new_entries.append(entry)
            source_rows.append(row_number)
            produced += 1
        if changed:
            resolved_rows += 1
            resolved_pairs += produced

    return {
        "new": new_entries,
        "skipped_duplicate": skipped_duplicate,
        "skipped_invalid": skipped_invalid,
        "invalid_rows": invalid_rows,
        "source_rows": source_rows,
        "resolved_rows": resolved_rows,
        "resolved_pairs": resolved_pairs,
        "check_rows": check_rows,
    }


def commit_import(language: str, plan: dict) -> dict:
    """Option B, step 2 - saves what plan_import() decided, exactly as
    previewed (same UUIDs). Re-checks each entry's (UUID_A, UUID_B) pair
    against the list as it is now, so a pair that appeared in between can
    never be added twice. Returns {"added": int, "skipped_duplicate": int,
    "skipped_invalid": int}."""
    entries = load_entries(language)
    existing = {(e["UUID_A"], e["UUID_B"]) for e in entries}
    fresh = [e for e in plan["new"] if (e["UUID_A"], e["UUID_B"]) not in existing]
    if fresh:
        entries.extend(fresh)
        save_entries(language, entries)

    added = len(fresh)
    skipped_duplicate = plan["skipped_duplicate"] + (len(plan["new"]) - added)
    _log.info(
        "import language=%s added=%d duplicate=%d invalid=%d",
        language, added, skipped_duplicate, plan["skipped_invalid"],
    )
    return {
        "added": added,
        "skipped_duplicate": skipped_duplicate,
        "skipped_invalid": plan["skipped_invalid"],
    }


def import_file(language: str, rows: list[dict], own_instance_id: str) -> dict:
    """Option B in one go - plan and save without a preview. Same result
    as before the preview existed: {"added", "skipped_duplicate",
    "skipped_invalid"}."""
    return commit_import(language, plan_import(language, rows, own_instance_id))


def export_rows(language: str, own_instance_id: str) -> list[dict]:
    """Option C — builds export rows, tagged with the exporting
    instance's ID (requirements 3.1) so a later import into a different
    instance correctly distrusts these UUIDs instead of creating
    duplicate terms. Pure data — writing the file is the caller's job
    (csv_io.write_csv_file())."""
    entries = load_entries(language)
    _log.info("export language=%s count=%d", language, len(entries))
    return [
        {
            "quelle_instance_id": own_instance_id,
            "UUID_A": e["UUID_A"],
            "Sprache_A": e["Sprache_A"],
            "UUID_B": e["UUID_B"],
            "Sprache_B": e["Sprache_B"],
            "Datum": e["Datum"],
        }
        for e in entries
    ]


def edit_term(language: str, term_uuid: str, new_text: str) -> int:
    """Edit function (requirements 5.1) — corrects a term's text wherever
    its UUID appears, in either the UUID_A or UUID_B column. A term can
    appear in multiple rows (ambiguity cluster, requirements 3.1/3.3), so
    a typo fix must apply everywhere that UUID is used, not just one
    row, or the cluster would end up with inconsistent spellings for
    what is supposed to be the same term. The UUID itself never changes
    — this is UPDATE by ID, not a new entry (requirements 3.1). Returns
    how many rows were updated."""
    entries = load_entries(language)
    updated = 0
    for entry in entries:
        if entry["UUID_A"] == term_uuid:
            entry["Sprache_A"] = new_text
            updated += 1
        if entry["UUID_B"] == term_uuid:
            entry["Sprache_B"] = new_text
            updated += 1
    if updated:
        save_entries(language, entries)
    _log.info("edit_term uuid=%s rows=%d", term_uuid, updated)
    return updated


def delete_entry(language: str, uuid_a: str, uuid_b: str) -> bool:
    """Delete function (requirements 5.1) — removes the specific row
    matching this (UUID_A, UUID_B) pairing. Identified by the pairing,
    not either UUID alone: a term's UUID can appear in other rows
    (ambiguity cluster, requirements 3.3) that must stay untouched.
    Returns whether a matching row was found and removed."""
    entries = load_entries(language)
    remaining = [e for e in entries if not (e["UUID_A"] == uuid_a and e["UUID_B"] == uuid_b)]
    if len(remaining) == len(entries):
        _log.info("delete_entry uuid_a=%s uuid_b=%s found=False", uuid_a, uuid_b)
        return False
    save_entries(language, remaining)
    _log.info("delete_entry uuid_a=%s uuid_b=%s found=True", uuid_a, uuid_b)
    return True
