# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# Tests for the documentation that ships with the app (v0.0.18): the build
# manifest, build.copy_info(), update.exe's copy logic and the in-app viewer
# have to agree on where README, guides, screenshots and LICENSE end up.
# No PyInstaller run: the folder layout is built the way build.py builds it.

import importlib.util
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "compiler"))

import build_manifest as manifest  # noqa: E402
import doc_files  # noqa: E402
import paths  # noqa: E402


def _load(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / "compiler" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build = _load("vt_build_script", "build.py")
update_installer = _load("vt_update_installer", "update_installer.py")


def _fake_dist(tmp_path: Path) -> Path:
    """What build_exe() leaves behind, plus copy_info() as build.py runs it."""
    dist = tmp_path / "dist" / manifest.APP_NAME
    (dist / "_internal").mkdir(parents=True)
    (dist / f"{manifest.APP_NAME}.exe").write_bytes(b"exe")
    build.copy_info(ROOT, dist)
    return dist


# --------------------------------------------------------------- manifest

def test_info_files_match_the_documents_the_app_knows():
    # the order differs (buttons: German first), the set of files must not
    assert sorted(Path(p).name for p in manifest.INFO_FILES) == sorted(d["name"] for d in doc_files.DOCUMENTS)
    assert sorted(manifest.INFO_FILES) == sorted(d["repo_path"] for d in doc_files.DOCUMENTS)


def test_every_source_of_the_documentation_exists_in_the_repository():
    for rel in [*manifest.INFO_FILES, manifest.INFO_IMAGES, manifest.LICENSE_FILE]:
        assert (ROOT / rel).exists(), rel
    assert len(list((ROOT / manifest.INFO_IMAGES).glob("*.png"))) >= 6


def test_the_images_folder_keeps_the_name_the_guides_refer_to():
    assert Path(manifest.INFO_IMAGES).name == "bilder"


def test_update_exe_carries_the_documentation_along():
    assert manifest.ONEDIR_ITEMS == [
        f"{manifest.APP_NAME}.exe", "_internal", manifest.INFO_DIR, manifest.LICENSE_FILE,
    ]


# ------------------------------------------------------------ build step

def test_copy_info_builds_the_expected_layout(tmp_path):
    dist = _fake_dist(tmp_path)
    info = dist / "info"
    assert sorted(p.name for p in info.iterdir() if p.is_file()) == sorted(d["name"] for d in doc_files.DOCUMENTS)
    assert sorted(p.name for p in (info / "bilder").iterdir()) == sorted(
        p.name for p in (ROOT / "docs" / "bilder").iterdir()
    )
    assert (dist / "LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes()
    assert (info / "User_Guide.md").read_bytes() == (ROOT / "docs" / "User_Guide.md").read_bytes()


def test_copy_info_can_run_twice(tmp_path):
    dist = _fake_dist(tmp_path)
    build.copy_info(ROOT, dist)  # dirs_exist_ok, no error
    assert (dist / "info" / "README.md").is_file()


def test_the_build_refuses_a_checkout_without_the_documentation(tmp_path):
    for rel in [manifest.ENTRY_POINT, "requirements.txt", manifest.LICENSE_FILE, *manifest.INFO_FILES]:
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("x", encoding="utf-8")
    with pytest.raises(SystemExit):  # screenshots folder missing
        build.check_source(tmp_path)
    (tmp_path / manifest.INFO_IMAGES).mkdir(parents=True)
    build.check_source(tmp_path)  # complete now: no exit


# ------------------------------------------------------ update.exe copying

def test_update_installer_sees_a_complete_package(tmp_path):
    dist = _fake_dist(tmp_path)
    assert update_installer.check_source(dist) == []


def test_update_installer_reports_missing_documentation(tmp_path):
    dist = tmp_path / "dist" / manifest.APP_NAME
    (dist / "_internal").mkdir(parents=True)
    (dist / f"{manifest.APP_NAME}.exe").write_bytes(b"exe")
    assert update_installer.check_source(dist) == ["info", "LICENSE"]


def test_an_update_brings_the_documentation_and_leaves_the_instance_alone(tmp_path):
    dist = _fake_dist(tmp_path)
    instance = tmp_path / "child"
    (instance / "daten" / "vokabeln").mkdir(parents=True)
    (instance / "daten" / "vokabeln" / "englisch.csv").write_text("mine", encoding="utf-8")
    (instance / "metadaten").mkdir()
    (instance / "metadaten" / "tracking.enc").write_bytes(b"progress")
    (instance / "config.json").write_text('{"pin_hash": "keep"}', encoding="utf-8")
    (instance / "logs").mkdir()
    (instance / "logs" / "app.log").write_text("log", encoding="utf-8")

    update_installer.copy_payload(dist, instance, lambda line: None)

    assert (instance / "info" / "User_Guide.md").is_file()
    assert (instance / "info" / "bilder" / "management.png").is_file()
    assert (instance / "LICENSE").is_file()
    assert (instance / "daten" / "vokabeln" / "englisch.csv").read_text(encoding="utf-8") == "mine"
    assert (instance / "metadaten" / "tracking.enc").read_bytes() == b"progress"
    assert (instance / "config.json").read_text(encoding="utf-8") == '{"pin_hash": "keep"}'
    assert (instance / "logs" / "app.log").read_text(encoding="utf-8") == "log"


# ------------------------------------- the runtime finds what the build made

def test_the_installed_app_finds_every_document_where_the_build_put_it(tmp_path, monkeypatch):
    dist = _fake_dist(tmp_path)
    instance = tmp_path / "child"
    update_installer.copy_payload(dist, instance, lambda line: None)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths, "base_dir", lambda: instance)
    for entry in doc_files.DOCUMENTS:
        assert doc_files.doc_path(entry["name"]) == instance / "info" / entry["name"]


def test_the_viewer_shows_the_guides_with_all_screenshots_from_an_installed_copy(tmp_path, monkeypatch):
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])  # noqa: F841
    dist = _fake_dist(tmp_path)
    instance = tmp_path / "child"
    update_installer.copy_payload(dist, instance, lambda line: None)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths, "base_dir", lambda: instance)

    from PyQt6.QtGui import QImage

    from gui.dialogs.doc_viewer_dialog import DocViewerDialog

    for name in ("Bedienungsanleitung.md", "User_Guide.md"):
        dialog = DocViewerDialog(None, name)
        assert dialog._message_label.isHidden(), name
        names = []
        block = dialog._browser.document().begin()
        while block.isValid():
            iterator = block.begin()
            while not iterator.atEnd():
                fmt = iterator.fragment().charFormat()
                if fmt.isImageFormat():
                    names.append(fmt.toImageFormat().name())
                iterator += 1
            block = block.next()
        assert len(names) == 6
        for image in names:
            assert not QImage(str(instance / "info" / image)).isNull(), (name, image)
