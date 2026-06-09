#!/usr/bin/env python3
"""Pure-function checks for project-name resolution and detail routing."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from actions.actions import (
    ActionListProjects,
    ActionHandleOutOfScope,
    _fuzzy_match_project,
    _intent_to_info_type,
    _looks_like_project_geo_query,
    _project_geo_result,
    _resolve_project,
)
from actions.projects_data import PROJECTS


def test_every_display_name_maps_to_itself():
    failures = []
    for key, project in PROJECTS.items():
        text = f"Tell me about {project['display_name']}"
        resolved = _fuzzy_match_project(text)
        if resolved != key:
            failures.append((key, resolved, project["display_name"]))

    assert not failures, failures


def test_title_words_do_not_hijack_general_project_questions():
    examples = [
        "Aéroport de Marseille Provence – Architectural Assistance for Commercial Facilities",
        "Félix Eboué Cayenne Airport – Interior Design",
        "French Embassy – Architectural Design",
        "Belgrade Metro Network – Line 1 Phase 1 Architectural Design",
        "Tocumen International Airport – Fire Safety Strategy Review",
    ]

    for title in examples:
        project_key = _fuzzy_match_project(f"Please tell me about {title}")
        assert project_key
        assert (
            _intent_to_info_type(
                "ask_project_architect",
                f"Please tell me about {title}",
                project_key,
            )
            == "about_project"
        )


def test_explicit_detail_question_still_wins_after_title_stripping():
    text = (
        "Who was the architect for "
        "Aéroport de Marseille Provence – Architectural Assistance for Commercial Facilities?"
    )
    project_key = _fuzzy_match_project(text)

    assert project_key == "marseille_commercial_assistance"
    assert _intent_to_info_type("ask_about_project", text, project_key) == "architect"


def test_named_project_token_beats_generic_airport_project_alias():
    assert _fuzzy_match_project("tell me about the Kigali airport project") == "kigali_airport"
    assert _fuzzy_match_project("nice airport project") == "nice_airport"
    assert _fuzzy_match_project("tell me about the biggest project") == "sofia_airport"


def test_partial_title_residue_still_routes_to_overview():
    text = "Please tell me about Aéroport de Marseille Provence Architectural Assistance"
    project_key = "marseille_commercial_assistance"

    assert _intent_to_info_type("ask_project_architect", text, project_key) == "about_project"


def test_current_website_titles_resolve_to_expected_projects():
    expected = {
        "Al Wakrah Metro Depot Masterplan": "doha_metro_depot",
        "Belgrade Airport Administration Building": "belgrade_admin_building",
        "Belgrade Airport Main Fire Station": "belgrade_fire_station",
        "Bordeaux International Airport - Hall B Terminal New Facades": "bordeaux_airport",
        "Hangar for Air Guyanne, Cayenne Airport": "air_guyane_hangar",
        "Industrial Building for Baggage Handling System – Architectural Design": "cdg_baggage_building",
        "Landside Design - Nikola Tesla Airport": "belgrade_nikola_tesla_landside",
        "Nikola Tesla International Airport Wayfinding signage design": "belgrade_wayfinding",
        "Pointe-à-Pitre International Airport - New extension": "pointe_a_pitre_t1",
        "Pointe-à-Pitre International Airport - T2 Extension": "pointe_a_pitre_t2",
        "Santiago International Airport - Wayfinding Design": "santiago_wayfinding",
    }

    failures = []
    for title, project_key in expected.items():
        resolved = _fuzzy_match_project(title)
        if resolved != project_key:
            failures.append((title, project_key, resolved))

    assert not failures, failures


class _Tracker:
    def __init__(self, text, entities=None, slot=None):
        self.latest_message = {
            "text": text,
            "metadata": {"lang": "EN"},
            "entities": [{"entity": "project", "value": value} for value in entities or []],
        }
        self.events = []
        self._slot = slot

    def get_latest_entity_values(self, entity_type):
        if entity_type != "project":
            return iter(())
        return (
            entity["value"]
            for entity in self.latest_message["entities"]
            if entity["entity"] == "project"
        )

    def get_slot(self, name):
        if name == "project_name":
            return self._slot
        return None


class _Dispatcher:
    def __init__(self):
        self.messages = []

    def utter_message(self, **kwargs):
        self.messages.append(kwargs)


def test_full_title_beats_broad_extracted_entity():
    tracker = _Tracker(
        "Tell me about Nikola Tesla International Airport – Wayfinding Signage Design",
        entities=["Nikola Tesla International Airport"],
    )

    project_key, _ = _resolve_project(tracker)

    assert project_key == "belgrade_wayfinding"


def test_geo_query_detects_country_and_region_without_hijacking_project_names():
    mexico = _project_geo_result("What projects do you have in Mexico?")

    assert mexico
    assert mexico["label"] == "Mexico"
    assert mexico["matched_label"] == "Latin America"
    assert not mexico["direct"]
    assert "tocumen_airport" in mexico["project_keys"]
    assert "cusco_airport" in mexico["project_keys"]

    south_america = _project_geo_result("What did you do in South America?")
    assert south_america
    assert south_america["direct"]
    assert "santiago_wayfinding" in south_america["project_keys"]

    assert not _looks_like_project_geo_query("Tell me about the French Embassy in Bangkok")


def test_action_list_projects_filters_country_instead_of_full_portfolio():
    tracker = _Tracker("What other projects does 1PAX have in Serbia?")
    dispatcher = _Dispatcher()

    ActionListProjects().run(dispatcher, tracker, {})

    assert dispatcher.messages
    text = dispatcher.messages[0]["text"]
    assert "Serbia" in text
    assert "Belgrade Airport" in text
    assert "AIK Bank" in text
    assert "Sofia Airport" not in text
    assert "all 58" not in text


def test_action_list_projects_mexico_uses_regional_fallback_not_all_projects():
    tracker = _Tracker("What projects do you have in Mexico?")
    dispatcher = _Dispatcher()

    ActionListProjects().run(dispatcher, tracker, {})

    assert dispatcher.messages
    text = dispatcher.messages[0]["text"]
    assert "Mexico" in text
    assert "Latin America" in text
    assert "Panama" in text
    assert "Peru" in text
    assert "Sofia Airport" not in text
    assert "all 58" not in text


def test_geo_query_detects_unsupported_country_without_full_portfolio():
    australia = _project_geo_result("What projects did you do in Australia?")

    assert australia
    assert australia["label"] == "Australia"
    assert not australia["direct"]
    assert australia["project_keys"] == []


def test_action_list_projects_unsupported_country_gives_negative_answer():
    tracker = _Tracker("What projects did you do in Australia?")
    dispatcher = _Dispatcher()

    ActionListProjects().run(dispatcher, tracker, {})

    assert dispatcher.messages
    text = dispatcher.messages[0]["text"]
    assert "Australia" in text
    assert "does not list a project in this area yet" in text
    assert "future collaborations" in text
    assert "Sofia Airport" not in text
    assert "all 58" not in text


def test_out_of_scope_project_safety_net_keeps_media_and_link():
    tracker = _Tracker("Tell me about Félix Eboué Cayenne Airport – Interior Design")
    dispatcher = _Dispatcher()

    events = ActionHandleOutOfScope().run(dispatcher, tracker, {})

    assert dispatcher.messages
    message = dispatcher.messages[0]
    project = PROJECTS["cayenne_interior_design"]
    assert message["image"] == project["cover_image_url"]
    assert project["project_url"] in message["text"]
    assert any(
        event.get("event") == "slot"
        and event.get("name") == "project_name"
        and event.get("value") == "cayenne_interior_design"
        for event in events
    )


if __name__ == "__main__":
    test_every_display_name_maps_to_itself()
    test_title_words_do_not_hijack_general_project_questions()
    test_explicit_detail_question_still_wins_after_title_stripping()
    test_named_project_token_beats_generic_airport_project_alias()
    test_partial_title_residue_still_routes_to_overview()
    test_current_website_titles_resolve_to_expected_projects()
    test_full_title_beats_broad_extracted_entity()
    test_geo_query_detects_country_and_region_without_hijacking_project_names()
    test_action_list_projects_filters_country_instead_of_full_portfolio()
    test_action_list_projects_mexico_uses_regional_fallback_not_all_projects()
    test_geo_query_detects_unsupported_country_without_full_portfolio()
    test_action_list_projects_unsupported_country_gives_negative_answer()
    test_out_of_scope_project_safety_net_keeps_media_and_link()
    print("Project resolution unit checks passed.")
