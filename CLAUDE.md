# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

1PAX (architectural firm) company chatbot. Rasa Open Source 3.6.21, Python 3.10, English-only NLU with a runtime translation layer so non-English users can still interact. The bot covers four content modules: projects, company, services, team.

## Training Discipline (CRITICAL)

- **Batch ALL NLU fixes before retraining.** Training takes 5+ minutes and saturates CPU/GPU. Never train after a single fix — accumulate every NLU example change, synonym addition, and action-code change into one batch, then train once.
- Before any retrain, check for cross-intent duplicate examples in `data/nlu.yml`.
- Probe the live bot via REST API (`curl` to `localhost:5005`) like a real user before running full test suites. Intuitive probing finds bugs the suites miss.
- Run `tests/test_stories.py` / `tests/test_extended.py` only after a retrain, to verify overall state.

## NLU Annotation Rules

- **NEVER annotate `[the X](entity)`** — always `[X](entity)` with no leading article. DIET will learn to extract "the" as a spurious entity and that breaks resolution across every intent.
- Synonyms in `nlu.yml` must match the **exact** surface form DIET extracts (after lowercasing). Before adding a synonym, verify extraction with `/model/parse`.

## Architecture

### Module pattern (same shape for all four modules)

Each content module is two files:
- `actions/<module>_data.py` — one dict of canonical-key → field dict. Keys are internal IDs (`sofia_airport`, `mabel_miranda`), never shown to users. Every entry has the same field schema; missing fields hold `"Not available."` so formatting never KeyErrors.
- `actions/<module>_actions.py` — one `ActionAnswer<Module>Query` router. It resolves the entity, reads the intent name, and dispatches to a per-field formatter via an `*_DISPATCH` dict.

Modules:
- **Projects** (`actions/actions.py`, `projects_data.py`) — slot-based. `project_name` slot carries conversation context so follow-ups like "and the budget?" resolve.
- **Company** (`company_actions.py`, `company_data.py`) — stateless.
- **Services** (`services_actions.py`, `services_data.py`) — stateless.
- **Team** (`team_actions.py`, `team_data.py`) — uses `person` entity + `person_name` slot.

Design principles for adding/modifying modules are in `docs/CHATBOT_MODULE_PRINCIPLES.md` — read it before building a new module.

### Entity resolution (projects + team)

Rasa auto-fills slots from extracted entities **before** the action runs. If DIET extracts a generic word ("depot", "tower", "terminal") the slot gets clobbered with a non-canonical value. Two defenses, both already in place:

1. `_resolve_project()` / `_handle_person_query()` try **all** extracted entity values, not just the first, and filter generic words via `_GENERIC_PROJECT_REF`.
2. On no match, scan `tracker.events` for the last valid slot value (recovers context the auto-fill overwrote).

When editing these resolvers, preserve both behaviours.

Primary resolution is via `EntitySynonymMapper` (mapping `T3` → `sofia_airport`, `CEO` → `mabel_miranda`, etc.) configured in `nlu.yml`. Fuzzy matching in the action is a fallback only. `_ascii_norm()` in `actions.py` handles accented phrases like "Pointe-à-Pitre".

### Translation layer (three pieces)

User-facing multilingual support, even though all training data and intent logic are English-only:

1. **`translation_server.py`** — HTTP proxy on port 5056. The UI POSTs user input here before sending to Rasa; nginx proxies `/api/translate` to it. Uses Gemini 3.5 Flash.
2. **`components/translation_component.py`** — custom Rasa NLU GraphComponent, registered first in `config.yml`'s pipeline. Fallback path for direct API hits: detects language with `langdetect`, translates non-English input to English via Gemini, stashes the detected language as a `__lang__` entity on the message.
3. **`actions/translation.py`** — `get_lang(tracker)` reads the detected language, `translate_response(text, lang)` translates outgoing bot text. Every action must call these and persist `SlotSet("language", lang)`.

Requires `GEMINI_API_KEY` in env. Without it, the bot is English-only but still runs.

### Serbian

Serbian responses are force-translated to Latin script (not Cyrillic) — see commit `8905058`. Croatian and Bosnian are mapped to `SR` in `_LANG_MAP` because `langdetect` often confuses them with Serbian Latin.

## Commands

```bash
# Full local stack (action server + Rasa API + translation proxy + UI on :8080)
./start.sh

# Individual servers (use when debugging one piece)
.venv/bin/python3 -m rasa run actions --port 5055
.venv/bin/python3 -m rasa run --enable-api --cors "*" -m models/<latest>.tar.gz
.venv/bin/python3 translation_server.py   # port 5056, needs GEMINI_API_KEY

# Retrain (batch all fixes first — see Training Discipline above)
.venv/bin/python3 -m rasa train

# Test suites (both servers must be running)
.venv/bin/python3 tests/test_stories.py     # 20 personas × ~10 questions
.venv/bin/python3 tests/test_extended.py
.venv/bin/python3 tests/test_blast.py       # 61-test automated harness

# Live probe
curl -s -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender":"test","message":"YOUR QUESTION HERE"}'

# Intent / entity parse (verify synonyms before adding them)
curl -s -X POST http://localhost:5005/model/parse \
  -H "Content-Type: application/json" \
  -d '{"text":"YOUR QUESTION HERE"}'
```

## Deployment

`Dockerfile` builds on top of `rasa/rasa:3.6.21` and adds nginx + `google-genai` + `langdetect` into the Rasa venv. `conf/start.sh` + `conf/supervisord.conf` run the action server, Rasa API, translation proxy, and nginx together; nginx serves the UI and proxies `/api/translate` to port 5056. Container exposes 8080.
