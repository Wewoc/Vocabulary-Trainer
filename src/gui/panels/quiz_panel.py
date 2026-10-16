#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Wewoc (github.com/wewoc)
# quiz_panel.py
# Vokabeltrainer — quiz panel: runs a contingented quiz session (see
# requirements 4) over the current vocab list, with
# ambiguity-cluster-aware evaluation and a Nachhaken follow-up on an
# "alt" outcome (requirements 3.3). Self-contained widget, knows nothing
# about its own placement on a page (see the project invariants,
# GUI composition principle) — a window places it, it never places
# itself. All fetching/evaluating/scoring happens through evaluation.py,
# priority.py, tracking.py and vocab.py — this file only wires widgets.
#
# Direction, quiz-set size, and the "newest"/"errors only" filters are
# configurable since v0.0.9.2 via the Test-Konfigurator (see
# gui/panels/test_konfigurator_panel.py, gui/dialogs/quiz_dialog.py) -
# vocab-language still falls back to vocab.pick_default_language() if
# none is chosen (e.g. no vocab list exists yet). "Mixed" direction is
# intentionally not supported - not in requirements 4.1's spec (only
# A->B/B->A), and mixing directions within one session would require
# tracking against two different UUID columns in the same pass.
#
# Tracking always keys off the *prompt* side's UUID: UUID_A for A->B,
# UUID_B for B->A (see the project invariants) - symmetric
# treatment, not a special case for A->B.
#
# Session recording (v0.0.8, see data model, section 2):
# finalize_session()/cancel_session() are called from outside (by
# QuizDialog) rather than internally, because a session only counts as
# "completed" once the evaluation popup that follows it has been closed
# - see gui/dialogs/quiz_dialog.py. There's no way to end a session
# early and keep it: Abbrechen (cancel_session()) never counts,
# finishing the full queue is the only path to a counted session
# (dropped the earlier "Finish - Keep Progress" mid-session button,
# maintainer decision - see git history).
#
# session_results() (v0.0.9.3) exposes the per-task outcomes collected
# during the session, for EvaluationDialog's real data - a Nachhaken
# retry never adds its own entry, only the first attempt is recorded
# (same as tracking, see _check_answer()).

from datetime import datetime

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

import config
import evaluation
import priority
import tracking
import vocab
from gui import i18n

_QUIZ_SET_SIZE = 20  # default when no count is passed in


class QuizPanel(QWidget):
    # Emitted when a session reaches its end (see _show_session_done()).
    # A containing dialog/page can react (e.g. open an evaluation popup)
    # without knowing anything about QuizPanel's internal session state -
    # same pattern as DirectEntryPanel's word_added signal.
    session_finished = pyqtSignal()

    def __init__(
        self,
        vocab_language: str | None = None,
        direction: str = "A->B",
        count: int | None = None,
        filter_newest: int | None = None,
        filter_errors_only: bool = False,
    ):
        super().__init__()
        self._vocab_language = vocab_language or vocab.pick_default_language()
        self._prompt_field = "Sprache_A" if direction == "A->B" else "Sprache_B"
        self._expected_field = "Sprache_B" if direction == "A->B" else "Sprache_A"
        self._prompt_uuid_field = "UUID_A" if direction == "A->B" else "UUID_B"
        self._prompt_column = "A" if direction == "A->B" else "B"
        self._count = count if count is not None else _QUIZ_SET_SIZE
        self._filter_newest = filter_newest
        self._filter_errors_only = filter_errors_only
        cfg = config.load_config()
        self._ui_language = cfg["language"]
        self._bewertung = cfg["bewertung"]
        # Article list for "Artikel ignorieren": the language being typed,
        # i.e. the answer side (B for A->B, A for B->A) - v0.0.15.
        self._answer_language = cfg["sprache_b_code"] if direction == "A->B" else cfg["sprache_a_code"]
        self._tracking_data = tracking.load_tracking()

        self._queue: list[dict] = []
        self._queue_index = 0
        self._current_entry = None
        self._awaiting_alt_retry = False
        self._session_correct = 0
        self._session_started_at: str | None = None
        self._session_results: list[dict] = []

        self._prompt_label = QLabel()
        self._answer_input = QLineEdit()
        self._check_button = QPushButton(i18n.text("check", self._ui_language))
        self._feedback_label = QLabel()

        input_row = QHBoxLayout()
        input_row.addWidget(self._answer_input)
        input_row.addWidget(self._check_button)

        layout = QVBoxLayout()
        layout.addWidget(self._prompt_label)
        layout.addLayout(input_row)
        layout.addWidget(self._feedback_label)
        self.setLayout(layout)

        self._check_button.clicked.connect(self._on_button_clicked)
        self._answer_input.returnPressed.connect(self._on_button_clicked)

        self._start_session()

    def _start_session(self) -> None:
        # vocab_language is always concrete now (vocab.pick_default_language()
        # never returns None) - an empty entries list already covers "no
        # vocab exists at all" the same as "list exists but is empty",
        # so no separate None-check is needed here.
        entries = vocab.load_entries(self._vocab_language)
        if self._filter_newest is not None:
            entries = sorted(entries, key=lambda e: e.get("Datum", ""), reverse=True)[
                : self._filter_newest
            ]

        vocab_stats = self._tracking_data["vocab_stats"]
        if self._filter_errors_only:
            entries = [
                e
                for e in entries
                if vocab_stats.get(e[self._prompt_uuid_field], {}).get("wrong_count", 0) > 0
            ]

        if not entries:
            self._show_no_vocab()
            return

        self._queue = priority.build_quiz_set(
            entries, vocab_stats, count=self._count, uuid_field=self._prompt_uuid_field
        )
        self._queue_index = 0
        self._session_correct = 0
        self._session_results = []
        self._session_started_at = datetime.now().isoformat(timespec="seconds")
        self._load_current_entry()

    def _load_current_entry(self) -> None:
        if self._queue_index >= len(self._queue):
            self._show_session_done()
            return
        self._current_entry = self._queue[self._queue_index]
        self._awaiting_alt_retry = False
        self._prompt_label.setText(self._current_entry[self._prompt_field])
        self._answer_input.clear()
        self._answer_input.setEnabled(True)
        self._check_button.setEnabled(True)
        self._feedback_label.setText("")

    def _show_no_vocab(self) -> None:
        self._current_entry = None
        self._prompt_label.setText(i18n.text("no_vocab", self._ui_language))
        self._answer_input.setEnabled(False)
        self._check_button.setEnabled(False)

    def _show_session_done(self) -> None:
        self._current_entry = None
        self._prompt_label.setText(
            i18n.text(
                "session_done",
                self._ui_language,
                # queue_index always equals len(self._queue) here - this
                # is only reached by running the queue to the end, see
                # module docstring.
                correct=self._session_correct,
                total=self._queue_index,
            )
        )
        self._answer_input.setEnabled(False)
        self._check_button.setEnabled(False)
        self.session_finished.emit()

    def session_results(self) -> list[dict]:
        """Per-task results recorded so far this session - one entry per
        answered question (`{prompt, expected, given, outcome}`), in
        answer order. A Nachhaken retry doesn't add a second entry - the
        outcome recorded is always the first attempt's (see
        _check_answer()). Read by QuizDialog to pass real data into
        EvaluationDialog (v0.0.9.3)."""
        return self._session_results

    def cancel_session(self) -> None:
        """Called from outside (QuizDialog's Abbrechen button, or its
        window close) - records the session as not completed. A no-op
        if no real session was ever attempted (no vocab existed, see
        _show_no_vocab())."""
        if self._session_started_at is None:
            return
        self._record_session(completed=False)

    def finalize_session(self) -> None:
        """Called from outside (QuizDialog), only after the evaluation
        popup following a finished session has been closed - a session
        counts as completed at that point, not when the last question
        was answered (see module docstring)."""
        if self._session_started_at is None:
            return
        self._record_session(completed=True)

    def _record_session(self, completed: bool) -> None:
        ended_at = datetime.now().isoformat(timespec="seconds")
        tracking.record_session(self._tracking_data, self._session_started_at, ended_at, completed)
        tracking.save_tracking(self._tracking_data)
        self._session_started_at = None

    def _on_button_clicked(self) -> None:
        """The same button/Enter serves two roles depending on state:
        checking an answer, or advancing once feedback is shown — a
        separate "Weiter" step is required so feedback text isn't
        instantly overwritten by the next entry in the same call."""
        if self._current_entry is None:
            return
        if self._check_button.text() == i18n.text("next", self._ui_language):
            self._advance()
        else:
            self._check_answer()

    def _check_answer(self) -> None:
        given = self._answer_input.text()
        expected = self._current_entry[self._expected_field]

        if self._awaiting_alt_retry:
            # Second attempt after a Nachhaken prompt - the "alt" outcome
            # was already recorded on the first attempt; this retry is
            # purely the pedagogical follow-up, it doesn't change tracking.
            if evaluation.is_correct(given, expected, self._bewertung, self._answer_language):
                self._feedback_label.setText(i18n.text("correct", self._ui_language))
            else:
                self._feedback_label.setText(
                    i18n.text("wrong", self._ui_language, answer=expected)
                )
            self._enter_feedback_mode()
            return

        entries = vocab.load_entries(self._vocab_language)
        cluster = vocab.find_entries_by_uuid(
            entries, self._prompt_column, self._current_entry[self._prompt_uuid_field]
        )
        alternates = [e[self._expected_field] for e in cluster]
        outcome = evaluation.evaluate_with_cluster(
            given, expected, alternates, self._bewertung, self._answer_language
        )
        self._record_outcome(outcome)
        self._session_results.append(
            {
                "prompt": self._current_entry[self._prompt_field],
                "expected": expected,
                "given": given,
                "outcome": outcome,
            }
        )

        if outcome == "correct":
            self._session_correct += 1
            self._feedback_label.setText(i18n.text("correct", self._ui_language))
            self._enter_feedback_mode()
        elif outcome == "wrong":
            self._feedback_label.setText(
                i18n.text("wrong", self._ui_language, answer=expected)
            )
            self._enter_feedback_mode()
        else:  # "alt" - Nachhaken: stay on the same entry, one retry
            self._feedback_label.setText(i18n.text("alt_nachhaken", self._ui_language))
            self._answer_input.clear()
            self._awaiting_alt_retry = True

    def _record_outcome(self, outcome: str) -> None:
        prompt_uuid = self._current_entry[self._prompt_uuid_field]
        timestamp = datetime.now().isoformat(timespec="seconds")
        tracking.record_outcome(self._tracking_data, prompt_uuid, outcome, timestamp)
        tracking.save_tracking(self._tracking_data)

    def _enter_feedback_mode(self) -> None:
        self._answer_input.setEnabled(False)
        self._check_button.setText(i18n.text("next", self._ui_language))

    def _advance(self) -> None:
        self._check_button.setText(i18n.text("check", self._ui_language))
        self._queue_index += 1
        self._load_current_entry()
