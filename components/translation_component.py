"""
TranslationComponent — Custom Rasa NLU GraphComponent

Placed FIRST in the NLU pipeline (config.yml). For each incoming user
message it:
  1. Detects the language with langdetect (fast, local, no API).
  2. If non-English, translates the text to English via Gemini REST so the
     English-trained DIET classifier can classify the intent correctly.
  3. Stores the detected language code (e.g. "FR", "ZH-HANS") as a
     special entity named "__lang__" in the message, so downstream actions
     can translate their English responses back to the user's language.

Note: the UI already translates input via translation_server.py before
sending to Rasa. This component acts as a fallback for direct API access.

Training data is never translated — it is already in English.

Requires:  pip install langdetect
Env var:   GEMINI_API_KEY
"""

import json
import logging
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Text

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData

logger = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-3.1-flash-lite"
_GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{_GEMINI_MODEL}:generateContent"
)

try:
    from langdetect import detect, LangDetectException
    _DEPS_OK = True
except ImportError:
    _DEPS_OK = False
    logger.warning(
        "TranslationComponent: 'langdetect' not installed — "
        "multilingual input translation disabled."
    )

_LANG_MAP: Dict[str, str] = {
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

LANG_ENTITY = "__lang__"

_LANG_NAMES = {
    "FR": "French",
    "ES": "Spanish",
    "PT-PT": "European Portuguese",
    "PT-BR": "Brazilian Portuguese",
    "ZH-HANS": "Simplified Chinese",
    "ZH-HANT": "Traditional Chinese",
    "SR": "Serbian (Latin script, never Cyrillic)",
}

_ENGLISH_HINT_WORDS = {
    "a",
    "about",
    "airport",
    "airports",
    "am",
    "an",
    "and",
    "are",
    "as",
    "at",
    "based",
    "bim",
    "build",
    "buildings",
    "budget",
    "can",
    "company",
    "contact",
    "cost",
    "design",
    "designer",
    "designers",
    "do",
    "does",
    "doing",
    "exactly",
    "firm",
    "for",
    "founded",
    "from",
    "have",
    "help",
    "hello",
    "hi",
    "how",
    "in",
    "is",
    "kind",
    "list",
    "me",
    "mission",
    "of",
    "offer",
    "offers",
    "overview",
    "pax",
    "projects",
    "schedule",
    "services",
    "show",
    "sofia",
    "studio",
    "team",
    "tell",
    "the",
    "there",
    "what",
    "where",
    "who",
    "work",
    "you",
    "your",
}

try:
    from actions.projects_data import PROJECTS as _PROJECTS_FOR_LANG_HINTS
except Exception:
    _PROJECTS_FOR_LANG_HINTS = {}

for _project_key, _project_data in _PROJECTS_FOR_LANG_HINTS.items():
    _ENGLISH_HINT_WORDS.update(
        re.findall(r"[a-zA-Z]+", _project_key.replace("_", " ").lower())
    )
    for _field in ("display_name", "location", "category"):
        _ENGLISH_HINT_WORDS.update(
            re.findall(r"[a-zA-Z]+", str(_project_data.get(_field, "")).lower())
        )


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_FEATURIZER, is_trainable=False
)
class TranslationComponent(GraphComponent):
    """Translates non-English user messages to English before NLU classification."""

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        return {"gemini_api_key": None}

    def __init__(self, config: Dict[Text, Any]) -> None:
        self._api_key = (
            config.get("gemini_api_key")
            or os.environ.get("GEMINI_API_KEY", "")
            or os.environ.get("GOOGLE_API_KEY", "")
        )
        if not self._api_key:
            logger.info(
                "TranslationComponent: GEMINI_API_KEY / GOOGLE_API_KEY not set — "
                "input translation will be skipped."
            )

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> "TranslationComponent":
        return cls(config)

    def process(self, messages: List[Message]) -> List[Message]:
        for msg in messages:
            self._handle(msg)
        return messages

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        return training_data  # Already English — never translate training data

    def _handle(self, message: Message) -> None:
        text = message.get("text", "")
        if not text or not _DEPS_OK:
            return

        metadata = message.get("metadata") or {}
        metadata_lang = _normalize_lang_code(metadata.get("lang"))
        if metadata_lang:
            # The web UI normally translates user input to English before
            # sending it to Rasa, and carries the target response language in
            # metadata. If that proxy returns the original non-English text,
            # do one more guarded translation pass here instead of letting NLU
            # classify untranslated Serbian/French/etc.
            self._set_lang_entity(message, metadata_lang)
            if _looks_like_english(text):
                return
            if not self._api_key:
                return
            translated = self._translate_to_english(text, metadata_lang)
            if translated:
                message.set("text", translated)
                logger.debug(f"[translate-in:metadata] → EN: '{text}' → '{translated}'")
            return

        if _looks_like_english(text):
            return

        try:
            raw_lang = detect(text)
        except Exception:
            raw_lang = "en"

        lang_code = _LANG_MAP.get(raw_lang)
        if not lang_code:
            return

        self._set_lang_entity(message, lang_code)

        if not self._api_key:
            return

        translated = self._translate_to_english(text, lang_code)
        if translated:
            message.set("text", translated)
            logger.debug(f"[translate-in] → EN: '{text}' → '{translated}'")

    def _translate_to_english(self, text: str, source_lang: Optional[str] = None) -> str:
        source_name = _LANG_NAMES.get(source_lang or "", source_lang or "")
        prompt = (
            f"Translate from {source_name} to English: {text}"
            if source_name
            else f"Translate to English: {text}"
        )
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {
                "parts": [{
                    "text": (
                        "You are a translator. Output ONLY the translated text. "
                        "If the input is already English, output it unchanged. "
                        "Preserve names, company names, project names, emails, URLs, phone numbers, "
                        "dates, times, airport codes, and acronyms exactly. "
                        "If the input is Serbian, Croatian, or Bosnian written without accents, "
                        "still translate it to natural English. "
                        "No explanations, no quotes, no notes."
                    )
                }]
            },
            "generationConfig": {"temperature": 0.1},
        }
        req = urllib.request.Request(
            f"{_GEMINI_URL}?key={self._api_key}",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                result = json.loads(resp.read())
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, IndexError, ValueError) as exc:
            logger.warning(f"TranslationComponent: input translation failed — {exc}")
            return ""

    def _set_lang_entity(self, message: Message, lang_code: str) -> None:
        entities = list(message.get("entities") or [])
        entities.append({
            "entity": LANG_ENTITY,
            "value": lang_code,
            "confidence": 1.0,
            "extractor": "TranslationComponent",
        })
        message.set("entities", entities)


def _looks_like_english(text: str) -> bool:
    """Protect short English/domain phrases from langdetect false positives."""
    tokens = re.findall(r"[a-zA-Z]+", text.lower())
    if not tokens:
        return False
    if len(tokens) > 8:
        return False
    hits = sum(token in _ENGLISH_HINT_WORDS for token in tokens)
    if hits == len(tokens):
        return True
    starters = {"who", "what", "where", "when", "how", "tell", "show", "give", "can", "does", "is"}
    if tokens[0] in starters and hits >= max(2, len(tokens) // 2):
        return True
    return hits >= max(3, int(len(tokens) * 0.6))


def _normalize_lang_code(lang: Optional[str]) -> Optional[str]:
    normalized = (lang or "").strip().upper()
    if not normalized or normalized.startswith("EN"):
        return None
    if normalized == "PT":
        return "PT-PT"
    if normalized == "ZH":
        return "ZH-HANS"
    return normalized
