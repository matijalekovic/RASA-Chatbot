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
import urllib.error
import urllib.request
from typing import Any, Dict, List, Text

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData

logger = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-2.5-flash-lite"
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
            config.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "")
        )
        if not self._api_key:
            logger.info(
                "TranslationComponent: GEMINI_API_KEY not set — "
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

        translated = self._translate_to_english(text)
        if translated:
            message.set("text", translated)
            logger.debug(f"[translate-in] → EN: '{text}' → '{translated}'")

    def _translate_to_english(self, text: str) -> str:
        body = {
            "contents": [{"parts": [{"text": f"Translate to English: {text}"}]}],
            "systemInstruction": {
                "parts": [{
                    "text": (
                        "You are a translator. Output ONLY the translated text. "
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
