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
from .meeting_prompts import meeting_buttons, meeting_cta_text
from .translation import get_lang, translate_response, translate_responses


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


def _infer_company_info_type(text: str) -> str:
    """Best-effort router for fallback paths when NLU confidence collapses."""
    normalized = text.lower()
    if any(
        token in normalized
        for token in (
            "what do you do",
            "what are you doing",
            "what work do you do",
            "what kind of work do you do",
            "what does your company do",
            "what does the studio do",
            "what is your thing",
        )
    ):
        return "overview"
    if any(token in normalized for token in ("founder", "founded", "mabel", "ceo")):
        return "founder"
    if any(token in normalized for token in ("office", "location", "where are you", "based")):
        return "offices"
    if any(token in normalized for token in ("mission", "purpose")):
        return "mission"
    if any(token in normalized for token in ("history", "heritage", "story")):
        return "history"
    if any(token in normalized for token in ("approach", "method", "process", "work")):
        return "approach"
    if any(token in normalized for token in ("sustainability", "sustainable", "green")):
        return "sustainability"
    if any(token in normalized for token in ("team", "people", "staff")):
        return "team"
    if any(token in normalized for token in ("client", "clients")):
        return "clients"
    if any(token in normalized for token in ("career", "job", "role", "hiring")):
        return "careers"
    if any(token in normalized for token in ("1pax", "company", "studio", "firm", "about")):
        return "overview"
    return ""


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
        if intent.startswith("ask_company_"):
            info_type = intent.replace("ask_company_", "")
        else:
            info_type = _infer_company_info_type(tracker.latest_message.get("text", ""))

        data_key = COMPANY_DISPATCH.get(info_type)

        if not data_key or data_key not in COMPANY_INFO:
            dispatcher.utter_message(
                text=translate_response(
                    "I can tell you about **1PAX** — our mission, design approach, team, "
                    "offices, sustainability commitment, careers, and more. What would you "
                    "like to know?",
                    lang,
                ),
                buttons=meeting_buttons(lang),
            )
            return lang_event

        output_parts = list(COMPANY_INFO[data_key])

        # Append a randomised follow-up prompt (not always — empty string weighted in)
        follow_up_pool = COMPANY_INFO.get("follow_up", [])
        if follow_up_pool and not lang:
            suffix = random.choice(follow_up_pool + ["", ""])   # 2-in-4 chance of no suffix
            if suffix:
                output_parts.append(suffix)

        meeting_cta_index = None
        if data_key in {"overview", "offices", "approach", "clients", "careers"}:
            meeting_cta_index = len(output_parts)
            output_parts.append(meeting_cta_text("company"))

        # Send each message part separately, but translate them in one batch.
        for index, msg in enumerate(translate_responses(output_parts, lang)):
            if index == meeting_cta_index:
                dispatcher.utter_message(text=msg, buttons=meeting_buttons(lang))
            else:
                dispatcher.utter_message(text=msg)

        return lang_event
