#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# doc_files.py
# Vokabeltrainer — the documents that ship with the app (README and user
# guide, German and English; v0.0.18): where they are, how a link inside one
# of them is resolved, and the heading anchors Qt does not make for us.
# No Qt, no GUI: the viewer (gui/dialogs/doc_viewer_dialog.py) only displays
# what this module decides.
#
# Layout: in a build the files lie flat in info/ next to the exe (images in
# info/bilder/); from source they are where the repository keeps them
# (repo_path). The repo path is also how links are resolved, so a link like
# docs/User_Guide.md inside README.md works in both layouts.

import posixpath
import re
import sys
from pathlib import Path

import paths
from version import REPO_URL

# The four buttons of the About window, in this order. The label names the
# language of the file, so it is never translated.
DOCUMENTS = [
    {"label": "README (Deutsch)", "name": "README.de.md", "repo_path": "README.de.md"},
    {"label": "README (English)", "name": "README.md", "repo_path": "README.md"},
    {"label": "Anleitung (Deutsch)", "name": "Bedienungsanleitung.md", "repo_path": "docs/Bedienungsanleitung.md"},
    {"label": "User Guide (English)", "name": "User_Guide.md", "repo_path": "docs/User_Guide.md"},
]

# Web links the documents may open: the project's own pages on GitHub only.
_ALLOWED_WEB = ("https://github.com/wewoc/",)
_ALLOWED_WEB_EXACT = ("https://github.com/wewoc",)
_SCHEME = re.compile(r"^[a-z][a-z0-9+.\-]*:")


def document(name: str) -> dict | None:
    return next((d for d in DOCUMENTS if d["name"] == name), None)


def doc_path(name: str) -> Path | None:
    """Where a shipped document is right now, None if it is missing or not
    one of ours. Frozen: info/ next to the exe. From source: the repository
    (never paths.base_dir(): that points elsewhere in tests)."""
    entry = document(name)
    if entry is None:
        return None
    if getattr(sys, "frozen", False):
        candidate = paths.base_dir() / "info" / entry["name"]
    else:
        candidate = Path(__file__).resolve().parent.parent / entry["repo_path"]
    return candidate if candidate.is_file() else None


def heading_slug(text: str) -> str:
    """GitHub-style anchor of a heading: lower case, letters/digits/-/_ stay,
    spaces become hyphens, other characters disappear ("10. PIN, Daten" ->
    "10-pin-daten"). The tables of contents of the guides use these."""
    out = []
    for ch in text.strip().lower():
        if ch.isalnum() or ch in "-_":
            out.append(ch)
        elif ch.isspace():
            out.append("-")
    return "".join(out)


def unique_slugs(headings: list[str]) -> list[str]:
    """Slugs for a list of headings; a repeated one gets -1, -2, ... like on
    GitHub."""
    seen: dict[str, int] = {}
    result = []
    for heading in headings:
        slug = heading_slug(heading)
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        result.append(slug if count == 0 else f"{slug}-{count}")
    return result


def resolve_link(current_name: str, link: str) -> tuple:
    """Decides what a click on `link`, found in the document `current_name`,
    does. Returns one of
      ("anchor", fragment)         scroll to a heading of this document
      ("doc", name, fragment)      show another shipped document
      ("web", url)                 open in the browser (project pages only)
      ("ignore",)                  do nothing
    Only a click ever reaches this; nothing opens by itself."""
    link = link.strip()
    if link.startswith("#"):
        return ("anchor", link[1:])

    lowered = link.lower()
    if lowered.startswith(("http://", "https://")):
        if lowered in _ALLOWED_WEB_EXACT or lowered.startswith(_ALLOWED_WEB):
            return ("web", link)
        return ("ignore",)
    if _SCHEME.match(lowered):  # mailto:, file:, javascript: ...
        return ("ignore",)

    current = document(current_name)
    current_dir = posixpath.dirname(current["repo_path"]) if current else ""
    path, _, fragment = link.partition("#")
    relative = posixpath.normpath(posixpath.join(current_dir, path))
    if not path or relative.startswith("..") or posixpath.isabs(relative) or relative == ".":
        return ("ignore",)

    for entry in DOCUMENTS:
        if entry["repo_path"] == relative:
            return ("doc", entry["name"], fragment)
    url = f"{REPO_URL}/blob/main/{relative}"
    return ("web", f"{url}#{fragment}" if fragment else url)
