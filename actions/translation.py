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

Requires:  pip install google-genai langdetect
Env var:   GEMINI_API_KEY
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_MODEL = "gemini-2.5-flash-lite-preview-06-17"

# ── Gemini setup ──────────────────────────────────────────────────────────────

try:
    from google import genai
    _GENAI_OK = True
except ImportError:
    _GENAI_OK = False
    logger.warning("translation.py: google-genai not installed")

try:
    from langdetect import detect, LangDetectException
    _LANGDETECT_OK = True
except ImportError:
    _LANGDETECT_OK = False

_client = None


def _get_client():
    global _client
    if _client is None and _GENAI_OK:
        key = os.environ.get("GEMINI_API_KEY", "")
        if key:
            try:
                _client = genai.Client(api_key=key)
            except Exception as exc:
                logger.warning(f"translation.py: Gemini init failed — {exc}")
    return _client


# ── Language name mapping for translation prompts ─────────────────────────────

_LANG_NAMES = {
    "FR":      "French",
    "ES":      "Spanish",
    "PT-PT":   "European Portuguese",
    "PT-BR":   "Brazilian Portuguese",
    "ZH-HANS": "Simplified Chinese",
    "ZH-HANT": "Traditional Chinese",
    "SR":      "Serbian",
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
    # 1. Language explicitly selected in the UI
    lang = (tracker.latest_message.get("metadata") or {}).get("lang")
    if lang:
        return lang

    # 2. Entity set by NLU component
    for entity in tracker.latest_message.get("entities", []):
        if entity.get("entity") == _LANG_ENTITY:
            return entity["value"]

    # 3. Slot from a previous turn
    slot = tracker.get_slot("language")
    if slot:
        return slot

    # 4. Langdetect fallback
    if _LANGDETECT_OK:
        text = (tracker.latest_message.get("text") or "").strip()
        if len(text) >= 4:
            try:
                raw = detect(text)
                return _LANGDETECT_MAP.get(raw)
            except Exception:
                pass

    return None


def translate_response(text: str, lang: Optional[str]) -> str:
    """
    Translate an English response string to the target language.
    Returns the original text unchanged on any error or when lang is None/English.
    Gemini preserves Markdown (*bold*, _italic_, bullet lists).
    """
    if not lang or lang.upper().startswith("EN"):
        return text

    lang_name = _LANG_NAMES.get(lang, lang)
    c = _get_client()
    if not c:
        logger.warning(
            f"translate_response: Gemini not available "
            f"(GEMINI_API_KEY set? _GENAI_OK={_GENAI_OK})"
        )
        return text

    try:
        prompt = (
            f"Translate the following text to {lang_name}. "
            "Preserve all Markdown formatting exactly (bold **, bullets •, hyphens -, etc.). "
            "Return only the translated text with no explanation or preamble:\n\n"
            + text
        )
        response = c.models.generate_content(model=_MODEL, contents=prompt)
        return response.text.strip()
    except Exception as exc:
        logger.warning(f"translate_response to {lang} failed: {exc}")
        return text
