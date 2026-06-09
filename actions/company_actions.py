"""
1PAX Company Info — Rasa Custom Action
=======================================
Handles all company-info intents (ask_company_*) via a single router action.
Stateless — no slot tracking needed (answers are about the studio, not a specific entity).
"""

import random
import re
import unicodedata
from typing import Any, Text, Dict, List, Optional, Set, Tuple

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from .company_data import CLIENT_PROFILES, CLIENT_SEGMENTS, COMPANY_INFO
from .meeting_prompts import meeting_buttons, meeting_cta_text
from .projects_data import PROJECTS
from .translation import get_lang, translate_response, translate_responses


# ── Intent suffix → COMPANY_INFO key ─────────────────────────────────────────

COMPANY_DISPATCH: Dict[str, str] = {
    "overview":       "overview",
    "name":           "name_meaning",
    "mission":        "mission",
    "history":        "history",
    "founder":        "founder",
    "offices":        "offices",
    "team":           "team",
    "expertise":      "expertise",
    "approach":       "approach",
    "human_centered": "human_centered",
    "sustainability": "sustainability",
    "innovation":     "innovation",
    "urbanism":       "urbanism",
    "methodology":    "methodology",
    "clients":        "clients",
    "contact":        "contact",
    "difference":     "difference",
    "why":            "why_1pax",
    "careers":        "careers",
    "application":    "application",
    "hiring_process": "hiring_process",
    "candidate_profile": "candidate_profile",
    "compensation":   "compensation_benefits",
    "visa_relocation": "visa_relocation",
    "culture":        "culture",
    "work_arrangements": "work_arrangements",
    "mentorship":     "mentorship",
    "internships":    "internships",
    "open_roles":     "open_roles",
    "values":         "values",
    # ── Ethics & Sustainability pillars ──────────────────────────────────────
    "ethics":         "ethics",
    "social":         "social_commitment",
    "heritage":       "heritage",
    "people_values":  "people_values",
    "diversity":      "diversity",
    "governance":     "governance",
    "suppliers":      "suppliers",
    "ip":             "ip",
    "plan":           "ethics_plan",
    # ── Innovation products ───────────────────────────────────────────────────
    "patents":        "patents",
    "pax_cart":       "pax_cart",
    "ecoport":        "ecoport",
    "skylo":          "skylo",
}

CAREER_INFO_TYPES = {
    "careers",
    "application",
    "hiring_process",
    "candidate_profile",
    "compensation",
    "visa_relocation",
    "culture",
    "work_arrangements",
    "mentorship",
    "internships",
    "open_roles",
}


def _has_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def looks_like_career_question(text: str) -> bool:
    """Return True when raw text is about applying to or working at 1PAX."""
    return _infer_company_info_type(text) in CAREER_INFO_TYPES


def _client_norm(text: str) -> str:
    """Normalize client aliases without depending on project action helpers."""
    nfd = unicodedata.normalize("NFD", text or "")
    ascii_only = nfd.encode("ascii", "ignore").decode("ascii")
    ascii_only = re.sub(r"[^a-zA-Z0-9]+", " ", ascii_only.lower())
    return " ".join(ascii_only.split())


def _client_slug(text: str) -> str:
    return _client_norm(text).replace(" ", "_")


def _split_client_names(client_text: str) -> List[str]:
    """Split a project client field into likely organization names."""
    if not client_text or client_text.lower().startswith("not available"):
        return []
    parts = re.split(r"\s*/\s*|\s*,\s*|\s*;\s*", client_text)
    return [part.strip() for part in parts if part.strip()]


def _client_alias_index() -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    for key, profile in CLIENT_PROFILES.items():
        aliases = set(profile.get("aliases", ()))
        aliases.add(profile.get("display_name", key))
        aliases.add(key)
        aliases.add(key.replace("_", " "))
        for alias in aliases:
            norm = _client_norm(alias)
            if norm:
                rows.append((norm, key))
    rows.sort(key=lambda row: len(row[0]), reverse=True)
    return rows


_CLIENT_ALIAS_INDEX = _client_alias_index()
_CLIENT_PROJECT_INDEX: Optional[Dict[str, List[Tuple[str, Dict[str, Any]]]]] = None
_DYNAMIC_CLIENT_NAMES: Dict[str, str] = {}


def _source_profile_keys(client_name: str) -> Set[str]:
    norm = _client_norm(client_name)
    if not norm:
        return set()
    padded = f" {norm} "
    keys: Set[str] = set()
    for alias_norm, key in _CLIENT_ALIAS_INDEX:
        if alias_norm == norm or f" {alias_norm} " in padded:
            keys.add(key)
    return keys


def _add_project_to_index(
    index: Dict[str, List[Tuple[str, Dict[str, Any]]]],
    key: str,
    project_key: str,
    project: Dict[str, Any],
) -> None:
    existing = {item[0] for item in index.setdefault(key, [])}
    if project_key not in existing:
        index[key].append((project_key, project))


def _get_client_project_index() -> Dict[str, List[Tuple[str, Dict[str, Any]]]]:
    global _CLIENT_PROJECT_INDEX
    if _CLIENT_PROJECT_INDEX is not None:
        return _CLIENT_PROJECT_INDEX

    index: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {
        key: [] for key in CLIENT_PROFILES
    }
    dynamic_names: Dict[str, str] = {}

    for project_key, project in PROJECTS.items():
        matched_keys: Set[str] = set()
        for client_name in _split_client_names(project.get("client", "")):
            source_keys = _source_profile_keys(client_name)
            matched_keys.update(source_keys)
            if not source_keys:
                slug = _client_slug(client_name)
                if slug:
                    dynamic_names.setdefault(slug, client_name)
                    _add_project_to_index(index, slug, project_key, project)

        for profile_key, profile in CLIENT_PROFILES.items():
            if project_key in profile.get("project_keys", ()):
                matched_keys.add(profile_key)

        for profile_key in matched_keys:
            _add_project_to_index(index, profile_key, project_key, project)

    _DYNAMIC_CLIENT_NAMES.clear()
    _DYNAMIC_CLIENT_NAMES.update(dynamic_names)
    _CLIENT_PROJECT_INDEX = index
    return index


def _client_display_name(client_key: str) -> str:
    if client_key in CLIENT_PROFILES:
        return CLIENT_PROFILES[client_key].get("display_name", client_key.replace("_", " ").title())
    return _DYNAMIC_CLIENT_NAMES.get(client_key, client_key.replace("_", " ").title())


def _resolve_client_value(value: str) -> Optional[str]:
    if not value:
        return None
    if value in CLIENT_PROFILES:
        return value
    _get_client_project_index()
    if value in _DYNAMIC_CLIENT_NAMES:
        return value

    norm = _client_norm(value)
    if not norm:
        return None
    for alias_norm, key in _CLIENT_ALIAS_INDEX:
        if alias_norm == norm:
            return key
    slug = _client_slug(value)
    if slug in _DYNAMIC_CLIENT_NAMES:
        return slug
    return None


def _resolve_client_from_text(raw_text: str) -> Optional[str]:
    norm = _client_norm(raw_text)
    if not norm:
        return None
    padded = f" {norm} "

    for alias_norm, key in _CLIENT_ALIAS_INDEX:
        if len(alias_norm) > 2 and f" {alias_norm} " in padded:
            return key

    _get_client_project_index()
    dynamic_aliases = sorted(
        ((_client_norm(name), key) for key, name in _DYNAMIC_CLIENT_NAMES.items()),
        key=lambda row: len(row[0]),
        reverse=True,
    )
    for alias_norm, key in dynamic_aliases:
        if len(alias_norm) > 3 and f" {alias_norm} " in padded:
            return key
    return None


def _resolve_client(tracker: Tracker, raw_text: str) -> Optional[str]:
    for value in tracker.get_latest_entity_values("client"):
        client_key = _resolve_client_value(value)
        if client_key:
            return client_key
    return _resolve_client_from_text(raw_text)


def _client_locations(projects: List[Tuple[str, Dict[str, Any]]]) -> str:
    locations = sorted({project.get("location", "") for _, project in projects if project.get("location")})
    return ", ".join(locations) if locations else "location details are not available in the project registry"


def _client_categories(projects: List[Tuple[str, Dict[str, Any]]]) -> str:
    categories = sorted({project.get("category", "") for _, project in projects if project.get("category")})
    return ", ".join(categories) if categories else "portfolio work"


def _client_project_lines(projects: List[Tuple[str, Dict[str, Any]]], limit: Optional[int] = None) -> str:
    selected = projects[:limit] if limit else projects
    lines = []
    for _, project in selected:
        scope = project.get("scope") or project.get("tagline") or project.get("overview", "")
        if len(scope) > 170:
            scope = scope[:167].rstrip() + "..."
        lines.append(
            f"• **{project['display_name']}** ({project.get('location', 'Location not available')}, "
            f"{project.get('year', 'year not available')}) — {scope}"
        )
    if limit and len(projects) > limit:
        lines.append(f"• Plus {len(projects) - limit} more linked project(s) in the portfolio.")
    return "\n".join(lines)


def _sentence(text: str) -> str:
    stripped = (text or "").strip()
    if not stripped:
        return ""
    return stripped if stripped.endswith((".", "!", "?")) else f"{stripped}."


def _infer_client_focus(raw_text: str) -> str:
    norm = _client_norm(raw_text)
    if _has_any(norm, (
        "what projects",
        "which projects",
        "projects did",
        "project did",
        "work did",
        "what did 1pax do",
        "what did you do",
        "what was 1pax role",
        "what was your role",
        "portfolio",
        "case studies",
    )):
        return "projects"
    if _has_any(norm, (
        "where",
        "where are",
        "where is",
        "from",
        "based",
        "country",
        "region",
        "geography",
    )):
        return "where"
    if _has_any(norm, (
        "what do they do",
        "what does",
        "who are they",
        "who is",
        "profile",
        "about",
        "what kind",
    )):
        return "profile"
    return "overview"


def _format_specific_client_answer(client_key: str, raw_text: str) -> List[str]:
    project_index = _get_client_project_index()
    projects = project_index.get(client_key, [])
    profile = CLIENT_PROFILES.get(client_key, {})
    display = _client_display_name(client_key)
    focus = _infer_client_focus(raw_text)

    if not profile:
        intro = (
            f"**{display}** appears in 1PAX's portfolio as a client or project stakeholder.\n\n"
            f"**Portfolio context:** {_client_categories(projects)}.\n"
            f"**Project geography:** {_client_locations(projects)}."
        )
        if not projects:
            intro += "\n\nI do not have a linked project entry for this client yet."
            return [intro]
        return [intro, f"**Linked project work:**\n\n{_client_project_lines(projects)}"]

    if focus == "where":
        text = (
            f"**{display} — geography**\n\n"
            f"{profile.get('geography', 'Geographic details are not available.')}\n\n"
            f"**1PAX project locations linked to this client:** {_client_locations(projects)}."
        )
        return [text]

    if focus == "projects":
        if not projects:
            return [
                f"**{display}** is in the client profile base, but I do not have a linked project entry yet."
            ]
        return [
            (
                f"**1PAX work linked to {display}:**\n\n"
                f"{profile.get('relationship', '')}\n\n"
                f"{_client_project_lines(projects)}"
            )
        ]

    text = (
        f"**{display}**\n\n"
        f"**Who they are:** {_sentence(profile.get('kind', 'Client / partner organization'))}\n"
        f"**Where they are from / active:** {_sentence(profile.get('geography', 'Not specified in the current profile.'))}\n"
        f"**What they do:** {_sentence(profile.get('does', 'They appear in the 1PAX project portfolio as a client or partner.'))}\n\n"
        f"**Relationship with 1PAX:** {_sentence(profile.get('relationship', '1PAX has project work linked to this organization.'))}"
    )
    if projects:
        text += (
            f"\n\n**Linked 1PAX project work ({len(projects)}):**\n\n"
            f"{_client_project_lines(projects)}"
        )
    return [text]


def _infer_client_segment(raw_text: str) -> Optional[str]:
    norm = _client_norm(raw_text)
    if not norm:
        return None

    if _has_any(norm, ("qatar", "doha", "gulf", "middle east", "middle eastern")):
        return "qatar" if "qatar" in norm or "doha" in norm else "middle_east"
    if _has_any(norm, ("peru", "peruvian", "lima", "callao", "cusco")):
        return "peru"
    if _has_any(norm, ("latin america", "south america", "panama", "chile", "bolivia")):
        return "latin_america"
    if _has_any(norm, ("serbia", "serbian", "belgrade", "balkans")):
        return "serbia"
    if _has_any(norm, ("france", "french", "paris", "cdg", "le bourget", "cergy")):
        return "france"
    if _has_any(norm, ("africa", "african", "cabo verde", "cape verde", "guinea", "rwanda")):
        return "africa"
    if _has_any(norm, ("asia", "asian", "china", "japan", "india", "maldives", "singapore", "thailand", "kazakhstan", "iran")):
        return "asia"
    if _has_any(norm, ("europe", "european", "eu clients", "europe clients")):
        return "europe"
    if _has_any(norm, ("technology", "tech", "engineering", "engineer", "siemens", "setec", "besix", "tso")):
        return "technology"
    if _has_any(norm, ("future mobility", "evtol", "vertiport", "air mobility", "aam", "skyports", "drone")):
        return "future_mobility"
    if _has_any(norm, ("metro", "rail", "railway", "transport authority", "transit authority", "urban transport")):
        return "transport"
    if _has_any(norm, ("government", "public", "ministry", "municipality", "city authority", "authorities", "authority")):
        return "public"
    if _has_any(norm, ("airport", "aviation", "airline", "terminal")):
        return "airport"
    if _has_any(norm, ("retail", "commercial", "bank", "developer", "interior", "food hall", "private sector")):
        return "commercial"
    if _has_any(norm, ("private", "investor", "concessionaire", "concession", "operator")):
        return "private"
    return None


def _format_client_segment_answer(segment_key: str) -> Optional[List[str]]:
    segment = CLIENT_SEGMENTS.get(segment_key)
    if not segment:
        return None

    project_index = _get_client_project_index()
    client_keys = [key for key in segment.get("client_keys", ()) if key in CLIENT_PROFILES or key in _DYNAMIC_CLIENT_NAMES]
    client_lines = []
    project_examples: List[Tuple[str, Dict[str, Any]]] = []

    for key in client_keys:
        profile = CLIENT_PROFILES.get(key, {})
        client_lines.append(
            f"• **{_client_display_name(key)}** — {profile.get('client_type', profile.get('kind', 'client / partner'))}"
        )
        for project in project_index.get(key, [])[:1]:
            if project[0] not in {item[0] for item in project_examples}:
                project_examples.append(project)

    first_part = (
        f"**{segment['title']}**\n\n"
        f"{segment['summary']}\n\n"
        f"**Representative clients / client contexts:**\n"
        f"{chr(10).join(client_lines)}"
    )
    if project_examples:
        first_part += (
            "\n\n**Representative project examples:**\n"
            f"{_client_project_lines(project_examples, limit=8)}"
        )
    first_part += "\n\nYou can ask about any client by name and I can list who they are, where they operate, and the 1PAX projects linked to them."
    return [first_part]


def _build_client_answer(tracker: Tracker, raw_text: str) -> Optional[List[str]]:
    client_key = _resolve_client(tracker, raw_text)
    if client_key:
        return _format_specific_client_answer(client_key, raw_text)

    segment_key = _infer_client_segment(raw_text)
    if segment_key:
        return _format_client_segment_answer(segment_key)

    return None


def _infer_company_info_type(text: str) -> str:
    """Best-effort router for fallback paths when NLU confidence collapses."""
    normalized = text.lower()
    if any(
        token in normalized
        for token in (
            "what do you do",
            "what are you doing",
            "what work do you do",
            "what kind of work do you do",
            "what does your company do",
            "what does the studio do",
            "what is your thing",
        )
    ):
        return "overview"
    if any(token in normalized for token in ("founder", "founded", "mabel", "ceo")):
        return "founder"
    if _has_any(normalized, (
        "skylo",
        "aerial logistics",
        "low-altitude economy",
        "low altitude economy",
        "low-altitude mobility",
        "low altitude mobility",
        "drone logistics",
        "drone network",
        "drone networks",
        "aerial logistics network",
    )):
        return "skylo"
    if "ecoport" in normalized:
        return "ecoport"
    if _has_any(normalized, (
        "pax cart",
        "pax mobility",
        "pax product",
        "passenger assisted",
        "patented cart",
        "airport cart",
        "seat-cart-stroller",
        "seat cart stroller",
        "all-in-one airport cart",
        "all in one airport cart",
    )):
        return "pax_cart"
    if normalized.strip().strip("?.!,;:") in {"what is pax", "what's pax", "tell me about pax"}:
        return "pax_cart"
    if _has_any(normalized, (
        "hiring process",
        "recruitment process",
        "application process",
        "interview process",
        "selection process",
        "what happens after i apply",
        "after i apply",
        "next steps after applying",
        "how does hiring work",
        "how do you hire",
        "when will i hear back",
        "when do i hear back",
        "application status",
        "status of my application",
        "follow up on my application",
        "follow-up on my application",
        "application deadline",
        "deadline to apply",
        "when is the deadline",
        "recruitment timeline",
    )):
        return "hiring_process"
    if _has_any(normalized, (
        "send my cv",
        "send you my cv",
        "submit my cv",
        "upload my cv",
        "send my resume",
        "send you my resume",
        "submit my resume",
        "send a resume",
        "submit a resume",
        "submit a portfolio",
        "send my portfolio",
        "send you my portfolio",
        "cover letter",
        "apply to work",
        "apply for a job",
        "job application",
        "career application",
        "where can i apply",
        "where should i apply",
        "where do i apply",
        "where do i send",
        "how do i apply",
        "application form",
        "contact page",
        "portfolio format",
        "portfolio file",
        "pdf portfolio",
        "application materials",
        "work samples",
    )):
        return "application"
    if _has_any(normalized, (
        "salary",
        "salaries",
        "pay",
        "paid",
        "compensation",
        "benefit",
        "benefits",
        "package",
        "insurance",
        "paid leave",
        "vacation",
        "bonus",
        "stipend",
        "internship paid",
        "paid internship",
    )):
        return "compensation"
    if _has_any(normalized, (
        "visa sponsorship",
        "visa support",
        "visa needs",
        "work visa",
        "sponsor visas",
        "sponsor a visa",
        "visa sponsor",
        "work permit",
        "sponsorship",
        "relocation",
        "relocate",
        "move to paris",
        "move to belgrade",
        "move to barcelona",
        "move to lima",
        "move to shanghai",
        "work authorization",
        "right to work",
        "hire internationally",
        "international applicants",
        "outside france",
        "outside serbia",
        "outside europe",
    )):
        return "visa_relocation"
    if _has_any(normalized, (
        "internship",
        "intern",
        "graduate position",
        "graduate program",
        "graduate fellowship",
        "fellowship",
        "student",
        "students",
        "recent graduate",
        "recent grad",
        "junior talent",
        "entry level",
        "entry-level",
    )):
        return "internships"
    if _has_any(normalized, (
        "open roles",
        "open positions",
        "job openings",
        "available jobs",
        "available roles",
        "current vacancies",
        "vacancies",
        "what positions",
        "what roles",
        "what jobs",
        "are you hiring architects",
        "are you hiring junior",
        "is 1pax hiring",
        "are you hiring",
        "looking for new people",
    )):
        return "open_roles"
    if _has_any(normalized, (
        "what skills",
        "which skills",
        "what qualities",
        "what kind of person",
        "what profile",
        "candidate profile",
        "candidate qualities",
        "candidate",
        "requirements",
        "experience required",
        "airport experience",
        "do i need to be an architect",
        "need to be an architect",
        "non-architect",
        "non architect",
        "who can apply",
        "what background",
        "which background",
        "what disciplines",
        "which disciplines",
        "fit in at 1pax",
        "language requirement",
        "language requirements",
        "what languages",
        "need english",
        "speak english",
        "do i need french",
        "do i need serbian",
        "software skills",
        "bim skills",
        "revit",
        "rhino",
        "visualization skills",
    )):
        return "candidate_profile"
    if _has_any(normalized, (
        "remote work",
        "hybrid work",
        "flexible work",
        "flexible schedule",
        "flexibility",
        "work-life",
        "work life",
        "working conditions",
        "day to day",
        "day-to-day",
        "work environment",
        "studio environment",
        "life at 1pax",
        "what is it like to work",
        "working at 1pax",
        "working there",
        "which office",
        "office would i work",
        "where would i work",
        "job location",
    )):
        return "work_arrangements"
    if _has_any(normalized, (
        "career",
        "careers",
        "job opportunities",
        "career opportunities",
        "employment",
        "employer",
        "jobs at 1pax",
        "join 1pax",
        "join the team",
        "join your team",
        "work at 1pax",
        "work for 1pax",
        "work with 1pax",
        "work in 1pax",
        "be part of 1pax",
        "get a job at 1pax",
        "taking applications",
        "recruiting",
    )):
        return "careers"
    if _has_any(normalized, (
        "phone",
        "telephone",
        "your number",
        "office number",
        "1pax's number",
        "1pax number",
        "call 1pax",
        "call your office",
        "call you",
        "email",
        "e-mail",
        "contact",
        "get in touch",
        "reach you",
        "reach 1pax",
        "contact details",
        "contact information",
        "contact form",
        "say ciao",
        "media inquiries",
        "journalists",
        "communications email",
        "press email",
    )):
        return "contact"
    if any(
        token in normalized
        for token in (
            "office",
            "offices",
            "location",
            "located",
            "where are you",
            "where is the company",
            "where is 1pax",
            "where is your company",
            "based",
            "headquarter",
        )
    ):
        return "offices"
    if any(token in normalized for token in ("mission", "purpose")):
        return "mission"
    if any(token in normalized for token in ("history", "heritage", "story")):
        return "history"
    if any(token in normalized for token in ("approach", "method", "process", "work")):
        return "approach"
    if any(token in normalized for token in ("sustainability", "sustainable", "green")):
        return "sustainability"
    if any(
        token in normalized
        for token in (
            "patent",
            "patents",
            "patented",
            "utility model",
            "protected innovation",
            "protected by 1pax",
            "license its innovations",
            "licensing innovations",
            "commercialize patents",
            "commercializing patents",
        )
    ):
        return "patents"
    if any(token in normalized for token in ("team", "people", "staff")):
        return "team"
    if any(
        token in normalized
        for token in (
            "client",
            "clients",
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
            "vinci airports",
            "sof connect",
            "groupe adp",
            "lagard",
        )
    ):
        return "clients"
    if any(token in normalized for token in ("1pax", "company", "studio", "firm", "about")):
        return "overview"
    return ""


class ActionAnswerCompanyQuery(Action):
    """Single router for all ask_company_* intents."""

    def name(self) -> Text:
        return "action_answer_company_query"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        from .calendly_actions import (
            continue_active_calendly_scheduling,
            schedule_topic_shift_events,
        )

        schedule_events = continue_active_calendly_scheduling(dispatcher, tracker, domain)
        if schedule_events is not None:
            return schedule_events
        schedule_reset_events = schedule_topic_shift_events(tracker)

        lang = get_lang(tracker)
        lang_event = [SlotSet("language", lang)] if lang else []

        raw_text = tracker.latest_message.get("text", "")
        from .actions import ActionListProjects, _looks_like_project_geo_query

        if _looks_like_project_geo_query(raw_text):
            return ActionListProjects().run(dispatcher, tracker, domain)

        intent = tracker.latest_message.get("intent", {}).get("name", "")

        # Strip prefix: "ask_company_overview" → "overview"
        if intent.startswith("ask_company_"):
            info_type = intent.replace("ask_company_", "")
        else:
            info_type = _infer_company_info_type(raw_text)

        data_key = COMPANY_DISPATCH.get(info_type)

        if not data_key or data_key not in COMPANY_INFO:
            dispatcher.utter_message(
                text=translate_response(
                    "I can tell you about **1PAX** — our mission, design approach, team, "
                    "offices, sustainability commitment, careers, and more. What would you "
                    "like to know?",
                    lang,
                ),
                buttons=meeting_buttons(lang),
            )
            return schedule_reset_events + lang_event

        client_answer_parts = None
        if data_key == "clients":
            client_answer_parts = _build_client_answer(tracker, raw_text)

        output_parts = (
            client_answer_parts
            if client_answer_parts is not None
            else list(COMPANY_INFO[data_key])
        )

        # Append a randomised follow-up prompt (not always — empty string weighted in)
        follow_up_pool = COMPANY_INFO.get("follow_up", [])
        if follow_up_pool and not lang and client_answer_parts is None:
            suffix = random.choice(follow_up_pool + ["", ""])   # 2-in-4 chance of no suffix
            if suffix:
                output_parts.append(suffix)

        meeting_cta_index = None
        if data_key in {"overview", "offices", "approach", "clients", "contact"}:
            meeting_cta_index = len(output_parts)
            output_parts.append(meeting_cta_text("company"))

        # Send each message part separately, but translate them in one batch.
        for index, msg in enumerate(translate_responses(output_parts, lang)):
            if index == meeting_cta_index:
                dispatcher.utter_message(text=msg, buttons=meeting_buttons(lang))
            else:
                dispatcher.utter_message(text=msg)

        return schedule_reset_events + lang_event
