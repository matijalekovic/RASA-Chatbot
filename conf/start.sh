#!/bin/bash
PORT=${PORT:-8080}
RASA=/opt/venv/bin/rasa

echo "[start] Rasa binary: $RASA"
echo "[start] Rasa version: $($RASA --version 2>&1 | head -1)"
echo "[start] Model files:"
ls /app/models/ 2>&1

echo "[start] Injecting port $PORT into nginx config..."
sed -i "s/NGINX_PORT/$PORT/g" /etc/nginx/conf.d/chatbot.conf

echo "[start] Starting action server..."
$RASA run actions --port 5055 2>&1 | sed 's/^/[actions] /' &

echo "[start] Waiting 5s for action server..."
sleep 5

echo "[start] Starting Rasa API server..."
$RASA run --enable-api --cors "*" --port 5005 --endpoints /app/endpoints.yml 2>&1 | sed 's/^/[rasa] /' &

echo "[start] Waiting 30s for Rasa to load model..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:5005/status > /dev/null 2>&1; then
        echo "[start] Rasa is up after ${i}s"
        break
    fi
    echo "[start] waiting... ${i}s"
    sleep 1
done

echo "[start] Testing nginx config..."
nginx -t

echo "[start] Starting nginx on port $PORT..."
exec nginx -g "daemon off;"
