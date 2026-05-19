#!/usr/bin/env python3
"""Focused tests for resolver/listing guardrails."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from actions.actions import _filtered_project_keys, _fuzzy_match_project
from actions.projects_data import PROJECTS
from actions.site_links import project_cover_image_url, project_url
from actions.team_actions import ActionAnswerTeamQuery, _lookup_person
from rasa_sdk.executor import CollectingDispatcher


class FakeTracker:
    def __init__(self, text, intent, entities=None, slots=None, events=None):
        self.latest_message = {
            "text": text,
            "intent": {"name": intent},
            "entities": entities or [],
        }
        self._slots = slots or {}
        self.events = events or []

    def get_slot(self, name):
        return self._slots.get(name)

    def get_latest_entity_values(self, entity_type):
        return (
            entity.get("value")
            for entity in self.latest_message.get("entities", [])
            if entity.get("entity") == entity_type
        )


class ProjectResolutionGuardTests(unittest.TestCase):
    def test_unknown_airport_does_not_match_iata_alias(self):
        self.assertIsNone(_fuzzy_match_project("Dubai Airport"))

    def test_known_airport_typo_still_resolves(self):
        self.assertEqual(_fuzzy_match_project("Bordeux airport"), "bordeaux_airport")

    def test_specific_cayenne_offices_phrase_beats_generic_airport(self):
        self.assertEqual(
            _fuzzy_match_project("Tell me about Cayenne airport office buildings"),
            "cayenne_airport_offices",
        )

    def test_airport_projects_in_africa_filter(self):
        keys, description = _filtered_project_keys("What airport projects do you have in Africa?")

        self.assertIsNotNone(keys)
        self.assertIn("Africa", description)
        self.assertIn("conakry_airport", keys)
        self.assertIn("kigali_airport", keys)
        self.assertIn("cabo_verde_airports", keys)
        self.assertNotIn("sofia_airport", keys)
        self.assertNotIn("jaipur_airport", keys)

    def test_every_project_has_website_link_and_cover_image(self):
        for key, project in PROJECTS.items():
            with self.subTest(project=key):
                url = project_url(key, project.get("category"))
                image = project_cover_image_url(key, project.get("category"))

                self.assertTrue(url.startswith("https://www.1pax.com/"))
                self.assertTrue(image.startswith("https://"))


class TeamResolutionGuardTests(unittest.TestCase):
    def test_ai_role_does_not_drift_to_ali(self):
        self.assertEqual(_lookup_person("AI"), "matija_lekovic")
        self.assertEqual(_lookup_person("artificial intelligence"), "matija_lekovic")

    def test_short_unknown_tokens_are_not_fuzzy_matched(self):
        self.assertIsNone(_lookup_person("her"))
        self.assertEqual(_lookup_person("Ali"), "ali_fawaz")

    def test_project_entity_misrouted_to_team_delegates_to_project_action(self):
        tracker = FakeTracker(
            "Tell me about Cayenne airport office buildings",
            "ask_about_team_member",
            entities=[{"entity": "project", "value": "cayenne airport"}],
        )
        dispatcher = CollectingDispatcher()

        ActionAnswerTeamQuery().run(dispatcher, tracker, {})

        texts = [message.get("text", "") for message in dispatcher.messages]
        images = [message.get("image") for message in dispatcher.messages if message.get("image")]
        self.assertTrue(any("Cayenne Airport" in text and "Office Buildings" in text for text in texts))
        self.assertTrue(any("View on the 1PAX website" in text for text in texts))
        self.assertTrue(images)


if __name__ == "__main__":
    unittest.main()
