#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# config.py
# Vokabeltrainer — Portable-Mode config (see requirements
# 9.2 and data model, section 3). Sole owner of config.json.
# Field names match the data contract documented in the data model —
# not translated, even though code comments are English.

import json
import os
import uuid
from pathlib import Path

import paths

_CONFIG_FILENAME = "config.json"

_DEFAULTS = {
    "instance_id": None,  # generated on first run
    "theme": "ozean",  # see theme.py for the full gallery
    "language": "en",  # UI language (DE/EN switch), see requirements 8
    "bewertung": {
        "case_sensitiv": False,
        "akzente_streng": True,
        "artikel_ignorieren": False,
    },
    "sprache_a_name": "Deutsch",  # display name for Sprache_A, see requirements 3.1/8
    "sprache_b_name": "Englisch",  # display name for Sprache_B
    # Article language codes (evaluation.article_languages(), "" = none) for
    # the "Artikel ignorieren" option - the code of the side being TYPED is
    # used (B for A->B, A for B->A). Defaults match the default names above.
    "sprache_a_code": "de",
    "sprache_b_code": "en",
    "pin_hash": None,  # "salt$hash" once a parent PIN is set, see pin_store.py
    "debug_log_level": "INFO",
}


def _config_path() -> Path:
    return paths.base_dir() / _CONFIG_FILENAME


def load_config() -> dict:
    """Loads config.json relative to the instance folder. If the file or
    individual fields are missing (first run, or a newer version adding
    new fields), defaults are merged in and written back immediately —
    including a freshly generated instance_id if none exists yet."""
    path = _config_path()
    cfg = {}
    if path.exists():
        try:
            cfg = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            cfg = {}

    changed = _merge_defaults(cfg, _DEFAULTS)
    if cfg.get("instance_id") is None:
        cfg["instance_id"] = str(uuid.uuid4())
        changed = True

    if changed:
        save_config(cfg)
    return cfg


def save_config(cfg: dict) -> None:
    """Writes config.json atomically (temp file + os.replace)."""
    path = _config_path()
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp_path, path)


def _merge_defaults(cfg: dict, defaults: dict) -> bool:
    """Recursively fills in missing fields from defaults. Returns whether
    anything was added."""
    changed = False
    for key, default_value in defaults.items():
        if key not in cfg:
            cfg[key] = default_value
            changed = True
        elif isinstance(default_value, dict) and isinstance(cfg.get(key), dict):
            if _merge_defaults(cfg[key], default_value):
                changed = True
    return changed
