#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# csv_io.py
# Vokabeltrainer — external CSV file I/O (see
# requirements 5.1). For files outside
# daten/vokabeln/ — an import source the user picked (USB stick), or an
# export destination. The canonical internal store (vocab.py's
# load_entries()/save_entries()) does not use this; it controls its own
# format exactly and doesn't need the tolerance this module provides.
# Leaf-Node: no project imports.

import csv
from pathlib import Path


def read_csv_file(path: Path) -> list[dict]:
    """Reads an externally-sourced CSV, tolerant of the two real-world
    variations Excel produces: UTF-8 with or without a BOM, comma- or
    semicolon-delimited. The official instruction to parents is "CSV
    UTF-8 (Comma delimited)" (requirements 5.1) — this tolerance is a
    safety net for the wrong Excel export option, not a license to skip
    that instruction."""
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if not lines:
        return []
    try:
        dialect = csv.Sniffer().sniff(lines[0], delimiters=",;")
    except csv.Error:
        dialect = csv.excel  # default: comma-delimited
    return list(csv.DictReader(lines, dialect=dialect))


def write_csv_file(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    """Writes UTF-8 with a BOM (utf-8-sig) so the file reopens correctly
    in Excel (umlauts etc.) — matches the "CSV UTF-8" format we ask
    parents to use. Atomic write (temp file + rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    tmp_path.replace(path)


def write_table_file(path: Path, rows: list[list[str]], delimiter: str = ",") -> None:
    """Writes free-form rows (e.g. the report with its two sections and a
    blank row between them) as UTF-8 with a BOM, atomically. `delimiter`
    is chosen by the caller (the report uses ";" for a German Excel)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f, delimiter=delimiter).writerows(rows)
    tmp_path.replace(path)
