"""
1PAX Services — Rasa Custom Action
====================================
Handles all service-query intents (ask_service_* and ask_services_list)
via a single router action.
Stateless — no slot tracking needed (answers are about service offerings, not a specific project).
"""

import random
import re
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from .services_data import SERVICES_INFO
from .projects_data import CATEGORIES, PROJECTS
from .meeting_prompts import meeting_buttons, meeting_cta_text
from .translation import get_lang, translate_response, translate_responses


# ── Intent suffix → SERVICES_INFO key ────────────────────────────────────────

SERVICES_DISPATCH: Dict[str, str] = {
    "list":            "services_list",
    "airports":        "airports",
    "urbanism":        "urbanism",
    "innovation":      "innovation",
    "future_mobility": "future_mobility",
    "control_towers":  "control_towers",
    "interior":        "interior",
    "working_living":  "working_living",
    "bim":             "bim",
}

_PROJECT_DETAIL_HINTS = {
    "approach",
    "architect",
    "budget",
    "capacity",
    "challenge",
    "client",
    "commission",
    "complete",
    "concept",
    "cost",
    "designed",
    "inaugurated",
    "location",
    "partner",
    "program",
    "programme",
    "scope",
    "status",
    "strategy",
    "tender",
    "timeline",
    "year",
}

_SERVICE_PROJECT_LIMIT = 5

_SERVICE_PROJECT_EXAMPLES: Dict[str, List[str]] = {
    "airports": [
        "sofia_airport",
        "velana_airport",
        "belgrade_airport",
        "bordeaux_airport",
        "cayenne_terminal",
    ],
    "urbanism": [
        "doha_metro_depot",
        "cayenne_airport_masterplan",
        "cabo_verde_airports",
        "lima_metro_line1_stations",
        "pachacamac_metro_station",
    ],
    "future_mobility": [
        "cergy_vertiport",
        "singapore_vertiport",
        "paris_heliport",
        "pachacamac_metro_station",
        "belgrade_metro_line1",
    ],
    "control_towers": [
        "riga_control_tower",
        "chateauroux_atct_mro",
        "le_bourget_fire_station",
        "belgrade_fire_station",
        "cdg_baggage_building",
    ],
    "interior": CATEGORIES.get("Interior Design", [])[:_SERVICE_PROJECT_LIMIT],
    "working_living": CATEGORIES.get("Working and Living", [])[:_SERVICE_PROJECT_LIMIT],
    "bim": [
        "velana_airport",
        "sofia_airport",
        "doha_metro_depot",
        "belgrade_airport",
        "fuzhou_airport",
    ],
    "innovation": [
        "cergy_vertiport",
        "singapore_vertiport",
        "paris_heliport",
        "pachacamac_metro_station",
        "lima_metro_line1_stations",
    ],
}


def _infer_service_info_type(text: str) -> str:
    """Best-effort router for fallback paths when NLU confidence collapses."""
    normalized = text.lower()
    if any(token in normalized for token in ("fee", "fees", "price", "pricing", "charge", "charges", "cost")):
        return "pricing"
    if any(token in normalized for token in ("bim", "model", "revit")):
        return "bim"
    if any(token in normalized for token in ("interior", "retail", "food hall", "lounge")):
        return "interior"
    if any(token in normalized for token in (
        "working",
        "living",
        "office",
        "residential",
        "residential tower",
        "housing",
        "hotel",
        "hotels",
        "resort",
        "resorts",
        "hospitality",
        "mixed-use",
        "mixed use",
        "workplace",
        "embassy",
        "embassies",
        "diplomatic",
        "diplomatic mission",
    )):
        return "working_living"
    if any(token in normalized for token in ("control tower", "air traffic control tower", "atct")):
        return "control_towers"
    if any(token in normalized for token in ("future mobility", "vertiport", "evtol", "mobility", "skylo", "drone logistics", "aerial logistics", "low-altitude", "low altitude")):
        return "future_mobility"
    if (
        any(token in normalized for token in ("innovation", "research", "patent"))
        or re.search(r"\bai\b", normalized)
    ):
        return "innovation"
    if any(token in normalized for token in (
        "urban",
        "urbanism",
        "masterplan",
        "master plan",
        "city",
        "public space",
        "public spaces",
        "civic space",
        "civic spaces",
    )):
        return "urbanism"
    if any(token in normalized for token in ("airport", "terminal", "rail", "station")):
        return "airports"
    if any(token in normalized for token in ("hospital", "hospitals", "healthcare")):
        return "list"
    if any(token in normalized for token in ("service", "services", "offer", "provide", "capabilities")):
        return "list"
    return ""


def _looks_like_construction_supervision_question(text: str) -> bool:
    normalized = (text or "").lower()
    return "construction supervision" in normalized or "site supervision" in normalized


def _looks_like_airport_proposal_request(text: str) -> bool:
    normalized = (text or "").lower()
    has_airport_scope = any(
        term in normalized
        for term in ("airport", "terminal", "airside", "landside", "aviation")
    )
    has_commercial_request = any(
        term in normalized
        for term in ("proposal", "request for proposal", "rfp", "hire 1pax", "fee proposal")
    )
    return has_airport_scope and has_commercial_request


def _should_delegate_to_project(tracker: Tracker, text: str) -> bool:
    project_values = list(tracker.get_latest_entity_values("project"))
    if not any(value in PROJECTS for value in project_values):
        return False
    normalized = (text or "").lower()
    return any(hint in normalized for hint in _PROJECT_DETAIL_HINTS)


def _project_card_payload(project_key: str) -> Dict[str, str]:
    project = PROJECTS[project_key]
    meta_bits = [
        project.get("location", ""),
        project.get("category", ""),
        project.get("year", ""),
    ]
    return {
        "id": project_key,
        "title": project.get("display_name", project_key.replace("_", " ").title()),
        "meta": " | ".join(bit for bit in meta_bits if bit),
        "image": project.get("cover_image_url", ""),
        "url": project.get("project_url", ""),
    }


def _service_project_cards(info_type: str) -> List[Dict[str, str]]:
    keys = [
        key
        for key in _SERVICE_PROJECT_EXAMPLES.get(info_type, [])
        if key in PROJECTS
    ]
    return [_project_card_payload(key) for key in keys[:_SERVICE_PROJECT_LIMIT]]


def _service_examples_text(info_type: str, count: int) -> str:
    labels = {
        "airports": "airport and railstation",
        "urbanism": "urbanism and masterplanning",
        "future_mobility": "future mobility",
        "control_towers": "control tower and ancillary building",
        "interior": "interior design and retail",
        "working_living": "working and living",
        "bim": "BIM-led",
        "innovation": "innovation and mobility",
    }
    label = labels.get(info_type, "service-related")
    return f"Here are **{count} relevant {label} project examples** from the 1PAX portfolio:"


class ActionAnswerServicesQuery(Action):
    """Single router for all ask_service_* and ask_services_list intents."""

    def name(self) -> Text:
        return "action_answer_services_query"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        from .calendly_actions import (
            continue_active_calendly_scheduling,
            schedule_topic_shift_events,
        )

        schedule_events = continue_active_calendly_scheduling(dispatcher, tracker, domain)
        if schedule_events is not None:
            return schedule_events
        schedule_reset_events = schedule_topic_shift_events(tracker)
        from .calendly_actions import looks_like_new_schedule_request, run_calendly_scheduling

        if looks_like_new_schedule_request(tracker.latest_message.get("text") or ""):
            return schedule_reset_events + run_calendly_scheduling(dispatcher, tracker, domain)

        lang = get_lang(tracker)
        lang_event = [SlotSet("language", lang)]

        intent = tracker.latest_message.get("intent", {}).get("name", "")
        raw_text = tracker.latest_message.get("text", "")

        from .company_actions import _looks_like_office_location_query

        if _looks_like_office_location_query(raw_text):
            from .company_actions import ActionAnswerCompanyQuery

            return ActionAnswerCompanyQuery().run(dispatcher, tracker, domain)

        if _looks_like_construction_supervision_question(raw_text):
            dispatcher.utter_message(
                text=translate_response(
                    "1PAX's published service list includes **construction phasing**, "
                    "coordination between construction works and live operations, BIM coordination, "
                    "clash detection, and project-management consulting. It does **not** list "
                    "standalone construction-site supervision as a standard service, so I should not "
                    "claim that scope without confirmation. For resident/site supervision, inspections, "
                    "or contract administration, send the project location, stage, and required role to "
                    "**contact@1pax.com** so the studio can confirm availability and scope.",
                    lang,
                ),
                buttons=meeting_buttons(lang),
            )
            return schedule_reset_events + lang_event

        from .actions import ActionListProjects, _portfolio_request
        from .company_inquiries import _building_type, build_inquiry_answer, infer_inquiry_type
        from .portfolio_insights import _norm as _insight_norm

        # Portfolio rankings/filters ("experience renovating live terminals?") and
        # company due-diligence questions ("are you ISO certified?") that NLU sent here.
        if _portfolio_request(tracker) is not None:
            return schedule_reset_events + ActionListProjects().run(dispatcher, tracker, domain)
        from .company_actions import _infer_client_segment

        inquiry_type = infer_inquiry_type(raw_text)
        norm_words = _insight_norm(raw_text).split()
        client_segment_question = bool(
            {"client", "clients", "customer", "customers"} & set(norm_words)
            and _infer_client_segment(raw_text)
        )
        if client_segment_question or (
            inquiry_type
            and inquiry_type not in {"beyond_airports", "engagement", "project_stages"}
            and "bim" not in norm_words
        ):
            from .company_actions import ActionAnswerCompanyQuery

            return ActionAnswerCompanyQuery().run(dispatcher, tracker, domain)

        building = _building_type(_insight_norm(raw_text))
        if building and building[0] == "not_in_portfolio":
            for part in build_inquiry_answer("beyond_airports", raw_text) or []:
                dispatcher.utter_message(text=translate_response(part, lang), buttons=meeting_buttons(lang))
            return schedule_reset_events + lang_event

        if _looks_like_airport_proposal_request(raw_text):
            dispatcher.utter_message(
                text=translate_response(
                    "Yes — 1PAX accepts enquiries for **airport and terminal design or consultancy "
                    "proposals**. To prepare a useful scope, send **contact@1pax.com** the project "
                    "location, greenfield or brownfield context, current design stage, required services, "
                    "target capacity, programme, procurement route, and any existing brief or drawings. "
                    "Relevant published capabilities include functional planning, passenger-flow and "
                    "capacity studies, terminal and envelope design, airside/landside masterplanning, "
                    "BHS feasibility, fire-safety review, multimodal integration, and BIM coordination.",
                    lang,
                ),
                buttons=meeting_buttons(lang),
            )
            return schedule_reset_events + lang_event

        if _should_delegate_to_project(tracker, raw_text):
            from .actions import ActionAnswerProjectQuery

            return ActionAnswerProjectQuery().run(dispatcher, tracker, domain)

        raw_info_type = _infer_service_info_type(raw_text)

        # Strip prefix: "ask_services_list" → "list", "ask_service_airports" → "airports".
        # Pricing words are more specific than the broad services-list intent.
        if raw_info_type == "pricing":
            info_type = "pricing"
        elif intent == "ask_services_list":
            info_type = "list"
        elif intent.startswith("ask_service_"):
            info_type = intent.replace("ask_service_", "")
        else:
            info_type = raw_info_type

        if info_type == "pricing":
            dispatcher.utter_message(
                text=translate_response(
                    "1PAX pricing depends on the project type, scope, location, "
                    "delivery stage, and required disciplines. For a realistic fee "
                    "or proposal, share the project context with the studio so the "
                    "team can scope it properly.",
                    lang,
                ),
                buttons=meeting_buttons(lang),
            )
            return schedule_reset_events + lang_event

        data_key = SERVICES_DISPATCH.get(info_type)

        if not data_key or data_key not in SERVICES_INFO:
            dispatcher.utter_message(
                text=translate_response(
                    "I can tell you about **1PAX's services** — airports, urbanism, BIM, "
                    "future mobility, interior design, and more. What would you like to know?",
                    lang,
                ),
                buttons=meeting_buttons(lang),
            )
            return schedule_reset_events + lang_event

        output_parts = list(SERVICES_INFO[data_key])

        # Append a randomised follow-up prompt for detail pages (not list)
        if info_type != "list":
            follow_up_pool = SERVICES_INFO.get("follow_up", [])
            if follow_up_pool:
                suffix = random.choice(follow_up_pool + ["", ""])   # 2-in-4 chance of no suffix
                if suffix:
                    output_parts.append(suffix)

        project_cards = _service_project_cards(info_type)
        project_cards_index = None
        if project_cards:
            project_cards_index = len(output_parts)
            output_parts.append(_service_examples_text(info_type, len(project_cards)))

        meeting_cta_index = None
        if data_key in {
            "services_list",
            "airports",
            "urbanism",
            "future_mobility",
            "control_towers",
            "bim",
        }:
            meeting_cta_index = len(output_parts)
            output_parts.append(meeting_cta_text("services"))

        # Send each message part separately, but translate them in one batch.
        for index, msg in enumerate(translate_responses(output_parts, lang)):
            if index == project_cards_index:
                dispatcher.utter_message(
                    text=msg,
                    json_message={"project_cards": project_cards},
                )
            elif index == meeting_cta_index:
                dispatcher.utter_message(text=msg, buttons=meeting_buttons(lang))
            else:
                dispatcher.utter_message(text=msg)

        return schedule_reset_events + lang_event
