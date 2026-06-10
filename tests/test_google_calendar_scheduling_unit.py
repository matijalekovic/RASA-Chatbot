#!/usr/bin/env python3
"""Pure-function checks for Google Calendar scheduling helpers and action flow."""

from pathlib import Path
import json
import os
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rasa_sdk.executor import CollectingDispatcher

import actions.calendly_actions as schedule_actions
import actions.google_calendar_scheduler as gcal


class _Tracker:
    def __init__(self, text, slots=None, metadata=None, intent="ask_schedule_meeting"):
        self.latest_message = {
            "text": text,
            "intent": {"name": intent},
            "entities": [],
            "metadata": metadata or {},
        }
        self._slots = slots or {}

    def get_slot(self, name):
        return self._slots.get(name)


def _with_google_dry_run_env(fn):
    original = dict(os.environ)
    os.environ["SCHEDULING_PROVIDER"] = "google"
    os.environ["GOOGLE_CALENDAR_DRY_RUN"] = "true"
    try:
        fn()
    finally:
        os.environ.clear()
        os.environ.update(original)


def test_context_routes_chinese_visitors_to_shanghai():
    cfg = gcal.config_from_env()
    context = gcal.detect_scheduling_context(
        lang="ZH-HANS",
        metadata={"timezone": "Asia/Shanghai", "browser_locale": "zh-CN"},
        text="I would like to schedule a meeting",
        timezone_name="Asia/Shanghai",
    )
    ranked = gcal.rank_colleagues(cfg.roster, context)
    assert ranked[0].id == "shanghai"


def test_context_routes_spanish_americas_to_lima():
    cfg = gcal.config_from_env()
    context = gcal.detect_scheduling_context(
        lang=None,
        metadata={"timezone": "America/Lima", "browser_locale": "es-PE"},
        text="I would like to schedule a meeting",
        timezone_name="America/Lima",
    )
    ranked = gcal.rank_colleagues(cfg.roster, context)
    assert ranked[0].id == "lima"


def test_keyless_impersonation_counts_as_google_credentials():
    original = dict(os.environ)
    os.environ["SCHEDULING_PROVIDER"] = "google"
    os.environ["GOOGLE_CALENDAR_DRY_RUN"] = "false"
    os.environ["GOOGLE_CALENDAR_IMPERSONATE_SERVICE_ACCOUNT"] = (
        "pax-calendar-scheduler@example-project.iam.gserviceaccount.com"
    )
    try:
        cfg = gcal.config_from_env()
        assert cfg.has_credentials
        assert cfg.is_connected
    finally:
        os.environ.clear()
        os.environ.update(original)


def test_action_suggests_detected_colleague_before_time_collection():
    def run():
        tracker = _Tracker(
            "I would like to schedule a meeting",
            slots={
                "schedule_name": "Priya Shah",
                "schedule_email": "priya@example.com",
                "schedule_purpose": "Airport terminal consultation",
            },
            metadata={"timezone": "America/Lima", "browser_locale": "es-PE"},
        )
        dispatcher = CollectingDispatcher()
        events = schedule_actions.run_calendly_scheduling(dispatcher, tracker, {})

        assert dispatcher.messages
        assert "Lima" in dispatcher.messages[-1]["text"]
        assert dispatcher.messages[-1]["buttons"]
        assert any(
            event.get("name") == "schedule_stage"
            and event.get("value") == "confirm_route"
            for event in events
        )

    _with_google_dry_run_env(run)


def test_action_offers_other_colleagues_when_route_declined():
    def run():
        cfg = gcal.config_from_env()
        context = gcal.detect_scheduling_context(
            lang=None,
            metadata={"timezone": "America/Lima", "browser_locale": "es-PE"},
            text="schedule",
            timezone_name="America/Lima",
        )
        ranked = gcal.rank_colleagues(cfg.roster, context)
        tracker = _Tracker(
            "no",
            slots={
                "schedule_stage": "confirm_route",
                "schedule_name": "Priya Shah",
                "schedule_email": "priya@example.com",
                "schedule_purpose": "Airport terminal consultation",
                "schedule_colleague_id": ranked[0].id,
                "schedule_colleague_options": gcal.colleague_options_payload(ranked),
            },
            metadata={"timezone": "America/Lima", "browser_locale": "es-PE"},
        )
        dispatcher = CollectingDispatcher()
        events = schedule_actions.run_calendly_scheduling(dispatcher, tracker, {})

        assert "Please choose" in dispatcher.messages[-1]["text"]
        assert "Barcelona" in dispatcher.messages[-1]["text"]
        assert any(
            event.get("name") == "schedule_stage"
            and event.get("value") == "choose_route"
            for event in events
        )

    _with_google_dry_run_env(run)


def test_action_books_google_calendar_dry_run_inside_chat():
    def run():
        offered_slots = [
            {
                "start_time": "2099-06-01T04:00:00Z",
                "end_time": "2099-06-01T04:30:00Z",
                "calendar_id": "dryrun:shanghai",
                "colleague_id": "shanghai",
                "colleague_label": "Shanghai office colleague",
                "colleague_office": "Shanghai",
                "colleague_timezone": "Asia/Shanghai",
                "label": "Mon, Jun 1 at 12:00 PM",
            }
        ]
        tracker = _Tracker(
            "yes",
            slots={
                "schedule_stage": "confirm",
                "schedule_name": "Li Chen",
                "schedule_email": "li.chen@example.com",
                "schedule_purpose": "Airport strategy consultation",
                "schedule_time_preference": "2099-06-01 afternoon",
                "schedule_timezone": "Asia/Shanghai",
                "schedule_offered_slots": json.dumps(offered_slots),
                "schedule_selected_slot": "2099-06-01T04:00:00Z",
                "schedule_selected_slot_label": "Mon, Jun 1 at 12:00 PM",
                "schedule_colleague_id": "shanghai",
            },
            metadata={"timezone": "Asia/Shanghai", "browser_locale": "zh-CN"},
            intent="confirm_schedule_booking",
        )
        dispatcher = CollectingDispatcher()
        events = schedule_actions.run_calendly_scheduling(dispatcher, tracker, {})

        assert "You're booked" in dispatcher.messages[-1]["text"]
        assert "dry-run mode" in dispatcher.messages[-1]["text"]
        assert any(
            event.get("name") == "schedule_booking_event_id"
            and str(event.get("value")).startswith("dryrun-shanghai")
            for event in events
        )

    _with_google_dry_run_env(run)


def test_action_requeries_when_translated_user_changes_slot_day():
    def run():
        original_available_slots = schedule_actions._google_available_slots
        captured = {}
        friday_slot = {
            "start_time": "2026-06-12T08:00:00Z",
            "end_time": "2026-06-12T08:30:00Z",
            "calendar_id": "dryrun:barcelona",
            "colleague_id": "barcelona",
            "colleague_label": "Barcelona office colleague",
            "colleague_office": "Barcelona",
            "colleague_timezone": "Europe/Madrid",
            "label": "Friday, Jun 12 at 10:00",
        }
        old_slots = [
            {
                "start_time": "2026-06-10T08:00:00Z",
                "end_time": "2026-06-10T08:30:00Z",
                "calendar_id": "dryrun:barcelona",
                "colleague_id": "barcelona",
                "colleague_label": "Barcelona office colleague",
                "colleague_office": "Barcelona",
                "colleague_timezone": "Europe/Madrid",
                "label": "Wednesday, Jun 10 at 10:00",
            }
        ]

        def fake_available_slots(cfg, colleague, preference, timezone_name, lang):
            captured["preference"] = preference
            captured["timezone_name"] = timezone_name
            captured["lang"] = lang
            return [friday_slot], True

        schedule_actions._google_available_slots = fake_available_slots
        try:
            tracker = _Tracker(
                "I want Friday morning",
                slots={
                    "schedule_stage": "select_slot",
                    "schedule_name": "Marko Simic",
                    "schedule_email": "marko@example.com",
                    "schedule_purpose": "Project consultation",
                    "schedule_time_preference": "tomorrow morning",
                    "schedule_timezone": "Europe/Belgrade",
                    "schedule_offered_slots": json.dumps(old_slots),
                    "schedule_colleague_id": "barcelona",
                },
                metadata={"lang": "SR", "timezone": "Europe/Belgrade"},
                intent="provide_schedule_time_preference",
            )
            dispatcher = CollectingDispatcher()
            events = schedule_actions.run_calendly_scheduling(dispatcher, tracker, {})
        finally:
            schedule_actions._google_available_slots = original_available_slots

        offered_values = [
            event.get("value")
            for event in events
            if event.get("name") == "schedule_offered_slots"
        ]
        assert captured == {
            "preference": "I want Friday morning",
            "timezone_name": "Europe/Belgrade",
            "lang": "SR",
        }
        assert offered_values[0] is None
        assert "2026-06-12T08:00:00Z" in offered_values[-1]
        assert "Petak, 12. jun u 10:00" in dispatcher.messages[-1]["text"]
        assert any(
            event.get("name") == "schedule_stage"
            and event.get("value") == "select_slot"
            for event in events
        )

    _with_google_dry_run_env(run)


def test_action_requeries_when_user_changes_time_at_confirmation():
    def run():
        original_available_slots = schedule_actions._google_available_slots
        captured = {}
        new_slot = {
            "start_time": "2026-06-12T12:00:00Z",
            "end_time": "2026-06-12T12:30:00Z",
            "calendar_id": "dryrun:barcelona",
            "colleague_id": "barcelona",
            "colleague_label": "Barcelona office colleague",
            "colleague_office": "Barcelona",
            "colleague_timezone": "Europe/Madrid",
            "label": "Friday, Jun 12 at 14:00",
        }
        old_slots = [
            {
                "start_time": "2026-06-10T08:00:00Z",
                "end_time": "2026-06-10T08:30:00Z",
                "calendar_id": "dryrun:barcelona",
                "colleague_id": "barcelona",
                "colleague_label": "Barcelona office colleague",
                "colleague_office": "Barcelona",
                "colleague_timezone": "Europe/Madrid",
                "label": "Wednesday, Jun 10 at 10:00",
            }
        ]

        def fake_available_slots(cfg, colleague, preference, timezone_name, lang):
            captured["preference"] = preference
            return [new_slot], True

        schedule_actions._google_available_slots = fake_available_slots
        try:
            tracker = _Tracker(
                "Friday at 2 pm instead",
                slots={
                    "schedule_stage": "confirm",
                    "schedule_name": "Marko Simic",
                    "schedule_email": "marko@example.com",
                    "schedule_purpose": "Project consultation",
                    "schedule_time_preference": "tomorrow morning",
                    "schedule_timezone": "Europe/Belgrade",
                    "schedule_offered_slots": json.dumps(old_slots),
                    "schedule_selected_slot": "2026-06-10T08:00:00Z",
                    "schedule_selected_slot_label": "Wednesday, Jun 10 at 10:00",
                    "schedule_colleague_id": "barcelona",
                },
                metadata={"timezone": "Europe/Belgrade"},
                intent="provide_schedule_time_preference",
            )
            dispatcher = CollectingDispatcher()
            events = schedule_actions.run_calendly_scheduling(dispatcher, tracker, {})
        finally:
            schedule_actions._google_available_slots = original_available_slots

        offered_values = [
            event.get("value")
            for event in events
            if event.get("name") == "schedule_offered_slots"
        ]
        assert captured["preference"] == "Friday at 2 pm instead"
        assert offered_values[0] is None
        assert "2026-06-12T12:00:00Z" in offered_values[-1]
        assert dispatcher.messages[-1]["text"].startswith("I found these available times")

    _with_google_dry_run_env(run)


if __name__ == "__main__":
    test_context_routes_chinese_visitors_to_shanghai()
    test_context_routes_spanish_americas_to_lima()
    test_keyless_impersonation_counts_as_google_credentials()
    test_action_suggests_detected_colleague_before_time_collection()
    test_action_offers_other_colleagues_when_route_declined()
    test_action_books_google_calendar_dry_run_inside_chat()
    test_action_requeries_when_translated_user_changes_slot_day()
    test_action_requeries_when_user_changes_time_at_confirmation()
    print("Google Calendar scheduling unit checks passed.")
