#!/bin/bash
PORT=${PORT:-8080}
RASA=/opt/venv/bin/rasa

echo "[start] Rasa binary: $RASA"
echo "[start] Model files:"
ls /app/models/ 2>&1

echo "[start] Injecting port $PORT into nginx config..."
sed -i "s/NGINX_PORT/$PORT/g" /etc/nginx/conf.d/chatbot.conf

echo "[start] Starting translation proxy server on port 5056..."
/opt/venv/bin/python /app/translation_server.py 2>&1 | sed 's/^/[translate] /' &

echo "[start] Starting action server (lightweight — rasa_sdk only, no TensorFlow)..."
/opt/venv/bin/python -m rasa_sdk --actions actions --port 5055 2>&1 | sed 's/^/[actions] /' &

echo "[start] Starting Rasa API server (model load takes ~60s on this hardware)..."
$RASA run --enable-api --cors "*" --port 5005 --endpoints /app/endpoints.yml 2>&1 | sed 's/^/[rasa] /' &

echo "[start] Starting nginx on port $PORT (UI available immediately, bot ready when model loads)..."
nginx -t
exec nginx -g "daemon off;"
