# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for doc_files.py (v0.0.18): the shipped documents, where they are,
# the GitHub-style heading anchors and what a click on a link does.

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import doc_files  # noqa: E402
import paths  # noqa: E402
from version import REPO_URL  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_four_documents_in_a_fixed_order_with_language_in_the_label():
    labels = [d["label"] for d in doc_files.DOCUMENTS]
    assert labels == ["README (Deutsch)", "README (English)", "Anleitung (Deutsch)", "User Guide (English)"]
    names = [d["name"] for d in doc_files.DOCUMENTS]
    assert len(set(names)) == 4 and len({d["repo_path"] for d in doc_files.DOCUMENTS}) == 4


@pytest.mark.parametrize("name", [d["name"] for d in doc_files.DOCUMENTS])
def test_from_source_the_documents_are_found_in_the_repository(name):
    path = doc_files.doc_path(name)
    assert path is not None and path.is_file()
    assert REPO_ROOT in path.parents


def test_an_unknown_name_is_not_a_document():
    assert doc_files.doc_path("config.json") is None
    assert doc_files.doc_path("../README.md") is None


def test_frozen_the_documents_are_looked_up_in_info_next_to_the_exe(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    assert doc_files.doc_path("README.md") is None  # nothing shipped yet
    (tmp_path / "info").mkdir()
    (tmp_path / "info" / "README.md").write_text("# x", encoding="utf-8")
    assert doc_files.doc_path("README.md") == tmp_path / "info" / "README.md"
    assert doc_files.doc_path("User_Guide.md") is None  # missing one by one


@pytest.mark.parametrize(
    "heading,slug",
    [
        ("1. Installation und erster Start", "1-installation-und-erster-start"),
        ("10. PIN, Datenschutz und Sicherheit", "10-pin-datenschutz-und-sicherheit"),
        ("5. Vokabeln suchen, bearbeiten und löschen", "5-vokabeln-suchen-bearbeiten-und-löschen"),
        ("11. A second child, updates and backups", "11-a-second-child-updates-and-backups"),
        ("Was geschützt ist — und was nicht", "was-geschützt-ist--und-was-nicht"),
    ],
)
def test_heading_slug_follows_github(heading, slug):
    assert doc_files.heading_slug(heading) == slug


def test_a_repeated_heading_gets_a_counter():
    assert doc_files.unique_slugs(["Die PIN", "Test", "Die PIN", "Die PIN"]) == [
        "die-pin", "test", "die-pin-1", "die-pin-2",
    ]


# ------------------------------------------------------------------ links

def test_an_anchor_stays_in_the_document():
    assert doc_files.resolve_link("README.md", "#known-limitations") == ("anchor", "known-limitations")


@pytest.mark.parametrize(
    "current,link,name",
    [
        ("README.md", "README.de.md", "README.de.md"),
        ("README.md", "docs/User_Guide.md", "User_Guide.md"),
        ("README.de.md", "docs/Bedienungsanleitung.md", "Bedienungsanleitung.md"),
        ("Bedienungsanleitung.md", "User_Guide.md", "User_Guide.md"),
        ("User_Guide.md", "Bedienungsanleitung.md", "Bedienungsanleitung.md"),
        ("User_Guide.md", "./Bedienungsanleitung.md", "Bedienungsanleitung.md"),
    ],
)
def test_a_link_to_a_shipped_document_stays_inside_the_app(current, link, name):
    assert doc_files.resolve_link(current, link) == ("doc", name, "")


def test_a_link_into_another_document_keeps_its_fragment():
    assert doc_files.resolve_link("README.md", "docs/User_Guide.md#4-importing-words") == (
        "doc", "User_Guide.md", "4-importing-words",
    )


def test_a_relative_link_to_something_not_shipped_goes_to_the_repository():
    assert doc_files.resolve_link("README.md", "docs/DEVELOPMENT.md") == (
        "web", f"{REPO_URL}/blob/main/docs/DEVELOPMENT.md",
    )
    assert doc_files.resolve_link("README.md", "LICENSE") == ("web", f"{REPO_URL}/blob/main/LICENSE")
    # relative to the document's own place in the repository
    assert doc_files.resolve_link("User_Guide.md", "DEVELOPMENT.md") == (
        "web", f"{REPO_URL}/blob/main/docs/DEVELOPMENT.md",
    )


@pytest.mark.parametrize(
    "link",
    [
        "https://github.com/Wewoc/Vocabulary-Trainer/issues",
        "https://github.com/wewoc",
        "HTTPS://GITHUB.COM/WEWOC/Vocabulary-Trainer",
    ],
)
def test_project_pages_on_github_open_in_the_browser(link):
    assert doc_files.resolve_link("README.md", link) == ("web", link)


@pytest.mark.parametrize(
    "link",
    [
        "https://example.com/",
        "http://github.com/Wewoc/x",  # not https
        "https://github.com/someone-else/repo",
        "https://github.com.evil.example/Wewoc/",
        "mailto:someone@example.com",
        "file:///C:/Windows/notepad.exe",
        "javascript:alert(1)",
        "../outside.md",
        "../../etc/passwd",
        "",
    ],
)
def test_everything_else_is_ignored(link):
    assert doc_files.resolve_link("README.md", link) == ("ignore",)
