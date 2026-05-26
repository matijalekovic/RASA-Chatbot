"""Headless Calendly hosted-page automation.

The chatbot uses Calendly's public booking page as the source of truth: inspect
available times, select the chosen slot, fill the prefilled invitee details, and
submit the hosted form.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
from dataclasses import asdict, dataclass
from datetime import datetime, time, timedelta, timezone
from typing import Iterable, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


DEFAULT_TIMEZONE = "Europe/Belgrade"
SCHEDULE_BUTTON_RE = re.compile(r"^(schedule event|schedule|confirm)$", re.I)
NEXT_BUTTON_RE = re.compile(r"^(next|continue)$", re.I)
SUCCESS_TEXT_RE = re.compile(
    r"(you are scheduled|this meeting is scheduled|scheduled|confirmed)",
    re.I,
)
COOKIE_BUTTON_RE = re.compile(
    r"^(i understand|accept all|accept|agree|decline)$",
    re.I,
)
TIME_BUTTON_RE = re.compile(r"^\s*(\d{1,2}):(\d{2})(?:\s*([AaPp]\.?[Mm]\.?))?\s*$")
SLOT_SEGMENT_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$"
)


@dataclass(frozen=True)
class CalendlyBrowserResult:
    scheduled: bool
    final_url: str
    message: str = ""
    confirmation_text: str = ""


class CalendlyBrowserError(RuntimeError):
    """Raised when browser automation cannot complete the Calendly flow."""


def _zone(name: Optional[str]) -> ZoneInfo:
    try:
        return ZoneInfo(name or DEFAULT_TIMEZONE)
    except ZoneInfoNotFoundError:
        return ZoneInfo(DEFAULT_TIMEZONE)


def parse_datetime(value: str) -> datetime:
    """Parse Calendly/RFC3339-ish datetimes into an aware UTC datetime."""

    normalized = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def calendly_slot_segment(start_time: str, timezone_name: str = DEFAULT_TIMEZONE) -> str:
    """Return Calendly's path segment for an exact selected start time."""

    local_dt = parse_datetime(start_time).astimezone(_zone(timezone_name))
    return local_dt.replace(microsecond=0).isoformat()


def build_calendly_scheduling_url(
    scheduling_link: str,
    name: str,
    email: str,
    purpose: str,
    start_time: Optional[str] = None,
    timezone_name: str = DEFAULT_TIMEZONE,
) -> str:
    """Build a prefilled Calendly URL, optionally pinned to a specific slot."""

    if not scheduling_link:
        raise ValueError("scheduling_link is required")

    parsed = urllib.parse.urlsplit(scheduling_link)
    path_parts = [part for part in parsed.path.split("/") if part]

    if start_time:
        slot_segment = calendly_slot_segment(start_time, timezone_name)
        if path_parts and SLOT_SEGMENT_RE.match(urllib.parse.unquote(path_parts[-1])):
            path_parts[-1] = urllib.parse.quote(slot_segment, safe=":+-T")
        else:
            path_parts.append(urllib.parse.quote(slot_segment, safe=":+-T"))

    query = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    query.update(
        {
            "name": name,
            "email": email,
            "a1": purpose,
            "timezone": timezone_name,
            "utm_source": "1pax_chatbot",
            "utm_medium": "chatbot",
            "utm_campaign": "website_consultation",
            "utm_content": purpose[:255],
            "utm_term": "meeting_request",
        }
    )

    return urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            "/" + "/".join(path_parts),
            urllib.parse.urlencode(query),
            parsed.fragment,
        )
    )


def _time_label_candidates(start_time: str, timezone_name: str) -> Iterable[str]:
    local_dt = parse_datetime(start_time).astimezone(_zone(timezone_name))
    hour_12 = str((local_dt.hour % 12) or 12)
    minute = f"{local_dt.minute:02d}"
    suffix = "AM" if local_dt.hour < 12 else "PM"
    yield f"{local_dt.hour}:{minute}"
    yield f"{local_dt.hour:02d}:{minute}"
    yield f"{hour_12}:{minute}"
    yield f"{hour_12}:{minute}{suffix}"
    yield f"{hour_12}:{minute} {suffix}"
    yield f"{hour_12}:{minute}{suffix.lower()}"
    yield f"{hour_12}:{minute} {suffix.lower()}"


def _date_label_candidates(
    start_time: str,
    timezone_name: str,
    include_day_only: bool = True,
) -> Iterable[str]:
    local_dt = parse_datetime(start_time).astimezone(_zone(timezone_name))
    weekday = local_dt.strftime("%A")
    month = local_dt.strftime("%B")
    yield f"{weekday}, {month} {local_dt.day}, {local_dt.year}"
    yield f"{weekday}, {month} {local_dt.day}"
    yield f"{month} {local_dt.day}, {local_dt.year}"
    yield f"{month} {local_dt.day}"
    if include_day_only:
        yield str(local_dt.day)


def _open_requested_month(page, day, timezone_name: str) -> bool:
    month_label = datetime.combine(day, time.min, tzinfo=_zone(timezone_name)).strftime(
        "%B %Y"
    )

    for _ in range(12):
        if _has_visible(page.get_by_text(re.compile(rf"^{re.escape(month_label)}$", re.I))):
            return True

        next_month = page.get_by_role(
            "button",
            name=re.compile(r"(next month|go to next month|next)", re.I),
        ).first
        try:
            next_month.click(timeout=1000)
            page.wait_for_timeout(250)
        except Exception:
            return False

    return False


def _visible_count(locator) -> int:
    try:
        return locator.count()
    except Exception:
        return 0


def _has_visible(locator) -> bool:
    for index in range(_visible_count(locator)):
        try:
            if locator.nth(index).is_visible(timeout=500):
                return True
        except Exception:
            continue
    return False


def _details_page_ready(page) -> bool:
    if _has_visible(page.locator("input[type='email'], input[name='email']")):
        return True
    if _has_visible(page.get_by_role("button", name=SCHEDULE_BUTTON_RE)):
        return True
    return False


def _dismiss_cookie_banner(page) -> None:
    button = page.get_by_role("button", name=COOKIE_BUTTON_RE).last
    try:
        button.click(timeout=1500)
        page.wait_for_timeout(250)
    except Exception:
        pass


def _fill_first(page, selector: str, value: str) -> bool:
    locator = page.locator(selector)
    count = _visible_count(locator)
    if not count:
        return False
    for index in range(count):
        item = locator.nth(index)
        try:
            if item.is_visible(timeout=500):
                item.fill(value, timeout=2000)
                return True
        except Exception:
            continue
    return False


def _button_by_name(page, label: str):
    exact = page.get_by_role("button", name=label)
    if _visible_count(exact):
        return exact
    return page.get_by_role(
        "button",
        name=re.compile(rf"^{re.escape(label)}$", re.I),
    )


def _parse_visible_time(label: str, day, timezone_name: str) -> Optional[datetime]:
    match = TIME_BUTTON_RE.match(" ".join(label.split()))
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2))
    meridiem = (match.group(3) or "").replace(".", "").lower()
    if meridiem:
        if hour < 1 or hour > 12:
            return None
        if meridiem == "pm" and hour != 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0
    if hour > 23 or minute > 59:
        return None

    return datetime.combine(day, time(hour, minute), tzinfo=_zone(timezone_name))


def _visible_time_buttons(page) -> Iterable[str]:
    buttons = page.locator("button")
    count = _visible_count(buttons)
    for index in range(count):
        button = buttons.nth(index)
        try:
            if not button.is_visible(timeout=500):
                continue
            text = " ".join(button.inner_text(timeout=1000).split())
        except Exception:
            continue
        if TIME_BUTTON_RE.match(text):
            yield text


def find_calendly_available_slots(
    scheduling_link: str,
    range_start: datetime,
    range_end: datetime,
    timezone_name: str = DEFAULT_TIMEZONE,
    max_slots: int = 5,
    timeout_seconds: int = 30,
    headless: bool = True,
    executable_path: Optional[str] = None,
) -> list[str]:
    """Return available hosted-page slot start times as UTC ISO strings."""

    if not scheduling_link:
        raise CalendlyBrowserError("scheduling_link is required")

    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise CalendlyBrowserError(
            "Playwright is not installed. Install it with: "
            "python -m pip install playwright && python -m playwright install chromium"
        ) from exc

    tz = _zone(timezone_name)
    start = range_start.astimezone(tz)
    end = range_end.astimezone(tz)
    if end <= start:
        return []

    timeout_ms = max(5, timeout_seconds) * 1000
    parsed = urllib.parse.urlsplit(scheduling_link)
    query = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    query["timezone"] = timezone_name
    url = urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urllib.parse.urlencode(query),
            parsed.fragment,
        )
    )

    launch_kwargs = {
        "headless": headless,
        "args": ["--no-sandbox", "--disable-dev-shm-usage"],
    }
    if executable_path:
        launch_kwargs["executable_path"] = executable_path

    slots: list[str] = []
    seen: set[str] = set()
    first_day = start.date()
    last_day = (end - timedelta(microseconds=1)).date()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**launch_kwargs)
        page = browser.new_page()
        page.set_default_timeout(timeout_ms)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except PlaywrightTimeoutError:
                pass
            _dismiss_cookie_banner(page)

            day = first_day
            while day <= last_day and len(slots) < max_slots:
                probe = datetime.combine(day, time.min, tzinfo=tz).isoformat()
                if not _open_requested_month(page, day, timezone_name):
                    day += timedelta(days=1)
                    continue
                if not _click_requested_date(
                    page,
                    probe,
                    timezone_name,
                    include_day_only=True,
                    advance_months=False,
                ):
                    day += timedelta(days=1)
                    continue
                page.wait_for_timeout(500)

                for label in _visible_time_buttons(page):
                    local_dt = _parse_visible_time(label, day, timezone_name)
                    if not local_dt or local_dt < start or local_dt >= end:
                        continue
                    value = (
                        local_dt.astimezone(timezone.utc)
                        .replace(microsecond=0)
                        .isoformat()
                        .replace("+00:00", "Z")
                    )
                    if value in seen:
                        continue
                    seen.add(value)
                    slots.append(value)
                    if len(slots) >= max_slots:
                        break

                day += timedelta(days=1)
        finally:
            browser.close()

    return slots


def _click_requested_date(
    page,
    start_time: str,
    timezone_name: str,
    include_day_only: bool = True,
    advance_months: bool = True,
) -> bool:
    for _ in range(12):
        candidate_found = False
        for label in _date_label_candidates(
            start_time,
            timezone_name,
            include_day_only=include_day_only,
        ):
            button = _button_by_name(page, label)
            try:
                if button.count():
                    candidate_found = True
            except Exception:
                pass
            try:
                button.first.click(timeout=1000)
                return True
            except Exception:
                continue

        if candidate_found:
            return False

        if not advance_months:
            return False

        next_month = page.get_by_role(
            "button",
            name=re.compile(r"(next month|go to next month|next)", re.I),
        ).first
        try:
            next_month.click(timeout=1000)
            page.wait_for_timeout(250)
        except Exception:
            return False
    return False


def _select_requested_slot(page, start_time: str, timezone_name: str, timeout_ms: int) -> None:
    if not _click_requested_date(page, start_time, timezone_name):
        raise CalendlyBrowserError("The requested Calendly date was not visible.")

    for label in _time_label_candidates(start_time, timezone_name):
        button = _button_by_name(page, label)
        try:
            button.first.click(timeout=2500)
            next_button = page.get_by_role("button", name=NEXT_BUTTON_RE).first
            next_button.click(timeout=timeout_ms)
            page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            return
        except Exception:
            continue

    raise CalendlyBrowserError("The requested Calendly time slot was not visible.")


def book_calendly_event(
    scheduling_link: str,
    name: str,
    email: str,
    purpose: str,
    start_time: Optional[str] = None,
    timezone_name: str = DEFAULT_TIMEZONE,
    timeout_seconds: int = 30,
    headless: bool = True,
    executable_path: Optional[str] = None,
    dry_run: bool = False,
) -> CalendlyBrowserResult:
    """Open Calendly, select/fill the requested slot, and submit the booking."""

    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise CalendlyBrowserError(
            "Playwright is not installed. Install it with: "
            "python -m pip install playwright && python -m playwright install chromium"
        ) from exc

    timeout_ms = max(5, timeout_seconds) * 1000
    url = build_calendly_scheduling_url(
        scheduling_link,
        name=name,
        email=email,
        purpose=purpose,
        start_time=start_time,
        timezone_name=timezone_name,
    )

    launch_kwargs = {
        "headless": headless,
        "args": ["--no-sandbox", "--disable-dev-shm-usage"],
    }
    if executable_path:
        launch_kwargs["executable_path"] = executable_path

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**launch_kwargs)
        page = browser.new_page()
        page.set_default_timeout(timeout_ms)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)

            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except PlaywrightTimeoutError:
                pass
            _dismiss_cookie_banner(page)

            if not _details_page_ready(page):
                if not start_time:
                    raise CalendlyBrowserError(
                        "Calendly did not open on the details page, and no start time "
                        "was provided for slot selection."
                    )
                _select_requested_slot(page, start_time, timezone_name, timeout_ms)

            _fill_first(page, "input[name='name'], input[autocomplete='name']", name)
            _fill_first(page, "input[type='email'], input[name='email']", email)
            _fill_first(page, "textarea", purpose)

            if dry_run:
                return CalendlyBrowserResult(
                    scheduled=False,
                    final_url=page.url,
                    message="Dry run stopped before clicking Schedule Event.",
                    confirmation_text="",
                )

            page.get_by_role("button", name=SCHEDULE_BUTTON_RE).first.click(
                timeout=timeout_ms
            )

            try:
                page.wait_for_load_state("networkidle", timeout=timeout_ms)
            except PlaywrightTimeoutError:
                pass

            try:
                page.get_by_text(SUCCESS_TEXT_RE).first.wait_for(timeout=timeout_ms)
            except PlaywrightTimeoutError as exc:
                raise CalendlyBrowserError(
                    "Calendly did not show a booking confirmation after submission."
                ) from exc

            body_text = page.locator("body").inner_text(timeout=2000)
            confirmation = "\n".join(
                line.strip() for line in body_text.splitlines() if line.strip()
            )[:1200]
            return CalendlyBrowserResult(
                scheduled=True,
                final_url=page.url,
                message="Calendly booking completed through the hosted page.",
                confirmation_text=confirmation,
            )
        finally:
            browser.close()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Book a prefilled Calendly event through the hosted page."
    )
    parser.add_argument("--link", required=True, help="Base Calendly scheduling link")
    parser.add_argument("--name", required=True, help="Invitee name")
    parser.add_argument("--email", required=True, help="Invitee email")
    parser.add_argument("--purpose", required=True, help="Purpose / first answer text")
    parser.add_argument(
        "--start-time",
        help="Selected slot start time, e.g. 2026-05-29T08:30:00Z",
    )
    parser.add_argument(
        "--timezone",
        default=DEFAULT_TIMEZONE,
        help="Calendly display timezone",
    )
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument(
        "--executable-path",
        help="Optional Chromium/Chrome executable path",
    )
    parser.add_argument(
        "--headful",
        action="store_true",
        help="Show the browser window",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fill the page but do not submit",
    )
    args = parser.parse_args(argv)

    result = book_calendly_event(
        scheduling_link=args.link,
        name=args.name,
        email=args.email,
        purpose=args.purpose,
        start_time=args.start_time,
        timezone_name=args.timezone,
        timeout_seconds=args.timeout_seconds,
        headless=not args.headful,
        executable_path=args.executable_path,
        dry_run=args.dry_run,
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
