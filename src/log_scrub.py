#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# log_scrub.py
# Vokabeltrainer — keeps clear-text vocabulary out of log output
# (requirements 7.2, data model, section 5): enforced by a
# logging filter, not just by the convention "log UUIDs only". Single
# source of the rule - the debug log and the crash handler both use it.
#
# Fail-closed: if the vocabulary can't be loaded (typical during a crash),
# the whole text is replaced by a placeholder, never passed through.
# Known limit: terms shorter than _MIN_TERM_LENGTH are not scrubbed,
# replacing "a"/"to" would shred every log line.
#
# vocab.load_entries() is called from here, so it must never log itself
# (it would recurse into this filter).

import logging
import re

_MIN_TERM_LENGTH = 3
_TERM_PLACEHOLDER = "<term>"
UNAVAILABLE = "<unavailable>"


def _known_terms() -> list[str]:
    import vocab  # local import: vocab -> logging -> this module would cycle

    terms = set()
    for language in vocab.list_languages():
        for entry in vocab.load_entries(language):
            for field in ("Sprache_A", "Sprache_B"):
                text = (entry.get(field) or "").strip()
                if len(text) >= _MIN_TERM_LENGTH:
                    terms.add(text)
    return sorted(terms, key=len, reverse=True)


def scrub(text: str) -> str:
    """Replaces every known vocabulary term (whole word, case-insensitive)
    with a placeholder. Returns UNAVAILABLE if the terms can't be read."""
    try:
        terms = _known_terms()
        if not terms:
            return text
        pattern = "|".join(re.escape(term) for term in terms)
        return re.sub(rf"(?<!\w)(?:{pattern})(?!\w)", _TERM_PLACEHOLDER, text, flags=re.IGNORECASE)
    except Exception:  # noqa: BLE001 - fail-closed on anything at all
        return UNAVAILABLE


class ScrubFilter(logging.Filter):
    """Scrubs message, arguments and exception text of every record."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.msg = scrub(record.getMessage())
            record.args = ()
            if record.exc_info:
                formatted = logging.Formatter().formatException(record.exc_info)
                record.exc_text = scrub(formatted)
                record.exc_info = None
        except Exception:  # noqa: BLE001
            record.msg = UNAVAILABLE
            record.args = ()
            record.exc_info = None
            record.exc_text = None
        return True
