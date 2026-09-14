FROM rasa/rasa:3.6.21

USER root
ENV PYTHONUNBUFFERED=1
ARG INSTALL_CALENDLY_BROWSER=true

# Install nginx + Python translation dependencies (needed by both Rasa NLU
# component and the action server, which share the same /opt/venv). Keep
# TensorFlow/Rasa's protobuf and requests versions compatible: unbounded
# Google client upgrades can otherwise install an incompatible protobuf.
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && /opt/venv/bin/pip install --no-cache-dir \
       "langdetect==1.0.9" \
       "tzdata==2026.3" \
       "playwright==1.62.0" \
       "google-api-python-client==2.198.0" \
       "google-auth==2.56.3" \
       "google-api-core==2.28.1" \
       "protobuf==4.23.3" \
       "requests==2.33.1" \
       "pydantic==1.10.9" \
    && /opt/venv/bin/pip check \
    && if [ "${INSTALL_CALENDLY_BROWSER}" = "true" ]; then \
       /opt/venv/bin/python -m playwright install --with-deps chromium; \
       fi

WORKDIR /app

# Copy project files
COPY . /app

# Models are NEVER trained on Railway or during image builds. Train locally on
# the MacBook (`rasa train --fixed-model-name production`) and commit
# models/production.tar.gz; the build only verifies the artifact is present.
RUN test -f /app/models/production.tar.gz \
    || (echo "models/production.tar.gz is missing — train locally before deploying" >&2 && exit 1)

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
