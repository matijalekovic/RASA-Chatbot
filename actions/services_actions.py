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
from .site_links import append_site_link, service_url
from .translation import get_lang, translate_response


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

SERVICE_LINK_LABELS: Dict[str, str] = {
    "services_list": "Our Projects",
    "airports": "Airports and Railstations",
    "urbanism": "Urbanism and Masterplan",
    "innovation": "Innovation and Research",
    "future_mobility": "Future of Mobility",
    "control_towers": "Airports and Railstations",
    "interior": "Retail and Interior Design",
    "working_living": "Working and Living",
    "bim": "BIM",
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
    if any(token in normalized for token in ("future mobility", "vertiport", "evtol", "mobility")):
        return "future_mobility"
    if any(token in normalized for token in ("innovation", "research", "ai", "patent")):
        return "innovation"
    if any(token in normalized for token in ("urban", "urbanism", "masterplan", "master plan", "city")):
        return "urbanism"
    if any(token in normalized for token in ("airport", "terminal", "rail", "station")):
        return "airports"
    if any(token in normalized for token in ("service", "services", "offer", "provide", "capabilities")):
        return "list"
    return ""


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

        from .calendly_actions import continue_active_calendly_scheduling

        schedule_events = continue_active_calendly_scheduling(dispatcher, tracker, domain)
        if schedule_events is not None:
            return schedule_events

        lang = get_lang(tracker)
        lang_event = [SlotSet("language", lang)] if lang else []

        intent = tracker.latest_message.get("intent", {}).get("name", "")

        # Strip prefix: "ask_services_list" → "list", "ask_service_airports" → "airports"
        if intent == "ask_services_list":
            info_type = "list"
        elif intent.startswith("ask_service_"):
            info_type = intent.replace("ask_service_", "")
        else:
            info_type = _infer_service_info_type(tracker.latest_message.get("text", ""))

        data_key = SERVICES_DISPATCH.get(info_type)

        if not data_key or data_key not in SERVICES_INFO:
            dispatcher.utter_message(
                text=translate_response(
                    "I can tell you about **1PAX's services** — airports, urbanism, BIM, "
                    "future mobility, interior design, and more. What would you like to know?",
                    lang,
                )
            )
            return lang_event

        messages = list(SERVICES_INFO[data_key])
        if messages:
            messages[-1] = append_site_link(
                messages[-1],
                SERVICE_LINK_LABELS.get(data_key, "Our Projects"),
                service_url(data_key),
            )

        # Send each message part separately (multi-part responses)
        for msg in messages:
            dispatcher.utter_message(text=translate_response(msg, lang))

        # Append a randomised follow-up prompt for detail pages (not list)
        if info_type != "list":
            follow_up_pool = SERVICES_INFO.get("follow_up", [])
            if follow_up_pool:
                suffix = random.choice(follow_up_pool + ["", ""])   # 2-in-4 chance of no suffix
                if suffix:
                    dispatcher.utter_message(text=translate_response(suffix, lang))

        return lang_event
