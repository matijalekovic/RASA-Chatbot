# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

1PAX (architectural firm) company chatbot. Rasa Open Source 3.6.21, Python 3.10, English-only NLU with a runtime translation layer so non-English users can still interact. The bot covers four content modules (projects, company, services, team) plus a conversational meeting scheduler.

## Training Discipline (CRITICAL)

- **Train ONLY locally on the MacBook — never on Railway or in a Docker build.** The Dockerfile has no training step; it only verifies `models/production.tar.gz` exists. Train with `rasa train --fixed-model-name production` and commit the artifact. The checkpoint is trained on Apple Silicon (Keras legacy Adam), which is why `conf/start.sh` launches Rasa through `conf/rasa_legacy_optimizer.py` on Linux — keep that shim.
- **Batch ALL NLU fixes before retraining.** Training takes 5+ minutes and saturates CPU/GPU. Never train after a single fix — accumulate every NLU example change, synonym addition, and action-code change into one batch, then train once.
- Before any retrain, run `tests/check_nlu_duplicates.py` (cross-intent duplicates, leading-article annotations), all `tests/*_unit.py`, and `rasa data validate`.
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

1. **`translation_server.py`** — HTTP proxy on port 5056. The UI POSTs user input here before sending to Rasa; nginx proxies `/api/translate` to it. Uses `gemini-3.1-flash-lite`.
2. **`components/translation_component.py`** — custom Rasa NLU GraphComponent, registered first in `config.yml`'s pipeline. Fallback path for direct API hits: detects language with `langdetect`, translates non-English input to English via Gemini, stashes the detected language as a `__lang__` entity on the message.
3. **`actions/translation.py`** — `get_lang(tracker)` reads the detected language, `translate_response(text, lang)` translates outgoing bot text. Every action must call these and persist `SlotSet("language", lang)`.

Requires `GEMINI_API_KEY` in env. Without it, the bot is English-only but still runs.

### Fallback routing

`ActionHandleOutOfScope` (`actions.py`) handles `out_of_scope` and `nlu_fallback`, but it is more than a canned reply. In order, it:
1. Hands off to the scheduler if a booking flow is active, so short replies like names, emails, "yes", or "2" keep the booking going.
2. Runs keyword safety nets that send misclassified greetings, company or location questions, and project/team questions to the right action.
3. Only then falls back to nudging the user toward the portfolio.

Most production misroutes get fixed here or in NLU data, so check both.

### Meeting scheduling

- **Entry point:** `action_schedule_meeting` (`calendly_actions.py`). Rules in `data/rules.yml` send all `*_schedule_*` intents to it.
- **State:** the flow is a state machine driven by the `schedule_stage` slot plus about 20 other `schedule_*` slots in `domain.yml`.
- **Providers:** `run_calendly_scheduling()` checks `SCHEDULING_PROVIDER` (or `MEETING_SCHEDULING_PROVIDER`):
  - **`google` (default):** `run_google_calendar_scheduling()` uses `google_calendar_scheduler.py`. It picks an office/colleague from language, region, and timezone hints, reads free/busy, and books the event directly. The per-office calendars come from `GOOGLE_CALENDAR_<OFFICE>_CALENDAR_ID` / `_LABEL` or `GOOGLE_CALENDAR_ROSTER_JSON`. Set `GOOGLE_CALENDAR_DRY_RUN=true` to get fake slots and bookings without auth. See `docs/GOOGLE_CALENDAR_SCHEDULING.md`.
  - **`calendly`:** reads availability through the API, then sends the UI a `redirect_url` custom payload pointing at the pre-filled hosted Calendly page, where the user confirms. `calendly_browser.py` is the fallback for scraping availability. See `docs/CALENDLY_INTEGRATION.md`.
- **Topic changes:** content actions call `_schedule_topic_shift_events()` so the scheduling slots reset when the user changes topic mid-flow.
- **Shared text:** meeting call-to-action text and buttons live in `meeting_prompts.py`.

### Portfolio insights (ranking, filtering, grouping, stats)

`actions/portfolio_insights.py` parses project fields into numbers (`FACTS`: area m², budget in € with USD converted approximately, annual passengers, start/end year, status class, procurement class, work type) and answers "biggest/smallest/most expensive/newest/first project", "which are built / under construction / competitions", "group by budget/size/year/status", "how many projects/countries", awards/prizes, and flagship highlights. Geography stays in the existing geo code in `actions.py`.

- Intents `ask_projects_ranking` / `ask_projects_filter` → `action_list_projects`, but routing is **text-based**: `_portfolio_request(tracker)` in `actions.py` is checked first in `ActionListProjects`, `ActionAnswerProjectQuery`, `ActionAnswerCompanyQuery`, and `ActionHandleOutOfScope`, so NLU misclassification between list/category/area/cost intents is harmless.
- Short follow-ups ("and the smallest?", "what about by budget?") inherit the previous ranking via `tracker.events`.
- Size rankings deliberately separate **built / under construction** from **competition and study** designs, and exclude non-footprint areas (wayfinding coverage, façades, reviews) via `_AREA_OVERRIDES`. When adding projects, check they classify correctly (`tests/test_company_inquiries_unit.py`).
- Superlatives must never be project synonyms (the old "biggest/flagship project" → `sofia_airport` synonym was removed).

### Company due-diligence inquiries + Graduate Fellowship

`actions/company_inquiries.py` answers what a prospective client/contractor asks: `languages`, `local_presence` (no office in my country?), `engineering` (1PAX does architecture, engineering is by partner firms), `partners` (derived from project `architect`/`partners` fields; "have you worked with Arup?"), `beyond_airports` (building-type experience, honest "not in portfolio" answers), `project_size`, `engagement`, `project_stages`, `certifications`, `track_record`, `awards`. Each has an `ask_company_<type>` intent; `ActionAnswerCompanyQuery` also infers the type from raw text (`infer_inquiry_type`) before the static `COMPANY_INFO` dispatch.

`actions/fellowship_data.py` holds the Graduate Fellowship facts and a topic router (eligibility, dates, pay, format, research, jury, selection, apply, visa…). Source of truth is the live portal code in `~/Documents/Internships/internship-portal` (`TalentPortal.tsx`, `fellowship-faq.ts`, `application-deadline.mjs`) — older PDFs/DOCX in Downloads are superseded. Deadline answers are date-aware (`DEADLINE_UTC`); update the dates for each new cohort.

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

# Unit tests: no servers or trained model needed; each file is runnable directly
.venv/bin/python3 tests/test_project_resolution_unit.py
.venv/bin/python3 tests/test_google_calendar_scheduling_unit.py
.venv/bin/python3 tests/test_calendly_actions_unit.py
.venv/bin/python3 tests/test_translation_unit.py
.venv/bin/python3 tests/test_company_inquiries_unit.py      # portfolio rankings, inquiries, fellowship
.venv/bin/python3 tests/check_nlu_duplicates.py             # NLU gate before training

# Local retrain (MacBook only — never on Railway)
.venv/bin/python3 -m rasa data validate
.venv/bin/python3 -m rasa train --fixed-model-name production

# Scheduling flow without Google auth
SCHEDULING_PROVIDER=google GOOGLE_CALENDAR_DRY_RUN=true ./start.sh

# Live test suites (both servers must be running; RASA_URL overrides localhost:5005)
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

- **Railway:** deploys this `Dockerfile` (`railway.json`). The build **does not train**; it ships the locally trained `models/production.tar.gz`, the only model file git tracks (see `.gitignore` / `.dockerignore`). At runtime `conf/start.sh` uses `RASA_MODEL` if set, otherwise `production.tar.gz`.
- **Split mode:** runs the action server as a separate service from `conf/Dockerfile.actions`. Set `RUN_LOCAL_ACTIONS=false` and `ACTION_ENDPOINT_URL` on the main service. See `docs/RAILWAY_MEMORY_OPTIMIZATION.md`.
- **UI:** `ui/index.html` is served locally and in the main image. `ui/index.html.template` is the standalone-UI variant (`conf/Dockerfile.ui`), where `envsubst` fills in `${RASA_API_URL}`. The two files have drifted apart, so check both when changing UI behaviour.
- **`.env`:** `./start.sh` loads `.env` if it exists.
