#!/usr/bin/env python3
"""Unit checks for action-server translation language selection."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from actions.translation import get_lang
from actions.actions import ActionHandleOutOfScope
from components.translation_component import TranslationComponent
from rasa.shared.nlu.training_data.message import Message
from rasa_sdk.executor import CollectingDispatcher
import translation_server


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


def test_confident_input_language_beats_response_language_and_old_slot():
    tracker = _Tracker(
        "innovations",
        metadata={
            "response_lang": "SR",
            "input_lang": "EN",
            "input_lang_confident": True,
        },
        slots={"language": "SR"},
    )

    assert get_lang(tracker) is None


def test_clear_long_english_direct_api_turn_clears_old_language_slot():
    tracker = _Tracker(
        "Can you tell me what construction supervision services your architecture studio provides?",
        slots={"language": "SR"},
    )

    assert get_lang(tracker) is None


def test_ambiguous_name_preserves_current_language():
    tracker = _Tracker("Priya Test", slots={"language": "SR"})

    assert get_lang(tracker) == "SR"


def test_short_english_project_scope_is_not_misdetected():
    assert get_lang(_Tracker("project scope")) is None
    assert get_lang(_Tracker("belgarde airport")) is None


def test_metadata_accepts_non_default_detected_languages():
    tracker = _Tracker(
        "What is the budget for Sofia Airport?",
        metadata={"lang": "IT"},
    )

    assert get_lang(tracker) == "IT"


def test_proxy_identifies_obvious_english_despite_serbian_hint():
    lang, confident = translation_server._identify_source_lang_with_gemini(
        "innovations",
        "SR",
    )

    assert (lang, confident) == ("EN", True)


def test_proxy_identifies_short_misspelled_airport_query_as_english():
    lang, confident = translation_server._identify_source_lang_with_gemini(
        "belgarde airport",
        "SR",
    )

    assert (lang, confident) == ("EN", True)


def test_proxy_preserves_current_language_for_ambiguous_name():
    lang, confident = translation_server._identify_source_lang_with_gemini(
        "Priya Test",
        "SR",
    )

    assert lang == ""
    assert confident is False
    assert translation_server._looks_like_low_information_turn("Priya Test")


def test_translation_component_does_not_translate_proxy_english_twice():
    component = TranslationComponent({"gemini_api_key": "unused"})
    message = Message({
        "text": "Tell me about 1PAX innovations",
        "metadata": {
            "response_lang": "SR",
            "input_lang": "SR",
            "input_lang_confident": True,
            "input_translated": True,
        },
    })

    def _must_not_translate(*_args, **_kwargs):
        raise AssertionError("already-translated text was translated a second time")

    component._translate_to_english = _must_not_translate
    component._handle(message)

    assert message.get("text") == "Tell me about 1PAX innovations"
    assert any(
        entity.get("entity") == "__lang__" and entity.get("value") == "SR"
        for entity in message.get("entities", [])
    )


def test_translation_component_respects_confident_english_input():
    component = TranslationComponent({"gemini_api_key": "unused"})
    message = Message({
        "text": "innovations",
        "metadata": {
            "response_lang": "SR",
            "input_lang": "EN",
            "input_lang_confident": True,
            "input_translated": False,
        },
    })

    component._handle(message)

    assert message.get("text") == "innovations"
    assert not any(
        entity.get("entity") == "__lang__"
        for entity in message.get("entities", [])
    )


def test_translation_component_protects_short_english_project_phrases():
    component = TranslationComponent({"gemini_api_key": ""})
    for text in ("nice airport project", "project scope", "belgarde airport"):
        message = Message({"text": text})
        component._handle(message)
        assert not any(
            entity.get("entity") == "__lang__"
            for entity in message.get("entities", [])
        ), text


def test_language_capability_question_gets_specific_answer():
    tracker = _Tracker("Do you speak French?", metadata={"lang": "EN"})
    dispatcher = CollectingDispatcher()

    ActionHandleOutOfScope().run(dispatcher, tracker, {})

    assert dispatcher.messages
    assert "another language" in dispatcher.messages[-1]["text"]
    assert "visible language buttons" in dispatcher.messages[-1]["text"]


if __name__ == "__main__":
    test_explicit_english_metadata_blocks_langdetect_and_old_slot()
    test_confident_input_language_beats_response_language_and_old_slot()
    test_clear_long_english_direct_api_turn_clears_old_language_slot()
    test_ambiguous_name_preserves_current_language()
    test_short_english_project_scope_is_not_misdetected()
    test_metadata_accepts_non_default_detected_languages()
    test_proxy_identifies_obvious_english_despite_serbian_hint()
    test_proxy_identifies_short_misspelled_airport_query_as_english()
    test_proxy_preserves_current_language_for_ambiguous_name()
    test_translation_component_does_not_translate_proxy_english_twice()
    test_translation_component_respects_confident_english_input()
    test_translation_component_protects_short_english_project_phrases()
    test_language_capability_question_gets_specific_answer()
    print("Translation unit checks passed.")
