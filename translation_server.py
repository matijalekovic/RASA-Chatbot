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
from http.server import BaseHTTPRequestHandler, HTTPServer

try:
    from google import genai
    from google.genai import types as genai_types
    _api_key = os.environ.get("GEMINI_API_KEY", "")
    if _api_key:
        _client = genai.Client(api_key=_api_key)
        _ready = True
        print("[translate] Gemini ready.")
    else:
        print("[translate] GEMINI_API_KEY not set — translation disabled.")
        _client = None
        _ready = False
except Exception as exc:
    print(f"[translate] Gemini unavailable: {exc}")
    _client = None
    _ready = False

_MODEL = "gemini-2.5-flash-lite"

_CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
}

# Normalize "1pax" → "1PAX" so Gemini treats it as a company name, not a number.
def _normalize(text: str) -> str:
    return re.sub(r'\b1pax\b', '1PAX', text, flags=re.IGNORECASE)


_CONFIG_TO_EN = genai_types.GenerateContentConfig(
    system_instruction="You are a translator. Output ONLY the translated text. No explanations, no quotes, no notes.",
    temperature=0.1,
)

def _translate_to_english(text: str) -> str:
    response = _client.models.generate_content(
        model=_MODEL,
        contents=f"Translate to English: {text}",
        config=_CONFIG_TO_EN,
    )
    return response.text.strip()


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

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length))
        except Exception:
            self._send({"error": "invalid JSON"}, 400)
            return

        text = _normalize((data.get("text") or "").strip())

        if not text or not _ready:
            self._send({"text": text})
            return

        try:
            translated = _translate_to_english(text)
            self._send({"text": translated})
        except Exception as exc:
            print(f"[translate] Gemini error: {exc}")
            self._send({"text": text})

    def log_message(self, *args):
        pass  # suppress per-request noise


if __name__ == "__main__":
    port = int(os.environ.get("TRANSLATE_PORT", 5056))
    print(f"[translate] Listening on port {port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
