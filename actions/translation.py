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
import threading
import urllib.error
import urllib.request
from collections import OrderedDict
from typing import Optional

logger = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-3.5-flash"
_GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{_GEMINI_MODEL}:generateContent"
)
_MAX_SYNC_TRANSLATION_CHARS = int(os.environ.get("MAX_SYNC_TRANSLATION_CHARS", "2400"))
_MAX_SYNC_TRANSLATION_BATCH_CHARS = int(
    os.environ.get("MAX_SYNC_TRANSLATION_BATCH_CHARS", "6000")
)
_MAX_TRANSLATION_CACHE_ENTRIES = int(
    os.environ.get("MAX_TRANSLATION_CACHE_ENTRIES", "512")
)
_TRANSLATION_CACHE: OrderedDict[tuple[str, str], str] = OrderedDict()
_TRANSLATION_CACHE_LOCK = threading.Lock()

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


def _normalize_lang(lang: Optional[str]) -> Optional[str]:
    if not lang:
        return None
    normalized = lang.upper()
    if normalized.startswith("EN"):
        return None
    return normalized


def _cache_get(lang: str, text: str) -> Optional[str]:
    if _MAX_TRANSLATION_CACHE_ENTRIES <= 0:
        return None

    key = (lang, text)
    with _TRANSLATION_CACHE_LOCK:
        if key not in _TRANSLATION_CACHE:
            return None
        value = _TRANSLATION_CACHE[key]
        _TRANSLATION_CACHE.move_to_end(key)
        return value


def _cache_put(lang: str, text: str, translated: str) -> None:
    if _MAX_TRANSLATION_CACHE_ENTRIES <= 0:
        return

    key = (lang, text)
    with _TRANSLATION_CACHE_LOCK:
        _TRANSLATION_CACHE[key] = translated
        _TRANSLATION_CACHE.move_to_end(key)
        while len(_TRANSLATION_CACHE) > _MAX_TRANSLATION_CACHE_ENTRIES:
            _TRANSLATION_CACHE.popitem(last=False)


def _extract_json_array(raw_text: str, expected_len: int) -> Optional[list[str]]:
    payload = raw_text.strip()
    if payload.startswith("```"):
        payload = payload.split("\n", 1)[1] if "\n" in payload else payload
        if payload.endswith("```"):
            payload = payload.rsplit("```", 1)[0]
        payload = payload.strip()

    try:
        parsed = json.loads(payload)
    except ValueError:
        start = payload.find("[")
        end = payload.rfind("]")
        if start == -1 or end <= start:
            return None
        try:
            parsed = json.loads(payload[start : end + 1])
        except ValueError:
            return None

    if (
        isinstance(parsed, list)
        and len(parsed) == expected_len
        and all(isinstance(item, str) for item in parsed)
    ):
        return parsed
    return None


def _translate_one_uncached(text: str, lang: str) -> str:
    lang_name = _LANG_NAMES.get(lang, lang)
    translated = _gemini_call(
        prompt=f"Translate to {lang_name}: {text}",
        system_instruction=(
            "You are a translator. Output ONLY the translated text. "
            "Preserve all Markdown formatting exactly (bold **, bullets •, hyphens -, etc.). "
            "No explanations, no quotes, no notes."
        ),
    )
    if translated is None:
        return text
    _cache_put(lang, text, translated)
    return translated


def translate_responses(texts: list[str], lang: Optional[str]) -> list[str]:
    """
    Translate a group of English response strings to the target language.
    Batches uncached strings into one Gemini call when possible, preserving the
    original fallback behavior for oversized strings or failed translations.
    """
    lang_code = _normalize_lang(lang)
    if not texts or not lang_code:
        return list(texts)

    translated: list[Optional[str]] = []
    pending: list[tuple[int, str]] = []

    for text in texts:
        if len(text) > _MAX_SYNC_TRANSLATION_CHARS:
            logger.warning(
                "Skipping synchronous response translation for %s chars; "
                "returning source text to avoid action timeout.",
                len(text),
            )
            translated.append(text)
            continue

        cached = _cache_get(lang_code, text)
        if cached is not None:
            translated.append(cached)
            continue

        translated.append(None)
        pending.append((len(translated) - 1, text))

    if len(pending) > 1:
        pending_texts = [text for _, text in pending]
        total_chars = sum(len(text) for text in pending_texts)
        if total_chars <= _MAX_SYNC_TRANSLATION_BATCH_CHARS:
            lang_name = _LANG_NAMES.get(lang_code, lang_code)
            raw_batch = _gemini_call(
                prompt=(
                    f"Translate this JSON array of English strings to {lang_name}. "
                    "Return ONLY a JSON array of strings in the same order:\n"
                    f"{json.dumps(pending_texts, ensure_ascii=False)}"
                ),
                system_instruction=(
                    "You are a translator. Output ONLY valid JSON. Preserve all "
                    "Markdown formatting exactly inside each string. No code fences, "
                    "no explanations, no notes."
                ),
                timeout=10.0,
            )
            parsed_batch = (
                _extract_json_array(raw_batch, len(pending_texts))
                if raw_batch is not None
                else None
            )
            if parsed_batch is not None:
                for (index, source), item in zip(pending, parsed_batch):
                    translated[index] = item
                    _cache_put(lang_code, source, item)
            else:
                logger.warning("Gemini batch translation failed; falling back to singles.")

    for index, source in pending:
        if translated[index] is None:
            translated[index] = _translate_one_uncached(source, lang_code)

    return [
        item if item is not None else source
        for item, source in zip(translated, texts)
    ]


def translate_response(text: str, lang: Optional[str]) -> str:
    """
    Translate an English response string to the target language.
    Returns the original text unchanged on any error or when lang is None/English.
    Gemini preserves Markdown (*bold*, _italic_, bullet lists).
    """
    return translate_responses([text], lang)[0]
