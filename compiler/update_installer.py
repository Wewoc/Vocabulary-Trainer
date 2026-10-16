#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# compiler/update_installer.py
#
# Built as its own standalone exe (update.exe, see build_manifest.py /
# build.py) and shipped inside the release ZIP next to Vocabulary_trainer.exe
# and _internal/. Asks for a target folder, then copies those two items into
# it — nothing else. Works for both a fresh install into an empty folder and
# an update of an existing instance: daten/, metadaten/, config.json and
# logs/ are never part of the release ZIP in the first place (see
# requirements 9), so there's nothing to protect against
# accidentally overwriting — the copy source simply doesn't contain it.
# (Crash reports live outside the instance folder, see src/crash_handler.py.)

import shutil
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

import build_manifest as manifest


def source_dir() -> Path:
    """Where update.exe's own payload (Vocabulary_trainer.exe + _internal/)
    lives: next to itself when frozen (ships that way inside the release
    ZIP), or dist/<APP_NAME>/ when run unfrozen for testing straight after
    a build.py run."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent / "dist" / manifest.APP_NAME


def check_source(src: Path) -> list[str]:
    """Returns the ONEDIR_ITEMS missing from src, empty if everything's
    there."""
    return [name for name in manifest.ONEDIR_ITEMS if not (src / name).exists()]


def copy_payload(src: Path, dest: Path, log) -> None:
    for name in manifest.ONEDIR_ITEMS:
        item_src = src / name
        item_dest = dest / name
        log(f"  {name} ...")
        if item_src.is_dir():
            shutil.copytree(item_src, item_dest, dirs_exist_ok=True)
        else:
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item_src, item_dest)
    log("  done.")


def run_gui() -> None:
    src = source_dir()

    root = tk.Tk()
    root.title(f"{manifest.APP_NAME} — Update/Installation")
    root.geometry("560x380")

    ttk.Label(root, text=f"{manifest.APP_NAME.upper()} — UPDATE/INSTALL",
              font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
    ttk.Label(root, text="Replaces only the program (exe + _internal) and the "
                         "documentation (info, LICENSE) in the chosen folder. "
                         "Vocabulary, tracking and settings stay untouched "
                         "— they're never part of this package.",
              wraplength=520, justify="left").pack(anchor="w", padx=10, pady=(4, 10))

    target_var = tk.StringVar(value="")
    row = ttk.Frame(root, padding=(10, 0))
    row.pack(fill="x")
    ttk.Label(row, text="Target folder (the existing or a new child instance):").pack(anchor="w")
    entry_row = ttk.Frame(row)
    entry_row.pack(fill="x", pady=(2, 0))
    entry = ttk.Entry(entry_row, textvariable=target_var, state="readonly", width=60)
    entry.pack(side="left", fill="x", expand=True)

    def _browse():
        chosen = filedialog.askdirectory(title="Choose target folder")
        if chosen:
            target_var.set(chosen)

    ttk.Button(entry_row, text="…", width=3, command=_browse).pack(side="left", padx=(6, 0))

    log_widget = scrolledtext.ScrolledText(root, height=12, state="disabled", font=("Consolas", 9))
    log_widget.pack(fill="both", expand=True, padx=10, pady=10)

    def log(line: str):
        log_widget.configure(state="normal")
        log_widget.insert(tk.END, line + "\n")
        log_widget.see(tk.END)
        log_widget.configure(state="disabled")
        root.update_idletasks()

    missing = check_source(src)
    if missing:
        log(f"[Error] This update.exe is incomplete — missing: {', '.join(missing)}")
        log(f"Expected location: {src}")

    btn_frame = ttk.Frame(root, padding=10)
    btn_frame.pack(fill="x")
    start_btn = ttk.Button(btn_frame, text="Start copying")
    start_btn.pack(side="left")

    def _on_start():
        target_str = target_var.get().strip()
        if not target_str:
            messagebox.showwarning(root.title(), "Please choose a target folder first.")
            return
        if missing:
            messagebox.showerror(root.title(), "Package incomplete — see message above. Aborted.")
            return

        target = Path(target_str).resolve()
        if target == src.resolve():
            messagebox.showerror(
                root.title(),
                "The target folder is the same folder update.exe itself is in — "
                "that would overwrite the program while it's being copied. "
                "Please choose a different folder (e.g. the existing child "
                "instance at its own location).")
            return

        start_btn.configure(state="disabled")
        log(f"\nCopying to {target} ...")
        try:
            copy_payload(src, target, log)
        except OSError as exc:
            log(f"[Error] {exc}")
            messagebox.showerror(
                root.title(),
                f"Copying failed:\n{exc}\n\n"
                "Is the target app still running? Close it and try again.")
            start_btn.configure(state="normal")
            return

        messagebox.showinfo(root.title(), "Done.")
        start_btn.configure(state="normal")

    start_btn.configure(command=_on_start)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
