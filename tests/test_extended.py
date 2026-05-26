#!/usr/bin/env python3
"""
1PAX Chatbot — Extended Test Suite (S21–S30)
============================================
10 new stories × 10 questions = 100 additional test cases.

Covers: project deep dives (Kigali, Nice, Chateauroux, Latin America,
interior design, Doha, Greyfoot, industrial buildings, Working & Living),
team deep dives (Ali, Bashan, Claudia), ethics/ESG, urban planning.

Usage:
    python test_extended.py
"""

import json, time, datetime, requests, uuid, sys, re, os

RASA_URL = os.environ.get("RASA_URL", "http://localhost:5005")
CHAT_URL = f"{RASA_URL}/webhooks/rest/webhook"
TIMEOUT  = 15
PAUSE    = 0.25

GREEN  = "\033[92m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def strip_ansi(text):
    return re.sub(r"\033\[[0-9;]*m", "", text)

def chat(session_id: str, message: str):
    try:
        r = requests.post(CHAT_URL, json={"sender": session_id, "message": message}, timeout=TIMEOUT)
        r.raise_for_status()
        full_text = " ".join(m.get("text", "") for m in r.json() if m.get("text"))
        return full_text.strip()
    except Exception as e:
        return f"[ERROR: {e}]"

OOS_PHRASES = [
    "outside my lane", "not quite my territory", "not what i'm here for",
    "not set up for that", "can't help with that", "i'm not able to help with",
    "isn't something i can", "that's not something",
]

def is_oos(text: str) -> bool:
    return any(p in text.lower() for p in OOS_PHRASES)

def check_contains(response: str, phrases: list) -> bool:
    lower = response.lower()
    return any(p.lower() in lower for p in phrases)

TESTS = []

def add(session_id, message, note, expected=None, forbidden=None, allow_oos=False):
    TESTS.append({
        "session_id": session_id, "message": message, "note": note,
        "expected": expected, "forbidden": forbidden, "allow_oos": allow_oos,
    })


# ══════════════════════════════════════════════════════════════════════════════
# S21 — Rwanda Infrastructure Consultant (Kigali + Africa)
# ══════════════════════════════════════════════════════════════════════════════
S21 = "s21_kigali"
add(S21, "tell me about the Kigali airport project", "S21-01: Kigali Airport", expected=["Kigali", "Rwanda", "airport", "Bugesera"])
add(S21, "what was 1PAX's scope of work there?", "S21-02: scope (slot)", expected=["scope", "value engineering", "design", "review", "consult"])
add(S21, "what was the main challenge?", "S21-03: challenge (slot)", expected=["challenge", "technical", "design", "12 million", "tropical", "review"])
add(S21, "what approach did 1PAX take?", "S21-04: approach (slot)", expected=["approach", "value engineering", "roof", "solar", "envelope", "skylight"])
add(S21, "any interesting facts about this project?", "S21-05: fun facts (slot)", expected=["Kigali", "Bugesera", "thermal", "climate", "Rwanda", "value engineering"])
add(S21, "was this project a direct commission or a competition?", "S21-06: tender (slot)", expected=["direct", "commission", "Vinci", "Qatar", "award"])
add(S21, "what other African projects has 1PAX done?", "S21-07: Africa projects", expected=["Africa", "Conakry", "Cabo Verde", "Rwanda", "Guinea", "Kigali"])
add(S21, "tell me about the Conakry Airport project", "S21-08: Conakry Airport", expected=["Conakry", "Guinea", "airport"])
add(S21, "what is the status of that project?", "S21-09: status (slot)", expected=["status", "built", "complet", "delivered", "Conakry", "construct"])
add(S21, "does 1PAX have a social impact commitment?", "S21-10: social commitment", expected=["social", "impact", "inclusive", "accessible", "community", "assess"])


# ══════════════════════════════════════════════════════════════════════════════
# S22 — Airfield Operations Manager (Nice + Chateauroux)
# ══════════════════════════════════════════════════════════════════════════════
S22 = "s22_nice"
add(S22, "tell me about the Nice Airport project", "S22-01: Nice Airport", expected=["Nice", "France", "airport", "Côte d'Azur", "Terminal"])
add(S22, "how many passengers does it handle?", "S22-02: capacity (slot)", expected=["million", "passenger", "5 million", "capacity", "gate", "lounge"])
add(S22, "what was the challenge at Nice?", "S22-03: challenge (slot)", expected=["challenge", "operational", "live", "capacity", "phasing", "construction"])
add(S22, "how did 1PAX approach the design?", "S22-04: approach (slot)", expected=["approach", "design", "boarding", "lounge", "stands", "phase", "Nice"])
add(S22, "any interesting facts about Nice Airport?", "S22-05: fun facts (slot)", expected=["Nice", "Mediterranean", "five-year", "5-year", "phased", "10,000"])
add(S22, "tell me about the Chateauroux control tower project", "S22-06: Chateauroux ATCT", expected=["Châteauroux", "control tower", "ATCT", "MRO", "France"])
add(S22, "what was 1PAX's role at Chateauroux?", "S22-07: scope (slot)", expected=["scope", "control tower", "design", "ATCT", "hangar", "400", "MRO"])
add(S22, "how was the Chateauroux project awarded?", "S22-08: tender (slot)", expected=["competition", "winner", "Calvo", "consortium", "award"])
add(S22, "are there any fun facts about that tower?", "S22-09: fun facts (slot)", expected=["400 m²", "9 million", "10,000 m²", "DGAC", "Châteauroux", "hangar"])
add(S22, "does 1PAX design other control towers?", "S22-10: control towers service", expected=["control tower", "ATCT", "service", "design", "aviation"])


# ══════════════════════════════════════════════════════════════════════════════
# S23 — Latin America Airport Authority
# ══════════════════════════════════════════════════════════════════════════════
S23 = "s23_latam"
add(S23, "what projects does 1PAX have in Latin America?", "S23-01: Latin America projects", expected=["Peru", "Lima", "Panama", "Chile", "Latin America", "Bolivia"])
add(S23, "tell me about Lima Metro Line 1", "S23-02: Lima Metro", expected=["Lima", "Metro", "Peru", "station", "Line 1", "Pachacamac"])
add(S23, "what was the approach for the metro stations?", "S23-03: approach (slot)", expected=["approach", "intermodal", "mobility", "platform", "urban", "Lima"])
add(S23, "what is the programme of those stations?", "S23-04: program (slot)", expected=["platform", "bus", "taxi", "bicycle", "pedestrian", "Pachacamac", "elevated"])
add(S23, "tell me about the Cusco Airport project", "S23-05: Cusco Airport", expected=["Cusco", "Peru", "airport", "altitude"])
add(S23, "what was the challenge at Cusco?", "S23-06: challenge (slot)", expected=["challenge", "altitude", "Cusco", "UNESCO", "constraint", "urban"])
add(S23, "tell me about the Jorge Chavez Food Hall", "S23-07: Jorge Chavez Food Hall", expected=["Jorge Chavez", "food hall", "Lima", "Peru"])
add(S23, "what is the programme for the food hall?", "S23-08: program (slot)", expected=["Sazón", "kiosk", "kitchen", "seating", "food", "zone", "KO Asian"])
add(S23, "any fun facts about the Jorge Chavez food hall?", "S23-09: fun facts (slot)", expected=["Jorge Chavez", "37.5 million", "Sazón", "Peru", "culinary", "Latin"])
add(S23, "what is 1PAX's experience in South America overall?", "S23-10: South America / clients", expected=["South America", "Latin America", "Peru", "Chile", "Panama", "Bolivia"])


# ══════════════════════════════════════════════════════════════════════════════
# S24 — Airport Retail Consultant (Interior Design deep dive)
# ══════════════════════════════════════════════════════════════════════════════
S24 = "s24_interior"
add(S24, "tell me about the Montijo Airport commercial design", "S24-01: Montijo Airport", expected=["Montijo", "Portugal", "airport", "commercial", "retail"])
add(S24, "what was the design concept for Montijo?", "S24-02: concept (slot)", expected=["concept", "Lisbon", "Art Nouveau", "heritage", "portico", "Portugal"])
add(S24, "what is the programme for Montijo?", "S24-03: program (slot)", expected=["retail", "storefronts", "digital", "LED", "plaza", "façade", "projection"])
add(S24, "tell me about the Santiago Airport wayfinding project", "S24-04: Santiago Wayfinding", expected=["Santiago", "Chile", "wayfinding", "signage", "airport"])
add(S24, "what was the challenge at Santiago?", "S24-05: challenge (slot)", expected=["challenge", "200,000", "wayfinding", "multilingual", "navigation", "terminal"])
add(S24, "how did 1PAX approach the Santiago wayfinding system?", "S24-06: approach (slot)", expected=["approach", "signage", "colour", "hierarchy", "ADP", "yellow", "blue"])
add(S24, "tell me about the Cayenne Airport interior design", "S24-07: Cayenne interior", expected=["Cayenne", "French Guiana", "interior", "bioclimatic", "tropical"])
add(S24, "what is the programme for the Cayenne interior?", "S24-08: program (slot)", expected=["departure", "arrival", "boarding", "commercial", "food court", "canopy", "health"])
add(S24, "any fun facts about the Cayenne interior design?", "S24-09: fun facts (slot)", expected=["25,000", "canopy", "sunlight", "natural light", "tropical", "Cayenne"])
add(S24, "what interior design services does 1PAX offer?", "S24-10: interior service", expected=["interior", "wayfinding", "retail", "commercial", "design", "service"])


# ══════════════════════════════════════════════════════════════════════════════
# S25 — Qatar Infrastructure Developer (Doha Metro + Qatar)
# ══════════════════════════════════════════════════════════════════════════════
S25 = "s25_doha"
add(S25, "tell me about the Doha West Metro Depot project", "S25-01: Doha Metro Depot", expected=["Doha", "Qatar", "metro", "depot"])
add(S25, "how large is the depot?", "S25-02: area (slot)", expected=["157,217", "m²", "large", "vast", "metro", "Qatar"])
add(S25, "what was the design approach?", "S25-03: approach (slot)", expected=["approach", "oasis", "landscape", "shaded", "depot", "flow", "zoning"])
add(S25, "what is included in the programme?", "S25-04: program (slot)", expected=["depot", "maintenance", "stabling", "control", "power", "oasis", "parking"])
add(S25, "what are the interesting facts about the Doha depot?", "S25-05: fun facts (slot)", expected=["157,217", "oasis", "Qatar", "metro", "largest", "Doha"])
add(S25, "tell me about the Qatar Railways HQ project", "S25-06: Qatar Railways HQ", expected=["Qatar", "Railways", "HQ", "headquarters"])
add(S25, "does 1PAX have experience in the Middle East?", "S25-07: Middle East clients", expected=["Middle East", "Qatar", "Doha", "Iran", "Mashhad", "region"])
add(S25, "who are 1PAX's clients in the region?", "S25-08: clients detail", expected=["Qatar", "Doha", "client", "Railways", "airport", "Middle East"])
add(S25, "does 1PAX work on metro and rail infrastructure?", "S25-09: metro / category", expected=["metro", "transit", "station", "Belgrade", "Lima", "Doha", "rail"])
add(S25, "what future mobility services does 1PAX provide?", "S25-10: future mobility service", expected=["vertiport", "eVTOL", "metro", "service", "mobility", "future"])


# ══════════════════════════════════════════════════════════════════════════════
# S26 — Investor exploring 1PAX leadership
# ══════════════════════════════════════════════════════════════════════════════
S26 = "s26_leadership"
add(S26, "who is the CFO of 1PAX?", "S26-01: Ali Fawaz lookup", expected=["Ali", "Fawaz", "CFO"])
add(S26, "tell me about Ali Fawaz", "S26-02: Ali bio", expected=["Ali", "Fawaz", "CFO", "financial", "contract"])
add(S26, "who is 1PAX's Shanghai representative?", "S26-03: Bashan Yang lookup", expected=["Bashan", "Yang", "Shanghai"])
add(S26, "tell me about Bashan Yang", "S26-04: Bashan bio", expected=["Bashan", "Yang", "Shanghai", "visualization", "visual"])
add(S26, "who handles business development at 1PAX?", "S26-05: Fabiola lookup", expected=["Fabiola", "Espinoza", "business development", "BD"])
add(S26, "who is the CCIO at 1PAX?", "S26-06: Carla lookup", expected=["Carla", "Miranda", "CCIO", "Barcelona"])
add(S26, "who are the senior architects?", "S26-07: team architects", expected=["architect", "Claudia", "Pedro", "Hanh", "Marija", "Diego", "Boris"])
add(S26, "tell me about Claudia Cornejo", "S26-08: Claudia bio", expected=["Claudia", "Cornejo", "project manager", "BIM", "Peru"])
add(S26, "who handles operations and admin at 1PAX?", "S26-09: ops team", expected=["Andreja", "Olenka", "admin", "operations", "studio"])
add(S26, "give me an overview of 1PAX's leadership team", "S26-10: leadership overview", expected=["Mabel", "Miranda", "CEO", "Ali", "leadership", "team"])


# ══════════════════════════════════════════════════════════════════════════════
# S27 — ESG Analyst (Ethics & Sustainability deep dive)
# ══════════════════════════════════════════════════════════════════════════════
S27 = "s27_esg"
add(S27, "what is 1PAX's social commitment?", "S27-01: social commitment", expected=["social", "impact", "inclusive", "accessible", "community", "assess"])
add(S27, "does 1PAX do post-completion evaluations?", "S27-02: post-completion eval", expected=["post-completion", "evaluation", "three years", "delivery", "impact", "annual"])
add(S27, "how does 1PAX approach diversity and inclusion?", "S27-03: diversity", expected=["diversity", "inclusion", "equal", "gender", "LMIC", "fellowship"])
add(S27, "what is 1PAX's supplier policy?", "S27-04: suppliers", expected=["supplier", "ethics", "sustainable", "local", "2028", "sourcing"])
add(S27, "tell me about 1PAX's 2026-2028 ethics and sustainability plan", "S27-05: plan", expected=["2026", "2028", "plan", "BREEAM", "commit", "diversity"])
add(S27, "what are the seven commitments in the plan?", "S27-06: plan details", expected=["seven", "commit", "sustainab", "diversity", "governance", "social", "supplier"])
add(S27, "what is 1PAX's approach to cultural heritage?", "S27-07: heritage", expected=["heritage", "cultural", "identity", "impact", "assessment", "design"])
add(S27, "what are 1PAX's governance practices?", "S27-08: governance", expected=["governance", "ethics", "anti-corruption", "committee", "transparenc", "annual"])
add(S27, "what makes 1PAX an ethical company?", "S27-09: ethics overview", expected=["ethics", "sustainab", "pillar", "commit", "value", "human"])
add(S27, "what is 1PAX's Grad Fellowship?", "S27-10: diversity / fellowship", expected=["fellowship", "LMIC", "grad", "architect", "diversity", "underrepresent"])


# ══════════════════════════════════════════════════════════════════════════════
# S28 — Urban Developer (Greyfoot Paris + urbanism)
# ══════════════════════════════════════════════════════════════════════════════
S28 = "s28_greyfoot"
add(S28, "tell me about the Greyfoot Paris project", "S28-01: Greyfoot Paris", expected=["Greyfoot", "Paris", "mixed-use", "urban"])
add(S28, "what was the concept behind Greyfoot?", "S28-02: concept (slot)", expected=["concept", "Paris", "porte", "urban", "gateway", "catalyst"])
add(S28, "how was Greyfoot awarded to 1PAX?", "S28-03: tender (slot)", expected=["competition", "1st Prize", "first prize", "winner"])
add(S28, "what is the programme for Greyfoot?", "S28-04: program (slot)", expected=["offices", "co-working", "housing", "retail", "landscape", "refurbish"])
add(S28, "what was the design approach?", "S28-05: approach (slot)", expected=["approach", "urban", "porosity", "pedestrian", "refurbish", "hierarchy", "landscape"])
add(S28, "what are the fun facts about Greyfoot?", "S28-06: fun facts (slot)", expected=["Paris", "porte", "Périphérique", "Champerret", "refurbish", "competition"])
add(S28, "what urbanism services does 1PAX offer?", "S28-07: urbanism service", expected=["urbanism", "masterplan", "planning", "service", "urban", "airport"])
add(S28, "can 1PAX handle airport-city integration?", "S28-08: urbanism / airport-city", expected=["airport", "city", "urban", "connect", "transport", "masterplan", "integrat"])
add(S28, "how does 1PAX approach public space design?", "S28-09: human-centered", expected=["human", "centered", "passenger", "people", "user", "design", "public"])
add(S28, "tell me about 1PAX's regenerative urbanism philosophy", "S28-10: company urbanism", expected=["urbanism", "urban", "ecosystem", "regenerat", "city", "design", "circular"])


# ══════════════════════════════════════════════════════════════════════════════
# S29 — Airport Safety Manager (Industrial Buildings)
# ══════════════════════════════════════════════════════════════════════════════
S29 = "s29_industrial"
add(S29, "tell me about the Riga control tower competition", "S29-01: Riga Control Tower", expected=["Riga", "Latvia", "control tower", "competition"])
add(S29, "what was the design approach for Riga?", "S29-02: approach (slot)", expected=["approach", "design", "ribbon", "landscape", "tower", "Riga"])
add(S29, "any fun facts about the Riga tower?", "S29-03: fun facts (slot)", expected=["Riga", "Latvia", "Baltic", "ribbon", "7 million", "landscape"])
add(S29, "tell me about the Belgrade fire station project", "S29-04: Belgrade Fire Station", expected=["Belgrade", "fire station", "Serbia", "airport", "emergency"])
add(S29, "what was the design challenge at the Belgrade fire station?", "S29-05: challenge (slot)", expected=["challenge", "emergency", "reaction", "operational", "fire", "zones", "rapid"])
add(S29, "tell me about the Le Bourget fire station", "S29-06: Le Bourget Fire Station", expected=["Le Bourget", "fire station", "Paris", "SSLIA", "ADP"])
add(S29, "what was the design approach for Le Bourget?", "S29-07: approach (slot)", expected=["approach", "volume", "emergency", "colour", "fire", "visible", "functional"])
add(S29, "tell me about the Papeete Airport project", "S29-08: Papeete Airport", expected=["Papeete", "Tahiti", "French Polynesia", "airport"])
add(S29, "what was the challenge at Papeete?", "S29-09: challenge (slot)", expected=["challenge", "peak", "traffic", "passenger", "capacity", "Papeete", "Tahiti"])
add(S29, "what approach did 1PAX take at Papeete?", "S29-10: approach (slot)", expected=["approach", "capacity", "peak", "Polynesian", "Tahiti", "terminal", "boarding"])


# ══════════════════════════════════════════════════════════════════════════════
# S30 — Real Estate Developer (Working & Living + AIK Bank)
# ══════════════════════════════════════════════════════════════════════════════
S30 = "s30_working"
add(S30, "tell me about the AIK Bank project", "S30-01: AIK Bank", expected=["AIK", "Bank", "Serbia", "branch"])
add(S30, "what was the scope of the AIK Bank commission?", "S30-02: scope (slot)", expected=["60", "400", "ATM", "office", "Serbia", "nationwide"])
add(S30, "what was the design concept?", "S30-03: concept (slot)", expected=["concept", "brand", "identity", "AIK", "Bank", "consistent"])
add(S30, "any fun facts about the AIK Bank project?", "S30-04: fun facts (slot)", expected=["AIK", "60", "400", "Serbia", "largest", "brand", "300,000"])
add(S30, "what working and living services does 1PAX offer?", "S30-05: working living service", expected=["office", "embassy", "resort", "headquarters", "working", "living", "design"])
add(S30, "tell me about the Tokyo EU Delegation project", "S30-06: Tokyo project", expected=["Tokyo", "EU Delegation", "Japan", "embassy"])
add(S30, "what was 1PAX's role at Tokyo?", "S30-07: scope (slot)", expected=["scope", "role", "design", "Tokyo", "Japan", "EU", "embassy"])
add(S30, "tell me about the French Embassy in Bangkok", "S30-08: French Embassy Bangkok", expected=["French Embassy", "Bangkok", "Thailand", "embassy"])
add(S30, "what was the design approach there?", "S30-09: approach (slot)", expected=["approach", "design", "embassy", "Bangkok", "French", "Thailand"])
add(S30, "does 1PAX design mixed-use and residential buildings?", "S30-10: working living / mixed-use", expected=["residential", "housing", "mixed-use", "living", "design", "working", "office"])


# ── Runner ─────────────────────────────────────────────────────────────────────

def run_tests():
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = os.path.join(results_dir, f"test_extended_{timestamp}.txt")

    passed = 0
    failed = 0
    failures = []
    lines = []

    def out(s):
        print(s)
        lines.append(strip_ansi(s))

    out(f"\n{BOLD}1PAX — Extended Test Suite (S21–S30){RESET}")
    out(f"Model: {RASA_URL}   Started: {timestamp}\n")

    sessions = {}

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

        if not allow_oos and is_oos(response):
            ok = False
            fail_reason = "got OOS response"

        if ok and expected and not check_contains(response, expected):
            ok = False
            fail_reason = f"none of {expected[:4]}... found in response"

        if ok and forbidden and check_contains(response, forbidden):
            ok = False
            fail_reason = "forbidden phrase found in response"

        status = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"

        out(f"  [{i:3d}] {status}  {BOLD}{note}{RESET}")
        if not ok:
            out(f"         MSG: {msg}")
            snippet = (response[:140] + "...") if len(response) > 140 else response
            out(f"         RESP: {CYAN}{snippet}{RESET}")
            out(f"         FAIL: {fail_reason}")
            failures.append((i, note, msg, response, fail_reason))
            failed += 1
        else:
            passed += 1

    divider = "═" * 60
    out(f"\n{BOLD}{divider} RESULTS ══{RESET}")
    out(f"  Overall: {GREEN if failed == 0 else RED}{passed}/{passed+failed}{RESET} ({100*passed/(passed+failed):.1f}%)")

    if failures:
        out(f"\n{BOLD}{RED}Failed tests:{RESET}")
        for num, note, msg, resp, reason in failures:
            out(f"  [{num}] {note}")
            out(f"         → {reason}")
            snippet = (resp[:100] + "...") if len(resp) > 100 else resp
            out(f"         → Response: {snippet}")
    else:
        out(f"\n  {GREEN}{BOLD}All tests passed! 🎉{RESET}")

    with open(outfile, "w") as f:
        f.write("\n".join(lines))
    out(f"\nReport saved → {outfile}")

if __name__ == "__main__":
    run_tests()
