#!/usr/bin/env python3
"""Pure-function checks for Calendly hosted-page scheduling helpers."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import actions.calendly_actions as calendly_actions


def test_confirmation_link_fallback_defaults_off():
    original_env = dict(calendly_actions.os.environ)
    calendly_actions.os.environ.clear()
    calendly_actions.os.environ.update(
        {
            "CALENDLY_SCHEDULING_LINK": "https://calendly.com/communications-1pax/30min",
        }
    )
    try:
        cfg = calendly_actions._config_from_env()
    finally:
        calendly_actions.os.environ.clear()
        calendly_actions.os.environ.update(original_env)

    assert cfg.allow_link_fallback is True
    assert cfg.browser_fallback is True
    assert cfg.allow_confirmation_link_fallback is False
    assert cfg.browser_timeout_seconds == 45


def _cfg() -> calendly_actions.CalendlyConfig:
    return calendly_actions.CalendlyConfig(
        scheduling_link="https://calendly.com/communications-1pax/30min",
        access_token="test-token",
        event_type_uri="https://api.calendly.com/event_types/test",
        location_kind="google_conference",
        allow_link_fallback=True,
        allow_confirmation_link_fallback=False,
        browser_fallback=True,
        browser_headless=True,
        browser_timeout_seconds=30,
        browser_executable_path="",
        default_timezone="Europe/Belgrade",
        max_slots=5,
    )


def test_booking_api_runtime_is_removed_even_when_credentials_exist():
    cfg = _cfg()
    assert cfg.is_connected is True
    assert cfg.availability_api_connected is True
    assert not hasattr(calendly_actions, "_calendly_api_request")
    assert not hasattr(calendly_actions, "_book_invitee_with_api")


def test_api_available_slot_times_filters_and_normalizes():
    original = calendly_actions._calendly_api_get

    def fake_get(cfg, path, query=None, timeout=15.0):
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

    calendly_actions._calendly_api_get = fake_get
    try:
        start = calendly_actions.datetime.fromisoformat("2026-05-29T00:00:00+02:00")
        end = start + calendly_actions.timedelta(days=1)
        assert calendly_actions._api_available_slot_times(_cfg(), start, end) == [
            "2026-05-29T08:00:00Z"
        ]
    finally:
        calendly_actions._calendly_api_get = original


def test_available_slots_prefers_read_only_api_before_hosted_page():
    import actions.calendly_browser as calendly_browser

    original_api = calendly_actions._api_available_slot_times
    original_browser = calendly_browser.find_calendly_available_slots
    captured = {}

    def fake_api(cfg, start, end):
        captured["api_called"] = True
        return [
            "2026-05-29T07:00:00Z",
            "2026-05-29T09:00:00Z",
            "2026-05-29T15:00:00Z",
        ]

    def fake_find_slots(**kwargs):
        raise AssertionError("Hosted page lookup should not run when API returns slots")

    calendly_actions._api_available_slot_times = fake_api
    calendly_browser.find_calendly_available_slots = fake_find_slots
    try:
        slots, matched = calendly_actions._available_slots(
            _cfg(),
            "Friday morning",
            "Europe/Belgrade",
        )
    finally:
        calendly_actions._api_available_slot_times = original_api
        calendly_browser.find_calendly_available_slots = original_browser

    assert captured["api_called"] is True
    assert matched is True
    assert [slot["start_time"] for slot in slots] == [
        "2026-05-29T07:00:00Z",
        "2026-05-29T09:00:00Z",
    ]


def test_browser_booking_runs_as_subprocess_script():
    original_run = calendly_actions.subprocess.run
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs

        class Result:
            returncode = 0
            stdout = (
                '{"scheduled": true, "final_url": "https://calendly.com/scheduled", '
                '"message": "ok", "confirmation_text": "confirmed"}'
            )
            stderr = ""

        return Result()

    calendly_actions.subprocess.run = fake_run
    try:
        result = calendly_actions._book_invitee_with_browser(
            _cfg(),
            name="Matija Lekovic",
            email="matija@example.com",
            purpose="Project consultation",
            timezone_name="Europe/Belgrade",
            start_time="2026-05-29T08:00:00Z",
        )
    finally:
        calendly_actions.subprocess.run = original_run

    assert result["final_url"] == "https://calendly.com/scheduled"
    assert captured["cmd"][1].endswith("calendly_browser.py")
    assert "--link" in captured["cmd"]
    assert "--start-time" in captured["cmd"]
    assert captured["kwargs"]["capture_output"] is True
    assert captured["kwargs"]["text"] is True


if __name__ == "__main__":
    test_confirmation_link_fallback_defaults_off()
    test_booking_api_runtime_is_removed_even_when_credentials_exist()
    test_api_available_slot_times_filters_and_normalizes()
    test_available_slots_prefers_read_only_api_before_hosted_page()
    test_browser_booking_runs_as_subprocess_script()
    print("Calendly action unit checks passed.")
