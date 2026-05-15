"""
Calendly scheduling flow for the 1PAX chatbot.

The flow is intentionally action-driven, matching the rest of this bot:
collect name/email/time preference, show live Calendly availability, ask for
confirmation, then create the invitee through Calendly.
"""

import json
import logging
import os
import re
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


@dataclass(frozen=True)
class CalendlyConfig:
    access_token: str
    event_type_uri: str
    scheduling_link: str
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

    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.status = status


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

    return CalendlyConfig(
        access_token=os.environ.get("CALENDLY_ACCESS_TOKEN", "").strip(),
        event_type_uri=event_type_uri,
        scheduling_link=(
            os.environ.get("CALENDLY_SCHEDULING_LINK", "").strip()
            or os.environ.get("CALENDLY_SCHEDULING_URL", "").strip()
        ),
        default_timezone=os.environ.get(
            "CALENDLY_DEFAULT_TIMEZONE",
            _DEFAULT_TIMEZONE,
        ).strip() or _DEFAULT_TIMEZONE,
        max_slots=max(1, min(max_slots, 10)),
        location_kind=os.environ.get("CALENDLY_LOCATION_KIND", "").strip(),
        location_value=os.environ.get("CALENDLY_LOCATION_VALUE", "").strip(),
        event_guests=guests,
    )


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


def _utter(
    dispatcher: CollectingDispatcher,
    text: str,
    lang: Optional[str],
) -> None:
    dispatcher.utter_message(text=translate_response(text, lang))


def _extract_email(text: str) -> Optional[str]:
    match = re.search(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        text,
        flags=re.IGNORECASE,
    )
    return match.group(0).lower() if match else None


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
    if lowered in {"yes", "y", "yeah", "yep", "sure", "ok", "okay", "confirm"}:
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
    if intent == "cancel_schedule_booking":
        return True
    if any(phrase in lowered for phrase in ("cancel", "never mind", "nevermind", "stop")):
        return True
    return stage in {"select_slot", "confirm"} and lowered in {"no", "no thanks", "not now"}


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


def _slot_label(start_time: str, timezone_name: str) -> str:
    tz = _zone(timezone_name)
    dt = _parse_calendly_dt(start_time).astimezone(tz)
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


def _format_slots(slots: List[Dict[str, str]], timezone_name: str) -> str:
    lines = [f"I found these available times ({timezone_name}):"]
    for idx, slot in enumerate(slots, start=1):
        lines.append(f"{idx}. **{slot['label']}**")
    lines.append("")
    lines.append("Reply with a number, or tell me a different day/time.")
    return "\n".join(lines)


def _parse_slot_choice(text: str, slots: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
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

    for slot in slots:
        label = slot["label"].lower()
        if label in lowered or slot["start_time"].lower() in lowered:
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
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        logger.warning("Calendly API returned HTTP %s", exc.code)
        raise CalendlyAPIError("Calendly rejected the request.", exc.code) from exc
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
    timezone_name: str,
    start_time: str,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "event_type": cfg.event_type_uri,
        "start_time": start_time,
        "invitee": {
            "name": name,
            "email": email,
            "timezone": timezone_name,
        },
        "tracking": {
            "utm_source": "1pax_chatbot",
            "utm_campaign": "website_consultation",
        },
    }
    if cfg.location_kind:
        location = {"kind": cfg.location_kind}
        if cfg.location_value:
            location["location"] = cfg.location_value
        body["location"] = location
    if cfg.event_guests:
        body["event_guests"] = list(cfg.event_guests)
    return body


def _book_invitee(
    cfg: CalendlyConfig,
    name: str,
    email: str,
    timezone_name: str,
    start_time: str,
) -> Dict[str, Any]:
    result = _calendly_request(
        cfg,
        "POST",
        "/invitees",
        body=_booking_body(cfg, name, email, timezone_name, start_time),
    )
    return result.get("resource", result)


def _config_unavailable_message(cfg: CalendlyConfig) -> str:
    if cfg.scheduling_link:
        return (
            "I can help with meetings, but live Calendly booking is not connected "
            f"inside the chat yet. You can schedule directly here: "
            f"[Schedule a meeting]({cfg.scheduling_link})"
        )
    return (
        "I can help schedule meetings, but Calendly is not connected inside the "
        "chat yet. Once it is connected, I will be able to show live availability "
        "and book the meeting here."
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

    extracted_time_preference = _extract_time_preference(text, stage)
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
        choice = _parse_slot_choice(text, offered_slots)
        if choice:
            selected_slot = choice["start_time"]
            selected_label = choice["label"]
            events.extend(
                [
                    SlotSet("schedule_selected_slot", selected_slot),
                    SlotSet("schedule_selected_slot_label", selected_label),
                ]
            )
            _utter(
                dispatcher,
                f"Perfect. Should I book **{selected_label}** for **{name}** "
                f"at **{email}**? Reply yes to confirm, or no to cancel.",
                lang,
            )
            return events + _set_stage("confirm")

        if _has_time_words(text):
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
                try:
                    booking = _book_invitee(
                        cfg,
                        name=name,
                        email=email,
                        timezone_name=timezone_name,
                        start_time=selected_slot,
                    )
                except CalendlyAPIError:
                    _utter(
                        dispatcher,
                        "Calendly could not complete the booking right now. "
                        "Please choose another time, or try again shortly.",
                        lang,
                    )
                    return events + _set_stage("select_slot")

                cancel_url = booking.get("cancel_url")
                reschedule_url = booking.get("reschedule_url")
                lines = [
                    f"You're booked: **{selected_label}**.",
                    f"Calendly will send the invitation to **{email}**.",
                ]
                if reschedule_url:
                    lines.append(f"[Reschedule]({reschedule_url})")
                if cancel_url:
                    lines.append(f"[Cancel]({cancel_url})")
                _utter(dispatcher, "\n\n".join(lines), lang)
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
                if cfg.scheduling_link
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
        _utter(dispatcher, _format_slots(offered_slots, timezone_name), lang)
        return events + _set_stage("select_slot")

    _utter(dispatcher, _format_slots(offered_slots, timezone_name), lang)
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
