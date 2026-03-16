"""
Translation utilities for the 1PAX action server.

get_lang(tracker)              → DeepL target code ("FR", "ZH-HANS", "SR", …)
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

Requires:  pip install deepl langdetect
Env var:   DEEPL_API_KEY  (free-tier key ends with :fx)
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import deepl
    from langdetect import detect, LangDetectException
    _DEPS_OK = True
except ImportError:
    _DEPS_OK = False

# Entity name set by TranslationComponent in the NLU pipeline
_LANG_ENTITY = "__lang__"

# Fallback: langdetect code → DeepL target code (used when __lang__ entity absent)
_LANGDETECT_TO_DEEPL: dict = {
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

_translator: Optional[object] = None


def _get_translator():
    global _translator
    if _translator is None and _DEPS_OK:
        key = os.environ.get("DEEPL_API_KEY", "")
        if key:
            try:
                _translator = deepl.Translator(key)
            except Exception as exc:
                logger.warning(f"translation.py: DeepL init failed — {exc}")
    return _translator


def get_lang(tracker) -> Optional[str]:
    """
    Return the DeepL target language code for the current user turn, or None
    for English.

    Priority:
      1. __lang__ entity  — set by TranslationComponent during NLU (most reliable)
      2. language slot    — persisted from a previous turn (handles short follow-ups)
      3. langdetect       — last-resort fallback when the entity is missing
    """
    # 1. Entity set by NLU component
    for entity in tracker.latest_message.get("entities", []):
        if entity.get("entity") == _LANG_ENTITY:
            return entity["value"]

    # 2. Slot from a previous turn
    slot = tracker.get_slot("language")
    if slot:
        return slot

    # 3. Langdetect fallback (action server has no DeepL dependency for detection)
    if _DEPS_OK:
        text = (tracker.latest_message.get("text") or "").strip()
        if len(text) >= 4:
            try:
                raw = detect(text)
                return _LANGDETECT_TO_DEEPL.get(raw)
            except Exception:
                pass

    return None


def translate_response(text: str, lang: Optional[str]) -> str:
    """
    Translate an English response string to the target language.
    Returns the original text unchanged on any error or when lang is None/English.
    DeepL preserves Markdown (*bold*, _italic_, bullet lists).
    """
    if not lang or lang.upper().startswith("EN"):
        return text

    t = _get_translator()
    if not t:
        logger.warning(
            "translate_response: no DeepL translator available "
            f"(DEEPL_API_KEY set? _DEPS_OK={_DEPS_OK})"
        )
        return text

    try:
        result = t.translate_text(text, source_lang="EN", target_lang=lang)
        return result.text
    except Exception as exc:
        logger.warning(f"translate_response to {lang} failed: {exc}")
        return text
