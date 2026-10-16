# Development

Notes for people who want to run, test or build the Vocabulary-Trainer from
source. For using the app, see the [user guide](User_Guide.md)
([Deutsch](Bedienungsanleitung.md)).

Python 3.13 and PyQt6, plus `cryptography` (see `requirements.txt`). Windows is
the target for the packaged release; the app itself is cross-platform.

## Run from source

```bash
pip install -r requirements.txt
python src/start.py
```

On Windows you can also double-click `src/bat/start.bat`, which keeps the
console open if the app exits with an error.

The program keeps all its data next to itself (the exe folder when frozen, the
repository root when run from source): `config.json`, `daten/`, `metadaten/`
and `logs/` are created on first start and are not checked in.

## Tests

```bash
python -m pytest -q
```

The GUI tests run with Qt's `offscreen` platform, so no window opens. Tests
that would open a browser or a file manager replace `QDesktopServices.openUrl`.
Tests never touch a real instance: they point `paths.base_dir` at a temporary
folder.

## Build the release

```bash
python compiler/build.py              # app + update.exe + release ZIP
python compiler/build.py --no-zip     # skip the ZIP
python compiler/build.py --no-updater # skip update.exe
```

The build uses a project-local `.venv-build/` and writes to `dist/`; the
release ZIP is `dist/Vocabulary_trainer.zip`. `compiler/build_manifest.py` is
the single source of truth for names and the files that make up a release.

The build also copies README, both guides and the screenshots to `info/` (the
list is `INFO_FILES`/`INFO_IMAGES` in the manifest) and `LICENSE` next to the
exe. The About window shows them in a viewer (`src/doc_files.py`,
`gui/dialogs/doc_viewer_dialog.py`). Keep `INFO_FILES` and
`doc_files.DOCUMENTS` in step and the links in those four files valid; the
tests (`test_build_manifest.py`, `test_gui_doc_viewer.py`) check both.

A build replaces the contents of `dist/`, including any instance data created
there by running the built app — use a copy of the folder for tests and close
the exe first.

## Instance folder

One folder is one app instance:

```
<instance folder>/
  Vocabulary_trainer.exe
  update.exe                  (install/update helper)
  _internal/                  (PyInstaller runtime — do not edit)
  info/                       (README and guides, de/en, with bilder/ screenshots)
  LICENSE
  config.json                 (created on first start, holds the PIN hash)
  daten/
    vokabeln/                 (one CSV per language list)
  metadaten/
    tracking.enc              (encrypted learning data)
  logs/
    app.log                   (technical log, no vocabulary)
```

`update.exe` only replaces the program files and the documentation (`info/`,
`LICENSE`), never `daten/`, `metadaten/`, `config.json` or `logs/`. Crash reports are written outside the instance, to
`%LOCALAPPDATA%\Vokabeltrainer\crash`.

## Vocabulary files

Hand-made CSV, UTF-8, comma or semicolon (detected automatically):

```csv
Deutsch,Englisch,Datum
Haus,house,2026-09-01
groß,big,2026-09-02
groß,large,2026-09-02
```

- Headers are the configured language names or `Sprache_A` / `Sprache_B`.
- `Datum` is optional and ignored for hand-made files: the import date is used.
- The same text in the same column reuses the same term UUID. That links the
  rows into an ambiguity cluster (`groß` → `big`/`large`): both answers count,
  the second one triggers a follow-up question.
- Cells with several meanings are resolved on import: `;` and `/` separate (not
  inside brackets), `(= long form)` is a second form, a bracket after a space
  is a hint and dropped, `Sei(d)` gives both spellings, the comma never splits.
  Only rows without trusted UUIDs are resolved; the preview has a tick box to
  switch it off and flags rows with several meanings on both sides.

Export file (for re-import or another instance):

```csv
quelle_instance_id,UUID_A,Sprache_A,UUID_B,Sprache_B,Datum
7c6bd2d5-...,x1a2b3...,large,g1c2d3...,groß,2026-09-01
```

On import, UUIDs are trusted only if `quelle_instance_id` equals the importing
instance's own `instance_id` (and then `Datum` is kept). Anything else is
matched by text and gets today's date. Existing entries are never overwritten.

## Repository layout

```
src/            application code (flat modules + gui/ for widgets)
tests/          automated tests (pytest, offscreen Qt)
compiler/       PyInstaller build and update helper
tools/          developer helpers (not part of the product)
docs/           user guides and this file
```

Developer helpers:

- `tools/seed_test_vocab.py` — fills a test vocabulary list (additive, safe to re-run)
- `tools/lektion1_vocab.csv` — 50 sample entries for manual import/export tests

## Conventions

- Code comments, docstrings and commit messages are English. Section numbers
  in comments ("requirements 3.3", "data model, section 2") refer to the
  maintainer's private requirements and data-model documents.
- Field names of the data contract (`Sprache_A`, `UUID_A`, `bewertung`,
  `case_sensitiv`, …) stay as specified and are not translated.
- The version lives in `src/version.py` (`APP_VERSION`); the About window and
  crash reports read it from there.
- GUI text for parents and children is German/English and lives in
  `src/gui/i18n.py`.
