FROM rasa/rasa:3.6.21

USER root

# Install nginx only — no supervisord needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . /app

# nginx config
COPY conf/nginx.conf /etc/nginx/conf.d/chatbot.conf
RUN rm -f /etc/nginx/sites-enabled/default

# Startup script
COPY conf/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080

# Override rasa/rasa's default ENTRYPOINT ["rasa"]
ENTRYPOINT []
CMD ["/start.sh"]
