#!/bin/sh
# Inject RASA_API_URL env var into the HTML at container startup
envsubst '${RASA_API_URL}' < /usr/share/nginx/html/index.html.template \
  > /usr/share/nginx/html/index.html

exec nginx -g 'daemon off;'
