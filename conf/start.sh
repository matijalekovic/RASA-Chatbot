#!/bin/bash
set -euo pipefail

PORT=${PORT:-8080}
RASA=/opt/venv/bin/rasa
PYTHON=/opt/venv/bin/python
RASA_PORT=${RASA_PORT:-5005}
ACTION_PORT=${ACTION_PORT:-5055}
TRANSLATE_PORT=${TRANSLATE_PORT:-5056}
MCP_PORT=${MCP_PORT:-5057}
BOOT_TIMEOUT_SECONDS=${BOOT_TIMEOUT_SECONDS:-300}
MODEL_DIR=/app/models

pick_model() {
  if [[ -n "${RASA_MODEL:-}" ]]; then
    if [[ -f "${RASA_MODEL}" ]]; then
      echo "${RASA_MODEL}"
      return
    fi
    if [[ -f "${MODEL_DIR}/${RASA_MODEL}" ]]; then
      echo "${MODEL_DIR}/${RASA_MODEL}"
      return
    fi
    echo "[start] ERROR: RASA_MODEL '${RASA_MODEL}' does not exist." >&2
    exit 1
  fi

  local latest
  latest="$(ls -1 "${MODEL_DIR}"/*.tar.gz 2>/dev/null | sort | tail -n 1 || true)"
  if [[ -z "${latest}" ]]; then
    echo "[start] ERROR: No model files found in ${MODEL_DIR}" >&2
    exit 1
  fi
  echo "${latest}"
}

wait_for_http() {
  local name="$1"
  local url="$2"
  local timeout="${3}"
  "${PYTHON}" - "${name}" "${url}" "${timeout}" <<'PY'
import sys
import time
import urllib.error
import urllib.request

name = sys.argv[1]
url = sys.argv[2]
timeout = int(sys.argv[3])
deadline = time.time() + timeout
last_error = "no response"

while time.time() < deadline:
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            if 200 <= resp.status < 500:
                print(f"[start] {name} is ready: {url}")
                sys.exit(0)
            last_error = f"HTTP {resp.status}"
    except Exception as exc:
        last_error = str(exc)
    time.sleep(2)

print(
    f"[start] ERROR: {name} did not become ready within {timeout}s ({last_error})",
    file=sys.stderr,
)
sys.exit(1)
PY
}

warm_up_rasa() {
  "${PYTHON}" - "${RASA_PORT}" <<'PY'
import json
import sys
import urllib.request

port = int(sys.argv[1])
req = urllib.request.Request(
    f"http://127.0.0.1:{port}/model/parse",
    data=json.dumps({"text": "hello"}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=10):
    pass
print("[start] Warm-up parse completed.")
PY
}

MODEL_PATH="$(pick_model)"
MODEL_FILE="$(basename "${MODEL_PATH}")"

echo "[start] Rasa binary: ${RASA}"
echo "[start] Model files:"
ls -1 "${MODEL_DIR}" 2>&1
echo "[start] Selected model: ${MODEL_FILE}"

echo "[start] Injecting port ${PORT} into nginx config..."
if grep -q "NGINX_PORT" /etc/nginx/conf.d/chatbot.conf; then
  sed -i "s/NGINX_PORT/${PORT}/g" /etc/nginx/conf.d/chatbot.conf
fi

cleanup() {
  kill 0 >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

echo "[start] Starting translation proxy server on port ${TRANSLATE_PORT}..."
PYTHONUNBUFFERED=1 "${PYTHON}" -u /app/translation_server.py 2>&1 | sed 's/^/[translate] /' &

echo "[start] Starting MCP QA server on port ${MCP_PORT}..."
PYTHONUNBUFFERED=1 MCP_TRANSPORT=http MCP_HOST=127.0.0.1 MCP_PORT="${MCP_PORT}" \
  "${PYTHON}" -u /app/mcp_server.py 2>&1 | sed 's/^/[mcp] /' &

echo "[start] Starting action server on port ${ACTION_PORT}..."
PYTHONUNBUFFERED=1 "${RASA}" run actions --port "${ACTION_PORT}" 2>&1 | sed 's/^/[actions] /' &

echo "[start] Starting Rasa API server on port ${RASA_PORT}..."
PYTHONUNBUFFERED=1 "${RASA}" run \
  --enable-api \
  --cors "*" \
  --port "${RASA_PORT}" \
  --model "${MODEL_PATH}" \
  --endpoints /app/endpoints.yml 2>&1 | sed 's/^/[rasa] /' &

wait_for_http "translation proxy" "http://127.0.0.1:${TRANSLATE_PORT}/health" "${BOOT_TIMEOUT_SECONDS}"
wait_for_http "MCP QA server" "http://127.0.0.1:${MCP_PORT}/health" "${BOOT_TIMEOUT_SECONDS}"
wait_for_http "action server" "http://127.0.0.1:${ACTION_PORT}/health" "${BOOT_TIMEOUT_SECONDS}"
wait_for_http "rasa API" "http://127.0.0.1:${RASA_PORT}/status" "${BOOT_TIMEOUT_SECONDS}"

if ! warm_up_rasa; then
  echo "[start] WARN: Warm-up parse failed; continuing."
fi

echo "[start] Backends are warm. Starting nginx on port ${PORT}..."
nginx -t
exec nginx -g "daemon off;"
