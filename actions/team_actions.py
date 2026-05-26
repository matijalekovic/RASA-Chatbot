"""
1PAX Team Members — Rasa Custom Action
========================================
Handles all team-query intents (ask_team_* and ask_about_team_member)
via a single router action.

Group intents (ask_team_overview/leadership/architects/specialists/operations/collaborators)
→ dispatch to TEAM_INFO group responses.

Individual intent (ask_about_team_member)
→ extract person entity, look up in PERSONS dict.
"""

import random
import re
import unicodedata
from difflib import SequenceMatcher, get_close_matches
from typing import Any, Optional, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from .team_data import TEAM_INFO, PERSONS
from .meeting_prompts import meeting_buttons, meeting_cta_text
from .translation import get_lang, translate_response, translate_responses


# ── Intent suffix → TEAM_INFO key ─────────────────────────────────────────────

TEAM_DISPATCH: Dict[str, str] = {
    "overview":      "overview",
    "leadership":    "leadership",
    "architects":    "architects",
    "specialists":   "specialists",
    "operations":    "operations",
    "collaborators": "collaborators",
}


def _infer_team_info_type(text: str) -> str:
    """Best-effort router for fallback paths when NLU confidence collapses."""
    normalized = text.lower()
    if any(token in normalized for token in ("leader", "leadership", "management", "founder", "ceo", "cfo")):
        return "leadership"
    if any(token in normalized for token in ("architect", "architecture", "design team", "designer")):
        return "architects"
    if any(token in normalized for token in ("specialist", "bim", "ai", "technical", "visualization")):
        return "specialists"
    if any(token in normalized for token in ("operations", "admin", "administrative", "support")):
        return "operations"
    if any(token in normalized for token in ("collaborator", "consultant", "partner")):
        return "collaborators"
    if any(token in normalized for token in ("team", "staff", "people", "members", "roster", "employees")):
        return "overview"
    return ""


# ── Name lookup helpers ────────────────────────────────────────────────────────

def _ascii_norm(s: str) -> str:
    """Normalise accented characters to ASCII equivalents."""
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("ascii").lower()


# Build a flat lookup index: normalised variant → canonical key
_PERSON_INDEX: Dict[str, str] = {}

for _key, _data in PERSONS.items():
    _display = _data.get("display_name", "")
    # canonical key
    _PERSON_INDEX[_key] = _key
    # full display name
    _PERSON_INDEX[_ascii_norm(_display)] = _key
    # first name
    _parts = _display.split()
    if _parts:
        _PERSON_INDEX[_ascii_norm(_parts[0])] = _key
    # last name (only if key is unambiguous — skip where first/last name clashes)
    if len(_parts) >= 2:
        _last = _ascii_norm(_parts[-1])
        if _last not in _PERSON_INDEX:  # only set if not already occupied
            _PERSON_INDEX[_last] = _key

# Add role aliases
_ROLE_ALIASES = {
    "ceo": "mabel_miranda",
    "founder": "mabel_miranda",
    "chief executive": "mabel_miranda",
    "cfo": "ali_fawaz",
    "fractional cfo": "ali_fawaz",
    "chief financial officer": "ali_fawaz",
    "business development manager": "fabiola_espinoza",
    "bd manager": "fabiola_espinoza",
    "business development": "fabiola_espinoza",
    "communications officer": "carla_miranda",
    "chief communications": "carla_miranda",
    "communications": "carla_miranda",
    "communications lead": "carla_miranda",
    "ccio": "carla_miranda",
    "innovation officer": "carla_miranda",
    "innovation": "carla_miranda",
    "patents": "carla_miranda",
    "barcelona lead": "carla_miranda",
    "barcelona office": "carla_miranda",
    "shanghai representative": "bashan_yang",
    "visualization expert": "bashan_yang",
    "airport project director": "marija_stevanovic",
    "project director": "marija_stevanovic",
    "senior project manager": "claudia_cornejo",
    "bim manager": "marko_soskic",
    "bim specialist": "kevin_guzman",
    "ai specialist": "matija_lekovic",
    "ai and digital specialist": "matija_lekovic",
    "ai and digital": "matija_lekovic",
    "digital specialist": "matija_lekovic",
    "architectural technologist": "tiago_cobrado",
    "construction phasing": "boris_stojnic",
    "construction phasing expert": "boris_stojnic",
    "phasing expert": "boris_stojnic",
    "finance": "ali_fawaz",
    "finances": "ali_fawaz",
    "financial officer": "ali_fawaz",
    "business development contact": "fabiola_espinoza",
    "bd contact": "fabiola_espinoza",
    "airport planner": "helene_henriot",
    "visualization": "christos_panagos",
    "bim": "marko_soskic",
    "bim lead": "marko_soskic",
    "bim coordinator": "marko_soskic",
    "jv contact": "fabiola_espinoza",
    "joint venture contact": "fabiola_espinoza",
    "business development contact": "fabiola_espinoza",
    "project manager": "claudia_cornejo",
    "1pax's business development contact": "fabiola_espinoza",
    "main point of contact for a jv": "fabiola_espinoza",
    "jv point of contact": "fabiola_espinoza",
    "point of contact for joint ventures": "fabiola_espinoza",
    "point of contact for a jv": "fabiola_espinoza",
    "the main point of contact for a jv": "fabiola_espinoza",
    "the jv contact": "fabiola_espinoza",
    "the project director for airport work": "marija_stevanovic",
    "project director for airport work": "marija_stevanovic",
    "airport projects": "marija_stevanovic",
}
_PERSON_INDEX.update(_ROLE_ALIASES)


def _lookup_person(value: str) -> Optional[str]:
    """Return canonical person key for a given entity value."""
    norm = _ascii_norm(value.strip())

    # Direct match
    if norm in _PERSON_INDEX:
        return _PERSON_INDEX[norm]

    # Fuzzy match
    candidates = list(_PERSON_INDEX.keys())
    matches = get_close_matches(norm, candidates, n=1, cutoff=0.72)
    if matches:
        return _PERSON_INDEX[matches[0]]

    return None


def _lookup_person_from_text(text: str) -> Optional[str]:
    """Find a known person or role alias in raw fallback text."""
    norm = _ascii_norm(text or "")
    for alias, key in sorted(_PERSON_INDEX.items(), key=lambda item: len(item[0]), reverse=True):
        if len(alias) < 3:
            continue
        if re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", norm):
            return key

    tokens = re.findall(r"[a-z0-9]+", norm)
    if not tokens:
        return None

    for alias, key in sorted(_PERSON_INDEX.items(), key=lambda item: len(item[0]), reverse=True):
        alias_tokens = [
            token for token in re.findall(r"[a-z0-9]+", alias)
            if len(token) >= 4
        ]
        if len(alias_tokens) >= 2 and all(
            any(_token_matches_alias(alias_token, token) for token in tokens)
            for alias_token in alias_tokens
        ):
            return key
        if len(alias_tokens) == 1 and len(alias_tokens[0]) >= 5:
            alias_token = alias_tokens[0]
            if any(_token_matches_alias(alias_token, token) for token in tokens):
                return key
    return None


def _token_matches_alias(alias_token: str, token: str) -> bool:
    """Match names with light inflection, e.g. matija→matiji or lekovic→lekovicu."""
    if alias_token == token:
        return True
    if len(alias_token) < 5 or len(token) < 5:
        return False
    if alias_token[:5] == token[:5]:
        return True
    return SequenceMatcher(None, alias_token, token).ratio() >= 0.84


def has_known_person_reference(text: str) -> bool:
    """Public fallback hook for routing known team-member questions."""
    return _lookup_person_from_text(text) is not None


# ── Action ─────────────────────────────────────────────────────────────────────

class ActionAnswerTeamQuery(Action):
    """Single router for all ask_team_* and ask_about_team_member intents."""

    def name(self) -> Text:
        return "action_answer_team_query"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        from .calendly_actions import continue_active_calendly_scheduling

        schedule_events = continue_active_calendly_scheduling(dispatcher, tracker, domain)
        if schedule_events is not None:
            return schedule_events

        lang = get_lang(tracker)
        lang_event = [SlotSet("language", lang)] if lang else []

        intent = tracker.latest_message.get("intent", {}).get("name", "")
        raw_text = tracker.latest_message.get("text", "")

        # ── Individual person lookup ─────────────────────────────────────────
        if intent == "ask_about_team_member" or _lookup_person_from_text(raw_text):
            return self._handle_person_query(dispatcher, tracker, lang)

        # ── Group dispatch ───────────────────────────────────────────────────
        if intent.startswith("ask_team_"):
            info_type = intent.replace("ask_team_", "")
        else:
            info_type = _infer_team_info_type(tracker.latest_message.get("text", ""))
        data_key = TEAM_DISPATCH.get(info_type)

        if not data_key or data_key not in TEAM_INFO:
            dispatcher.utter_message(
                text=translate_response(
                    "I can tell you about the **1PAX team** — overview, leadership, architects, "
                    "specialists, and operations. Or ask about a specific person: "
                    "*\"Tell me about Mabel Miranda\"* or *\"Who is the BIM Manager?\"*",
                    lang,
                ),
                buttons=meeting_buttons(lang),
            )
            return lang_event

        output_parts = list(TEAM_INFO[data_key])

        meeting_cta_index = None
        if data_key in {"overview", "leadership", "operations"}:
            meeting_cta_index = len(output_parts)
            output_parts.append(meeting_cta_text("team"))

        for index, msg in enumerate(translate_responses(output_parts, lang)):
            if index == meeting_cta_index:
                dispatcher.utter_message(text=msg, buttons=meeting_buttons(lang))
            else:
                dispatcher.utter_message(text=msg)

        return lang_event

    # ────────────────────────────────────────────────────────────────────────────

    def _handle_person_query(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        lang: Optional[str] = None,
    ) -> List[Dict[Text, Any]]:
        """Look up a person by entity value and return their bio."""

        # Extract person entity from current message — try ALL entities to be
        # robust against spurious short-token extractions like 'the'
        person_key = None
        for entity in tracker.latest_message.get("entities", []):
            if entity.get("entity") == "person":
                raw_value = entity.get("value", "")
                person_key = _lookup_person(raw_value)
                if person_key:
                    break

        # Fallback: check person_name slot (cross-turn context)
        if not person_key:
            slot_val = tracker.get_slot("person_name")
            if slot_val:
                person_key = _lookup_person(slot_val)

        if not person_key:
            person_key = _lookup_person_from_text(tracker.latest_message.get("text", ""))

        lang_event = [SlotSet("language", lang)] if lang else []

        if not person_key or person_key not in PERSONS:
            dispatcher.utter_message(
                text=translate_response(
                    "Who would you like to know about? You can ask about any 1PAX team member — "
                    "for example: *\"Tell me about Marija Stevanovic\"*, *\"Who is the CFO?\"*, "
                    "or *\"Who handles AI at 1PAX?\"*",
                    lang,
                )
            )
            return lang_event

        person = PERSONS[person_key]
        output_parts = list(person["bio"])

        # Light follow-up
        suffix = random.choice([
            "\n\nWant to know about anyone else on the team?",
            "\n\nAny other team member you'd like to explore?",
            "",
            "",
        ])
        if suffix:
            output_parts.append(suffix)

        for msg in translate_responses(output_parts, lang):
            dispatcher.utter_message(text=msg)

        return lang_event
