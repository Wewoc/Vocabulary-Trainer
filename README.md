# Vocabulary-Trainer

**English** · [Deutsch](README.de.md)

A vocabulary trainer for school children that practises **your own lists**.
It ships with no vocabulary: parents bring the words from the school book, the
teacher or an Excel sheet and **import them as CSV**. The import shows a
preview of what will be added and never overwrites existing entries. Each
child gets their own app folder with their own list and progress.

Local and offline: no cloud, no account, no third-party services. The app
itself never connects to the internet. The only way it touches the network
is a click on a link to the project's GitHub pages — in the **About** window or
in the documentation shown there —, which opens your browser.

> **Status:** development version `0.0.18`. The last packaged release is
> `v0.1.0` (first beta, a standalone Windows program tested on a real
> Windows machine). Everything built since then — PIN gate, logging and crash
> reports, import preview, report export, search, article languages, the
> About window — is covered by automated tests but has **not yet been
> packaged and hand-tested on a real PC**. See
> [Known limitations](#known-limitations) before using it with a child.

---

## Bring your own vocabulary

The trainer has no built-in course and no dictionary data — the lists are
yours:

1. Write the words in Excel (two columns, one per language) or take them from
   the school book. Photos of a book page can be turned into such a list with
   an AI assistant; a ready-made prompt for that is in the user guide
   (section 4). That step happens outside the app.
2. Save the sheet as **CSV UTF-8** and use **Import from CSV** in the
   Management tab.
3. Check the **preview**, confirm, and the words are ready to practise.

Cells with several meanings (`dein/deine; euer/eure`, `I'm (= I am)`, hints in
brackets) are split into one entry per meaning; a tick box in the preview
switches that off.

---

## What it does

**Practice (Test tab)**

- Sessions of 1–999 words (default 20) — exactly the number you ask for, or
  all words if there are fewer. Direction A → B or B → A, optional filters
  (*newest words only*, *words with errors only*)
- The most urgent words come first: never tested, then newest, then error
  rate, error count and last-tested date; shown in random order
- Configurable answer checking: case, accents, optional ignoring of a leading
  article (German, English, Spanish or French)
- Several correct answers per word: giving a valid alternative triggers a
  follow-up question (*"Correct, but not the one we were looking for — is
  there a second one?"*)
- A summary after each test and a motivating overview (tests done, streaks,
  mastered words, week comparison)

**Parents' area (Management tab, PIN-protected)**

- CSV import of your own lists with preview, direct entry, live search, edit
  and delete
- Export of the word list and a readable report (CSV for Excel)
- Settings: language (German/English), colour theme, names of the two
  languages, answer checking, PIN, optional debug log

**Data and privacy**

- Vocabulary lives in plain CSV files; learning progress is stored encrypted
  next to the program. Each installation is portable: everything is in one
  folder (only crash reports go to `%LOCALAPPDATA%`)
- The PIN is only an access code for the Management tab — a forgotten PIN
  never costs learning data
- `logs/app.log` holds technical events only, never vocabulary in clear text

---

## Installation

Windows, no Python needed:

1. Download the release ZIP (`Vocabulary_trainer.zip`).
2. Extract it to a folder of your choice.
3. Start `Vocabulary_trainer.exe`.

To install a second copy (one per child) or to update an existing one, run
`update.exe` from the extracted folder and choose the target folder. It only
replaces the program files and the documentation — vocabulary, learning
progress, settings and PIN stay untouched.

---

## Documentation

- **In the app:** README and user guide (German and English) ship with the
  program — **About** → **Documentation**.
- **User guide:** [English](docs/User_Guide.md) · [Deutsch](docs/Bedienungsanleitung.md)
- **For developers** (run from source, tests, build, file formats):
  [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

## Questions and problems

Please open an issue: <https://github.com/Wewoc/Vocabulary-Trainer/issues>.
Include the version (**About** button) and, if the app showed an error window,
the report file named there.

---

## Known limitations

- **The PIN is a simple access code, not a lock.** It keeps a child out of the
  Management tab; it does not protect against someone who edits `config.json`
  or knows the program. The learning data is encrypted so it cannot be read
  or edited with a text editor — against a technically skilled person it
  protects nothing.
- **Single list in management.** Import, export, search and direct entry work
  on the first available vocabulary list.
- **One foreign language per instance for ignoring articles.** The article
  lists are short (`the`, `der/die/das`, `el/la/los/las`, `le/la/les`) — no
  `a/an`, `un/una`, `l'` or `ein/eine`.
- **Import drops hints in brackets** (`Herr (Anrede)` becomes `Herr`).
- **Errors before the window opens** are not covered by the crash handler.
- **Windows only** for the packaged release.

---

## License

GPL-3.0-or-later — see [LICENSE](LICENSE).

Copyright (C) 2026 Wewoc ([github.com/wewoc](https://github.com/wewoc))
