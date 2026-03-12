FROM rasa/rasa:3.6.21

USER root

WORKDIR /app

# Copy project files
COPY . /app

EXPOSE 5005

# ACTION_SERVER_URL must be set as an environment variable in Railway
# e.g. https://your-actions-service.up.railway.app/webhook
CMD ["run", "--enable-api", "--cors", "*", "--port", "5005", "--endpoints", "endpoints.yml"]
