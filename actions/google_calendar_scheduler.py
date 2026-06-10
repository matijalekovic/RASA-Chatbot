"""Google Calendar scheduling helpers for the 1PAX chatbot.

The action layer owns the conversation. This module owns the scheduling model:
colleague routing, allowed booking windows, Google Calendar free/busy lookup,
and event creation.

Live Google access is intentionally isolated behind GoogleCalendarClient so the
chatbot can be tested end-to-end without Workspace credentials. Set
GOOGLE_CALENDAR_DRY_RUN=true for local smoke tests; set service-account
credentials or keyless service-account impersonation plus Workspace
domain-wide delegation for production booking.
"""

from __future__ import annotations

import json
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


logger = logging.getLogger(__name__)

DEFAULT_TIMEZONE = "Europe/Belgrade"

CALENDAR_SCOPES = (
    "https://www.googleapis.com/auth/calendar.freebusy",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.events.readonly",
)

_WEEKDAY_ALIASES = {
    "mon": 0,
    "monday": 0,
    "tue": 1,
    "tues": 1,
    "tuesday": 1,
    "wed": 2,
    "wednesday": 2,
    "thu": 3,
    "thurs": 3,
    "thursday": 3,
    "fri": 4,
    "friday": 4,
    "sat": 5,
    "saturday": 5,
    "sun": 6,
    "sunday": 6,
}

_COUNTRY_REGION = {
    "CN": "Asia",
    "HK": "Asia",
    "MO": "Asia",
    "TW": "Asia",
    "SG": "Asia",
    "JP": "Asia",
    "KR": "Asia",
    "ES": "Europe",
    "FR": "Europe",
    "RS": "Europe",
    "GB": "Europe",
    "DE": "Europe",
    "IT": "Europe",
    "PE": "LATAM",
    "MX": "LATAM",
    "CO": "LATAM",
    "CL": "LATAM",
    "AR": "LATAM",
    "BR": "LATAM",
    "US": "Americas",
    "CA": "Americas",
}

_LANG_REGION_HINTS = {
    "zh": ("CN", "Asia"),
    "es": ("ES", "Europe"),
    "fr": ("FR", "Europe"),
    "sr": ("RS", "Europe"),
}

_TEXT_HINTS = (
    (re.compile(r"\b(china|chinese|mandarin|shanghai|asia|asian)\b", re.I), "zh", "CN"),
    (re.compile(r"\b(spanish|español|espanol|spain|barcelona)\b", re.I), "es", "ES"),
    (re.compile(r"\b(lima|peru|perú|latin america|latam|south america)\b", re.I), "es", "PE"),
    (re.compile(r"\b(france|french|paris)\b", re.I), "fr", "FR"),
    (re.compile(r"\b(serbia|serbian|belgrade|beograd)\b", re.I), "sr", "RS"),
)


class GoogleCalendarError(RuntimeError):
    """Raised when Google Calendar scheduling cannot continue."""


@dataclass(frozen=True)
class BookingWindow:
    weekday: int
    start: time
    end: time


@dataclass(frozen=True)
class CalendarColleague:
    id: str
    label: str
    office: str
    calendar_id: str
    timezone: str
    languages: Tuple[str, ...]
    regions: Tuple[str, ...]
    booking_windows: Tuple[BookingWindow, ...]
    priority: int = 0
    availability_calendar_id: str = ""

    @property
    def display_name(self) -> str:
        return f"{self.label} ({self.office})"


@dataclass(frozen=True)
class SchedulingContext:
    language: str
    region: str
    region_label: str
    timezone_name: str


@dataclass(frozen=True)
class CalendarSlot:
    start_time: str
    end_time: str
    calendar_id: str
    colleague_id: str
    colleague_label: str
    colleague_office: str
    colleague_timezone: str
    label: str


@dataclass(frozen=True)
class CalendarBooking:
    event_id: str
    html_link: str = ""
    meet_link: str = ""
    dry_run: bool = False


@dataclass(frozen=True)
class GoogleCalendarConfig:
    roster: Tuple[CalendarColleague, ...]
    dry_run: bool
    service_account_file: str
    service_account_json: str
    impersonate_service_account: str
    delegated_subject: str
    application_name: str
    default_timezone: str
    event_duration_minutes: int
    slot_step_minutes: int
    lead_time_minutes: int
    buffer_minutes: int
    max_slots: int
    create_meet: bool
    send_updates: str
    meeting_summary: str

    @property
    def has_credentials(self) -> bool:
        return bool(
            self.service_account_file
            or self.service_account_json
            or self.impersonate_service_account
        )

    @property
    def is_connected(self) -> bool:
        return self.dry_run or (self.has_credentials and bool(self.roster))


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(value, maximum))


def _zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return ZoneInfo(DEFAULT_TIMEZONE)


def _parse_time(value: str) -> time:
    hour, minute = value.strip().split(":", 1)
    return time(int(hour), int(minute))


def _parse_day_range(value: str) -> List[int]:
    key = value.strip().lower()
    if "-" not in key:
        return [_WEEKDAY_ALIASES[key]]
    start_key, end_key = [part.strip() for part in key.split("-", 1)]
    start = _WEEKDAY_ALIASES[start_key]
    end = _WEEKDAY_ALIASES[end_key]
    if start <= end:
        return list(range(start, end + 1))
    return list(range(start, 7)) + list(range(0, end + 1))


def _parse_booking_windows(raw: Any) -> Tuple[BookingWindow, ...]:
    windows: List[BookingWindow] = []
    source = raw or {"mon-fri": [["09:00", "17:00"]]}
    if not isinstance(source, dict):
        source = {"mon-fri": [["09:00", "17:00"]]}

    for day_key, ranges in source.items():
        try:
            weekdays = _parse_day_range(str(day_key))
        except (KeyError, ValueError):
            continue
        for item in ranges or []:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                continue
            try:
                start = _parse_time(str(item[0]))
                end = _parse_time(str(item[1]))
            except (TypeError, ValueError):
                continue
            if start >= end:
                continue
            windows.extend(BookingWindow(day, start, end) for day in weekdays)

    if not windows:
        return _parse_booking_windows({"mon-fri": [["09:00", "17:00"]]})
    return tuple(windows)


def _normalize_lang(value: Optional[str]) -> str:
    raw = (value or "").strip().lower()
    if not raw or raw in {"en", "en-us", "en-gb"}:
        return "en"
    if raw.startswith("zh"):
        return "zh"
    if raw.startswith("pt"):
        return "pt"
    return raw.split("-", 1)[0]


def _normalize_region(value: Optional[str]) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    return re.sub(r"[^A-Za-z0-9]+", "", raw).upper()


def _country_from_locale(locale: str) -> str:
    parts = re.split(r"[-_]", locale or "")
    if len(parts) >= 2 and len(parts[1]) == 2:
        return parts[1].upper()
    return ""


def _country_from_timezone(timezone_name: str) -> str:
    tz = (timezone_name or "").strip()
    direct = {
        "Asia/Shanghai": "CN",
        "Asia/Hong_Kong": "HK",
        "Asia/Singapore": "SG",
        "Europe/Madrid": "ES",
        "Europe/Paris": "FR",
        "Europe/Belgrade": "RS",
        "America/Lima": "PE",
        "America/Mexico_City": "MX",
        "America/Bogota": "CO",
        "America/Santiago": "CL",
        "America/Argentina/Buenos_Aires": "AR",
    }
    if tz in direct:
        return direct[tz]
    if tz.startswith("Asia/"):
        return "CN"
    if tz.startswith("Europe/"):
        return "FR"
    if tz.startswith("America/"):
        return "US"
    return ""


def _region_label(country: str, region: str) -> str:
    if country:
        labels = {
            "CN": "China / Asia",
            "HK": "Hong Kong / Asia",
            "ES": "Spain / Europe",
            "FR": "France / Europe",
            "RS": "Serbia / Europe",
            "PE": "Peru / Latin America",
            "MX": "Mexico / Latin America",
            "US": "Americas",
        }
        return labels.get(country, country)
    return region or "your region"


def detect_scheduling_context(
    *,
    lang: Optional[str],
    metadata: Optional[Dict[str, Any]],
    text: str,
    timezone_name: str,
) -> SchedulingContext:
    metadata = metadata or {}
    language = _normalize_lang(lang)
    country = ""

    for key in ("country", "country_code", "region"):
        country = _normalize_region(str(metadata.get(key) or ""))
        if country:
            break

    locale_values = [
        str(metadata.get("locale") or ""),
        str(metadata.get("browser_locale") or ""),
        str(metadata.get("browser_language") or ""),
    ]
    locale_values.extend(str(item) for item in metadata.get("browser_languages") or [])

    if language == "en":
        for locale in locale_values:
            locale_lang = _normalize_lang(locale)
            if locale_lang != "en":
                language = locale_lang
                break

    if not country:
        for locale in locale_values:
            country = _country_from_locale(locale)
            if country:
                break

    text_language = ""
    text_country = ""
    for pattern, hinted_lang, hinted_country in _TEXT_HINTS:
        if pattern.search(text or ""):
            text_language = hinted_lang
            text_country = hinted_country
            break

    if text_language:
        language = text_language
    if text_country:
        country = text_country

    if not country:
        country = _country_from_timezone(timezone_name)

    if not country and language in _LANG_REGION_HINTS:
        country = _LANG_REGION_HINTS[language][0]

    region = _COUNTRY_REGION.get(country, "")
    if not region and language in _LANG_REGION_HINTS:
        region = _LANG_REGION_HINTS[language][1]
    if not region:
        region = "Global"

    return SchedulingContext(
        language=language,
        region=country or region,
        region_label=_region_label(country, region),
        timezone_name=timezone_name or DEFAULT_TIMEZONE,
    )


def _default_roster() -> Tuple[CalendarColleague, ...]:
    entries = [
        {
            "id": "shanghai",
            "label": os.environ.get("GOOGLE_CALENDAR_SHANGHAI_LABEL", "Shanghai office colleague"),
            "office": "Shanghai",
            "calendar_id": os.environ.get("GOOGLE_CALENDAR_SHANGHAI_CALENDAR_ID", ""),
            "timezone": "Asia/Shanghai",
            "languages": ["zh", "en"],
            "regions": ["CN", "HK", "Asia"],
            "booking_hours": {"mon-fri": [["12:00", "17:00"]]},
            "priority": 90,
        },
        {
            "id": "barcelona",
            "label": os.environ.get("GOOGLE_CALENDAR_BARCELONA_LABEL", "Barcelona office colleague"),
            "office": "Barcelona",
            "calendar_id": os.environ.get("GOOGLE_CALENDAR_BARCELONA_CALENDAR_ID", ""),
            "timezone": "Europe/Madrid",
            "languages": ["es", "en"],
            "regions": ["ES", "Europe"],
            "booking_hours": {"mon-fri": [["10:00", "17:00"]]},
            "priority": 80,
        },
        {
            "id": "lima",
            "label": os.environ.get("GOOGLE_CALENDAR_LIMA_LABEL", "Lima office colleague"),
            "office": "Lima",
            "calendar_id": os.environ.get("GOOGLE_CALENDAR_LIMA_CALENDAR_ID", ""),
            "timezone": "America/Lima",
            "languages": ["es", "en"],
            "regions": ["PE", "LATAM", "Americas"],
            "booking_hours": {"mon-fri": [["10:00", "13:00"]]},
            "priority": 75,
        },
        {
            "id": "paris",
            "label": os.environ.get("GOOGLE_CALENDAR_PARIS_LABEL", "Paris office colleague"),
            "office": "Paris",
            "calendar_id": os.environ.get("GOOGLE_CALENDAR_PARIS_CALENDAR_ID", ""),
            "timezone": "Europe/Paris",
            "languages": ["fr", "en"],
            "regions": ["FR", "Europe", "Global"],
            "booking_hours": {"mon-fri": [["09:30", "17:30"]]},
            "priority": 60,
        },
        {
            "id": "belgrade",
            "label": os.environ.get("GOOGLE_CALENDAR_BELGRADE_LABEL", "Belgrade office colleague"),
            "office": "Belgrade",
            "calendar_id": os.environ.get("GOOGLE_CALENDAR_BELGRADE_CALENDAR_ID", ""),
            "timezone": "Europe/Belgrade",
            "languages": ["sr", "en"],
            "regions": ["RS", "Europe", "Global"],
            "booking_hours": {"mon-fri": [["09:00", "17:00"]]},
            "priority": 55,
        },
    ]
    return tuple(_colleague_from_dict(item) for item in entries)


def _colleague_from_dict(item: Dict[str, Any]) -> CalendarColleague:
    languages = tuple(_normalize_lang(str(lang)) for lang in item.get("languages", ["en"]))
    regions = tuple(_normalize_region(str(region)) for region in item.get("regions", ["Global"]))
    return CalendarColleague(
        id=str(item["id"]).strip(),
        label=str(item.get("label") or item.get("name") or item["id"]).strip(),
        office=str(item.get("office") or item.get("location") or item["id"]).strip(),
        calendar_id=str(item.get("calendar_id") or item.get("calendarId") or "").strip(),
        timezone=str(item.get("timezone") or DEFAULT_TIMEZONE).strip(),
        languages=languages or ("en",),
        regions=regions or ("GLOBAL",),
        booking_windows=_parse_booking_windows(
            item.get("booking_hours") or item.get("booking_windows")
        ),
        priority=int(item.get("priority") or 0),
        availability_calendar_id=str(
            item.get("availability_calendar_id")
            or item.get("availabilityCalendarId")
            or ""
        ).strip(),
    )


def _load_roster_from_env() -> Tuple[CalendarColleague, ...]:
    raw = os.environ.get("GOOGLE_CALENDAR_ROSTER_JSON", "").strip()
    if not raw:
        return _default_roster()
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise GoogleCalendarError("GOOGLE_CALENDAR_ROSTER_JSON is invalid JSON.") from exc
    if not isinstance(data, list):
        raise GoogleCalendarError("GOOGLE_CALENDAR_ROSTER_JSON must be a list.")
    roster = tuple(_colleague_from_dict(item) for item in data if isinstance(item, dict))
    if len(roster) < 1:
        raise GoogleCalendarError("GOOGLE_CALENDAR_ROSTER_JSON did not define any colleagues.")
    return roster


def config_from_env() -> GoogleCalendarConfig:
    return GoogleCalendarConfig(
        roster=_load_roster_from_env(),
        dry_run=_env_bool("GOOGLE_CALENDAR_DRY_RUN", False),
        service_account_file=os.environ.get("GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE", "").strip(),
        service_account_json=os.environ.get("GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON", "").strip(),
        impersonate_service_account=os.environ.get(
            "GOOGLE_CALENDAR_IMPERSONATE_SERVICE_ACCOUNT",
            "",
        ).strip(),
        delegated_subject=os.environ.get("GOOGLE_CALENDAR_DELEGATED_SUBJECT", "").strip(),
        application_name=os.environ.get("GOOGLE_CALENDAR_APPLICATION_NAME", "1PAX Chatbot").strip(),
        default_timezone=os.environ.get("GOOGLE_CALENDAR_DEFAULT_TIMEZONE", DEFAULT_TIMEZONE).strip()
        or DEFAULT_TIMEZONE,
        event_duration_minutes=_env_int("GOOGLE_CALENDAR_EVENT_DURATION_MINUTES", 30, 15, 240),
        slot_step_minutes=_env_int("GOOGLE_CALENDAR_SLOT_STEP_MINUTES", 30, 5, 120),
        lead_time_minutes=_env_int("GOOGLE_CALENDAR_LEAD_TIME_MINUTES", 120, 0, 10080),
        buffer_minutes=_env_int("GOOGLE_CALENDAR_BUFFER_MINUTES", 0, 0, 240),
        max_slots=_env_int("GOOGLE_CALENDAR_MAX_SLOTS", 5, 1, 10),
        create_meet=_env_bool("GOOGLE_CALENDAR_CREATE_MEET", True),
        send_updates=os.environ.get("GOOGLE_CALENDAR_SEND_UPDATES", "all").strip() or "all",
        meeting_summary=os.environ.get(
            "GOOGLE_CALENDAR_EVENT_SUMMARY",
            "1PAX consultation",
        ).strip()
        or "1PAX consultation",
    )


def rank_colleagues(
    roster: Sequence[CalendarColleague],
    context: SchedulingContext,
) -> List[CalendarColleague]:
    language = _normalize_lang(context.language)
    region = _normalize_region(context.region)
    broad_region = _COUNTRY_REGION.get(region, region)

    def score(colleague: CalendarColleague) -> Tuple[int, int, str]:
        regions = {_normalize_region(item) for item in colleague.regions}
        languages = {_normalize_lang(item) for item in colleague.languages}
        value = colleague.priority
        if language in languages:
            value += 100
        elif "en" in languages and language == "en":
            value += 30
        if region and region in regions:
            value += 90
        if broad_region and _normalize_region(broad_region) in regions:
            value += 55
        if "GLOBAL" in regions:
            value += 15
        return value, colleague.priority, colleague.id

    return sorted(roster, key=score, reverse=True)


def colleague_options_payload(colleagues: Sequence[CalendarColleague]) -> str:
    return json.dumps(
        [
            {
                "id": colleague.id,
                "label": colleague.label,
                "office": colleague.office,
                "calendar_id": colleague.calendar_id,
                "timezone": colleague.timezone,
                "languages": list(colleague.languages),
                "regions": list(colleague.regions),
            }
            for colleague in colleagues
        ]
    )


def options_from_payload(payload: Any, roster: Sequence[CalendarColleague]) -> List[CalendarColleague]:
    if not payload:
        return []
    try:
        data = json.loads(payload) if isinstance(payload, str) else payload
    except (TypeError, ValueError):
        return []
    ids = [item.get("id") for item in data if isinstance(item, dict)]
    by_id = {colleague.id: colleague for colleague in roster}
    return [by_id[item] for item in ids if item in by_id]


def colleague_by_id(
    roster: Sequence[CalendarColleague],
    colleague_id: Optional[str],
) -> Optional[CalendarColleague]:
    if not colleague_id:
        return None
    for colleague in roster:
        if colleague.id == colleague_id:
            return colleague
    return None


def parse_colleague_choice(
    text: str,
    options: Sequence[CalendarColleague],
) -> Optional[CalendarColleague]:
    lowered = (text or "").strip().lower()
    if not lowered:
        return None
    match = re.search(r"\b([1-9]|10)\b", lowered)
    if match:
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(options):
            return options[idx]
    for colleague in options:
        haystacks = {
            colleague.id.lower(),
            colleague.label.lower(),
            colleague.office.lower(),
            colleague.display_name.lower(),
        }
        if any(item and item in lowered for item in haystacks):
            return colleague
    return None


def _iso_utc(dt: datetime) -> str:
    return (
        dt.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _parse_google_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _overlaps(
    start: datetime,
    end: datetime,
    busy: Iterable[Tuple[datetime, datetime]],
    buffer: timedelta,
) -> bool:
    checked_start = start - buffer
    checked_end = end + buffer
    return any(checked_start < busy_end and checked_end > busy_start for busy_start, busy_end in busy)


def _booking_windows_between(
    colleague: CalendarColleague,
    range_start: datetime,
    range_end: datetime,
) -> List[Tuple[datetime, datetime]]:
    host_tz = _zone(colleague.timezone)
    local_start = range_start.astimezone(host_tz)
    local_end = range_end.astimezone(host_tz)
    start_date = local_start.date()
    end_date = local_end.date()
    windows: List[Tuple[datetime, datetime]] = []
    current = start_date
    while current <= end_date:
        weekday = current.weekday()
        for window in colleague.booking_windows:
            if window.weekday != weekday:
                continue
            block_start = datetime.combine(current, window.start, tzinfo=host_tz)
            block_end = datetime.combine(current, window.end, tzinfo=host_tz)
            clipped_start = max(block_start, range_start.astimezone(host_tz))
            clipped_end = min(block_end, range_end.astimezone(host_tz))
            if clipped_start < clipped_end:
                windows.append((clipped_start, clipped_end))
        current = current + timedelta(days=1)
    return windows


class GoogleCalendarClient:
    def __init__(self, cfg: GoogleCalendarConfig):
        self.cfg = cfg
        self._services: Dict[str, Any] = {}

    def _credentials(self, subject: Optional[str] = None):
        delegated = subject or self.cfg.delegated_subject or None

        if self.cfg.impersonate_service_account:
            try:
                import google.auth
                from google.auth import impersonated_credentials
            except ImportError as exc:
                raise GoogleCalendarError(
                    "Google auth libraries are not installed. Install google-auth."
                ) from exc

            source_credentials, quota_project_id = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            return impersonated_credentials.Credentials(
                source_credentials=source_credentials,
                target_principal=self.cfg.impersonate_service_account,
                target_scopes=CALENDAR_SCOPES,
                subject=delegated,
                lifetime=3600,
                quota_project_id=quota_project_id,
            )

        if self.cfg.service_account_json:
            try:
                from google.oauth2 import service_account
            except ImportError as exc:
                raise GoogleCalendarError(
                    "Google Calendar libraries are not installed. Install google-api-python-client and google-auth."
                ) from exc
            try:
                info = json.loads(self.cfg.service_account_json)
            except ValueError as exc:
                raise GoogleCalendarError("GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON is invalid JSON.") from exc
            credentials = service_account.Credentials.from_service_account_info(
                info,
                scopes=CALENDAR_SCOPES,
            )
            return credentials.with_subject(delegated) if delegated else credentials

        if self.cfg.service_account_file:
            try:
                from google.oauth2 import service_account
            except ImportError as exc:
                raise GoogleCalendarError(
                    "Google Calendar libraries are not installed. Install google-api-python-client and google-auth."
                ) from exc
            credentials = service_account.Credentials.from_service_account_file(
                self.cfg.service_account_file,
                scopes=CALENDAR_SCOPES,
            )
            return credentials.with_subject(delegated) if delegated else credentials

        if delegated:
            raise GoogleCalendarError("Google Calendar service account credentials are not configured.")
        raise GoogleCalendarError("Google Calendar credentials are not configured.")

    def _service(self, subject: Optional[str] = None):
        if self.cfg.dry_run:
            raise GoogleCalendarError("Dry-run mode does not build a Google service.")
        subject_key = subject or self.cfg.delegated_subject or ""
        if subject_key in self._services:
            return self._services[subject_key]

        try:
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise GoogleCalendarError(
                "Google Calendar libraries are not installed. Install google-api-python-client and google-auth."
            ) from exc

        credentials = self._credentials(subject=subject_key or self.cfg.delegated_subject or None)
        service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
        self._services[subject_key] = service
        return service

    def freebusy(
        self,
        calendar_ids: Sequence[str],
        start: datetime,
        end: datetime,
    ) -> Dict[str, List[Tuple[datetime, datetime]]]:
        if self.cfg.dry_run:
            return {calendar_id: [] for calendar_id in calendar_ids}
        if not self.cfg.has_credentials:
            raise GoogleCalendarError("Google Calendar credentials are not configured.")

        service = self._service()
        body = {
            "timeMin": _iso_utc(start),
            "timeMax": _iso_utc(end),
            "items": [{"id": calendar_id} for calendar_id in calendar_ids],
        }
        data = service.freebusy().query(body=body).execute()
        result: Dict[str, List[Tuple[datetime, datetime]]] = {}
        for calendar_id, value in (data.get("calendars") or {}).items():
            periods = []
            for item in value.get("busy", []):
                if item.get("start") and item.get("end"):
                    periods.append(
                        (_parse_google_dt(item["start"]), _parse_google_dt(item["end"]))
                    )
            result[calendar_id] = periods
        return result

    def availability_blocks(
        self,
        colleague: CalendarColleague,
        start: datetime,
        end: datetime,
    ) -> Optional[List[Tuple[datetime, datetime]]]:
        if not colleague.availability_calendar_id:
            return None
        if self.cfg.dry_run:
            return None
        service = self._service()
        data = (
            service.events()
            .list(
                calendarId=colleague.availability_calendar_id,
                timeMin=_iso_utc(start),
                timeMax=_iso_utc(end),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        blocks: List[Tuple[datetime, datetime]] = []
        for item in data.get("items", []):
            start_value = (item.get("start") or {}).get("dateTime")
            end_value = (item.get("end") or {}).get("dateTime")
            if start_value and end_value:
                blocks.append((_parse_google_dt(start_value), _parse_google_dt(end_value)))
        return blocks

    def create_event(
        self,
        *,
        colleague: CalendarColleague,
        start: datetime,
        end: datetime,
        name: str,
        email: str,
        purpose: str,
        timezone_name: str,
    ) -> CalendarBooking:
        if self.cfg.dry_run:
            event_id = f"dryrun-{colleague.id}-{uuid.uuid4().hex[:10]}"
            return CalendarBooking(
                event_id=event_id,
                html_link=f"https://calendar.google.com/calendar/event?eid={event_id}",
                meet_link="",
                dry_run=True,
            )
        if not colleague.calendar_id:
            raise GoogleCalendarError(f"{colleague.display_name} does not have a calendar_id configured.")

        delegated_subject = (
            colleague.calendar_id
            if "@" in colleague.calendar_id
            else self.cfg.delegated_subject or None
        )
        service = self._service(subject=delegated_subject)
        description = (
            f"Meeting requested through the 1PAX chatbot.\n\n"
            f"Visitor: {name} <{email}>\n"
            f"Purpose: {purpose}\n"
            f"Visitor timezone: {timezone_name}\n"
            f"Suggested host: {colleague.display_name}"
        )
        body: Dict[str, Any] = {
            "summary": self.cfg.meeting_summary,
            "description": description,
            "start": {"dateTime": start.astimezone(_zone(colleague.timezone)).isoformat(), "timeZone": colleague.timezone},
            "end": {"dateTime": end.astimezone(_zone(colleague.timezone)).isoformat(), "timeZone": colleague.timezone},
            "attendees": [{"email": email}],
            "extendedProperties": {
                "private": {
                    "source": "1pax-chatbot",
                    "colleague_id": colleague.id,
                }
            },
        }
        conference_version = 0
        if self.cfg.create_meet:
            conference_version = 1
            body["conferenceData"] = {
                "createRequest": {
                    "requestId": f"1pax-{uuid.uuid4().hex}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            }

        event = (
            service.events()
            .insert(
                calendarId=colleague.calendar_id,
                body=body,
                sendUpdates=self.cfg.send_updates,
                conferenceDataVersion=conference_version,
            )
            .execute()
        )
        meet_link = ""
        for entry in (event.get("conferenceData") or {}).get("entryPoints", []):
            if entry.get("entryPointType") == "video" and entry.get("uri"):
                meet_link = entry["uri"]
                break
        return CalendarBooking(
            event_id=event.get("id", ""),
            html_link=event.get("htmlLink", ""),
            meet_link=meet_link,
            dry_run=False,
        )


def available_slots(
    *,
    cfg: GoogleCalendarConfig,
    client: GoogleCalendarClient,
    colleague: CalendarColleague,
    range_start: datetime,
    range_end: datetime,
    visitor_timezone: str,
    preferred_time_window: Optional[Tuple[int, int]] = None,
    label_formatter,
) -> Tuple[List[CalendarSlot], bool]:
    if not cfg.is_connected:
        raise GoogleCalendarError("Google Calendar credentials are not configured.")
    if not colleague.calendar_id and not cfg.dry_run:
        raise GoogleCalendarError(f"{colleague.display_name} does not have a calendar_id configured.")

    range_start = range_start.astimezone(timezone.utc)
    range_end = range_end.astimezone(timezone.utc)
    now = datetime.now(timezone.utc) + timedelta(minutes=cfg.lead_time_minutes)
    duration = timedelta(minutes=cfg.event_duration_minutes)
    step = timedelta(minutes=cfg.slot_step_minutes)
    buffer = timedelta(minutes=cfg.buffer_minutes)
    calendar_id = colleague.calendar_id or f"dryrun:{colleague.id}"

    busy = client.freebusy([calendar_id], range_start, range_end).get(calendar_id, [])
    blocks = client.availability_blocks(colleague, range_start, range_end)
    if not blocks:
        blocks = _booking_windows_between(colleague, range_start, range_end)

    all_candidates: List[CalendarSlot] = []
    matched_candidates: List[CalendarSlot] = []
    visitor_tz = _zone(visitor_timezone)

    for block_start, block_end in blocks:
        cursor = max(block_start.astimezone(timezone.utc), range_start, now)
        block_end_utc = min(block_end.astimezone(timezone.utc), range_end)
        while cursor + duration <= block_end_utc:
            end = cursor + duration
            if not _overlaps(cursor, end, busy, buffer):
                label = label_formatter(_iso_utc(cursor), visitor_timezone)
                slot = CalendarSlot(
                    start_time=_iso_utc(cursor),
                    end_time=_iso_utc(end),
                    calendar_id=calendar_id,
                    colleague_id=colleague.id,
                    colleague_label=colleague.label,
                    colleague_office=colleague.office,
                    colleague_timezone=colleague.timezone,
                    label=label,
                )
                all_candidates.append(slot)
                if preferred_time_window:
                    local_dt = cursor.astimezone(visitor_tz)
                    local_minute = local_dt.hour * 60 + local_dt.minute
                    if preferred_time_window[0] <= local_minute < preferred_time_window[1]:
                        matched_candidates.append(slot)
                else:
                    matched_candidates.append(slot)
            cursor += step

    if matched_candidates:
        return matched_candidates[: cfg.max_slots], True
    return all_candidates[: cfg.max_slots], False
