#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# seed_test_vocab.py
# Vokabeltrainer — developer utility: populates a representative
# "englisch" vocab list for manual testing. NOT part of the shipped app
# (lives in tools/, outside src/, see the project invariants).
# Safe to re-run — vocab.add_entry() is additive, duplicates are skipped.
#
# Includes a couple of deliberate ambiguity clusters (groß -> big/large,
# Schloss -> castle/lock) so the Mehrdeutigkeits-Cluster/Nachhaken
# mechanism (requirements 3.3) has something real to exercise, not just
# plain word pairs.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import vocab  # noqa: E402

_WORDS = [
    ("Haus", "house"),
    ("Baum", "tree"),
    ("Katze", "cat"),
    ("Hund", "dog"),
    ("Buch", "book"),
    ("Tisch", "table"),
    ("Stuhl", "chair"),
    ("Fenster", "window"),
    ("Tür", "door"),
    ("Wasser", "water"),
    ("Brot", "bread"),
    ("Apfel", "apple"),
    ("Schule", "school"),
    ("Lehrer", "teacher"),
    ("Freund", "friend"),
    ("Straße", "street"),
    ("Auto", "car"),
    ("Blume", "flower"),
    ("Sonne", "sun"),
    ("Mond", "moon"),
    # Ambiguity clusters (requirements 3.3) - same Sprache_A, different Sprache_B
    ("groß", "big"),
    ("groß", "large"),
    ("Schloss", "castle"),
    ("Schloss", "lock"),
]


def main() -> None:
    added = duplicate = 0
    for text_a, text_b in _WORDS:
        _, was_added = vocab.add_entry("englisch", text_a, text_b)
        added += was_added
        duplicate += not was_added
    print(f"Seed abgeschlossen: {added} neu, {duplicate} bereits vorhanden.")
    print(f"Gesamtbestand: {len(vocab.load_entries('englisch'))} Zeilen.")


if __name__ == "__main__":
    main()
