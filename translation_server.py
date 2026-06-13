#!/usr/bin/env python3
"""
Tiny translation proxy for the 1PAX chatbot.

POST /translate  { "text": "...", "source_lang": "FR" }
→ { "text": "... (in English)" }

Runs on port 5056.
Nginx proxies /api/translate → http://localhost:5056/translate
The UI calls this before sending messages to Rasa so that DIET always
sees English input regardless of the user's selected language.

Requires: GEMINI_API_KEY env var.
"""

import json
import os
import re
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    from langdetect import detect
    _LANGDETECT_OK = True
except ImportError:
    _LANGDETECT_OK = False

_GEMINI_MODEL = "gemini-3.1-flash-lite"
_GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{_GEMINI_MODEL}:generateContent"
)
_BATCH_DELIMITER = "<<<1PAX_TRANSLATION_SPLIT_DO_NOT_TRANSLATE>>>"

_LANG_NAMES = {
    "FR": "French",
    "ES": "Spanish",
    "PT-PT": "European Portuguese",
    "PT-BR": "Brazilian Portuguese",
    "ZH-HANS": "Simplified Chinese",
    "ZH-HANT": "Traditional Chinese",
    "SR": "Serbian (Latin script, never Cyrillic)",
    "DE": "German",
    "IT": "Italian",
    "NL": "Dutch",
    "PL": "Polish",
    "JA": "Japanese",
    "KO": "Korean",
    "AR": "Arabic",
}

_LANG_MAP = {
    "en": "",
    "es": "ES",
    "fr": "FR",
    "zh-cn": "ZH-HANS",
    "zh-tw": "ZH-HANT",
    "zh": "ZH-HANS",
    "pt": "PT-PT",
    "sr": "SR",
    "hr": "SR",
    "bs": "SR",
}

def _read_api_key() -> str:
    # Support both names so deployment envs are less brittle.
    return (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
    )


_API_KEY = _read_api_key()
_READY = bool(_API_KEY)
if _READY:
    print("[translate] Gemini REST ready.")
else:
    print("[translate] GEMINI_API_KEY / GOOGLE_API_KEY not set — translation disabled.")

_CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
}


# Normalize "1pax" → "1PAX" so Gemini treats it as a company name, not a number.
def _normalize(text: str) -> str:
    return re.sub(r'\b1pax\b', '1PAX', text, flags=re.IGNORECASE)


def _normalize_target_lang(lang: str) -> str:
    normalized = (lang or "").strip().upper()
    if not normalized or normalized.startswith("EN"):
        return ""
    if normalized == "PT":
        return "PT-PT"
    if normalized == "ZH":
        return "ZH-HANS"
    return normalized


def _normalize_detected_lang(lang: str) -> str:
    raw = (lang or "").strip().replace("_", "-")
    if not raw:
        return ""
    lowered = raw.lower()
    if lowered in {"und", "unknown", "un", "none", "null"}:
        return ""
    if lowered.startswith("en"):
        return ""
    if lowered in _LANG_MAP:
        return _LANG_MAP[lowered]
    if lowered == "pt":
        return "PT-PT"
    if lowered == "zh":
        return "ZH-HANS"
    return lowered.upper()


def _detect_source_lang(text: str) -> str:
    if not _LANGDETECT_OK or len(text.strip()) < 4:
        return ""
    try:
        return _normalize_detected_lang(detect(text))
    except Exception:
        return ""


def _extract_json_object(raw_text: str) -> dict:
    payload = (raw_text or "").strip()
    if payload.startswith("```"):
        payload = payload.split("\n", 1)[1] if "\n" in payload else payload
        if payload.endswith("```"):
            payload = payload.rsplit("```", 1)[0]
        payload = payload.strip()
    try:
        return json.loads(payload)
    except ValueError:
        start = payload.find("{")
        end = payload.rfind("}")
        if start == -1 or end <= start:
            return {}
        try:
            return json.loads(payload[start : end + 1])
        except ValueError:
            return {}


def _identify_source_lang_with_gemini(text: str, source_hint: str = "") -> tuple[str, bool]:
    if not _READY or not text.strip():
        return "", False

    hint = _source_lang_name(source_hint) or source_hint or "none"
    try:
        raw = _gemini_call(
            prompt=(
                "Identify the primary language the user actually wrote in. "
                "Do not identify languages merely mentioned inside the text. "
                "If the text is a name, email, number, URL, or too short to identify, "
                "use the hint only if it is available; otherwise return UNKNOWN.\n\n"
                f"Hint: {hint}\n"
                f"Text: {text}\n\n"
                "Return JSON only: {\"language_code\":\"<ISO 639-1 or BCP-47 or UNKNOWN>\","
                "\"language_name\":\"<English name or UNKNOWN>\"}"
            ),
            system_instruction=(
                "You are a precise language identifier. Return only compact JSON. "
                "Use EN for English, SR for Serbian/Croatian/Bosnian Latin if appropriate, "
                "PT for Portuguese, ZH for Chinese, and UNKNOWN when uncertain."
            ),
            timeout=6.0,
        )
    except Exception as exc:
        print(f"[translate] Gemini language identification error: {exc}")
        return "", False

    payload = _extract_json_object(raw)
    lang = _normalize_detected_lang(
        str(payload.get("language_code") or payload.get("lang") or "")
    )
    raw_code = str(payload.get("language_code") or "").strip().lower()
    if lang or raw_code in {"en", "eng", "english"}:
        return lang, True
    return "", False


def _gemini_call(prompt: str, system_instruction: str, timeout: float = 10.0) -> str:
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "generationConfig": {"temperature": 0.1},
    }
    req = urllib.request.Request(
        f"{_GEMINI_URL}?key={_API_KEY}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        result = json.loads(resp.read())
    return result["candidates"][0]["content"]["parts"][0]["text"].strip()


def _source_lang_name(lang: str) -> str:
    normalized = (lang or "").strip().upper()
    if not normalized:
        return ""
    if normalized == "PT":
        normalized = "PT-PT"
    if normalized == "ZH":
        normalized = "ZH-HANS"
    return _LANG_NAMES.get(normalized, normalized)


def _translate_to_english(text: str, source_lang: str = "") -> str:
    source_name = _source_lang_name(source_lang)
    prompt = (
        f"Translate from {source_name} to English: {text}"
        if source_name
        else f"Translate to English: {text}"
    )
    return _gemini_call(
        prompt=prompt,
        system_instruction=(
            "You are a translator. Output ONLY the translated text. "
            "If the input is already English, output it unchanged. "
            "Preserve names, company names, project names, emails, URLs, phone numbers, "
            "dates, times, airport codes, and acronyms exactly. "
            "If the input is Serbian, Croatian, or Bosnian written without accents, "
            "still translate it to natural English. "
            "No explanations, no quotes, no notes."
        ),
    )


def _translate_from_english(text: str, target_lang: str) -> str:
    lang_name = _LANG_NAMES.get(target_lang, target_lang)
    return _gemini_call(
        prompt=f"Translate to {lang_name}: {text}",
        system_instruction=(
            "You are a translator. Output ONLY the translated text. "
            "Preserve all Markdown formatting exactly (bold **, bullets •, hyphens -, etc.). "
            "Keep brand names, project names, URLs, patents, and technical acronyms themselves "
            "intact when needed, but translate job titles, role labels, service names, UI labels, "
            "and every explanatory phrase. No explanations, no quotes, no notes."
        ),
    )


def _translate_many_from_english(texts: list[str], target_lang: str) -> list[str]:
    if len(texts) == 1:
        return [_translate_from_english(texts[0], target_lang)]

    lang_name = _LANG_NAMES.get(target_lang, target_lang)
    batch_text = f"\n\n{_BATCH_DELIMITER}\n\n".join(texts)
    raw = _gemini_call(
        prompt=(
            f"Translate each segment below to {lang_name}. Keep brand names, "
            "project names, URLs, Markdown markers, patents, and technical acronyms themselves "
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
    )
    translated = [part.strip() for part in raw.split(_BATCH_DELIMITER)]
    if len(translated) != len(texts):
        raise ValueError("Gemini returned an unexpected number of translated segments")
    return translated


def _translate_project_labels_from_english(texts: list[str], target_lang: str) -> list[str]:
    """Translate visible project-list labels while preserving lookup-safe names."""
    if not texts:
        return []

    lang_name = _LANG_NAMES.get(target_lang, target_lang)
    batch_text = f"\n\n{_BATCH_DELIMITER}\n\n".join(texts)
    raw = _gemini_call(
        prompt=(
            f"Translate each project list label below to {lang_name}. Preserve proper nouns, "
            "city names, country names, brand names, airport codes, acronyms, numbers, years, "
            "currency values, and URLs. Translate generic architecture and infrastructure terms "
            "inside titles, such as airport, international airport, terminal, station, control tower, "
            "food hall, commercial areas, passenger experience, refurbishment, expansion, new building, "
            "wayfinding, signage, masterplan, offices, headquarters, branches, and network. "
            "Keep this delimiter line exactly unchanged between segments: "
            f"{_BATCH_DELIMITER}\n\n{batch_text}"
        ),
        system_instruction=(
            "You are a concise UI localization translator for an architecture portfolio. "
            "Output ONLY the translated labels separated by the exact delimiter. Preserve Markdown "
            "or punctuation already present. Use Serbian Latin script for Serbian, never Cyrillic. "
            "No explanations, no quotes, no notes."
        ),
    )
    translated = [part.strip() for part in raw.split(_BATCH_DELIMITER)]
    if len(translated) != len(texts):
        raise ValueError("Gemini returned an unexpected number of translated project labels")
    return translated


class Handler(BaseHTTPRequestHandler):

    def _send(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        for k, v in _CORS.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send({})

    def do_GET(self):
        if self.path.rstrip("/") == "/health":
            self._send({
                "status": "ok",
                "translation_enabled": _READY,
                "model": _GEMINI_MODEL,
            })
            return
        self._send({"error": "not found"}, 404)

    def do_POST(self):
        if self.path.rstrip("/") != "/translate":
            self._send({"error": "not found"}, 404)
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length))
        except Exception:
            self._send({"error": "invalid JSON"}, 400)
            return

        target_lang = _normalize_target_lang(
            data.get("target_lang") or data.get("target") or ""
        )
        raw_texts = data.get("texts")
        mode = (data.get("mode") or "").strip()

        if target_lang:
            if raw_texts is not None:
                if (
                    not isinstance(raw_texts, list)
                    or not all(isinstance(item, str) for item in raw_texts)
                ):
                    self._send({"error": "texts must be a list of strings"}, 400)
                    return
                texts = [item.strip() for item in raw_texts]
                if not _READY:
                    self._send({"texts": texts, "translation_enabled": False})
                    return
                try:
                    if mode == "project_labels":
                        translated_texts = _translate_project_labels_from_english(
                            texts,
                            target_lang,
                        )
                    else:
                        translated_texts = _translate_many_from_english(texts, target_lang)
                    self._send({"texts": translated_texts, "translation_enabled": True})
                except Exception as exc:
                    print(f"[translate] Gemini output error: {exc}")
                    self._send({
                        "texts": texts,
                        "translation_enabled": True,
                        "translation_error": True,
                    })
                return

            text = (data.get("text") or "").strip()
            if not text or not _READY:
                self._send({"text": text, "translation_enabled": _READY})
                return
            try:
                translated = _translate_from_english(text, target_lang)
                self._send({"text": translated, "translation_enabled": True})
            except Exception as exc:
                print(f"[translate] Gemini output error: {exc}")
                self._send({
                    "text": text,
                    "translation_enabled": True,
                    "translation_error": True,
                })
            return

        text = _normalize((data.get("text") or "").strip())
        source_hint = _normalize_detected_lang(
            data.get("source_lang") or data.get("source") or ""
        )
        identified_lang = ""
        language_identified = False
        if data.get("identify_language"):
            identified_lang, language_identified = _identify_source_lang_with_gemini(
                text,
                source_hint,
            )
        detected_lang = _detect_source_lang(text)
        source_lang = identified_lang or detected_lang or source_hint

        if not text:
            self._send({
                "text": text,
                "translation_enabled": _READY,
                "identified_lang": identified_lang,
                "language_identified": language_identified,
                "detected_lang": detected_lang,
                "source_lang": source_lang,
            })
            return

        if not _READY:
            self._send({
                "text": text,
                "translation_enabled": False,
                "identified_lang": identified_lang,
                "language_identified": language_identified,
                "detected_lang": detected_lang,
                "source_lang": source_lang,
            })
            return

        try:
            translated = _translate_to_english(text, source_lang)
            self._send({
                "text": translated,
                "translation_enabled": True,
                "identified_lang": identified_lang,
                "language_identified": language_identified,
                "detected_lang": detected_lang,
                "source_lang": source_lang,
            })
        except Exception as exc:
            print(f"[translate] Gemini error: {exc}")
            self._send({
                "text": text,
                "translation_enabled": True,
                "translation_error": True,
                "identified_lang": identified_lang,
                "language_identified": language_identified,
                "detected_lang": detected_lang,
                "source_lang": source_lang,
            })

    def log_message(self, *args):
        pass


class TranslationHTTPServer(ThreadingHTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    port = int(os.environ.get("TRANSLATE_PORT", 5056))
    print(f"[translate] Listening on port {port}")
    TranslationHTTPServer(("0.0.0.0", port), Handler).serve_forever()
