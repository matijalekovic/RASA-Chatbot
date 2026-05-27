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


def test_api_runtime_is_removed_even_when_credentials_exist():
    cfg = _cfg()
    assert cfg.is_connected is True
    assert not hasattr(cfg, "api_connected")
    assert not hasattr(cfg, "access_token")
    assert not hasattr(cfg, "event_type_uri")
    assert not hasattr(calendly_actions, "_calendly_api_request")
    assert not hasattr(calendly_actions, "_api_available_slot_times")
    assert not hasattr(calendly_actions, "_book_invitee_with_api")


def test_available_slots_uses_hosted_page_only():
    import actions.calendly_browser as calendly_browser

    original = calendly_browser.find_calendly_available_slots
    captured = {}

    def fake_find_slots(**kwargs):
        captured.update(kwargs)
        return [
            "2026-05-29T07:00:00Z",
            "2026-05-29T09:00:00Z",
            "2026-05-29T15:00:00Z",
        ]

    calendly_browser.find_calendly_available_slots = fake_find_slots
    try:
        slots, matched = calendly_actions._available_slots(
            _cfg(),
            "Friday morning",
            "Europe/Belgrade",
        )
    finally:
        calendly_browser.find_calendly_available_slots = original

    assert captured["scheduling_link"] == "https://calendly.com/communications-1pax/30min"
    assert captured["timezone_name"] == "Europe/Belgrade"
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
    test_api_runtime_is_removed_even_when_credentials_exist()
    test_available_slots_uses_hosted_page_only()
    test_browser_booking_runs_as_subprocess_script()
    print("Calendly action unit checks passed.")
