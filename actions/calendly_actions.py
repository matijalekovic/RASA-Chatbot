"""
Calendly scheduling flow for the 1PAX chatbot.

The flow is intentionally action-driven, matching the rest of this bot:
collect name/email/meeting purpose/time preference, show live Calendly
availability, ask for confirmation, then create the invitee through Calendly.
"""

import json
import logging
import os
import re
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

from .translation import get_lang, translate_response


logger = logging.getLogger(__name__)

_API_BASE = "https://api.calendly.com"
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
    access_token: str
    event_type_uri: str
    scheduling_link: str
    allow_link_fallback: bool
    browser_fallback: bool
    browser_preferred: bool
    browser_headless: bool
    browser_timeout_seconds: int
    browser_executable_path: str
    default_timezone: str
    max_slots: int
    location_kind: str
    location_value: str
    event_guests: Tuple[str, ...]

    @property
    def is_connected(self) -> bool:
        return bool(self.access_token and self.event_type_uri)


class CalendlyAPIError(RuntimeError):
    """Raised when Calendly returns an error or cannot be reached."""

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
    event_type_uri = (
        os.environ.get("CALENDLY_EVENT_TYPE_URI", "").strip()
        or os.environ.get("CALENDLY_EVENT_TYPE", "").strip()
    )
    event_type_uuid = os.environ.get("CALENDLY_EVENT_TYPE_UUID", "").strip()
    if not event_type_uri and event_type_uuid:
        event_type_uri = f"{_API_BASE}/event_types/{event_type_uuid}"

    guests = tuple(
        email.strip()
        for email in os.environ.get("CALENDLY_EVENT_GUESTS", "").split(",")
        if email.strip()
    )

    try:
        max_slots = int(os.environ.get("CALENDLY_MAX_SLOTS", "5"))
    except ValueError:
        max_slots = 5

    try:
        browser_timeout_seconds = int(
            os.environ.get("CALENDLY_BROWSER_TIMEOUT_SECONDS", "30")
        )
    except ValueError:
        browser_timeout_seconds = 30

    scheduling_link = (
        os.environ.get("CALENDLY_SCHEDULING_LINK", "").strip()
        or os.environ.get("CALENDLY_SCHEDULING_URL", "").strip()
    )
    allow_link_fallback = _env_bool("CALENDLY_ALLOW_LINK_FALLBACK") or _env_bool(
        "CALENDLY_ENABLE_LINK_FALLBACK"
    )
    browser_preferred = _env_bool("CALENDLY_BROWSER_PREFERRED")

    browser_fallback = (
        _env_bool(
            "CALENDLY_BROWSER_FALLBACK",
            default=browser_preferred or bool(allow_link_fallback and scheduling_link),
        )
        or _env_bool("CALENDLY_AUTOMATE_FALLBACK")
    )

    return CalendlyConfig(
        access_token=os.environ.get("CALENDLY_ACCESS_TOKEN", "").strip(),
        event_type_uri=event_type_uri,
        scheduling_link=scheduling_link,
        allow_link_fallback=allow_link_fallback,
        browser_fallback=browser_fallback,
        browser_preferred=browser_preferred,
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
        location_kind=os.environ.get("CALENDLY_LOCATION_KIND", "").strip(),
        location_value=os.environ.get("CALENDLY_LOCATION_VALUE", "").strip(),
        event_guests=guests,
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


def _utter(
    dispatcher: CollectingDispatcher,
    text: str,
    lang: Optional[str],
    already_localized: bool = False,
) -> None:
    dispatcher.utter_message(
        text=text if already_localized else translate_response(text, lang)
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
    lowered = text.lower()
    signals = {
        "today",
        "tomorrow",
        "week",
        "morning",
        "afternoon",
        "evening",
        "noon",
        "night",
        "anytime",
        "any time",
    }
    if any(signal in lowered for signal in signals):
        return True
    if any(day in lowered for day in _WEEKDAYS):
        return True
    if any(month in lowered for month in _MONTHS):
        return True
    return bool(re.search(r"\b\d{1,2}(:\d{2})?\s*(am|pm)?\b", lowered))


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


def _parse_date_value(raw: str, today: date) -> Optional[date]:
    text = raw.lower()

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

    month_names = "|".join(sorted(_MONTHS, key=len, reverse=True))
    month_first = re.search(
        rf"\b({month_names})\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,\s*(\d{{4}}))?\b",
        text,
    )
    day_first = re.search(
        rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({month_names})(?:\s+(\d{{4}}))?\b",
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
    lowered = preference.lower()

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

    for word, weekday in _WEEKDAYS.items():
        if re.search(rf"\b{re.escape(word)}\b", lowered):
            delta = (weekday - now.weekday()) % 7
            if delta == 0 or f"next {word}" in lowered:
                delta = 7
            start_date = now.date() + timedelta(days=delta)
            start = datetime.combine(start_date, time.min, tzinfo=tz)
            return start, start + timedelta(days=1)

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


def _time_window(preference: str) -> Optional[Tuple[int, int]]:
    lowered = preference.lower()
    if "morning" in lowered:
        return 8, 12
    if "afternoon" in lowered:
        return 12, 17
    if "evening" in lowered:
        return 17, 21
    if "noon" in lowered:
        return 11, 14
    return None


def _to_calendly_iso(value: datetime) -> str:
    return (
        value.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _parse_calendly_dt(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


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
    if _is_sr(lang):
        lines = [f"Pronašao sam ove dostupne termine ({timezone_name}):"]
        for idx, slot in enumerate(slots, start=1):
            lines.append(
                f"{idx}. **{_slot_label(slot['start_time'], timezone_name, lang)}**"
            )
        lines.append("")
        lines.append("Odgovorite brojem, ili recite drugi dan/vreme.")
        return "\n".join(lines)

    lines = [f"I found these available times ({timezone_name}):"]
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


def _calendly_request(
    cfg: CalendlyConfig,
    method: str,
    path: str,
    params: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    url = f"{_API_BASE}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {cfg.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "1PAX-Chatbot/1.0 (+https://www.1pax.com)",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        logger.warning(
            "Calendly API returned HTTP %s for %s %s: %s",
            exc.code,
            method,
            path,
            detail[:800],
        )
        raise CalendlyAPIError(
            "Calendly rejected the request.",
            exc.code,
            detail[:1200],
        ) from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        logger.warning("Calendly API call failed: %s", exc)
        raise CalendlyAPIError("Calendly could not be reached.") from exc


def _available_slots(
    cfg: CalendlyConfig,
    preference: str,
    timezone_name: str,
) -> Tuple[List[Dict[str, str]], bool]:
    tz = _zone(timezone_name)
    start, end = _date_range_for_preference(preference, tz)
    if end - start > timedelta(days=_MAX_RANGE_DAYS):
        end = start + timedelta(days=_MAX_RANGE_DAYS)

    result = _calendly_request(
        cfg,
        "GET",
        "/event_type_available_times",
        params={
            "event_type": cfg.event_type_uri,
            "start_time": _to_calendly_iso(start),
            "end_time": _to_calendly_iso(end),
        },
    )

    raw_slots = []
    for item in result.get("collection", []):
        start_time = item.get("start_time")
        if not start_time:
            continue
        if item.get("status") and item.get("status") != "available":
            continue
        raw_slots.append(start_time)

    window = _time_window(preference)
    filtered = raw_slots
    used_preference_filter = False
    if window:
        start_hour, end_hour = window
        filtered = [
            slot
            for slot in raw_slots
            if start_hour <= _parse_calendly_dt(slot).astimezone(tz).hour < end_hour
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


def _booking_body(
    cfg: CalendlyConfig,
    name: str,
    email: str,
    purpose: str,
    timezone_name: str,
    start_time: str,
    location: Optional[Dict[str, str]],
) -> Dict[str, Any]:
    tracking = {
        "utm_source": "1pax_chatbot",
        "utm_medium": "chatbot",
        "utm_campaign": "website_consultation",
        "utm_content": purpose[:255],
        "utm_term": "meeting_request",
    }
    salesforce_uuid = os.environ.get("CALENDLY_SALESFORCE_UUID", "").strip()
    if salesforce_uuid:
        tracking["salesforce_uuid"] = salesforce_uuid

    body: Dict[str, Any] = {
        "event_type": cfg.event_type_uri,
        "start_time": start_time,
        "invitee": {
            "name": name,
            "email": email,
            "timezone": timezone_name,
        },
        "booking_source": "ai_scheduling_assistant",
        "tracking": tracking,
        "questions_and_answers": [
            {
                "question": "Purpose of meeting",
                "answer": purpose,
                "position": 1,
            }
        ],
    }
    if location:
        body["location"] = location
    if cfg.event_guests:
        body["event_guests"] = list(cfg.event_guests)
    return body


def _configured_location(cfg: CalendlyConfig) -> Optional[Dict[str, str]]:
    if not cfg.location_kind:
        return None
    location = {"kind": cfg.location_kind}
    if cfg.location_value:
        location["location"] = cfg.location_value
    return location


def _event_type_location(cfg: CalendlyConfig) -> Optional[Dict[str, str]]:
    event_type_uuid = cfg.event_type_uri.rstrip("/").split("/")[-1]
    result = _calendly_request(cfg, "GET", f"/event_types/{event_type_uuid}")
    event_type = result.get("resource", result)
    locations = event_type.get("locations") or []
    if len(locations) != 1:
        return None

    location = locations[0] or {}
    kind = location.get("kind")
    if not kind:
        return None
    payload = {"kind": kind}
    location_value = location.get("location")
    if location_value:
        payload["location"] = location_value
    return payload


def _booking_location(cfg: CalendlyConfig) -> Optional[Dict[str, str]]:
    configured = _configured_location(cfg)
    if configured:
        return configured
    try:
        return _event_type_location(cfg)
    except CalendlyAPIError:
        logger.warning("Could not infer Calendly event type location.")
        return None


def _book_invitee(
    cfg: CalendlyConfig,
    name: str,
    email: str,
    purpose: str,
    timezone_name: str,
    start_time: str,
) -> Dict[str, Any]:
    location = _booking_location(cfg)
    result = _calendly_request(
        cfg,
        "POST",
        "/invitees",
        body=_booking_body(
            cfg,
            name,
            email,
            purpose,
            timezone_name,
            start_time,
            location,
        ),
    )
    return result.get("resource", result)


def _config_unavailable_message(cfg: CalendlyConfig) -> str:
    if cfg.allow_link_fallback and cfg.scheduling_link:
        return (
            "I can help with meetings, but live Calendly booking is not connected "
            f"inside the chat yet. You can schedule directly here: "
            f"[Schedule a meeting]({cfg.scheduling_link})"
        )
    return (
        "I can help schedule meetings, but direct Calendly booking is not "
        "connected inside the chat yet. Once it is connected, I will be able "
        "to show live availability and book the meeting here."
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

    try:
        from .calendly_browser import book_calendly_event

        result = book_calendly_event(
            scheduling_link=cfg.scheduling_link,
            name=name,
            email=email,
            purpose=purpose,
            start_time=start_time,
            timezone_name=timezone_name,
            timeout_seconds=cfg.browser_timeout_seconds,
            headless=cfg.browser_headless,
            executable_path=cfg.browser_executable_path or None,
        )
    except Exception as exc:
        logger.warning("Calendly browser fallback failed: %s", exc)
        return None

    if not result.scheduled:
        logger.warning("Calendly browser fallback did not submit: %s", result.message)
        return None

    return {
        "final_url": result.final_url,
        "message": result.message,
        "confirmation_text": result.confirmation_text,
    }


def _booking_summary_lines(
    name: str,
    email: str,
    purpose: str,
    selected_label: Optional[str],
    lang: Optional[str] = None,
) -> List[str]:
    if _is_sr(lang):
        return [
            "**Rezime rezervacije**",
            f"Vreme: **{selected_label or 'Izabrani Calendly termin'}**",
            f"Ime: **{name}**",
            f"Email: **{email}**",
            f"Povod: **{purpose}**",
        ]
    return [
        "**Booking summary**",
        f"Time: **{selected_label or 'Selected Calendly slot'}**",
        f"Name: **{name}**",
        f"Email: **{email}**",
        f"Purpose: **{purpose}**",
    ]


def _booking_confirmation_prompt(
    name: str,
    email: str,
    purpose: str,
    selected_label: Optional[str],
    lang: Optional[str] = None,
) -> str:
    lines = _booking_summary_lines(name, email, purpose, selected_label, lang)
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


def _direct_booking_error_message(error: CalendlyAPIError) -> str:
    if error.status == 403:
        return (
            "I could not complete the booking inside the chat because Calendly "
            "rejected the Scheduling API request. The 1PAX Calendly account "
            "may need a paid plan with Scheduling API access, or the token may "
            "need the right account permissions."
        )
    if error.status == 400:
        return (
            "I could not complete the booking inside the chat because Calendly "
            "rejected one of the booking details. Please try another available "
            "time. If this keeps happening, the event type location or invitee "
            "form settings need to be adjusted for API booking."
        )
    if error.status == 401:
        return (
            "I could not complete the booking inside the chat because Calendly "
            "did not accept the API token. The scheduler needs a fresh "
            "Calendly access token."
        )
    return (
        "Calendly could not complete the booking inside the chat right now. "
        "Please choose another time, or try again shortly."
    )


def run_calendly_scheduling(
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
) -> List[SlotSet]:
    """Shared implementation used by the scheduling action and active fallback."""

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
            events.extend(
                [
                    SlotSet("schedule_time_preference", time_preference),
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
                browser_attempted = False
                if cfg.browser_preferred:
                    browser_attempted = True
                    browser_booking = _book_invitee_with_browser(
                        cfg,
                        name=name,
                        email=email,
                        purpose=purpose,
                        timezone_name=timezone_name,
                        start_time=selected_slot,
                    )
                    if browser_booking:
                        _utter(
                            dispatcher,
                            _booking_success_message(
                                name=name,
                                email=email,
                                purpose=purpose,
                                selected_label=selected_label,
                                confirmation_url=browser_booking.get("final_url"),
                                lang=lang,
                            ),
                            lang,
                            already_localized=_is_sr(lang),
                        )
                        return _clear_schedule_events() + events

                try:
                    booking = _book_invitee(
                        cfg,
                        name=name,
                        email=email,
                        purpose=purpose,
                        timezone_name=timezone_name,
                        start_time=selected_slot,
                    )
                except CalendlyAPIError as exc:
                    logger.warning(
                        "Calendly direct booking failed with status %s; "
                        "trying browser fallback when enabled.",
                        exc.status,
                    )
                    browser_booking = None
                    if not browser_attempted:
                        browser_booking = _book_invitee_with_browser(
                            cfg,
                            name=name,
                            email=email,
                            purpose=purpose,
                            timezone_name=timezone_name,
                            start_time=selected_slot,
                        )
                    if browser_booking:
                        _utter(
                            dispatcher,
                            _booking_success_message(
                                name=name,
                                email=email,
                                purpose=purpose,
                                selected_label=selected_label,
                                confirmation_url=browser_booking.get("final_url"),
                                lang=lang,
                            ),
                            lang,
                            already_localized=_is_sr(lang),
                        )
                        return _clear_schedule_events() + events

                    fallback = _manual_finalize_message(
                        cfg,
                        name=name,
                        email=email,
                        purpose=purpose,
                        selected_label=selected_label,
                        selected_start_time=selected_slot,
                        timezone_name=timezone_name,
                        lang=lang,
                    )
                    if fallback:
                        _utter(dispatcher, fallback, lang, already_localized=_is_sr(lang))
                        return _clear_schedule_events() + events

                    _utter(dispatcher, _direct_booking_error_message(exc), lang)
                    return events + _set_stage("select_slot")

                cancel_url = booking.get("cancel_url")
                reschedule_url = booking.get("reschedule_url")
                _utter(
                    dispatcher,
                    _booking_success_message(
                        name=name,
                        email=email,
                        purpose=purpose,
                        selected_label=selected_label,
                        cancel_url=cancel_url,
                        reschedule_url=reschedule_url,
                        lang=lang,
                    ),
                    lang,
                    already_localized=_is_sr(lang),
                )
                return _clear_schedule_events() + events

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
        except CalendlyAPIError:
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
