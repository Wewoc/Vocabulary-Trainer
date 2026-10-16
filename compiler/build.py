#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# compiler/build.py
# Builds the Vokabeltrainer as a --onedir PyInstaller package
# (Vocabulary_trainer.exe).
#
# --onedir instead of --onefile: see requirements 9 —
# faster startup, fewer antivirus false positives, more reliable with
# native dependencies (cryptography) than --onefile's DLL unpacking.
#
# dist/Vocabulary_trainer/ is disposable build output, not a persistent
# install — it is wiped clean before every build. The hand-off unit is the
# release ZIP.
#
# Also builds update.exe alongside the app by default (see
# build_updater_exe()) — the install/update GUI from
# compiler/update_installer.py, shipped inside the same release ZIP.
#
# Run from the project root:
#     python compiler/build.py
#     python compiler/build.py --no-zip
#     python compiler/build.py --no-updater

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import build_manifest as manifest


def check_source(root: Path):
    required = [manifest.ENTRY_POINT, "requirements.txt", *manifest.INFO_FILES,
                manifest.INFO_IMAGES, manifest.LICENSE_FILE]
    missing = [name for name in required if not (root / name).exists()]
    if missing:
        print(f"  [build] Not a vokabeltrainer checkout (missing {', '.join(missing)}): {root}")
        raise SystemExit(1)


def ensure_build_venv(root: Path) -> Path:
    """
    Creates (if missing) or reuses a project-local build venv at
    .venv-build/, installs requirements.txt + PyInstaller into it, returns
    its python executable.

    Deliberately project-local, not a shared system-wide location: keeps
    whatever else happens to be installed in the machine's global Python
    (or another project's venv) out of PyInstaller's Analysis step, at the
    cost of nothing more than one `pip install` per dependency change.
    """
    print("\n[1/4] Checking build venv ...")
    venv_dir = root / ".venv-build"
    venv_python = venv_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

    if not venv_python.exists():
        print(f"  Not found at {venv_dir} — creating ...")
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
    else:
        print(f"  Reusing existing venv: {venv_dir}")

    subprocess.check_call([str(venv_python), "-m", "pip", "install", "-q",
                            "-r", str(root / "requirements.txt")])
    subprocess.check_call([str(venv_python), "-m", "pip", "install", "-q", "pyinstaller"])
    print("  Build venv ready.")
    return venv_python


def build_exe(root: Path, venv_python: Path, dist_dir: Path):
    print("\n[2/4] Building EXE (--onedir) ...")

    if dist_dir.exists():
        print(f"  Clearing previous build output: {dist_dir}")
        shutil.rmtree(dist_dir)

    sep = ";" if sys.platform == "win32" else ":"
    add_data_args = []
    for src, dest in manifest.DATA_FILES:
        add_data_args += ["--add-data", f"{root / src}{sep}{dest}"]

    hidden_args = []
    for h in manifest.HIDDEN_IMPORTS:
        hidden_args += ["--hidden-import", h]

    paths_args = []
    for p in manifest.EXTRA_PATHS:
        paths_args += ["--paths", str(root / p)]

    cmd = [
        str(venv_python), "-m", "PyInstaller",
        "--onedir",
        "--noconsole",
        "--name", manifest.APP_NAME,
        "--distpath", str(root / "dist"),
        "--workpath", str(root / "build"),
        "--specpath", str(Path(__file__).parent),
        *paths_args,
        *add_data_args,
        *hidden_args,
        str(root / manifest.ENTRY_POINT),
    ]
    result = subprocess.run(cmd, cwd=str(root))
    if result.returncode != 0:
        print("\n  [build] PyInstaller failed — see output above.")
        raise SystemExit(1)

    if not dist_dir.exists():
        print(f"  [build] PyInstaller reported success but {dist_dir} doesn't exist.")
        raise SystemExit(1)


def build_updater_exe(root: Path, venv_python: Path, dist_dir: Path):
    """
    Builds compiler/update_installer.py as a second, standalone EXE —
    --onefile, placed directly in dist_dir (next to the app's own exe and
    _internal/), not a subfolder, so it ships inside the same release ZIP.
    Needs its own --paths entry (compiler/) so its `import build_manifest`
    resolves the same way start.py's flat imports do for the app build.
    Tkinter-only — no extra pip installs needed beyond the main build venv.
    """
    print("\n[3/4] Building updater EXE (--onefile) ...")

    cmd = [
        str(venv_python), "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name", manifest.UPDATER_NAME,
        "--distpath", str(dist_dir),
        "--workpath", str(root / "build" / "updater"),
        "--specpath", str(Path(__file__).parent),
        "--paths", str(Path(__file__).parent),
        str(root / manifest.UPDATER_ENTRY_POINT),
    ]
    result = subprocess.run(cmd, cwd=str(root))
    if result.returncode != 0:
        print("\n  [build] PyInstaller failed while building the updater — see output above.")
        raise SystemExit(1)

    exe_name = manifest.UPDATER_NAME + (".exe" if sys.platform == "win32" else "")
    exe_path = dist_dir / exe_name
    if not exe_path.exists():
        print(f"  [build] PyInstaller reported success but {exe_path} doesn't exist.")
        raise SystemExit(1)
    print(f"  {exe_path}")


def copy_external_defaults(root: Path, dist_dir: Path):
    if not manifest.EXTERNAL_DEFAULTS:
        return
    print("\n  Copying editable defaults ...")
    for name in manifest.EXTERNAL_DEFAULTS:
        src = root / name
        if not src.exists():
            print(f"  [build] Warning: {name} not found in {root} — skipped.")
            continue
        shutil.copy2(src, dist_dir / name)
        print(f"  {name} -> {dist_dir / name}")


def copy_info(root: Path, dist_dir: Path):
    """Puts the documentation next to the exe (see build_manifest.INFO_*):
    the four documents flat into info/, the screenshots into info/bilder/,
    LICENSE beside the exe. Runs after build_exe(), which wipes dist_dir."""
    print("\n  Copying documentation ...")
    info_dir = dist_dir / manifest.INFO_DIR
    info_dir.mkdir(parents=True, exist_ok=True)
    for rel in manifest.INFO_FILES:
        src = root / rel
        shutil.copy2(src, info_dir / src.name)
        print(f"  {rel} -> {info_dir / src.name}")
    images = root / manifest.INFO_IMAGES
    shutil.copytree(images, info_dir / images.name, dirs_exist_ok=True)
    print(f"  {manifest.INFO_IMAGES}/ -> {info_dir / images.name}")
    shutil.copy2(root / manifest.LICENSE_FILE, dist_dir / manifest.LICENSE_FILE)
    print(f"  {manifest.LICENSE_FILE} -> {dist_dir / manifest.LICENSE_FILE}")


def build_zip(dist_dir: Path):
    zip_path = dist_dir.parent / f"{manifest.APP_NAME}.zip"
    print(f"\n[4/4] Creating {zip_path.name} ...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in dist_dir.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(dist_dir.parent))
    print(f"  -> {zip_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Build the Vokabeltrainer as a --onedir PyInstaller package.")
    parser.add_argument("--no-zip", action="store_true", help="Skip creating the release ZIP.")
    parser.add_argument("--no-updater", action="store_true",
                         help="Skip building update.exe (the install/update GUI). "
                              "Built by default, included in the release ZIP alongside the app.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent  # compiler/ -> project root
    check_source(root)

    venv_python = ensure_build_venv(root)

    dist_dir = root / "dist" / manifest.APP_NAME
    build_exe(root, venv_python, dist_dir)
    copy_external_defaults(root, dist_dir)
    copy_info(root, dist_dir)

    if not args.no_updater:
        build_updater_exe(root, venv_python, dist_dir)
    else:
        print("\nupdate.exe not included (--no-updater given).")

    if not args.no_zip:
        build_zip(dist_dir)

    print(f"\n  Build finished: {dist_dir}")


if __name__ == "__main__":
    main()
