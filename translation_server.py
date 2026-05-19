#!/usr/bin/env python3
"""
Tiny translation proxy for the 1PAX chatbot.

POST /translate  { "text": "...", "source_lang": "FR" }
→ { "text": "... (in English)" }

POST /translate  { "text": "...", "target_lang": "SR" }
→ { "text": "... (in Serbian)" }

Runs on port 5056.
Nginx proxies /api/translate → http://localhost:5056/translate
The UI calls this before sending messages to Rasa so that DIET always
sees English input regardless of the user's selected language.

Requires: GEMINI_API_KEY env var.
"""

import json
import os
import re
import socket
import time
import unicodedata
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

_GEMINI_MODEL = "gemini-2.5-flash-lite"
_GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{_GEMINI_MODEL}:generateContent"
)

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

_LANG_NAMES = {
    "FR": "French",
    "ES": "Spanish",
    "PT": "Portuguese",
    "PT-PT": "European Portuguese",
    "PT-BR": "Brazilian Portuguese",
    "ZH": "Chinese",
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


# Normalize "1pax" → "1PAX" so Gemini treats it as a company name, not a number.
def _normalize(text: str) -> str:
    return re.sub(r'\b1pax\b', '1PAX', text, flags=re.IGNORECASE)


def _ascii_lower(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return ascii_text.casefold()


def _quick_schedule_translation(text: str, source_lang: str) -> str:
    if not (source_lang or "").upper().startswith("SR"):
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


def _gemini_translate(prompt: str, system_instruction: str, timeout: float = 8.0) -> str:
    last_error = None
    for attempt in range(2):
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
            last_error = exc
            if attempt == 0:
                time.sleep(0.25)
    raise last_error or RuntimeError("translation failed")


def _translate_to_english(text: str) -> str:
    return _gemini_translate(
        f"Translate to English: {text}",
        (
            "You are a translator. Output ONLY the translated text. "
            "No explanations, no quotes, no notes."
        ),
        timeout=5.0,
    )


def _paragraph_chunks(paragraph: str, max_chars: int = 800) -> list[str]:
    """Split one Markdown paragraph into line-safe translation chunks."""
    if len(paragraph) <= max_chars:
        return [paragraph]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for line in paragraph.splitlines():
        line_len = len(line) + 1
        if current and current_len + line_len > max_chars:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(line)
        current_len += line_len
    if current:
        chunks.append("\n".join(current))
    return chunks


def _translate_from_english(text: str, target_lang: str) -> str:
    lang_name = _LANG_NAMES.get((target_lang or "").upper(), target_lang)
    system_instruction = (
        "You are a translator. Output ONLY the translated text. "
        "Preserve all Markdown formatting exactly (bold **, bullets •, hyphens -, etc.). "
        "Preserve Markdown links and URLs exactly; translate link labels only. "
        "No explanations, no quotes, no notes."
    )
    translated_paragraphs: list[str] = []
    for paragraph in text.split("\n\n"):
        translated_chunks = [
            _gemini_translate(
                f"Translate to {lang_name}: {chunk}",
                system_instruction,
                timeout=8.0,
            )
            for chunk in _paragraph_chunks(paragraph)
            if chunk
        ]
        translated_paragraphs.append("\n".join(translated_chunks))
    return "\n\n".join(translated_paragraphs)


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

        text = _normalize((data.get("text") or "").strip())
        source_lang = (data.get("source_lang") or "").strip()
        target_lang = (data.get("target_lang") or "").strip()

        if not text:
            self._send({"text": text, "translation_enabled": _READY})
            return

        if target_lang:
            if not _READY:
                self._send({"text": text, "translation_enabled": False})
                return
            try:
                translated = _translate_from_english(text, target_lang)
                self._send({
                    "text": translated,
                    "translation_enabled": True,
                    "target_lang": target_lang,
                })
            except Exception as exc:
                print(f"[translate] Gemini target error: {exc}")
                self._send({
                    "text": text,
                    "translation_enabled": True,
                    "translation_failed": True,
                    "fallback": True,
                    "error": exc.__class__.__name__,
                })
            return

        quick = _quick_schedule_translation(text, source_lang)
        if quick:
            self._send({"text": quick, "translation_enabled": _READY, "quick": True})
            return

        if not _READY:
            self._send({"text": text, "translation_enabled": False})
            return

        try:
            translated = _translate_to_english(text)
            self._send({"text": translated, "translation_enabled": True})
        except Exception as exc:
            print(f"[translate] Gemini error: {exc}")
            self._send({
                "text": text,
                "translation_enabled": True,
                "translation_failed": True,
                "fallback": True,
                "error": exc.__class__.__name__,
            })

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("TRANSLATE_PORT", 5056))
    print(f"[translate] Listening on port {port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
