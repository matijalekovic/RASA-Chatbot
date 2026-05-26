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

_GEMINI_MODEL = "gemini-3.1-flash-lite"
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
_TRANSLATION_TIMEOUT_SECONDS = float(os.environ.get("TRANSLATION_TIMEOUT_SECONDS", "8.0"))
_TRANSLATION_BATCH_TIMEOUT_SECONDS = float(
    os.environ.get("TRANSLATION_BATCH_TIMEOUT_SECONDS", "12.0")
)
_TRANSLATION_PROXY_TIMEOUT_SECONDS = float(
    os.environ.get("TRANSLATION_PROXY_TIMEOUT_SECONDS", "12.0")
)
_TRANSLATION_LONG_PROXY_TIMEOUT_SECONDS = float(
    os.environ.get("TRANSLATION_LONG_PROXY_TIMEOUT_SECONDS", "24.0")
)
_LONG_TRANSLATION_CHUNK_CHARS = int(
    os.environ.get("LONG_TRANSLATION_CHUNK_CHARS", "1800")
)
_MAX_INDIVIDUAL_TRANSLATION_FALLBACKS = int(
    os.environ.get("MAX_INDIVIDUAL_TRANSLATION_FALLBACKS", "8")
)
_BATCH_DELIMITER = "<<<1PAX_TRANSLATION_SPLIT_DO_NOT_TRANSLATE>>>"
_TRANSLATION_PROXY_URL = os.environ.get(
    "TRANSLATION_PROXY_URL",
    f"http://127.0.0.1:{os.environ.get('TRANSLATE_PORT', '5056')}/translate",
).strip()
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


def _proxy_translate_texts(
    texts: list[str],
    lang: str,
    timeout: float = _TRANSLATION_PROXY_TIMEOUT_SECONDS,
) -> Optional[list[str]]:
    """Ask the local translation proxy to translate English responses."""
    if not _TRANSLATION_PROXY_URL:
        return None

    body = {
        "texts": texts,
        "target_lang": lang,
    }
    req = urllib.request.Request(
        _TRANSLATION_PROXY_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read())
    except (
        TimeoutError,
        socket.timeout,
        urllib.error.URLError,
        urllib.error.HTTPError,
        OSError,
        ValueError,
    ) as exc:
        logger.warning(f"Translation proxy call failed: {exc}")
        return None

    if result.get("translation_enabled") is False or result.get("translation_error"):
        return None

    translated = result.get("texts")
    if (
        isinstance(translated, list)
        and len(translated) == len(texts)
        and all(isinstance(item, str) for item in translated)
    ):
        return translated

    if len(texts) == 1 and isinstance(result.get("text"), str):
        return [result["text"]]

    logger.warning("Translation proxy returned an unexpected response shape.")
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


def _extract_delimited_batch(raw_text: str, expected_len: int) -> Optional[list[str]]:
    parts = [part.strip() for part in raw_text.strip().split(_BATCH_DELIMITER)]
    if len(parts) != expected_len:
        return None
    return parts


def _translate_one_uncached(text: str, lang: str) -> str:
    proxied = _proxy_translate_texts([text], lang)
    if proxied is not None:
        output = proxied[0]
        _cache_put(lang, text, output)
        return output

    lang_name = _LANG_NAMES.get(lang, lang)
    translated = _gemini_call(
        prompt=f"Translate to {lang_name}: {text}",
        system_instruction=(
            "You are a translator. Output ONLY the translated text. "
            "Preserve all Markdown formatting exactly (bold **, bullets •, hyphens -, etc.). "
            "Keep brand names, project names, URLs, patents, and technical acronyms themselves "
            "intact when needed, but translate job titles, role labels, service names, UI labels, "
            "and every explanatory phrase. "
            "No explanations, no quotes, no notes."
        ),
        timeout=_TRANSLATION_TIMEOUT_SECONDS,
    )
    if translated is not None:
        _cache_put(lang, text, translated)
        return translated

    return text


def _split_long_text(text: str, max_chars: int = _LONG_TRANSLATION_CHUNK_CHARS) -> list[str]:
    """Split long Markdown-ish text on paragraph/line boundaries for translation."""
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    current = ""

    def push(part: str) -> None:
        nonlocal current
        if not part:
            return
        candidate = part if not current else f"{current}\n\n{part}"
        if len(candidate) <= max_chars:
            current = candidate
            return
        if current:
            chunks.append(current)
            current = ""
        if len(part) <= max_chars:
            current = part
            return

        line_current = ""
        for line in part.splitlines():
            candidate_line = line if not line_current else f"{line_current}\n{line}"
            if len(candidate_line) <= max_chars:
                line_current = candidate_line
                continue
            if line_current:
                chunks.append(line_current)
            line_current = line
        if line_current:
            current = line_current

    for paragraph in text.split("\n\n"):
        push(paragraph)

    if current:
        chunks.append(current)

    return chunks or [text]


def _translate_long_uncached(text: str, lang: str) -> str:
    """Translate long responses in smaller chunks instead of returning English."""
    chunks = _split_long_text(text)
    if len(chunks) == 1:
        return _translate_one_uncached(text, lang)

    proxied = _proxy_translate_texts(
        chunks,
        lang,
        timeout=_TRANSLATION_LONG_PROXY_TIMEOUT_SECONDS,
    )
    if proxied is not None:
        output = "\n\n".join(proxied)
        _cache_put(lang, text, output)
        return output

    logger.warning(
        "Long response batch translation failed; falling back to %s chunk translations.",
        len(chunks),
    )
    translated_chunks = [_translate_one_uncached(chunk, lang) for chunk in chunks]
    output = "\n\n".join(translated_chunks)
    _cache_put(lang, text, output)
    return output


def _translate_remaining_with_proxy_chunks(
    remaining: list[tuple[int, str]],
    translated: list[Optional[str]],
    lang: str,
) -> None:
    """Retry failed batches in small proxy batches before using single calls."""
    if len(remaining) <= 1:
        return

    chunk: list[tuple[int, str]] = []
    chunk_chars = 0

    def flush() -> None:
        nonlocal chunk, chunk_chars
        if not chunk:
            return
        sources = [source for _, source in chunk]
        proxied = _proxy_translate_texts(sources, lang)
        if proxied is not None:
            for (index, source), item in zip(chunk, proxied):
                translated[index] = item
                _cache_put(lang, source, item)
        chunk = []
        chunk_chars = 0

    for item in remaining:
        _, source = item
        source_len = len(source)
        if chunk and (
            len(chunk) >= 2
            or chunk_chars + source_len > _MAX_SYNC_TRANSLATION_BATCH_CHARS
        ):
            flush()
        chunk.append(item)
        chunk_chars += source_len
    flush()


def translate_responses(texts: list[str], lang: Optional[str]) -> list[str]:
    """
    Translate a group of English response strings to the target language.
    Batches uncached strings when possible, then retries smaller chunks before
    falling back to source text. This keeps selected-language conversations from
    silently switching back to English when one large/busy batch misses.
    """
    lang_code = _normalize_lang(lang)
    if not texts or not lang_code:
        return list(texts)

    translated: list[Optional[str]] = []
    pending: list[tuple[int, str]] = []

    for text in texts:
        cached = _cache_get(lang_code, text)
        if cached is not None:
            translated.append(cached)
            continue

        if len(text) > _MAX_SYNC_TRANSLATION_CHARS:
            translated.append(_translate_long_uncached(text, lang_code))
            continue

        translated.append(None)
        pending.append((len(translated) - 1, text))

    if len(pending) > 1:
        pending_texts = [text for _, text in pending]
        proxied_batch = _proxy_translate_texts(
            pending_texts,
            lang_code,
            timeout=_TRANSLATION_PROXY_TIMEOUT_SECONDS,
        )
        if proxied_batch is not None:
            for (index, source), item in zip(pending, proxied_batch):
                translated[index] = item
                _cache_put(lang_code, source, item)

    remaining_for_batch = [
        (index, source) for index, source in pending if translated[index] is None
    ]

    if len(remaining_for_batch) > 1:
        pending_texts = [text for _, text in remaining_for_batch]
        total_chars = sum(len(text) for text in pending_texts)
        if total_chars <= _MAX_SYNC_TRANSLATION_BATCH_CHARS:
            lang_name = _LANG_NAMES.get(lang_code, lang_code)
            batch_text = f"\n\n{_BATCH_DELIMITER}\n\n".join(pending_texts)
            raw_batch = _gemini_call(
                prompt=(
                    f"Translate each segment below to {lang_name}. Keep brand names, "
                    "project names, URLs, Markdown markers, and technical acronyms themselves "
                    "intact when needed, but translate job titles, role labels, service names, UI labels, "
                    "and every explanatory phrase. Keep this delimiter "
                    f"line exactly unchanged between segments: {_BATCH_DELIMITER}\n\n"
                    f"{batch_text}"
                ),
                system_instruction=(
                    "You are a translator. Output ONLY the translated segments separated "
                    "by the exact delimiter. Preserve Markdown formatting exactly. No "
                    "code fences, no explanations, no notes."
                ),
                timeout=_TRANSLATION_BATCH_TIMEOUT_SECONDS,
            )
            parsed_batch = (
                _extract_delimited_batch(raw_batch, len(pending_texts))
                if raw_batch is not None
                else None
            )
            if parsed_batch is not None:
                for (index, source), item in zip(remaining_for_batch, parsed_batch):
                    translated[index] = item
                    _cache_put(lang_code, source, item)
            else:
                logger.warning("Gemini batch translation failed; falling back to singles.")

    remaining = [(index, source) for index, source in pending if translated[index] is None]
    _translate_remaining_with_proxy_chunks(remaining, translated, lang_code)
    remaining = [(index, source) for index, source in pending if translated[index] is None]

    if len(remaining) > _MAX_INDIVIDUAL_TRANSLATION_FALLBACKS:
        logger.warning(
            "Translating %s individual fallback chunks after batch miss; "
            "this may add response latency.",
            len(remaining),
        )

    for index, source in remaining:
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
