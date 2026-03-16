"""
Custom actions for the 1PAX company chatbot.

ActionAnswerProjectQuery  — handles all project detail intents.
ActionListProjects         — lists projects, optionally filtered by category.
ActionHandleOutOfScope     — context-aware handler for unrecognised inputs.
"""

import random
import unicodedata
from difflib import get_close_matches
from typing import Any, Dict, List, Optional, Text, Tuple

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from .projects_data import PROJECTS, CATEGORIES
from .translation import get_lang, translate_response


# ── Variation pools ──────────────────────────────────────────────────────────

_OVERVIEW_INTROS = [
    "Here's a look at **{name}**",
    "Great choice — **{name}** is one of our more interesting projects.",
    "Happy to talk about **{name}** — here's the short version:",
    "Let me tell you about **{name}**",
    "**{name}** — here's the story:",
    "Sure, **{name}** is a fascinating one.",
]

_FOLLOW_UP_PROMPTS = [
    "There's quite a bit more to this one — curious about the **budget**, the **design concept**, or what the **key challenge** was?",
    "Happy to go deeper. What interests you most — the **team**, the **cost**, the **approach**, or how it turned out?",
    "Plenty more to explore here: the **design concept**, **sustainability**, **status**, or **what was actually built**.",
    "What would you like to dig into? The **challenge**, the **concept**, the **timeline**, or maybe the **highlights**?",
]

_DETAIL_SUFFIXES = [
    "\n\nAnything else you'd like to know?",
    "\n\nHappy to go further — what else are you curious about?",
    "\n\nLet me know if you'd like to explore any other angle on this.",
    "",
    "",
]

_OUT_OF_SCOPE_WITH_CONTEXT = [
    (
        "Hmm, that one's outside my scope — I'm really only useful for questions about 1PAX's projects.\n\n"
        "We were just talking about **{name}** — want to keep going? I can tell you about the "
        "**design concept**, **what was built**, **the team**, or **how the project went**."
    ),
    (
        "I'm not sure I can help with that one — but I'd love to keep exploring **{name}** with you.\n\n"
        "What would you like to know — the **budget**, the **challenge**, the **approach**, or the **highlights**?"
    ),
    (
        "That's a little outside what I do, but we don't have to stop here.\n\n"
        "Still curious about **{name}**? Ask me anything — the design, the team, the timeline, or just what makes it stand out."
    ),
]

_OUT_OF_SCOPE_NO_CONTEXT = [
    (
        "I'm really only set up to talk about 1PAX's architectural work — but that's a pretty interesting topic! "
        "Name a project or ask 'what projects do you have?' to get started. "
        "For direct contact, visit **1pax.com**."
    ),
    (
        "That's a bit outside my lane — I'm all about 1PAX's portfolio. "
        "Try naming a project (like **Sofia Airport** or **Belgrade Metro**) and I'll tell you everything about it. "
        "To reach 1PAX directly, head to **1pax.com**."
    ),
    (
        "Not quite my territory — I focus on 1PAX's projects. "
        "Ask 'show me all projects' or just name one and we can go from there. "
        "To contact the team, visit **1pax.com**."
    ),
]


# ── Greet / Goodbye / Bot challenge ─────────────────────────────────────────


class ActionGreet(Action):
    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher, tracker, domain):
        lang = get_lang(tracker)
        dispatcher.utter_message(text=translate_response(random.choice([
            "Hi! I can tell you about 1PAX — our studio, mission, design approach, team, or careers — or help you explore our 58 architectural projects. What would you like to know?",
            "Hello! Ask about the studio, our founder, design philosophy, sustainability commitment, or explore our project portfolio. Where would you like to start?",
            "Welcome! I can answer questions about 1PAX as a studio — our mission, values, team, and approach — or dive into any of our 58 projects across airports, mobility infrastructure, and more. What's on your mind?",
            "Hello! Ask me about 1PAX — who we are, how we work, what we build, or where we're based. You can also say 'show me all projects' to browse the full portfolio.",
        ]), lang))
        return [SlotSet("language", lang)] if lang else []


class ActionGoodbye(Action):
    def name(self) -> Text:
        return "action_goodbye"

    def run(self, dispatcher, tracker, domain):
        lang = get_lang(tracker)
        dispatcher.utter_message(text=translate_response(random.choice([
            "Thank you for your interest in 1PAX. Feel free to come back anytime!",
            "It was a pleasure — hope to see you again. Goodbye!",
            "Thanks for exploring 1PAX's work. Have a great day!",
            "Goodbye! Don't hesitate to reach out if you have more questions about our projects.",
        ]), lang))
        return [SlotSet("language", lang)] if lang else []


class ActionIAmABot(Action):
    def name(self) -> Text:
        return "action_iamabot"

    def run(self, dispatcher, tracker, domain):
        lang = get_lang(tracker)
        dispatcher.utter_message(text=translate_response(random.choice([
            "I'm the 1PAX virtual assistant, here to help you explore our architectural portfolio. I'm powered by Rasa.",
            "I'm a chatbot built to answer questions about 1PAX's projects — airports, mobility infrastructure, interior design, and more.",
            "I'm the 1PAX assistant — an AI built to guide you through our portfolio of 58 architectural projects.",
        ]), lang))
        return [SlotSet("language", lang)] if lang else []


# ── Fuzzy project matching ───────────────────────────────────────────────────

# Common English words to skip when fuzzy-matching project names
_SKIP_WORDS = {
    # Function words
    'the', 'a', 'an', 'is', 'was', 'are', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'can', 'shall', 'and', 'or', 'but',
    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'about',
    'what', 'how', 'when', 'where', 'why', 'who', 'which', 'that', 'this',
    'it', 'its', 'my', 'your', 'our', 'their', 'we', 'they', 'he', 'she',
    'not', 'no', 'yes', 'ok', 'tell', 'show', 'give', 'get', 'make', 'know',
    'me', 'you', 'him', 'her', 'us', 'them', 'am', 'just', 'some',
    'any', 'all', 'more', 'also', 'so', 'if', 'then', 'than', 'too', 'very',
    # Transport/sector words — too generic to use as city identifiers
    'airport', 'metro', 'station', 'terminal', 'railway', 'railways',
    'rail', 'port', 'depot', 'hangar', 'tower', 'line', 'network',
    # Generic business / function words that can collide with city names
    'bank', 'banks', 'design', 'project', 'building', 'center', 'centre',
    'hall', 'hotel', 'office', 'offices', 'house', 'hub', 'park',
}

# City name → project key (only for unambiguous cities — one project per city)
_city_bucket: Dict[str, List[str]] = {}
for _key, _p in PROJECTS.items():
    _city = _p['location'].lower().split(',')[0].strip()
    _city_bucket.setdefault(_city, []).append(_key)

_CITY_INDEX: Dict[str, str] = {
    _city: _keys[0]
    for _city, _keys in _city_bucket.items()
    if len(_keys) == 1
}

# Full display name / slug phrase → project key
_NAME_INDEX: Dict[str, str] = {}
for _key, _p in PROJECTS.items():
    _NAME_INDEX[_p['display_name'].lower()] = _key
    _NAME_INDEX[_key.replace('_', ' ')] = _key

# Short common aliases for projects in ambiguous cities
_NAME_INDEX.update({
    # Belgrade projects
    "belgrade metro":              "belgrade_metro_line1",
    "belgrade metro line 1":       "belgrade_metro_line1",
    "belgrade metro line1":        "belgrade_metro_line1",
    "belgrade underground":        "belgrade_metro_line1",
    "belgrade airport":            "belgrade_airport",
    "belgrade fire station":       "belgrade_fire_station",
    "belgrade admin building":     "belgrade_admin_building",
    "belgrade wayfinding":         "belgrade_wayfinding",
    "nikola tesla landside":       "belgrade_nikola_tesla_landside",
    "beg landside":                "belgrade_nikola_tesla_landside",
    "belgrade landside":           "belgrade_nikola_tesla_landside",
    # These refer to the airport, not landside — align with EntitySynonymMapper
    "nikola tesla airport":        "belgrade_airport",
    "tesla airport":               "belgrade_airport",
    "belgrade nikola tesla":       "belgrade_airport",
    "belgrade nikola tesla airport": "belgrade_airport",
    "nikola tesla":                "belgrade_airport",
    # Doha projects
    "doha metro":                  "doha_metro_depot",
    "doha west metro":             "doha_metro_depot",
    "qatar metro":                 "doha_metro_depot",
    "qatar railways":              "qatar_railways_hq",
    "qatar rail hq":               "qatar_railways_hq",
    "qatar railways hq":           "qatar_railways_hq",
    # Lima / Callao
    "lima metro":                  "lima_metro_line1_stations",
    "lima metro line 1":           "lima_metro_line1_stations",
    "pachacamac metro":            "pachacamac_metro_station",
    "jorge chavez food hall":      "jorge_chavez_food_hall",
    "peru plaza":                  "lima_peru_plaza_food_court",
    # Cayenne (French Guiana)
    "cayenne airport":             "cayenne_terminal",
    "cayenne terminal":            "cayenne_terminal",
    "cayenne masterplan":          "cayenne_airport_masterplan",
    "cayenne interior":            "cayenne_interior_design",
    "cayenne offices":             "cayenne_airport_offices",
    "air guyane hangar":           "air_guyane_hangar",
    # Pointe-à-Pitre — ASCII-normalized variants (accent + hyphen handling)
    "pointe a pitre t1":           "pointe_a_pitre_t1",
    "pointe a pitre t2":           "pointe_a_pitre_t2",
    "pointe-a-pitre t1":           "pointe_a_pitre_t1",
    "pointe-a-pitre t2":           "pointe_a_pitre_t2",
    "guadeloupe airport":          "pointe_a_pitre_t1",
    "guadeloupe t1":               "pointe_a_pitre_t1",
    "guadeloupe t2":               "pointe_a_pitre_t2",
    "pap t1":                      "pointe_a_pitre_t1",
    "pap t2":                      "pointe_a_pitre_t2",
    "ptp t1":                      "pointe_a_pitre_t1",
    "ptp t2":                      "pointe_a_pitre_t2",
    # Velana / Maldives — city is "Malé" so city index won't catch "Velana"
    "velana":                      "velana_airport",
    "maldives airport":            "velana_airport",
    "maldives":                    "velana_airport",
    "male airport":                "velana_airport",
    # Tahiti / Papeete — city is "Papeete Faa'a" so short forms need aliases
    "tahiti":                      "papeete_airport",
    "tahiti airport":              "papeete_airport",
    "papeete":                     "papeete_airport",
    "french polynesia airport":    "papeete_airport",
    # AIK Bank
    "aik":                         "aik_bank_design",
    "aik bank":                    "aik_bank_design",
    # Sofia Airport — short forms and IATA-style
    "sofia":                       "sofia_airport",
    "sofia international":         "sofia_airport",
    "sof airport":                 "sofia_airport",
    "sofia t3":                    "sofia_airport",
    "t3 sofia":                    "sofia_airport",
    # Bordeaux–Mérignac
    "merignac":                    "bordeaux_airport",
    "bordeaux merignac":           "bordeaux_airport",
    "bordeaux merignac airport":   "bordeaux_airport",
    "bod airport":                 "bordeaux_airport",
    # Annecy
    "annecy":                      "annecy_airport",
    "annecy mont blanc":           "annecy_airport",
    "annecy mont-blanc airport":   "annecy_airport",
    "annecy general aviation":     "annecy_airport",
    # Conakry
    "conakry gbessia":             "conakry_airport",
    "gbessia airport":             "conakry_airport",
    "guinea airport":              "conakry_airport",
    "guinea conakry":              "conakry_airport",
    # Fuzhou
    "fuzhou":                      "fuzhou_airport",
    "fuzhou new airport":          "fuzhou_airport",
    "fujian airport":              "fuzhou_airport",
    # Lanzhou
    "lanzhou":                     "lanzhou_airport",
    "lanzhou new airport":         "lanzhou_airport",
    "gansu airport":               "lanzhou_airport",
    # Mashhad
    "mashhad":                     "mashhad_airport",
    "mashhad international":       "mashhad_airport",
    "mashhad iran":                "mashhad_airport",
    "iran airport":                "mashhad_airport",
    # Almaty
    "almaty":                      "almaty_airport",
    "almaty international":        "almaty_airport",
    "ala airport":                 "almaty_airport",
    "kazakhstan airport":          "almaty_airport",
    # Kigali / Bugesera
    "kigali":                      "kigali_airport",
    "kigali bugesera":             "kigali_airport",
    "bugesera airport":            "kigali_airport",
    "rwanda airport":              "kigali_airport",
    "kigali new airport":          "kigali_airport",
    # Tocumen / Panama
    "tocumen":                     "tocumen_airport",
    "panama airport":              "tocumen_airport",
    "panama city airport":         "tocumen_airport",
    "pty airport":                 "tocumen_airport",
    # Cusco
    "cusco":                       "cusco_airport",
    "cuzco":                       "cusco_airport",
    "cuzco airport":               "cusco_airport",
    "alejandro velasco astete":    "cusco_airport",
    "cusco peru":                  "cusco_airport",
    # Jaipur
    "jaipur":                      "jaipur_airport",
    "jaipur india":                "jaipur_airport",
    "jai airport":                 "jaipur_airport",
    # Ahmedabad
    "ahmedabad":                   "ahmedabad_airport",
    "sardar patel airport":        "ahmedabad_airport",
    "amd airport":                 "ahmedabad_airport",
    "gujarat airport":             "ahmedabad_airport",
    # Cergy Vertiport
    "cergy":                       "cergy_vertiport",
    "cergy pontoise":              "cergy_vertiport",
    "cergy pontoise vertiport":    "cergy_vertiport",
    "first european vertiport":    "cergy_vertiport",
    "taxidrone vertiport":         "cergy_vertiport",
    # Singapore Vertiport
    "voloport":                    "singapore_vertiport",
    "voloport singapore":          "singapore_vertiport",
    "singapore taxidrone":         "singapore_vertiport",
    # Paris Heliport / Issy-les-Moulineaux
    "issy heliport":               "paris_heliport",
    "issy les moulineaux":         "paris_heliport",
    "issy les moulineaux heliport": "paris_heliport",
    "paris issy":                  "paris_heliport",
    # Cabo Verde — 7 airports group
    "cape verde airports":         "cabo_verde_airports",
    "cabo verde seven airports":   "cabo_verde_airports",
    "cape verde seven airports":   "cabo_verde_airports",
    "cabo verde concession":       "cabo_verde_airports",
    # Amilcar Cabral / Cape Verde individual airports
    "amilcar cabral":              "amilcar_cabral_airport",
    "sal airport":                 "amilcar_cabral_airport",
    "cape verde sal":              "amilcar_cabral_airport",
    "aristides pereira":           "aristides_pereira_airport",
    "boa vista airport":           "aristides_pereira_airport",
    "nelson mandela airport":      "nelson_mandela_airport",
    "nelson mandela cabo verde":   "nelson_mandela_airport",
    "praia airport":               "nelson_mandela_airport",
    # Euroairport Basel-Mulhouse-Freiburg
    "euroairport":                 "euroairport_modernization",
    "basel airport":               "euroairport_modernization",
    "mulhouse airport":            "euroairport_modernization",
    "bsl airport":                 "euroairport_modernization",
    "basel mulhouse airport":      "euroairport_modernization",
    "euroairport south":           "euroairport_south_gates",
    "euroairport south gates":     "euroairport_south_gates",
    # Lima Metro stations
    "lima metro stations":         "lima_metro_line1_stations",
    "lima line 1":                 "lima_metro_line1_stations",
    "lima metro line 1 stations":  "lima_metro_line1_stations",
    # Pachacamac
    "pachacamac":                  "pachacamac_metro_station",
    "pachacamac station":          "pachacamac_metro_station",
    # Riga Control Tower
    "riga":                        "riga_control_tower",
    "riga tower":                  "riga_control_tower",
    "riga airport tower":          "riga_control_tower",
    "riga airport":                "riga_control_tower",
    "riga control":                "riga_control_tower",
    "latvia tower":                "riga_control_tower",
    # CDG Baggage Building
    "cdg baggage":                 "cdg_baggage_building",
    "charles de gaulle baggage":   "cdg_baggage_building",
    "roissy baggage":              "cdg_baggage_building",
    "cdg building":                "cdg_baggage_building",
    "paris cdg baggage":           "cdg_baggage_building",
    # Le Bourget Fire Station
    "le bourget":                  "le_bourget_fire_station",
    "bourget fire station":        "le_bourget_fire_station",
    "le bourget airport":          "le_bourget_fire_station",
    "bourget sslia":               "le_bourget_fire_station",
    # Belgrade Fire Station
    "nikola tesla fire station":   "belgrade_fire_station",
    "beg fire station":            "belgrade_fire_station",
    "belgrade airport fire station": "belgrade_fire_station",
    # Belgrade Admin Building
    "nikola tesla administration": "belgrade_admin_building",
    "beg admin building":          "belgrade_admin_building",
    "belgrade airport admin":      "belgrade_admin_building",
    # Belgrade Wayfinding
    "belgrade airport wayfinding": "belgrade_wayfinding",
    "nikola tesla wayfinding":     "belgrade_wayfinding",
    "beg wayfinding":              "belgrade_wayfinding",
    "belgrade signage":            "belgrade_wayfinding",
    # Tokyo EU Delegation
    "tokyo eu":                    "tokyo_eu_delegation",
    "eu delegation tokyo":         "tokyo_eu_delegation",
    "european delegation tokyo":   "tokyo_eu_delegation",
    "tokyo delegation":            "tokyo_eu_delegation",
    "japan eu building":           "tokyo_eu_delegation",
    # French Embassy Bangkok
    "french embassy":              "french_embassy_bangkok",
    "bangkok embassy":             "french_embassy_bangkok",
    "france embassy thailand":     "french_embassy_bangkok",
    "france embassy bangkok":      "french_embassy_bangkok",
    "france bangkok":              "french_embassy_bangkok",
    # Châteauroux (hard to spell)
    "chateauroux":                 "chateauroux_atct_mro",
    "chateauroux airport":         "chateauroux_atct_mro",
    "chateauroux tower":           "chateauroux_atct_mro",
    "chateauroux mro":             "chateauroux_atct_mro",
    # Greyfoot Paris
    "greyfoot":                    "greyfoot_paris",
    "greyfoot paris":              "greyfoot_paris",
    # Montijo Airport (Portugal)
    "montijo":                     "montijo_airport_commercial",
    "montijo airport":             "montijo_airport_commercial",
    "montijo portugal":            "montijo_airport_commercial",
    # Jorge Chavez Food Hall (Callao/Lima)
    "jorge chavez":                "jorge_chavez_food_hall",
    "jorge chavez food hall":      "jorge_chavez_food_hall",
    "lima food hall":              "jorge_chavez_food_hall",
    "callao food hall":            "jorge_chavez_food_hall",
    "jorge chavez airport":        "jorge_chavez_food_hall",
    # Lima Peru Plaza Food Court
    "peru plaza":                  "lima_peru_plaza_food_court",
    "peru plaza food court":       "lima_peru_plaza_food_court",
    "lima food court":             "lima_peru_plaza_food_court",
    "callao plaza":                "lima_peru_plaza_food_court",
    # Marseille Airport
    "marseille airport":           "marseille_commercial_assistance",
    "marseille provence":          "marseille_commercial_assistance",
    "mrs airport":                 "marseille_commercial_assistance",
    "marseille commercial":        "marseille_commercial_assistance",
    # Nantes Airport
    "nantes airport":              "nantes_commercial_zone",
    "nantes atlantique":           "nantes_commercial_zone",
    "nte airport":                 "nantes_commercial_zone",
    "nantes commercial":           "nantes_commercial_zone",
    # Lyon Airport
    "lyon airport":                "lyon_retail_shell",
    "lyon saint exupery":          "lyon_retail_shell",
    "saint-exupery airport":       "lyon_retail_shell",
    "lys airport":                 "lyon_retail_shell",
    "lyon retail":                 "lyon_retail_shell",
    # Cayenne Interior Design
    "cayenne interior design":     "cayenne_interior_design",
    "felix eboue interior":        "cayenne_interior_design",
    # Cayenne Airport Offices
    "cayenne cnes":                "cayenne_airport_offices",
    "air guyane offices":          "cayenne_airport_offices",
    # Santiago Wayfinding (Chile)
    "santiago wayfinding":         "santiago_wayfinding",
    "santiago chile wayfinding":   "santiago_wayfinding",
    "arturo merino benitez":       "santiago_wayfinding",
    "scl airport":                 "santiago_wayfinding",
    "santiago signage":            "santiago_wayfinding",
    # Lille Airport
    "lille":                       "lille_airport",
    "lille lesquin":               "lille_airport",
    "lil airport":                 "lille_airport",
})


def _ascii_norm(text: str) -> str:
    """Strip accents, lowercase, collapse hyphens → spaces for fuzzy comparison."""
    nfd = unicodedata.normalize("NFD", text)
    ascii_only = nfd.encode("ascii", "ignore").decode("ascii")
    return ascii_only.replace("-", " ").lower()


def _fuzzy_match_project(text: str) -> Optional[str]:
    """
    Try to find a project key from free text using fuzzy matching.
    Handles short forms ('belgrade metro'), typos ('nice sirport'), accented
    chars ('Pointe-à-Pitre'), country references ('Maldives'), and sentences.

    Priority:
      0a. Exact phrase lookup on original (lowercased) text
      0b. Exact phrase lookup on ASCII-normalised text (handles accents/hyphens)
      1.  Word-level fuzzy city match (skip generic transport/function words)
      2.  Fuzzy full-text match against all known names/aliases
    """
    import re as _re
    lower = _re.sub(r"[?!.,;:\"']", " ", text.lower())  # strip punctuation before split
    normed = _ascii_norm(lower)
    normed_words = normed.split()

    # 0a. Exact phrase lookup — original text (catches standard aliases + single words)
    all_words = lower.split()
    for size in range(min(4, len(all_words)), 0, -1):
        for i in range(len(all_words) - size + 1):
            phrase = ' '.join(all_words[i:i + size])
            if phrase in _NAME_INDEX:
                return _NAME_INDEX[phrase]

    # 0b. Exact phrase lookup — ASCII-normalised (catches "Pointe-à-Pitre T1", etc.)
    if normed != lower:
        for size in range(min(4, len(normed_words)), 0, -1):
            for i in range(len(normed_words) - size + 1):
                phrase = ' '.join(normed_words[i:i + size])
                if phrase in _NAME_INDEX:
                    return _NAME_INDEX[phrase]

    # 1. Match each meaningful word against unambiguous city names (fuzzy)
    for word in normed_words:
        if len(word) < 4 or word in _SKIP_WORDS:
            continue
        matches = get_close_matches(word, _CITY_INDEX.keys(), n=1, cutoff=0.82)
        if matches:
            return _CITY_INDEX[matches[0]]

    # 2. Fuzzy full-text match against all known display names / aliases
    # Cutoff 0.80 prevents false matches like "jfk airport" → "sof airport"
    matches = get_close_matches(normed, _NAME_INDEX.keys(), n=1, cutoff=0.80)
    if matches:
        return _NAME_INDEX[matches[0]]

    return None


# ── Formatting helpers ───────────────────────────────────────────────────────

def _short_overview(text: str, max_sentences: int = 2) -> str:
    """Return the first N complete sentences from an overview text."""
    clean = ' '.join(text.split())
    parts = clean.split('. ')
    result = '. '.join(parts[:max_sentences])
    if result and not result.endswith('.'):
        result += '.'
    return result


def _fmt_teaser(p: Dict) -> str:
    """Short intro card for ask_about_project — 2 sentences + tagline + follow-up."""
    intro = random.choice(_OVERVIEW_INTROS).format(name=p['display_name'])
    follow_up = random.choice(_FOLLOW_UP_PROMPTS)
    short = _short_overview(p['overview'])
    return f"{intro}\n\n_{p['tagline']}_\n\n{short}\n\n{follow_up}"


def _fmt_full_overview(p: Dict) -> str:
    """Full overview for explicit ask_project_overview requests."""
    variations = [
        f"**{p['display_name']}**\n\n_{p['tagline']}_\n\n{p['overview']}",
        f"Here's the full overview of **{p['display_name']}**:\n\n_{p['tagline']}_\n\n{p['overview']}",
    ]
    return random.choice(variations)


def _fmt_detail(label: str, value: str, emoji: str = "", project_name: str = "") -> str:
    prefix = f"{emoji} " if emoji else ""
    suffix = random.choice(_DETAIL_SUFFIXES)
    header = f"**{project_name}**\n\n" if project_name else ""
    return f"{header}{prefix}**{label}:** {value}{suffix}"


# ── Intent → info-type dispatch map ─────────────────────────────────────────

INFO_DISPATCH: Dict[str, Any] = {
    "about_project":  _fmt_teaser,
    "overview":       _fmt_full_overview,
    "location":       lambda p: _fmt_detail("Location", p['location'], "📍", p['display_name']),
    "year":           lambda p: _fmt_detail("Timeline", p['year'], "🗓", p['display_name']),
    "client":         lambda p: _fmt_detail("Client", p['client'], "👤", p['display_name']),
    "cost":           lambda p: _fmt_detail("Budget", p['cost'], "💶", p['display_name']),
    "area":           lambda p: _fmt_detail("Total area", p['area'], "📐", p['display_name']),
    "capacity":       lambda p: _fmt_detail("Passenger capacity", p['capacity'], "👥", p['display_name']),
    "architect":      lambda p: _fmt_detail("Architect", p['architect'], "🏛", p['display_name']),
    "partners":       lambda p: _fmt_detail("Partners", p['partners'], "🤝", p['display_name']),
    "challenge":      lambda p: (
        f"**Key Challenge — {p['display_name']}**\n\n{p['key_challenge']}"
        + random.choice(_DETAIL_SUFFIXES)
    ),
    "approach":       lambda p: (
        f"**Design Approach — {p['display_name']}**\n\n{p['approach']}"
        + random.choice(_DETAIL_SUFFIXES)
    ),
    "5star":          lambda p: f"**5-Star Certification — {p['display_name']}**\n\n{p['five_star_detail']}",
    "video":          lambda p: (
        f"Here's a video of **{p['display_name']}** — take a look:\n\n{p['video_url']}"
        if p.get('video_url')
        else (
            f"We don't have public media for **{p['display_name']}** yet. "
            f"Check [1pax.com](https://1pax.com) for the latest."
        )
    ),
    "sustainability": lambda p: (
        f"**Sustainability — {p['display_name']}**\n\n{p['sustainability']}"
        + random.choice(_DETAIL_SUFFIXES)
    ),
    "concept":    lambda p: (
        f"💡 **Design Concept — {p['display_name']}**\n\n_{p['tagline']}_"
        + random.choice(_DETAIL_SUFFIXES)
    ),
    "status": lambda p: _fmt_detail(
        "Current Status", p.get('status', 'Status information not available.'), "🔄", p['display_name']
    ),
    "tender":  lambda p: _fmt_detail(
        "How 1PAX Was Selected", p.get('tender_result', 'Information not available.'), "🏆", p['display_name']
    ),
    "scope":   lambda p: _fmt_detail(
        "1PAX's Role / Scope", p.get('scope', 'Information not available.'), "🎯", p['display_name']
    ),
    "program": lambda p: (
        f"**Programme — {p['display_name']}**\n\n{p.get('program', 'Programme details not available.')}"
        + random.choice(_DETAIL_SUFFIXES)
    ),
    "facts":   lambda p: (
        f"**Key Highlights — {p['display_name']}**\n\n{p.get('fun_facts', 'Details not available.')}"
        + random.choice(_DETAIL_SUFFIXES)
    ),
}


# ── Resolve project from entity / fuzzy / slot ───────────────────────────────


# Generic words that, when extracted as an entity, do NOT unambiguously
# identify a specific project — slot context should take precedence.
_GENERIC_PROJECT_REF = {
    "the", "this", "that", "these", "those", "it", "them", "here", "there",
    "a", "an", "airport", "terminal", "station", "depot", "tower", "building",
    "project", "hub", "port", "base", "facility",
}


def _resolve_project(tracker: Tracker) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Returns (project_key, project_dict).
    Priority:
      1. Any extracted entity that is a canonical PROJECTS key
      2. Fuzzy match on any extracted entity value
      3. Fuzzy match on full message text
      4. Slot context (carry-over from previous turn)

    Only blocks slot fallback when a *meaningful* entity (not a generic
    building-type word like 'depot', 'tower', 'terminal', or articles like
    'the') was explicitly extracted but didn't match any project.
    """
    entity_values = list(tracker.get_latest_entity_values("project"))
    raw_text = tracker.latest_message.get("text", "")

    # Partition entities into meaningful vs generic/spurious
    meaningful = [ev for ev in entity_values
                  if ev.lower() not in _GENERIC_PROJECT_REF and len(ev) > 3]

    # 1. Try each meaningful entity for a canonical PROJECTS key
    for ev in meaningful:
        if ev in PROJECTS:
            return ev, PROJECTS[ev]

    # 2. Fuzzy match on each meaningful entity value
    for ev in meaningful:
        fuzzy_key = _fuzzy_match_project(ev)
        if fuzzy_key:
            return fuzzy_key, PROJECTS.get(fuzzy_key)

    # 3. Meaningful entity was present but didn't match — signal not found.
    # Do NOT fall through to slot (it would return the wrong project).
    if meaningful:
        return None, None

    # 4. No meaningful entity — try fuzzy on the full message text
    fuzzy_key = _fuzzy_match_project(raw_text)
    if fuzzy_key:
        return fuzzy_key, PROJECTS.get(fuzzy_key)

    # 5. Fall back to slot (conversation context).
    # Rasa auto-fills project_name from the entity BEFORE the action runs, so
    # the slot may now hold a generic/invalid entity text (e.g. "depot"). If the
    # current slot value is not a valid PROJECTS key, scan the event history for
    # the most recent valid project.
    slot_key = tracker.get_slot("project_name")
    if not slot_key:
        return None, None
    if slot_key in PROJECTS:
        return slot_key, PROJECTS[slot_key]
    # Slot was auto-filled with an invalid value — find the last valid one
    for event in reversed(list(tracker.events)):
        if event.get("event") == "slot" and event.get("name") == "project_name":
            old_val = event.get("value")
            if old_val and old_val != slot_key and old_val in PROJECTS:
                return old_val, PROJECTS[old_val]
    return None, None


def _intent_to_info_type(intent_name: str) -> str:
    if intent_name == "ask_about_project":
        return "about_project"
    prefix = "ask_project_"
    if intent_name.startswith(prefix):
        return intent_name[len(prefix):]
    return "about_project"


# ── Actions ──────────────────────────────────────────────────────────────────

class ActionAnswerProjectQuery(Action):
    """
    Single router action for all project detail intents.
    Handles: ask_about_project, ask_project_overview, ask_project_location,
    ask_project_year, ask_project_client, ask_project_cost, ask_project_area,
    ask_project_capacity, ask_project_architect, ask_project_partners,
    ask_project_challenge, ask_project_approach, ask_project_5star,
    ask_project_video, ask_project_sustainability.
    """

    def name(self) -> Text:
        return "action_answer_project_query"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        lang = get_lang(tracker)
        lang_event = [SlotSet("language", lang)] if lang else []

        entity_value = next(tracker.get_latest_entity_values("project"), None)
        project_key, project = _resolve_project(tracker)

        if not project_key:
            if entity_value:
                dispatcher.utter_message(text=translate_response(
                    random.choice([
                        "I don't have data on that project yet. Try 'list projects' to see all 58 projects in our portfolio.",
                        "Hmm, I can't find that one. Ask 'what projects do you have?' to browse the full catalogue.",
                    ]), lang
                ))
            else:
                dispatcher.utter_message(text=translate_response(
                    random.choice([
                        "Which project are you asking about? You can name a city, airport, or project — like **Sofia Airport**, **Belgrade Metro**, or **Lima Food Hall**.",
                        "Sure! Which project did you have in mind? Try saying **Tahiti airport**, **Paris Heliport**, or type 'list projects' for the full catalogue.",
                        "I'd love to help — which project are you interested in? Ask 'what projects do you have?' for the full list of 58 projects.",
                    ]), lang
                ))
            return lang_event

        if not project:
            dispatcher.utter_message(text=translate_response(random.choice([
                (
                    "I don't have details on that project yet. Try asking about "
                    "**Sofia Airport**, **Belgrade Airport**, or type 'list projects' "
                    "to browse all 58 projects."
                ),
                (
                    "Hmm, I can't find that one. Ask 'what projects do you have?' "
                    "to see the full list — there are 58 to explore!"
                ),
            ]), lang))
            return lang_event

        intent_name = tracker.latest_message.get("intent", {}).get("name", "")
        info_type = _intent_to_info_type(intent_name)
        raw_msg = tracker.latest_message.get("text", "").lower()

        # Special case: photo query routed to video intent → acknowledge mismatch
        if info_type == "video":
            _photo_words = {"photo", "photos", "image", "images", "picture", "pictures", "pic", "pics"}
            if any(w in raw_msg.split() for w in _photo_words):
                if project.get("video_url"):
                    dispatcher.utter_message(text=translate_response(
                        f"I don't have individual project photos, but there's a video of "
                        f"**{project['display_name']}** you can check out:\n\n{project['video_url']}",
                        lang,
                    ))
                else:
                    dispatcher.utter_message(text=translate_response(
                        f"We don't have photos or media for **{project['display_name']}** yet — "
                        f"check [1pax.com](https://1pax.com) for the latest.",
                        lang,
                    ))
                return [SlotSet("project_name", project_key)] + lang_event

        # Special case: "ask_about_project" with no new entity = "what else can you tell me"
        # Show highlights instead of repeating the intro teaser
        if info_type == "about_project":
            entity_value = next(tracker.get_latest_entity_values("project"), None)
            if not entity_value:
                info_type = "facts"

        formatter = INFO_DISPATCH.get(info_type, _fmt_teaser)
        dispatcher.utter_message(text=translate_response(formatter(project), lang))
        return [SlotSet("project_name", project_key)] + lang_event


class ActionListProjects(Action):
    """Lists all projects grouped by category."""

    def name(self) -> Text:
        return "action_list_projects"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        lang = get_lang(tracker)
        lang_event = [SlotSet("language", lang)] if lang else []

        if not PROJECTS:
            dispatcher.utter_message(
                text=translate_response("No projects in the database yet — check back soon!", lang)
            )
            return lang_event

        lines = [random.choice([
            "Here are 1PAX's architectural projects:\n",
            "1PAX's portfolio spans 6 categories — here's the full list:\n",
            "These are all 58 1PAX projects across our portfolio:\n",
        ])]

        for category, project_keys in CATEGORIES.items():
            lines.append(f"**{category}**")
            for key in project_keys:
                p = PROJECTS[key]
                lines.append(
                    f"  • **{p['display_name']}** — {p['location']} ({p['year']})"
                )
            lines.append("")

        lines.append(random.choice([
            "Ask me anything about a project — cost, design challenge, team, and more!",
            "Just name a project and I'll tell you all about it — budget, approach, sustainability, and more.",
            "Pick any project and ask away — I can cover cost, location, design approach, and much more.",
        ]))

        dispatcher.utter_message(text=translate_response("\n".join(lines), lang))
        return lang_event


class ActionHandleOutOfScope(Action):
    """
    Context-aware handler for out_of_scope and nlu_fallback.
    If a project is active in the slot, invites the user to continue exploring it.
    If not, nudges the user toward the portfolio.
    """

    def name(self) -> Text:
        return "action_handle_out_of_scope"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        lang = get_lang(tracker)
        lang_event = [SlotSet("language", lang)] if lang else []

        user_text = tracker.latest_message.get("text", "")
        lower_text = user_text.lower()

        # ── Capability question: "what can you do", "what else can you do", etc. ─
        _CAP_SIGNALS = {"what can you do", "what else can you do", "what do you offer",
                        "what are you capable of", "what do you know", "what can you help",
                        "what are your features", "what are your capabilities",
                        "what can you tell me about", "what topics do you cover",
                        "what can you answer", "how can you help"}
        if any(sig in lower_text for sig in _CAP_SIGNALS):
            dispatcher.utter_message(text=translate_response(
                "Here's what I can help you with:\n\n"
                "**About 1PAX as a studio:**\n"
                "• Who we are, our mission and history\n"
                "• Our founder (Mabel Miranda) and team\n"
                "• Office locations and how we work\n"
                "• Design approach and principles\n"
                "• Sustainability, innovation, and urbanism\n"
                "• Careers, culture, and open roles\n\n"
                "**Our project portfolio (58 projects):**\n"
                "• Ask *'show me all projects'* to browse by category\n"
                "• Ask about any project by name, city, or airport code\n"
                "• For any project: location, year, client, budget, design concept, "
                "key challenge, sustainability, team, highlights, and more\n\n"
                "Try: _'Tell me about 1PAX'_, _'who founded the studio?'_, or _'tell me about Sofia Airport'_.",
                lang,
            ))
            return [SlotSet("project_name", None)] + lang_event

        # ── Safety net: try to fuzzy-match a project from the raw message ────────
        # This catches cases where NLU misfires on bare project names or typos
        # (e.g. "fuzhou airport", "greyfoot paris", "aik bankk") before giving up.
        # Skip if the message looks like a genuine OOS query (weather, time, etc.)
        _OOS_SIGNALS = {"weather", "temperature", "forecast", "rain", "raining",
                        "sunny", "time", "joke", "taxi", "uber", "order", "pizza",
                        "translate", "news", "stock", "president", "restaurant"}
        _is_genuine_oos = any(w in lower_text for w in _OOS_SIGNALS)
        fuzzy_key = None if _is_genuine_oos else _fuzzy_match_project(user_text)
        if fuzzy_key and fuzzy_key in PROJECTS:
            p = PROJECTS[fuzzy_key]
            for text in _fmt_teaser(p).split("\n\n"):
                if text.strip():
                    dispatcher.utter_message(text=translate_response(text.strip(), lang))
            return [SlotSet("project_name", fuzzy_key)] + lang_event

        # ── Normal out-of-scope / fallback handling ───────────────────────────────
        project_key = tracker.get_slot("project_name")

        if project_key and project_key in PROJECTS:
            p = PROJECTS[project_key]
            msg = random.choice(_OUT_OF_SCOPE_WITH_CONTEXT).format(
                name=p['display_name']
            )
        else:
            msg = random.choice(_OUT_OF_SCOPE_NO_CONTEXT)

        dispatcher.utter_message(text=translate_response(msg, lang))
        return lang_event
