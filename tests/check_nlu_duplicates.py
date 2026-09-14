#!/usr/bin/env python3
"""Fail fast on normalized examples shared by more than one NLU intent."""

from collections import defaultdict
from pathlib import Path
import re
import sys
import unicodedata

import yaml


ROOT = Path(__file__).resolve().parents[1]
NLU_PATH = ROOT / "data" / "nlu.yml"

MARKDOWN_ENTITY = re.compile(r"\[([^\]]+)]\([^)]+\)")
JSON_ENTITY = re.compile(r"\[([^\]]+)]\{[^}]+\}")


def normalize_example(example: str) -> str:
    surface = MARKDOWN_ENTITY.sub(r"\1", example)
    surface = JSON_ENTITY.sub(r"\1", surface)
    surface = unicodedata.normalize("NFKC", surface).casefold()
    surface = re.sub(r"[^\w]+", " ", surface, flags=re.UNICODE)
    return " ".join(surface.split())


def main() -> int:
    payload = yaml.safe_load(NLU_PATH.read_text(encoding="utf-8"))
    examples_by_surface = defaultdict(list)
    within_intent_duplicates = 0

    for block in payload.get("nlu", []):
        intent = block.get("intent")
        examples = block.get("examples")
        if not intent or not isinstance(examples, str):
            continue
        seen_in_intent = set()
        for raw_line in examples.splitlines():
            raw_line = raw_line.strip()
            if not raw_line.startswith("-"):
                continue
            example = raw_line[1:].strip()
            surface = normalize_example(example)
            if not surface:
                continue
            if surface in seen_in_intent:
                within_intent_duplicates += 1
            seen_in_intent.add(surface)
            examples_by_surface[surface].append((intent, example))

    conflicts = []
    for surface, occurrences in sorted(examples_by_surface.items()):
        intents = {intent for intent, _ in occurrences}
        if len(intents) > 1:
            conflicts.append((surface, occurrences))

    forbidden_articles = [
        (line_number, line.strip())
        for line_number, line in enumerate(
            NLU_PATH.read_text(encoding="utf-8").splitlines(),
            start=1,
        )
        if re.search(r"\[the\s+[^\]]+]\(", line, re.IGNORECASE)
    ]

    if conflicts:
        print(f"Found {len(conflicts)} normalized cross-intent duplicate(s):")
        for surface, occurrences in conflicts:
            print(f"  {surface!r}")
            for intent, example in occurrences:
                print(f"    {intent}: {example}")
    if forbidden_articles:
        print("Found forbidden leading-article entity annotations:")
        for line_number, line in forbidden_articles:
            print(f"  {NLU_PATH}:{line_number}: {line}")

    if conflicts or forbidden_articles:
        return 1

    print(
        "NLU duplicate gate passed: 0 cross-intent duplicates, "
        f"0 forbidden leading-article annotations ({within_intent_duplicates} "
        "within-intent duplicate occurrence(s) reported for cleanup only)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
