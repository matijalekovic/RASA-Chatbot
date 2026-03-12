#!/usr/bin/env python3
"""
1PAX Chatbot — Automated Test Blast
=====================================
Sends 50+ test messages to a running Rasa REST API + action server,
captures intents, entities, confidence scores, and full responses.

Usage:
    # Terminal 1: rasa run actions --port 5055
    # Terminal 2: rasa run --enable-api --cors "*" --port 5005
    # Terminal 3: python test_blast.py

Output: test_results/test_results_<timestamp>.txt
"""

import json
import time
import datetime
import requests
import uuid
import sys
from typing import Optional

RASA_URL   = "http://localhost:5005"
NLU_PARSE  = f"{RASA_URL}/model/parse"
CHAT_URL   = f"{RASA_URL}/webhooks/rest/webhook"

TIMEOUT    = 12   # seconds per request
PAUSE      = 0.3  # seconds between requests


# ── Colour helpers (terminal only, stripped in file output) ──────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def strip_ansi(text: str) -> str:
    import re
    return re.sub(r"\033\[[0-9;]*m", "", text)


# ── Test case definitions ─────────────────────────────────────────────────────
#
# Each test is a dict:
#   session_id  : group tests that share conversation context
#   message     : user message text
#   expect_intent (optional): intended intent for labelling
#   expect_project (optional): project key the answer should be about
#   note        : human label for the test
#
# Sessions that share an ID will be sent in order so the slot carries context.

TESTS = [

    # ── GREETING / META ───────────────────────────────────────────────────────
    {"session_id": "s_greet",  "message": "Hello!",                      "expect_intent": "greet",          "note": "Basic greeting"},
    {"session_id": "s_greet2", "message": "hey, what's up?",             "expect_intent": "greet",          "note": "Casual greeting"},
    {"session_id": "s_bot",    "message": "Are you a robot?",            "expect_intent": "bot_challenge",  "note": "Bot challenge"},
    {"session_id": "s_bye",    "message": "Thanks, bye!",                "expect_intent": "goodbye",        "note": "Goodbye"},

    # ── PROJECT LIST / DISCOVERY ───────────────────────────────────────────────
    {"session_id": "s_list1",  "message": "Show me all your projects",   "expect_intent": "ask_projects_list",    "note": "List all projects"},
    {"session_id": "s_list2",  "message": "what does 1PAX do",           "expect_intent": "ask_company_overview", "note": "Generic 'what do you do' → company overview"},
    {"session_id": "s_cat1",   "message": "what airport projects do you have?", "expect_intent": "ask_project_category", "note": "Category filter"},

    # ── ASK ABOUT PROJECT (teaser) ────────────────────────────────────────────
    {"session_id": "s_sofia",  "message": "Tell me about Sofia Airport", "expect_intent": "ask_about_project",   "expect_project": "sofia_airport",    "note": "Sofia Airport teaser"},
    {"session_id": "s_bel",    "message": "Belgrade Airport",            "expect_intent": "ask_about_project",   "expect_project": "belgrade_airport", "note": "Belgrade Airport — bare name"},
    {"session_id": "s_vel",    "message": "tell me about Velana Airport","expect_intent": "ask_about_project",   "expect_project": "velana_airport",   "note": "Velana Airport"},

    # ── SINGLE-TURN DETAIL QUERIES (entity in message) ────────────────────────
    {"session_id": "s_d01",    "message": "Where is Sofia Airport?",                     "expect_intent": "ask_project_location",  "expect_project": "sofia_airport",     "note": "Location — Sofia"},
    {"session_id": "s_d02",    "message": "When was the Belgrade Airport project?",      "expect_intent": "ask_project_year",      "expect_project": "belgrade_airport",  "note": "Timeline — Belgrade"},
    {"session_id": "s_d03",    "message": "Who is the client for Sofia Airport?",        "expect_intent": "ask_project_client",    "expect_project": "sofia_airport",     "note": "Client — Sofia"},
    {"session_id": "s_d04",    "message": "How much did Velana Airport cost?",           "expect_intent": "ask_project_cost",      "expect_project": "velana_airport",    "note": "Cost — Velana"},
    {"session_id": "s_d05",    "message": "How big is the Bordeaux Airport project?",   "expect_intent": "ask_project_area",      "expect_project": "bordeaux_airport",  "note": "Area — Bordeaux"},
    {"session_id": "s_d06",    "message": "Capacity of Pointe-à-Pitre Terminal 1?",     "expect_intent": "ask_project_capacity",  "expect_project": "pointe_a_pitre_t1", "note": "Capacity — Guadeloupe T1"},
    {"session_id": "s_d07",    "message": "Who designed Sofia Airport?",                 "expect_intent": "ask_project_architect", "expect_project": "sofia_airport",     "note": "Architect — Sofia"},
    {"session_id": "s_d08",    "message": "Who were the partners on Belgrade Airport?",  "expect_intent": "ask_project_partners",  "expect_project": "belgrade_airport",  "note": "Partners — Belgrade"},
    {"session_id": "s_d09",    "message": "What was the design challenge at Sofia Airport?", "expect_intent": "ask_project_challenge", "expect_project": "sofia_airport",  "note": "Challenge — Sofia"},
    {"session_id": "s_d10",    "message": "How did 1PAX approach the Belgrade Airport design?", "expect_intent": "ask_project_approach", "expect_project": "belgrade_airport", "note": "Approach — Belgrade"},
    {"session_id": "s_d11",    "message": "What's the sustainability strategy for Velana?", "expect_intent": "ask_project_sustainability", "expect_project": "velana_airport", "note": "Sustainability — Velana"},
    {"session_id": "s_d12",    "message": "Is there a video of Sofia Airport?",          "expect_intent": "ask_project_video",     "expect_project": "sofia_airport",     "note": "Video — Sofia"},
    {"session_id": "s_d13",    "message": "What is the 5-star label for Sofia Airport?","expect_intent": "ask_project_5star",     "expect_project": "sofia_airport",     "note": "5-Star — Sofia"},

    # ── NEW GRANULAR INTENTS — single turn ────────────────────────────────────
    {"session_id": "s_n01",    "message": "Was Sofia Airport built?",                    "expect_intent": "ask_project_status",  "expect_project": "sofia_airport",    "note": "Status — Sofia"},
    {"session_id": "s_n02",    "message": "Is the Belgrade Airport project complete?",   "expect_intent": "ask_project_status",  "expect_project": "belgrade_airport", "note": "Status — Belgrade"},
    {"session_id": "s_n03",    "message": "Was Velana Airport inaugurated?",             "expect_intent": "ask_project_status",  "expect_project": "velana_airport",   "note": "Status — Velana (inaugurated keyword)"},
    {"session_id": "s_n04",    "message": "Was this a competition or a commission for Pointe-à-Pitre T1?", "expect_intent": "ask_project_tender", "expect_project": "pointe_a_pitre_t1", "note": "Tender — Guadeloupe T1"},
    {"session_id": "s_n05",    "message": "How did 1PAX get the Sofia Airport project?","expect_intent": "ask_project_tender",  "expect_project": "sofia_airport",    "note": "Tender — Sofia (how did you get it)"},
    {"session_id": "s_n06",    "message": "What was 1PAX's role at Belgrade Airport?",  "expect_intent": "ask_project_scope",   "expect_project": "belgrade_airport", "note": "Scope — Belgrade"},
    {"session_id": "s_n07",    "message": "What does the Sofia Airport project include?","expect_intent": "ask_project_program", "expect_project": "sofia_airport",    "note": "Programme — Sofia"},
    {"session_id": "s_n08",    "message": "Any interesting facts about Velana Airport?","expect_intent": "ask_project_facts",   "expect_project": "velana_airport",   "note": "Facts — Velana"},
    {"session_id": "s_n09",    "message": "What's the design concept for Sofia Airport?","expect_intent": "ask_project_concept","expect_project": "sofia_airport",    "note": "Concept — Sofia"},
    {"session_id": "s_n10",    "message": "Elevator pitch for Belgrade Airport",         "expect_intent": "ask_project_concept","expect_project": "belgrade_airport", "note": "Concept — Belgrade (elevator pitch)"},

    # ── MULTI-TURN (slot context) — same session_id = consecutive turns ───────
    {"session_id": "s_multi1", "message": "Tell me about Bordeaux Airport",             "expect_intent": "ask_about_project",   "expect_project": "bordeaux_airport", "note": "MULTI-TURN 1/4: Set context → Bordeaux"},
    {"session_id": "s_multi1", "message": "How much did it cost?",                      "expect_intent": "ask_project_cost",    "expect_project": "bordeaux_airport", "note": "MULTI-TURN 2/4: Cost — slot context"},
    {"session_id": "s_multi1", "message": "Was it built?",                              "expect_intent": "ask_project_status",  "expect_project": "bordeaux_airport", "note": "MULTI-TURN 3/4: Status — slot context"},
    {"session_id": "s_multi1", "message": "What's the main concept?",                   "expect_intent": "ask_project_concept", "expect_project": "bordeaux_airport", "note": "MULTI-TURN 4/4: Concept — slot context"},

    {"session_id": "s_multi2", "message": "I'm interested in the Cayenne Terminal project", "expect_intent": "ask_about_project", "expect_project": "cayenne_terminal", "note": "MULTI-TURN 1/3: Set context → Cayenne"},
    {"session_id": "s_multi2", "message": "What sustainability features does it have?",     "expect_intent": "ask_project_sustainability", "expect_project": "cayenne_terminal", "note": "MULTI-TURN 2/3: Sustainability — slot"},
    {"session_id": "s_multi2", "message": "What was built exactly?",                        "expect_intent": "ask_project_program",       "expect_project": "cayenne_terminal", "note": "MULTI-TURN 3/3: Programme — slot"},

    # ── FUZZY MATCHING / TYPOS ────────────────────────────────────────────────
    {"session_id": "s_fz1",    "message": "tell me about sofia airpot",                 "expect_project": "sofia_airport",    "note": "FUZZY: Typo in 'airport'"},
    {"session_id": "s_fz2",    "message": "what about the belegrade airport?",          "expect_project": "belgrade_airport", "note": "FUZZY: Typo in 'belgrade'"},
    {"session_id": "s_fz3",    "message": "Tahiti airport",                             "expect_project": "papeete_airport",  "note": "FUZZY: City alias (Tahiti = Papeete)"},
    {"session_id": "s_fz4",    "message": "tell me about the maldives airport",         "expect_project": "velana_airport",   "note": "FUZZY: Country reference (Maldives)"},
    {"session_id": "s_fz5",    "message": "T3",                                         "expect_project": "sofia_airport",    "note": "FUZZY: Alias T3 → Sofia"},
    {"session_id": "s_fz6",    "message": "nice airport project",                       "expect_project": "nice_airport",     "note": "FUZZY: Bare city name"},
    {"session_id": "s_fz7",    "message": "belgrade metro",                             "expect_project": "belgrade_metro_line1", "note": "FUZZY: Alias — Belgrade Metro"},

    # ── EDGE CASES / CONFLICT TESTS ───────────────────────────────────────────
    {"session_id": "s_ec1",    "message": "is this still ongoing?",                     "expect_intent": "ask_project_status",  "note": "EDGE: 'ongoing' — removed from year intent"},
    {"session_id": "s_ec2",    "message": "what was the scope of work?",                "expect_intent": "ask_project_scope",   "note": "EDGE: 'scope of work' — should NOT go to overview"},
    {"session_id": "s_ec3",    "message": "what is in the building?",                   "expect_intent": "ask_project_program", "note": "EDGE: Programme phrasing"},
    {"session_id": "s_ec4",    "message": "who built it?",                              "expect_intent": "ask_project_architect","note": "EDGE: 'who built it' → architect, not status"},
    {"session_id": "s_ec5",    "message": "when was it built?",                         "expect_intent": "ask_project_year",    "note": "EDGE: 'when was it built' → year, not status"},
    {"session_id": "s_ec6",    "message": "what's the design concept?",                 "expect_intent": "ask_project_concept", "note": "EDGE: concept — should NOT go to approach"},
    {"session_id": "s_ec7",    "message": "what was the architectural vision?",         "expect_intent": "ask_project_concept", "note": "EDGE: 'architectural vision' → concept"},
    {"session_id": "s_ec8",    "message": "project scope",                              "expect_intent": "ask_project_scope",   "note": "EDGE: bare 'project scope' → scope (removed from overview)"},
    {"session_id": "s_ec9",    "message": "describe the project",                       "expect_intent": "ask_project_overview","note": "EDGE: 'describe' → overview not about_project"},
    {"session_id": "s_ec10",   "message": "in a nutshell?",                             "expect_intent": "ask_project_concept", "note": "EDGE: 'in a nutshell' → concept"},

    # ── UNKNOWN PROJECT ───────────────────────────────────────────────────────
    {"session_id": "s_unk1",   "message": "tell me about Dubai Airport",               "note": "UNKNOWN PROJECT: should ask which project"},
    {"session_id": "s_unk2",   "message": "what about the Heathrow project?",          "note": "UNKNOWN PROJECT: Heathrow not in portfolio"},

    # ── OUT OF SCOPE ──────────────────────────────────────────────────────────
    {"session_id": "s_oos1",   "message": "What's the weather in Sofia?",              "expect_intent": "out_of_scope",  "note": "OOS: Weather question"},
    {"session_id": "s_oos2",   "message": "Can you book me a flight?",                 "expect_intent": "out_of_scope",  "note": "OOS: Flight booking"},

]


# ── Session management ────────────────────────────────────────────────────────

# Pre-assign unique sender IDs per session_id
_session_map: dict[str, str] = {}
for t in TESTS:
    sid = t["session_id"]
    if sid not in _session_map:
        _session_map[sid] = f"test_{sid}_{uuid.uuid4().hex[:6]}"


# ── Core request functions ────────────────────────────────────────────────────

def parse_nlu(message: str) -> dict:
    """Call /model/parse to get intent + entities."""
    try:
        r = requests.post(NLU_PARSE, json={"text": message}, timeout=TIMEOUT)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def send_message(sender: str, message: str) -> list[dict]:
    """Send a message to the REST webhook, return list of bot responses."""
    try:
        r = requests.post(CHAT_URL, json={"sender": sender, "message": message}, timeout=TIMEOUT)
        return r.json()
    except Exception as e:
        return [{"error": str(e)}]


# ── Confidence colour ─────────────────────────────────────────────────────────

def conf_colour(score: float) -> str:
    if score >= 0.85:
        return GREEN
    elif score >= 0.60:
        return YELLOW
    else:
        return RED


# ── Main test runner ──────────────────────────────────────────────────────────

def run_tests() -> list[dict]:
    results = []

    print(f"\n{BOLD}{CYAN}══════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}{CYAN}  1PAX Chatbot — Automated Test Blast  ({len(TESTS)} tests){RESET}")
    print(f"{BOLD}{CYAN}══════════════════════════════════════════════════{RESET}\n")

    # Group consecutive messages by session for slot continuity
    # Process tests in order — multi-turn sessions share a sender_id
    session_cursor = {}  # session_id → last sent index (just tracking order)

    for i, test in enumerate(TESTS):
        sid    = test["session_id"]
        sender = _session_map[sid]
        msg    = test["message"]
        note   = test.get("note", "")
        exp_i  = test.get("expect_intent")
        exp_p  = test.get("expect_project")

        # NLU parse
        nlu    = parse_nlu(msg)
        intent = nlu.get("intent", {})
        ents   = nlu.get("entities", [])
        int_name = intent.get("name", "—")
        int_conf = intent.get("confidence", 0.0)

        # Bot response
        responses = send_message(sender, msg)
        bot_texts  = [r.get("text", "") for r in responses if "text" in r]

        # Verdict
        intent_ok = (exp_i is None) or (int_name == exp_i)
        project_ok = True  # checked below

        # Check project in NLU entities
        entity_project = next(
            (e.get("value") for e in ents if e.get("entity") == "project"),
            None,
        )

        # Naive check: does any bot response mention the expected project?
        if exp_p:
            all_text = " ".join(bot_texts).lower()
            # Try to match display name fragments or project key words
            project_key_words = exp_p.replace("_", " ").split()
            project_ok = any(w in all_text for w in project_key_words if len(w) > 3)

        # Status indicator
        if intent_ok and project_ok:
            status_sym = f"{GREEN}✓{RESET}"
        elif intent_ok and not exp_p:
            status_sym = f"{GREEN}✓{RESET}"
        elif not intent_ok:
            status_sym = f"{RED}✗ INTENT{RESET}"
        else:
            status_sym = f"{YELLOW}~ PROJECT?{RESET}"

        # Print to console
        cconf = conf_colour(int_conf)
        print(f"  [{i+1:02d}] {status_sym}  {BOLD}{note}{RESET}")
        print(f"        MSG     : {msg}")
        print(f"        INTENT  : {cconf}{int_name}{RESET} ({cconf}{int_conf:.2f}{RESET})")
        if exp_i:
            match_str = f"{GREEN}match{RESET}" if int_name == exp_i else f"{RED}MISMATCH (expected {exp_i}){RESET}"
            print(f"        EXPECTED: {match_str}")
        if ents:
            for e in ents:
                print(f"        ENTITY  : [{e.get('entity')}] = {e.get('value')!r}  (from role: {e.get('role','—')})")
        if exp_p:
            pr_str = f"{GREEN}found{RESET}" if project_ok else f"{RED}NOT FOUND in response{RESET}"
            print(f"        PROJECT : expected={exp_p} → {pr_str}")
        for t in bot_texts:
            preview = t[:200].replace("\n", " ↵ ")
            print(f"        RESPONSE: {CYAN}{preview}{RESET}")
        print()

        # Store for file output
        result = {
            "index":       i + 1,
            "note":        note,
            "session_id":  sid,
            "message":     msg,
            "intent":      int_name,
            "confidence":  round(int_conf, 4),
            "entities":    ents,
            "expect_intent":  exp_i,
            "expect_project": exp_p,
            "intent_match":   intent_ok,
            "project_match":  project_ok,
            "bot_responses":  bot_texts,
        }
        results.append(result)
        time.sleep(PAUSE)

    return results


# ── Report writer ─────────────────────────────────────────────────────────────

def write_report(results: list[dict], path: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []

    def h(text):
        lines.append("=" * 60)
        lines.append(text)
        lines.append("=" * 60)

    def s(text):
        lines.append("-" * 60)
        lines.append(text)
        lines.append("-" * 60)

    h(f"1PAX CHATBOT — AUTOMATED TEST REPORT")
    lines.append(f"Generated : {ts}")
    lines.append(f"Total tests: {len(results)}")
    lines.append("")

    # Summary stats
    intent_matches  = sum(1 for r in results if r["intent_match"] and r["expect_intent"])
    intent_tested   = sum(1 for r in results if r["expect_intent"])
    project_matches = sum(1 for r in results if r["expect_project"] and r["project_match"])
    project_tested  = sum(1 for r in results if r["expect_project"])

    h("SUMMARY")
    lines.append(f"Intent accuracy  : {intent_matches}/{intent_tested} = {intent_matches/intent_tested*100:.0f}%  (tests with expected intent)")
    lines.append(f"Project accuracy : {project_matches}/{project_tested} = {project_matches/project_tested*100:.0f}%  (tests with expected project)")
    lines.append("")

    # Failures
    failures = [r for r in results if (r["expect_intent"] and not r["intent_match"]) or (r["expect_project"] and not r["project_match"])]
    h(f"FAILURES ({len(failures)})")
    if not failures:
        lines.append("No failures detected.")
    for r in failures:
        lines.append(f"  [{r['index']:02d}] {r['note']}")
        lines.append(f"       MSG      : {r['message']}")
        if r["expect_intent"] and not r["intent_match"]:
            lines.append(f"       INTENT   : got={r['intent']}  expected={r['expect_intent']}  conf={r['confidence']}")
        if r["expect_project"] and not r["project_match"]:
            lines.append(f"       PROJECT  : expected={r['expect_project']} not found in response")
        lines.append("")

    # Low confidence
    low_conf = [r for r in results if r["confidence"] < 0.70]
    h(f"LOW CONFIDENCE CLASSIFICATIONS (<0.70) — {len(low_conf)} cases")
    for r in low_conf:
        lines.append(f"  [{r['index']:02d}] conf={r['confidence']:.4f}  intent={r['intent']}")
        lines.append(f"       MSG: {r['message']}")
    lines.append("")

    # Per-intent summary
    from collections import Counter
    intent_counts = Counter(r["intent"] for r in results)
    h("INTENT DISTRIBUTION (classified)")
    for intent, count in sorted(intent_counts.items()):
        lines.append(f"  {intent:<35} {count}")
    lines.append("")

    # Full detail
    h("FULL DETAIL — ALL TESTS")
    for r in results:
        s(f"[{r['index']:02d}] {r['note']}")
        lines.append(f"  Session   : {r['session_id']}")
        lines.append(f"  Message   : {r['message']}")
        lines.append(f"  Intent    : {r['intent']}  (conf={r['confidence']:.4f})")
        if r["expect_intent"]:
            match = "✓ MATCH" if r["intent_match"] else f"✗ MISMATCH (expected {r['expect_intent']})"
            lines.append(f"  Expected  : {r['expect_intent']}  → {match}")
        if r["entities"]:
            for e in r["entities"]:
                lines.append(f"  Entity    : [{e.get('entity')}] = {e.get('value')!r}")
        if r["expect_project"]:
            pm = "✓ found" if r["project_match"] else "✗ NOT FOUND"
            lines.append(f"  Project   : expected={r['expect_project']} → {pm}")
        lines.append(f"  Response(s):")
        for t in r["bot_responses"]:
            for line in t.split("\n"):
                lines.append(f"    | {line}")
        lines.append("")

    output = "\n".join(lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(strip_ansi(output))

    print(f"\n{GREEN}Report saved → {path}{RESET}\n")


# ── Entry point ───────────────────────────────────────────────────────────────

def check_server():
    """Quick health check before running tests."""
    try:
        r = requests.get(f"{RASA_URL}/", timeout=5)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    print(f"\nChecking Rasa server at {RASA_URL} ...")
    if not check_server():
        print(f"{RED}ERROR: Rasa server not reachable at {RASA_URL}{RESET}")
        print("Start it with:  rasa run --enable-api --cors '*' --port 5005")
        sys.exit(1)
    print(f"{GREEN}Server OK{RESET}\n")

    results = run_tests()

    # Summary to console
    intent_tested   = sum(1 for r in results if r["expect_intent"])
    intent_matches  = sum(1 for r in results if r["intent_match"] and r["expect_intent"])
    project_tested  = sum(1 for r in results if r["expect_project"])
    project_matches = sum(1 for r in results if r["project_match"] and r["expect_project"])

    print(f"\n{BOLD}══ RESULTS ══{RESET}")
    print(f"  Intent accuracy  : {GREEN}{intent_matches}/{intent_tested}{RESET}")
    print(f"  Project accuracy : {GREEN}{project_matches}/{project_tested}{RESET}")

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"/Users/macbookpro/Documents/RASA Chatbot/test_results/test_results_{ts}.txt"
    write_report(results, report_path)
