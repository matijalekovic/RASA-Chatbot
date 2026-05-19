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
import socket
import time
import unicodedata
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
    from langdetect import detect_langs, LangDetectException
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

_ENGLISH_MARKERS = {
    " the ",
    " and ",
    " is ",
    " are ",
    " was ",
    " were ",
    " with ",
    " about ",
    " what ",
    " who ",
    " where ",
    " when ",
    " how ",
    " tell ",
    " show ",
    " project",
    " projects",
    " airport",
    " design",
    " company",
    " team",
}


def _ascii_lower(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return ascii_text.casefold()


def _looks_like_english(text: str) -> bool:
    normalized = f" {_ascii_lower(text)} "
    if any(marker in normalized for marker in _ENGLISH_MARKERS):
        return True
    words = [word.strip(".,!?;:()[]{}'\"") for word in normalized.split()]
    common = {
        "a",
        "an",
        "do",
        "does",
        "did",
        "can",
        "could",
        "would",
        "should",
        "me",
        "you",
        "your",
        "it",
        "its",
    }
    return sum(1 for word in words if word in common) >= 2


def _quick_schedule_translation(text: str, lang_code: str) -> str:
    if lang_code != "SR":
        return ""

    lowered = _ascii_lower(text)
    stripped = lowered.strip(" .!?,;:")
    if stripped in {"da", "da molim", "moze", "moze tako", "vazi", "u redu"}:
        return "yes"
    if stripped in {"ne", "ne hvala", "nemoj"}:
        return "no"

    mentions_sofia_airport = (
        any(term in lowered for term in ("sofija", "sofia"))
        and any(term in lowered for term in ("aerodrom", "terminal"))
    )
    asks_budget = any(term in lowered for term in ("budzet", "budžet", "cena", "cijena", "koshta", "kosta"))
    if mentions_sofia_airport and asks_budget:
        return "What is the budget for Sofia Airport?"

    pieces = []

    next_week_requested = any(
        phrase in lowered
        for phrase in (
            "sledece nedelje",
            "sljedece nedelje",
            "sledecu nedelju",
            "sljedecu nedjelju",
            "sledece sedmice",
            "sljedece sedmice",
        )
    )

    if "sutra" in lowered:
        pieces.append("tomorrow")
    if "danas" in lowered:
        pieces.append("today")

    weekdays = {
        ("ponedeljak", "ponedjeljak", "ponedeljka", "ponedjeljka"): "Monday",
        ("utorak", "utorka"): "Tuesday",
        ("sreda", "srijeda", "sredu", "srijedu", "srede", "srijede"): "Wednesday",
        ("cetvrtak", "cetvrtka"): "Thursday",
        ("petak", "petka"): "Friday",
        ("subota", "subotu", "subote"): "Saturday",
        ("nedelja", "nedjelja", "nedelju", "nedjelju"): "Sunday",
    }
    mentioned_weekday = False
    for sr_words, en_word in weekdays.items():
        if any(re.search(rf"\b{re.escape(sr_word)}\b", lowered) for sr_word in sr_words):
            mentioned_weekday = True
            if "sledec" in lowered or "sljedec" in lowered or next_week_requested:
                pieces.append(f"next {en_word}")
            elif re.search(r"\bov(?:aj|og|e|u)\b", lowered):
                pieces.append(f"this {en_word}")
            else:
                pieces.append(en_word)
            break
    if next_week_requested and not mentioned_weekday:
        pieces.append("next week")

    if any(phrase in lowered for phrase in ("ujutru", "pre podne", "prije podne", "prepodne", "prijepodne")):
        pieces.append("morning")
    if any(phrase in lowered for phrase in ("popodne", "posle podne", "poslije podne", "poslepodne", "poslijepodne")):
        pieces.append("afternoon")
    if "uvece" in lowered or "vece" in lowered:
        pieces.append("evening")

    preference = " ".join(dict.fromkeys(pieces))

    if "termin" in lowered and ("slobod" in lowered or "dostup" in lowered):
        return f"which times are free {preference}".strip()

    wants_meeting = any(token in lowered for token in ("sastanak", "zakaz", "poziv"))
    wants_project = "projekat" in lowered and any(
        token in lowered for token in ("predloz", "nov", "diskut", "razgov")
    )
    if wants_meeting or wants_project:
        if preference:
            return f"I want to schedule a meeting {preference}"
        if wants_project:
            return "I want to schedule a meeting to discuss a new project"
        return "I want to schedule a meeting"

    if preference:
        return preference

    return ""


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
            try:
                self._handle(msg)
            except Exception as exc:
                logger.warning(
                    "TranslationComponent: skipped input translation after error — %s",
                    exc,
                )
        return messages

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        return training_data  # Already English — never translate training data

    def _handle(self, message: Message) -> None:
        text = message.get("text", "")
        if not text or not _DEPS_OK:
            return

        if _looks_like_english(text):
            return

        try:
            detected = detect_langs(text)
            best = detected[0] if detected else None
            raw_lang = best.lang if best else "en"
            confidence = float(best.prob) if best else 0.0
        except Exception:
            raw_lang = "en"
            confidence = 0.0

        if raw_lang == "en" or confidence < 0.70:
            return

        lang_code = _LANG_MAP.get(raw_lang)
        if not lang_code:
            return

        self._set_lang_entity(message, lang_code)

        quick_translation = _quick_schedule_translation(text, lang_code)
        if quick_translation:
            message.set("text", quick_translation)
            return

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
        last_error = None
        for attempt in range(2):
            req = urllib.request.Request(
                f"{_GEMINI_URL}?key={self._api_key}",
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=5.0) as resp:
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
                last_error = exc
                if attempt == 0:
                    time.sleep(0.25)

        logger.warning(f"TranslationComponent: input translation failed — {last_error}")
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
