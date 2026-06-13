#!/usr/bin/env python3
"""Unit checks for action-server translation language selection."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from actions.translation import get_lang
from actions.actions import ActionHandleOutOfScope
from rasa_sdk.executor import CollectingDispatcher


class _Tracker:
    def __init__(self, text, metadata=None, slots=None, entities=None):
        self.latest_message = {
            "text": text,
            "intent": {"name": "out_of_scope"},
            "metadata": metadata or {},
            "entities": entities or [],
        }
        self._slots = slots or {}

    def get_slot(self, name):
        return self._slots.get(name)


def test_explicit_english_metadata_blocks_langdetect_and_old_slot():
    tracker = _Tracker(
        "Alex Tester",
        metadata={"lang": "EN"},
        slots={"language": "SR"},
    )

    assert get_lang(tracker) is None


def test_metadata_accepts_non_default_detected_languages():
    tracker = _Tracker(
        "What is the budget for Sofia Airport?",
        metadata={"lang": "IT"},
    )

    assert get_lang(tracker) == "IT"


def test_language_capability_question_gets_specific_answer():
    tracker = _Tracker("Do you speak French?", metadata={"lang": "EN"})
    dispatcher = CollectingDispatcher()

    ActionHandleOutOfScope().run(dispatcher, tracker, {})

    assert dispatcher.messages
    assert "another language" in dispatcher.messages[-1]["text"]
    assert "visible language buttons" in dispatcher.messages[-1]["text"]


if __name__ == "__main__":
    test_explicit_english_metadata_blocks_langdetect_and_old_slot()
    test_metadata_accepts_non_default_detected_languages()
    test_language_capability_question_gets_specific_answer()
    print("Translation unit checks passed.")
