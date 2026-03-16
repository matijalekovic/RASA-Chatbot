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

        lang = get_lang(tracker)
        lang_event = [SlotSet("language", lang)] if lang else []

        intent = tracker.latest_message.get("intent", {}).get("name", "")

        # Strip prefix: "ask_services_list" → "list", "ask_service_airports" → "airports"
        if intent == "ask_services_list":
            info_type = "list"
        else:
            info_type = intent.replace("ask_service_", "")

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

        messages = SERVICES_INFO[data_key]

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
