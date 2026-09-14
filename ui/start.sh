#!/bin/sh
# Inject RASA_API_URL env var into the HTML at container startup
: "${RASA_API_URL:?RASA_API_URL must be the public 1PAX backend base URL}"
envsubst '${RASA_API_URL}' < /usr/share/nginx/html/index.html.template \
  > /usr/share/nginx/html/index.html

exec nginx -g 'daemon off;'
