#!/usr/bin/env python3
"""Pure-function checks for Calendly API scheduling helpers."""

from datetime import datetime, timedelta
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
    assert payload["tracking"]["salesforce_uuid"] == ""
    assert result["cancel_url"].endswith("/test")
    assert result["reschedule_url"].endswith("/test")


def test_api_request_uses_curl_without_leaking_token_in_args():
    original_which = calendly_actions.shutil.which
    original_run = calendly_actions.subprocess.run
    captured = {}

    def fake_which(name):
        assert name == "curl"
        return "/usr/bin/curl"

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        header_arg = cmd[cmd.index("--header") + 1]
        assert header_arg.startswith("@")
        with open(header_arg[1:], encoding="utf-8") as headers:
            captured["headers"] = headers.read()

        class Result:
            stdout = '{"ok": true}\n201'
            stderr = ""

        return Result()

    calendly_actions.shutil.which = fake_which
    calendly_actions.subprocess.run = fake_run
    try:
        result = calendly_actions._calendly_api_request(
            _cfg(),
            "POST",
            "/invitees",
            payload={"hello": "world"},
        )
    finally:
        calendly_actions.shutil.which = original_which
        calendly_actions.subprocess.run = original_run

    assert result == {"ok": True}
    assert "Bearer test-token" in captured["headers"]
    assert "test-token" not in " ".join(captured["cmd"])


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
    test_api_available_slot_times_filters_and_normalizes()
    test_api_booking_payload_contains_invitee_location_and_tracking()
    test_api_request_uses_curl_without_leaking_token_in_args()
    test_browser_booking_runs_as_subprocess_script()
    print("Calendly action unit checks passed.")
