"""
1PAX Company Info — Rasa Custom Action
=======================================
Handles all company-info intents (ask_company_*) via a single router action.
Stateless — no slot tracking needed (answers are about the studio, not a specific entity).
"""

import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from .company_data import COMPANY_INFO
from .site_links import append_site_link, company_url
from .translation import get_lang, translate_response


# ── Intent suffix → COMPANY_INFO key ─────────────────────────────────────────

COMPANY_DISPATCH: Dict[str, str] = {
    "overview":       "overview",
    "name":           "name_meaning",
    "mission":        "mission",
    "history":        "history",
    "founder":        "founder",
    "offices":        "offices",
    "team":           "team",
    "expertise":      "expertise",
    "approach":       "approach",
    "human_centered": "human_centered",
    "sustainability": "sustainability",
    "innovation":     "innovation",
    "urbanism":       "urbanism",
    "methodology":    "methodology",
    "clients":        "clients",
    "difference":     "difference",
    "why":            "why_1pax",
    "careers":        "careers",
    "culture":        "culture",
    "mentorship":     "mentorship",
    "open_roles":     "open_roles",
    "values":         "values",
    # ── Ethics & Sustainability pillars ──────────────────────────────────────
    "ethics":         "ethics",
    "social":         "social_commitment",
    "heritage":       "heritage",
    "people_values":  "people_values",
    "diversity":      "diversity",
    "governance":     "governance",
    "suppliers":      "suppliers",
    "ip":             "ip",
    "plan":           "ethics_plan",
    # ── Innovation products ───────────────────────────────────────────────────
    "pax_cart":       "pax_cart",
    "ecoport":        "ecoport",
}

COMPANY_LINK_LABELS: Dict[str, str] = {
    "offices": "Contact and offices",
    "team": "The Team",
    "culture": "The Team",
    "mentorship": "The Team",
    "careers": "Contact 1PAX",
    "open_roles": "Contact 1PAX",
    "pax_cart": "PAX Cart Patent",
    "ecoport": "Ecoport Patent",
    "ip": "Patents",
    "innovation": "Innovation and Research",
    "urbanism": "Urbanism and Masterplan",
}


class ActionAnswerCompanyQuery(Action):
    """Single router for all ask_company_* intents."""

    def name(self) -> Text:
        return "action_answer_company_query"

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

        # Strip prefix: "ask_company_overview" → "overview"
        info_type = intent.replace("ask_company_", "")

        data_key = COMPANY_DISPATCH.get(info_type)

        if not data_key or data_key not in COMPANY_INFO:
            dispatcher.utter_message(
                text=translate_response(
                    "I can tell you about **1PAX** — our mission, design approach, team, "
                    "offices, sustainability commitment, careers, and more. What would you "
                    "like to know?",
                    lang,
                )
            )
            return lang_event

        messages = list(COMPANY_INFO[data_key])
        link_label = COMPANY_LINK_LABELS.get(data_key, "About 1PAX")
        if messages:
            messages[-1] = append_site_link(
                messages[-1],
                link_label,
                company_url(data_key),
            )

        # Send each message part separately (multi-part responses)
        for msg in messages:
            dispatcher.utter_message(text=translate_response(msg, lang))

        # Append a randomised follow-up prompt (not always — empty string weighted in)
        follow_up_pool = COMPANY_INFO.get("follow_up", [])
        if follow_up_pool:
            suffix = random.choice(follow_up_pool + ["", ""])   # 2-in-4 chance of no suffix
            if suffix:
                dispatcher.utter_message(text=translate_response(suffix, lang))

        return lang_event
