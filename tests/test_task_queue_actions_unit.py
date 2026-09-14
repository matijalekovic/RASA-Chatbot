#!/usr/bin/env python3
"""Focused checks for queued chatbot implementation tasks."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rasa_sdk.executor import CollectingDispatcher

from actions.actions import ActionListProjects
from actions.calendly_actions import ActionScheduleMeeting, looks_like_new_schedule_request
from actions.company_actions import ActionAnswerCompanyQuery
from actions.services_actions import ActionAnswerServicesQuery
from actions.team_actions import (
    ActionAnswerTeamQuery,
    _lookup_explicit_role_owner_from_text,
    _lookup_person_from_text,
)


class _Tracker:
    def __init__(self, text, intent, entities=None, slots=None):
        self.latest_message = {
            "text": text,
            "intent": {"name": intent},
            "entities": entities or [],
            "metadata": {},
        }
        self.events = []
        self._slots = slots or {}

    def get_slot(self, name):
        return self._slots.get(name)

    def get_latest_entity_values(self, entity_type):
        for entity in self.latest_message.get("entities", []):
            if entity.get("entity") == entity_type:
                yield entity.get("value")


def _combined_text(dispatcher):
    return "\n".join(
        message.get("text", "")
        for message in dispatcher.messages
        if message.get("text")
    )


def test_region_project_list_is_capped_and_has_cards():
    tracker = _Tracker(
        "show me projects in Europe",
        "ask_projects_list",
    )
    dispatcher = CollectingDispatcher()
    ActionListProjects().run(dispatcher, tracker, {})

    message = dispatcher.messages[-1]
    assert "5 most relevant" in message["text"]
    assert len(message["custom"]["project_cards"]) == 5
    assert all(card["image"] for card in message["custom"]["project_cards"])


def test_service_project_examples_have_thumbnail_cards():
    tracker = _Tracker(
        "show me urbanism projects",
        "ask_service_urbanism",
    )
    dispatcher = CollectingDispatcher()
    ActionAnswerServicesQuery().run(dispatcher, tracker, {})

    card_messages = [
        message
        for message in dispatcher.messages
        if message.get("custom", {}).get("project_cards")
    ]
    assert len(card_messages) == 1
    cards = card_messages[0]["custom"]["project_cards"]
    assert len(cards) == 5
    assert cards[0]["id"] == "doha_metro_depot"
    assert all(card["image"] for card in cards)


def test_project_category_service_filter_has_thumbnail_cards():
    tracker = _Tracker(
        "show me urbanism projects",
        "ask_project_category",
    )
    dispatcher = CollectingDispatcher()
    ActionListProjects().run(dispatcher, tracker, {})

    assert len(dispatcher.messages) == 1
    message = dispatcher.messages[0]
    cards = message["custom"]["project_cards"]
    assert "Urbanism & Masterplan" in message["text"]
    assert len(cards) == 5
    assert cards[0]["id"] == "doha_metro_depot"
    assert all(card["image"] for card in cards)


def test_unknown_office_query_suggests_nearest_office():
    tracker = _Tracker(
        "do you have an office in Madrid?",
        "ask_company_offices",
    )
    dispatcher = CollectingDispatcher()
    ActionAnswerCompanyQuery().run(dispatcher, tracker, {})

    text = dispatcher.messages[0]["text"]
    assert "does not currently list an office in **Madrid**" in text
    assert "**Barcelona, Spain**" in text


def test_company_location_beats_active_project_context():
    tracker = _Tracker(
        "where is the company located?",
        "ask_company_offices",
        slots={"project_name": "sofia_airport"},
    )
    dispatcher = CollectingDispatcher()
    ActionAnswerCompanyQuery().run(dispatcher, tracker, {})

    text = _combined_text(dispatcher)
    assert all(city in text for city in ("Paris", "Belgrade", "Shanghai", "Barcelona", "Lima"))
    assert "Sofia, Bulgaria" not in text


def test_service_office_misroute_delegates_to_company_offices():
    tracker = _Tracker(
        "do you have an office in Spain?",
        "ask_service_working_living",
    )
    dispatcher = CollectingDispatcher()
    ActionAnswerServicesQuery().run(dispatcher, tracker, {})

    text = dispatcher.messages[0]["text"]
    assert "Yes — 1PAX has an office in **Barcelona, Spain**" in text
    assert "office design" not in text.lower()


def test_about_us_values_routes_to_values_content():
    tracker = _Tracker(
        "what does the about us page say about 1PAX values?",
        "nlu_fallback",
    )
    dispatcher = CollectingDispatcher()
    ActionAnswerCompanyQuery().run(dispatcher, tracker, {})

    combined = "\n".join(message["text"] for message in dispatcher.messages)
    assert "The values that guide 1PAX" in combined
    assert "From the About Us story" in combined


def test_generic_innovations_never_fuzzy_match_carla():
    assert _lookup_person_from_text("innovations") is None

    tracker = _Tracker(
        "innovations",
        "ask_about_team_member",
        entities=[{"entity": "person", "value": "carla_miranda"}],
        slots={"project_name": "pachacamac_metro_station"},
    )
    dispatcher = CollectingDispatcher()
    ActionAnswerTeamQuery().run(dispatcher, tracker, {})

    text = _combined_text(dispatcher)
    assert any(term in text for term in ("Ecoport", "PAX", "Skylo"))
    assert "Carla" not in text
    assert "ESADE" not in text


def test_explicit_bim_owner_question_resolves_marko():
    assert _lookup_explicit_role_owner_from_text("who handles BIM?") == "marko_soskic"

    tracker = _Tracker(
        "who handles BIM at 1PAX?",
        "ask_about_team_member",
        entities=[],
    )
    dispatcher = CollectingDispatcher()
    ActionAnswerTeamQuery().run(dispatcher, tracker, {})

    text = _combined_text(dispatcher)
    assert "Marko Soskic" in text
    assert "BIM Manager" in text


def test_explicit_innovation_owner_beats_noisy_person_entity():
    assert (
        _lookup_explicit_role_owner_from_text("who manages patents and innovation?")
        == "carla_miranda"
    )

    tracker = _Tracker(
        "who manages patents and innovation?",
        "ask_about_team_member",
        entities=[{"entity": "person", "value": "marko_soskic"}],
        slots={"person_name": "matija_lekovic"},
    )
    dispatcher = CollectingDispatcher()
    ActionAnswerTeamQuery().run(dispatcher, tracker, {})

    text = _combined_text(dispatcher)
    assert "Carla Miranda" in text
    assert any(term in text for term in ("patent", "innovation", "CCIO"))
    assert "Marko Soskic" not in text


def test_team_topic_clears_stale_project_context():
    tracker = _Tracker(
        "tell me about the team",
        "ask_team_overview",
        slots={"project_name": "sofia_airport"},
    )
    dispatcher = CollectingDispatcher()
    events = ActionAnswerTeamQuery().run(dispatcher, tracker, {})

    assert any(
        event.get("event") == "slot"
        and event.get("name") == "project_name"
        and event.get("value") is None
        for event in events
    )


def test_generic_director_entity_routes_to_studio_leadership():
    tracker = _Tracker(
        "who is the director",
        "ask_about_team_member",
        entities=[{"entity": "person", "value": "director"}],
        slots={"project_name": "pachacamac_metro_station"},
    )
    dispatcher = CollectingDispatcher()
    ActionAnswerTeamQuery().run(dispatcher, tracker, {})

    text = _combined_text(dispatcher)
    assert "Mabel Miranda" in text
    assert "Founder & CEO" in text
    assert "Who would you like" not in text
    assert "Pachac" not in text


def test_founder_question_beats_stale_carla_slot():
    tracker = _Tracker(
        "who founded 1PAX",
        "ask_about_team_member",
        entities=[{"entity": "person", "value": "founder"}],
        slots={"person_name": "carla_miranda"},
    )
    dispatcher = CollectingDispatcher()
    ActionAnswerTeamQuery().run(dispatcher, tracker, {})

    text = _combined_text(dispatcher)
    assert "Mabel Miranda" in text
    assert "2016" in text
    assert "Carla" not in text


def test_construction_supervision_does_not_start_booking():
    tracker = _Tracker(
        "Do you provide construction supervision?",
        "provide_schedule_purpose",
    )
    dispatcher = CollectingDispatcher()
    ActionScheduleMeeting().run(dispatcher, tracker, {})

    text = _combined_text(dispatcher).lower()
    assert "construction phasing" in text
    assert "does **not** list" in text
    assert "contact@1pax.com" in text
    assert "what name" not in text
    assert "your email" not in text


def test_airport_proposal_misroute_returns_service_guidance():
    tracker = _Tracker(
        "I want a proposal for an airport in Dubai",
        "ask_projects_list",
    )
    dispatcher = CollectingDispatcher()
    ActionListProjects().run(dispatcher, tracker, {})

    text = _combined_text(dispatcher).lower()
    assert "airport" in text
    assert "proposal" in text
    assert "contact@1pax.com" in text
    assert "greenfield or brownfield" in text
    assert "not sure" not in text


def test_airport_investor_misroute_returns_company_guidance():
    tracker = _Tracker(
        "I am an investor interested in airport concessions",
        "ask_projects_list",
    )
    dispatcher = CollectingDispatcher()
    ActionListProjects().run(dispatcher, tracker, {})

    text = _combined_text(dispatcher).lower()
    assert any(term in text for term in ("investor", "concession", "partnership"))
    assert not any(message.get("custom", {}).get("project_cards") for message in dispatcher.messages)


def test_book_with_mabel_starts_scheduler_instead_of_biography():
    tracker = _Tracker(
        "book me tomorrow with Mabel about Sofia Airport",
        "ask_about_team_member",
        entities=[{"entity": "person", "value": "mabel_miranda"}],
    )
    dispatcher = CollectingDispatcher()
    ActionAnswerTeamQuery().run(dispatcher, tracker, {})

    text = _combined_text(dispatcher).lower()
    assert any(term in text for term in ("name", "email", "meeting", "timezone"))
    assert "founder and ceo" not in text


def test_flight_booking_is_not_a_meeting_request():
    assert looks_like_new_schedule_request("Can you book me a flight?") is False
    assert looks_like_new_schedule_request("Book a call about an airline terminal") is True


if __name__ == "__main__":
    test_region_project_list_is_capped_and_has_cards()
    test_service_project_examples_have_thumbnail_cards()
    test_project_category_service_filter_has_thumbnail_cards()
    test_unknown_office_query_suggests_nearest_office()
    test_company_location_beats_active_project_context()
    test_service_office_misroute_delegates_to_company_offices()
    test_about_us_values_routes_to_values_content()
    test_generic_innovations_never_fuzzy_match_carla()
    test_explicit_bim_owner_question_resolves_marko()
    test_explicit_innovation_owner_beats_noisy_person_entity()
    test_team_topic_clears_stale_project_context()
    test_generic_director_entity_routes_to_studio_leadership()
    test_founder_question_beats_stale_carla_slot()
    test_construction_supervision_does_not_start_booking()
    test_airport_proposal_misroute_returns_service_guidance()
    test_airport_investor_misroute_returns_company_guidance()
    test_book_with_mabel_starts_scheduler_instead_of_biography()
    test_flight_booking_is_not_a_meeting_request()
    print("Queued chatbot task action checks passed.")
