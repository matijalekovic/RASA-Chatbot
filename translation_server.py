#!/usr/bin/env python3
"""
Tiny translation proxy for the 1PAX chatbot.

POST /translate  { "text": "...", "source_lang": "FR" }
→ { "text": "... (in English)" }

Runs on port 5056.
Nginx proxies /api/translate → http://localhost:5056/translate
The UI calls this before sending messages to Rasa so that DIET always
sees English input regardless of the user's selected language.

Requires: DEEPL_API_KEY env var (same one used by the action server).
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

try:
    import deepl
    _translator = deepl.Translator(os.environ.get("DEEPL_API_KEY", ""))
    _ready = True
    print(f"[translate] DeepL ready.")
except Exception as exc:
    print(f"[translate] DeepL unavailable: {exc}")
    _translator = None
    _ready = False

_CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
}


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

        text = (data.get("text") or "").strip()

        if not text or not _ready:
            self._send({"text": text})
            return

        try:
            result = _translator.translate_text(text, target_lang="EN-US")
            self._send({"text": result.text})
        except Exception:
            # Source == target (already English) or any API error → return as-is
            self._send({"text": text})

    def log_message(self, *args):
        pass  # suppress per-request noise


if __name__ == "__main__":
    port = int(os.environ.get("TRANSLATE_PORT", 5056))
    print(f"[translate] Listening on port {port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
