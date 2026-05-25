"""
Translation utilities for the 1PAX action server.

get_lang(tracker)              → language code ("FR", "ZH-HANS", "SR", …)
                                 or None when the user is writing English.

translate_response(text, lang) → English text translated to lang, or original
                                 text if lang is None / unavailable.

Usage in every action:
    from .translation import get_lang, translate_response
    from rasa_sdk.events import SlotSet

    def run(self, dispatcher, tracker, domain):
        lang = get_lang(tracker)
        ...
        dispatcher.utter_message(text=translate_response("Hello!", lang))
        return [SlotSet("language", lang), ...]   # persist across short follow-ups

Requires:  pip install langdetect
Env var:   GEMINI_API_KEY
"""

import json
import logging
import os
import socket
import urllib.error
import urllib.request
from typing import Optional

logger = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-3.5-flash"
_GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{_GEMINI_MODEL}:generateContent"
)
_MAX_SYNC_TRANSLATION_CHARS = int(os.environ.get("MAX_SYNC_TRANSLATION_CHARS", "2400"))

try:
    from langdetect import detect, LangDetectException
    _LANGDETECT_OK = True
except ImportError:
    _LANGDETECT_OK = False


# ── Language name mapping for translation prompts ─────────────────────────────

_LANG_NAMES = {
    "FR":      "French",
    "ES":      "Spanish",
    "PT-PT":   "European Portuguese",
    "PT-BR":   "Brazilian Portuguese",
    "ZH-HANS": "Simplified Chinese",
    "ZH-HANT": "Traditional Chinese",
    "SR":      "Serbian (Latin script, never Cyrillic)",
    "DE":      "German",
    "IT":      "Italian",
    "NL":      "Dutch",
    "PL":      "Polish",
    "JA":      "Japanese",
    "KO":      "Korean",
    "AR":      "Arabic",
}

# Entity name set by TranslationComponent in the NLU pipeline
_LANG_ENTITY = "__lang__"

# Fallback: langdetect code → our language code
_LANGDETECT_MAP: dict = {
    "es":    "ES",
    "fr":    "FR",
    "zh-cn": "ZH-HANS",
    "zh-tw": "ZH-HANT",
    "zh":    "ZH-HANS",
    "pt":    "PT-PT",
    "sr":    "SR",
    "hr":    "SR",
    "bs":    "SR",
}


def get_lang(tracker) -> Optional[str]:
    """
    Return the language code for the current user turn, or None for English.

    Priority:
      1. UI metadata      — lang code sent by the frontend with every message
      2. __lang__ entity  — set by TranslationComponent during NLU
      3. language slot    — persisted from a previous turn
      4. langdetect       — last-resort fallback
    """
    lang = (tracker.latest_message.get("metadata") or {}).get("lang")
    if lang:
        return lang

    for entity in tracker.latest_message.get("entities", []):
        if entity.get("entity") == _LANG_ENTITY:
            return entity["value"]

    slot = tracker.get_slot("language")
    if slot:
        return slot

    if _LANGDETECT_OK:
        text = (tracker.latest_message.get("text") or "").strip()
        if len(text) >= 4:
            try:
                raw = detect(text)
                return _LANGDETECT_MAP.get(raw)
            except Exception:
                pass

    return None


def _gemini_call(prompt: str, system_instruction: str, timeout: float = 6.0) -> Optional[str]:
    """POST to Gemini REST; return the text or None on any error."""
    api_key = (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
    )
    if not api_key:
        return None

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {"temperature": 0.1},
    }
    req = urllib.request.Request(
        f"{_GEMINI_URL}?key={api_key}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read())
        return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (
        TimeoutError,
        socket.timeout,
        urllib.error.URLError,
        urllib.error.HTTPError,
        OSError,
        KeyError,
        IndexError,
        ValueError,
    ) as exc:
        logger.warning(f"Gemini REST call failed: {exc}")
        return None
    except Exception as exc:
        logger.warning(f"Unexpected Gemini REST failure: {exc}")
        return None


def translate_response(text: str, lang: Optional[str]) -> str:
    """
    Translate an English response string to the target language.
    Returns the original text unchanged on any error or when lang is None/English.
    Gemini preserves Markdown (*bold*, _italic_, bullet lists).
    """
    if not lang or lang.upper().startswith("EN"):
        return text

    if len(text) > _MAX_SYNC_TRANSLATION_CHARS:
        logger.warning(
            "Skipping synchronous response translation for %s chars; "
            "returning source text to avoid action timeout.",
            len(text),
        )
        return text

    lang_name = _LANG_NAMES.get(lang, lang)
    translated = _gemini_call(
        prompt=f"Translate to {lang_name}: {text}",
        system_instruction=(
            "You are a translator. Output ONLY the translated text. "
            "Preserve all Markdown formatting exactly (bold **, bullets •, hyphens -, etc.). "
            "No explanations, no quotes, no notes."
        ),
    )
    return translated if translated is not None else text
