"""
1PAX Company Info — Rasa Custom Action
=======================================
Handles all company-info intents (ask_company_*) via a single router action.
Stateless — no slot tracking needed (answers are about the studio, not a specific entity).
"""

import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from .company_data import COMPANY_INFO


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

        intent = tracker.latest_message.get("intent", {}).get("name", "")

        # Strip prefix: "ask_company_overview" → "overview"
        info_type = intent.replace("ask_company_", "")

        data_key = COMPANY_DISPATCH.get(info_type)

        if not data_key or data_key not in COMPANY_INFO:
            dispatcher.utter_message(
                text=(
                    "I can tell you about **1PAX** — our mission, design approach, team, "
                    "offices, sustainability commitment, careers, and more. What would you "
                    "like to know?"
                )
            )
            return []

        messages = COMPANY_INFO[data_key]

        # Send each message part separately (multi-part responses)
        for msg in messages:
            dispatcher.utter_message(text=msg)

        # Append a randomised follow-up prompt (not always — empty string weighted in)
        follow_up_pool = COMPANY_INFO.get("follow_up", [])
        if follow_up_pool:
            suffix = random.choice(follow_up_pool + ["", ""])   # 2-in-4 chance of no suffix
            if suffix:
                dispatcher.utter_message(text=suffix)

        return []
