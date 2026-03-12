# Claude Code – 1PAX Chatbot Project Rules

## Training Discipline (CRITICAL)
- **Batch ALL NLU fixes before retraining.** Training is computationally expensive — it takes 5+ minutes and hammers the CPU/GPU. Never train after a single fix. Accumulate ALL identified fixes (NLU examples, synonym additions, action code changes) into one batch, then train once.
- Before any retrain, run the conflict-check script to ensure no cross-intent duplicates.
- Test intuitively by probing the live bot via REST API (curl to localhost:5005) — talk to it naturally as a real user would, not just by running prewritten test suites. This surfaces bugs the test suite won't catch.
- Only run the full test suites (test_stories.py, test_extended.py) after a retrain to verify overall state.

## NLU Annotation Rules
- NEVER annotate `[the X](entity)` — always annotate `[X](entity)` without leading articles. Annotating "the" causes DIET to extract "the" as a spurious entity, which breaks entity resolution across all intents.
- Synonyms must match the EXACT text DIET will extract (after lowercasing). Test entity extraction with `/model/parse` before adding synonyms.

## Code Quality
- `_resolve_project()` and `_resolve_person()` in actions must try ALL extracted entity values (not just the first) to be robust against spurious short-token extractions.

## How to Run
```bash
# Action server (port 5055)
cd /Users/macbookpro/documents/rasa-chatbot && .venv/bin/python3 -m rasa run actions --port 5055

# Rasa API (port 5005)
cd /Users/macbookpro/documents/rasa-chatbot && .venv/bin/python3 -m rasa run --enable-api --cors "*" -m models/<latest>.tar.gz

# Train
cd /Users/macbookpro/documents/rasa-chatbot && .venv/bin/python3 -m rasa train

# Quick probe
curl -s -X POST http://localhost:5005/webhooks/rest/webhook -H "Content-Type: application/json" -d '{"sender":"test","message":"YOUR QUESTION HERE"}'

# Intent parse
curl -s -X POST http://localhost:5005/model/parse -H "Content-Type: application/json" -d '{"text":"YOUR QUESTION HERE"}'
```
