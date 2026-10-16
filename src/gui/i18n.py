#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# i18n.py
# Vokabeltrainer — minimal GUI string lookup (DE/EN switch, see
# requirements 8). Not the vocabulary being
# learned (that's vocab.py) — this is the app's own interface text.
# Leaf-Node: no project imports.

_STRINGS = {
    "check": {"de": "Prüfen", "en": "Check"},
    "correct": {"de": "Richtig!", "en": "Correct!"},
    "wrong": {
        "de": "Falsch. Richtig wäre: {answer}",
        "en": "Wrong. The correct answer was: {answer}",
    },
    "no_vocab": {
        "de": "Keine Vokabeln vorhanden.",
        "en": "No vocabulary available.",
    },
    "next": {"de": "Weiter", "en": "Next"},
    "alt_nachhaken": {
        "de": "Richtig, aber nicht die gesuchte Lösung — es gibt noch "
              "eine zweite. Wie lautet sie?",
        "en": "Correct, but not the one I'm looking for — there's a "
              "second answer. What is it?",
    },
    "session_done": {
        "de": "Test beendet. {correct}/{total} richtig.",
        "en": "Test complete. {correct}/{total} correct.",
    },
    "add_word": {"de": "Hinzufügen", "en": "Add"},
    "added": {"de": "Hinzugefügt: {a} – {b}", "en": "Added: {a} – {b}"},
    "added_duplicate": {
        "de": "Gibt es schon: {a} – {b}",
        "en": "Already exists: {a} – {b}",
    },
    "missing_fields": {
        "de": "Bitte beide Felder ausfüllen.",
        "en": "Please fill in both fields.",
    },
    "tab_test": {"de": "Test", "en": "Test"},
    "tab_verwaltung": {"de": "Verwaltung", "en": "Management"},
    "edit": {"de": "Bearbeiten", "en": "Edit"},
    "delete": {"de": "Löschen", "en": "Delete"},
    "import_csv": {"de": "Import aus CSV", "en": "Import from CSV"},
    "export": {"de": "Export", "en": "Export"},
    "change_pin": {"de": "PIN ändern", "en": "Change PIN"},
    "case_sensitive_option": {"de": "Case-sensitiv", "en": "Case-sensitive"},
    "strict_accents_option": {"de": "Akzente streng", "en": "Strict accents"},
    "ignore_articles_option": {"de": "Artikel ignorieren", "en": "Ignore articles"},
    "filter_newest": {"de": "Nur neueste Vokabeln", "en": "Newest words only"},
    "filter_errors": {
        "de": "Nur Vokabeln mit Fehlern",
        "en": "Words with errors only",
    },
    "count_label": {"de": "Anzahl Fragen", "en": "Question Count"},
    "theme_label": {"de": "Design", "en": "Theme"},
    "language_label": {"de": "Sprache (DE/EN)", "en": "Language (EN/DE)"},
    "language_restart_hint": {
        "de": "Wirkt erst nach Neustart der App.",
        "en": "Takes effect after restarting the app.",
    },
    "test_konfigurator_title": {"de": "Test-Konfigurator", "en": "Test Configurator"},
    "start_test": {"de": "Test starten", "en": "Start Test"},
    "banner_title": {
        "de": "🦄 Vokabel-Trainer 🐲",
        "en": "🦄 Vocab Trainer 🐲",
    },
    "banner_subtitle": {
        "de": "Lernen / wiederholen / behalten",
        "en": "Learn / review / remember",
    },
    "status_tests_done": {
        "de": "Absolvierte Tests: {count}",
        "en": "Tests completed: {count}",
    },
    "status_correct": {
        "de": "Richtig beantwortet: {correct}/{total}",
        "en": "Correct answers: {correct}/{total}",
    },
    "quiz_dialog_title": {"de": "Test läuft", "en": "Test in progress"},
    "cancel": {"de": "Abbrechen", "en": "Cancel"},
    "finish_early": {
        "de": "Beenden – Erfolge übernehmen",
        "en": "Finish – Keep Progress",
    },
    "evaluation_dialog_title": {"de": "Auswertung", "en": "Evaluation"},
    "evaluation_total": {
        "de": "Gesamt: {correct}/{total} richtig",
        "en": "Total: {correct}/{total} correct",
    },
    "status_last_test": {
        "de": "Letzter Test: {date}",
        "en": "Last test: {date}",
    },
    "status_never_tested": {"de": "noch nie", "en": "never"},
    "status_day_streak": {
        "de": "Tage-Serie: {current} (Rekord: {longest})",
        "en": "Day streak: {current} (record: {longest})",
    },
    "status_correct_streak": {
        "de": "Fehlerfreie Serie: {current} (Rekord: {longest})",
        "en": "Error-free streak: {current} (record: {longest})",
    },
    "status_mastered": {
        "de": "Gemeisterte Wörter: {count}",
        "en": "Mastered words: {count}",
    },
    "status_week_comparison": {
        "de": "Diese Woche: {this_week} (letzte Woche: {last_week})",
        "en": "This week: {this_week} (last week: {last_week})",
    },
    "save": {"de": "Speichern", "en": "Save"},
    "import_result": {
        "de": "{added} hinzugefügt, {skipped_duplicate} bereits vorhanden, "
              "{skipped_invalid} ungültig",
        "en": "{added} added, {skipped_duplicate} already existed, "
              "{skipped_invalid} invalid",
    },
    "import_read_error": {
        "de": "Datei konnte nicht gelesen werden.",
        "en": "Could not read the file.",
    },
    "import_preview_title": {"de": "Import-Vorschau", "en": "Import preview"},
    "import_preview_summary": {
        "de": "{new} neu, {skipped_duplicate} bereits vorhanden, {skipped_invalid} ungültig",
        "en": "{new} new, {skipped_duplicate} already existed, {skipped_invalid} invalid",
    },
    "import_preview_invalid": {
        "de": "Ungültige Zeilen (Sprache A oder B fehlt): {rows}",
        "en": "Invalid rows (language A or B missing): {rows}",
    },
    "import_preview_more": {"de": "… und {count} weitere", "en": "… and {count} more"},
    "import_preview_confirm": {"de": "Importieren", "en": "Import"},
    "import_preview_resolve_option": {
        "de": "Klammern und Trennzeichen (; /) auflösen",
        "en": "Resolve brackets and separators (; /)",
    },
    "import_preview_resolved": {
        "de": "Aus {rows} Zeilen wurden {pairs} Paare gebildet.",
        "en": "{rows} rows were turned into {pairs} pairs.",
    },
    "import_preview_check": {
        "de": "Bitte prüfen (mehrere Bedeutungen auf beiden Seiten, die Paarungen passen evtl. nicht): Zeilen {rows}",
        "en": "Please check (several meanings on both sides, the pairings may not fit): rows {rows}",
    },
    "import_preview_row_column": {"de": "Zeile", "en": "Row"},
    "import_cancelled": {"de": "Import abgebrochen.", "en": "Import cancelled."},
    "export_includes": {"de": "Export enthält:", "en": "Export contains:"},
    "export_wordlist_option": {"de": "Wortliste", "en": "Word list"},
    "export_report_option": {"de": "Report", "en": "Report"},
    "export_nothing_selected": {
        "de": "Bitte mindestens eine Option wählen.",
        "en": "Please select at least one option.",
    },
    "export_files_result": {
        "de": "{count} Datei(en) exportiert: {names}",
        "en": "{count} file(s) exported: {names}",
    },
    "export_write_error": {
        "de": "Datei konnte nicht geschrieben werden.",
        "en": "Could not write the file.",
    },
    "report_section_total": {"de": "Gesamt", "en": "Overall"},
    "report_section_words": {"de": "Pro Vokabel", "en": "Per word"},
    "report_tests_completed": {"de": "Tests abgeschlossen", "en": "Tests completed"},
    "report_tests_aborted": {"de": "Tests abgebrochen", "en": "Tests aborted"},
    "report_period": {"de": "Zeitraum der Tests", "en": "Test period"},
    "report_answered": {"de": "Beantwortete Fragen", "en": "Questions answered"},
    "report_words_tested": {"de": "Verschiedene Wörter getestet", "en": "Different words tested"},
    "report_wrong": {"de": "Fehler", "en": "Mistakes"},
    "report_accuracy": {"de": "Trefferquote", "en": "Accuracy"},
    "report_test_time": {
        "de": "Testzeit (abgeschlossene Tests)",
        "en": "Test time (completed tests)",
    },
    "report_col_word": {"de": "Wort", "en": "Word"},
    "report_col_language": {"de": "Sprache", "en": "Language"},
    "report_col_tests": {"de": "Tests", "en": "Tests"},
    "report_col_wrong": {"de": "Fehler", "en": "Mistakes"},
    "report_col_accuracy": {"de": "Trefferquote", "en": "Accuracy"},
    "report_col_last_wrong": {"de": "Letzter Fehler", "en": "Last mistake"},
    "report_removed": {"de": "(entfernt)", "en": "(removed)"},
    "confirm_delete_title": {"de": "Löschen bestätigen", "en": "Confirm deletion"},
    "confirm_delete_message": {
        "de": "Diesen Eintrag wirklich löschen?",
        "en": "Really delete this entry?",
    },
    "sprache_a_name_label": {"de": "Name Sprache A", "en": "Language A name"},
    "sprache_b_name_label": {"de": "Name Sprache B", "en": "Language B name"},
    "article_language_a_label": {"de": "Artikel-Sprache A", "en": "Article language A"},
    "article_language_b_label": {"de": "Artikel-Sprache B", "en": "Article language B"},
    "article_language_hint": {
        "de": "Für \u201eArtikel ignorieren\u201c. Wirkt ab dem nächsten Test.",
        "en": "For \u201cIgnore articles\u201d. Takes effect with the next test.",
    },
    "lang_de": {"de": "Deutsch", "en": "German"},
    "lang_en": {"de": "Englisch", "en": "English"},
    "lang_es": {"de": "Spanisch", "en": "Spanish"},
    "lang_fr": {"de": "Französisch", "en": "French"},
    "lang_none": {"de": "keine", "en": "none"},
    "sprache_name_restart_hint": {
        "de": "Wirkt erst nach Neustart der App.",
        "en": "Takes effect after restarting the app.",
    },
    "date_label": {"de": "Datum", "en": "Date"},
    "pin_prompt_title": {"de": "PIN erforderlich", "en": "PIN required"},
    "pin_prompt_hint": {
        "de": "Bitte die Eltern-PIN eingeben.",
        "en": "Please enter the parent PIN.",
    },
    "pin_wrong": {"de": "Falsche PIN.", "en": "Wrong PIN."},
    "pin_change_title": {"de": "PIN ändern", "en": "Change PIN"},
    "pin_old_label": {"de": "Alte PIN", "en": "Old PIN"},
    "pin_new_label": {"de": "Neue PIN", "en": "New PIN"},
    "pin_repeat_label": {"de": "Neue PIN wiederholen", "en": "Repeat new PIN"},
    "pin_mismatch": {
        "de": "Die beiden neuen PINs stimmen nicht überein.",
        "en": "The two new PINs do not match.",
    },
    "pin_too_short": {
        "de": "Die PIN muss mindestens 4 Zeichen lang sein.",
        "en": "The PIN must be at least 4 characters long.",
    },
    "pin_changed": {"de": "PIN geändert.", "en": "PIN changed."},
    "crash_title": {"de": "Unerwarteter Fehler", "en": "Unexpected error"},
    "crash_message": {
        "de": "Ein unerwarteter Fehler ist aufgetreten. Die App läuft weiter.\n"
              "Ein Protokoll wurde gespeichert unter:\n{path}",
        "en": "An unexpected error occurred. The app keeps running.\n"
              "A report was saved to:\n{path}",
    },
    "about_button": {"de": "Info", "en": "About"},
    "about_title": {"de": "Über {name}", "en": "About {name}"},
    "about_version": {"de": "Version {version}", "en": "Version {version}"},
    "about_license": {
        "de": "Freie Software unter der GPL-3.0-or-later. Es gibt KEINE GEWÄHRLEISTUNG.",
        "en": "Free software under the GPL-3.0-or-later. It comes with ABSOLUTELY NO WARRANTY.",
    },
    "about_source": {"de": "Quellcode:", "en": "Source code:"},
    "about_close": {"de": "Schließen", "en": "Close"},
    "about_docs": {"de": "Dokumentation", "en": "Documentation"},
    "doc_close": {"de": "Schließen", "en": "Close"},
    "doc_not_found": {"de": "Datei nicht gefunden: {name}", "en": "File not found: {name}"},
    "search_placeholder": {"de": "Suchen…", "en": "Search…"},
    "search_count": {"de": "{shown} von {total}", "en": "{shown} of {total}"},
    "entry_count": {"de": "{total} Einträge", "en": "{total} entries"},
    "debug_log_option": {
        "de": "Debug-Protokoll (bis zum Beenden)",
        "en": "Debug log (until the app is closed)",
    },
}


def text(key: str, language: str, **kwargs) -> str:
    """Looks up a GUI string for the given UI language. Falls back to
    'en' if the language or key is unknown, so a typo never crashes the
    GUI — just shows English instead of the requested language."""
    entry = _STRINGS.get(key, {})
    template = entry.get(language) or entry.get("en") or key
    return template.format(**kwargs) if kwargs else template
