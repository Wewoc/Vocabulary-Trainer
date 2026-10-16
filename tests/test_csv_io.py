# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for csv_io.write_table_file() (free-form rows, used by the report).

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import csv_io  # noqa: E402


def test_write_table_file_bom_delimiter_and_blank_row(tmp_path):
    target = tmp_path / "t" / "table.csv"
    csv_io.write_table_file(target, [["a", "b"], [], ["Tschüss", "1,5"]], delimiter=";")
    raw = target.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").splitlines()
    assert lines == ["a;b", "", "Tschüss;1,5"]  # the comma value is not quoted with ';'
    assert not list(target.parent.glob("*.tmp"))  # atomic write leaves no temp file
