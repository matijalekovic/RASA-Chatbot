#!/bin/bash
PORT=${PORT:-8080}

echo "[start] Injecting port $PORT into nginx config..."
sed -i "s/NGINX_PORT/$PORT/g" /etc/nginx/conf.d/chatbot.conf

echo "[start] Starting action server..."
rasa run actions --port 5055 2>&1 | sed 's/^/[actions] /' &

echo "[start] Starting Rasa API server..."
rasa run --enable-api --cors "*" --port 5005 --endpoints /app/endpoints.yml 2>&1 | sed 's/^/[rasa] /' &

echo "[start] Testing nginx config..."
nginx -t

echo "[start] Starting nginx on port $PORT..."
exec nginx -g "daemon off;"
