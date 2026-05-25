"""Headless Calendly page automation used as a last-resort booking fallback.

Calendly's Scheduling API is still the preferred path. This module exists for
the hosted booking page case where the invitee form is already prefilled and
Calendly only needs the selected slot and final "Schedule Event" submission.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


DEFAULT_TIMEZONE = "Europe/Belgrade"
SCHEDULE_BUTTON_RE = re.compile(r"^(schedule event|schedule|confirm)$", re.I)
NEXT_BUTTON_RE = re.compile(r"^(next|continue)$", re.I)
SUCCESS_TEXT_RE = re.compile(
    r"(you are scheduled|this meeting is scheduled|scheduled|confirmed)",
    re.I,
)
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


def _date_label_candidates(start_time: str, timezone_name: str) -> Iterable[str]:
    local_dt = parse_datetime(start_time).astimezone(_zone(timezone_name))
    weekday = local_dt.strftime("%A")
    month = local_dt.strftime("%B")
    yield f"{weekday}, {month} {local_dt.day}, {local_dt.year}"
    yield f"{weekday}, {month} {local_dt.day}"
    yield f"{month} {local_dt.day}, {local_dt.year}"
    yield f"{month} {local_dt.day}"
    yield str(local_dt.day)


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


def _click_requested_date(page, start_time: str, timezone_name: str) -> None:
    for _ in range(12):
        for label in _date_label_candidates(start_time, timezone_name):
            button = page.get_by_role(
                "button",
                name=re.compile(rf"^{re.escape(label)}$", re.I),
            )
            try:
                button.first.click(timeout=1000)
                return
            except Exception:
                continue

        next_month = page.get_by_role(
            "button",
            name=re.compile(r"(next month|go to next month|next)", re.I),
        ).first
        try:
            next_month.click(timeout=1000)
            page.wait_for_timeout(250)
        except Exception:
            return


def _select_requested_slot(page, start_time: str, timezone_name: str, timeout_ms: int) -> None:
    _click_requested_date(page, start_time, timezone_name)

    for label in _time_label_candidates(start_time, timezone_name):
        button = page.get_by_role(
            "button",
            name=re.compile(rf"\b{re.escape(label)}\b", re.I),
        )
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
