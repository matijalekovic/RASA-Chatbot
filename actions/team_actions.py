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

_TEAM_PAGE_URL = "https://www.1pax.com/the-team"
_TEAM_PAGE_LABELS = {
    "FR": "Voir la page de l'équipe sur 1pax.com",
    "ES": "Ver la página del equipo en 1pax.com",
    "PT-PT": "Ver a página da equipa em 1pax.com",
    "PT-BR": "Ver a página da equipe em 1pax.com",
    "ZH-HANS": "查看 1pax.com 团队页面",
    "ZH-HANT": "查看 1pax.com 團隊頁面",
    "SR": "Pogledaj stranicu tima na 1pax.com",
}


def _team_page_link(lang: Optional[str]) -> str:
    code = (lang or "").upper()
    label = _TEAM_PAGE_LABELS.get(code, "View the team page on 1pax.com")
    return f"[{label}]({_TEAM_PAGE_URL})"


def _infer_team_info_type(text: str) -> str:
    """Best-effort router for fallback paths when NLU confidence collapses."""
    normalized = text.lower()
    if any(token in normalized for token in (
        "leader", "leadership", "management", "founder", "ceo", "cfo",
        "director", "who runs", "who leads", "in charge", "at the helm", "boss",
    )):
        return "leadership"
    if any(token in normalized for token in ("architect", "architecture", "design team", "designer")):
        return "architects"
    if any(token in normalized for token in ("specialist", "bim", "ai", "technical", "visualization")):
        return "specialists"
    if any(token in normalized for token in ("operations", "admin", "administrative", "support")):
        return "operations"
    if any(token in normalized for token in ("collaborator", "consultant", "partner")):
        return "collaborators"
    if any(
        token in normalized
        for token in (
            "team",
            "staff",
            "people",
            "members",
            "roster",
            "employees",
            "who works",
            "who all works",
            "who is working",
            "who do you employ",
            "who is employed",
            "who works for you",
            "who works with you",
            "who works in your company",
            "who works at your company",
            "who works for your company",
            "people working",
            "people at your company",
            "employees at your company",
            "staff at your company",
        )
    ):
        return "overview"
    return ""


def _looks_like_company_founder_question(text: str) -> bool:
    normalized = _ascii_norm(text or "")
    return any(phrase in normalized for phrase in (
        "who founded", "who started 1pax", "who started the company",
        "who started the studio", "who created 1pax", "who created the company",
        "who established 1pax", "founder of 1pax", "how was 1pax founded",
    ))


def _looks_like_generic_innovation_question(text: str) -> bool:
    normalized = _ascii_norm(text or "").strip(" .!?,;:")
    if any(marker in normalized for marker in (
        "who leads innovation", "who handles innovation", "innovation officer",
        "innovation director", "communications and innovation",
    )):
        return False
    return normalized in {
        "innovation", "innovations", "your innovation", "your innovations",
        "tell me about innovation", "tell me about innovations",
        "tell me about your innovation", "tell me about your innovations",
        "what are your innovations", "show me your innovations",
    }


def _looks_like_studio_director_question(text: str) -> bool:
    normalized = _ascii_norm(text or "")
    if "director" not in normalized:
        return False
    if any(specific in normalized for specific in (
        "project director", "airport director", "airport project", "creative director",
        "design director", "communications director", "innovation director",
    )):
        return False
    return any(marker in normalized for marker in (
        "who is director", "who is the director", "who is your director",
        "who is 1pax director", "director of 1pax", "studio director",
        "company director", "who directs 1pax",
    ))


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
    "communications lead": "carla_miranda",
    "ccio": "carla_miranda",
    "innovation officer": "carla_miranda",
    "who leads innovation": "carla_miranda",
    "leads innovation": "carla_miranda",
    "who handles innovation": "carla_miranda",
    "patents lead": "carla_miranda",
    "who handles patents": "carla_miranda",
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
    "finance manager": "ali_fawaz",
    "who manages finances": "ali_fawaz",
    "financial officer": "ali_fawaz",
    "business development contact": "fabiola_espinoza",
    "bd contact": "fabiola_espinoza",
    "airport planner": "helene_henriot",
    "visualization": "christos_panagos",
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
    "who leads airport projects": "marija_stevanovic",
    "leads airport projects": "marija_stevanovic",
}
_PERSON_INDEX.update(_ROLE_ALIASES)


def _lookup_person(value: str) -> Optional[str]:
    """Return canonical person key for a given entity value."""
    norm = _ascii_norm(value.strip())

    if norm in {
        "innovation", "innovations", "patent", "patents", "communications",
        "finance", "finances", "bim", "director", "leader", "leadership",
        "management", "project", "projects",
    }:
        return None

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


def _lookup_explicit_role_owner_from_text(text: str) -> Optional[str]:
    """Resolve a topic owner only when the user explicitly asks *who* owns it.

    Bare topic words such as ``BIM`` and ``innovation`` deliberately stay out of
    the general person index: otherwise ordinary service/company questions can
    be hijacked by a team biography.  A guarded owner question is different and
    should take precedence over any noisy or stale ``person`` entity.
    """
    norm = _ascii_norm(text or "")
    if not re.search(r"\bwho\b", norm):
        return None

    if re.search(r"\b(?:patents?|innovation|communications?)\b", norm):
        return "carla_miranda"
    if re.search(r"\bbim\b", norm):
        return "marko_soskic"
    if re.search(r"\bai\b", norm) and re.search(r"\bdigital\b", norm):
        return "matija_lekovic"
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


def looks_like_person_detail_followup(text: str) -> bool:
    detail_type = _infer_person_detail_type(text)
    if detail_type is None:
        return False

    norm = _ascii_norm(text or "")
    tokens = set(re.findall(r"[a-z0-9]+", norm))
    pronoun_markers = {
        "her",
        "hers",
        "she",
        "him",
        "his",
        "he",
        "their",
        "theirs",
        "they",
        "them",
    }
    phrase_markers = (
        "that person",
        "this person",
        "team member",
        "person profile",
    )
    if tokens & pronoun_markers or any(phrase in norm for phrase in phrase_markers):
        return True

    if detail_type in {"email", "role"} and len(tokens) <= 4:
        return True

    return False


def _infer_person_detail_type(text: str) -> Optional[str]:
    norm = _ascii_norm(text or "")
    if not norm:
        return None
    if any(term in norm for term in ("email", "e mail", "contact", "reach her", "reach him", "reach them")):
        return "email"
    if any(term in norm for term in ("role", "title", "job", "position", "what does she do", "what does he do", "what do they do")):
        return "role"
    if any(term in norm for term in ("projects", "project", "worked on", "works on", "portfolio")):
        return "projects"
    return None


def _person_detail_answer(person_key: str, detail_type: str) -> str:
    person = PERSONS[person_key]
    name = person.get("display_name", "This team member")
    title = person.get("title", "Team member")
    group = person.get("group", "Team")

    if detail_type == "email":
        return (
            f"I do not have a public direct email for **{name}** in the team profile. "
            "For a routed message, use **contact@1pax.com** or the contact form on "
            "1pax.com and mention the person or topic."
        )
    if detail_type == "role":
        return f"**{name}** is **{title}** in the 1PAX **{group}** group."
    if detail_type == "projects":
        return (
            f"**{name}**'s public profile lists the role as **{title}**. "
            "The chatbot does not have a named project-assignment list for each "
            "person yet, but I can answer project-specific team, scope, and role "
            "questions if you name the project."
        )
    return f"**{name}** — **{title}**."


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

        from .calendly_actions import (
            continue_active_calendly_scheduling,
            looks_like_new_schedule_request,
            run_calendly_scheduling,
            schedule_topic_shift_events,
        )

        schedule_events = continue_active_calendly_scheduling(dispatcher, tracker, domain)
        if schedule_events is not None:
            return schedule_events
        schedule_reset_events = schedule_topic_shift_events(tracker)
        if looks_like_new_schedule_request(tracker.latest_message.get("text") or ""):
            return schedule_reset_events + run_calendly_scheduling(
                dispatcher,
                tracker,
                domain,
            )

        lang = get_lang(tracker)
        lang_event = [SlotSet("language", lang)]
        team_context_events = [SlotSet("project_name", None)]

        intent = tracker.latest_message.get("intent", {}).get("name", "")
        raw_text = tracker.latest_message.get("text", "")

        # Career/applicant questions often say "join the team"; keep those in
        # the company careers path instead of showing the team roster.
        from .company_actions import ActionAnswerCompanyQuery, looks_like_career_question

        if looks_like_career_question(raw_text):
            return ActionAnswerCompanyQuery().run(dispatcher, tracker, domain)

        # "what projects have they done?" is about the studio's portfolio, not a person.
        raw_words = set(re.sub(r"[^a-z0-9 ]+", " ", raw_text.lower()).split())
        if raw_words & {"projects", "portfolio"} and not has_known_person_reference(raw_text):
            from .actions import ActionListProjects

            return ActionListProjects().run(dispatcher, tracker, domain)

        if _looks_like_company_founder_question(raw_text):
            return ActionAnswerCompanyQuery().run(dispatcher, tracker, domain)

        if _looks_like_generic_innovation_question(raw_text):
            return ActionAnswerCompanyQuery().run(dispatcher, tracker, domain)

        if _looks_like_studio_director_question(raw_text):
            dispatcher.utter_message(
                text=translate_response(
                    "1PAX does not list a single generic **Director** title. The studio is led by "
                    "**Mabel Miranda, Founder & CEO**. If you meant project delivery, "
                    "**Marija Stevanovic** is the Airport Project Director.",
                    lang,
                )
            )
            dispatcher.utter_message(text=_team_page_link(lang))
            return schedule_reset_events + [
                SlotSet("person_name", "mabel_miranda"),
                SlotSet("project_name", None),
            ] + lang_event

        slot_person = tracker.get_slot("person_name")
        if slot_person and looks_like_person_detail_followup(raw_text):
            return (
                schedule_reset_events
                + team_context_events
                + self._handle_person_query(dispatcher, tracker, lang)
            )

        # ── Individual person lookup ─────────────────────────────────────────
        if intent == "ask_about_team_member" or _lookup_person_from_text(raw_text):
            return (
                schedule_reset_events
                + team_context_events
                + self._handle_person_query(dispatcher, tracker, lang)
            )

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
            return schedule_reset_events + team_context_events + lang_event

        translated_parts = translate_responses(list(TEAM_INFO[data_key]), lang)
        translated_parts.append(_team_page_link(lang))

        meeting_cta_index = None
        if data_key in {"overview", "leadership", "operations"}:
            meeting_cta_index = len(translated_parts)
            translated_parts.append(translate_response(meeting_cta_text("team"), lang))

        for index, msg in enumerate(translated_parts):
            if index == meeting_cta_index:
                dispatcher.utter_message(text=msg, buttons=meeting_buttons(lang))
            else:
                dispatcher.utter_message(text=msg)

        return schedule_reset_events + team_context_events + lang_event

    # ────────────────────────────────────────────────────────────────────────────

    def _handle_person_query(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        lang: Optional[str] = None,
    ) -> List[Dict[Text, Any]]:
        """Look up a person by entity value and return their bio."""

        raw_text = tracker.latest_message.get("text", "")

        # Explicit role-owner wording is stronger evidence than an extracted
        # entity.  This prevents a noisy entity (or an auto-filled stale slot)
        # from turning "who manages patents and innovation?" into the wrong bio.
        person_key = _lookup_explicit_role_owner_from_text(raw_text)

        # Otherwise try ALL current entities to be robust against spurious
        # short-token extractions like 'the'.
        if not person_key:
            for entity in tracker.latest_message.get("entities", []):
                if entity.get("entity") == "person":
                    raw_value = entity.get("value", "")
                    person_key = _lookup_person(raw_value)
                    if person_key:
                        break

        if not person_key:
            person_key = _lookup_person_from_text(raw_text)

        # Use prior person context only for genuine anaphoric/detail follow-ups.
        # A stale Carla slot must never beat a new explicit founder/director query.
        if not person_key and looks_like_person_detail_followup(
            raw_text
        ):
            slot_val = tracker.get_slot("person_name")
            if slot_val:
                person_key = _lookup_person(slot_val)

        lang_event = [SlotSet("language", lang)]

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
        detail_type = _infer_person_detail_type(tracker.latest_message.get("text", ""))
        if detail_type:
            dispatcher.utter_message(
                text=translate_response(_person_detail_answer(person_key, detail_type), lang)
            )
            return [SlotSet("person_name", person_key)] + lang_event

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

        translated_parts = translate_responses(output_parts, lang)
        translated_parts.append(_team_page_link(lang))

        for msg in translated_parts:
            dispatcher.utter_message(text=msg)

        return [SlotSet("person_name", person_key)] + lang_event
