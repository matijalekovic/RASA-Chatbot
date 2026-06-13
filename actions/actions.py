"""
Custom actions for the 1PAX company chatbot.

ActionAnswerProjectQuery  — handles all project detail intents.
ActionListProjects         — lists projects, optionally filtered by category.
ActionHandleOutOfScope     — context-aware handler for unrecognised inputs.
"""

import random
import re
import unicodedata
from difflib import SequenceMatcher, get_close_matches
from typing import Any, Dict, List, Optional, Set, Text, Tuple

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from .projects_data import PROJECTS, CATEGORIES
from .translation import get_lang, translate_response
from .meeting_prompts import meeting_buttons, meeting_cta_text


def _continue_schedule_if_active(dispatcher, tracker, domain):
    from .calendly_actions import continue_active_calendly_scheduling

    return continue_active_calendly_scheduling(dispatcher, tracker, domain)


def _schedule_topic_shift_events(tracker):
    from .calendly_actions import schedule_topic_shift_events

    return schedule_topic_shift_events(tracker)


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

_PHOTO_WORDS = {"photo", "photos", "image", "images", "picture", "pictures", "pic", "pics"}

_PROJECT_LINK_LABELS = {
    "FR": "Voir la page du projet",
    "ES": "Ver la página del proyecto",
    "PT-PT": "Ver a página do projeto",
    "PT-BR": "Ver a página do projeto",
    "ZH-HANS": "查看项目页面",
    "ZH-HANT": "查看專案頁面",
    "SR": "Pogledaj stranicu projekta",
}

_PROJECT_MEETING_INFO_TYPES = {
    "about_project",
    "overview",
    "approach",
    "challenge",
    "scope",
    "program",
    "sustainability",
}

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
        "For direct contact, visit **1pax.com** or ask me to **schedule a meeting**."
    ),
    (
        "That's a bit outside my lane — I'm all about 1PAX's portfolio. "
        "Try naming a project (like **Sofia Airport** or **Belgrade Metro**) and I'll tell you everything about it. "
        "To reach 1PAX directly, head to **1pax.com** or ask me to **schedule a meeting**."
    ),
    (
        "Not quite my territory — I focus on 1PAX's projects. "
        "Ask 'show me all projects' or just name one and we can go from there. "
        "To contact the team, visit **1pax.com** or ask me to **schedule a meeting**."
    ),
]


_PROJECT_LIST_TEXT = {
    "FR": {
        "intro": "Voici les 57 projets de 1PAX dans notre portefeuille :\n",
        "suffix": "Posez-moi n'importe quelle question sur un projet — coût, défi de conception, équipe, et plus encore !",
        "cta": "Si ce projet est proche de ce que vous planifiez, je peux vous aider à planifier une réunion avec 1PAX.",
        "categories": {
            "Airports and Transportation": "Aéroports et transports",
            "Future of Mobility": "Futur de la mobilité",
            "Industrial Buildings": "Bâtiments industriels",
            "Working and Living": "Espaces de travail et de vie",
            "Urbanism and Masterplan": "Urbanisme et masterplan",
            "Interior Design": "Design d'intérieur",
        },
    },
    "ES": {
        "intro": "Estos son los 57 proyectos de 1PAX en nuestro portafolio:\n",
        "suffix": "Pregúnteme cualquier cosa sobre un proyecto: coste, desafío de diseño, equipo y más.",
        "cta": "Si este proyecto se parece a algo que está planificando, puedo ayudarle a programar una reunión con 1PAX.",
        "categories": {
            "Airports and Transportation": "Aeropuertos y transporte",
            "Future of Mobility": "Futuro de la movilidad",
            "Industrial Buildings": "Edificios industriales",
            "Working and Living": "Espacios de trabajo y vivienda",
            "Urbanism and Masterplan": "Urbanismo y masterplan",
            "Interior Design": "Diseño interior",
        },
    },
    "PT": {
        "intro": "Estes são os 57 projetos da 1PAX no nosso portefólio:\n",
        "suffix": "Pergunte-me qualquer coisa sobre um projeto — custo, desafio de design, equipa e muito mais.",
        "cta": "Se este projeto for próximo de algo que está a planear, posso ajudar a agendar uma reunião com a 1PAX.",
        "categories": {
            "Airports and Transportation": "Aeroportos e transportes",
            "Future of Mobility": "Futuro da mobilidade",
            "Industrial Buildings": "Edifícios industriais",
            "Working and Living": "Espaços de trabalho e vida",
            "Urbanism and Masterplan": "Urbanismo e masterplan",
            "Interior Design": "Design de interiores",
        },
    },
    "ZH": {
        "intro": "以下是 1PAX 项目组合中的 57 个项目：\n",
        "suffix": "您可以询问任何项目相关问题：成本、设计挑战、团队等。",
        "cta": "如果这个项目接近您正在规划的内容，我可以帮助您与 1PAX 安排会议。",
        "categories": {
            "Airports and Transportation": "机场与交通",
            "Future of Mobility": "未来出行",
            "Industrial Buildings": "工业建筑",
            "Working and Living": "工作与生活空间",
            "Urbanism and Masterplan": "城市规划与总体规划",
            "Interior Design": "室内设计",
        },
    },
    "SR": {
        "intro": "Ovo je svih 57 projekata iz 1PAX portfolija:\n",
        "suffix": "Pitajte me bilo šta o projektu — troškovima, izazovu dizajna, timu i još mnogo toga.",
        "cta": "Ako je ovaj projekat sličan nečemu što planirate, mogu vam pomoći da zakažete sastanak sa 1PAX.",
        "categories": {
            "Airports and Transportation": "Aerodromi i saobraćaj",
            "Future of Mobility": "Budućnost mobilnosti",
            "Industrial Buildings": "Industrijski objekti",
            "Working and Living": "Radni i stambeni prostori",
            "Urbanism and Masterplan": "Urbanizam i masterplan",
            "Interior Design": "Dizajn enterijera",
        },
    },
}


def _project_list_lang(lang: Optional[str]) -> Optional[str]:
    if not lang:
        return None
    normalized = lang.upper()
    if normalized.startswith("EN"):
        return None
    if normalized.startswith("PT"):
        return "PT"
    if normalized.startswith("ZH"):
        return "ZH"
    return normalized if normalized in _PROJECT_LIST_TEXT else None


def _localized_project_list_text(lang: Optional[str], key: str, fallback: str) -> str:
    lang_key = _project_list_lang(lang)
    if not lang_key:
        return fallback
    return _PROJECT_LIST_TEXT[lang_key].get(key, fallback)


def _localized_project_category(category: str, lang: Optional[str]) -> str:
    lang_key = _project_list_lang(lang)
    if not lang_key:
        return category
    return _PROJECT_LIST_TEXT[lang_key]["categories"].get(category, category)


# ── Greet / Goodbye / Bot challenge ─────────────────────────────────────────


class ActionGreet(Action):
    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher, tracker, domain):
        schedule_events = _continue_schedule_if_active(dispatcher, tracker, domain)
        if schedule_events is not None:
            return schedule_events
        schedule_reset_events = _schedule_topic_shift_events(tracker)

        lang = get_lang(tracker)
        dispatcher.utter_message(
            text=translate_response(random.choice([
                "Hi! I can tell you about 1PAX — our studio, mission, design approach, team, or careers — help you explore our 57 architectural projects, or help schedule a meeting. What would you like to know?",
                "Hello! Ask about the studio, our founder, design philosophy, sustainability commitment, explore our project portfolio, or schedule a meeting with 1PAX. Where would you like to start?",
                "Welcome! I can answer questions about 1PAX as a studio — our mission, values, team, and approach — dive into any of our 57 projects, or help you schedule a meeting. What's on your mind?",
                "Hello! Ask me about 1PAX — who we are, how we work, what we build, or where we're based. You can also say 'show me all projects' or schedule a meeting with the studio.",
            ]), lang),
            buttons=meeting_buttons(lang),
        )
        return schedule_reset_events + ([SlotSet("language", lang)] if lang else [])


class ActionGoodbye(Action):
    def name(self) -> Text:
        return "action_goodbye"

    def run(self, dispatcher, tracker, domain):
        schedule_events = _continue_schedule_if_active(dispatcher, tracker, domain)
        if schedule_events is not None:
            return schedule_events

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
        schedule_events = _continue_schedule_if_active(dispatcher, tracker, domain)
        if schedule_events is not None:
            return schedule_events

        lang = get_lang(tracker)
        dispatcher.utter_message(text=translate_response(random.choice([
            "I'm the 1PAX virtual assistant, here to help you explore our architectural portfolio. I'm powered by Rasa.",
            "I'm a chatbot built to answer questions about 1PAX's projects — airports, mobility infrastructure, interior design, and more.",
            "I'm the 1PAX assistant — an AI built to guide you through our portfolio of 57 architectural projects.",
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
    "airport in belgrade":         "belgrade_airport",
    "the airport in belgrade":     "belgrade_airport",
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
    "biggest project":             "sofia_airport",
    "the biggest project":         "sofia_airport",
    "our biggest project":         "sofia_airport",
    "your biggest project":        "sofia_airport",
    "flagship project":            "sofia_airport",
    "the flagship project":        "sofia_airport",
    "our flagship project":        "sofia_airport",
    "your flagship project":       "sofia_airport",
    "airport project":             "sofia_airport",
    "terminal project":            "sofia_airport",
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
    "santiago international airport wayfinding design": "santiago_wayfinding",
    "santiago international airport wayfinding design signage": "santiago_wayfinding",
    "arturo merino benitez":       "santiago_wayfinding",
    "scl airport":                 "santiago_wayfinding",
    "santiago signage":            "santiago_wayfinding",
    # Lille Airport
    "lille":                       "lille_airport",
    "lille lesquin":               "lille_airport",
    "lil airport":                 "lille_airport",
    # Current public website titles that differ from internal display names
    "al wakrah metro depot masterplan": "doha_metro_depot",
    "qatar railways al wakrah metro depot masterplan": "doha_metro_depot",
    "bordeaux international airport hall b terminal new facades": "bordeaux_airport",
    "design of five airports in cape verde": "cabo_verde_airports",
    "industrial building for baggage handling system architectural design": "cdg_baggage_building",
    "hangar for air guyane cayenne airport": "air_guyane_hangar",
    "hangar for air guyanne cayenne airport": "air_guyane_hangar",
    "belgrade airport administration building": "belgrade_admin_building",
    "belgrade airport main fire station": "belgrade_fire_station",
    "landside design nikola tesla airport": "belgrade_nikola_tesla_landside",
    "nikola tesla airport landside design vehicle simulation": "belgrade_nikola_tesla_landside",
    "nikola tesla international airport wayfinding signage design": "belgrade_wayfinding",
    "pointe a pitre international airport new extension": "pointe_a_pitre_t1",
    "pointe a pitre international airport new terminal extension": "pointe_a_pitre_t1",
    "pointe a pitre international airport t2 extension": "pointe_a_pitre_t2",
    "velana international airport interior design": "velana_airport",
})


def _ascii_norm(text: str) -> str:
    """Strip accents and collapse punctuation to spaces for fuzzy comparison."""
    nfd = unicodedata.normalize("NFD", text)
    ascii_only = nfd.encode("ascii", "ignore").decode("ascii")
    ascii_only = re.sub(r"[^a-zA-Z0-9]+", " ", ascii_only.lower())
    return " ".join(ascii_only.split())


def _contains_normalized_phrase(text: str, phrase: str) -> bool:
    return f" {phrase} " in f" {text} "


# ── Project geolocation ─────────────────────────────────────────────────────

_GEO_AREA_INFO: Dict[str, Dict[str, Tuple[str, ...]]] = {
    "Bulgaria": {
        "aliases": ("bulgarian",),
        "regions": ("Europe", "Balkans", "Southeast Europe"),
    },
    "Serbia": {
        "aliases": ("serbian",),
        "regions": ("Europe", "Balkans", "Southeast Europe"),
    },
    "Maldives": {
        "aliases": ("maldivian",),
        "regions": ("Asia", "South Asia", "Indian Ocean"),
    },
    "France": {
        "aliases": ("french", "metropolitan france"),
        "regions": ("Europe", "Western Europe"),
    },
    "French Guiana": {
        "aliases": ("guyane", "cayenne", "french guyana"),
        "regions": ("South America", "Latin America"),
    },
    "Guadeloupe": {
        "aliases": ("pointe a pitre", "pointe-a-pitre"),
        "regions": ("Caribbean", "Latin America"),
    },
    "Guinea": {
        "aliases": ("guinean", "conakry"),
        "regions": ("Africa", "West Africa", "Francophone Africa"),
    },
    "French Polynesia": {
        "aliases": ("tahiti", "papeete"),
        "regions": ("Oceania", "Pacific"),
    },
    "Cabo Verde": {
        "aliases": ("cape verde", "macaronesia"),
        "regions": ("Africa", "West Africa", "Macaronesia", "Francophone Africa"),
    },
    "China": {
        "aliases": ("chinese",),
        "regions": ("Asia", "East Asia"),
    },
    "Iran": {
        "aliases": ("iranian", "mashhad"),
        "regions": ("Asia", "Middle East"),
    },
    "Kazakhstan": {
        "aliases": ("kazakh", "almaty"),
        "regions": ("Asia", "Central Asia"),
    },
    "Rwanda": {
        "aliases": ("rwandan", "kigali"),
        "regions": ("Africa", "East Africa", "Francophone Africa"),
    },
    "Panama": {
        "aliases": ("panamanian", "tocumen", "panama city"),
        "regions": ("Latin America", "Central America"),
    },
    "Peru": {
        "aliases": ("peruvian", "lima", "callao", "cusco", "cuzco"),
        "regions": ("South America", "Latin America"),
    },
    "India": {
        "aliases": ("indian",),
        "regions": ("Asia", "South Asia"),
    },
    "Singapore": {
        "aliases": ("singaporean",),
        "regions": ("Asia", "Southeast Asia"),
    },
    "Qatar": {
        "aliases": ("qatari", "doha", "gulf"),
        "regions": ("Asia", "Middle East", "Gulf Region"),
    },
    "Latvia": {
        "aliases": ("latvian", "riga"),
        "regions": ("Europe", "Baltics"),
    },
    "Japan": {
        "aliases": ("japanese", "tokyo"),
        "regions": ("Asia", "East Asia"),
    },
    "Thailand": {
        "aliases": ("thai", "bangkok"),
        "regions": ("Asia", "Southeast Asia"),
    },
    "Portugal": {
        "aliases": ("portuguese", "montijo"),
        "regions": ("Europe", "Western Europe"),
    },
    "Chile": {
        "aliases": ("chilean", "santiago", "santiago de chile"),
        "regions": ("South America", "Latin America"),
    },
    # Known broader client/geography references without a project row today.
    "Mexico": {
        "aliases": ("mexican",),
        "regions": ("Latin America", "North America"),
    },
    "Bolivia": {
        "aliases": ("bolivian",),
        "regions": ("South America", "Latin America"),
    },
    "Senegal": {
        "aliases": ("senegalese",),
        "regions": ("Africa", "West Africa", "Francophone Africa"),
    },
    # Common geography filters where the public project database has no
    # standalone project today. Keeping them here prevents filtered project
    # queries from falling through to the full portfolio list.
    "Australia": {
        "aliases": ("australian", "sydney", "melbourne", "brisbane", "perth"),
        "regions": ("Oceania", "Pacific"),
    },
    "United States": {
        "aliases": ("usa", "u s a", "united states of america", "american"),
        "regions": ("North America",),
    },
    "Canada": {
        "aliases": ("canadian",),
        "regions": ("North America",),
    },
    "United Kingdom": {
        "aliases": ("uk", "u k", "great britain", "britain", "england", "london", "british"),
        "regions": ("Europe", "Western Europe"),
    },
    "Spain": {
        "aliases": ("spanish", "barcelona", "madrid"),
        "regions": ("Europe", "Western Europe"),
    },
    "Belgium": {
        "aliases": ("belgian", "brussels"),
        "regions": ("Europe", "Western Europe"),
    },
    "Germany": {
        "aliases": ("german", "berlin", "frankfurt", "munich"),
        "regions": ("Europe", "Western Europe"),
    },
    "Switzerland": {
        "aliases": ("swiss", "zurich", "geneva"),
        "regions": ("Europe", "Western Europe"),
    },
    "Italy": {
        "aliases": ("italian", "rome", "milan"),
        "regions": ("Europe", "Western Europe"),
    },
    "Netherlands": {
        "aliases": ("dutch", "amsterdam"),
        "regions": ("Europe", "Western Europe"),
    },
    "Brazil": {
        "aliases": ("brazilian",),
        "regions": ("South America", "Latin America"),
    },
    "Argentina": {
        "aliases": ("argentinian", "argentine"),
        "regions": ("South America", "Latin America"),
    },
    "Colombia": {
        "aliases": ("colombian",),
        "regions": ("South America", "Latin America"),
    },
    "Morocco": {
        "aliases": ("moroccan", "casablanca", "marrakesh", "marrakech", "rabat"),
        "regions": ("Africa", "North Africa", "Francophone Africa"),
    },
    "Algeria": {
        "aliases": ("algerian", "algiers"),
        "regions": ("Africa", "North Africa", "Francophone Africa"),
    },
    "Egypt": {
        "aliases": ("egyptian", "cairo"),
        "regions": ("Africa", "North Africa"),
    },
    "United Arab Emirates": {
        "aliases": ("uae", "u a e", "emirati"),
        "regions": ("Asia", "Middle East", "Gulf Region"),
    },
    "Saudi Arabia": {
        "aliases": ("saudi", "riyadh", "jeddah"),
        "regions": ("Asia", "Middle East", "Gulf Region"),
    },
    "Turkey": {
        "aliases": ("turkish", "istanbul"),
        "regions": ("Europe", "Asia", "Middle East"),
    },
}

_GEO_REGION_ALIASES: Dict[str, Tuple[str, ...]] = {
    "Europe": ("european", "eu", "western europe", "southeast europe", "balkans", "balkan"),
    "Asia": ("asian", "east asia", "south asia", "southeast asia", "central asia"),
    "Africa": ("african",),
    "Latin America": ("latin american", "latam", "central america", "central and south america"),
    "South America": ("south american",),
    "Middle East": ("middle east", "middle eastern", "gulf", "gulf region"),
    "Caribbean": ("caribbean",),
    "Francophone Africa": ("francophone africa", "french speaking africa", "french-speaking africa"),
    "West Africa": ("west africa", "western africa"),
    "North Africa": ("north africa", "northern africa"),
    "North America": ("north america", "north american"),
    "Oceania": ("oceania", "pacific"),
}

_GEO_BROWSE_CUES = (
    "airport",
    "airports",
    "built",
    "delivered",
    "designed",
    "did",
    "do in",
    "done",
    "experience",
    "have in",
    "portfolio",
    "project",
    "projects",
    "show me",
    "what work",
    "what did",
    "work in",
    "worked in",
)

_COUNTRY_ONLY_FALLBACKS = {
    "Mexico": "Latin America",
    "Bolivia": "Latin America",
    "Senegal": "Africa",
}

_GEO_REGION_NOTES = {
    "Latin America": (
        "Broader regional references also include **Bolivia**, although no standalone "
        "Bolivia project is currently listed in the project database."
    ),
    "South America": (
        "For the wider **Latin America** portfolio, 1PAX also has work in **Panama** "
        "and **Guadeloupe**. Broader regional references include **Bolivia**, although "
        "no standalone Bolivia project is currently listed in the project database."
    ),
}


def _geo_area_regions(area: str) -> Set[str]:
    return set(_GEO_AREA_INFO.get(area, {}).get("regions", ()))


def _areas_for_region(region: str) -> Set[str]:
    return {
        area
        for area in _GEO_AREA_INFO
        if region == area or region in _geo_area_regions(area)
    }


def _project_geo_areas(project: Dict) -> Tuple[str, ...]:
    location_norm = _ascii_norm(project.get("location", ""))
    areas = []
    for area in _GEO_AREA_INFO:
        area_norm = _ascii_norm(area)
        if _contains_normalized_phrase(location_norm, area_norm):
            areas.append(area)
    return tuple(areas)


_PROJECT_GEO_AREAS: Dict[str, Tuple[str, ...]] = {
    key: _project_geo_areas(project)
    for key, project in PROJECTS.items()
}

_PROJECT_ORDER = {
    key: index
    for index, key in enumerate(
        key
        for project_keys in CATEGORIES.values()
        for key in project_keys
    )
}

_GEO_TARGETS: Dict[str, Dict[str, Any]] = {}
for _area, _info in _GEO_AREA_INFO.items():
    for _alias in (_area, *_info.get("aliases", ())):
        _GEO_TARGETS[_ascii_norm(_alias)] = {
            "kind": "area",
            "label": _area,
            "areas": {_area},
            "fallback_region": _COUNTRY_ONLY_FALLBACKS.get(_area),
        }

for _region, _aliases in _GEO_REGION_ALIASES.items():
    for _alias in (_region, *_aliases):
        _GEO_TARGETS[_ascii_norm(_alias)] = {
            "kind": "region",
            "label": _region,
            "areas": _areas_for_region(_region),
            "fallback_region": None,
        }

_SORTED_GEO_TARGETS = sorted(
    _GEO_TARGETS.items(),
    key=lambda item: (len(item[0].split()), len(item[0])),
    reverse=True,
)


def _find_geo_target(text: str) -> Optional[Dict[str, Any]]:
    normalized = _ascii_norm(text or "")
    if not normalized:
        return None

    for alias, target in _SORTED_GEO_TARGETS:
        if _contains_normalized_phrase(normalized, alias):
            return target
    return None


def _looks_like_project_geo_query(text: str) -> bool:
    normalized = _ascii_norm(text or "")
    if not normalized or not _find_geo_target(normalized):
        return False
    words = set(normalized.split())
    plural_or_browse = any(
        cue in normalized
        for cue in (
            "projects",
            "show me",
            "list",
            "what projects",
            "which projects",
            "what work",
            "what did",
            "experience",
            "worked in",
            "work in",
            "have in",
            "done",
            "delivered",
            "designed",
        )
    )
    if "projects" not in words and not plural_or_browse and _fuzzy_match_project(text):
        return False
    return any(cue in normalized for cue in _GEO_BROWSE_CUES)


def _project_keys_for_areas(areas: Set[str]) -> List[str]:
    keys = [
        key
        for key, project_areas in _PROJECT_GEO_AREAS.items()
        if areas.intersection(project_areas)
    ]
    return sorted(keys, key=lambda key: _PROJECT_ORDER.get(key, 9999))


def _project_geo_result(text: str) -> Optional[Dict[str, Any]]:
    if not _looks_like_project_geo_query(text):
        return None

    target = _find_geo_target(text)
    if not target:
        return None

    direct_keys = _project_keys_for_areas(target["areas"])
    if direct_keys:
        return {
            "direct": True,
            "label": target["label"],
            "kind": target["kind"],
            "matched_label": target["label"],
            "project_keys": direct_keys,
            "areas": target["areas"],
        }

    fallback_region = target.get("fallback_region")
    if not fallback_region:
        return {
            "direct": False,
            "label": target["label"],
            "kind": target["kind"],
            "matched_label": target["label"],
            "project_keys": [],
            "areas": target["areas"],
            "fallback_label": None,
        }

    fallback_areas = _areas_for_region(fallback_region)
    fallback_keys = _project_keys_for_areas(fallback_areas)
    return {
        "direct": False,
        "label": target["label"],
        "kind": target["kind"],
        "matched_label": fallback_region,
        "project_keys": fallback_keys,
        "areas": fallback_areas,
        "fallback_label": fallback_region,
    }


def _city_from_location(location: str) -> str:
    return location.split(",")[0].strip()


def _areas_for_project_key(project_key: str) -> Tuple[str, ...]:
    return _PROJECT_GEO_AREAS.get(project_key, ())


def _format_geo_project_list(result: Dict[str, Any]) -> str:
    label = result["label"]
    matched_label = result.get("matched_label") or label
    project_keys = result.get("project_keys", [])

    if result["direct"]:
        intro = f"1PAX projects in **{label}**:"
    elif project_keys:
        intro = (
            f"I don't see a current 1PAX project tagged directly to **{label}** "
            f"in the project database. The closest regional view is **{matched_label}**:"
        )
    else:
        intro = (
            f"I don't see a current 1PAX project tagged to **{label}** in the project database."
        )

    lines = [intro]
    if not project_keys:
        lines.append(
            "\nThe current public portfolio does not list a project in this area yet. "
            "1PAX works internationally and is open to future collaborations, so if "
            "you're exploring an opportunity there, I can help you schedule a meeting "
            "with the team."
        )
        lines.append(
            "\nYou can also browse current project locations such as **Serbia**, "
            "**France**, **Latin America**, **Europe**, **Africa**, or **Asia**."
        )
        return "\n".join(lines)

    covered_areas = []
    for key in project_keys:
        for area in _areas_for_project_key(key):
            if area in result["areas"] and area not in covered_areas:
                covered_areas.append(area)
    if covered_areas:
        lines.append(f"Countries / territories covered: **{', '.join(covered_areas)}**.")

    grouped: Dict[str, List[str]] = {}
    for key in project_keys:
        areas = [area for area in _areas_for_project_key(key) if area in result["areas"]]
        group = areas[0] if areas else "Other"
        grouped.setdefault(group, []).append(key)

    for area in covered_areas or grouped.keys():
        keys = grouped.get(area, [])
        if not keys:
            continue
        city_names = sorted({_city_from_location(PROJECTS[key]["location"]) for key in keys})
        if city_names:
            lines.append(f"\n**{area}** — {', '.join(city_names)}")
        else:
            lines.append(f"\n**{area}**")
        for key in keys:
            project = PROJECTS[key]
            lines.append(
                f"• **{project['display_name']}** — {project['location']} "
                f"({project['category']}, {project['year']})"
            )

    note = _GEO_REGION_NOTES.get(matched_label)
    if note:
        lines.append(f"\n{note}")

    lines.append(
        "\nName any of these projects and I can go deeper into the budget, scope, "
        "timeline, design approach, or key challenge."
    )
    return "\n".join(lines)


def _register_project_alias(
    alias: str,
    project_key: str,
    index: Dict[str, str],
    aliases_by_project: Dict[str, List[str]],
) -> None:
    normalized = _ascii_norm(alias)
    if not normalized:
        return
    index[normalized] = project_key
    aliases_by_project.setdefault(project_key, [])
    if normalized not in aliases_by_project[project_key]:
        aliases_by_project[project_key].append(normalized)


_NORMALIZED_NAME_INDEX: Dict[str, str] = {}
_ALIASES_BY_PROJECT: Dict[str, List[str]] = {}
for _alias, _key in _NAME_INDEX.items():
    _register_project_alias(_alias, _key, _NORMALIZED_NAME_INDEX, _ALIASES_BY_PROJECT)
for _key, _p in PROJECTS.items():
    _register_project_alias(
        _p["display_name"],
        _key,
        _NORMALIZED_NAME_INDEX,
        _ALIASES_BY_PROJECT,
    )

_SORTED_NORMALIZED_ALIASES = sorted(
    _NORMALIZED_NAME_INDEX.items(),
    key=lambda item: (len(item[0].split()), len(item[0])),
    reverse=True,
)
for _key in list(_ALIASES_BY_PROJECT):
    _ALIASES_BY_PROJECT[_key] = sorted(
        _ALIASES_BY_PROJECT[_key],
        key=lambda alias: (len(alias.split()), len(alias)),
        reverse=True,
    )


def _has_meaningful_token_overlap(candidate: str, input_words: List[str]) -> bool:
    """Require at least one real project/city token before accepting fuzzy aliases."""
    candidate_words = [w for w in candidate.split() if len(w) >= 3 and w not in _SKIP_WORDS]
    meaningful_input = [w for w in input_words if len(w) >= 3 and w not in _SKIP_WORDS]
    if not candidate_words or not meaningful_input:
        return False

    for candidate_word in candidate_words:
        for input_word in meaningful_input:
            if candidate_word == input_word:
                return True
            if SequenceMatcher(None, candidate_word, input_word).ratio() >= 0.82:
                return True
    return False


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
    lower = re.sub(r"[?!.,;:\"']", " ", text.lower())  # strip punctuation before split
    normed = _ascii_norm(lower)
    normed_words = normed.split()

    # 0. Exact normalized phrase lookup across full project titles and aliases.
    # Do this before city matching, otherwise ambiguous places like Belgrade,
    # Cayenne, or Paris can steal queries that contain a precise project name.
    direct_key = _NORMALIZED_NAME_INDEX.get(normed)
    if direct_key:
        return direct_key
    for phrase, project_key in _SORTED_NORMALIZED_ALIASES:
        if len(phrase) < 3:
            continue
        phrase_words = phrase.split()
        if (
            normed != phrase
            and not any(word not in _SKIP_WORDS and len(word) >= 3 for word in phrase_words)
        ):
            continue
        if _contains_normalized_phrase(normed, phrase):
            return project_key

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
    matches = get_close_matches(normed, _NORMALIZED_NAME_INDEX.keys(), n=1, cutoff=0.80)
    if matches and _has_meaningful_token_overlap(matches[0], normed_words):
        return _NORMALIZED_NAME_INDEX[matches[0]]

    return None


_SPECIFIC_PROJECT_SIGNALS = {
    "biggest project",
    "the biggest project",
    "your biggest project",
    "our biggest project",
    "most famous project",
    "signature project",
    "flagship project",
    "the flagship project",
    "airport project",
    "terminal project",
}

_PROJECT_QUERY_CUES = {
    "about",
    "design",
    "details",
    "info",
    "interested",
    "overview",
    "project",
    "airport",
    "terminal",
    "metro",
    "station",
    "tower",
    "building",
    "portfolio",
}


def _looks_like_specific_project_query(text: str) -> bool:
    """Catch one-project queries when NLU falls back or routes to project list."""
    lower = text.lower()

    # Plural browse/category prompts should stay with the project-list action.
    ascii_text = _ascii_norm(lower).strip()
    words = set(ascii_text.split())
    if "projects" in words:
        return False

    if any(signal in lower for signal in _SPECIFIC_PROJECT_SIGNALS):
        return True

    if _fuzzy_match_project(lower) is None:
        return False

    # Exact aliases like "T3" or "Belgrade Metro" are project references by themselves.
    if ascii_text in _NORMALIZED_NAME_INDEX:
        return True

    return any(cue in words for cue in _PROJECT_QUERY_CUES)


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


def _project_link_label(lang: Optional[str]) -> str:
    if not lang:
        return "View project page on 1pax.com"
    return _PROJECT_LINK_LABELS.get(lang.upper(), "View project page on 1pax.com")


def _format_project_response(
    text: str,
    project: Dict,
    lang: Optional[str],
    offer_meeting: bool = False,
) -> str:
    if offer_meeting:
        text = f"{text}\n\n{meeting_cta_text('project')}"
    response = translate_response(text, lang)
    project_url = project.get("project_url")
    if project_url:
        response = f"{response}\n\n[{_project_link_label(lang)}]({project_url})"
    return response


def _has_photo_word(raw_msg: str) -> bool:
    words = {word.strip(".,?!;:()[]{}\"'").lower() for word in raw_msg.split()}
    return bool(words & _PHOTO_WORDS)


def _should_attach_cover_image(info_type: str, raw_msg: str) -> bool:
    return info_type in {"about_project", "overview", "photo"} or _has_photo_word(raw_msg)


def _user_turn_count(tracker: Tracker) -> int:
    return sum(1 for event in tracker.events if event.get("event") == "user")


def _should_offer_project_meeting(tracker: Tracker, info_type: str) -> bool:
    if tracker.get_slot("schedule_stage"):
        return False
    if info_type not in _PROJECT_MEETING_INFO_TYPES:
        return False
    return _user_turn_count(tracker) % 2 == 0


def _utter_project_response(
    dispatcher: CollectingDispatcher,
    text: str,
    project: Dict,
    lang: Optional[str],
    info_type: str,
    raw_msg: str,
    offer_meeting: bool = False,
) -> None:
    cover_image_url = project.get("cover_image_url")
    message = {
        "text": _format_project_response(text, project, lang, offer_meeting),
    }
    if cover_image_url and _should_attach_cover_image(info_type, raw_msg):
        message["image"] = cover_image_url
    if offer_meeting:
        message["buttons"] = meeting_buttons(lang)
    dispatcher.utter_message(**message)


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
    "project", "hub", "port", "base", "facility", "metro", "rail", "railway",
    "railways", "stations", "terminals", "exactly",
}


def _resolve_project(tracker: Tracker) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Returns (project_key, project_dict).
    Priority:
      1. Any extracted entity that is a canonical PROJECTS key
      2. Fuzzy/exact match on full message text
      3. Fuzzy match on any extracted entity value
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

    # 2. Try fuzzy/exact lookup on the full message before broad entity values.
    # DIET can extract "Nikola Tesla Airport" from a longer title like
    # "Nikola Tesla Airport – Wayfinding Signage Design"; the full title must
    # take precedence over that broad airport reference.
    fuzzy_key = _fuzzy_match_project(raw_text)
    if fuzzy_key:
        return fuzzy_key, PROJECTS.get(fuzzy_key)

    # 3. Fuzzy match on each meaningful entity value
    for ev in meaningful:
        fuzzy_key = _fuzzy_match_project(ev)
        if fuzzy_key:
            return fuzzy_key, PROJECTS.get(fuzzy_key)

    # 4. Meaningful entity was present but didn't match — signal not found.
    # Do NOT fall through to slot (it would return the wrong project).
    if meaningful:
        return None, None

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


def _infer_project_info_type(text: str) -> str:
    raw = _ascii_norm(text or "")
    words = set(raw.split())

    def has_phrase(*phrases: str) -> bool:
        padded = f" {raw} "
        return any(f" {_ascii_norm(phrase)} " in padded for phrase in phrases)

    if any(token in raw for token in ("tender", "competition", "selected")):
        return "tender"
    if any(token in raw for token in (
        "scope",
        "role",
        "commission",
        "responsible for",
        "what did 1pax do",
        "what did you do",
        "what did 1pax design",
        "what did you design",
        "what was 1pax's work",
        "what was your work",
    )):
        return "scope"
    if any(token in raw for token in (
        "sustainability",
        "sustainable",
        "environmental",
        "eco-friendly",
        "eco friendly",
        "green",
        "low carbon",
        "carbon footprint",
        "energy efficiency",
        "climate-conscious",
        "climate conscious",
    )):
        return "sustainability"
    if any(token in raw for token in ("approach", "strategy", "method", "process")):
        return "approach"
    if any(token in raw for token in ("concept", "vision", "elevator pitch", "nutshell")):
        return "concept"
    if any(token in raw for token in ("challenge", "obstacle", "difficulty")):
        return "challenge"
    if any(token in raw for token in ("program", "programme", "what was built", "what is in")):
        return "program"
    if any(token in raw for token in ("status", "complete", "completed", "ongoing", "inaugurated", "built")):
        return "status"
    if any(token in raw for token in ("cost", "budget", "price", "investment", "capex", "funding", "contract value")):
        return "cost"
    if any(token in raw for token in ("where", "location", "located")):
        return "location"
    if any(token in raw for token in ("when", "year", "timeline")):
        return "year"
    if "client" in raw:
        return "client"
    if any(token in raw for token in ("area", "size", "big", "large")):
        return "area"
    if any(token in raw for token in ("capacity", "passenger", "traveler", "traveller", "throughput", "mppa", "volume", "gate")):
        return "capacity"
    if (
        words & {"architect", "architects", "designer", "designers"}
        or has_phrase("who designed", "designed by", "design team")
    ):
        return "architect"
    if any(token in raw for token in ("partner", "collaborator", "team")):
        return "partners"
    return "about_project"


def _strip_project_reference(text: str, project_key: Optional[str]) -> str:
    """Remove the resolved project title/aliases before looking for detail cues."""
    normalized = _ascii_norm(text or "")
    if not normalized or not project_key:
        return normalized

    for alias in _ALIASES_BY_PROJECT.get(project_key, []):
        if not alias:
            continue
        normalized = re.sub(
            rf"\b{re.escape(alias)}\b",
            " ",
            normalized,
        )
    return " ".join(normalized.split())


def _is_general_project_intro(text: str) -> bool:
    """True when only generic intro words remain after removing a project title."""
    if not text:
        return True

    generic_words = {
        "a",
        "about",
        "can",
        "could",
        "describe",
        "details",
        "explain",
        "for",
        "give",
        "hello",
        "hey",
        "hi",
        "i",
        "info",
        "information",
        "know",
        "like",
        "me",
        "mi",
        "more",
        "nesto",
        "o",
        "on",
        "please",
        "project",
        "recite",
        "reci",
        "regarding",
        "say",
        "some",
        "something",
        "tell",
        "the",
        "to",
        "us",
        "want",
        "what",
        "would",
        "you",
    }
    remaining = [word for word in text.split() if word not in generic_words]
    return not remaining


def _starts_with_general_project_intro(text: str) -> bool:
    generic_starts = (
        "can you tell me about",
        "could you tell me about",
        "describe",
        "explain",
        "give me information about",
        "i want to know about",
        "please tell me about",
        "reci mi nesto o",
        "recite mi nesto o",
        "tell me about",
        "tell me more about",
        "tell me something about",
        "what can you tell me about",
    )
    return any(text == start or text.startswith(f"{start} ") for start in generic_starts)


def _looks_like_project_detail_followup(text: str, has_project_context: bool = False) -> bool:
    """Detect project-field questions even when NLU falls back."""
    raw = _ascii_norm(text or "")
    if not has_project_context and any(
        marker in raw
        for marker in ("1pax", "company", "studio", "firm", "practice")
    ):
        return False

    info_type = _infer_project_info_type(text)
    if info_type != "about_project":
        return True

    words = {
        word.strip("?!.,;:\"'()[]{}")
        for word in raw.split()
        if word.strip("?!.,;:\"'()[]{}")
    }
    common_followups = {
        "budget",
        "cost",
        "price",
        "capacity",
        "passenger",
        "passengers",
        "area",
        "size",
        "client",
        "owner",
        "architect",
        "partners",
        "challenge",
        "approach",
        "concept",
        "status",
        "sustainability",
        "sustainable",
        "environmental",
        "eco-friendly",
        "green",
        "scope",
        "program",
        "programme",
        "highlights",
        "facts",
        "timeline",
        "year",
    }
    if words & common_followups:
        return True

    return False


def _intent_to_info_type(
    intent_name: str,
    text: str = "",
    project_key: Optional[str] = None,
) -> str:
    text_without_project = _strip_project_reference(text, project_key)
    inferred = _infer_project_info_type(text_without_project)
    if inferred != "about_project":
        return inferred

    if intent_name == "ask_about_project":
        return "about_project"
    prefix = "ask_project_"
    if intent_name.startswith(prefix):
        # DIET often over-weights words inside project titles, e.g.
        # "Architectural Assistance" → ask_project_architect. If the remaining
        # user phrase is just "tell me about", treat it as a general overview.
        if project_key and (
            _is_general_project_intro(text_without_project)
            or _starts_with_general_project_intro(text_without_project)
        ):
            return "about_project"
        return intent_name[len(prefix):]
    return inferred


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

        schedule_events = _continue_schedule_if_active(dispatcher, tracker, domain)
        if schedule_events is not None:
            return schedule_events
        schedule_reset_events = _schedule_topic_shift_events(tracker)

        lang = get_lang(tracker)
        lang_event = [SlotSet("language", lang)] if lang else []
        raw_text = tracker.latest_message.get("text", "")
        intent_name = tracker.latest_message.get("intent", {}).get("name", "")
        raw_msg = raw_text.lower()

        if _looks_like_project_geo_query(raw_text):
            return ActionListProjects().run(dispatcher, tracker, domain)

        entity_value = next(tracker.get_latest_entity_values("project"), None)
        project_key, project = _resolve_project(tracker)

        if not project_key:
            if entity_value:
                dispatcher.utter_message(text=translate_response(
                    random.choice([
                        "I don't have data on that project yet. Try 'list projects' to see all 57 projects in our portfolio.",
                        "Hmm, I can't find that one. Ask 'what projects do you have?' to browse the full catalogue.",
                    ]), lang
                ))
            else:
                if intent_name == "ask_project_sustainability":
                    dispatcher.utter_message(text=translate_response(
                        (
                            "A strong sustainable project example is **Félix Eboué Cayenne Airport – New Terminal**, "
                            "where the programme includes solar panels, natural ventilation, rainwater harvesting, "
                            "and a climate-responsive tropical design strategy.\n\n"
                            "**Bordeaux–Mérignac Airport – Hall B New Façades** is another good example: it focuses "
                            "on adaptive reuse, material performance, energy efficiency, and environmental quality "
                            "through a targeted façade reconstruction.\n\n"
                            "You can name either project if you want the detailed sustainability story."
                        ), lang
                    ))
                else:
                    dispatcher.utter_message(text=translate_response(
                        random.choice([
                            "Which project are you asking about? You can name a city, airport, or project — like **Sofia Airport**, **Belgrade Metro**, or **Lima Food Hall**.",
                            "Sure! Which project did you have in mind? Try saying **Tahiti airport**, **Paris Heliport**, or type 'list projects' for the full catalogue.",
                            "I'd love to help — which project are you interested in? Ask 'what projects do you have?' for the full list of 57 projects.",
                        ]), lang
                    ))
            return schedule_reset_events + lang_event

        if not project:
            dispatcher.utter_message(text=translate_response(random.choice([
                (
                    "I don't have details on that project yet. Try asking about "
                    "**Sofia Airport**, **Belgrade Airport**, or type 'list projects' "
                    "to browse all 57 projects."
                ),
                (
                    "Hmm, I can't find that one. Ask 'what projects do you have?' "
                    "to see the full list — there are 57 to explore!"
                ),
            ]), lang))
            return schedule_reset_events + lang_event

        info_type = _intent_to_info_type(intent_name, raw_msg, project_key)

        # Special case: photo query routed to video intent → acknowledge mismatch
        if info_type == "video":
            if _has_photo_word(raw_msg):
                if project.get("cover_image_url"):
                    text = (
                        f"Here's the cover image for **{project['display_name']}** "
                        "from the 1PAX project page."
                    )
                    if project.get("video_url"):
                        text += f"\n\nThere is also a project video you can watch:\n\n{project['video_url']}"
                    _utter_project_response(dispatcher, text, project, lang, "photo", raw_msg)
                elif project.get("video_url"):
                    _utter_project_response(
                        dispatcher,
                        (
                            f"I don't have a public cover image for **{project['display_name']}**, "
                            f"but there's a video you can check out:\n\n{project['video_url']}"
                        ),
                        project,
                        lang,
                        info_type,
                        raw_msg,
                    )
                else:
                    _utter_project_response(
                        dispatcher,
                        (
                            f"We don't have public media for **{project['display_name']}** yet — "
                            "check [1pax.com](https://1pax.com) for the latest."
                        ),
                        project,
                        lang,
                        info_type,
                        raw_msg,
                    )
                return schedule_reset_events + [SlotSet("project_name", project_key)] + lang_event

        # Special case: "ask_about_project" with no new entity = "what else can you tell me"
        # Show highlights instead of repeating the intro teaser
        if info_type == "about_project":
            entity_value = next(tracker.get_latest_entity_values("project"), None)
            raw_project_key = _fuzzy_match_project(raw_msg)
            if not entity_value and raw_project_key != project_key:
                info_type = "facts"

        formatter = INFO_DISPATCH.get(info_type, _fmt_teaser)
        _utter_project_response(
            dispatcher,
            formatter(project),
            project,
            lang,
            info_type,
            raw_msg,
            offer_meeting=_should_offer_project_meeting(tracker, info_type),
        )
        return schedule_reset_events + [SlotSet("project_name", project_key)] + lang_event


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

        schedule_events = _continue_schedule_if_active(dispatcher, tracker, domain)
        if schedule_events is not None:
            return schedule_events
        schedule_reset_events = _schedule_topic_shift_events(tracker)

        lang = get_lang(tracker)
        lang_event = [SlotSet("language", lang)] if lang else []
        raw_msg = tracker.latest_message.get("text", "")

        if _looks_like_specific_project_query(raw_msg):
            return ActionAnswerProjectQuery().run(dispatcher, tracker, domain)

        geo_result = _project_geo_result(raw_msg)
        if geo_result:
            dispatcher.utter_message(
                text=translate_response(_format_geo_project_list(geo_result), lang)
            )
            return schedule_reset_events + lang_event

        if not PROJECTS:
            dispatcher.utter_message(
                text=translate_response("No projects in the database yet — check back soon!", lang)
            )
            return schedule_reset_events + lang_event

        intro = random.choice([
            "Here are 1PAX's architectural projects:\n",
            "1PAX's portfolio spans 6 categories — here's the full list:\n",
            "These are all 57 1PAX projects across our portfolio:\n",
        ])
        lines = [_localized_project_list_text(lang, "intro", intro)]

        for category, project_keys in CATEGORIES.items():
            lines.append(f"**{_localized_project_category(category, lang)}**")
            for key in project_keys:
                p = PROJECTS[key]
                lines.append(
                    f"  • **{p['display_name']}** — {p['location']} ({p['year']})"
                )
            lines.append("")

        suffix = random.choice([
            "Ask me anything about a project — cost, design challenge, team, and more!",
            "Just name a project and I'll tell you all about it — budget, approach, sustainability, and more.",
            "Pick any project and ask away — I can cover cost, location, design approach, and much more.",
        ])
        lines.append(_localized_project_list_text(lang, "suffix", suffix))
        lines.append("")
        lines.append(_localized_project_list_text(lang, "cta", meeting_cta_text("project")))

        list_text = "\n".join(lines)
        if not _project_list_lang(lang):
            list_text = translate_response(list_text, lang)
        dispatcher.utter_message(
            text=list_text,
            buttons=meeting_buttons(lang),
        )
        return schedule_reset_events + lang_event


def _looks_like_language_capability_question(text: str) -> bool:
    normalized = _ascii_norm(text)
    if not normalized:
        return False
    return any(
        phrase in normalized
        for phrase in (
            "do you speak",
            "can you speak",
            "are you able to speak",
            "can i write in",
            "can i talk to you in",
            "can we speak",
            "what languages do you speak",
            "which languages do you speak",
            "parlez vous",
            "hablas",
            "habla usted",
            "falas",
            "fala voce",
            "govoris",
            "govorite",
            "sprichst du",
            "sprechen sie",
            "parli",
            "parla",
        )
    )


def _language_capability_text() -> str:
    return (
        "Yes. You can write to me in English or in another language, even if it "
        "is not one of the visible language buttons. For the first few messages "
        "I identify the language you are using, translate your question into "
        "English for the 1PAX knowledge model, and translate my reply back to "
        "that language. If you want to switch languages later, just send a "
        "message in the new language."
    )


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

        # If a Calendly flow is already active, let the scheduler handle terse
        # follow-ups like names, emails, numbers, "yes", or "no".
        schedule_events = _continue_schedule_if_active(dispatcher, tracker, domain)
        if schedule_events is not None:
            return schedule_events
        schedule_reset_events = _schedule_topic_shift_events(tracker)

        # ── Greeting safety net: production can occasionally route greetings
        # through nlu_fallback while the model is warming or degraded.
        _GREETING_SIGNALS = {
            "hello", "hi", "hey", "good morning", "good afternoon",
            "good evening", "zdravo", "cao", "ćao", "dobar dan",
        }
        greeting_text = lower_text.strip().strip("!.?,;:")
        if (
            greeting_text in _GREETING_SIGNALS
            or any(greeting_text.startswith(f"{sig} ") for sig in _GREETING_SIGNALS)
        ):
            return schedule_reset_events + ActionGreet().run(dispatcher, tracker, domain)

        # ── Company overview safety net: short translated prompts like
        # "cime se bavite" often arrive as "What do you do?", and production
        # lang detection can still route that through out_of_scope.
        _COMPANY_OVERVIEW_SIGNALS = {
            "what do you do",
            "what are you doing",
            "what work do you do",
            "what kind of work do you do",
            "what does your company do",
            "what does the studio do",
            "what is your thing",
        }
        if any(sig in lower_text for sig in _COMPANY_OVERVIEW_SIGNALS):
            from .company_actions import ActionAnswerCompanyQuery

            return ActionAnswerCompanyQuery().run(dispatcher, tracker, domain)

        if _looks_like_language_capability_question(user_text):
            dispatcher.utter_message(
                text=translate_response(_language_capability_text(), lang),
                buttons=meeting_buttons(lang),
            )
            return schedule_reset_events + [SlotSet("project_name", None)] + lang_event

        # ── Capability question: "what can you do", "what else can you do", etc. ─
        _CAP_SIGNALS = {"what can you do", "what else can you do", "what do you offer",
                        "what are you capable of", "what do you know", "what can you help",
                        "what are your features", "what are your capabilities",
                        "what can you tell me about", "what topics do you cover",
                        "what can you answer", "how can you help"}
        if any(sig in lower_text for sig in _CAP_SIGNALS):
            dispatcher.utter_message(
                text=translate_response(
                    "Here's what I can help you with:\n\n"
                    "**About 1PAX as a studio:**\n"
                    "• Who we are, our mission and history\n"
                    "• Our founder (Mabel Miranda) and team\n"
                    "• Office locations and how we work\n"
                    "• Design approach and principles\n"
                    "• Sustainability, innovation, and urbanism\n"
                    "• Careers, applications, culture, and open roles\n\n"
                    "**Our project portfolio (57 projects):**\n"
                    "• Ask *'show me all projects'* to browse by category\n"
                    "• Ask about any project by name, city, or airport code\n"
                    "• For any project: location, year, client, budget, design concept, "
                    "key challenge, sustainability, team, highlights, and more\n\n"
                    "**Scheduling:**\n"
                    "• Ask me to *schedule a meeting* and I can help find a Calendly time.\n\n"
                    "Try: _'Tell me about 1PAX'_, _'who founded the studio?'_, _'tell me about Sofia Airport'_, "
                    "or _'schedule a meeting'_.",
                    lang,
                ),
                buttons=meeting_buttons(lang),
            )
            return schedule_reset_events + [SlotSet("project_name", None)] + lang_event

        # ── Careers/applicant safety net: "join your team" and CV questions
        # can otherwise drift into team-roster answers when NLU is uncertain.
        from .company_actions import ActionAnswerCompanyQuery, looks_like_career_question

        if looks_like_career_question(user_text):
            return ActionAnswerCompanyQuery().run(dispatcher, tracker, domain)

        # ── Company fact safety net: MTM-0040 queries like "what are your
        # patents?", "main clients", or "phone number" should never fall
        # through to a generic out-of-scope response.
        _COMPANY_FACT_SIGNALS = {
            "patent",
            "patents",
            "patented",
            "client",
            "clients",
            "phone",
            "telephone",
            "your number",
            "office number",
            "1pax's number",
            "1pax number",
            "call 1pax",
            "call your office",
            "email",
            "e-mail",
            "contact",
            "contact form",
            "get in touch",
            "reach you",
            "reach 1pax",
            "say ciao",
            "media inquiries",
            "journalists",
            "clients and partners",
            "customer",
            "customers",
            "who trusts",
            "who hires",
            "who commissions",
            "airport operators",
            "concessionaires",
            "public authorities",
            "transport authorities",
            "government ministries",
            "utility model",
            "protected innovation",
            "protected by 1pax",
            "license its innovations",
            "licensing innovations",
            "commercializing patents",
            "commercialize patents",
            "ecoport",
            "pax cart",
            "pax mobility",
            "passenger assisted",
            "patented cart",
            "airport cart",
            "skylo",
            "aerial logistics",
            "low-altitude economy",
            "low altitude economy",
            "low-altitude mobility",
            "low altitude mobility",
            "drone logistics",
            "drone network",
            "drone networks",
        }
        if any(sig in lower_text for sig in _COMPANY_FACT_SIGNALS):
            return ActionAnswerCompanyQuery().run(dispatcher, tracker, domain)

        # ── Production safety net: route core project browse/detail flows from raw text.
        # Do this before person aliases so "airport projects" means portfolio browsing,
        # while "who leads airport projects" can still resolve to the team member.
        _PROJECT_LIST_SIGNALS = {
            "project",
            "projects",
            "portfolio",
            "show me all",
            "list all",
            "what have you designed",
        }
        person_question = (
            lower_text.strip().startswith("who ")
            or "who leads" in lower_text
            or "who runs" in lower_text
            or "director" in lower_text
        )
        if _looks_like_specific_project_query(lower_text):
            return ActionAnswerProjectQuery().run(dispatcher, tracker, domain)

        if _looks_like_project_geo_query(user_text):
            return ActionListProjects().run(dispatcher, tracker, domain)

        if any(sig in lower_text for sig in _PROJECT_LIST_SIGNALS) and not person_question:
            return ActionListProjects().run(dispatcher, tracker, domain)

        _PERSON_SIGNALS = {"mabel", "miranda", "ceo", "chief executive"}
        _FOUNDER_PERSON_SIGNALS = {"who is founder", "who is the founder", "tell me about founder", "tell me about the founder"}
        from .team_actions import ActionAnswerTeamQuery, has_known_person_reference

        if (
            has_known_person_reference(user_text)
            or any(sig in lower_text for sig in _PERSON_SIGNALS)
            or any(sig in lower_text for sig in _FOUNDER_PERSON_SIGNALS)
        ):
            return ActionAnswerTeamQuery().run(dispatcher, tracker, domain)

        _SCHEDULE_SIGNALS = {
            "schedule",
            "meeting",
            "book a call",
            "book call",
            "appointment",
            "calendly",
        }
        if any(sig in lower_text for sig in _SCHEDULE_SIGNALS):
            from .calendly_actions import run_calendly_scheduling

            return run_calendly_scheduling(dispatcher, tracker, domain)

        _SERVICE_SIGNALS = {
            "service",
            "services",
            "offer",
            "provide",
            "capabilities",
            "bim",
            "urbanism",
            "masterplan",
            "future mobility",
            "vertiport",
            "interior",
            "control tower",
            "hospital",
            "hospitals",
            "healthcare",
        }
        if any(sig in lower_text for sig in _SERVICE_SIGNALS):
            from .services_actions import ActionAnswerServicesQuery

            return ActionAnswerServicesQuery().run(dispatcher, tracker, domain)

        _TEAM_SIGNALS = {
            "team",
            "staff",
            "people",
            "member",
            "members",
            "roster",
            "employee",
            "employees",
            "leadership",
            "architects",
            "specialists",
            "who works",
            "who all works",
            "who is working",
            "who do you employ",
            "who is employed",
            "who works for you",
            "who works with you",
            "who works in your company",
            "who works at your company",
            "who works for your company",
            "people working",
            "people at your company",
            "employees at your company",
            "staff at your company",
        }
        if any(sig in lower_text for sig in _TEAM_SIGNALS):
            from .team_actions import ActionAnswerTeamQuery

            return ActionAnswerTeamQuery().run(dispatcher, tracker, domain)

        _COMPANY_LOCATION_SIGNALS = {
            "where is the company located",
            "where is the company based",
            "where is 1pax located",
            "where is 1pax based",
            "where are you located",
            "where are you based",
            "where are your offices",
            "where is your office",
            "where is your head office",
            "what are your office locations",
        }
        if any(sig in lower_text for sig in _COMPANY_LOCATION_SIGNALS):
            from .company_actions import ActionAnswerCompanyQuery

            return ActionAnswerCompanyQuery().run(dispatcher, tracker, domain)

        # ── Project detail safety net ────────────────────────────────────────
        # Short translated follow-ups such as "what is the passenger capacity"
        # or "what was the budget" can land in nlu_fallback on older models.
        # Route them through the normal project action so active slot context is
        # still respected, or so the user is asked which project if none exists.
        active_project_key, _ = _resolve_project(tracker)
        if _looks_like_project_detail_followup(
            user_text,
            has_project_context=bool(active_project_key),
        ):
            return ActionAnswerProjectQuery().run(dispatcher, tracker, domain)

        _COMPANY_SIGNALS = {
            "1pax",
            "company",
            "studio",
            "firm",
            "founder",
            "mission",
            "offices",
            "clients",
            "sustainability",
            "careers",
        }
        if any(sig in lower_text for sig in _COMPANY_SIGNALS):
            from .company_actions import ActionAnswerCompanyQuery

            return ActionAnswerCompanyQuery().run(dispatcher, tracker, domain)

        # ── Safety net: try to fuzzy-match a project from the raw message ────────
        # This catches cases where NLU misfires on bare project names or typos
        # (e.g. "fuzhou airport", "aik bankk") before giving up.
        # Skip if the message looks like a genuine OOS query (weather, time, etc.)
        _OOS_SIGNALS = {"weather", "temperature", "forecast", "rain", "raining",
                        "sunny", "time", "joke", "taxi", "uber", "order", "pizza",
                        "translate", "news", "stock", "president", "restaurant"}
        _is_genuine_oos = any(w in lower_text for w in _OOS_SIGNALS)
        fuzzy_key = None if _is_genuine_oos else _fuzzy_match_project(user_text)
        if fuzzy_key and fuzzy_key in PROJECTS:
            p = PROJECTS[fuzzy_key]
            _utter_project_response(
                dispatcher,
                _fmt_teaser(p),
                p,
                lang,
                "about_project",
                user_text,
            )
            return schedule_reset_events + [SlotSet("project_name", fuzzy_key)] + lang_event

        # ── Normal out-of-scope / fallback handling ───────────────────────────────
        project_key = tracker.get_slot("project_name")

        if project_key and project_key in PROJECTS:
            p = PROJECTS[project_key]
            msg = random.choice(_OUT_OF_SCOPE_WITH_CONTEXT).format(
                name=p['display_name']
            )
            buttons = None
        else:
            msg = random.choice(_OUT_OF_SCOPE_NO_CONTEXT)
            buttons = meeting_buttons(lang)

        message = {"text": translate_response(msg, lang)}
        if buttons:
            message["buttons"] = buttons
        dispatcher.utter_message(**message)
        return schedule_reset_events + lang_event
