# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Guard for the files that are published: they must not carry references to
# private documents, a private name, e-mail addresses or local paths. The
# patterns are built from fragments so this file does not match itself.
# It scans the published scope only, so it runs unchanged in the exported copy.

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

SCOPE_DIRS = ["src", "tests", "compiler", "tools"]
SCOPE_FILES = [
    "README.md", "README.de.md", "requirements.txt", ".gitignore",
    "docs/Bedienungsanleitung.md", "docs/User_Guide.md", "docs/DEVELOPMENT.md",
]
TEXT_SUFFIXES = {".py", ".md", ".txt", ".bat", ".csv", ".json", ".toml", ".cfg", ".ini", ""}

FORBIDDEN = {
    "private first name": (r"\bTi" + r"mo\b", 0),
    "private requirements document": (r"Lasten" + r"heft", 0),
    "private data model document": (r"Analyse_" + r"Datenmodell", 0),
    "private invariants document": (r"REFERENCE_" + r"INVARIANTS", 0),
    "private roadmap": (r"\bROAD" + r"MAP\b", 0),
    "private change log": (r"PROTO" + r"KOLL", 0),
    "private e-mail (provider)": (r"gm" + r"x", re.IGNORECASE),
    "private surname": (r"sei" + r"del", re.IGNORECASE),
    "private e-mail (other)": (r"haus" + r"deswahns|resonanz" + r"\.archirekt", re.IGNORECASE),
    "local path (user)": (r"[A-Z]:[\\/]+Us" + r"ers", 0),
    "local path (projects)": (r"[A-Z]:[\\/]+Git" + r"hub", 0),
}
NEVER_SHIPPED_NAMES = {"config.json", "app.log", "tracking.enc"}


def _scope() -> list[Path]:
    found = []
    for directory in SCOPE_DIRS:
        for path in (ROOT / directory).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix in TEXT_SUFFIXES | {".png", ".enc", ".pyc"}:
                found.append(path)
    for name in SCOPE_FILES:
        if (ROOT / name).is_file():
            found.append(ROOT / name)
    return found


def test_the_guard_actually_scans_something():
    texts = [p for p in _scope() if p.suffix in TEXT_SUFFIXES]
    assert len(texts) >= 70  # src + tests + compiler + tools + the public documents


@pytest.mark.parametrize("label", list(FORBIDDEN))
def test_published_files_carry_no_private_reference(label):
    pattern, flags = FORBIDDEN[label]
    regex = re.compile(pattern, flags)
    hits = []
    for path in _scope():
        if path.suffix not in TEXT_SUFFIXES:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if regex.search(line):
                hits.append(f"{path.relative_to(ROOT)}:{number}")
    assert not hits, f"{label}: {hits[:10]}"


def test_no_instance_data_in_the_published_scope():
    names = {p.name for p in _scope() if p.suffix != ".pyc"}
    assert not (names & NEVER_SHIPPED_NAMES), names & NEVER_SHIPPED_NAMES
