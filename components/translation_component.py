"""
TranslationComponent — Custom Rasa NLU GraphComponent

Placed FIRST in the NLU pipeline (config.yml). For each incoming user
message it:
  1. Detects the language with langdetect (fast, local, no API).
  2. If non-English, translates the text to English via Gemini so the
     English-trained DIET classifier can classify the intent correctly.
  3. Stores the detected language code (e.g. "FR", "ZH-HANS") as a
     special entity named "__lang__" in the message, so downstream actions
     can translate their English responses back to the user's language.

Note: the UI already translates input via translation_server.py before
sending to Rasa. This component acts as a fallback for direct API access.

Training data is never translated — it is already in English.

Requires:  pip install google-genai langdetect
Env var:   GEMINI_API_KEY
"""

import os
import logging
from typing import Any, Dict, List, Text

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData

logger = logging.getLogger(__name__)

_MODEL = "gemini-2.5-flash-lite"

try:
    from google import genai
    from google.genai import types as genai_types
    from langdetect import detect, LangDetectException
    _DEPS_OK = True
except ImportError:
    _DEPS_OK = False
    logger.warning(
        "TranslationComponent: 'google-genai' or 'langdetect' not installed — "
        "multilingual input translation disabled."
    )

# langdetect ISO code → language code used in metadata/slots
_LANG_MAP: Dict[str, str] = {
    "es":    "ES",
    "fr":    "FR",
    "zh-cn": "ZH-HANS",
    "zh-tw": "ZH-HANT",
    "zh":    "ZH-HANS",
    "pt":    "PT-PT",
    "sr":    "SR",
    "hr":    "SR",  # Croatian often detected instead of Serbian Latin
    "bs":    "SR",  # Bosnian similarly confused
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
        self._client = None
        if not _DEPS_OK:
            return
        api_key = config.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            try:
                self._client = genai.Client(api_key=api_key)
                logger.info("TranslationComponent: Gemini translator initialised.")
            except Exception as exc:
                logger.warning(f"TranslationComponent: Gemini init failed — {exc}")

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> "TranslationComponent":
        return cls(config)

    # ── Inference ─────────────────────────────────────────────────────────────

    def process(self, messages: List[Message]) -> List[Message]:
        for msg in messages:
            self._handle(msg)
        return messages

    # ── Training ──────────────────────────────────────────────────────────────

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        return training_data  # Already English — never translate training data

    # ── Internals ─────────────────────────────────────────────────────────────

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
            return  # English or unsupported

        self._set_lang_entity(message, lang_code)

        if self._client:
            try:
                config = genai_types.GenerateContentConfig(
                    system_instruction="You are a translator. Output ONLY the translated text. No explanations, no quotes, no notes.",
                    temperature=0.1,
                )
                result = self._client.models.generate_content(
                    model=_MODEL,
                    contents=f"Translate to English: {text}",
                    config=config,
                )
                translated = result.text.strip()
                message.set("text", translated)
                logger.debug(f"[translate-in] → EN: '{text}' → '{translated}'")
            except Exception as exc:
                logger.warning(f"TranslationComponent: input translation failed — {exc}")

    def _set_lang_entity(self, message: Message, lang_code: str) -> None:
        entities = list(message.get("entities") or [])
        entities.append({
            "entity": LANG_ENTITY,
            "value": lang_code,
            "confidence": 1.0,
            "extractor": "TranslationComponent",
        })
        message.set("entities", entities)
