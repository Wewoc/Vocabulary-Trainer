# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for tracking.py's encryption (fixed app secret, one-time migration
# of pre-v0.0.10.7 files) with a temporary instance directory.

import json
import os
import sys
from pathlib import Path

import pytest
from cryptography.fernet import Fernet, InvalidToken

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import paths  # noqa: E402
import tracking  # noqa: E402


@pytest.fixture
def instance(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    return tmp_path


def _write_with_secret(secret: str, data: dict) -> None:
    salt = os.urandom(16)
    token = Fernet(tracking._derive_key(secret, salt)).encrypt(json.dumps(data).encode("utf-8"))
    path = tracking._tracking_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(salt + token)


def test_missing_file_gives_empty_structure(instance):
    assert tracking.load_tracking() == {"schema_version": 1, "vocab_stats": {}, "sessions": []}


def test_roundtrip(instance):
    data = {"schema_version": 1, "vocab_stats": {"x": {"correct_count": 3}}, "sessions": []}
    tracking.save_tracking(data)
    assert tracking.load_tracking() == data


def test_legacy_file_is_migrated_once(instance):
    data = {"schema_version": 1, "vocab_stats": {"x": {"correct_count": 7}}, "sessions": []}
    _write_with_secret("1234", data)

    assert tracking.load_tracking() == data

    raw = tracking._tracking_path().read_bytes()
    salt, token = raw[:16], raw[16:]
    key = tracking._derive_key(tracking._APP_SECRET, salt)
    assert json.loads(Fernet(key).decrypt(token)) == data


def test_unknown_secret_raises_and_leaves_file_alone(instance):
    _write_with_secret("something-else", {"schema_version": 1})
    before = tracking._tracking_path().read_bytes()
    with pytest.raises(InvalidToken):
        tracking.load_tracking()
    assert tracking._tracking_path().read_bytes() == before
