#!/usr/bin/env python3
"""
1PAX Chatbot — Advanced Conversational Test Suite
==================================================
Tests context flow, slot persistence, context-snapping, conversational tone,
typos/aliases, response accuracy, and edge cases via multi-turn sessions.

Usage:
    # Requires both servers running:
    # Terminal 1: rasa run actions --port 5055
    # Terminal 2: rasa run --enable-api --cors "*" --port 5005
    python test_advanced.py

Output: test_results/test_advanced_<timestamp>.txt
"""

import json
import time
import datetime
import requests
import uuid
import sys
import re
import os
from typing import Optional, List

RASA_URL  = os.environ.get("RASA_URL", "http://localhost:5005")
NLU_PARSE = f"{RASA_URL}/model/parse"
CHAT_URL  = f"{RASA_URL}/webhooks/rest/webhook"
TIMEOUT   = 15
PAUSE     = 0.25

# ── Colour helpers ─────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def strip_ansi(text):
    return re.sub(r"\033\[[0-9;]*m", "", text)

# ── Test case format ───────────────────────────────────────────────────────────
#
# Each test case dict:
#   session_id    : tests sharing this ID run in one conversation (slot carries)
#   message       : user input
#   note          : human-readable label
#   category      : grouping label (for statistics)
#   expect_intent : (optional) NLU intent that should be classified
#   expect_project: (optional) project key words that must appear in response
#   must_contain  : (optional) list of strings — ALL must appear in response
#   any_contain   : (optional) list of strings — at least ONE must appear
#   must_not      : (optional) list of strings — NONE may appear in response
#   slot_cleared  : (optional) if True, response should NOT mention the prev project
#
# A test PASSES if all specified checks pass.

TESTS = [

    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY 1 — CONTEXT FLOW: SLOT PERSISTENCE
    # Tests that the bot carries project context across turns
    # ═══════════════════════════════════════════════════════════════════════════

    {"session_id": "s_ctx_01", "category": "Context Flow",
     "note": "CTX-01a: introduce sofia airport",
     "message": "tell me about sofia airport",
     "expect_intent": "ask_about_project",
     "expect_project": "sofia_airport",
     "any_contain": ["Sofia Airport"]},

    {"session_id": "s_ctx_01", "category": "Context Flow",
     "note": "CTX-01b: follow-up location — no project named",
     "message": "where is it?",
     "expect_intent": "ask_project_location",
     "expect_project": "sofia_airport",
     "any_contain": ["Sofia", "Bulgaria"]},

    {"session_id": "s_ctx_01", "category": "Context Flow",
     "note": "CTX-01c: follow-up cost — no project named",
     "message": "what was the budget?",
     "expect_intent": "ask_project_cost",
     "expect_project": "sofia_airport",
     "any_contain": ["Sofia"]},

    {"session_id": "s_ctx_01", "category": "Context Flow",
     "note": "CTX-01d: translated SR follow-up capacity — no project named",
     "message": "what is the passenger capacity",
     "expect_intent": "ask_project_capacity",
     "expect_project": "sofia_airport",
     "any_contain": ["Sofia", "passenger", "million"]},

    {"session_id": "s_ctx_01", "category": "Context Flow",
     "note": "CTX-01e: follow-up challenge — no project named",
     "message": "what was the key challenge?",
     "expect_intent": "ask_project_challenge",
     "expect_project": "sofia_airport",
     "any_contain": ["Sofia"]},

    {"session_id": "s_ctx_01", "category": "Context Flow",
     "note": "CTX-01f: follow-up scope — what did 1PAX do on it?",
     "message": "what did 1PAX do on it?",
     "expect_intent": "ask_project_scope",
     "expect_project": "sofia_airport",
     "any_contain": ["Sofia", "Role", "Scope"]},

    {"session_id": "s_ctx_01", "category": "Context Flow",
     "note": "CTX-01g: broad team question should leave project context",
     "message": "tell me about the team",
     "expect_intent": "ask_team_overview",
     "must_not": ["Sofia Airport", "Terminal 3"],
     "any_contain": ["1PAX team", "team members", "Mabel"]},

    {"session_id": "s_ctx_01", "category": "Context Flow",
     "note": "CTX-01h: company location should not be stolen by active project context",
     "message": "where is the company located?",
     "expect_intent": "ask_company_offices",
     "must_not": ["📍 Location: Sofia", "Location: Sofia"],
     "any_contain": ["Paris", "Belgrade", "Shanghai", "Barcelona", "Lima"]},

    # ── Context switch: switch projects mid-conversation ───────────────────────

    {"session_id": "s_ctx_02", "category": "Context Flow",
     "note": "CTX-02a: start with belgrade airport",
     "message": "tell me about belgrade airport",
     "expect_intent": "ask_about_project",
     "expect_project": "belgrade_airport",
     "any_contain": ["Belgrade Airport"]},

    {"session_id": "s_ctx_02", "category": "Context Flow",
     "note": "CTX-02b: switch to velana airport",
     "message": "actually, tell me about velana airport instead",
     "expect_intent": "ask_about_project",
     "expect_project": "velana_airport",
     "any_contain": ["Velana", "Maldives"]},

    {"session_id": "s_ctx_02", "category": "Context Flow",
     "note": "CTX-02c: follow-up location — should be velana not belgrade",
     "message": "and where exactly is it?",
     "expect_intent": "ask_project_location",
     "expect_project": "velana_airport",
     "any_contain": ["Maldives"],
     "must_not": ["Belgrade", "Serbia"]},

    # ── Multi-detail session: bordeaux ─────────────────────────────────────────

    {"session_id": "s_ctx_03", "category": "Context Flow",
     "note": "CTX-03a: introduce bordeaux airport",
     "message": "tell me about bordeaux airport",
     "expect_intent": "ask_about_project",
     "expect_project": "bordeaux_airport",
     "any_contain": ["Bordeaux"]},

    {"session_id": "s_ctx_03", "category": "Context Flow",
     "note": "CTX-03b: year — should use slot",
     "message": "when was it built?",
     "expect_intent": "ask_project_year",
     "expect_project": "bordeaux_airport",
     "any_contain": ["Bordeaux"]},

    {"session_id": "s_ctx_03", "category": "Context Flow",
     "note": "CTX-03c: client — should use slot",
     "message": "who commissioned it?",
     "expect_intent": "ask_project_client",
     "expect_project": "bordeaux_airport",
     "any_contain": ["Bordeaux"]},

    {"session_id": "s_ctx_03", "category": "Context Flow",
     "note": "CTX-03d: team — should use slot",
     "message": "who was on the team?",
     "expect_project": "bordeaux_airport",
     "any_contain": ["Bordeaux"]},

    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY 2 — SNAP OUT OF CONTEXT
    # Tests that certain queries correctly exit the project context
    # ═══════════════════════════════════════════════════════════════════════════

    {"session_id": "s_snap_01", "category": "Snap Out",
     "note": "SNAP-01a: establish aik bank context",
     "message": "tell me about aik bank",
     "expect_project": "aik_bank_design",
     "any_contain": ["AIK Bank"]},

    {"session_id": "s_snap_01", "category": "Snap Out",
     "note": "SNAP-01b: ask what bot can do → exits context, shows capabilities",
     "message": "what else can you do",
     "any_contain": ["Browse the portfolio", "Location", "Budget"],
     "must_not": ["AIK Bank – Branches"]},

    {"session_id": "s_snap_01", "category": "Snap Out",
     "note": "SNAP-01c: after capabilities, start fresh with new project",
     "message": "tell me about paris heliport",
     "expect_project": "paris_heliport",
     "any_contain": ["Heliport", "Paris"]},

    # ── OOS mid-conversation ───────────────────────────────────────────────────

    {"session_id": "s_snap_02", "category": "Snap Out",
     "note": "SNAP-02a: establish belgrade metro context",
     "message": "tell me about belgrade metro",
     "expect_project": "belgrade_metro_line1",
     "any_contain": ["Belgrade Metro"]},

    {"session_id": "s_snap_02", "category": "Snap Out",
     "note": "SNAP-02b: weather question mid-conversation → OOS, not project info",
     "message": "what's the weather in Belgrade?",
     "expect_intent": "out_of_scope",
     "must_not": ["Timeline:", "Budget:", "Location:"]},

    # ── List projects mid-conversation ─────────────────────────────────────────

    {"session_id": "s_snap_03", "category": "Snap Out",
     "note": "SNAP-03a: establish nice airport context",
     "message": "tell me about nice airport",
     "expect_project": "nice_airport",
     "any_contain": ["Nice"]},

    {"session_id": "s_snap_03", "category": "Snap Out",
     "note": "SNAP-03b: ask for all projects → should list portfolio",
     "message": "what other projects do you have?",
     "expect_intent": "ask_projects_list",
     "any_contain": ["Airports and Transportation", "Sofia Airport"]},

    {"session_id": "s_snap_04", "category": "Snap Out",
     "note": "SNAP-04a: establish aik bank context",
     "message": "tell me about aik bank",
     "expect_project": "aik_bank_design",
     "any_contain": ["AIK Bank"]},

    {"session_id": "s_snap_04", "category": "Snap Out",
     "note": "SNAP-04b: 'who works in your company' should leave project context",
     "message": "who works in your company?",
     "expect_intent": "ask_team_overview",
     "must_not": ["AIK Bank", "branches", "ATM"],
     "any_contain": ["Mabel", "architects", "team", "1pax.com/the-team"]},

    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY 3 — CONVERSATIONAL TONE & CASUAL PHRASING
    # Tests that casual/informal queries map to the right intent
    # ═══════════════════════════════════════════════════════════════════════════

    {"session_id": "s_tone_01", "category": "Conversational Tone",
     "note": "TONE-01a: establish velana context",
     "message": "tell me about velana airport",
     "expect_project": "velana_airport"},

    {"session_id": "s_tone_01", "category": "Conversational Tone",
     "note": "TONE-01b: 'what would you point out' → facts/highlights",
     "message": "what would you point out on this one?",
     "expect_intent": "ask_project_facts",
     "expect_project": "velana_airport",
     "any_contain": ["Velana", "Highlights"]},

    {"session_id": "s_tone_01", "category": "Conversational Tone",
     "note": "TONE-01c: 'walk me through the design' → approach",
     "message": "walk me through the design",
     "expect_intent": "ask_project_approach",
     "expect_project": "velana_airport",
     "any_contain": ["Velana"]},

    {"session_id": "s_tone_01", "category": "Conversational Tone",
     "note": "TONE-01d: 'what gave you headaches' → challenge",
     "message": "what gave you the most headaches on this?",
     "expect_intent": "ask_project_challenge",
     "expect_project": "velana_airport",
     "any_contain": ["Velana"]},

    {"session_id": "s_tone_01", "category": "Conversational Tone",
     "note": "TONE-01e: 'give me the gist' → concept",
     "message": "give me the gist",
     "expect_intent": "ask_project_concept",
     "expect_project": "velana_airport",
     "any_contain": ["Velana"]},

    {"session_id": "s_tone_02", "category": "Conversational Tone",
     "note": "TONE-02a: establish sofia context",
     "message": "sofia airport",
     "expect_project": "sofia_airport"},

    {"session_id": "s_tone_02", "category": "Conversational Tone",
     "note": "TONE-02b: 'what else can you tell me' → highlights not repeat teaser",
     "message": "what else can you tell me",
     "expect_project": "sofia_airport",
     "any_contain": ["Key Highlights", "Sofia"]},

    {"session_id": "s_tone_02", "category": "Conversational Tone",
     "note": "TONE-02c: 'any photos?' → video response, acknowledge photos",
     "message": "any photos of this project?",
     "expect_intent": "ask_project_video",
     "any_contain": ["video", "don't have individual"],
     "must_not": ["🎬 **Sofia Airport – Terminal 3"]},

    {"session_id": "s_tone_03", "category": "Conversational Tone",
     "note": "TONE-03a: establish belgrade airport context",
     "message": "tell me about belgrade airport",
     "expect_project": "belgrade_airport",
     "any_contain": ["Belgrade Airport"]},

    {"session_id": "s_tone_03", "category": "Conversational Tone",
     "note": "TONE-03b: 'how did you end up winning this?' → tender",
     "message": "how did you end up winning this project?",
     "expect_intent": "ask_project_tender",
     "expect_project": "belgrade_airport",
     "any_contain": ["Belgrade Airport"]},

    {"session_id": "s_tone_03", "category": "Conversational Tone",
     "note": "TONE-03c: 'what exactly was 1PAX's role?' → scope",
     "message": "what exactly was 1PAX's role here?",
     "expect_intent": "ask_project_scope",
     "expect_project": "belgrade_airport",
     "any_contain": ["Belgrade Airport"]},

    {"session_id": "s_tone_03", "category": "Conversational Tone",
     "note": "TONE-03d: casual sustainability ask",
     "message": "what's the sustainability story on this one?",
     "expect_intent": "ask_project_sustainability",
     "expect_project": "belgrade_airport",
     "any_contain": ["Belgrade Airport"]},

    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY 4 — TYPOS & ALIASES
    # Tests that misspellings and alternative names resolve correctly
    # ═══════════════════════════════════════════════════════════════════════════

    {"session_id": "s_typo_01", "category": "Typos & Aliases",
     "note": "TYPO-01: 'sofia ariport' (typo)",
     "message": "tell me about sofia ariport",
     "expect_project": "sofia_airport",
     "any_contain": ["Sofia Airport"]},

    {"session_id": "s_typo_02", "category": "Typos & Aliases",
     "note": "TYPO-02: 'belgarde airport' (transposed letter)",
     "message": "belgarde airport",
     "expect_project": "belgrade_airport",
     "any_contain": ["Belgrade Airport"]},

    {"session_id": "s_typo_03", "category": "Typos & Aliases",
     "note": "TYPO-03: 'aik bankk' (double letter typo)",
     "message": "tell me about aik bankk",
     "expect_project": "aik_bank_design",
     "any_contain": ["AIK Bank"]},

    {"session_id": "s_typo_04", "category": "Typos & Aliases",
     "note": "TYPO-04: 'velana?' (with punctuation)",
     "message": "velana?",
     "expect_project": "velana_airport",
     "any_contain": ["Velana"]},

    {"session_id": "s_typo_05", "category": "Typos & Aliases",
     "note": "TYPO-05: 'tahiti airport' → papeete airport",
     "message": "tell me about tahiti airport",
     "expect_project": "papeete_airport",
     "any_contain": ["Papeete", "Tahiti", "French Polynesia"]},

    {"session_id": "s_typo_06", "category": "Typos & Aliases",
     "note": "TYPO-06: 'maldives airport' → velana",
     "message": "maldives airport project",
     "expect_project": "velana_airport",
     "any_contain": ["Velana", "Maldives"]},

    {"session_id": "s_typo_07", "category": "Typos & Aliases",
     "note": "TYPO-07: 'T3' → sofia airport (synonym)",
     "message": "tell me about T3",
     "expect_project": "sofia_airport",
     "any_contain": ["Sofia Airport"]},

    {"session_id": "s_typo_08", "category": "Typos & Aliases",
     "note": "TYPO-08: 'BEG airport' → belgrade airport",
     "message": "BEG airport",
     "expect_project": "belgrade_airport",
     "any_contain": ["Belgrade Airport"]},

    {"session_id": "s_typo_09", "category": "Typos & Aliases",
     "note": "TYPO-09: 'Al Wakrah depot' → doha metro depot",
     "message": "tell me about Al Wakrah metro depot",
     "expect_project": "doha_metro_depot",
     "any_contain": ["Doha", "Metro", "Depot"]},

    {"session_id": "s_typo_10", "category": "Typos & Aliases",
     "note": "TYPO-10: 'issy heliport' → paris heliport",
     "message": "tell me about issy heliport",
     "expect_project": "paris_heliport",
     "any_contain": ["Heliport"]},

    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY 5 — RESPONSE ACCURACY
    # Tests that specific data fields return correct factual information
    # ═══════════════════════════════════════════════════════════════════════════

    {"session_id": "s_acc_01", "category": "Response Accuracy",
     "note": "ACC-01: sofia airport location → Bulgaria",
     "message": "where is sofia airport?",
     "expect_project": "sofia_airport",
     "must_contain": ["Bulgaria"]},

    {"session_id": "s_acc_02", "category": "Response Accuracy",
     "note": "ACC-02: velana airport client → MACL",
     "message": "who was the client for velana airport?",
     "expect_project": "velana_airport",
     "any_contain": ["MACL", "Maldives Airport"]},

    {"session_id": "s_acc_03", "category": "Response Accuracy",
     "note": "ACC-03: bordeaux airport location → France",
     "message": "where is bordeaux airport?",
     "expect_project": "bordeaux_airport",
     "any_contain": ["France", "Bordeaux", "Mérignac", "Merignac"]},

    {"session_id": "s_acc_04", "category": "Response Accuracy",
     "note": "ACC-04: aik bank category → interior design",
     "message": "what category is aik bank?",
     "expect_project": "aik_bank_design",
     "any_contain": ["Interior Design", "AIK Bank"]},

    {"session_id": "s_acc_05", "category": "Response Accuracy",
     "note": "ACC-05: paris heliport location → Issy-les-Moulineaux or Paris",
     "message": "where is the paris heliport?",
     "expect_project": "paris_heliport",
     "any_contain": ["Paris", "Issy", "France"]},

    {"session_id": "s_acc_06", "category": "Response Accuracy",
     "note": "ACC-06: belgrade airport overview → mentions Serbia",
     "message": "give me an overview of belgrade airport",
     "expect_project": "belgrade_airport",
     "any_contain": ["Serbia", "Belgrade"]},

    {"session_id": "s_acc_07", "category": "Response Accuracy",
     "note": "ACC-07: sofia airport status → completed/delivered",
     "message": "is sofia airport complete?",
     "expect_intent": "ask_project_status",
     "expect_project": "sofia_airport",
     "any_contain": ["Sofia"]},

    {"session_id": "s_acc_08", "category": "Response Accuracy",
     "note": "ACC-08: lima metro → mentions Lima or Peru",
     "message": "tell me about lima metro line 1",
     "expect_project": "lima_metro_line1_stations",
     "any_contain": ["Lima", "Peru"]},

    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY 6 — EDGE CASES & EMPTY CONTEXT
    # ═══════════════════════════════════════════════════════════════════════════

    {"session_id": "s_edge_01", "category": "Edge Cases",
     "note": "EDGE-01: 'where is it?' with no prior context → asks which project",
     "message": "where is it?",
     "must_not": ["Location:", "Bulgaria"],
     "any_contain": ["which project", "Which project", "which one", "what project", "name a", "Name a",
                     "city, airport", "city or airport"]},

    {"session_id": "s_edge_02", "category": "Edge Cases",
     "note": "EDGE-02: 'what's the budget?' with no prior context → asks which",
     "message": "what's the budget?",
     "must_not": ["Budget:", "million"],
     "any_contain": ["which project", "Which project", "which one", "what project", "name a", "Name a"]},

    {"session_id": "s_edge_02b", "category": "Edge Cases",
     "note": "EDGE-02b: translated SR capacity with no prior context → asks which",
     "message": "what is the passenger capacity",
     "expect_intent": "ask_project_capacity",
     "must_not": ["Passenger capacity:", "million"],
     "any_contain": ["which project", "Which project", "which one", "what project", "name a", "Name a"]},

    {"session_id": "s_edge_02c", "category": "Edge Cases",
     "note": "EDGE-02c: broad airport projects browse should not resolve to Marija",
     "message": "tell me about your airport projects",
     "expect_intent": "ask_project_category",
     "must_not": ["Marija Stevanovic", "Airport Project Director"],
     "any_contain": ["Airports", "Belgrade Airport", "Sofia Airport", "portfolio"]},

    {"session_id": "s_edge_03", "category": "Edge Cases",
     "note": "EDGE-03a: establish context then use 'and the cost?' phrasing",
     "message": "velana airport",
     "expect_project": "velana_airport"},

    {"session_id": "s_edge_03", "category": "Edge Cases",
     "note": "EDGE-03b: 'and the cost?' with leading conjunction → slot context",
     "message": "and the cost?",
     "expect_project": "velana_airport",
     "any_contain": ["Velana"]},

    {"session_id": "s_edge_04", "category": "Edge Cases",
     "note": "EDGE-04: unknown project → asks which project (not crash, not wrong project)",
     "message": "tell me about JFK airport",
     "must_not": ["JFK", "John F. Kennedy"],
     "any_contain": ["don't have", "not have", "portfolio", "can't find", "which project",
                      "Which", "which one", "Name a", "name a", "Jaipur", "list projects"]},

    {"session_id": "s_edge_05", "category": "Edge Cases",
     "note": "EDGE-05: pure project name with no verb → still resolves",
     "message": "cergy vertiport",
     "expect_project": "cergy_vertiport",
     "any_contain": ["Cergy", "Vertiport"]},

    {"session_id": "s_edge_06", "category": "Edge Cases",
     "note": "EDGE-06: very casual intro 'what's the deal with sofia airport'",
     "message": "what's the deal with sofia airport?",
     "expect_project": "sofia_airport",
     "any_contain": ["Sofia Airport"]},

    {"session_id": "s_edge_07", "category": "Edge Cases",
     "note": "EDGE-07: multi-turn with 'and' prefix follow-up",
     "message": "tell me about bordeaux airport",
     "expect_project": "bordeaux_airport"},

    {"session_id": "s_edge_07", "category": "Edge Cases",
     "note": "EDGE-07b: 'and the design concept?' → concept using slot",
     "message": "and the design concept?",
     "expect_intent": "ask_project_concept",
     "expect_project": "bordeaux_airport",
     "any_contain": ["Bordeaux"]},

    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY 7 — OUT OF SCOPE SAFETY
    # ═══════════════════════════════════════════════════════════════════════════

    {"session_id": "s_oos_01", "category": "OOS Safety",
     "note": "OOS-01: plain weather question → OOS not project info",
     "message": "what's the weather in sofia?",
     "expect_intent": "out_of_scope",
     "must_not": ["Terminal 3", "SOF Connect", "Timeline:", "Budget:"]},

    {"session_id": "s_oos_02", "category": "OOS Safety",
     "note": "OOS-02: flight booking → OOS",
     "message": "can you book me a flight?",
     "expect_intent": "out_of_scope"},

    {"session_id": "s_oos_03", "category": "OOS Safety",
     "note": "OOS-03: joke request → OOS",
     "message": "tell me a joke",
     "expect_intent": "out_of_scope"},

    {"session_id": "s_oos_04", "category": "OOS Safety",
     "note": "OOS-04: 'what can you do' → capabilities list (not OOS dead-end)",
     "message": "what can you do?",
     "any_contain": ["Browse the portfolio", "Location", "Budget"],
     "must_not": ["outside my"]},

    {"session_id": "s_oos_05", "category": "OOS Safety",
     "note": "OOS-05: establish context then non-sequitur → OOS with context offer",
     "message": "tell me about sofia airport",
     "expect_project": "sofia_airport"},

    {"session_id": "s_oos_05", "category": "OOS Safety",
     "note": "OOS-05b: non-sequitur mid-conversation → OOS response mentions sofia",
     "message": "can you order me a pizza?",
     "expect_intent": "out_of_scope",
     "any_contain": ["Sofia Airport", "outside", "lane", "scope", "territory"]},

]

# ── Session manager ────────────────────────────────────────────────────────────

sessions: dict = {}

def get_session_id(session_key: str) -> str:
    if session_key not in sessions:
        sessions[session_key] = f"adv_{uuid.uuid4().hex[:10]}"
    return sessions[session_key]


def nlu_parse(message: str) -> tuple:
    try:
        r = requests.post(NLU_PARSE, json={"text": message}, timeout=TIMEOUT)
        data = r.json()
        intent = data.get("intent", {}).get("name", "")
        conf   = data.get("intent", {}).get("confidence", 0.0)
        return intent, conf
    except Exception:
        return "", 0.0


def send_message(session_key: str, message: str) -> list:
    sid = get_session_id(session_key)
    try:
        r = requests.post(CHAT_URL,
                          json={"sender": sid, "message": message},
                          timeout=TIMEOUT)
        return r.json()
    except Exception as e:
        return [{"text": f"[ERROR: {e}]"}]


def get_all_text(responses: list) -> str:
    return " ".join(r.get("text", "") for r in responses if r.get("text"))


def check_project(all_text: str, project_key: str) -> bool:
    words = [w for w in project_key.split("_") if len(w) > 3]
    return any(w in all_text.lower() for w in words)


# ── Test runner ────────────────────────────────────────────────────────────────

def run_tests():
    print(f"\n{BOLD}{CYAN}{'═'*58}{RESET}")
    print(f"{BOLD}{CYAN}  1PAX Chatbot — Advanced Conversational Tests  ({len(TESTS)} tests){RESET}")
    print(f"{BOLD}{CYAN}{'═'*58}{RESET}\n")

    results = []
    category_stats: dict = {}

    for i, test in enumerate(TESTS, 1):
        session_key    = test["session_id"]
        message        = test["message"]
        note           = test.get("note", f"Test {i}")
        category       = test.get("category", "General")
        expect_intent  = test.get("expect_intent")
        expect_project = test.get("expect_project")
        must_contain   = test.get("must_contain", [])
        any_contain    = test.get("any_contain", [])
        must_not       = test.get("must_not", [])

        # NLU classification
        intent, conf = nlu_parse(message)

        # Send message and get response
        responses  = send_message(session_key, message)
        all_text   = get_all_text(responses)
        all_lower  = all_text.lower()

        # ── Evaluate checks ──────────────────────────────────────────────────
        failures = []

        # Intent check
        intent_ok = True
        if expect_intent:
            if intent != expect_intent:
                intent_ok = False
                failures.append(f"intent={intent} (expected {expect_intent})")

        # Project check
        project_ok = True
        if expect_project:
            if not check_project(all_text, expect_project):
                project_ok = False
                failures.append(f"project '{expect_project}' not in response")

        # must_contain (ALL must appear)
        for s in must_contain:
            if s.lower() not in all_lower:
                failures.append(f"missing required: '{s}'")

        # any_contain (at least ONE must appear)
        if any_contain:
            if not any(s.lower() in all_lower for s in any_contain):
                failures.append(f"none of {any_contain} found in response")

        # must_not (NONE may appear)
        for s in must_not:
            if s.lower() in all_lower:
                failures.append(f"forbidden string found: '{s}'")

        passed = len(failures) == 0
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        conf_color = GREEN if conf >= 0.70 else YELLOW

        # ── Print test result ────────────────────────────────────────────────
        print(f"  [{i:02d}] {status}  {BOLD}{note}{RESET}")
        print(f"        MSG     : {message}")
        if expect_intent:
            intent_disp = f"{GREEN}{intent}{RESET}" if intent_ok else f"{RED}{intent}{RESET}"
            print(f"        INTENT  : {intent_disp} ({conf_color}{conf:.2f}{RESET})")
        if expect_project:
            proj_disp = f"{GREEN}✓ found{RESET}" if project_ok else f"{RED}✗ not found{RESET}"
            print(f"        PROJECT : {proj_disp} (expected {expect_project})")
        for resp in responses:
            if resp.get("text"):
                print(f"        RESPONSE: {CYAN}{resp['text'][:120]}{RESET}")
        if failures:
            for f in failures:
                print(f"        {RED}FAIL: {f}{RESET}")
        print()

        # ── Track stats ──────────────────────────────────────────────────────
        if category not in category_stats:
            category_stats[category] = {"pass": 0, "fail": 0}
        if passed:
            category_stats[category]["pass"] += 1
        else:
            category_stats[category]["fail"] += 1

        results.append({
            "id": i,
            "note": note,
            "category": category,
            "message": message,
            "intent": intent,
            "intent_conf": conf,
            "expected_intent": expect_intent,
            "expected_project": expect_project,
            "response": all_text[:400],
            "passed": passed,
            "failures": failures,
        })

        time.sleep(PAUSE)

    # ── Summary ───────────────────────────────────────────────────────────────
    total  = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed

    print(f"{BOLD}{'═'*40} RESULTS {'═'*9}{RESET}")
    print(f"  Overall       : {GREEN if failed == 0 else RED}{passed}/{total}{RESET} passed\n")

    print(f"  {'Category':<30} {'Pass':>5} {'Fail':>5} {'Rate':>7}")
    print(f"  {'─'*30} {'─'*5} {'─'*5} {'─'*7}")
    for cat, stats in category_stats.items():
        p, f = stats["pass"], stats["fail"]
        rate = p / (p + f) * 100 if (p + f) > 0 else 0
        color = GREEN if f == 0 else (YELLOW if rate >= 70 else RED)
        print(f"  {cat:<30} {color}{p:>5}{RESET} {RED if f > 0 else GREEN}{f:>5}{RESET} {color}{rate:>6.0f}%{RESET}")

    print()
    # Failed tests summary
    failed_tests = [r for r in results if not r["passed"]]
    if failed_tests:
        print(f"  {BOLD}{RED}Failed tests:{RESET}")
        for r in failed_tests:
            print(f"    [{r['id']:02d}] {r['note']}")
            for f in r["failures"]:
                print(f"         → {f}")
        print()

    # ── Save report ───────────────────────────────────────────────────────────
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("test_results", exist_ok=True)
    report_path = f"test_results/test_advanced_{ts}.txt"

    with open(report_path, "w") as fh:
        fh.write(f"1PAX Advanced Conversational Test Suite\n")
        fh.write(f"Run at: {datetime.datetime.now().isoformat()}\n")
        fh.write(f"Overall: {passed}/{total} passed\n\n")
        for cat, stats in category_stats.items():
            p, f = stats["pass"], stats["fail"]
            fh.write(f"{cat}: {p}/{p+f}\n")
        fh.write("\nFailed tests:\n")
        for r in failed_tests:
            fh.write(f"  [{r['id']:02d}] {r['note']}\n")
            fh.write(f"       MSG: {r['message']}\n")
            fh.write(f"       INTENT: {r['intent']} (expected: {r['expected_intent']})\n")
            fh.write(f"       RESPONSE: {r['response'][:200]}\n")
            for f in r["failures"]:
                fh.write(f"       FAIL: {f}\n")
            fh.write("\n")

    print(f"{GREEN}Report saved → {report_path}{RESET}\n")
    return passed, total


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Check server availability
    print(f"Checking Rasa server at {RASA_URL} ...")
    try:
        r = requests.get(f"{RASA_URL}/status", timeout=8)
        print(f"{GREEN}Server OK{RESET}\n")
    except Exception:
        print(f"{RED}Cannot reach Rasa server. Start both servers first.{RESET}")
        sys.exit(1)

    passed, total = run_tests()
    sys.exit(0 if passed == total else 1)
