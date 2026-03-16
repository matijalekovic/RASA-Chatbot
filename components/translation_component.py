"""
TranslationComponent — Custom Rasa NLU GraphComponent

Placed FIRST in the NLU pipeline (config.yml). For each incoming user
message it:
  1. Detects the language with langdetect (fast, local, no API).
  2. If non-English, translates the text to English via DeepL so the
     English-trained DIET classifier can classify the intent correctly.
  3. Stores the detected DeepL target code (e.g. "FR", "ZH-HANS") as a
     special entity named "__lang__" in the message, so downstream actions
     can translate their English responses back to the user's language.

Training data is never translated — it is already in English.

Requires:  pip install deepl langdetect
Env var:   DEEPL_API_KEY  (free-tier key works; ends with :fx)
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

try:
    import deepl
    from langdetect import detect, LangDetectException
    _DEPS_OK = True
except ImportError:
    _DEPS_OK = False
    logger.warning(
        "TranslationComponent: 'deepl' or 'langdetect' not installed — "
        "multilingual input translation disabled."
    )

# langdetect ISO code → (DeepL source code, DeepL target code)
# DeepL source uses regional-neutral codes; target uses specific variants.
_LANG_MAP: Dict[str, tuple] = {
    "es":    ("ES",   "ES"),
    "fr":    ("FR",   "FR"),
    "zh-cn": ("ZH",   "ZH-HANS"),
    "zh-tw": ("ZH",   "ZH-HANT"),
    "zh":    ("ZH",   "ZH-HANS"),
    "pt":    ("PT",   "PT-PT"),
    "sr":    ("SR",   "SR"),
    "hr":    ("SR",   "SR"),   # Croatian often detected instead of Serbian Latin
    "bs":    ("SR",   "SR"),   # Bosnian similarly confused
}

# Entity name used to pass the detected language to the action server
LANG_ENTITY = "__lang__"


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_FEATURIZER, is_trainable=False
)
class TranslationComponent(GraphComponent):
    """Translates non-English user messages to English before NLU classification."""

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        return {"deepl_api_key": None}

    def __init__(self, config: Dict[Text, Any]) -> None:
        self._translator = None
        if not _DEPS_OK:
            return
        api_key = config.get("deepl_api_key") or os.environ.get("DEEPL_API_KEY", "")
        if api_key:
            try:
                self._translator = deepl.Translator(api_key)
                logger.info("TranslationComponent: DeepL translator initialised.")
            except Exception as exc:
                logger.warning(f"TranslationComponent: DeepL init failed — {exc}")

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
        """Called during prediction. Translate each message and tag language."""
        for msg in messages:
            self._handle(msg)
        return messages

    # ── Training ──────────────────────────────────────────────────────────────

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        """Training data is already English — return unchanged."""
        return training_data

    # ── Internals ─────────────────────────────────────────────────────────────

    def _handle(self, message: Message) -> None:
        text = message.get("text", "")
        if not text or not _DEPS_OK:
            return

        # Detect language
        try:
            raw_lang = detect(text)
        except Exception:
            raw_lang = "en"

        mapping = _LANG_MAP.get(raw_lang)
        if not mapping:
            return  # English or unsupported — no action

        src_code, tgt_code = mapping

        # Persist target code as a special entity for the action server
        self._set_lang_entity(message, tgt_code)

        # Translate to English for DIET
        if self._translator:
            try:
                result = self._translator.translate_text(
                    text, source_lang=src_code, target_lang="EN-US"
                )
                message.set("text", result.text)
                logger.debug(
                    f"[translate-in] {src_code} → EN: '{text}' → '{result.text}'"
                )
            except Exception as exc:
                logger.warning(f"TranslationComponent: input translation failed — {exc}")

    def _set_lang_entity(self, message: Message, target_code: str) -> None:
        """Append the __lang__ entity so actions can read detected language."""
        entities = list(message.get("entities") or [])
        entities.append({
            "entity": LANG_ENTITY,
            "value": target_code,
            "confidence": 1.0,
            "extractor": "TranslationComponent",
        })
        message.set("entities", entities)
