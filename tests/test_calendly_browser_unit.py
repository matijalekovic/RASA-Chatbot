#!/usr/bin/env python3
"""Small pure-function checks for the Calendly browser fallback."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from actions.calendly_browser import build_calendly_scheduling_url


def test_prefilled_url_pins_selected_slot():
    url = build_calendly_scheduling_url(
        "https://calendly.com/communications-1pax/30min?utm_source=old",
        name="Matija Lekovic",
        email="matija.lekovic@1pax.com",
        purpose="chatbot scheduling testing",
        start_time="2026-05-29T08:30:00Z",
        timezone_name="Europe/Belgrade",
    )

    assert url.startswith(
        "https://calendly.com/communications-1pax/30min/"
        "2026-05-29T10:30:00+02:00?"
    )
    assert "name=Matija+Lekovic" in url
    assert "email=matija.lekovic%401pax.com" in url
    assert "a1=chatbot+scheduling+testing" in url
    assert "utm_source=1pax_chatbot" in url


if __name__ == "__main__":
    test_prefilled_url_pins_selected_slot()
    print("Calendly browser unit checks passed.")
