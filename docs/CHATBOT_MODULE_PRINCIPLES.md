# Chatbot Module Architecture — Principles & Approach

This document captures the design principles used to build the **1PAX Projects module** of the company chatbot. These principles are technology-agnostic and apply equally to any information module — company info, team profiles, career prospects, news, services, etc.

Share this with any agent tasked with building a new module so the architecture stays consistent.

---

## 1. Data Structure

### One file, one registry
All data for a module lives in a single dedicated Python file (e.g., `projects_data.py`, `team_data.py`). It exports one dict: `ENTITIES = { "canonical_key": { ...fields... } }`. Never scatter data across multiple files.

### Canonical key convention
Keys are lowercase, underscore-separated, unique, and stable (e.g., `sofia_airport`, `jean_dupont`, `senior_architect`). They are never shown to users — only used internally for slot tracking and routing.

### Rich, consistent field schema
Every entity in the module must have the same set of fields. If a field doesn't apply, set it to `"Not available."` rather than omitting it. This prevents KeyErrors and keeps response formatting uniform.

**Recommended base fields for any entity:**
- `display_name` — the human-readable label shown in responses (bold, every time)
- `category` — grouping label for list views
- `tagline` — one-liner summary (for concept/intro responses)
- `overview` — 2–4 sentence paragraph (for the teaser and full overview)
- `key_challenge` — what was difficult, what was navigated
- `approach` — how the problem was solved, the methodology
- `fun_facts` — 3 bullet highlights (the most memorable/impressive things)
- `status` — current state (active, completed, ongoing, etc.)

Add domain-specific fields on top of these (e.g., `location`, `year`, `client` for projects; `role`, `bio`, `expertise` for team members).

### Display name in every response
Every bot response must include `p['display_name']` as a bold header at the top. This serves two purposes: (1) it confirms to the user which entity the bot is talking about, and (2) it allows automated test harnesses to verify correct entity resolution.

---

## 2. NLU Design

### One intent per field type — not one catch-all
Don't create a single `ask_about_entity` intent that handles everything. Create a dedicated intent for each type of information users might request: `ask_entity_overview`, `ask_entity_location`, `ask_entity_cost`, `ask_entity_team`, etc.

This granularity lets you:
- Route each question to a specific data field
- Test intent accuracy independently
- Add field-specific response formatting

### Entity extraction + synonym mapping
Every entity name variant must be registered in an `EntitySynonymMapper` block in `nlu.yml`. This maps surface forms to canonical keys at NLU time (before the action runs):

```yaml
- synonym: sofia_airport
  examples: |
    - Sofia Airport
    - T3
    - SOF airport
    - Sofia T3
```

This is the primary resolution path. Fuzzy matching in the action is only a fallback.

### Annotated NLU examples for every entity
For the main "ask about entity" intent, every entity needs at least 5 entity-annotated training examples:

```yaml
- tell me about [Sofia Airport](entity)
- what is [T3](entity)?
- [Sofia Airport](entity) project
```

Without these, the NLU won't reliably extract entities for less common names.

### Cover conversational phrasing, not just formal queries
Users don't talk like database queries. Cover the full range:
- Formal: "what is the design approach for this project?"
- Casual: "walk me through the design", "what drove the decisions here"
- Indirect: "what gave you headaches?", "how did you end up winning this?"
- Minimal: "in a nutshell?", "and the concept?", "keep going"

Add 10–15 conversational variants per intent. Aim for phrasing that actual customers or curious visitors would use.

### Prefix variants ("and the...", "what about the...")
Users naturally say "and the budget?" or "what about the design?" when following up. These need explicit NLU examples. Without them, the classifier sees unusual syntax and may misfire.

```yaml
- and the concept?
- and the budget?
- what about the sustainability?
- so what was the challenge?
```

### Out-of-scope training examples that match the domain
Add OOS examples that specifically include domain-relevant words (e.g., city names, weather, flights for a travel-adjacent chatbot). This prevents the NLU from routing domain-adjacent queries to the wrong intent.

---

## 3. Action Design

### Single action router pattern
One custom action handles all detail intents for a module. Inside, it:
1. Resolves the entity (from entity extraction, fuzzy match, or slot)
2. Determines the info type from the intent name
3. Dispatches to the right formatter via a dict: `INFO_DISPATCH = { "overview": lambda e: ..., "cost": lambda e: ... }`

This keeps all module logic in one place.

### Four-priority entity resolution
In `_resolve_project()` (or its equivalent):
1. **Entity extracted + canonical key** — EntitySynonymMapper already normalized it → use directly
2. **Entity extracted but not canonical** — fuzzy-match the extracted entity value
3. **No entity extracted** — fuzzy-match the full raw message text
4. **No match** — fall back to the conversation slot (context from previous turn)

### Fuzzy matching layers
- **Step 0**: Exact phrase lookup in `_NAME_INDEX` (dict of phrase → key), with punctuation stripped and accent-normalized (handles "velana?", "Pointe-à-Pitre")
- **Step 1**: Word-level fuzzy against city/key index (cutoff 0.82), skipping generic words ("airport", "project", "bank", "building")
- **Step 2**: Full-text fuzzy against all keys (cutoff 0.80 — high enough to reject "JFK airport" matching "SOF airport" via shared word "airport")

Maintain a `_SKIP_WORDS` set of generic words that should never trigger a fuzzy city match on their own.

### Slot for conversation context
Set a slot at the end of every successful entity response: `SlotSet("entity_name", entity_key)`. This allows follow-up questions ("where is it?", "what was the challenge?") to resolve without naming the entity again.

### "What else" redirection logic
When a general "tell me about X" intent fires but no new entity was extracted (user is following up, not introducing a new entity), redirect to the highlights/fun_facts formatter rather than repeating the intro teaser. This prevents the bot from looping on the same opener.

```python
if info_type == "about_entity":
    entity_value = next(tracker.get_latest_entity_values("entity"), None)
    if not entity_value:
        info_type = "facts"  # show highlights instead of repeating teaser
```

### Photo vs. video distinction
If the module includes media, detect whether the user asked for photos vs. video in the raw message and frame the response accordingly. Don't label a video response "Video" when the user asked for "photos" — acknowledge the mismatch gracefully.

### Out-of-scope action with fuzzy safety net
The OOS action (`action_handle_out_of_scope`) should attempt a fuzzy entity match on the raw message before giving up. This catches genuine entity queries that the NLU misclassified (rare project names, typos, unusual phrasing). Only skip the fuzzy safety net for messages containing clear non-domain signals (weather, taxi, joke, etc.) — maintain an `_OOS_SIGNALS` set for this.

### Capabilities question → clear context and explain
When the user asks "what else can you do?" or "what can you help me with?", they are exiting the entity context entirely. The response should:
1. Clear the slot: `SlotSet("entity_name", None)`
2. List all capabilities of the module (what fields it can explain, how to navigate, etc.)

---

## 4. Response Design

### Randomized response pools
Use 4–6 variant templates for openers, follow-up prompts, and suffixes. This prevents every response sounding identical. Use `random.choice()` at render time.

```python
_OPENERS = [
    "Here's a look at **{name}**",
    "Great choice — **{name}** is one of our more interesting ones.",
    "**{name}** — here's the story:",
]
```

### Follow-up prompts are genuine invitations, not menus
After the intro teaser, offer a follow-up prompt that feels like curiosity, not a product menu:

> "There's quite a bit more to this one — curious about the **budget**, the **design concept**, or what the **key challenge** was?"

Not:

> "Please select an option: 1. Budget 2. Concept 3. Challenge"

### OOS responses are warm recoveries, not dead ends
When the bot can't help, it should always offer a path back in. If a project/entity is active in the slot, reference it. If not, invite the user to name one.

> "That's a bit outside my lane — but we were just talking about **Sofia Airport**. Want to keep going? I can tell you about the team, the timeline, or what makes it stand out."

### Conversational suffixes (not always)
Add a trailing sentence to detail responses — but not every time. Include empty strings in the suffix pool so responses sometimes end cleanly. Over-suffixing makes the bot feel mechanical.

```python
_DETAIL_SUFFIXES = [
    "\n\nAnything else you'd like to know?",
    "\n\nHappy to go further — what else are you curious about?",
    "",  # clean ending, no suffix
    "",  # weighted toward no suffix
]
```

---

## 5. Context Flow Design

### Slot persistence is the default
Every turn should work without the user re-stating the entity. Design for multi-turn conversations:

> "tell me about sofia airport" → "where is it?" → "what was the challenge?" → "got any fun facts?"

All four turns should resolve to Sofia Airport without the user repeating the name.

### Explicit context switch trumps slot
If the user names a new entity, always switch to it — even mid-conversation. The new entity annotation takes priority over the slot.

### Three snap-out behaviors
1. **Capabilities question** (`"what else can you do?"`) → explain bot scope, clear slot
2. **Portfolio/list question** (`"what other X do you have?"`) → list all entities, don't clear slot
3. **Hard OOS** (weather, booking, etc.) → acknowledge OOS, offer to return to active entity

---

## 6. Testing Principles

### Two test suites
- **test_blast.py** — fast single-turn tests covering all intents and a representative set of projects (60–70 tests). Measures intent accuracy and project/entity resolution. Run after every retrain.
- **test_advanced.py** — multi-turn conversational tests organized by category (context flow, snap-out, conversational tone, typos, accuracy, edge cases, OOS). Run when making significant changes to actions or NLU.

### Test categories to cover
1. **Context Flow** — slot persistence across 3–4 turns, project switching, "and the X?" prefixes
2. **Snap Out** — capabilities question, OOS mid-convo, list-all mid-convo
3. **Conversational Tone** — casual phrasings for each intent
4. **Typos & Aliases** — one typo test per entity category, alias coverage
5. **Response Accuracy** — spot-check key facts per entity (location, client, year, etc.)
6. **Edge Cases** — no-context queries, unknown entities, pure entity names with no verb
7. **OOS Safety** — domain-adjacent OOS queries (weather cities, booking, etc.)

### Response content checks (not just intent)
Use three types of content checks per test:
- `must_contain` — all strings must appear (use for factual data: "Bulgaria", "MACL")
- `any_contain` — at least one string must appear (use for flexible phrasing)
- `must_not` — none may appear (use to confirm context switch worked, or OOS was caught)

### Multi-turn tests share a session
Tests in the same session group use the same sender ID, so the Rasa slot carries across turns. Group related tests under a shared `session_id`. Each group should be functionally independent of other groups.

### Confidence floor
Flag any classification below 0.70 confidence as a warning, even if the intent is correct. Low-confidence correct classifications are brittle and will fail with slight phrasing variations.

---

## 7. Extensibility Rules

### Adding a new entity (e.g., new project, new team member)
1. Add the entry to the data file (`projects_data.py`, `team_data.py`)
2. Add a synonym block in `nlu.yml` for all name variants
3. Add 5–10 entity-annotated NLU examples to the main intro intent
4. Run `rasa train`
5. No other files need changing

### Adding a new information field
1. Add the field to all entities in the data file (with a default for missing data)
2. Add a new intent in `domain.yml`
3. Add NLU examples (formal + conversational) in `nlu.yml`
4. Add a rule or story in `rules.yml` / `stories.yml`
5. Add an entry to `INFO_DISPATCH` in `actions.py`
6. Add test cases to both test suites

### Adding a new module (e.g., Team module alongside Projects)
Each module gets:
- Its own data file
- Its own slot (e.g., `team_member_name`)
- Its own action (`action_answer_team_query`)
- Its own `INFO_DISPATCH` dict
- Its own `_NAME_INDEX` and `_CITY_INDEX` equivalents
- Its own synonym blocks in `nlu.yml`
- Dedicated NLU intents prefixed clearly (e.g., `ask_team_*`, `ask_career_*`)

Modules should not share slots. A user asking about a team member and then a project in the same session should have independent context for each.

---

## Summary Table

| Principle | Rule |
|---|---|
| Data | One file, one dict, consistent schema, display_name always in response |
| NLU | One intent per field, entity-annotated examples for every entity, conversational phrasing |
| Resolution | EntitySynonymMapper first, then 4-priority fuzzy fallback |
| Actions | Single router + INFO_DISPATCH dict, slot for context, "what else" → highlights |
| Responses | Randomized templates, warm tone, follow-up invitations not menus |
| Context | Slot persists by default, new entity switches, three snap-out behaviors |
| Testing | Two suites, 7 categories, content checks (must/any/must_not), multi-turn sessions |
| Extensibility | New entity = 4 steps, new field = 6 steps, new module = independent slot + action |
