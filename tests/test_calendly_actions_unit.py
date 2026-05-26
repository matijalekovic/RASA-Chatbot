#!/usr/bin/env python3
"""Pure-function checks for Calendly API scheduling helpers."""

from datetime import datetime, timedelta
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import actions.calendly_actions as calendly_actions


def _cfg() -> calendly_actions.CalendlyConfig:
    return calendly_actions.CalendlyConfig(
        scheduling_link="https://calendly.com/communications-1pax/30min",
        access_token="test-token",
        event_type_uri="https://api.calendly.com/event_types/test",
        location_kind="google_conference",
        allow_link_fallback=True,
        browser_fallback=True,
        browser_headless=True,
        browser_timeout_seconds=30,
        browser_executable_path="",
        default_timezone="Europe/Belgrade",
        max_slots=5,
    )


def test_api_available_slot_times_filters_and_normalizes():
    original = calendly_actions._calendly_api_request

    def fake_request(cfg, method, path, query=None, payload=None, timeout=15.0):
        assert method == "GET"
        assert path == "/event_type_available_times"
        assert query["event_type"] == cfg.event_type_uri
        return {
            "collection": [
                {
                    "start_time": "2026-05-29T08:00:00Z",
                    "status": "available",
                    "invitees_remaining": 1,
                },
                {
                    "start_time": "2026-05-29T08:30:00+00:00",
                    "status": "available",
                    "invitees_remaining": 0,
                },
                {
                    "start_time": "2026-05-29T09:00:00Z",
                    "status": "unavailable",
                    "invitees_remaining": 1,
                },
            ]
        }

    calendly_actions._calendly_api_request = fake_request
    try:
        start = datetime.fromisoformat("2026-05-29T00:00:00+02:00")
        end = start + timedelta(days=1)
        assert calendly_actions._api_available_slot_times(_cfg(), start, end) == [
            "2026-05-29T08:00:00Z"
        ]
    finally:
        calendly_actions._calendly_api_request = original


def test_api_booking_payload_contains_invitee_location_and_tracking():
    captured = {}
    original = calendly_actions._calendly_api_request

    def fake_request(cfg, method, path, query=None, payload=None, timeout=15.0):
        captured.update({"method": method, "path": path, "payload": payload})
        return {
            "resource": {
                "uri": "https://api.calendly.com/invitees/test",
                "cancel_url": "https://calendly.com/cancellations/test",
                "reschedule_url": "https://calendly.com/reschedulings/test",
            }
        }

    calendly_actions._calendly_api_request = fake_request
    try:
        result = calendly_actions._book_invitee_with_api(
            _cfg(),
            name="Matija Lekovic",
            email="matija@example.com",
            purpose="Project consultation",
            timezone_name="Europe/Belgrade",
            start_time="2026-05-29T08:00:00Z",
        )
    finally:
        calendly_actions._calendly_api_request = original

    assert captured["method"] == "POST"
    assert captured["path"] == "/invitees"
    payload = captured["payload"]
    assert payload["invitee"]["name"] == "Matija Lekovic"
    assert payload["invitee"]["email"] == "matija@example.com"
    assert payload["invitee"]["timezone"] == "Europe/Belgrade"
    assert payload["location"] == {"kind": "google_conference"}
    assert payload["questions_and_answers"][0]["answer"] == "Project consultation"
    assert payload["tracking"]["utm_source"] == "1pax_chatbot"
    assert result["cancel_url"].endswith("/test")
    assert result["reschedule_url"].endswith("/test")


if __name__ == "__main__":
    test_api_available_slot_times_filters_and_normalizes()
    test_api_booking_payload_contains_invitee_location_and_tracking()
    print("Calendly action unit checks passed.")
