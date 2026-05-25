"""Shared meeting-scheduling prompts and quick-reply buttons."""

from typing import Dict, List, Optional


MEETING_REQUEST_TEXT = "I would like to schedule a meeting."

_MEETING_BUTTON_TITLES = {
    "FR": "Planifier un rendez-vous",
    "ES": "Agendar una reunión",
    "PT": "Agendar uma reunião",
    "PT-PT": "Agendar uma reunião",
    "PT-BR": "Agendar uma reunião",
    "ZH": "预约会议",
    "ZH-HANS": "预约会议",
    "ZH-HANT": "預約會議",
    "SR": "Zakazati sastanak",
}

_MEETING_CTA_TEXT = {
    "default": "If you would like to discuss this with 1PAX, I can also help schedule a meeting.",
    "project": "If this project is close to something you are planning, I can help schedule a meeting with 1PAX.",
    "services": "If you would like to discuss which service fits your project, I can help schedule a meeting with 1PAX.",
    "team": "If you would like to speak with the studio directly, I can help schedule a meeting with 1PAX.",
    "company": "If you would like to continue the conversation with 1PAX, I can help schedule a meeting.",
}


def meeting_buttons(lang: Optional[str] = None) -> List[Dict[str, str]]:
    lang_key = (lang or "").upper()
    base_lang = lang_key.split("-")[0]
    title = (
        _MEETING_BUTTON_TITLES.get(lang_key)
        or _MEETING_BUTTON_TITLES.get(base_lang)
        or "Schedule a meeting"
    )
    return [{"title": title, "payload": MEETING_REQUEST_TEXT}]


def meeting_cta_text(context: str = "default") -> str:
    return _MEETING_CTA_TEXT.get(context, _MEETING_CTA_TEXT["default"])
