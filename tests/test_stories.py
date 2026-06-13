#!/usr/bin/env python3
"""
1PAX Chatbot — 20 User Story Test Suite
=========================================
20 stories × ~10 questions each = 201 questions.
10 casual personas (S01-S10) + 10 professional personas (S11-S20).

Usage:
    # Both servers must be running:
    # Terminal 1: rasa run actions --port 5055
    # Terminal 2: rasa run --enable-api --cors "*" --port 5005
    python test_stories.py

Output: test_results/test_stories_<timestamp>.txt
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
CHAT_URL  = f"{RASA_URL}/webhooks/rest/webhook"
TIMEOUT   = 15
PAUSE     = 0.25

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def strip_ansi(text):
    return re.sub(r"\033\[[0-9;]*m", "", text)

def chat(session_id: str, message: str):
    """Send a message to Rasa and return the full text response."""
    try:
        r = requests.post(
            CHAT_URL,
            json={"sender": session_id, "message": message},
            timeout=TIMEOUT
        )
        r.raise_for_status()
        responses = r.json()
        full_text = " ".join(m.get("text", "") for m in responses if m.get("text"))
        return full_text.strip()
    except Exception as e:
        return f"[ERROR: {e}]"

# ── OOS detection ──────────────────────────────────────────────────────────────
OOS_PHRASES = [
    "outside my lane",
    "not quite my territory",
    "not what i'm here for",
    "not set up for that",
    "can't help with that",
    "i'm not able to help with",
    "isn't something i can",
    "that's not something",
]

def is_oos(text: str) -> bool:
    lower = text.lower()
    return any(p in lower for p in OOS_PHRASES)

def check_contains(response: str, phrases: list) -> bool:
    """Return True if ANY phrase is found in response (case-insensitive)."""
    lower = response.lower()
    return any(p.lower() in lower for p in phrases)

# ── Test case definition ───────────────────────────────────────────────────────
# Each entry: (session_id, message, note, expected_phrases, forbidden_phrases)
# expected_phrases: at least one must be present (or None = just check not OOS)
# forbidden_phrases: none must be present (or None)

TESTS = []

def add(session_id, message, note, expected=None, forbidden=None, allow_oos=False):
    TESTS.append({
        "session_id": session_id,
        "message": message,
        "note": note,
        "expected": expected,
        "forbidden": forbidden,
        "allow_oos": allow_oos,
    })

# ══════════════════════════════════════════════════════════════════════════════
# S01 — Maria: Traveler who flew through Sofia Airport
# ══════════════════════════════════════════════════════════════════════════════
S01 = "s01_maria"
add(S01, "hi!", "S01-01: greeting", expected=["hello", "hi", "1pax", "welcome", "help"])
add(S01, "I flew through Sofia Airport last year — did 1PAX design it?", "S01-02: Sofia Airport project", expected=["Sofia Airport", "terminal", "1PAX", "Terminal 3"])
add(S01, "when was it built?", "S01-03: project year (slot context)", expected=["2023", "2024", "2025", "2026", "year", "design"])
add(S01, "how big is it?", "S01-04: area/capacity", expected=["m²", "mppa", "million", "passenger", "sqm", "capacity", "area"])
add(S01, "what was the main challenge?", "S01-05: key challenge", expected=["challenge", "live", "operational", "terminal", "passenger"])
add(S01, "is there a sustainability angle?", "S01-06: sustainability", expected=["sustainab", "energy", "green", "carbon", "environment"])
add(S01, "can I see a video of it?", "S01-07: video", expected=["vimeo", "video", "film", "watch", "view"])
add(S01, "who is the company behind this?", "S01-08: company overview", expected=["1PAX", "architectural", "aviation", "firm"])
add(S01, "where are they based?", "S01-09: offices", expected=["Paris", "Belgrade", "Barcelona", "office"])
add(S01, "thanks, goodbye!", "S01-10: goodbye", expected=["bye", "goodbye", "pleasure", "take care", "have a great", "best", "Thank"])

# ══════════════════════════════════════════════════════════════════════════════
# S02 — Jake: University student curious about architecture
# ══════════════════════════════════════════════════════════════════════════════
S02 = "s02_jake"
add(S02, "what does 1PAX do?", "S02-01: company overview", expected=["1PAX", "architecture", "airport", "design"])
add(S02, "who founded the company?", "S02-02: founder", expected=["Mabel", "founder", "founded", "1PAX"])
add(S02, "what's the company's design approach?", "S02-03: methodology", expected=["design", "approach", "process", "human", "methodology"])
add(S02, "what projects have they done?", "S02-04: projects list", expected=["projects", "57", "airport", "portfolio"])
add(S02, "tell me about one of the airport projects", "S02-05: ask about project", expected=["airport", "terminal", "design", "1PAX"])
add(S02, "what's their sustainability philosophy?", "S02-06: sustainability", expected=["sustainab", "environment", "carbon", "green", "energy"])
add(S02, "do they use any innovation in their work?", "S02-07: innovation", expected=["innovat", "AI", "digital", "patent", "technology", "process"])
add(S02, "how big is the team?", "S02-08: team", expected=["team", "people", "staff", "international", "member"])
add(S02, "what are their values?", "S02-09: values", expected=["value", "ethics", "human", "sustainab", "community"])
add(S02, "are there any job openings?", "S02-10: careers", expected=["career", "job", "role", "opportun", "talent", "application", "seeking", "team", "1PAX", "studio"])

# ══════════════════════════════════════════════════════════════════════════════
# S03 — Priya: Saw Velana Airport (Maldives) on LinkedIn
# ══════════════════════════════════════════════════════════════════════════════
S03 = "s03_priya"
add(S03, "I saw the Maldives airport project — tell me about it", "S03-01: Velana Airport", expected=["Velana", "Maldives", "island", "airport", "terminal"])
add(S03, "where exactly is it?", "S03-02: location", expected=["Maldives", "Male", "island", "Velana"])
add(S03, "what was the concept behind it?", "S03-03: concept", expected=["concept", "tagline", "vision", "island", "gateway", "connectivity"])
add(S03, "what approach did they take?", "S03-04: approach", expected=["approach", "design", "spatial", "passenger", "connect"])
add(S03, "how does it deal with the island environment?", "S03-05: sustainability", expected=["sustainab", "island", "climate", "environment", "tropical"])
add(S03, "who is 1PAX?", "S03-06: company overview", expected=["1PAX", "architecture", "aviation", "design", "airport"])
add(S03, "do they have similar projects in Asia?", "S03-07: Asia projects", expected=["Asia", "China", "Japan", "Singapore", "Fuzhou", "Lanzhou", "Jaipur", "Ahmedabad", "Bangkok"])
add(S03, "what services does 1PAX offer?", "S03-08: services list", expected=["service", "airport", "design", "BIM", "interior", "urban"])
add(S03, "tell me about the team", "S03-09: team overview", expected=["team", "Mabel", "Miranda", "architect", "member"])
add(S03, "is there a video of the Maldives airport?", "S03-10: video (no slot)", expected=["video", "Velana", "Maldives", "media", "check", "1pax.com", "vimeo"])

# ══════════════════════════════════════════════════════════════════════════════
# S04 — Carlos: Non-architect job seeker
# ══════════════════════════════════════════════════════════════════════════════
S04 = "s04_carlos"
add(S04, "what kind of company is 1PAX?", "S04-01: company overview", expected=["1PAX", "architecture", "aviation", "airport"])
add(S04, "what is 1PAX's culture like?", "S04-02: culture", expected=["culture", "human", "team", "collaborative", "studio", "people"])
add(S04, "do they have any open roles?", "S04-03: open roles", expected=["role", "job", "career", "opportun", "application"])
add(S04, "what does 1PAX look for in people?", "S04-04: values/careers", expected=["talent", "people", "passion", "team", "culture", "value"])
add(S04, "does 1PAX do mentoring?", "S04-05: mentorship", expected=["mentor", "learn", "grow", "junior", "develop"])
add(S04, "who leads the company?", "S04-06: leadership", expected=["Mabel", "Miranda", "CEO", "lead", "founder"])
add(S04, "what projects does 1PAX do?", "S04-07: projects list", expected=["airport", "57", "project", "portfolio", "terminal"])
add(S04, "how international is 1PAX?", "S04-08: international", expected=["international", "global", "countr", "continent", "language", "nation"])
add(S04, "what are 1PAX's ethics?", "S04-09: ethics", expected=["ethics", "sustainab", "community", "fair", "value", "governance"])
add(S04, "how do I get in touch?", "S04-10: OOS (contact details)", expected=["1pax.com", "website", "contact", "architectural work", "email", "reach", "set up", "outside"], allow_oos=True)

# ══════════════════════════════════════════════════════════════════════════════
# S05 — Sophie: Environmental activist
# ══════════════════════════════════════════════════════════════════════════════
S05 = "s05_sophie"
add(S05, "is 1PAX committed to sustainability?", "S05-01: company sustainability", expected=["sustainab", "environment", "carbon", "green", "energy"])
add(S05, "what green certifications do your buildings have?", "S05-02: certifications", expected=["sustainab", "BREEAM", "LEED", "certif", "green", "energy", "carbon", "environment"])
add(S05, "do you design for energy efficiency?", "S05-03: energy", expected=["energy", "efficient", "carbon", "green", "sustainab"])
add(S05, "tell me about a sustainable project", "S05-04: project sustainability", expected=["sustainab", "environment", "carbon", "green", "energy", "solar"])
add(S05, "what is 1PAX's social responsibility?", "S05-05: social", expected=["social", "community", "people", "impact", "responsib"])
add(S05, "tell me about Bordeaux Airport", "S05-06: Bordeaux Airport", expected=["Bordeaux", "airport", "terminal", "France"])
add(S05, "what did 1PAX do there for sustainability?", "S05-07: sustainability slot", expected=["sustainab", "environment", "carbon", "green", "Bordeaux", "certif", "energy"])
add(S05, "does 1PAX consider climate in their designs?", "S05-08: climate", expected=["climate", "environment", "carbon", "sustainab", "green"])
add(S05, "what values drive 1PAX?", "S05-09: values", expected=["value", "human", "sustainab", "ethics", "people"])
add(S05, "do they publish a sustainability report?", "S05-10: ethics/governance", expected=["sustainab", "report", "publish", "ethics", "governance", "transparenc", "plan"])

# ══════════════════════════════════════════════════════════════════════════════
# S06 — Ahmed: Aviation enthusiast
# ══════════════════════════════════════════════════════════════════════════════
S06 = "s06_ahmed"
add(S06, "what airports has 1PAX designed?", "S06-01: project category airports", expected=["airport", "Sofia", "Belgrade", "Velana", "terminal"])
add(S06, "tell me about Belgrade Airport", "S06-02: Belgrade Airport", expected=["Belgrade", "airport", "Nikola Tesla", "Serbia"])
add(S06, "how many passengers does it handle?", "S06-03: capacity (slot)", expected=["million", "mppa", "passenger", "capacity", "year"])
add(S06, "how big is it?", "S06-04: area (slot)", expected=["m²", "sqm", "area", "GFA", "million", "square"])
add(S06, "when was it completed?", "S06-05: year (slot)", expected=["2020", "2021", "2022", "2023", "2024", "2025", "year"])
add(S06, "what was the key design challenge?", "S06-06: challenge (slot)", expected=["challenge", "design", "terminal", "airport", "operational"])
add(S06, "does 1PAX design control towers too?", "S06-07: control towers service", expected=["control tower", "ATCT", "tower", "air traffic"])
add(S06, "what about the future of aviation — eVTOL, vertiports?", "S06-08: future mobility service", expected=["vertiport", "eVTOL", "AAM", "future", "mobility", "UAM"])
add(S06, "who leads the airport projects at 1PAX?", "S06-09: project director / team", expected=["Marija", "Stevanovic", "director", "project"])
add(S06, "are there airports in Africa?", "S06-10: Africa projects", expected=["Africa", "Kigali", "Conakry", "Guinea", "Rwanda", "Cabo Verde", "Nelson Mandela"])

# ══════════════════════════════════════════════════════════════════════════════
# S07 — Lisa: Journalist writing a profile of 1PAX
# ══════════════════════════════════════════════════════════════════════════════
S07 = "s07_lisa"
add(S07, "give me an overview of 1PAX", "S07-01: company overview", expected=["1PAX", "architecture", "aviation", "airport", "design"])
add(S07, "when was it founded and by whom?", "S07-02: founder/history", expected=["Mabel", "Miranda", "founded", "2012", "2013", "2014", "2015", "year"])
add(S07, "what is the company's mission?", "S07-03: mission", expected=["mission", "human", "airport", "design", "vision", "purpose"])
add(S07, "does 1PAX use AI in its work?", "S07-04: AI/innovation", expected=["AI", "artificial intelligence", "digital", "innovat", "technology", "BIM"])
add(S07, "what's most unique about the firm?", "S07-05: difference/USP", expected=["unique", "different", "speciali", "airport", "aviation", "5-star", "specialist"])
add(S07, "how many projects have you completed?", "S07-06: projects count", expected=["57", "project", "portfolio", "completed", "delivered"])
add(S07, "tell me about the biggest project", "S07-07: Sofia Airport (flagship)", expected=["Sofia", "Terminal", "airport", "1PAX"])
add(S07, "what is 1PAX's approach to urban design?", "S07-08: urbanism", expected=["urban", "masterplan", "city", "mobility", "transport", "public"])
add(S07, "how diverse is the team?", "S07-09: diversity", expected=["divers", "international", "nation", "countr", "language", "team"])
add(S07, "what are 1PAX's plans for the future?", "S07-10: future/plan", expected=["future", "plan", "grow", "expand", "vision", "strategy", "ambition"])

# ══════════════════════════════════════════════════════════════════════════════
# S08 — Tom: Curious about urban design
# ══════════════════════════════════════════════════════════════════════════════
S08 = "s08_tom"
add(S08, "does 1PAX do urban masterplanning?", "S08-01: urbanism service", expected=["urban", "masterplan", "city", "plan"])
add(S08, "tell me about the Doha West Metro Depot project", "S08-02: Doha Metro Depot", expected=["Doha", "Qatar", "metro", "masterplan"])
add(S08, "what was the approach?", "S08-03: approach (slot)", expected=["approach", "zoning", "operational", "landscape", "masterplan"])
add(S08, "do they handle traffic and phasing?", "S08-04: phasing service", expected=["phasing", "traffic", "construction", "urban", "plan", "stage"])
add(S08, "what's the future of mobility work 1PAX does?", "S08-05: future mobility", expected=["mobility", "vertiport", "eVTOL", "metro", "future"])
add(S08, "tell me about the Cergy Vertiport", "S08-06: Cergy Vertiport", expected=["Cergy", "vertiport", "eVTOL", "France"])
add(S08, "who are 1PAX's typical clients for urban work?", "S08-07: clients", expected=["client", "government", "authority", "ministry", "public"])
add(S08, "do they work with cities or municipalities?", "S08-08: clients (urban)", expected=["city", "municipality", "urban", "government", "public", "authority"])
add(S08, "what is 1PAX's human-centered design philosophy?", "S08-09: human-centered", expected=["human", "center", "passenger", "user", "experience", "people"])
add(S08, "show me all the 1PAX projects in France", "S08-10: France projects", expected=["France", "Paris", "Nice", "Bordeaux", "Cergy", "Annecy", "Lille"])

# ══════════════════════════════════════════════════════════════════════════════
# S09 — Anna: Flying through Belgrade next month
# ══════════════════════════════════════════════════════════════════════════════
S09 = "s09_anna"
add(S09, "I'm flying through Belgrade Airport — what did 1PAX do there?", "S09-01: Belgrade Airport project", expected=["Belgrade", "Nikola Tesla", "airport", "terminal"])
add(S09, "how big is the terminal?", "S09-02: area/capacity", expected=["m²", "sqm", "mppa", "million", "passenger", "terminal", "area"])
add(S09, "is it a modern design?", "S09-03: overview/approach", expected=["design", "modern", "terminal", "passenger", "Belgrade"])
add(S09, "what is the passenger experience like?", "S09-04: approach/5star", expected=["passenger", "experience", "5-star", "service", "wayfinding", "flow"])
add(S09, "how did 1PAX deal with the live airport?", "S09-05: challenge", expected=["live", "operational", "airport", "challenge", "phase", "construct"])
add(S09, "who is Mabel Miranda?", "S09-06: person lookup", expected=["Mabel", "Miranda", "CEO", "founder"])
add(S09, "who runs the company?", "S09-07: leadership", expected=["Mabel", "Miranda", "CEO", "leader", "found"])
add(S09, "what other projects does 1PAX have in Serbia?", "S09-08: Serbia projects", expected=["Serbia", "Belgrade", "Nikola Tesla", "fire station", "admin", "wayfinding", "metro"])
add(S09, "tell me about the Belgrade Metro project", "S09-09: Belgrade Metro", expected=["Belgrade", "metro", "line", "station"])
add(S09, "what does 1PAX value?", "S09-10: values", expected=["value", "human", "people", "quality", "ethics", "sustainab"])

# ══════════════════════════════════════════════════════════════════════════════
# S10 — David: Architecture enthusiast
# ══════════════════════════════════════════════════════════════════════════════
S10 = "s10_david"
add(S10, "I love architecture — what is 1PAX known for?", "S10-01: expertise/difference", expected=["airport", "aviation", "speciali", "5-star", "design", "1PAX"])
add(S10, "what does 1PAX's design process look like?", "S10-02: methodology", expected=["design", "process", "methodology", "approach", "human", "research"])
add(S10, "show me a project in Asia", "S10-03: Asia category", expected=["Asia", "China", "Fuzhou", "Lanzhou", "Jaipur", "Ahmedabad", "Singapore", "Bangkok", "Japan", "Maldives"])
add(S10, "tell me about the Fuzhou Airport project", "S10-04: Fuzhou Airport", expected=["Fuzhou", "China", "airport"])
add(S10, "what was the architectural concept?", "S10-05: concept (slot)", expected=["concept", "tagline", "vision", "Fuzhou", "China"])
add(S10, "who are the architects at 1PAX?", "S10-06: team architects", expected=["architect", "Marija", "Claudia", "Pedro", "Diego", "Hanh", "Boris", "Renzo"])
add(S10, "who handles BIM?", "S10-07: BIM person lookup", expected=["Marko", "Soskic", "BIM", "manager"])
add(S10, "tell me about Marko Soskic", "S10-08: Marko bio", expected=["Marko", "Soskic", "BIM"])
add(S10, "what is the Kigali Airport project?", "S10-09: Kigali Airport", expected=["Kigali", "Rwanda", "airport"])
add(S10, "how does 1PAX approach heritage in design?", "S10-10: heritage", expected=["heritage", "history", "context", "local", "culture", "place"])

# ══════════════════════════════════════════════════════════════════════════════
# S11 — Airport Authority Director commissioning a terminal
# ══════════════════════════════════════════════════════════════════════════════
S11 = "s11_director"
add(S11, "we are looking to commission a new terminal — what does 1PAX offer?", "S11-01: airport service", expected=["terminal", "airport", "design", "masterplan", "service"])
add(S11, "what is your experience with international airports?", "S11-02: airport projects portfolio", expected=["airport", "international", "Sofia", "Belgrade", "Velana", "project"])
add(S11, "how many airports have you designed?", "S11-03: project count/category", expected=["airport", "26", "transportation", "project", "terminal"])
add(S11, "what scope of work does 1PAX typically cover on airport projects?", "S11-04: airport service scope", expected=["concept", "design", "masterplan", "planning", "scope", "stage", "RIBA", "feasibility", "service"])
add(S11, "can you deliver projects within live operational environments?", "S11-05: live airport experience", expected=["live", "operational", "airport", "phasing", "construc"])
add(S11, "tell me about Sofia Airport Terminal 3", "S11-06: Sofia Airport flagship", expected=["Sofia", "Terminal 3", "Terminal", "airport", "1PAX"])
add(S11, "how did 1PAX handle the passenger flow design?", "S11-07: approach/challenge", expected=["passenger", "flow", "design", "terminal", "experience"])
add(S11, "what was the cost of the Sofia Airport project?", "S11-08: cost", expected=["cost", "million", "budget", "EUR", "USD", "invest"])
add(S11, "do you work with public sector clients?", "S11-09: clients", expected=["public", "government", "authority", "ministry", "airport", "client"])
add(S11, "who is the project director for airport work?", "S11-10: Marija person lookup", expected=["Marija", "Stevanovic", "project", "director"])

# ══════════════════════════════════════════════════════════════════════════════
# S12 — Government Urban Planner
# ══════════════════════════════════════════════════════════════════════════════
S12 = "s12_planner"
add(S12, "does 1PAX offer urban masterplanning services?", "S12-01: urbanism service", expected=["urban", "masterplan", "plan", "service"])
add(S12, "what is your experience with urban mobility projects?", "S12-02: future mobility / urbanism", expected=["urban", "mobility", "transport", "metro", "vertiport", "transit"])
add(S12, "can you handle airport-city integration?", "S12-03: urbanism/airport", expected=["airport", "city", "urban", "masterplan", "integrat"])
add(S12, "tell me about the Doha West Metro Depot masterplan", "S12-04: Doha Metro Depot", expected=["Doha", "Qatar", "metro", "masterplan"])
add(S12, "what is 1PAX's approach to construction phasing?", "S12-05: phasing service", expected=["phasing", "construc", "stage", "airport", "operational", "plan"])
add(S12, "what is your fee structure?", "S12-06: fee (OOS or services)", expected=["fee", "cost", "service", "contact", "discuss", "scope", "quote", "reach", "1pax.com"], allow_oos=True)
add(S12, "do you work with government ministries?", "S12-07: clients", expected=["government", "ministry", "public", "authority", "client"])
add(S12, "what is 1PAX's urbanism philosophy?", "S12-08: urbanism service detail", expected=["urban", "city", "transit", "masterplan", "mobility", "public"])
add(S12, "tell me about the Lima Metro stations", "S12-09: Lima Metro", expected=["Lima", "metro", "station", "Peru"])
add(S12, "what is 1PAX's approach to public space design?", "S12-10: human-centered/urbanism", expected=["public", "space", "human", "user", "passenger", "community"])

# ══════════════════════════════════════════════════════════════════════════════
# S13 — AAM Company Executive seeking vertiport design
# ══════════════════════════════════════════════════════════════════════════════
S13 = "s13_aam"
add(S13, "we are building an eVTOL network — can 1PAX design vertiports?", "S13-01: future mobility service", expected=["vertiport", "eVTOL", "AAM", "UAM", "future", "mobility", "service"])
add(S13, "what vertiport experience does 1PAX have?", "S13-02: vertiport projects", expected=["vertiport", "Cergy", "Singapore", "eVTOL"])
add(S13, "tell me about the Cergy Vertiport project", "S13-03: Cergy Vertiport", expected=["Cergy", "vertiport", "France", "eVTOL"])
add(S13, "what was the design concept?", "S13-04: concept (slot)", expected=["concept", "vertiport", "Cergy", "eVTOL", "design"])
add(S13, "what approach did 1PAX take?", "S13-05: approach (slot)", expected=["approach", "design", "vertiport", "Cergy", "mobility"])
add(S13, "what about Singapore?", "S13-06: Singapore Vertiport", expected=["Singapore", "vertiport", "Voloport"])
add(S13, "how does 1PAX handle regulatory compliance for AAM?", "S13-07: future mobility service", expected=["vertiport", "AAM", "eVTOL", "regulat", "standard", "service", "design"])
add(S13, "does 1PAX collaborate with technology partners?", "S13-08: innovation/clients", expected=["partner", "collaborat", "technology", "innovat", "firm", "joint"])
add(S13, "who leads the AAM/vertiport work at 1PAX?", "S13-09: leadership/team", expected=["Mabel", "team", "1PAX", "lead", "specialist"])
add(S13, "what services beyond vertiports does 1PAX offer?", "S13-10: services list", expected=["airport", "BIM", "interior", "urban", "service", "masterplan"])

# ══════════════════════════════════════════════════════════════════════════════
# S14 — Real Estate Developer seeking BIM management
# ══════════════════════════════════════════════════════════════════════════════
S14 = "s14_developer"
add(S14, "does 1PAX offer BIM management services?", "S14-01: BIM service", expected=["BIM", "model", "Revit", "digital", "service"])
add(S14, "what BIM tools do you use — Revit? ArchiCAD?", "S14-02: BIM tools", expected=["Revit", "BIM", "ArchiCAD", "model", "digital", "tool"])
add(S14, "are you ISO 19650 certified?", "S14-03: ISO 19650", expected=["ISO", "19650", "BIM", "standard", "certif", "digital"])
add(S14, "what BIM standards do you work to?", "S14-04: BIM standards", expected=["BIM", "standard", "ISO", "19650", "LOD", "CDE", "model"])
add(S14, "do you have experience with working and living typologies?", "S14-05: working living service", expected=["office", "embassy", "resort", "working", "living", "residential", "workspace"])
add(S14, "tell me about the Tokyo EU Delegation building", "S14-06: Tokyo project", expected=["Tokyo", "EU", "delegation", "European"])
add(S14, "what was 1PAX's role there?", "S14-07: scope (slot)", expected=["scope", "role", "design", "Tokyo", "EU", "delegation", "1PAX"])
add(S14, "what other embassy or government buildings have you done?", "S14-08: clients/projects", expected=["embassy", "government", "Bangkok", "Tokyo", "diplomatic", "delegation"])
add(S14, "who handles BIM at 1PAX?", "S14-09: BIM manager person", expected=["Marko", "Soskic", "BIM", "manager"])
add(S14, "what is 1PAX's track record with large-scale projects?", "S14-10: projects overview", expected=["project", "57", "airport", "large", "scale", "portfolio", "terminal"])

# ══════════════════════════════════════════════════════════════════════════════
# S15 — Embassy Official seeking diplomatic building design
# ══════════════════════════════════════════════════════════════════════════════
S15 = "s15_embassy"
add(S15, "does 1PAX design embassies or diplomatic buildings?", "S15-01: working living service", expected=["embassy", "diplomatic", "office", "government", "building", "design"])
add(S15, "tell me about the French Embassy in Bangkok", "S15-02: French Embassy Bangkok", expected=["French", "Embassy", "Bangkok", "Thailand"])
add(S15, "what was the approach?", "S15-03: approach (slot)", expected=["approach", "design", "embassy", "Bangkok", "French"])
add(S15, "what was your scope on that project?", "S15-04: scope (slot)", expected=["scope", "role", "design", "Bangkok", "embassy", "1PAX"])
add(S15, "who designed it?", "S15-05: architect (slot)", expected=["architect", "1PAX", "Bangkok", "design", "French"])
add(S15, "how does 1PAX handle security requirements in embassies?", "S15-06: working living service / approach", expected=["security", "diplomatic", "design", "approach", "requirement", "embassy"])
add(S15, "what other diplomatic projects have you done?", "S15-07: clients/projects", expected=["Tokyo", "EU", "delegation", "embassy", "diplomatic", "government"])
add(S15, "who at 1PAX would manage this kind of project?", "S15-08: project director", expected=["Marija", "director", "project", "manager", "team"])
add(S15, "what is 1PAX's experience with government clients?", "S15-09: clients", expected=["government", "public", "ministry", "authority", "client"])
add(S15, "what is 1PAX's governance approach?", "S15-10: governance/ethics", expected=["governance", "ethics", "transparenc", "compliance", "integrity"])

# ══════════════════════════════════════════════════════════════════════════════
# S16 — Innovation Executive exploring patent licensing
# ══════════════════════════════════════════════════════════════════════════════
S16 = "s16_innovation"
add(S16, "I heard 1PAX holds patents — can you tell me about that?", "S16-01: innovation service", expected=["patent", "innovat", "product", "license", "IP"])
add(S16, "does 1PAX do passenger experience consulting?", "S16-02: passenger experience / innovation", expected=["passenger", "experience", "consult", "innovat", "service", "airport"])
add(S16, "how do you approach innovation in architecture?", "S16-03: company innovation", expected=["innovat", "AI", "digital", "patent", "technology", "process", "research"])
add(S16, "what digital tools does 1PAX use?", "S16-04: BIM/AI tools", expected=["BIM", "Revit", "AI", "digital", "tool", "model", "parametric"])
add(S16, "who handles AI and digital at 1PAX?", "S16-05: Matija person lookup", expected=["Matija", "Lekovic", "AI", "digital", "specialist"])
add(S16, "tell me about Matija Lekovic", "S16-06: Matija bio", expected=["Matija", "Lekovic", "AI", "digital"])
add(S16, "who manages patents and innovation?", "S16-07: Carla / innovation", expected=["Carla", "Miranda", "patent", "innovat", "IP", "CCIO", "communications"])
add(S16, "tell me about Carla Miranda", "S16-08: Carla bio", expected=["Carla", "Miranda", "CCIO", "Barcelona", "patent"])
add(S16, "what is 1PAX's IP policy?", "S16-09: IP/ethics", expected=["IP", "patent", "intellect", "property", "innovat", "protect"])
add(S16, "what sectors does 1PAX innovate in?", "S16-10: innovation service", expected=["airport", "vertiport", "mobility", "BIM", "innovat", "patent", "digital"])

# ══════════════════════════════════════════════════════════════════════════════
# S17 — Airline Retail Manager interested in commercial zones
# ══════════════════════════════════════════════════════════════════════════════
S17 = "s17_retail"
add(S17, "does 1PAX design airport commercial zones and retail?", "S17-01: interior service", expected=["retail", "commercial", "interior", "zone", "design", "wayfinding"])
add(S17, "tell me about the Jorge Chavez Food Hall project", "S17-02: Jorge Chavez Food Hall", expected=["Jorge Chavez", "food hall", "Lima", "Peru"])
add(S17, "what was the design concept?", "S17-03: concept (slot)", expected=["concept", "food hall", "Jorge Chavez", "Lima", "design"])
add(S17, "what about the Lima Peru Plaza Food Court?", "S17-04: Lima Peru Plaza", expected=["Lima", "Peru", "food court", "commercial", "interior"])
add(S17, "do you also do wayfinding design?", "S17-05: wayfinding", expected=["wayfinding", "signage", "navigat", "interior", "passenger"])
add(S17, "tell me about the Belgrade Wayfinding project", "S17-06: Belgrade Wayfinding", expected=["Belgrade", "wayfinding", "airport", "navigat"])
add(S17, "what kind of airports have you done retail work in?", "S17-07: interior service / projects", expected=["airport", "retail", "commercial", "interior", "zone", "Nantes", "Marseille", "Montijo"])
add(S17, "what are the passenger flow principles in retail design?", "S17-08: human-centered / interior", expected=["passenger", "flow", "retail", "commercial", "interior", "design", "wayfinding"])
add(S17, "can 1PAX do both architecture and interior on one project?", "S17-09: services integrated", expected=["interior", "architect", "design", "service", "both"])
add(S17, "who handles the interior design work?", "S17-10: team / specialists", expected=["interior", "team", "design", "specialist", "architect"])

# ══════════════════════════════════════════════════════════════════════════════
# S18 — Construction PM managing a live airport expansion
# ══════════════════════════════════════════════════════════════════════════════
S18 = "s18_pm"
add(S18, "we're expanding a live airport — has 1PAX done this before?", "S18-01: live airport / airport service", expected=["live", "operational", "airport", "phasing", "construction", "stage"])
add(S18, "have you done phasing at Belgrade Airport?", "S18-02: Belgrade Airport phasing", expected=["Belgrade", "airport", "phasing", "construc", "operational", "stage", "Nikola Tesla"])
add(S18, "tell me about how 1PAX managed construction phasing at Sofia Airport", "S18-03: Sofia phasing", expected=["Sofia", "phasing", "construc", "terminal", "stage", "live"])
add(S18, "who is the construction phasing expert at 1PAX?", "S18-04: Boris person lookup", expected=["Boris", "Stojnic", "phasing", "construction"])
add(S18, "tell me about Boris Stojnic", "S18-05: Boris bio", expected=["Boris", "Stojnic", "phasing"])
add(S18, "what project management tools does 1PAX use?", "S18-06: BIM / tools service", expected=["BIM", "Revit", "model", "tool", "digital", "manage"])
add(S18, "how does 1PAX coordinate with airport operators during construction?", "S18-07: airport service / challenge", expected=["coordinat", "airport", "operator", "construct", "live", "operational", "phasing"])
add(S18, "do you have experience in the Middle East?", "S18-08: region clients", expected=["Middle East", "Qatar", "Mashhad", "Doha", "Iran", "region"])
add(S18, "tell me about the Qatar Railways HQ project", "S18-09: Qatar Railways", expected=["Qatar", "railways", "HQ", "headquarters"])
add(S18, "what is 1PAX's record of delivering on time?", "S18-10: company approach / difference", expected=["deliver", "quality", "project", "time", "commit", "1PAX"])

# ══════════════════════════════════════════════════════════════════════════════
# S19 — Investor doing due diligence
# ══════════════════════════════════════════════════════════════════════════════
S19 = "s19_investor"
add(S19, "give me a company overview of 1PAX", "S19-01: company overview", expected=["1PAX", "architecture", "aviation", "airport", "design"])
add(S19, "what is 1PAX's mission and vision?", "S19-02: mission", expected=["mission", "vision", "human", "design", "airport", "purpose"])
add(S19, "what regions are you most active in?", "S19-03: clients/geographic reach", expected=["region", "Europe", "Asia", "Africa", "Latin America", "South America", "global", "international", "countr"])
add(S19, "how many projects has 1PAX delivered?", "S19-04: projects count", expected=["57", "project", "portfolio", "delivered", "completed"])
add(S19, "who are your key clients?", "S19-05: clients", expected=["client", "airport", "government", "authority", "ministry"])
add(S19, "what is 1PAX's competitive advantage?", "S19-06: difference/USP", expected=["speciali", "airport", "5-star", "unique", "aviation", "advantage", "different"])
add(S19, "does 1PAX have a sustainability commitment?", "S19-07: sustainability", expected=["sustainab", "carbon", "green", "environment", "commit"])
add(S19, "what are 1PAX's governance and ethics practices?", "S19-08: ethics/governance", expected=["governance", "ethics", "transparenc", "compliance", "integrity"])
add(S19, "what is 1PAX's supplier policy?", "S19-09: suppliers", expected=["supplier", "vendor", "partner", "ethics", "sourcing", "responsible"])
add(S19, "what is the leadership team?", "S19-10: leadership", expected=["Mabel", "Miranda", "CEO", "leadership", "Ali", "Fawaz", "Fabiola"])

# ══════════════════════════════════════════════════════════════════════════════
# S20 — Architecture Firm exploring JV partnership
# ══════════════════════════════════════════════════════════════════════════════
S20 = "s20_jv"
add(S20, "we're an architecture firm — can 1PAX be a specialist sub-consultant?", "S20-01: clients/collaboration", expected=["partner", "sub-consultant", "collaborat", "joint", "specialist", "firm"])
add(S20, "what is your experience working with other firms?", "S20-02: clients/JV", expected=["partner", "collaborat", "firm", "joint", "team", "international"])
add(S20, "what BIM standards do you work to?", "S20-03: BIM standards", expected=["BIM", "standard", "ISO", "19650", "Revit", "LOD", "model"])
add(S20, "what regions are you most active in?", "S20-04: clients/geographic", expected=["region", "Europe", "Africa", "Asia", "South America", "global", "international", "countr"])
add(S20, "tell me about the Almaty Airport project", "S20-05: Almaty Airport", expected=["Almaty", "Kazakhstan", "airport"])
add(S20, "what was 1PAX's role there?", "S20-06: scope (slot)", expected=["scope", "role", "design", "Almaty", "Kazakhstan", "1PAX"])
add(S20, "do you work in francophone Africa?", "S20-07: Africa projects", expected=["Africa", "Guinea", "Conakry", "Cabo Verde", "francophone", "Kigali"])
add(S20, "tell me about the Conakry Airport project", "S20-08: Conakry Airport", expected=["Conakry", "Guinea", "airport"])
add(S20, "who would be the main point of contact at 1PAX for a JV?", "S20-09: Fabiola BD person", expected=["Fabiola", "Espinoza", "business development", "BD", "contact"])
add(S20, "tell me about Fabiola Espinoza", "S20-10: Fabiola bio", expected=["Fabiola", "Espinoza", "business development"])


# ── Runner ─────────────────────────────────────────────────────────────────────

def run_tests():
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = os.path.join(results_dir, f"test_stories_{timestamp}.txt")

    passed = 0
    failed = 0
    failures = []
    lines = []

    def out(s):
        print(s)
        lines.append(strip_ansi(s))

    out(f"\n{BOLD}1PAX — 20 User Story Test Suite{RESET}")
    out(f"Model: {RASA_URL}   Started: {timestamp}\n")

    sessions = {}  # session_id → uuid

    for i, test in enumerate(TESTS, 1):
        sid = test["session_id"]
        if sid not in sessions:
            sessions[sid] = str(uuid.uuid4())
        sender = sessions[sid]

        msg = test["message"]
        note = test["note"]
        expected = test.get("expected")
        forbidden = test.get("forbidden")
        allow_oos = test.get("allow_oos", False)

        response = chat(sender, msg)
        time.sleep(PAUSE)

        ok = True
        fail_reason = ""

        # Check OOS (unless explicitly allowed)
        if not allow_oos and is_oos(response):
            ok = False
            fail_reason = f"got OOS response"

        # Check expected phrases
        if ok and expected and not check_contains(response, expected):
            ok = False
            fail_reason = f"none of {expected[:3]}... found in response"

        # Check forbidden phrases
        if ok and forbidden and check_contains(response, forbidden):
            ok = False
            fail_reason = f"forbidden phrase found in response"

        status = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"

        out(f"  [{i:3d}] {status}  {BOLD}{note}{RESET}")
        if not ok:
            out(f"         MSG: {msg}")
            snippet = (response[:120] + "...") if len(response) > 120 else response
            out(f"         RESP: {CYAN}{snippet}{RESET}")
            out(f"         FAIL: {fail_reason}")
            failures.append((i, note, msg, response, fail_reason))
            failed += 1
        else:
            passed += 1

    total = passed + failed
    pct = passed / total * 100 if total else 0

    color = GREEN if pct >= 97 else (YELLOW if pct >= 90 else RED)
    out(f"\n{BOLD}{'═'*60} RESULTS {'═'*10}{RESET}")
    out(f"  Overall: {color}{passed}/{total}{RESET} ({pct:.1f}%)\n")

    if failures:
        out(f"{BOLD}{RED}Failed tests:{RESET}")
        for n, note, msg, resp, reason in failures:
            out(f"  [{n:3d}] {note}")
            out(f"         → {reason}")
            snippet = (resp[:100] + "...") if len(resp) > 100 else resp
            out(f"         → Response: {snippet}\n")

    # Save report
    with open(outfile, "w") as f:
        f.write("\n".join(lines))
    out(f"\nReport saved → {outfile}")

    return passed, total

if __name__ == "__main__":
    run_tests()
