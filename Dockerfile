FROM rasa/rasa:3.6.21

USER root
ENV PYTHONUNBUFFERED=1
ARG INSTALL_CALENDLY_BROWSER=true

# Install nginx + Python translation dependencies (needed by both Rasa NLU
# component and the action server, which share the same /opt/venv)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    && rm -rf /var/lib/apt/lists/* \
    && /opt/venv/bin/pip install --no-cache-dir \
       "langdetect>=1.0.9" \
       "tzdata>=2025.2" \
       "playwright>=1.44,<2.0" \
    && if [ "${INSTALL_CALENDLY_BROWSER}" = "true" ]; then \
       /opt/venv/bin/python -m playwright install --with-deps chromium; \
       fi

WORKDIR /app

# Copy project files
COPY . /app

# Re-train inside the Linux build environment so runtime model weights match
# Railway's TensorFlow stack (fixes cross-platform checkpoint mismatch).
RUN rm -f /app/models/*.tar.gz \
    && /opt/venv/bin/rasa train \
         --config /app/config.yml \
         --domain /app/domain.yml \
         --data /app/data \
         --out /app/models

# Runtime memory controls. Keep these after training so image builds can still
# use normal TensorFlow parallelism while the live service keeps a smaller RSS.
ENV MALLOC_ARENA_MAX=2 \
    OMP_NUM_THREADS=1 \
    TF_NUM_INTRAOP_THREADS=1 \
    TF_NUM_INTEROP_THREADS=1

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
