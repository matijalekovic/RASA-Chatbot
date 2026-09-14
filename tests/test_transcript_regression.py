#!/usr/bin/env python3
"""Strict live replay of the conversation that exposed the production failures.

Run only after the action server, translation proxy, and candidate Rasa model are
running. This script exercises the same translation contract as the browser UI.
"""

import os
import re
import time
import uuid

import requests


RASA_URL = os.environ.get("RASA_URL", "http://localhost:5005").rstrip("/")
TRANSLATE_URL = os.environ.get(
    "TRANSLATE_URL",
    "http://localhost:5056/translate",
)
TRANSLATE_HEALTH_URL = os.environ.get(
    "TRANSLATE_HEALTH_URL",
    TRANSLATE_URL.rsplit("/", 1)[0] + "/health",
)
TIMEOUT = 30


def _post(url, payload):
    response = requests.post(url, json=payload, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def _response_text(replies):
    return "\n".join(reply.get("text", "") for reply in replies if reply.get("text"))


def _assert_contains(text, required, label):
    folded = text.casefold()
    missing = [item for item in required if item.casefold() not in folded]
    assert not missing, f"{label}: missing {missing!r}\n{text}"


def _assert_not_contains(text, forbidden, label):
    folded = text.casefold()
    found = [item for item in forbidden if item.casefold() in folded]
    assert not found, f"{label}: found forbidden {found!r}\n{text}"


def _send_rasa(sender, english_text, response_lang, input_state):
    payload = {
        "sender": sender,
        "message": english_text,
        "metadata": {
            "lang": response_lang,
            "response_lang": response_lang,
            **input_state,
        },
    }
    replies = _post(f"{RASA_URL}/webhooks/rest/webhook", payload)
    assert replies, f"Rasa returned no response for {english_text!r}"
    return _response_text(replies), replies


def _send_synthetic(sender, english_text, response_lang):
    return _send_rasa(
        sender,
        english_text,
        response_lang,
        {
            "input_lang": "EN",
            "input_lang_confident": False,
            "input_translated": True,
            "synthetic_payload": True,
        },
    )


def _send_typed(sender, user_text, current_lang):
    translated = _post(
        TRANSLATE_URL,
        {
            "text": user_text,
            "response_lang": current_lang,
            "identify_language": True,
        },
    )
    assert translated.get("translation_enabled") is True, (
        "Translation proxy is not enabled; live multilingual regression is invalid"
    )
    assert not translated.get("translation_error"), translated

    identified = bool(
        translated.get("input_lang_confident", translated.get("language_identified"))
    )
    input_lang = str(
        translated.get("input_lang")
        or (translated.get("identified_lang") if identified else "UNKNOWN")
        or "UNKNOWN"
    ).upper()
    preserve_current = bool(translated.get("preserve_current"))
    if identified and not preserve_current and input_lang != "UNKNOWN":
        current_lang = input_lang

    english_text = translated.get("english_text") or translated.get("text") or user_text
    text, replies = _send_rasa(
        sender,
        english_text,
        current_lang,
        {
            "input_lang": input_lang if identified else "UNKNOWN",
            "input_lang_confident": identified,
            "input_translated": bool(translated.get("input_translated")),
            "preserve_current_language": preserve_current,
            "synthetic_payload": False,
        },
    )
    return current_lang, text, replies, translated


def run_transcript_regression():
    health = requests.get(TRANSLATE_HEALTH_URL, timeout=TIMEOUT).json()
    assert health.get("translation_enabled") is True, health

    sender = f"transcript_regression_{uuid.uuid4().hex[:10]}"
    current_lang = "SR"  # Simulates the Serbian geolocation default.

    greeting, _ = _send_synthetic(sender, "hello", current_lang)
    _assert_contains(greeting, ["1PAX"], "Serbian geo greeting")
    _assert_not_contains(greeting, ["Hello!", "What would you like"], "Serbian geo greeting")

    current_lang, answer, _, translation = _send_typed(sender, "hi", current_lang)
    assert current_lang == "EN", translation
    assert translation.get("input_lang") == "EN", translation
    _assert_contains(answer, ["1PAX"], "English language switch")
    _assert_not_contains(answer, ["Šta biste", "Pitajte", "Zdravo"], "English language switch")

    current_lang, answer, _, _ = _send_typed(
        sender,
        "reci mi nesto o 1pax",
        current_lang,
    )
    assert current_lang == "SR"
    _assert_contains(answer, ["1PAX", "Mabel Mirand", "2016"], "Serbian overview")
    assert not re.search(r"[\u0400-\u04FF]", answer), "Serbian output must use Latin script"

    current_lang, answer, _, _ = _send_typed(
        sender,
        "koji su vasi projekti",
        current_lang,
    )
    assert current_lang == "SR"
    _assert_contains(answer, ["57", "Sofia"], "Serbian project list")

    current_lang, answer, _, translation = _send_typed(
        sender,
        "Tell me about Intermodal Metro Station Pachacámac",
        current_lang,
    )
    assert current_lang == "EN", translation
    _assert_contains(
        answer,
        ["Pachacámac", "ATU", "2018", "2019", "3,900", "5,000"],
        "English project switch",
    )
    _assert_not_contains(answer, ["Drago mi je", "putnika na sat"], "English project switch")

    current_lang, answer, _, _ = _send_typed(sender, "inovacije", current_lang)
    assert current_lang == "SR"
    _assert_contains(answer, ["Ecoport", "PAX", "SKYLO"], "Innovation routing")
    _assert_not_contains(answer, ["Carla Miranda", "ESADE"], "Innovation routing")

    current_lang, answer, _, _ = _send_typed(sender, "ko je direktor", current_lang)
    assert current_lang == "SR"
    _assert_contains(answer, ["Mabel Mirand"], "Director routing")
    _assert_not_contains(
        answer,
        ["Pachacámac", "Who would you like", "izvan onoga"],
        "Director routing",
    )

    current_lang, answer, _, _ = _send_typed(
        sender,
        "ko je osnovao 1pax",
        current_lang,
    )
    assert current_lang == "SR"
    _assert_contains(answer, ["Mabel Mirand", "2016"], "Founder routing")
    _assert_not_contains(answer, ["Carla Miranda", "ESADE"], "Founder routing")
    assert not re.search(r"[\u0400-\u04FF]", answer), "Serbian output must use Latin script"

    return 8


if __name__ == "__main__":
    started = time.monotonic()
    turns = run_transcript_regression()
    print(f"Transcript regression passed: {turns} turns in {time.monotonic() - started:.1f}s.")
