#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# tracking.py
# Vokabeltrainer — encrypted tracking store (see
# requirements 6/7, the data model
# section 2). Sole owner of metadaten/tracking.enc.
#
# The encryption key is derived from a fixed app secret, deliberately
# NOT from the parent PIN (requirements 7, changed in v0.0.10.7): the PIN
# is only an access code (see pin_store.py), so losing or changing it can
# never cost the tracking data. Files written before v0.0.10.7 used the
# placeholder PIN "1234" as the secret; load_tracking() migrates those
# once on first read.

import json
import logging
import os
from base64 import urlsafe_b64encode
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import paths

_log = logging.getLogger(__name__)

_TRACKING_DIR = "metadaten"
_TRACKING_FILENAME = "tracking.enc"
_SALT_LENGTH = 16
_PBKDF2_ITERATIONS = 600_000
_SCHEMA_VERSION = 1
_APP_SECRET = "Vokabeltrainer/tracking/v1"
_LEGACY_SECRET = "1234"  # pre-v0.0.10.7 files, see load_tracking()


def _tracking_path() -> Path:
    return paths.base_dir() / _TRACKING_DIR / _TRACKING_FILENAME


def _derive_key(secret: str, salt: bytes) -> bytes:
    """PBKDF2-HMAC-SHA256, 600,000 iterations (current OWASP guidance),
    encoded for Fernet."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=_PBKDF2_ITERATIONS,
    )
    return urlsafe_b64encode(kdf.derive(secret.encode("utf-8")))


def _default_data() -> dict:
    return {"schema_version": _SCHEMA_VERSION, "vocab_stats": {}, "sessions": []}


def _decrypt(secret: str, raw: bytes) -> dict:
    salt, token = raw[:_SALT_LENGTH], raw[_SALT_LENGTH:]
    plaintext = Fernet(_derive_key(secret, salt)).decrypt(token)
    return json.loads(plaintext.decode("utf-8"))


def load_tracking() -> dict:
    """Decrypts and returns the tracking store. Returns a fresh, empty
    structure if the file doesn't exist yet (first run). A file written
    before v0.0.10.7 (encrypted with the placeholder PIN "1234") is
    decrypted that way once and immediately re-saved with the app
    secret. Raises cryptography.fernet.InvalidToken if neither secret
    fits — never silently resets the data."""
    path = _tracking_path()
    if not path.exists():
        return _default_data()

    raw = path.read_bytes()
    try:
        return _decrypt(_APP_SECRET, raw)
    except InvalidToken:
        data = _decrypt(_LEGACY_SECRET, raw)
    _log.info("tracking.enc migrated from the pre-v0.0.10.7 key")
    save_tracking(data)
    return data


def save_tracking(data: dict) -> None:
    """Encrypts and writes the tracking store atomically (temp file +
    rename) — the plaintext JSON never touches disk, only the finished
    salt+ciphertext bytes. A fresh random salt is generated on every
    save; nothing needs to persist across saves, the salt travels with
    the ciphertext and is read back out on load."""
    path = _tracking_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    salt = os.urandom(_SALT_LENGTH)
    key = _derive_key(_APP_SECRET, salt)
    token = Fernet(key).encrypt(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_bytes(salt + token)
    tmp_path.replace(path)


_OUTCOME_COUNT_KEYS = {
    "correct": "correct_count",
    "wrong": "wrong_count",
    "alt": "alt_count",
}


def record_outcome(data: dict, uuid_a: str, outcome: str, timestamp: str) -> None:
    """Updates vocab_stats for a Begriffs-UUID in place, given a test
    outcome ("correct"/"wrong"/"alt", see evaluation.evaluate_with_cluster()
    and requirements 3.3). Mutates `data` — the caller still owns calling
    save_tracking() afterward; this function has no file I/O itself."""
    stats = data["vocab_stats"].setdefault(
        uuid_a,
        {"correct_count": 0, "wrong_count": 0, "alt_count": 0,
         "last_tested": None, "history": []},
    )
    stats[_OUTCOME_COUNT_KEYS[outcome]] += 1
    stats["last_tested"] = timestamp
    stats["history"].append({"ts": timestamp, "outcome": outcome})


def record_session(data: dict, started_at: str, ended_at: str, completed: bool) -> None:
    """Appends a session record (see data model, section 2).
    Every session is recorded, finished or not - `completed` distinguishes
    them. Mutates `data` — the caller still owns calling save_tracking()
    afterward; this function has no file I/O itself."""
    data["sessions"].append(
        {"started_at": started_at, "ended_at": ended_at, "completed": completed}
    )
    _log.debug("session recorded completed=%s", completed)
