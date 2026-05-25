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
from http.server import BaseHTTPRequestHandler, HTTPServer

_GEMINI_MODEL = "gemini-3.5-flash"
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


def _should_skip_translation(text: str) -> bool:
    """Keep structured scheduling/contact inputs exact."""
    stripped = text.strip()
    if not stripped:
        return True
    if re.fullmatch(r"\d{1,2}[.)]?", stripped):
        return True
    if re.fullmatch(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", stripped, re.I):
        return True
    return False


def _normalize_target_lang(lang: str) -> str:
    normalized = (lang or "").strip().upper()
    if not normalized or normalized.startswith("EN"):
        return ""
    if normalized == "PT":
        return "PT-PT"
    if normalized == "ZH":
        return "ZH-HANS"
    return normalized


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


def _translate_to_english(text: str) -> str:
    return _gemini_call(
        prompt=f"Translate to English: {text}",
        system_instruction=(
            "You are a translator. Output ONLY the translated text. "
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
            "Keep brand names, project names, URLs, patents, and technical acronyms intact "
            "when needed. No explanations, no quotes, no notes."
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
            "project names, URLs, Markdown markers, patents, and technical acronyms intact "
            "when needed, but translate every explanatory phrase. Keep this delimiter "
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
            self._send({"status": "ok", "translation_enabled": _READY})
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

        if not text:
            self._send({"text": text, "translation_enabled": _READY})
            return

        if _should_skip_translation(text):
            self._send({"text": text, "translation_enabled": _READY})
            return

        if not _READY:
            self._send({"text": text, "translation_enabled": False})
            return

        try:
            translated = _translate_to_english(text)
            self._send({"text": translated, "translation_enabled": True})
        except Exception as exc:
            print(f"[translate] Gemini error: {exc}")
            self._send({"text": text, "translation_enabled": True})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("TRANSLATE_PORT", 5056))
    print(f"[translate] Listening on port {port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
