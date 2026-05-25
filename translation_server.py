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


def _translate_to_english(text: str) -> str:
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
        f"{_GEMINI_URL}?key={_API_KEY}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10.0) as resp:
        result = json.loads(resp.read())
    return result["candidates"][0]["content"]["parts"][0]["text"].strip()


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

        if not text:
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
