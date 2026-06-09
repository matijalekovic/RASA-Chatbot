FROM rasa/rasa:3.6.21

USER root
ENV PYTHONUNBUFFERED=1
ARG INSTALL_CALENDLY_BROWSER=true

# Install nginx + Python translation dependencies (needed by both Rasa NLU
# component and the action server, which share the same /opt/venv)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && /opt/venv/bin/pip install --no-cache-dir \
       "langdetect>=1.0.9" \
       "tzdata>=2025.2" \
       "playwright>=1.44,<2.0" \
       "google-api-python-client>=2.120,<3.0" \
       "google-auth>=2.29,<3.0" \
    && if [ "${INSTALL_CALENDLY_BROWSER}" = "true" ]; then \
       /opt/venv/bin/python -m playwright install --with-deps chromium; \
       fi

WORKDIR /app

# Copy project files
COPY . /app

# Railway deploys the locally trained artifact by default. Set this to true
# only for an intentional image-build retrain.
ARG TRAIN_RASA_MODEL=false
RUN if [ "${TRAIN_RASA_MODEL}" = "true" ]; then \
      rm -f /app/models/*.tar.gz && \
      /opt/venv/bin/rasa train --out /app/models --fixed-model-name production; \
    else \
      test -f /app/models/production.tar.gz; \
    fi

# Runtime memory controls. Keep these after training so image builds can still
# use normal TensorFlow parallelism while the live service keeps bounded RSS
# without forcing every live inference path onto a single worker thread.
ENV MALLOC_ARENA_MAX=2 \
    OMP_NUM_THREADS=2 \
    TF_NUM_INTRAOP_THREADS=2 \
    TF_NUM_INTEROP_THREADS=2

# nginx config — run workers as root, remove default site, fix permissions
COPY conf/nginx.conf /etc/nginx/conf.d/chatbot.conf
RUN rm -f /etc/nginx/sites-enabled/default \
    && sed -i 's/user www-data;/user root;/' /etc/nginx/nginx.conf \
    && chmod -R 755 /app

# Startup script
COPY conf/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080

# Override rasa/rasa's default ENTRYPOINT ["rasa"]
ENTRYPOINT []
CMD ["/start.sh"]
