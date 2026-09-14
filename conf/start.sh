#!/bin/bash
set -euo pipefail

PORT=${PORT:-8080}
RASA=/opt/venv/bin/rasa
PYTHON=/opt/venv/bin/python
RASA_MODEL_LAUNCHER=/app/conf/rasa_legacy_optimizer.py
RASA_PORT=${RASA_PORT:-5005}
ACTION_PORT=${ACTION_PORT:-5055}
TRANSLATE_PORT=${TRANSLATE_PORT:-5056}
BOOT_TIMEOUT_SECONDS=${BOOT_TIMEOUT_SECONDS:-300}
RUN_LOCAL_ACTIONS=${RUN_LOCAL_ACTIONS:-true}
WAIT_FOR_ACTIONS=${WAIT_FOR_ACTIONS:-true}
ACTION_ENDPOINT_URL=${ACTION_ENDPOINT_URL:-http://127.0.0.1:${ACTION_PORT}/webhook}
ACTION_HEALTH_URL=${ACTION_HEALTH_URL:-${ACTION_ENDPOINT_URL%/webhook}/health}
MODEL_DIR=/app/models
RUNTIME_ENDPOINTS=/tmp/endpoints.runtime.yml
SERVICE_PIDS=()

is_true() {
  case "$(echo "${1}" | tr '[:upper:]' '[:lower:]')" in
    1|true|yes|y|on) return 0 ;;
    *) return 1 ;;
  esac
}

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

  if [[ -f "${MODEL_DIR}/production.tar.gz" ]]; then
    echo "${MODEL_DIR}/production.tar.gz"
    return
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
probe_text = "What innovations has 1PAX developed?"
expected_intent = "ask_company_innovation"
minimum_confidence = 0.70
req = urllib.request.Request(
    f"http://127.0.0.1:{port}/model/parse",
    data=json.dumps({"text": probe_text}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=30) as response:
    payload = json.load(response)

intent = payload.get("intent") or {}
intent_name = intent.get("name")
confidence = float(intent.get("confidence") or 0.0)
if intent_name != expected_intent or confidence < minimum_confidence:
    print(
        "[start] ERROR: Model readiness probe failed: "
        f"expected {expected_intent!r} >= {minimum_confidence:.2f}, "
        f"got {intent_name!r} at {confidence:.4f}.",
        file=sys.stderr,
    )
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)

print(
    "[start] Model readiness probe passed: "
    f"{intent_name} at {confidence:.4f}."
)
PY
}

write_runtime_endpoints() {
  "${PYTHON}" - "${ACTION_ENDPOINT_URL}" "${RUNTIME_ENDPOINTS}" <<'PY'
import sys
from pathlib import Path

import yaml

action_endpoint_url = sys.argv[1]
output_path = Path(sys.argv[2])
source_path = Path("/app/endpoints.yml")

data = yaml.safe_load(source_path.read_text()) or {}
data.setdefault("action_endpoint", {})["url"] = action_endpoint_url
output_path.write_text(yaml.safe_dump(data, sort_keys=False))

print(f"[start] Action endpoint: {action_endpoint_url}")
print(f"[start] Runtime endpoints file: {output_path}")
PY
}

MODEL_PATH="$(pick_model)"
MODEL_FILE="$(basename "${MODEL_PATH}")"

echo "[start] Rasa binary: ${RASA}"
echo "[start] Rasa model launcher: ${RASA_MODEL_LAUNCHER}"
echo "[start] Model files:"
ls -1 "${MODEL_DIR}" 2>&1
echo "[start] Selected model: ${MODEL_FILE}"

echo "[start] Injecting port ${PORT} into nginx config..."
if grep -q "NGINX_PORT" /etc/nginx/conf.d/chatbot.conf; then
  sed -i "s/NGINX_PORT/${PORT}/g" /etc/nginx/conf.d/chatbot.conf
fi

cleanup() {
  local pid
  trap - EXIT INT TERM
  for pid in "${SERVICE_PIDS[@]}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT INT TERM

echo "[start] Starting translation proxy server on port ${TRANSLATE_PORT}..."
PYTHONUNBUFFERED=1 "${PYTHON}" -u /app/translation_server.py 2>&1 | sed 's/^/[translate] /' &
SERVICE_PIDS+=("$!")

if is_true "${RUN_LOCAL_ACTIONS}"; then
  echo "[start] Starting local action server on port ${ACTION_PORT}..."
  PYTHONUNBUFFERED=1 "${RASA}" run actions --port "${ACTION_PORT}" 2>&1 | sed 's/^/[actions] /' &
  SERVICE_PIDS+=("$!")
else
  echo "[start] RUN_LOCAL_ACTIONS=false; using external action server."
fi

write_runtime_endpoints

echo "[start] Starting Rasa API server on port ${RASA_PORT}..."
PYTHONUNBUFFERED=1 "${PYTHON}" "${RASA_MODEL_LAUNCHER}" run \
  --enable-api \
  --cors "*" \
  --port "${RASA_PORT}" \
  --model "${MODEL_PATH}" \
  --endpoints "${RUNTIME_ENDPOINTS}" 2>&1 | sed 's/^/[rasa] /' &
SERVICE_PIDS+=("$!")

wait_for_http "translation proxy" "http://127.0.0.1:${TRANSLATE_PORT}/health" "${BOOT_TIMEOUT_SECONDS}"
if is_true "${WAIT_FOR_ACTIONS}"; then
  wait_for_http "action server" "${ACTION_HEALTH_URL}" "${BOOT_TIMEOUT_SECONDS}"
fi
wait_for_http "rasa API" "http://127.0.0.1:${RASA_PORT}/status" "${BOOT_TIMEOUT_SECONDS}"

warm_up_rasa

echo "[start] Backends are warm. Starting nginx on port ${PORT}..."
nginx -t
nginx -g "daemon off;" &
SERVICE_PIDS+=("$!")

echo "[start] Monitoring ${#SERVICE_PIDS[@]} managed services."
set +e
wait -n "${SERVICE_PIDS[@]}"
service_status=$?
set -e

echo "[start] ERROR: A managed service exited (status ${service_status}); restarting container." >&2
exit 1
