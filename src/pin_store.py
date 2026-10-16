#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# pin_store.py
# Vokabeltrainer — parent PIN as a plain access code (requirements 7.1,
# simplified in v0.0.10.7). The PIN is NOT an encryption key: tracking.py
# uses its own fixed app secret, so changing or losing the PIN never
# touches tracking.enc.
#
# Storage: a salted PBKDF2 hash ("salt$hash", both hex) in config.json's
# "pin_hash", never the PIN itself. No hash set (null) means the default
# PIN applies; removing the entry resets to the default.

import hashlib
import hmac
import logging
import os

import config

_log = logging.getLogger(__name__)

_DEFAULT_PIN = "1234"
_MIN_LENGTH = 4
_SALT_LENGTH = 16
_ITERATIONS = 200_000

RESULT_OK = "ok"
RESULT_WRONG_PIN = "wrong_pin"
RESULT_TOO_SHORT = "too_short"
RESULT_MISMATCH = "mismatch"


def _hash_pin(pin: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, _ITERATIONS).hex()


def _stored_parts() -> tuple[bytes, str] | None:
    """(salt, hash_hex) from config.json, or None if no PIN is set. A
    malformed entry counts as unset (reset to default) rather than
    locking everyone out."""
    stored = config.load_config()["pin_hash"]
    if not isinstance(stored, str) or "$" not in stored:
        return None
    salt_hex, hash_hex = stored.split("$", 1)
    try:
        return bytes.fromhex(salt_hex), hash_hex
    except ValueError:
        return None


def verify_pin(pin: str) -> bool:
    parts = _stored_parts()
    if parts is None:
        ok = hmac.compare_digest(pin.encode("utf-8"), _DEFAULT_PIN.encode("utf-8"))
    else:
        salt, expected = parts
        ok = hmac.compare_digest(_hash_pin(pin, salt), expected)
    if not ok:
        _log.warning("PIN attempt failed")
    return ok


def change_pin(old: str, new: str, repeat: str) -> str:
    """Sets a new PIN. Returns one of the RESULT_* constants; the config
    is only written on RESULT_OK."""
    if not verify_pin(old):
        return RESULT_WRONG_PIN
    if new != repeat:
        return RESULT_MISMATCH
    if len(new) < _MIN_LENGTH:
        return RESULT_TOO_SHORT

    salt = os.urandom(_SALT_LENGTH)
    cfg = config.load_config()
    cfg["pin_hash"] = f"{salt.hex()}${_hash_pin(new, salt)}"
    config.save_config(cfg)
    _log.info("PIN changed")
    return RESULT_OK
