"""
Calendly scheduling flow for the 1PAX chatbot.

The flow is intentionally action-driven, matching the rest of this bot:
collect name/email/meeting purpose/time preference, inspect the hosted Calendly
page for available slots, ask for confirmation, then submit the hosted Calendly
form through browser automation.
"""

import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict, List, Optional, Text, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from . import google_calendar_scheduler as gcal
from .translation import get_lang, translate_response


logger = logging.getLogger(__name__)

_DEFAULT_TIMEZONE = "Europe/Belgrade"
_MAX_RANGE_DAYS = 7

_SCHEDULE_SLOTS = [
    "schedule_stage",
    "schedule_name",
    "schedule_email",
    "schedule_purpose",
    "schedule_time_preference",
    "schedule_timezone",
    "schedule_offered_slots",
    "schedule_selected_slot",
    "schedule_selected_slot_label",
    "schedule_detected_language",
    "schedule_region",
    "schedule_region_label",
    "schedule_colleague_id",
    "schedule_colleague_label",
    "schedule_colleague_office",
    "schedule_colleague_timezone",
    "schedule_colleague_calendar_id",
    "schedule_colleague_options",
    "schedule_booking_event_id",
    "schedule_booking_meet_link",
]

_WEEKDAYS = {
    "monday": 0,
    "mon": 0,
    "tuesday": 1,
    "tue": 1,
    "tues": 1,
    "wednesday": 2,
    "wed": 2,
    "thursday": 3,
    "thu": 3,
    "thurs": 3,
    "friday": 4,
    "fri": 4,
    "saturday": 5,
    "sat": 5,
    "sunday": 6,
    "sun": 6,
}

_MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}

_SR_WEEKDAYS = [
    "Ponedeljak",
    "Utorak",
    "Sreda",
    "Četvrtak",
    "Petak",
    "Subota",
    "Nedelja",
]

_SR_MONTHS = [
    "",
    "januar",
    "februar",
    "mart",
    "april",
    "maj",
    "jun",
    "jul",
    "avgust",
    "septembar",
    "oktobar",
    "novembar",
    "decembar",
]

_SLOT_WORD_TO_NUMBER = {
    "one": 1,
    "first": 1,
    "two": 2,
    "second": 2,
    "three": 3,
    "third": 3,
    "four": 4,
    "fourth": 4,
    "five": 5,
    "fifth": 5,
    "six": 6,
    "sixth": 6,
    "seven": 7,
    "seventh": 7,
    "eight": 8,
    "eighth": 8,
    "nine": 9,
    "ninth": 9,
    "ten": 10,
    "tenth": 10,
    "jedan": 1,
    "jedna": 1,
    "jedno": 1,
    "prvi": 1,
    "prva": 1,
    "prvo": 1,
    "dva": 2,
    "dve": 2,
    "drugi": 2,
    "druga": 2,
    "drugo": 2,
    "tri": 3,
    "treci": 3,
    "treca": 3,
    "trece": 3,
    "cetiri": 4,
    "cetvrti": 4,
    "cetvrta": 4,
    "cetvrto": 4,
    "pet": 5,
    "peti": 5,
    "peta": 5,
    "peto": 5,
    "sest": 6,
    "sesti": 6,
    "sesta": 6,
    "sesto": 6,
    "sedam": 7,
    "sedmi": 7,
    "sedma": 7,
    "sedmo": 7,
    "osam": 8,
    "osmi": 8,
    "osma": 8,
    "osmo": 8,
    "devet": 9,
    "deveti": 9,
    "deveta": 9,
    "deveto": 9,
    "deset": 10,
    "deseti": 10,
    "deseta": 10,
    "deseto": 10,
}


@dataclass(frozen=True)
class CalendlyConfig:
    scheduling_link: str
    access_token: str
    event_type_uri: str
    location_kind: str
    allow_link_fallback: bool
    allow_confirmation_link_fallback: bool
    browser_fallback: bool
    browser_headless: bool
    browser_timeout_seconds: int
    browser_executable_path: str
    default_timezone: str
    max_slots: int

    @property
    def is_connected(self) -> bool:
        return bool(self.scheduling_link)

    @property
    def availability_api_connected(self) -> bool:
        return bool(self.access_token and self.event_type_uri)


class CalendlyAutomationError(RuntimeError):
    """Raised when hosted-page automation cannot reach Calendly."""

    def __init__(
        self,
        message: str,
        status: Optional[int] = None,
        detail: Optional[str] = None,
    ):
        super().__init__(message)
        self.status = status
        self.detail = detail


def _config_from_env() -> CalendlyConfig:
    try:
        max_slots = int(os.environ.get("CALENDLY_MAX_SLOTS", "5"))
    except ValueError:
        max_slots = 5

    try:
        browser_timeout_seconds = int(
            os.environ.get("CALENDLY_BROWSER_TIMEOUT_SECONDS", "45")
        )
    except ValueError:
        browser_timeout_seconds = 45

    scheduling_link = (
        os.environ.get("CALENDLY_SCHEDULING_LINK", "").strip()
        or os.environ.get("CALENDLY_SCHEDULING_URL", "").strip()
    )
    access_token = os.environ.get("CALENDLY_ACCESS_TOKEN", "").strip()
    event_type_uri = os.environ.get("CALENDLY_EVENT_TYPE_URI", "").strip()
    location_kind = os.environ.get("CALENDLY_LOCATION_KIND", "").strip()
    allow_link_fallback = _env_bool(
        "CALENDLY_ALLOW_LINK_FALLBACK",
        default=bool(scheduling_link),
    ) or _env_bool("CALENDLY_ENABLE_LINK_FALLBACK")
    allow_confirmation_link_fallback = _env_bool(
        "CALENDLY_ALLOW_CONFIRMATION_LINK_FALLBACK",
        default=False,
    )

    browser_fallback = (
        _env_bool(
            "CALENDLY_BROWSER_FALLBACK",
            default=bool(scheduling_link),
        )
        or _env_bool("CALENDLY_AUTOMATE_FALLBACK")
    )

    return CalendlyConfig(
        scheduling_link=scheduling_link,
        access_token=access_token,
        event_type_uri=event_type_uri,
        location_kind=location_kind,
        allow_link_fallback=allow_link_fallback,
        allow_confirmation_link_fallback=allow_confirmation_link_fallback,
        browser_fallback=browser_fallback,
        browser_headless=not _env_flag("CALENDLY_BROWSER_HEADFUL"),
        browser_timeout_seconds=max(5, min(browser_timeout_seconds, 120)),
        browser_executable_path=os.environ.get(
            "CALENDLY_BROWSER_EXECUTABLE_PATH",
            "",
        ).strip(),
        default_timezone=os.environ.get(
            "CALENDLY_DEFAULT_TIMEZONE",
            _DEFAULT_TIMEZONE,
        ).strip() or _DEFAULT_TIMEZONE,
        max_slots=max(1, min(max_slots, 10)),
    )


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return ZoneInfo(_DEFAULT_TIMEZONE)


def _user_timezone(tracker: Tracker, cfg: CalendlyConfig) -> str:
    metadata = tracker.latest_message.get("metadata") or {}
    for key in ("timezone", "time_zone", "tz"):
        value = (metadata.get(key) or "").strip()
        if value:
            return value

    slot_value = tracker.get_slot("schedule_timezone")
    if slot_value:
        return slot_value

    return cfg.default_timezone


def _lang_event(lang: Optional[str]) -> List[SlotSet]:
    return [SlotSet("language", lang)] if lang else []


def _clear_schedule_events() -> List[SlotSet]:
    return [SlotSet(slot, None) for slot in _SCHEDULE_SLOTS]


def _set_stage(stage: str) -> List[SlotSet]:
    return [SlotSet("schedule_stage", stage)]


def _lang_code(lang: Optional[str]) -> str:
    return (lang or "").upper()


def _is_sr(lang: Optional[str]) -> bool:
    return _lang_code(lang) == "SR"


def _ascii_norm(value: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    ).lower()


def _sr_scheduler_text(text: str) -> Optional[str]:
    exact = {
        "No problem. I will leave the meeting scheduling there.": (
            "Nema problema. Zaustaviću zakazivanje sastanka."
        ),
        "Of course. I can help schedule a meeting with 1PAX. What name should I put on the invite?": (
            "Naravno. Mogu da pomognem oko zakazivanja sastanka sa 1PAX-om. "
            "Koje ime da stavim na pozivnicu?"
        ),
        "What is the purpose of the meeting? A short note is enough, for example: project consultation, partnership, proposal, careers, press, or a general introduction.": (
            "Koji je povod sastanka? Dovoljna je kratka napomena, na primer: "
            "konsultacije o projektu, partnerstvo, ponuda, karijera, mediji ili opšte upoznavanje."
        ),
        "Great. When would you like to meet? You can say *tomorrow afternoon*, *next Tuesday morning*, or *any time next week*.": (
            "Odlično. Kada biste želeli sastanak? Možete reći *sutra popodne*, "
            "*sledećeg utorka ujutru* ili *bilo kada sledeće nedelje*."
        ),
        "I did not catch which time you wanted. Please reply with one of the numbers, or tell me another day/time.": (
            "Nisam razumeo koje vreme želite. Molim vas odgovorite jednim od brojeva, "
            "ili mi recite drugi dan/vreme."
        ),
        "I lost the selected time. Let me show the available slots again.": (
            "Izgubio sam izabrani termin. Prikazaću dostupne termine ponovo."
        ),
        "Please reply yes to book that time, or no to cancel.": (
            "Odgovorite da za rezervaciju tog termina, ili ne za otkazivanje."
        ),
        "Calendly could not complete the booking inside the chat right now. Please choose another time, or try again shortly.": (
            "Calendly trenutno ne može da završi rezervaciju u chatu. "
            "Molim vas izaberite drugi termin ili pokušajte ponovo uskoro."
        ),
        "I could not automate the Calendly booking page right now. Please choose another time, or try again shortly.": (
            "Trenutno nisam mogao automatski da završim Calendly rezervaciju. "
            "Molim vas izaberite drugi termin ili pokušajte ponovo uskoro."
        ),
        "I can help schedule meetings, but the Calendly booking link is not configured yet.": (
            "Mogu da pomognem oko zakazivanja sastanaka, ali Calendly link za "
            "rezervaciju još nije podešen."
        ),
        "I could not find open Calendly times in that window. Try another option, like *tomorrow morning* or *next week*.": (
            "Nisam pronašao slobodne Calendly termine u tom periodu. "
            "Pokušajte drugu opciju, na primer *sutra ujutru* ili *sledeće nedelje*."
        ),
        "I could not find times in that exact part of the day, but these nearby options are open.": (
            "Nisam pronašao termine baš u tom delu dana, ali ovi bliski termini su dostupni."
        ),
    }
    if text in exact:
        return exact[text]

    if text.startswith("Thanks, ") and "What email address should Calendly send the invitation to?" in text:
        name = text.removeprefix("Thanks, ").split(".", 1)[0]
        return f"Hvala, {name}. Na koju email adresu Calendly treba da pošalje pozivnicu?"

    if text.startswith("Calendly could not be reached right now. Please try again shortly."):
        fallback = ""
        match = re.search(r"\[Schedule a meeting\]\(([^)]+)\)", text)
        if match:
            fallback = f"\n\nMožete zakazati i direktno ovde: [Zakažite sastanak]({match.group(1)})"
        return f"Calendly trenutno nije dostupan. Molim vas pokušajte ponovo uskoro.{fallback}"

    if text.startswith("I can help with meetings, but live Calendly booking is not connected inside the chat yet."):
        match = re.search(r"\[Schedule a meeting\]\(([^)]+)\)", text)
        if match:
            return (
                "Mogu da pomognem oko sastanaka, ali zakazivanje uživo preko Calendlyja "
                "trenutno nije povezano u chatu. Možete zakazati direktno ovde: "
                f"[Zakažite sastanak]({match.group(1)})"
            )

    if text.startswith("I can help schedule meetings, but direct Calendly booking is not connected"):
        return (
            "Mogu da pomognem oko zakazivanja sastanaka, ali direktno Calendly zakazivanje "
            "trenutno nije povezano u chatu."
        )

    return None


def _utter(
    dispatcher: CollectingDispatcher,
    text: str,
    lang: Optional[str],
    already_localized: bool = False,
    buttons: Optional[List[Dict[str, str]]] = None,
) -> None:
    if _is_sr(lang) and not already_localized:
        sr_text = _sr_scheduler_text(text)
        if sr_text:
            dispatcher.utter_message(text=sr_text, buttons=buttons)
            return

    dispatcher.utter_message(
        text=text if already_localized else translate_response(text, lang),
        buttons=buttons,
    )


def _extract_email(text: str) -> Optional[str]:
    match = re.search(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        text,
        flags=re.IGNORECASE,
    )
    return match.group(0).lower() if match else None


def _clean_purpose(raw: str) -> Optional[str]:
    value = re.sub(r"\s+", " ", raw).strip(" .,;:!?")
    if not value or len(value) < 3:
        return None
    if len(value) > 500:
        value = value[:500].rstrip()

    lowered = value.lower()
    blocked = {
        "yes",
        "no",
        "confirm",
        "cancel",
        "book it",
        "go ahead",
        "tomorrow",
        "today",
        "next week",
    }
    if lowered in blocked:
        return None
    if _extract_email(value):
        return None
    return value


def _extract_purpose(text: str, stage: Optional[str]) -> Optional[str]:
    if stage == "collect_purpose":
        return _clean_purpose(text)

    patterns = [
        r"\b(?:purpose|intent|reason)\s+(?:is|for the meeting is)\s+(.+)",
        r"\b(?:meeting is|call is)\s+(?:about|regarding)\s+(.+)",
        r"\b(?:to discuss|about|regarding)\s+(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _clean_purpose(match.group(1))
    return None


def _clean_name(raw: str) -> Optional[str]:
    value = re.sub(r"\s+", " ", raw).strip(" .,;:!?")
    value = re.split(r"\s+(?:and|email|e-mail|mail)\b", value, maxsplit=1)[0]
    value = value.strip(" .,;:!?")
    if not value or "@" in value:
        return None
    if len(value) < 2 or len(value) > 80:
        return None
    if not re.search(r"[A-Za-z]", value):
        return None
    low = value.lower()
    blocked = {
        "yes",
        "no",
        "confirm",
        "cancel",
        "tomorrow",
        "today",
        "next week",
        "this week",
    }
    if low in blocked:
        return None
    return value


def _extract_name(text: str, stage: Optional[str]) -> Optional[str]:
    email = _extract_email(text)
    text_without_email = text.replace(email, " ") if email else text

    patterns = [
        r"\bmy name is\s+(.+)",
        r"\bname is\s+(.+)",
        r"\bi am\s+(.+)",
        r"\bi'm\s+(.+)",
        r"\bthis is\s+(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text_without_email, flags=re.IGNORECASE)
        if match:
            return _clean_name(match.group(1))

    if stage == "collect_name":
        return _clean_name(text_without_email)

    return None


def _has_time_words(text: str) -> bool:
    lowered = _ascii_norm(text)
    signals = {
        "today",
        "tomorrow",
        "week",
        "morning",
        "afternoon",
        "evening",
        "noon",
        "lunch",
        "night",
        "anytime",
        "any time",
        "after",
        "before",
        "between",
    }
    if any(signal in lowered for signal in signals):
        return True
    if any(day in lowered for day in _WEEKDAYS):
        return True
    if any(month in lowered for month in _MONTHS):
        return True
    return bool(_time_window(lowered))


def _extract_time_preference(text: str, stage: Optional[str]) -> Optional[str]:
    stripped = text.strip()
    if not stripped:
        return None
    if stage == "collect_time":
        return stripped
    return stripped if _has_time_words(stripped) else None


def _is_affirmation(text: str) -> bool:
    lowered = text.lower().strip(" .!?,")
    if lowered in {"yes", "y", "yeah", "yep", "sure", "ok", "okay", "confirm", "da"}:
        return True
    return any(
        phrase in lowered
        for phrase in (
            "book it",
            "confirm it",
            "that works",
            "please book",
            "go ahead",
            "sounds good",
        )
    )


def _is_cancel(text: str, intent: str, stage: Optional[str]) -> bool:
    lowered = text.lower().strip(" .!?,")
    if not lowered:
        return False

    explicit_cancel_phrases = (
        "cancel",
        "no thanks",
        "not now",
        "never mind",
        "nevermind",
        "stop",
        "forget it",
        "leave it",
        "do not schedule",
        "don't schedule",
        "do not book",
        "don't book",
        "do not want to book",
        "don't want to book",
        "changed my mind",
        "otkazi",
        "otkaži",
    )
    if any(phrase in lowered for phrase in explicit_cancel_phrases):
        return True

    return stage in {"select_slot", "confirm"} and lowered in {"no", "ne"}


def _scheduling_provider() -> str:
    return (
        os.environ.get("SCHEDULING_PROVIDER")
        or os.environ.get("MEETING_SCHEDULING_PROVIDER")
        or "google"
    ).strip().lower()


def _google_calendar_config() -> gcal.GoogleCalendarConfig:
    return gcal.config_from_env()


def _google_calendar_client(cfg: gcal.GoogleCalendarConfig) -> gcal.GoogleCalendarClient:
    return gcal.GoogleCalendarClient(cfg)


def _route_confirmation_buttons(
    colleague: gcal.CalendarColleague,
    lang: Optional[str],
) -> List[Dict[str, str]]:
    base = (_lang_code(lang).split("-", 1)[0] or "EN").upper()
    labels = {
        "ES": ("Sí, usar esta oficina", "Ver otras oficinas"),
        "ZH": ("是的，使用这个办公室", "查看其他办公室"),
        "FR": ("Oui, utiliser ce bureau", "Voir d'autres bureaux"),
        "SR": ("Da, ova kancelarija", "Prikaži druge opcije"),
    }
    yes, other = labels.get(base, ("Yes, use this office", "Show other offices"))
    return [
        {
            "title": yes,
            "payload": f"Yes, schedule with {colleague.office}",
        },
        {
            "title": other,
            "payload": "Show other scheduling options",
        },
    ]


def _colleague_option_buttons(
    options: List[gcal.CalendarColleague],
) -> List[Dict[str, str]]:
    return [
        {
            "title": f"{idx}. {colleague.office}",
            "payload": f"Use option {idx}: {colleague.office}",
        }
        for idx, colleague in enumerate(options[:5], start=1)
    ]


def _route_confirmation_text(
    context: gcal.SchedulingContext,
    colleague: gcal.CalendarColleague,
) -> str:
    languages = ", ".join(lang.upper() for lang in colleague.languages)
    return (
        "Based on your language, region, and timezone, I suggest scheduling "
        f"this with **{colleague.display_name}**.\n\n"
        f"Office: **{colleague.office}**\n"
        f"Timezone: **{colleague.timezone}**\n"
        f"Languages: **{languages}**\n"
        f"Detected region: **{context.region_label}**\n\n"
        "Does this work for you?"
    )


def _route_options_text(options: List[gcal.CalendarColleague]) -> str:
    lines = ["Of course. Please choose the office or colleague you prefer:"]
    for idx, colleague in enumerate(options[:5], start=1):
        languages = ", ".join(lang.upper() for lang in colleague.languages)
        lines.append(
            f"{idx}. **{colleague.display_name}** — {colleague.timezone}; {languages}"
        )
    lines.append("")
    lines.append("Reply with a number, office, or colleague name.")
    return "\n".join(lines)


def _is_route_rejection(text: str) -> bool:
    lowered = (text or "").lower().strip(" .!?,")
    if lowered in {"no", "ne", "not that one", "another", "other"}:
        return True
    return any(
        phrase in lowered
        for phrase in (
            "other option",
            "other office",
            "show other",
            "someone else",
            "different colleague",
            "different office",
            "not this",
            "not that",
        )
    )


def _google_context_events(
    context: gcal.SchedulingContext,
    colleague: Optional[gcal.CalendarColleague] = None,
    options: Optional[List[gcal.CalendarColleague]] = None,
) -> List[SlotSet]:
    events: List[SlotSet] = [
        SlotSet("schedule_detected_language", context.language),
        SlotSet("schedule_region", context.region),
        SlotSet("schedule_region_label", context.region_label),
    ]
    if colleague:
        events.extend(
            [
                SlotSet("schedule_colleague_id", colleague.id),
                SlotSet("schedule_colleague_label", colleague.label),
                SlotSet("schedule_colleague_office", colleague.office),
                SlotSet("schedule_colleague_timezone", colleague.timezone),
                SlotSet("schedule_colleague_calendar_id", colleague.calendar_id),
            ]
        )
    if options:
        events.append(SlotSet("schedule_colleague_options", gcal.colleague_options_payload(options)))
    return events


def _google_slot_dict(slot: gcal.CalendarSlot) -> Dict[str, str]:
    return {
        "start_time": slot.start_time,
        "end_time": slot.end_time,
        "calendar_id": slot.calendar_id,
        "colleague_id": slot.colleague_id,
        "colleague_label": slot.colleague_label,
        "colleague_office": slot.colleague_office,
        "colleague_timezone": slot.colleague_timezone,
        "label": slot.label,
    }


def _google_colleague_from_slots(
    cfg: gcal.GoogleCalendarConfig,
    tracker: Tracker,
) -> Optional[gcal.CalendarColleague]:
    return gcal.colleague_by_id(cfg.roster, tracker.get_slot("schedule_colleague_id"))


def _google_available_slots(
    cfg: gcal.GoogleCalendarConfig,
    colleague: gcal.CalendarColleague,
    preference: str,
    timezone_name: str,
    lang: Optional[str],
) -> Tuple[List[Dict[str, str]], bool]:
    tz = _zone(timezone_name)
    start, end = _date_range_for_preference(preference, tz)
    if end - start > timedelta(days=_MAX_RANGE_DAYS):
        end = start + timedelta(days=_MAX_RANGE_DAYS)

    client = _google_calendar_client(cfg)
    slots, matched = gcal.available_slots(
        cfg=cfg,
        client=client,
        colleague=colleague,
        range_start=start,
        range_end=end,
        visitor_timezone=timezone_name,
        preferred_time_window=_time_window(preference),
        label_formatter=lambda start_time, display_tz: _slot_label(
            start_time,
            display_tz,
            lang,
        ),
    )
    return [_google_slot_dict(slot) for slot in slots], matched


def _google_booking_success_message(
    email: str,
    purpose: str,
    selected_label: Optional[str],
    colleague: gcal.CalendarColleague,
    booking: gcal.CalendarBooking,
    lang: Optional[str] = None,
) -> str:
    dry_note = " This was created in dry-run mode." if booking.dry_run else ""
    if _is_sr(lang):
        lines = [
            f"Sastanak je zakazan: **{selected_label}**.",
            f"Domaćin: **{colleague.display_name}**.",
            f"Google Calendar će poslati pozivnicu na **{email}**.",
            f"Povod: **{purpose}**.{dry_note}",
        ]
        if booking.meet_link:
            lines.append(f"Google Meet: {booking.meet_link}")
        if booking.html_link:
            lines.append(f"Calendar event: {booking.html_link}")
        return "\n\n".join(lines)

    lines = [
        f"You're booked: **{selected_label}**.",
        f"Host: **{colleague.display_name}**.",
        f"Google Calendar will send the invitation to **{email}**.",
        f"Purpose: **{purpose}**.{dry_note}",
    ]
    if booking.meet_link:
        lines.append(f"Google Meet: {booking.meet_link}")
    if booking.html_link:
        lines.append(f"Calendar event: {booking.html_link}")
    return "\n\n".join(lines)


def _book_google_calendar_event(
    cfg: gcal.GoogleCalendarConfig,
    colleague: gcal.CalendarColleague,
    name: str,
    email: str,
    purpose: str,
    selected_slot: str,
    selected_end: Optional[str],
    timezone_name: str,
) -> gcal.CalendarBooking:
    client = _google_calendar_client(cfg)
    start = _parse_calendly_dt(selected_slot)
    end = (
        _parse_calendly_dt(selected_end)
        if selected_end
        else start + timedelta(minutes=cfg.event_duration_minutes)
    )

    calendar_id = colleague.calendar_id or f"dryrun:{colleague.id}"
    busy = client.freebusy([calendar_id], start, end).get(calendar_id, [])
    if busy:
        raise gcal.GoogleCalendarError("That time was just booked. Please choose another slot.")

    return client.create_event(
        colleague=colleague,
        start=start,
        end=end,
        name=name,
        email=email,
        purpose=purpose,
        timezone_name=timezone_name,
    )


def _looks_like_content_shift_while_scheduling(text: str, stage: Optional[str]) -> bool:
    """Detect when a user abandons early scheduling prompts to ask about 1PAX."""
    if stage not in {"collect_name", "collect_email"}:
        return False

    lowered = (text or "").lower().strip()
    if not lowered:
        return False

    if _extract_email(lowered) or _has_time_words(lowered):
        return False

    starters = (
        "what ",
        "who ",
        "where ",
        "when ",
        "which ",
        "how ",
        "tell me",
        "show me",
        "list ",
        "do you",
        "does 1pax",
        "can you",
        "i want to know",
    )
    content_terms = (
        "1pax",
        "company",
        "studio",
        "firm",
        "project",
        "projects",
        "portfolio",
        "airport",
        "terminal",
        "metro",
        "station",
        "team",
        "people",
        "member",
        "service",
        "services",
        "design",
        "hospital",
        "hospitals",
        "healthcare",
        "budget",
        "capacity",
        "client",
        "location",
        "located",
        "founder",
        "mabel",
        "office",
        "offices",
        "mission",
        "sustainability",
        "urbanism",
        "bim",
        "vertiport",
    )
    return any(lowered.startswith(starter) for starter in starters) and any(
        term in lowered for term in content_terms
    )


def schedule_topic_shift_events(tracker: Tracker) -> List[SlotSet]:
    """Clear a partial booking flow when the latest message changes topic."""
    stage = tracker.get_slot("schedule_stage")
    text = tracker.latest_message.get("text") or ""
    if _looks_like_content_shift_while_scheduling(text, stage):
        return _clear_schedule_events()
    return []


def _parse_date_value(raw: str, today: date) -> Optional[date]:
    text = _ascii_norm(raw)

    iso_match = re.search(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", text)
    if iso_match:
        try:
            parsed = date(
                int(iso_match.group(1)),
                int(iso_match.group(2)),
                int(iso_match.group(3)),
            )
            return parsed if parsed >= today else None
        except ValueError:
            return None

    dotted_match = re.search(
        r"\b(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?\b",
        text,
    )
    if dotted_match:
        day = int(dotted_match.group(1))
        month = int(dotted_match.group(2))
        raw_year = dotted_match.group(3)
        year = int(raw_year) if raw_year else today.year
        if year < 100:
            year += 2000
        try:
            parsed = date(year, month, day)
            if parsed < today and raw_year is None:
                parsed = date(year + 1, month, day)
            return parsed if parsed >= today else None
        except ValueError:
            return None

    month_names = "|".join(sorted(_MONTHS, key=len, reverse=True))
    month_first = re.search(
        rf"\b({month_names})\s+(\d{{1,2}})(?:st|nd|rd|th|\.)?(?:,\s*(\d{{4}}))?\b",
        text,
    )
    day_first = re.search(
        rf"\b(\d{{1,2}})(?:st|nd|rd|th|\.)?\s+({month_names})(?:\s+(\d{{4}}))?\b",
        text,
    )

    month = day = year = None
    if month_first:
        month = _MONTHS[month_first.group(1)]
        day = int(month_first.group(2))
        year = int(month_first.group(3) or today.year)
    elif day_first:
        day = int(day_first.group(1))
        month = _MONTHS[day_first.group(2)]
        year = int(day_first.group(3) or today.year)

    if month and day and year:
        try:
            parsed = date(year, month, day)
            if parsed < today and year == today.year:
                parsed = date(year + 1, month, day)
            return parsed if parsed >= today else None
        except ValueError:
            return None

    return None


def _date_range_for_preference(
    preference: str,
    tz: ZoneInfo,
) -> Tuple[datetime, datetime]:
    now = datetime.now(tz)
    lowered = _ascii_norm(preference)

    parsed_date = _parse_date_value(lowered, now.date())
    if parsed_date:
        start = datetime.combine(parsed_date, time.min, tzinfo=tz)
        end = start + timedelta(days=1)
        return _ensure_future_range(start, end, now)

    if "tomorrow" in lowered:
        start_date = now.date() + timedelta(days=1)
        start = datetime.combine(start_date, time.min, tzinfo=tz)
        return start, start + timedelta(days=1)

    if "today" in lowered:
        start = now + timedelta(minutes=10)
        end = datetime.combine(now.date() + timedelta(days=1), time.min, tzinfo=tz)
        return _ensure_future_range(start, end, now)

    if "next week" in lowered:
        days_until_monday = (7 - now.weekday()) % 7
        days_until_monday = 7 if days_until_monday == 0 else days_until_monday
        start_date = now.date() + timedelta(days=days_until_monday)
        start = datetime.combine(start_date, time.min, tzinfo=tz)
        return start, start + timedelta(days=_MAX_RANGE_DAYS)

    if "this week" in lowered:
        start = now + timedelta(minutes=10)
        days_until_next_monday = 7 - now.weekday()
        end_date = now.date() + timedelta(days=days_until_next_monday)
        end = datetime.combine(end_date, time.min, tzinfo=tz)
        return _ensure_future_range(start, end, now)

    for word, weekday in _WEEKDAYS.items():
        if re.search(rf"\b{re.escape(word)}\b", lowered):
            has_next = bool(
                re.search(rf"\bnext\s+{re.escape(word)}\b", lowered)
                or re.search(rf"\b{re.escape(word)}\s+next\b", lowered)
            )
            has_this = bool(
                re.search(rf"\bthis\s+{re.escape(word)}\b", lowered)
                or re.search(rf"\b{re.escape(word)}\s+this\b", lowered)
            )
            delta = (weekday - now.weekday()) % 7
            if has_next or (delta == 0 and not has_this):
                delta = 7
            start_date = now.date() + timedelta(days=delta)
            start = datetime.combine(start_date, time.min, tzinfo=tz)
            return _ensure_future_range(start, start + timedelta(days=1), now)

    start = now + timedelta(minutes=10)
    end = start + timedelta(days=_MAX_RANGE_DAYS)
    return _ensure_future_range(start, end, now)


def _ensure_future_range(
    start: datetime,
    end: datetime,
    now: datetime,
) -> Tuple[datetime, datetime]:
    if start <= now:
        start = now + timedelta(minutes=10)
    if end <= start:
        end = start + timedelta(days=1)
    if end - start > timedelta(days=_MAX_RANGE_DAYS):
        end = start + timedelta(days=_MAX_RANGE_DAYS)
    return start, end


def _coerce_time_minutes(
    hour: int,
    minute: int,
    meridiem: str,
    preference: str,
) -> Optional[int]:
    if minute < 0 or minute > 59:
        return None
    meridiem = meridiem.lower().replace(".", "")
    if meridiem in {"pm", "p"} and hour < 12:
        hour += 12
    elif meridiem in {"am", "a"} and hour == 12:
        hour = 0
    elif not meridiem and 1 <= hour <= 7 and "morning" not in preference:
        hour += 12
    if hour < 0 or hour > 23:
        return None
    return hour * 60 + minute


def _bounded_window(start: int, end: int) -> Optional[Tuple[int, int]]:
    start = max(0, min(start, 24 * 60))
    end = max(0, min(end, 24 * 60))
    if end <= start:
        return None
    return start, end


def _exact_time_window(preference: str) -> Optional[Tuple[int, int]]:
    range_match = re.search(
        r"\b(?:between|from|od|entre|de)\s+"
        r"(\d{1,2})(?::([0-5]\d))?\s*(am|pm|a\.m\.|p\.m\.)?\s+"
        r"(?:and|to|do|a|e|y|et)\s+"
        r"(\d{1,2})(?::([0-5]\d))?\s*(am|pm|a\.m\.|p\.m\.)?\b",
        preference,
    )
    if range_match:
        start_meridiem = range_match.group(3) or range_match.group(6) or ""
        end_meridiem = range_match.group(6) or range_match.group(3) or ""
        start = _coerce_time_minutes(
            int(range_match.group(1)),
            int(range_match.group(2) or 0),
            start_meridiem,
            preference,
        )
        end = _coerce_time_minutes(
            int(range_match.group(4)),
            int(range_match.group(5) or 0),
            end_meridiem,
            preference,
        )
        if start is not None and end is not None and end > start:
            return _bounded_window(start, end)

    h_match = re.search(
        r"\b(?:(at|around|about|after|before|from|by|u|oko|posle|poslije|pre|"
        r"prije|depois|antes|vers|apres|avant|a\s+las|as)\s+)?"
        r"(\d{1,2})h([0-5]\d)?\b",
        preference,
    )
    if h_match:
        minute = _coerce_time_minutes(
            int(h_match.group(2)),
            int(h_match.group(3) or 0),
            "",
            preference,
        )
        if minute is not None:
            marker = h_match.group(1) or ""
            return _window_for_time_marker(marker, minute)

    time_match = re.search(
        r"\b(?:(at|around|about|after|before|from|by|u|oko|posle|poslije|pre|"
        r"prije|depois|antes|vers|apres|avant|a\s+las|as)\s+)?"
        r"(\d{1,2})(?::([0-5]\d))?\s*(am|pm|a\.m\.|p\.m\.)?\b",
        preference,
    )
    if not time_match:
        return None

    marker = time_match.group(1) or ""
    has_explicit_time = bool(marker or time_match.group(3) or time_match.group(4))
    if not has_explicit_time:
        return None

    minute = _coerce_time_minutes(
        int(time_match.group(2)),
        int(time_match.group(3) or 0),
        time_match.group(4) or "",
        preference,
    )
    if minute is None:
        return None
    return _window_for_time_marker(marker, minute)


def _window_for_time_marker(marker: str, minute: int) -> Optional[Tuple[int, int]]:
    marker = (marker or "").strip()
    if marker in {"after", "from", "posle", "poslije", "depois", "apres"}:
        return _bounded_window(minute, 24 * 60)
    if marker in {"before", "by", "pre", "prije", "antes", "avant"}:
        return _bounded_window(0, minute)
    if marker in {"around", "about", "oko", "vers"}:
        return _bounded_window(minute - 30, minute + 31)
    return _bounded_window(minute, minute + 1)


def _time_window(preference: str) -> Optional[Tuple[int, int]]:
    lowered = _ascii_norm(preference)
    exact = _exact_time_window(lowered)
    if exact:
        return exact
    if "before noon" in lowered:
        return 8 * 60, 12 * 60
    if "after lunch" in lowered:
        return 13 * 60, 17 * 60
    if "morning" in lowered:
        return 8 * 60, 12 * 60
    if "afternoon" in lowered:
        return 12 * 60, 17 * 60
    if "evening" in lowered:
        return 17 * 60, 21 * 60
    if "noon" in lowered:
        return 11 * 60, 14 * 60
    return None


def _parse_calendly_dt(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


def _iso_utc(dt: datetime) -> str:
    return (
        dt.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _calendly_api_get(
    cfg: CalendlyConfig,
    path: str,
    query: Optional[Dict[str, str]] = None,
    timeout: float = 15.0,
) -> Dict[str, Any]:
    """Read-only Calendly API helper.

    This intentionally supports GET only. Booking is always done through the
    hosted Calendly page and browser automation.
    """

    if not cfg.access_token:
        raise CalendlyAutomationError("Calendly API token is not configured.")

    query_string = urllib.parse.urlencode(query or {})
    url = f"https://api.calendly.com/{path.lstrip('/')}"
    if query_string:
        url = f"{url}?{query_string}"

    curl_result = _curl_calendly_api_get(cfg, url=url, timeout=timeout)
    if curl_result is not None:
        return curl_result

    req = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Authorization": f"Bearer {cfg.access_token}",
            "Accept": "application/json",
            "User-Agent": "1PAX-Chatbot/1.0",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")[:500]
        raise CalendlyAutomationError(
            "Calendly API request failed.",
            status=exc.code,
            detail=body_text,
        ) from exc
    except (OSError, ValueError) as exc:
        raise CalendlyAutomationError("Calendly API request failed.") from exc


def _curl_calendly_api_get(
    cfg: CalendlyConfig,
    url: str,
    timeout: float = 15.0,
) -> Optional[Dict[str, Any]]:
    """Use curl for read-only Calendly API calls if urllib TLS is blocked."""

    curl_bin = shutil.which("curl")
    if not curl_bin:
        return None

    header_file = None
    try:
        with tempfile.NamedTemporaryFile("w", delete=False) as headers:
            header_file = headers.name
            headers.write(f"Authorization: Bearer {cfg.access_token}\n")
            headers.write("Accept: application/json\n")
            headers.write(
                "User-Agent: Mozilla/5.0 AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0 Safari/537.36\n"
            )

        completed = subprocess.run(
            [
                curl_bin,
                "--silent",
                "--show-error",
                "--location",
                "--max-time",
                str(max(5, int(timeout))),
                "--request",
                "GET",
                "--url",
                url,
                "--header",
                f"@{header_file}",
                "--write-out",
                "\n%{http_code}",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=max(10, timeout + 5),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        logger.warning("Calendly curl availability request failed: %s", exc)
        return None
    finally:
        if header_file:
            try:
                os.unlink(header_file)
            except OSError:
                pass

    output = completed.stdout or ""
    if "\n" not in output:
        logger.warning("Calendly curl availability request returned no HTTP status.")
        return None

    raw_body, status_text = output.rsplit("\n", 1)
    try:
        status = int(status_text.strip())
    except ValueError:
        logger.warning(
            "Calendly curl availability request returned invalid status: %s",
            status_text,
        )
        return None

    if not 200 <= status < 300:
        raise CalendlyAutomationError(
            "Calendly API availability request failed.",
            status=status,
            detail=(raw_body or completed.stderr or "")[:500],
        )

    try:
        return json.loads(raw_body) if raw_body else {}
    except ValueError as exc:
        raise CalendlyAutomationError(
            "Calendly API returned invalid JSON.",
            status=status,
            detail=raw_body[:500],
        ) from exc


def _api_available_slot_times(
    cfg: CalendlyConfig,
    start: datetime,
    end: datetime,
) -> List[str]:
    if not cfg.availability_api_connected:
        return []

    data = _calendly_api_get(
        cfg,
        "/event_type_available_times",
        query={
            "event_type": cfg.event_type_uri,
            "start_time": _iso_utc(start),
            "end_time": _iso_utc(end),
        },
    )

    slots: List[str] = []
    for item in data.get("collection", []):
        if item.get("status") and item.get("status") != "available":
            continue
        if (
            item.get("invitees_remaining") is not None
            and item.get("invitees_remaining") <= 0
        ):
            continue
        start_time = item.get("start_time")
        if isinstance(start_time, str) and start_time:
            slots.append(_iso_utc(_parse_calendly_dt(start_time)))
    return slots


def _slot_label(start_time: str, timezone_name: str, lang: Optional[str] = None) -> str:
    tz = _zone(timezone_name)
    dt = _parse_calendly_dt(start_time).astimezone(tz)
    if _is_sr(lang):
        weekday = _SR_WEEKDAYS[dt.weekday()]
        month = _SR_MONTHS[dt.month]
        return f"{weekday}, {dt.day}. {month} u {dt:%H:%M}"
    return dt.strftime("%a, %b %-d at %-I:%M %p")


def _json_slot(value: Any, default: Any) -> Any:
    if not value:
        return default
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


def _format_slots(
    slots: List[Dict[str, str]],
    timezone_name: str,
    lang: Optional[str] = None,
) -> str:
    host = (slots[0].get("colleague_label") or "").strip() if slots else ""
    office = (slots[0].get("colleague_office") or "").strip() if slots else ""
    host_label = f"{host} ({office})" if host and office else host
    if _is_sr(lang):
        intro = (
            f"Pronašao sam ove dostupne termine sa {host_label} ({timezone_name}):"
            if host_label
            else f"Pronašao sam ove dostupne termine ({timezone_name}):"
        )
        lines = [intro]
        for idx, slot in enumerate(slots, start=1):
            lines.append(
                f"{idx}. **{_slot_label(slot['start_time'], timezone_name, lang)}**"
            )
        lines.append("")
        lines.append("Odgovorite brojem, ili recite drugi dan/vreme.")
        return "\n".join(lines)

    intro = (
        f"I found these available times with {host_label} ({timezone_name}):"
        if host_label
        else f"I found these available times ({timezone_name}):"
    )
    lines = [intro]
    for idx, slot in enumerate(slots, start=1):
        lines.append(f"{idx}. **{slot['label']}**")
    lines.append("")
    lines.append("Reply with a number, or tell me a different day/time.")
    return "\n".join(lines)


def _word_slot_choice(text: str) -> Optional[int]:
    normalized = _ascii_norm(text)
    for token in re.findall(r"[a-z0-9]+", normalized):
        number = _SLOT_WORD_TO_NUMBER.get(token)
        if number:
            return number
    return None


def _looks_like_slot_choice_only(text: str) -> bool:
    stripped = text.strip().lower()
    if re.fullmatch(r"\d{1,2}[.)]?", stripped):
        return True
    normalized = _ascii_norm(stripped)
    tokens = re.findall(r"[a-z0-9]+", normalized)
    return bool(tokens) and all(
        token in _SLOT_WORD_TO_NUMBER or token in {"option", "slot", "broj", "termin"}
        for token in tokens
    )


def _parse_slot_choice(
    text: str,
    slots: List[Dict[str, str]],
    timezone_name: str = _DEFAULT_TIMEZONE,
) -> Optional[Dict[str, str]]:
    lowered = text.lower()
    ordinal_map = {
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
    }
    for word, number in ordinal_map.items():
        if word in lowered and 1 <= number <= len(slots):
            return slots[number - 1]

    match = re.search(r"\b([1-9]|10)\b", lowered)
    if match:
        index = int(match.group(1)) - 1
        if 0 <= index < len(slots):
            return slots[index]

    word_choice = _word_slot_choice(text)
    if word_choice:
        index = word_choice - 1
        if 0 <= index < len(slots):
            return slots[index]

    for slot in slots:
        labels = {
            slot.get("label", "").lower(),
            _slot_label(slot["start_time"], timezone_name).lower(),
            _slot_label(slot["start_time"], timezone_name, "SR").lower(),
        }
        if any(label and label in lowered for label in labels):
            return slot
        if slot["start_time"].lower() in lowered:
            return slot

    return None


def _available_slots(
    cfg: CalendlyConfig,
    preference: str,
    timezone_name: str,
) -> Tuple[List[Dict[str, str]], bool]:
    tz = _zone(timezone_name)
    start, end = _date_range_for_preference(preference, tz)
    if end - start > timedelta(days=_MAX_RANGE_DAYS):
        end = start + timedelta(days=_MAX_RANGE_DAYS)

    raw_slots: List[str] = []
    api_error: Optional[Exception] = None

    if cfg.availability_api_connected:
        try:
            raw_slots = _api_available_slot_times(cfg, start, end)
        except Exception as exc:
            api_error = exc
            detail = getattr(exc, "detail", None)
            status = getattr(exc, "status", None)
            logger.warning(
                "Calendly read-only availability failed: status=%s detail=%s",
                status,
                detail,
            )

    if not raw_slots and cfg.scheduling_link:
        try:
            from .calendly_browser import find_calendly_available_slots

            raw_slots = find_calendly_available_slots(
                scheduling_link=cfg.scheduling_link,
                range_start=start,
                range_end=end,
                timezone_name=timezone_name,
                max_slots=max(cfg.max_slots * 4, cfg.max_slots),
                timeout_seconds=cfg.browser_timeout_seconds,
                headless=cfg.browser_headless,
                executable_path=cfg.browser_executable_path or None,
            )
        except Exception as exc:
            logger.warning("Calendly hosted-page availability failed: %s", exc)
            if api_error:
                raise CalendlyAutomationError(
                    "Calendly availability could not be reached."
                ) from exc
            raise CalendlyAutomationError(
                "Calendly hosted page could not be reached."
            ) from exc
    elif not raw_slots and api_error:
        raise CalendlyAutomationError(
            "Calendly availability could not be reached."
        ) from api_error

    window = _time_window(preference)
    filtered = raw_slots
    used_preference_filter = False
    if window:
        start_minute, end_minute = window
        filtered = [
            slot
            for slot in raw_slots
            if (
                start_minute
                <= (
                    _parse_calendly_dt(slot).astimezone(tz).hour * 60
                    + _parse_calendly_dt(slot).astimezone(tz).minute
                )
                < end_minute
            )
        ]
        used_preference_filter = bool(filtered)
        if not filtered:
            filtered = raw_slots

    slots = [
        {
            "start_time": slot,
            "label": _slot_label(slot, timezone_name),
        }
        for slot in sorted(filtered)[: cfg.max_slots]
    ]
    return slots, used_preference_filter or not window


def _config_unavailable_message(cfg: CalendlyConfig) -> str:
    return (
        "I can help schedule meetings, but the Calendly booking link is not "
        "configured yet."
    )


def _prefilled_scheduling_link(
    cfg: CalendlyConfig,
    name: str,
    email: str,
    purpose: str,
    start_time: Optional[str] = None,
    timezone_name: str = _DEFAULT_TIMEZONE,
) -> str:
    if not cfg.scheduling_link:
        return ""

    from .calendly_browser import build_calendly_scheduling_url

    return build_calendly_scheduling_url(
        cfg.scheduling_link,
        name=name,
        email=email,
        purpose=purpose,
        start_time=start_time,
        timezone_name=timezone_name,
    )


def _book_invitee_with_browser(
    cfg: CalendlyConfig,
    name: str,
    email: str,
    purpose: str,
    timezone_name: str,
    start_time: str,
) -> Optional[Dict[str, str]]:
    if not (cfg.browser_fallback and cfg.scheduling_link):
        return None

    script_path = os.path.join(os.path.dirname(__file__), "calendly_browser.py")
    cmd = [
        sys.executable,
        script_path,
        "--link",
        cfg.scheduling_link,
        "--name",
        name,
        "--email",
        email,
        "--purpose",
        purpose,
        "--start-time",
        start_time,
        "--timezone",
        timezone_name,
        "--timeout-seconds",
        str(cfg.browser_timeout_seconds),
    ]
    if not cfg.browser_headless:
        cmd.append("--headful")
    if cfg.browser_executable_path:
        cmd.extend(["--executable-path", cfg.browser_executable_path])

    logger.warning(
        "Calendly browser automation starting: start_time=%s timezone=%s "
        "timeout=%ss",
        start_time,
        timezone_name,
        cfg.browser_timeout_seconds,
    )
    print(
        "[calendly] browser automation starting "
        f"start_time={start_time} timezone={timezone_name} "
        f"timeout={cfg.browser_timeout_seconds}s",
        flush=True,
    )
    try:
        completed = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=max(20, cfg.browser_timeout_seconds + 15),
        )
    except Exception as exc:
        logger.warning("Calendly browser automation failed: %s", exc)
        return None

    if completed.returncode != 0:
        print(
            "[calendly] browser automation failed "
            f"rc={completed.returncode} "
            f"stderr={(completed.stderr or '')[-1200:]} "
            f"stdout={(completed.stdout or '')[-500:]}",
            flush=True,
        )
        logger.warning(
            "Calendly browser automation failed: rc=%s stderr=%s stdout=%s",
            completed.returncode,
            (completed.stderr or "")[-500:],
            (completed.stdout or "")[-500:],
        )
        return None

    try:
        result = json.loads(completed.stdout)
    except ValueError:
        print(
            "[calendly] browser automation invalid json "
            f"stdout={(completed.stdout or '')[-500:]}",
            flush=True,
        )
        logger.warning(
            "Calendly browser automation returned invalid JSON: %s",
            (completed.stdout or "")[-500:],
        )
        return None

    if not result.get("scheduled"):
        print(
            "[calendly] browser automation did not submit "
            f"message={result.get('message', '')}",
            flush=True,
        )
        logger.warning(
            "Calendly browser automation did not submit: %s",
            result.get("message", ""),
        )
        return None

    logger.warning(
        "Calendly browser automation completed: start_time=%s", start_time
    )
    print(
        "[calendly] browser automation completed "
        f"start_time={start_time}",
        flush=True,
    )
    return {
        "final_url": result.get("final_url", ""),
        "message": result.get("message", ""),
        "confirmation_text": result.get("confirmation_text", ""),
    }


def _booking_summary_lines(
    name: str,
    email: str,
    purpose: str,
    selected_label: Optional[str],
    lang: Optional[str] = None,
    colleague_label: Optional[str] = None,
) -> List[str]:
    if _is_sr(lang):
        lines = [
            "**Rezime rezervacije**",
            f"Vreme: **{selected_label or 'Izabrani Calendly termin'}**",
        ]
        if colleague_label:
            lines.append(f"Domaćin: **{colleague_label}**")
        lines.extend([
            f"Ime: **{name}**",
            f"Email: **{email}**",
            f"Povod: **{purpose}**",
        ])
        return lines

    lines = [
        "**Booking summary**",
        f"Time: **{selected_label or 'Selected Calendly slot'}**",
    ]
    if colleague_label:
        lines.append(f"Host: **{colleague_label}**")
    lines.extend([
        f"Name: **{name}**",
        f"Email: **{email}**",
        f"Purpose: **{purpose}**",
    ])
    return lines


def _booking_confirmation_prompt(
    name: str,
    email: str,
    purpose: str,
    selected_label: Optional[str],
    lang: Optional[str] = None,
    colleague_label: Optional[str] = None,
) -> str:
    lines = _booking_summary_lines(
        name,
        email,
        purpose,
        selected_label,
        lang,
        colleague_label=colleague_label,
    )
    lines.append("")
    if _is_sr(lang):
        lines.append("Odgovorite **da** i odmah ću završiti rezervaciju.")
        lines.append("Odgovorite **ne** za otkazivanje.")
        return "\n".join(lines)
    lines.append("Reply **yes** and I will finalize this booking now.")
    lines.append("Reply **no** to cancel.")
    return "\n".join(lines)


def _booking_success_message(
    name: str,
    email: str,
    purpose: str,
    selected_label: Optional[str],
    confirmation_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
    reschedule_url: Optional[str] = None,
    lang: Optional[str] = None,
) -> str:
    if _is_sr(lang):
        lines = [
            f"Rezervisano je: **{selected_label}**.",
            f"Calendly će poslati pozivnicu na **{email}**.",
            f"Povod: **{purpose}**.",
        ]
        confirmation_label = "Calendly potvrda"
        reschedule_label = "Promeni termin"
        cancel_label = "Otkaži"
    else:
        lines = [
            f"You're booked: **{selected_label}**.",
            f"Calendly will send the invitation to **{email}**.",
            f"Purpose: **{purpose}**.",
        ]
        confirmation_label = "Calendly confirmation"
        reschedule_label = "Reschedule"
        cancel_label = "Cancel"
    if confirmation_url:
        lines.append(f"[{confirmation_label}]({confirmation_url})")
    if reschedule_url:
        lines.append(f"[{reschedule_label}]({reschedule_url})")
    if cancel_url:
        lines.append(f"[{cancel_label}]({cancel_url})")
    return "\n\n".join(lines)


def _manual_finalize_message(
    cfg: CalendlyConfig,
    name: str,
    email: str,
    purpose: str,
    selected_label: Optional[str],
    selected_start_time: Optional[str],
    timezone_name: str,
    lang: Optional[str] = None,
) -> Optional[str]:
    if not cfg.allow_link_fallback:
        return None

    link = _prefilled_scheduling_link(
        cfg,
        name,
        email,
        purpose,
        start_time=selected_start_time,
        timezone_name=timezone_name,
    )
    if not link:
        return None

    lines = _booking_summary_lines(name, email, purpose, selected_label, lang)
    lines.append("")
    if _is_sr(lang):
        lines.append(
            "Pripremio sam tačan, unapred popunjen Calendly link za potvrdu "
            "ovog termina:"
        )
        lines.append(f"[Završi u Calendlyju]({link})")
        return "\n\n".join(lines)

    lines.append(
        "I prepared the exact pre-filled Calendly confirmation link for this "
        "slot:"
    )
    lines.append(f"[Finalize in Calendly]({link})")
    return "\n\n".join(lines)


def _calendly_redirect_message(
    name: str,
    email: str,
    purpose: str,
    selected_label: Optional[str],
    link: str,
    lang: Optional[str] = None,
) -> str:
    lines = _booking_summary_lines(name, email, purpose, selected_label, lang)
    lines.append("")
    if _is_sr(lang):
        lines.append(
            "Otvaram tačan, unapred popunjen Calendly termin u vašem browseru."
        )
        lines.append(
            "Ako se stranica ne otvori automatski, koristite ovaj link: "
            f"[Otvori u Calendlyju]({link})"
        )
        return "\n\n".join(lines)

    lines.append("Opening the exact pre-filled Calendly slot in your browser.")
    lines.append(
        "If it does not open automatically, use this link: "
        f"[Open in Calendly]({link})"
    )
    return "\n\n".join(lines)


def _utter_calendly_redirect(
    dispatcher: CollectingDispatcher,
    text: str,
    link: str,
    lang: Optional[str],
    already_localized: bool = False,
) -> None:
    dispatcher.utter_message(
        text=text if already_localized else translate_response(text, lang),
        json_message={
            "redirect_url": link,
            "redirect_delay_ms": 600,
            "redirect_reason": "calendly_prefilled_confirmation",
        },
    )


def run_calendly_scheduling(
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
) -> List[SlotSet]:
    """Shared scheduling entrypoint used by the action and active fallback."""

    if _scheduling_provider() != "calendly":
        return run_google_calendar_scheduling(dispatcher, tracker, domain)
    return _run_calendly_scheduling(dispatcher, tracker, domain)


def run_google_calendar_scheduling(
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
) -> List[SlotSet]:
    """Conversational Google Calendar scheduler."""

    del domain
    lang = get_lang(tracker)
    events: List[SlotSet] = _lang_event(lang)
    cfg = _google_calendar_config()

    text = tracker.latest_message.get("text") or ""
    intent = tracker.latest_message.get("intent", {}).get("name", "")
    stage = tracker.get_slot("schedule_stage")

    if _is_cancel(text, intent, stage):
        _utter(
            dispatcher,
            "No problem. I will leave the meeting scheduling there.",
            lang,
        )
        return _clear_schedule_events() + events

    timezone_name = _user_timezone(tracker, cfg)
    metadata = tracker.latest_message.get("metadata") or {}
    context = gcal.detect_scheduling_context(
        lang=lang,
        metadata=metadata,
        text=text,
        timezone_name=timezone_name,
    )
    ranked_options = gcal.options_from_payload(
        tracker.get_slot("schedule_colleague_options"),
        cfg.roster,
    ) or gcal.rank_colleagues(cfg.roster, context)
    selected_colleague = _google_colleague_from_slots(cfg, tracker)

    name = tracker.get_slot("schedule_name")
    email = tracker.get_slot("schedule_email")
    purpose = tracker.get_slot("schedule_purpose")
    time_preference = tracker.get_slot("schedule_time_preference")
    selected_slot = tracker.get_slot("schedule_selected_slot")
    selected_label = tracker.get_slot("schedule_selected_slot_label")
    offered_slots = _json_slot(tracker.get_slot("schedule_offered_slots"), [])

    extracted_name = _extract_name(text, stage)
    if extracted_name:
        name = extracted_name
        events.append(SlotSet("schedule_name", name))

    extracted_email = _extract_email(text)
    if extracted_email:
        email = extracted_email
        events.append(SlotSet("schedule_email", email))

    extracted_purpose = _extract_purpose(text, stage)
    if extracted_purpose:
        purpose = extracted_purpose
        events.append(SlotSet("schedule_purpose", purpose))

    extracted_time_preference = (
        None if stage == "collect_purpose" else _extract_time_preference(text, stage)
    )
    if extracted_time_preference and stage not in {"select_slot", "confirm"}:
        time_preference = extracted_time_preference
        offered_slots = []
        selected_slot = None
        selected_label = None
        events.extend(
            [
                SlotSet("schedule_time_preference", time_preference),
                SlotSet("schedule_offered_slots", None),
                SlotSet("schedule_selected_slot", None),
                SlotSet("schedule_selected_slot_label", None),
            ]
        )

    if not name:
        _utter(
            dispatcher,
            "Of course. I can help schedule a meeting with 1PAX. What name "
            "should I put on the invite?",
            lang,
        )
        return events + _set_stage("collect_name")

    if not email:
        _utter(
            dispatcher,
            f"Thanks, {name}. What email address should Google Calendar send "
            "the invitation to?",
            lang,
        )
        return events + _set_stage("collect_email")

    if not purpose:
        _utter(
            dispatcher,
            "What is the purpose of the meeting? A short note is enough, for "
            "example: project consultation, partnership, proposal, careers, "
            "press, or a general introduction.",
            lang,
        )
        return events + _set_stage("collect_purpose")

    if stage == "confirm_route":
        parsed_choice = gcal.parse_colleague_choice(text, ranked_options)
        if parsed_choice:
            selected_colleague = parsed_choice
            offered_slots = []
            events.extend(
                _google_context_events(context, selected_colleague, ranked_options)
            )
        elif _is_affirmation(text) and selected_colleague:
            events.extend(
                _google_context_events(context, selected_colleague, ranked_options)
            )
        elif _is_route_rejection(text):
            _utter(
                dispatcher,
                _route_options_text(ranked_options),
                lang,
                buttons=_colleague_option_buttons(ranked_options),
            )
            return events + _google_context_events(
                context,
                selected_colleague,
                ranked_options,
            ) + _set_stage("choose_route")
        else:
            prompt_colleague = selected_colleague or ranked_options[0]
            _utter(
                dispatcher,
                "Please reply yes to use that office, or say you would like "
                "another option.",
                lang,
                buttons=_route_confirmation_buttons(prompt_colleague, lang),
            )
            return events + _set_stage("confirm_route")

    if stage == "choose_route":
        selected_colleague = gcal.parse_colleague_choice(text, ranked_options)
        if not selected_colleague:
            _utter(
                dispatcher,
                _route_options_text(ranked_options),
                lang,
                buttons=_colleague_option_buttons(ranked_options),
            )
            return events + _google_context_events(
                context,
                options=ranked_options,
            ) + _set_stage("choose_route")
        offered_slots = []
        events.extend(_google_context_events(context, selected_colleague, ranked_options))

    if not selected_colleague:
        if not ranked_options:
            _utter(
                dispatcher,
                "I can help schedule meetings, but no Google Calendar colleagues "
                "are configured yet.",
                lang,
            )
            return _clear_schedule_events() + events

        selected_colleague = ranked_options[0]
        _utter(
            dispatcher,
            _route_confirmation_text(context, selected_colleague),
            lang,
            buttons=_route_confirmation_buttons(selected_colleague, lang),
        )
        return events + _google_context_events(
            context,
            selected_colleague,
            ranked_options,
        ) + _set_stage("confirm_route")

    if not time_preference:
        _utter(
            dispatcher,
            f"Great. I will look for times with {selected_colleague.display_name}. "
            "When would you like to meet? You can say *tomorrow afternoon*, "
            "*next Tuesday morning*, or *any time next week*.",
            lang,
        )
        return events + _google_context_events(
            context,
            selected_colleague,
            ranked_options,
        ) + [
            SlotSet("schedule_timezone", timezone_name),
            SlotSet("schedule_stage", "collect_time"),
        ]

    if stage == "select_slot" and offered_slots:
        choice = _parse_slot_choice(text, offered_slots, timezone_name)
        if choice:
            selected_slot = choice["start_time"]
            selected_label = choice.get("label") or _slot_label(
                selected_slot,
                timezone_name,
                lang,
            )
            slot_colleague = gcal.colleague_by_id(cfg.roster, choice.get("colleague_id"))
            if slot_colleague:
                selected_colleague = slot_colleague
                events.extend(_google_context_events(context, selected_colleague, ranked_options))
            events.extend(
                [
                    SlotSet("schedule_selected_slot", selected_slot),
                    SlotSet("schedule_selected_slot_label", selected_label),
                ]
            )
            _utter(
                dispatcher,
                _booking_confirmation_prompt(
                    name=name,
                    email=email,
                    purpose=purpose,
                    selected_label=selected_label,
                    lang=lang,
                    colleague_label=selected_colleague.display_name,
                ),
                lang,
                already_localized=_is_sr(lang),
            )
            return events + _set_stage("confirm")

        if _has_time_words(text) and not _looks_like_slot_choice_only(text):
            time_preference = text.strip()
            offered_slots = []
            selected_slot = None
            selected_label = None
            events.extend(
                [
                    SlotSet("schedule_time_preference", time_preference),
                    SlotSet("schedule_offered_slots", None),
                    SlotSet("schedule_selected_slot", None),
                    SlotSet("schedule_selected_slot_label", None),
                ]
            )
        else:
            _utter(
                dispatcher,
                "I did not catch which time you wanted. Please reply with one "
                "of the numbers, or tell me another day/time.",
                lang,
            )
            return events + _set_stage("select_slot")

    if stage == "confirm" and _has_time_words(text) and not _looks_like_slot_choice_only(text):
        time_preference = text.strip()
        offered_slots = []
        selected_slot = None
        selected_label = None
        stage = "collect_time"
        events.extend(
            [
                SlotSet("schedule_time_preference", time_preference),
                SlotSet("schedule_offered_slots", None),
                SlotSet("schedule_selected_slot", None),
                SlotSet("schedule_selected_slot_label", None),
            ]
        )

    if stage == "confirm":
        if _is_affirmation(text):
            if not selected_slot:
                _utter(
                    dispatcher,
                    "I lost the selected time. Let me show the available slots "
                    "again.",
                    lang,
                )
                offered_slots = []
            else:
                selected_payload = next(
                    (
                        slot
                        for slot in offered_slots
                        if slot.get("start_time") == selected_slot
                    ),
                    {},
                )
                try:
                    booking = _book_google_calendar_event(
                        cfg=cfg,
                        colleague=selected_colleague,
                        name=name,
                        email=email,
                        purpose=purpose,
                        selected_slot=selected_slot,
                        selected_end=selected_payload.get("end_time"),
                        timezone_name=timezone_name,
                    )
                except gcal.GoogleCalendarError as exc:
                    logger.warning("Google Calendar booking failed: %s", exc)
                    _utter(
                        dispatcher,
                        "Google Calendar could not complete the booking inside "
                        "the chat yet. Please choose another time, or try again "
                        "after the Workspace calendar connection is configured.",
                        lang,
                    )
                    return events + _set_stage("select_slot")

                _utter(
                    dispatcher,
                    _google_booking_success_message(
                        email=email,
                        purpose=purpose,
                        selected_label=selected_label,
                        colleague=selected_colleague,
                        booking=booking,
                        lang=lang,
                    ),
                    lang,
                    already_localized=_is_sr(lang),
                )
                return _clear_schedule_events() + events + [
                    SlotSet("schedule_booking_event_id", booking.event_id),
                    SlotSet("schedule_booking_meet_link", booking.meet_link or None),
                ]

        _utter(
            dispatcher,
            "Please reply yes to book that time, or no to cancel.",
            lang,
        )
        return events + _set_stage("confirm")

    if not offered_slots:
        try:
            offered_slots, matched_preference = _google_available_slots(
                cfg,
                selected_colleague,
                time_preference,
                timezone_name,
                lang,
            )
        except gcal.GoogleCalendarError as exc:
            logger.warning("Google Calendar availability failed: %s", exc)
            _utter(
                dispatcher,
                "I can route the meeting inside the chat, but live Google "
                "Calendar availability is not connected yet. Once the Workspace "
                "calendar authentication is configured, I will show open times "
                "and book the event here without sending you to another page.",
                lang,
            )
            return events + _google_context_events(
                context,
                selected_colleague,
                ranked_options,
            ) + _set_stage("collect_time")

        if not offered_slots:
            _utter(
                dispatcher,
                f"I could not find open times with {selected_colleague.display_name} "
                "in that window. Try another option, like *tomorrow morning* "
                "or *next week*, or ask for another office.",
                lang,
            )
            return events + _set_stage("collect_time")

        events.extend(
            [
                SlotSet("schedule_timezone", timezone_name),
                SlotSet("schedule_offered_slots", json.dumps(offered_slots)),
            ]
        )
        if not matched_preference:
            _utter(
                dispatcher,
                "I could not find times in that exact part of the day, but "
                "these nearby options are open.",
                lang,
            )
        _utter(
            dispatcher,
            _format_slots(offered_slots, timezone_name, lang),
            lang,
            already_localized=_is_sr(lang),
        )
        return events + _google_context_events(
            context,
            selected_colleague,
            ranked_options,
        ) + _set_stage("select_slot")

    _utter(
        dispatcher,
        _format_slots(offered_slots, timezone_name, lang),
        lang,
        already_localized=_is_sr(lang),
    )
    return events + _set_stage("select_slot")


def _run_calendly_scheduling(
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
) -> List[SlotSet]:
    """Legacy Calendly implementation."""

    del domain
    lang = get_lang(tracker)
    events: List[SlotSet] = _lang_event(lang)
    cfg = _config_from_env()

    text = tracker.latest_message.get("text") or ""
    intent = tracker.latest_message.get("intent", {}).get("name", "")
    stage = tracker.get_slot("schedule_stage")

    if _is_cancel(text, intent, stage):
        _utter(
            dispatcher,
            "No problem. I will leave the meeting scheduling there.",
            lang,
        )
        return _clear_schedule_events() + events

    if not cfg.is_connected:
        _utter(dispatcher, _config_unavailable_message(cfg), lang)
        return _clear_schedule_events() + events

    timezone_name = _user_timezone(tracker, cfg)
    name = tracker.get_slot("schedule_name")
    email = tracker.get_slot("schedule_email")
    purpose = tracker.get_slot("schedule_purpose")
    time_preference = tracker.get_slot("schedule_time_preference")
    selected_slot = tracker.get_slot("schedule_selected_slot")
    selected_label = tracker.get_slot("schedule_selected_slot_label")
    offered_slots = _json_slot(tracker.get_slot("schedule_offered_slots"), [])

    extracted_name = _extract_name(text, stage)
    if extracted_name:
        name = extracted_name
        events.append(SlotSet("schedule_name", name))

    extracted_email = _extract_email(text)
    if extracted_email:
        email = extracted_email
        events.append(SlotSet("schedule_email", email))

    extracted_purpose = _extract_purpose(text, stage)
    if extracted_purpose:
        purpose = extracted_purpose
        events.append(SlotSet("schedule_purpose", purpose))

    extracted_time_preference = (
        None if stage == "collect_purpose" else _extract_time_preference(text, stage)
    )
    if extracted_time_preference and stage not in {"select_slot", "confirm"}:
        time_preference = extracted_time_preference
        offered_slots = []
        selected_slot = None
        selected_label = None
        events.extend(
            [
                SlotSet("schedule_time_preference", time_preference),
                SlotSet("schedule_offered_slots", None),
                SlotSet("schedule_selected_slot", None),
                SlotSet("schedule_selected_slot_label", None),
            ]
        )

    if not name:
        _utter(
            dispatcher,
            "Of course. I can help schedule a meeting with 1PAX. What name "
            "should I put on the invite?",
            lang,
        )
        return events + _set_stage("collect_name")

    if not email:
        _utter(
            dispatcher,
            f"Thanks, {name}. What email address should Calendly send the "
            "invitation to?",
            lang,
        )
        return events + _set_stage("collect_email")

    if not purpose:
        _utter(
            dispatcher,
            "What is the purpose of the meeting? A short note is enough, for "
            "example: project consultation, partnership, proposal, careers, "
            "press, or a general introduction.",
            lang,
        )
        return events + _set_stage("collect_purpose")

    if not time_preference:
        _utter(
            dispatcher,
            "Great. When would you like to meet? You can say *tomorrow "
            "afternoon*, *next Tuesday morning*, or *any time next week*.",
            lang,
        )
        return events + [
            SlotSet("schedule_timezone", timezone_name),
            SlotSet("schedule_stage", "collect_time"),
        ]

    if stage == "select_slot" and offered_slots:
        choice = _parse_slot_choice(text, offered_slots, timezone_name)
        if choice:
            selected_slot = choice["start_time"]
            selected_label = _slot_label(selected_slot, timezone_name, lang)
            events.extend(
                [
                    SlotSet("schedule_selected_slot", selected_slot),
                    SlotSet("schedule_selected_slot_label", selected_label),
                ]
            )
            _utter(
                dispatcher,
                _booking_confirmation_prompt(
                    name=name,
                    email=email,
                    purpose=purpose,
                    selected_label=selected_label,
                    lang=lang,
                ),
                lang,
                already_localized=_is_sr(lang),
            )
            return events + _set_stage("confirm")

        if _has_time_words(text) and not _looks_like_slot_choice_only(text):
            time_preference = text.strip()
            offered_slots = []
            selected_slot = None
            selected_label = None
            events.extend(
                [
                    SlotSet("schedule_time_preference", time_preference),
                    SlotSet("schedule_offered_slots", None),
                    SlotSet("schedule_selected_slot", None),
                    SlotSet("schedule_selected_slot_label", None),
                ]
            )
        else:
            _utter(
                dispatcher,
                "I did not catch which time you wanted. Please reply with one "
                "of the numbers, or tell me another day/time.",
                lang,
            )
            return events + _set_stage("select_slot")

    if stage == "confirm" and _has_time_words(text) and not _looks_like_slot_choice_only(text):
        time_preference = text.strip()
        offered_slots = []
        selected_slot = None
        selected_label = None
        stage = "collect_time"
        events.extend(
            [
                SlotSet("schedule_time_preference", time_preference),
                SlotSet("schedule_offered_slots", None),
                SlotSet("schedule_selected_slot", None),
                SlotSet("schedule_selected_slot_label", None),
            ]
        )

    if stage == "confirm":
        if _is_affirmation(text):
            if not selected_slot:
                _utter(
                    dispatcher,
                    "I lost the selected time. Let me show the available slots "
                    "again.",
                    lang,
                )
                offered_slots = []
            else:
                redirect_link = _prefilled_scheduling_link(
                    cfg=cfg,
                    name=name,
                    email=email,
                    purpose=purpose,
                    start_time=selected_slot,
                    timezone_name=timezone_name,
                )
                if redirect_link:
                    _utter_calendly_redirect(
                        dispatcher,
                        _calendly_redirect_message(
                            name=name,
                            email=email,
                            purpose=purpose,
                            selected_label=selected_label,
                            link=redirect_link,
                            lang=lang,
                        ),
                        redirect_link,
                        lang,
                        already_localized=_is_sr(lang),
                    )
                    return _clear_schedule_events() + events

                _utter(
                    dispatcher,
                    "I could not prepare the Calendly confirmation link right "
                    "now. Please choose another time, or try again shortly.",
                    lang,
                )
                return events + _set_stage("select_slot")

        _utter(
            dispatcher,
            "Please reply yes to book that time, or no to cancel.",
            lang,
        )
        return events + _set_stage("confirm")

    if not offered_slots:
        try:
            offered_slots, matched_preference = _available_slots(
                cfg,
                time_preference,
                timezone_name,
            )
        except CalendlyAutomationError:
            fallback = (
                f"\n\nYou can also schedule directly here: "
                f"[Schedule a meeting]({cfg.scheduling_link})"
                if cfg.allow_link_fallback and cfg.scheduling_link
                else ""
            )
            _utter(
                dispatcher,
                "Calendly could not be reached right now. Please try again "
                f"shortly.{fallback}",
                lang,
            )
            return events + _set_stage("collect_time")

        if not offered_slots:
            _utter(
                dispatcher,
                "I could not find open Calendly times in that window. Try "
                "another option, like *tomorrow morning* or *next week*.",
                lang,
            )
            return events + _set_stage("collect_time")

        events.extend(
            [
                SlotSet("schedule_timezone", timezone_name),
                SlotSet("schedule_offered_slots", json.dumps(offered_slots)),
            ]
        )
        if not matched_preference:
            _utter(
                dispatcher,
                "I could not find times in that exact part of the day, but "
                "these nearby options are open.",
                lang,
            )
        _utter(
            dispatcher,
            _format_slots(offered_slots, timezone_name, lang),
            lang,
            already_localized=_is_sr(lang),
        )
        return events + _set_stage("select_slot")

    _utter(
        dispatcher,
        _format_slots(offered_slots, timezone_name, lang),
        lang,
        already_localized=_is_sr(lang),
    )
    return events + _set_stage("select_slot")


def continue_active_calendly_scheduling(
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
) -> Optional[List[SlotSet]]:
    """Let the scheduler handle follow-ups while a booking flow is active."""

    if not tracker.get_slot("schedule_stage"):
        return None
    if schedule_topic_shift_events(tracker):
        return None
    return run_calendly_scheduling(dispatcher, tracker, domain)


class ActionScheduleMeeting(Action):
    """Conversational Calendly scheduler."""

    def name(self) -> Text:
        return "action_schedule_meeting"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[SlotSet]:
        return run_calendly_scheduling(dispatcher, tracker, domain)
