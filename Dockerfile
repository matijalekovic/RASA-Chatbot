FROM rasa/rasa:3.6.21

USER root

# Install nginx and supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . /app

# nginx config
COPY conf/nginx.conf /etc/nginx/conf.d/chatbot.conf
RUN rm -f /etc/nginx/sites-enabled/default

# supervisor config + startup script
COPY conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY conf/start.sh /start.sh
RUN chmod +x /start.sh

# endpoints.yml uses localhost (action server is in the same container)
ENV ACTION_SERVER_URL=http://localhost:5055/webhook

EXPOSE 8080

CMD ["/start.sh"]
