# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for pin_store.py (requirements 7.1) with a temporary instance
# directory - never touches the real config.json.

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import config  # noqa: E402
import paths  # noqa: E402
import pin_store  # noqa: E402


@pytest.fixture
def instance(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "base_dir", lambda: tmp_path)
    return tmp_path


def test_default_pin_applies_without_hash(instance):
    assert pin_store.verify_pin("1234") is True
    assert pin_store.verify_pin("0000") is False


def test_change_pin_then_verify(instance):
    assert pin_store.change_pin("1234", "secret", "secret") == pin_store.RESULT_OK
    assert pin_store.verify_pin("secret") is True
    assert pin_store.verify_pin("1234") is False


def test_change_pin_wrong_old_pin(instance):
    assert pin_store.change_pin("0000", "secret", "secret") == pin_store.RESULT_WRONG_PIN
    assert config.load_config()["pin_hash"] is None
    assert pin_store.verify_pin("1234") is True


def test_change_pin_too_short(instance):
    assert pin_store.change_pin("1234", "abc", "abc") == pin_store.RESULT_TOO_SHORT
    assert config.load_config()["pin_hash"] is None


def test_change_pin_repeat_mismatch(instance):
    assert pin_store.change_pin("1234", "secret", "secreT") == pin_store.RESULT_MISMATCH
    assert config.load_config()["pin_hash"] is None


def test_change_pin_requires_current_custom_pin(instance):
    pin_store.change_pin("1234", "first", "first")
    assert pin_store.change_pin("1234", "second", "second") == pin_store.RESULT_WRONG_PIN
    assert pin_store.change_pin("first", "second", "second") == pin_store.RESULT_OK
    assert pin_store.verify_pin("second") is True


def test_hash_is_never_the_pin_in_plaintext(instance):
    pin_store.change_pin("1234", "secret", "secret")
    raw = (instance / "config.json").read_text(encoding="utf-8")
    assert "secret" not in raw
    assert "$" in json.loads(raw)["pin_hash"]


def test_removing_hash_resets_to_default(instance):
    pin_store.change_pin("1234", "secret", "secret")
    cfg = config.load_config()
    cfg["pin_hash"] = None
    config.save_config(cfg)
    assert pin_store.verify_pin("1234") is True
    assert pin_store.verify_pin("secret") is False


def test_malformed_hash_counts_as_unset(instance):
    cfg = config.load_config()
    cfg["pin_hash"] = "not-a-valid-entry"
    config.save_config(cfg)
    assert pin_store.verify_pin("1234") is True
