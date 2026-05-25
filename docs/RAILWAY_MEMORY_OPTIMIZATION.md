# Railway memory optimization

This deployment can run in two modes:

- **Single service**: the default. One container runs nginx, the translation
  proxy, the Rasa API, and a local action server.
- **Split actions**: the main service runs nginx, the translation proxy, and
  the Rasa API. A second Railway service runs the action server from
  `conf/Dockerfile.actions`.

## Runtime memory controls

Both Docker images set conservative runtime memory/thread controls:

```bash
MALLOC_ARENA_MAX=2
OMP_NUM_THREADS=1
TF_NUM_INTRAOP_THREADS=1
TF_NUM_INTEROP_THREADS=1
```

The main Dockerfile sets these after model training so build-time training can
still use normal TensorFlow parallelism.

## Split action service

Create a second Railway service from the same repo and configure it to build
with:

```text
conf/Dockerfile.actions
```

The action service exposes port `5055` and starts:

```bash
python -m rasa_sdk --actions actions --port 5055
```

On the main Rasa service, set:

```bash
RUN_LOCAL_ACTIONS=false
ACTION_ENDPOINT_URL=http://<action-service-internal-host>:5055/webhook
ACTION_HEALTH_URL=http://<action-service-internal-host>:5055/health
```

Keep `RUN_LOCAL_ACTIONS=true` or unset for the current single-container setup.

## Translation component

The Rasa NLU pipeline no longer includes
`components.translation_component.TranslationComponent`.

The production UI already translates non-English input through `/api/translate`
and sends the selected language as request metadata, which the action server
uses for translated responses. Direct REST calls to `/webhooks/rest/webhook`
should send English text, or include translated text plus `metadata.lang`.
