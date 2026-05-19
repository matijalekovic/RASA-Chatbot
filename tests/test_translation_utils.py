#!/usr/bin/env python3
"""Focused tests for action-server translation safeguards."""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from actions import translation
from components import translation_component
import translation_server


class FakeTracker:
    def __init__(self, text, entities=None, metadata=None, slot=None):
        self.latest_message = {
            "text": text,
            "entities": entities or [],
            "metadata": metadata or {},
        }
        self._slot = slot

    def get_slot(self, name):
        if name == "language":
            return self._slot
        return None


class TranslationResponseTests(unittest.TestCase):
    def test_english_returns_original_without_backend_call(self):
        with patch.object(translation, "_gemini_call") as gemini:
            self.assertEqual(
                translation.translate_response("Hello from 1PAX.", None),
                "Hello from 1PAX.",
            )
            self.assertEqual(
                translation.translate_response("Hello from 1PAX.", "EN"),
                "Hello from 1PAX.",
            )
            gemini.assert_not_called()

    def test_non_english_failure_does_not_leak_english(self):
        with (
            patch.object(translation, "_proxy_translate_response", return_value=None),
            patch.object(translation, "_gemini_call", return_value=None),
            patch.object(translation.logger, "error"),
        ):
            result = translation.translate_response(
                "Great choice - Belgrade Airport is one of our projects.",
                "SR",
            )

        self.assertIn("prevod", result.lower())
        self.assertNotIn("Great choice", result)
        self.assertNotIn("Belgrade Airport is one of our projects", result)

    def test_unchanged_english_translation_is_treated_as_failure(self):
        source = "What interests you most - the team, the cost, or the approach?"
        with (
            patch.object(translation, "_proxy_translate_response", return_value=None),
            patch.object(translation, "_gemini_call", return_value=source),
            patch.object(translation.logger, "error"),
        ):
            result = translation.translate_response(source, "SR")

        self.assertIn("prevod", result.lower())
        self.assertNotEqual(result, source)

    def test_successful_translation_is_returned(self):
        with (
            patch.object(translation, "_proxy_translate_response", return_value=None),
            patch.object(translation, "_gemini_call", return_value="Odlican izbor."),
        ):
            self.assertEqual(
                translation.translate_response("Great choice.", "SR"),
                "Odlican izbor.",
            )

    def test_response_translation_uses_local_proxy_before_direct_gemini(self):
        with (
            patch.object(translation, "_proxy_translate_response", return_value="Odlican izbor.") as proxy,
            patch.object(translation, "_gemini_call") as gemini,
        ):
            self.assertEqual(
                translation.translate_response("Great choice.", "SR"),
                "Odlican izbor.",
            )

        proxy.assert_called_once_with("Great choice.", "SR")
        gemini.assert_not_called()

    def test_serbian_booking_prompt_uses_static_translation(self):
        with patch.object(translation, "_gemini_call") as gemini:
            result = translation.translate_response(
                "Of course. I can help schedule a meeting with 1PAX. What name "
                "should I put on the invite?",
                "SR",
            )

        self.assertIn("Koje ime", result)
        gemini.assert_not_called()

    def test_serbian_booking_email_and_purpose_prompts_use_static_translation(self):
        with patch.object(translation, "_gemini_call") as gemini:
            email_prompt = translation.translate_response(
                "Thanks, Matija Lekovic. What email address should Calendly send the invitation to?",
                "SR",
            )
            purpose_prompt = translation.translate_response(
                "What is the purpose of the meeting? A short note is enough, for "
                "example: project consultation, partnership, proposal, careers, "
                "press, or a general introduction.",
                "SR",
            )

        self.assertIn("Na koju email adresu", email_prompt)
        self.assertIn("Koja je svrha sastanka", purpose_prompt)
        gemini.assert_not_called()

    def test_serbian_slot_list_uses_static_translation(self):
        source = "\n".join(
            [
                "I found these available times (Europe/Belgrade):",
                "1. **Fri, May 29 at 8:30 AM**",
                "",
                "Reply with a number, or tell me a different day/time.",
            ]
        )
        with patch.object(translation, "_gemini_call") as gemini:
            result = translation.translate_response(source, "SR")

        self.assertIn("Pronašao sam sledeće slobodne termine", result)
        self.assertIn("1. **Pet, 29. maj u 08:30**", result)
        self.assertIn("Odgovorite brojem", result)
        gemini.assert_not_called()

    def test_serbian_confirmation_with_purpose_uses_static_translation(self):
        source = (
            "Perfect. Should I book **Fri, May 29 at 8:30 AM** for **Matija Lekovic** "
            "at **matija@example.com**?\n\nPurpose: **testing**\n\nReply yes to confirm, or no to cancel."
        )
        with patch.object(translation, "_gemini_call") as gemini:
            result = translation.translate_response(source, "SR")

        self.assertIn("Da li da zakažem **Pet, 29. maj u 08:30**", result)
        self.assertIn("Svrha: **testing**", result)
        self.assertIn("Odgovorite da", result)
        gemini.assert_not_called()

    def test_serbian_booking_success_uses_static_translation(self):
        source = "\n\n".join(
            [
                "You're booked: **Fri, May 22 at 11:00 AM**.",
                "Calendly will send the invitation to **ana@example.com**.",
                "Purpose: **testing**.",
                "[Reschedule](https://calendly.example/reschedule)",
                "[Cancel](https://calendly.example/cancel)",
            ]
        )
        with patch.object(translation, "_gemini_call") as gemini:
            result = translation.translate_response(source, "SR")

        self.assertIn("Zakazano je: **Pet, 22. maj u 11:00**", result)
        self.assertIn("Calendly će poslati pozivnicu", result)
        self.assertIn("Svrha: **testing**", result)
        self.assertIn("[Promeni termin]", result)
        self.assertIn("[Otkaži]", result)
        gemini.assert_not_called()

    def test_serbian_booking_fallback_link_uses_static_translation(self):
        source = "\n\n".join(
            [
                "Calendly needs the final confirmation on its booking page for this meeting. "
                "I prepared a pre-filled link with your details:",
                "[Finish booking in Calendly](https://calendly.example/book)",
                "Choose **Fri, May 29 at 8:30 AM** if it is still available.",
                "Name: **Matija Lekovic**",
                "Email: **matija@example.com**",
                "Purpose: **testing**",
            ]
        )
        with patch.object(translation, "_gemini_call") as gemini:
            result = translation.translate_response(source, "SR")

        self.assertIn("konačnu potvrdu", result)
        self.assertIn("[Završite zakazivanje u Calendlyju]", result)
        self.assertIn("Izaberite **Pet, 29. maj u 08:30**", result)
        self.assertIn("Ime: **Matija Lekovic**", result)
        self.assertIn("Svrha: **testing**", result)
        gemini.assert_not_called()

    def test_gemini_timeout_fails_closed(self):
        with patch("actions.translation.urllib.request.urlopen", side_effect=TimeoutError("slow")):
            self.assertIsNone(
                translation._gemini_call(
                    "Translate this",
                    "Return only translated text.",
                )
            )

    def test_serbian_schedule_phrase_has_local_fast_path(self):
        self.assertEqual(
            translation_server._quick_schedule_translation(
                "mogu li da zakazem sastanak",
                "SR",
            ),
            "I want to schedule a meeting",
        )
        self.assertEqual(
            translation_server._quick_schedule_translation(
                "koji termini su slobodni sutra",
                "SR",
            ),
            "which times are free tomorrow",
        )
        self.assertEqual(
            translation_server._quick_schedule_translation(
                "zelim da predlozim novi projekat",
                "SR",
            ),
            "I want to schedule a meeting to discuss a new project",
        )
        self.assertEqual(
            translation_server._quick_schedule_translation("sutra pre podne", "SR"),
            "tomorrow morning",
        )
        self.assertEqual(
            translation_server._quick_schedule_translation("da", "SR"),
            "yes",
        )
        self.assertEqual(
            translation_server._quick_schedule_translation("ne", "SR"),
            "no",
        )
        self.assertEqual(
            translation_server._quick_schedule_translation(
                "sledeceg petka pre podne",
                "SR",
            ),
            "next Friday morning",
        )
        self.assertEqual(
            translation_component._quick_schedule_translation(
                "sutra pre podne",
                "SR",
            ),
            "tomorrow morning",
        )
        self.assertEqual(
            translation_component._quick_schedule_translation("da", "SR"),
            "yes",
        )
        self.assertEqual(
            translation_server._quick_schedule_translation(
                "Koliki je budzet za aerodrom Sofija?",
                "SR",
            ),
            "What is the budget for Sofia Airport?",
        )
        self.assertEqual(
            translation_component._quick_schedule_translation(
                "Koliki je budzet za aerodrom Sofija?",
                "SR",
            ),
            "What is the budget for Sofia Airport?",
        )

    def test_response_proxy_splits_long_markdown_for_translation(self):
        calls = []

        def fake_translate(prompt, system_instruction, timeout=8.0, attempts=1):
            calls.append(prompt)
            return prompt.replace("Translate to Serbian using the Latin alphabet: ", "SR:")

        long_text = "\n".join([f"- **Item {index}** — details about project delivery, scope, and context" for index in range(90)])
        with patch.object(translation_server, "_gemini_translate", side_effect=fake_translate):
            result = translation_server._translate_from_english(long_text, "SR")

        self.assertGreater(len(calls), 1)
        self.assertIn("SR:- **Item 0**", result)
        self.assertIn("- **Item 39**", result)

    def test_short_english_prompt_is_not_treated_as_portuguese(self):
        tracker = FakeTracker(
            "What does 1PAX do?",
            entities=[{"entity": "__lang__", "value": "PT-PT"}],
        )

        self.assertIsNone(translation.get_lang(tracker))
        self.assertTrue(translation_component._looks_like_english("What does 1PAX do?"))


if __name__ == "__main__":
    unittest.main()
