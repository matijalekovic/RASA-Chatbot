"""
1PAX Services — Rasa Custom Action
====================================
Handles all service-query intents (ask_service_* and ask_services_list)
via a single router action.
Stateless — no slot tracking needed (answers are about service offerings, not a specific project).
"""

import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from .services_data import SERVICES_INFO
from .projects_data import PROJECTS
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


def _infer_service_info_type(text: str) -> str:
    """Best-effort router for fallback paths when NLU confidence collapses."""
    normalized = text.lower()
    if any(token in normalized for token in ("bim", "model", "revit")):
        return "bim"
    if any(token in normalized for token in ("control tower", "tower")):
        return "control_towers"
    if any(token in normalized for token in ("interior", "retail", "food hall", "lounge")):
        return "interior"
    if any(token in normalized for token in ("working", "living", "office", "residential", "workplace")):
        return "working_living"
    if any(token in normalized for token in ("future mobility", "vertiport", "evtol", "mobility", "skylo", "drone logistics", "aerial logistics", "low-altitude", "low altitude")):
        return "future_mobility"
    if any(token in normalized for token in ("innovation", "research", "ai", "patent")):
        return "innovation"
    if any(token in normalized for token in ("urban", "urbanism", "masterplan", "master plan", "city")):
        return "urbanism"
    if any(token in normalized for token in ("airport", "terminal", "rail", "station")):
        return "airports"
    if any(token in normalized for token in ("hospital", "hospitals", "healthcare")):
        return "list"
    if any(token in normalized for token in ("service", "services", "offer", "provide", "capabilities")):
        return "list"
    return ""


def _should_delegate_to_project(tracker: Tracker, text: str) -> bool:
    project_values = list(tracker.get_latest_entity_values("project"))
    if not any(value in PROJECTS for value in project_values):
        return False
    normalized = (text or "").lower()
    return any(hint in normalized for hint in _PROJECT_DETAIL_HINTS)


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

        lang = get_lang(tracker)
        lang_event = [SlotSet("language", lang)] if lang else []

        intent = tracker.latest_message.get("intent", {}).get("name", "")
        raw_text = tracker.latest_message.get("text", "")

        if _should_delegate_to_project(tracker, raw_text):
            from .actions import ActionAnswerProjectQuery

            return ActionAnswerProjectQuery().run(dispatcher, tracker, domain)

        # Strip prefix: "ask_services_list" → "list", "ask_service_airports" → "airports"
        if intent == "ask_services_list":
            info_type = "list"
        elif intent.startswith("ask_service_"):
            info_type = intent.replace("ask_service_", "")
        else:
            info_type = _infer_service_info_type(raw_text)

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
            if index == meeting_cta_index:
                dispatcher.utter_message(text=msg, buttons=meeting_buttons(lang))
            else:
                dispatcher.utter_message(text=msg)

        return schedule_reset_events + lang_event
