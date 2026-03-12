#!/bin/bash
# Inject Railway's $PORT into nginx config (default 8080)
PORT=${PORT:-8080}
sed -i "s/NGINX_PORT/$PORT/" /etc/nginx/conf.d/chatbot.conf

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
