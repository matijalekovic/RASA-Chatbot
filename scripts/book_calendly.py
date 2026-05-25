#!/usr/bin/env python3
"""CLI wrapper for the Calendly hosted-page booking fallback."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from actions.calendly_browser import main


if __name__ == "__main__":
    raise SystemExit(main())
