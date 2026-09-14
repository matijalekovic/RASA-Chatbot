"""
Portfolio insights — ranking, filtering, grouping, and statistics over PROJECTS.

Answers questions such as "what is your biggest project?", "which projects are
built?", "how many countries have you worked in?", "which competitions did you
win?", or "group your projects by budget". Pure functions only; the Rasa actions
call ``answer_portfolio_query`` and send the returned text + project keys.
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .projects_data import CATEGORIES, PROJECTS

USD_TO_EUR = 0.9  # rough, used only to order mixed-currency budgets

REALIZED_STATUSES = ("built", "under_construction")

STATUS_LABELS = {
    "built": "Built",
    "under_construction": "Under construction",
    "design": "Design delivered / in progress",
    "study": "Study, feasibility or consultancy",
    "competition": "Competition entry",
    "concession": "Concession bid support",
}

PROCUREMENT_LABELS = {
    "competition_won": "Competition won (1st prize / selected)",
    "prize": "Competition prize (2nd or 3rd)",
    "competition_entry": "Competition entry",
    "concession_won": "Winning concession bid support",
    "direct": "Direct commission",
}

# Areas that are not a built footprint designed by 1PAX (coverage, façade,
# reviews of another architect's terminal) or multi-part totals.
_AREA_OVERRIDES: Dict[str, Tuple[Optional[float], str]] = {
    "belgrade_airport": (97000, "47,000 m² new build + 50,000 m² refurbishment"),
    "mashhad_airport": (93000, "60,000 m² international + 33,000 m² domestic"),
    "belgrade_wayfinding": (None, "wayfinding coverage, not built area"),
    "santiago_wayfinding": (None, "wayfinding coverage, not built area"),
    "tocumen_airport": (None, "fire-safety review of another architect's terminal"),
    "aik_bank_design": (None, "branch network (60+ offices, 400 ATMs)"),
    "bordeaux_airport": (1800, "façade surface"),
}

_CAPACITY_EXCLUDE = {"pointe_a_pitre_t2", "tocumen_airport"}

_PRE_FOUNDING_NOTE = (
    "Projects dated before 2016 predate 1PAX's founding; they are credited to ADPI "
    "with founder Mabel Miranda as lead architect."
)

FLAGSHIP_KEYS = [
    ("velana_airport", "new international terminal inaugurated in July 2025 — 102,000 m², 850 million €"),
    ("belgrade_airport", "phased expansion of Serbia's main airport under the VINCI concession — 700 million € programme"),
    ("sofia_airport", "new Terminal 3 + Terminal 2 refurbishment, 110,000 m², targeting a 5-Star airport label"),
    ("pointe_a_pitre_t1", "won through an international competition — 23,600 m² terminal extension"),
    ("cergy_vertiport", "Europe's first fully operational vertiport (2022)"),
    ("belgrade_metro_line1", "architectural identity for Serbia's first metro line"),
]

# ── Normalization / parsing ──────────────────────────────────────────────────


def _norm(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text or "")
    ascii_only = nfd.encode("ascii", "ignore").decode("ascii").lower()
    return " ".join(re.sub(r"[^a-z0-9%]+", " ", ascii_only).split())


def _has(norm_text: str, phrases: Sequence[str]) -> bool:
    padded = f" {norm_text} "
    return any(f" {phrase} " in padded for phrase in phrases)


def _number(raw: str) -> float:
    return float(raw.replace(",", ""))


def parse_area(key: str, project: Dict[str, Any]) -> Optional[float]:
    if key in _AREA_OVERRIDES:
        return _AREA_OVERRIDES[key][0]
    match = re.search(r"(\d[\d,]*(?:\.\d+)?)\s*m²", project.get("area", ""))
    return _number(match.group(1)) if match else None


def parse_cost(project: Dict[str, Any]) -> Optional[Tuple[float, str]]:
    """Return (EUR-equivalent value, currency) or None when undisclosed."""
    text = project.get("cost", "")
    match = re.search(r"(\d[\d,]*(?:\.\d+)?)\s*(million|billion)?\s*(€|EUR|USD)", text)
    if not match:
        return None
    value = _number(match.group(1))
    if match.group(2) == "million":
        value *= 1_000_000
    elif match.group(2) == "billion":
        value *= 1_000_000_000
    currency = "USD" if match.group(3) == "USD" else "EUR"
    return (value * USD_TO_EUR if currency == "USD" else value), currency


def parse_capacity(key: str, project: Dict[str, Any]) -> Optional[float]:
    """Annual passengers for airport/mobility projects (max phase)."""
    if key in _CAPACITY_EXCLUDE:
        return None
    if project.get("category") not in ("Airports and Transportation", "Future of Mobility"):
        return None
    text = project.get("capacity", "")
    if re.match(r"\s*(supporting|serving|various)", text, re.I) or "per hour" in text:
        return None
    values = []
    for number, unit in re.findall(r"(\d[\d,]*(?:\.\d+)?)\s*(million)?\s*passengers", text):
        value = _number(number)
        values.append(value * 1_000_000 if unit else value)
    return max(values) if values else None


def parse_years(project: Dict[str, Any]) -> Tuple[Optional[int], Optional[int]]:
    years = [int(y) for y in re.findall(r"\b(20\d\d)\b", project.get("year", ""))]
    if not years:
        years = [int(y) for y in re.findall(r"\b(20\d\d)\b", project.get("status", ""))]
    if not years:
        return None, None
    return min(years), max(years)


def status_class(project: Dict[str, Any]) -> str:
    status = project.get("status", "").lower()
    if status.startswith("built"):
        return "built"
    if status.startswith("under construction"):
        return "under_construction"
    if status.startswith("competition"):
        return "competition"
    if status.startswith("concession"):
        return "concession"
    if status.startswith("design"):
        return "design"
    return "study"


def procurement_class(project: Dict[str, Any]) -> str:
    tender = project.get("tender_result", "")
    lower = tender.lower()
    if re.search(r"2nd prize|3rd prize|second prize|third prize", lower):
        return "prize"
    if lower.startswith("winner"):
        return "competition_won"
    if lower.startswith("competition entry"):
        return "competition_entry"
    if lower.startswith("concession support"):
        return "concession_won"
    return "direct"


def work_types(project: Dict[str, Any]) -> List[str]:
    blob = _norm(f"{project.get('display_name', '')} {project.get('scope', '')}")
    types = []
    if _has(blob, ("refurbishment", "renovation", "reconstruction", "redesign", "retrofit",
                   "modernization", "reconfiguration", "transformation")):
        types.append("refurbishment")
    if _has(blob, ("extension", "expansion")):
        types.append("extension")
    if _has(blob, ("new", "new build")) and "refurbishment" not in types:
        types.append("new_build")
    return types


def _base_name(display_name: str) -> str:
    return re.split(r"\s+[–-]\s+", display_name, maxsplit=1)[0]


_BASE_NAME_COUNTS: Dict[str, int] = {}
for _project in PROJECTS.values():
    _base = _base_name(_project["display_name"])
    _BASE_NAME_COUNTS[_base] = _BASE_NAME_COUNTS.get(_base, 0) + 1


_PLACE_WORDS = ("airport", "airports", "terminal", "vertiport", "heliport", "station", "metro",
                "embassy", "delegation", "building", "bank", "tower", "depot", "hangar")


def short_name(project: Dict[str, Any]) -> str:
    """Short display name; keeps the full title when the short form is ambiguous or vague."""
    base = _base_name(project["display_name"])
    if _BASE_NAME_COUNTS.get(base, 0) > 1 or not _has(_norm(base), _PLACE_WORDS):
        return project["display_name"]
    return base


def project_facts() -> Dict[str, Dict[str, Any]]:
    facts = {}
    for key, project in PROJECTS.items():
        cost = parse_cost(project)
        start, end = parse_years(project)
        facts[key] = {
            "area": parse_area(key, project),
            "cost_eur": cost[0] if cost else None,
            "currency": cost[1] if cost else None,
            "capacity": parse_capacity(key, project),
            "start": start,
            "end": end,
            "duration": (end - start) if start and end and end > start else None,
            "status": status_class(project),
            "procurement": procurement_class(project),
            "work_types": work_types(project),
        }
    return facts


FACTS = project_facts()

# ── Query parsing ────────────────────────────────────────────────────────────

_METRIC_WORDS = {
    "cost": ("expensive", "budget", "budgets", "cost", "costs", "costliest", "priciest", "cheapest",
             "investment", "capex", "value", "money", "euro", "euros", "price", "pricey"),
    "capacity": ("busiest", "passengers", "passenger", "capacity", "traffic", "pax", "mppa"),
    "duration": ("longest running", "took the longest", "longest project", "longest projects",
                 "shortest project", "duration"),
    "year": ("newest", "latest", "most recent", "recent", "oldest", "earliest", "first project",
             "first projects", "your first", "1pax s first", "chronological", "by year", "timeline",
             "new projects", "current projects", "old projects"),
    "area": ("area", "square meters", "square metres", "m2", "sqm", "footprint", "surface",
             "gfa", "floor area", "size", "built area"),
}

_MAX_WORDS = ("biggest", "largest", "most", "highest", "busiest", "newest", "latest", "recent",
              "top", "greatest", "priciest", "costliest", "expensive", "maximum", "longest",
              "major", "huge", "massive", "big")
_MIN_WORDS = ("smallest", "least", "lowest", "cheapest", "oldest", "earliest", "first", "tiniest",
              "minimum", "shortest", "small", "smaller", "cheaper", "modest")

_SUPERLATIVE_WORDS = (
    "biggest", "largest", "smallest", "tiniest", "most expensive", "least expensive", "cheapest",
    "priciest", "costliest", "busiest", "newest", "latest", "most recent", "oldest", "earliest",
    "highest budget", "lowest budget", "highest", "lowest", "longest", "shortest",
    "first project", "your first", "1pax s first", "top 3", "top 5", "top 10", "top three",
    "top five", "top ten", "largest ones", "smallest ones", "biggest ones",
    "most passengers", "most traffic", "the most", "largest capacity", "highest capacity",
    "biggest airport", "largest airport", "biggest airports", "largest airports",
)

_BROWSE_CUES = ("projects", "which", "what", "list", "show me", "any", "ones", "all your",
                "how many", "examples", "portfolio")

_PORTFOLIO_NOUNS = (
    "project", "projects", "portfolio", "work", "works", "job", "jobs", "commission",
    "commissions", "building", "buildings", "airport", "airports", "terminal", "terminals",
    "design", "designs", "you did", "you ve done", "you have done", "you ever", "have you done",
    "did you", "you designed", "you built", "you worked on", "1pax did", "1pax has done", "ever done",
    "one", "ones", "contract", "contracts", "tower", "towers", "station", "stations",
    "vertiport", "vertiports", "interior", "interiors",
)

_FLAGSHIP_WORDS = ("most important", "most notable", "most famous", "most iconic", "most prestigious",
                   "most significant", "best project", "best projects", "signature project",
                   "signature projects", "flagship", "landmark project", "landmark projects",
                   "key projects", "proudest", "highlight projects", "notable projects",
                   "most impressive", "star projects", "best work", "showcase projects",
                   "most proud", "iconic projects", "famous projects", "important projects")

_AWARD_WORDS = ("award", "awards", "prize", "prizes", "competition wins", "competitions won",
                "won competitions", "competitions did you win", "competitions have you won",
                "win any competition", "won any competition", "won a competition", "award winning",
                "awarded projects", "recognition", "honours", "honors", "winning designs",
                "1st prize", "first prize", "second prize")

_STATUS_FILTERS = {
    "under_construction": ("under construction", "being built", "ongoing", "in progress",
                           "current projects", "currently working", "working on now",
                           "active projects", "on site now", "in construction", "live projects",
                           "right now", "at the moment", "currently"),
    "built": ("built projects", "completed projects", "delivered projects", "finished projects",
              "realized projects", "realised projects", "projects built", "projects completed",
              "projects delivered", "have been built", "been built", "actually built",
              "already built", "operational projects", "you have built", "you ve built",
              "you built", "have you completed", "you completed", "can i visit", "can visit",
              "exist today", "open today", "in operation", "finished", "completed", "delivered",
              "built", "realized", "realised", "operational"),
    "competition": ("competition entries", "competitions", "competition", "tenders", "tender entries",
                    "bids", "competition projects"),
    "study": ("studies", "feasibility", "consultancy", "consulting projects", "consultations",
              "diagnostics", "advisory projects", "study projects", "reviews"),
    "concession": ("concession", "concessions", "concession bids", "bid support"),
    "design": ("unbuilt", "not built", "on paper", "design only", "paper projects"),
}

_WORK_TYPE_FILTERS = {
    "refurbishment": ("refurbishment", "refurbishments", "renovation", "renovations", "retrofit",
                      "renovating", "renovate", "refurbishing", "refurbish", "retrofitting",
                      "upgrading", "modernizing", "modernising", "transforming existing",
                      "brownfield", "existing buildings", "live airport", "live terminals",
                      "operational airport", "modernization", "modernisation", "upgrade", "upgrades"),
    "extension": ("extension", "extensions", "expansion", "expansions", "enlargement", "expanding",
                  "extending"),
    "new_build": ("new build", "new builds", "greenfield", "from scratch", "new terminals",
                  "brand new"),
}

_CATEGORY_FILTERS = {
    "Airports and Transportation": ("airport", "airports", "terminal", "terminals", "aviation"),
    "Future of Mobility": ("vertiport", "vertiports", "heliport", "evtol", "metro", "rail",
                           "future mobility", "mobility projects"),
    "Industrial Buildings": ("control tower", "control towers", "fire station", "fire stations",
                             "hangar", "hangars", "industrial"),
    "Working and Living": ("office", "offices", "embassy", "embassies", "headquarters", "hq",
                           "working and living"),
    "Interior Design": ("interior", "interiors", "retail", "food hall", "food court", "wayfinding",
                        "signage"),
}

_GROUPING_WORDS = ("group", "grouped", "grouping", "categorize", "categorise", "classify",
                   "sort", "sorted", "rank", "ranked", "ranking", "rankings", "order by",
                   "ordered by", "breakdown", "break down", "split by", "organized by",
                   "organised by", "by size", "by budget", "by year", "by status", "by cost",
                   "by capacity", "by scale", "by type", "by procurement", "size bands",
                   "budget bands", "compare your projects", "comparison of projects")

_STATS_WORDS = ("how many projects", "how many countries", "how many airports", "how many terminals",
                "number of projects", "number of countries", "how many buildings",
                "how many have you built", "how many built", "how many competitions",
                "how many are built", "how many were built", "how many completed",
                "portfolio in numbers", "portfolio statistics", "portfolio stats", "key figures",
                "key numbers", "track record in numbers", "how many vertiports",
                "how many control towers", "how many interior", "how many of your projects",
                "what countries have you worked", "which countries have you worked",
                "countries have you worked in", "countries have you designed",
                "in how many countries", "how many territories")

_NUMBER_WORDS = {"three": 3, "five": 5, "ten": 10, "two": 2, "four": 4}


def _category_filter(norm_text: str) -> Optional[str]:
    for category, aliases in _CATEGORY_FILTERS.items():
        if _has(norm_text, aliases):
            return category
    return None


def _metric(norm_text: str) -> Optional[str]:
    for metric in ("cost", "capacity", "duration", "year"):
        if _has(norm_text, _METRIC_WORDS[metric]):
            return metric
    if _has(norm_text, _METRIC_WORDS["area"]):
        return "area"
    return None


def _direction(norm_text: str, metric: Optional[str]) -> str:
    if metric == "year" and _has(norm_text, ("oldest", "earliest", "first", "first project")):
        return "min"
    if _has(norm_text, ("most expensive", "highest budget", "biggest budget", "largest budget")):
        return "max"
    if _has(norm_text, _MIN_WORDS):
        return "min"
    return "max"


def _limit(norm_text: str) -> Optional[int]:
    match = re.search(r"\btop (\d{1,2})\b|\b(\d{1,2}) (?:biggest|largest|smallest|most|newest|oldest|cheapest)\b", norm_text)
    if match:
        return max(1, min(10, int(match.group(1) or match.group(2))))
    for word, value in _NUMBER_WORDS.items():
        if _has(norm_text, (f"top {word}", f"{word} biggest", f"{word} largest", f"{word} smallest",
                            f"{word} most", f"{word} newest", f"{word} oldest")):
            return value
    return None


def parse_portfolio_query(text: str) -> Optional[Dict[str, Any]]:
    """Return a structured request or None when the text is not a portfolio query."""
    norm_text = _norm(text)
    if not norm_text:
        return None

    category = _category_filter(norm_text)
    metric = _metric(norm_text)
    base = {
        "category": category,
        "metric": metric,
        "direction": _direction(norm_text, metric),
        "limit": _limit(norm_text),
        "status": None,
        "work_type": None,
        "realized_only": _has(norm_text, ("built", "completed", "delivered", "realized", "realised")),
    }
    has_portfolio_noun = _has(norm_text, _PORTFOLIO_NOUNS)

    if _has(norm_text, _AWARD_WORDS) and not _has(norm_text, ("5 star", "five star", "skytrax")):
        return {**base, "kind": "awards"}

    if _has(norm_text, _FLAGSHIP_WORDS):
        return {**base, "kind": "flagship"}

    if _has(norm_text, _STATS_WORDS):
        return {**base, "kind": "stats"}

    if _has(norm_text, _GROUPING_WORDS) and (has_portfolio_noun or metric):
        group_by = "status"
        if _has(norm_text, ("size", "area", "scale", "m2", "square")):
            group_by = "area"
        elif _has(norm_text, ("budget", "cost", "value", "investment")):
            group_by = "cost"
        elif _has(norm_text, ("year", "date", "chronological", "time")):
            group_by = "year"
        elif _has(norm_text, ("procurement", "how you won", "how they were won", "tender", "commission")):
            group_by = "procurement"
        elif _has(norm_text, ("type", "category", "categories")):
            group_by = "category"
        return {**base, "kind": "group", "group_by": group_by}

    if _has(norm_text, ("chronological", "timeline of your projects", "projects by year")):
        return {**base, "kind": "group", "group_by": "year"}

    superlative = _has(norm_text, _SUPERLATIVE_WORDS)
    if superlative and (has_portfolio_noun or metric in ("cost", "capacity", "duration")):
        return {**base, "kind": "rank", "metric": metric or "size"}

    for work_type, aliases in _WORK_TYPE_FILTERS.items():
        if _has(norm_text, aliases) and has_portfolio_noun:
            return {**base, "kind": "filter", "work_type": work_type}

    browse = _has(norm_text, _BROWSE_CUES)
    for status, aliases in _STATUS_FILTERS.items():
        if _has(norm_text, aliases) and (has_portfolio_noun or status == "competition") and browse:
            if status == "competition" and _has(norm_text, ("won", "win", "winning")):
                return {**base, "kind": "awards"}
            return {**base, "kind": "filter", "status": status}

    return None


def parse_followup(text: str, previous: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Short follow-ups like "and the smallest?" or "what about by budget?"."""
    if not previous or previous.get("kind") not in ("rank", "group"):
        return None
    norm_text = _norm(text)
    if len(norm_text.split()) > 8:
        return None
    metric = _metric(norm_text)
    wants_other_direction = _has(norm_text, _MIN_WORDS + _MAX_WORDS)
    if not metric and not wants_other_direction:
        return None
    request = dict(previous)
    if metric:
        request["metric"] = metric
        if previous.get("kind") == "group":
            request["group_by"] = metric if metric in ("area", "cost", "year") else previous.get("group_by")
    if wants_other_direction:
        request["direction"] = _direction(norm_text, request.get("metric"))
    category = _category_filter(norm_text)
    if category:
        request["category"] = category
    return request


def looks_like_portfolio_query(text: str) -> bool:
    return parse_portfolio_query(text) is not None


# ── Formatting ───────────────────────────────────────────────────────────────


def _fmt_area(value: Optional[float]) -> str:
    return f"{int(round(value)):,} m²" if value else "area not disclosed"


def _fmt_money(key: str) -> str:
    return PROJECTS[key].get("cost", "")


def _fmt_capacity(key: str) -> str:
    return PROJECTS[key].get("capacity", "")


def _status_tag(key: str) -> str:
    return PROJECTS[key].get("status", "").split(" — ")[0]


def _line(key: str, detail: str) -> str:
    project = PROJECTS[key]
    return f"• **{short_name(project)}** ({project['location']}) — {detail} · _{_status_tag(key)}_"


def _pool(request: Dict[str, Any], keys: Optional[List[str]] = None) -> List[str]:
    pool = list(keys) if keys is not None else list(PROJECTS)
    if request.get("category"):
        pool = [k for k in pool if PROJECTS[k]["category"] == request["category"]]
    if request.get("status"):
        pool = [k for k in pool if FACTS[k]["status"] == request["status"]]
    if request.get("work_type"):
        pool = [k for k in pool if request["work_type"] in FACTS[k]["work_types"]]
    return pool


def _sorted_by(pool: List[str], field: str, direction: str) -> List[str]:
    if field != "year":
        with_values = [k for k in pool if FACTS[k][field] is not None]
    if field == "year":
        with_values = [k for k in pool if FACTS[k]["start"] is not None]
        if direction == "max":
            return sorted(with_values, key=lambda k: (FACTS[k]["start"], FACTS[k]["end"]), reverse=True)
        return sorted(with_values, key=lambda k: (FACTS[k]["start"], FACTS[k]["end"]))
    return sorted(with_values, key=lambda k: FACTS[k][field], reverse=(direction == "max"))


def _scope_label(request: Dict[str, Any]) -> str:
    bits = []
    if request.get("status"):
        bits.append(STATUS_LABELS[request["status"]].lower())
    if request.get("work_type"):
        bits.append(request["work_type"].replace("_", "-"))
    if request.get("category"):
        bits.append(request["category"])
    return f" ({', '.join(bits)})" if bits else ""


def _rank_section(pool: List[str], field: str, direction: str, limit: int, title: str) -> Tuple[str, List[str]]:
    ranked = _sorted_by(pool, field, direction)[:limit]
    if not ranked:
        return "", []
    detail = {
        "area": lambda k: _fmt_area(FACTS[k]["area"]),
        "cost_eur": _fmt_money,
        "capacity": _fmt_capacity,
        "year": lambda k: PROJECTS[k]["year"],
        "duration": lambda k: f"{PROJECTS[k]['year']} (~{FACTS[k]['duration']} years)",
    }[field]
    lines = [f"**{title}**"] + [_line(k, detail(k)) for k in ranked]
    return "\n".join(lines), ranked


def _answer_rank(request: Dict[str, Any], subject_key: Optional[str]) -> Tuple[str, List[str]]:
    pool = _pool(request)
    direction = request.get("direction", "max")
    word = "Largest" if direction == "max" else "Smallest"
    scope = _scope_label(request)
    metric = request.get("metric") or "size"
    sections: List[str] = []
    keys: List[str] = []

    if metric in ("size", "area"):
        limit = request.get("limit") or 3
        realized = [k for k in pool if FACTS[k]["status"] in REALIZED_STATUSES]
        text, ranked = _rank_section(realized, "area", direction, limit,
                                     f"{word} built or under construction, by area{scope}:")
        if text:
            sections.append(text)
            keys += ranked
        if not request.get("realized_only"):
            text, ranked = _rank_section(pool, "area", direction, limit,
                                         f"{word} designs overall, including competitions and studies:")
            if text and ranked != keys[:len(ranked)]:
                sections.append(text)
                keys += [k for k in ranked if k not in keys]
        if metric == "size":
            text, ranked = _rank_section(pool, "cost_eur", direction, limit,
                                         f"{word} by disclosed budget:")
            if text:
                sections.append(text)
                keys += [k for k in ranked if k not in keys]
    elif metric == "cost":
        word = "Highest" if direction == "max" else "Lowest"
        text, ranked = _rank_section(pool, "cost_eur", direction, request.get("limit") or 5,
                                     f"{word} disclosed budgets{scope}:")
        sections.append(text)
        keys += ranked
        if any(FACTS[k]["currency"] == "USD" for k in ranked):
            sections.append("_USD budgets are converted approximately to euros for ordering only._")
    elif metric == "capacity":
        word = "Highest" if direction == "max" else "Lowest"
        text, ranked = _rank_section(pool, "capacity", direction, request.get("limit") or 5,
                                     f"{word} passenger capacity{scope}:")
        sections.append(text)
        keys += ranked
    elif metric == "duration":
        word = "Longest" if direction == "max" else "Shortest"
        text, ranked = _rank_section(pool, "duration", direction, request.get("limit") or 5,
                                     f"{word}-running projects{scope}:")
        sections.append(text)
        keys += ranked
    else:  # year
        word = "Most recent" if direction == "max" else "Earliest"
        text, ranked = _rank_section(pool, "year", direction, request.get("limit") or 5,
                                     f"{word} projects{scope}:")
        sections.append(text)
        keys += ranked
        if direction == "min" and any((FACTS[k]["start"] or 9999) < 2016 for k in ranked):
            sections.append(_PRE_FOUNDING_NOTE)

    sections = [s for s in sections if s]
    if not sections:
        return ("I don't have enough disclosed figures to rank those projects. "
                "Ask about a specific project and I can share its details."), []

    if subject_key and subject_key in PROJECTS:
        field = {"size": "area", "area": "area", "cost": "cost_eur", "capacity": "capacity",
                 "duration": "duration", "year": "year"}[metric]
        ordered = _sorted_by(pool, field, direction)
        name = short_name(PROJECTS[subject_key])
        if subject_key in ordered:
            sections.insert(0, f"**{name}** ranks **#{ordered.index(subject_key) + 1} of {len(ordered)}** on this measure.")
        else:
            sections.insert(0, f"**{name}** has no disclosed figure for this measure.")

    sections.append("Name any of these projects and I can go deeper into its scope, client, budget, or design approach.")
    return "\n\n".join(sections), keys


def _answer_filter(request: Dict[str, Any]) -> Tuple[str, List[str]]:
    pool = _pool(request)
    if request.get("status"):
        label = STATUS_LABELS[request["status"]]
    elif request.get("work_type"):
        label = {"refurbishment": "Refurbishment, renovation and upgrade work on existing buildings",
                 "extension": "Extensions and expansions",
                 "new_build": "New-build projects"}[request["work_type"]]
    else:
        label = "Matching projects"
    if request.get("category"):
        label += f" — {request['category']}"
    if not pool:
        return f"I don't see any projects in the current portfolio matching **{label.lower()}**.", []
    pool = sorted(pool, key=lambda k: (FACTS[k]["start"] or 0), reverse=True)
    lines = [f"**{label}: {len(pool)} project{'s' if len(pool) != 1 else ''}**", ""]
    lines += [_line(k, PROJECTS[k]["year"]) for k in pool[:15]]
    if len(pool) > 15:
        lines.append(f"• …plus {len(pool) - 15} more.")
    if request.get("status") == "built":
        others = sum(1 for k in _pool({**request, "status": None}) if FACTS[k]["status"] in ("design", "study"))
        lines.append(f"\nBeyond built work, 1PAX has also delivered **{others} design packages, studies, "
                     "and consultancy missions** in the same scope.")
    lines.append("\nName a project to go deeper.")
    return "\n".join(lines), pool


def _answer_awards() -> Tuple[str, List[str]]:
    won = [k for k in PROJECTS if FACTS[k]["procurement"] == "competition_won"]
    prizes = [k for k in PROJECTS if FACTS[k]["procurement"] == "prize"]
    lines = ["**Competition results in the 1PAX portfolio:**", "", "**Won / 1st prize:**"]
    lines += [_line(k, PROJECTS[k]["tender_result"]) for k in won]
    lines += ["", "**Podium prizes:**"]
    lines += [_line(k, PROJECTS[k]["tender_result"].replace("Winner of international competition — ", ""))
              for k in prizes]
    lines += ["", "Other recognitions highlighted in project data: **Europe's first fully operational "
              "vertiport** (Cergy-Pontoise, 2022) and the **HQE-certified** Annecy terminal. I don't have a "
              "separate register of industry awards; for press or award material contact "
              "**communications@1pax.com**.", "", _PRE_FOUNDING_NOTE]
    return "\n".join(lines), won + prizes


def _answer_flagship() -> Tuple[str, List[str]]:
    lines = ["**Highlight projects that show 1PAX's range:**", ""]
    lines += [f"• **{short_name(PROJECTS[k])}** ({PROJECTS[k]['location']}) — {why}" for k, why in FLAGSHIP_KEYS]
    lines += ["", "Ask for the biggest, the newest, the built ones, or any project by name."]
    return "\n".join(lines), [k for k, _ in FLAGSHIP_KEYS]


def _portfolio_countries() -> List[str]:
    try:
        from .actions import _PROJECT_GEO_AREAS
    except Exception:  # pragma: no cover - only when imported standalone
        return []
    return sorted({area for areas in _PROJECT_GEO_AREAS.values() for area in areas})


def portfolio_stats() -> Dict[str, Any]:
    from collections import Counter

    return {
        "total": len(PROJECTS),
        "categories": {cat: len(keys) for cat, keys in CATEGORIES.items()},
        "status": Counter(FACTS[k]["status"] for k in PROJECTS),
        "procurement": Counter(FACTS[k]["procurement"] for k in PROJECTS),
        "countries": _portfolio_countries(),
    }


def _answer_stats() -> Tuple[str, List[str]]:
    stats = portfolio_stats()
    status = stats["status"]
    proc = stats["procurement"]
    countries = stats["countries"]
    lines = [
        f"**1PAX portfolio in numbers — {stats['total']} projects**",
        "",
        "**By type:**",
    ]
    lines += [f"• {cat}: {count}" for cat, count in stats["categories"].items()]
    lines += ["", "**By status:**"]
    lines += [f"• {STATUS_LABELS[s]}: {status.get(s, 0)}" for s in STATUS_LABELS if status.get(s)]
    lines += ["", "**How the work was won:**"]
    lines += [f"• {PROCUREMENT_LABELS[p]}: {proc.get(p, 0)}" for p in PROCUREMENT_LABELS if proc.get(p)]
    if countries:
        lines += ["", f"**Geography:** {len(countries)} countries and territories — {', '.join(countries)}."]
    lines += ["", "The studio was founded in 2016 and works from five offices: Paris, Belgrade, Shanghai, "
              "Barcelona, and Lima.", "",
              "You can also ask for the biggest or smallest projects, the built ones, competition wins, "
              "or projects grouped by budget, size, or year."]
    return "\n".join(lines), []


def _band(value: Optional[float], bands: List[Tuple[float, str]], missing: str) -> str:
    if value is None:
        return missing
    for upper, label in bands:
        if value < upper:
            return label
    return bands[-1][1]


def _answer_group(request: Dict[str, Any]) -> Tuple[str, List[str]]:
    pool = _pool(request)
    group_by = request.get("group_by", "status")
    groups: Dict[str, List[str]] = {}
    if group_by == "area":
        bands = [(5000, "Small (under 5,000 m²)"), (50000, "Medium (5,000–50,000 m²)"),
                 (float("inf"), "Large (over 50,000 m²)")]
        order = [b[1] for b in bands] + ["Area not disclosed / not applicable"]
        for k in pool:
            groups.setdefault(_band(FACTS[k]["area"], bands, order[-1]), []).append(k)
        title = "Projects grouped by size"
    elif group_by == "cost":
        bands = [(10_000_000, "Under 10 million €"), (100_000_000, "10–100 million €"),
                 (float("inf"), "Over 100 million €")]
        order = [b[1] for b in bands] + ["Budget not disclosed"]
        for k in pool:
            groups.setdefault(_band(FACTS[k]["cost_eur"], bands, order[-1]), []).append(k)
        title = "Projects grouped by disclosed budget"
    elif group_by == "year":
        for k in pool:
            start = FACTS[k]["start"]
            groups.setdefault(str(start) if start else "Year not disclosed", []).append(k)
        order = sorted((g for g in groups if g.isdigit()), reverse=True) + ["Year not disclosed"]
        title = "Projects by start year"
    elif group_by == "procurement":
        for k in pool:
            groups.setdefault(PROCUREMENT_LABELS[FACTS[k]["procurement"]], []).append(k)
        order = list(PROCUREMENT_LABELS.values())
        title = "Projects grouped by how they were won"
    elif group_by == "category":
        for k in pool:
            groups.setdefault(PROJECTS[k]["category"], []).append(k)
        order = list(CATEGORIES)
        title = "Projects grouped by type"
    else:
        for k in pool:
            groups.setdefault(STATUS_LABELS[FACTS[k]["status"]], []).append(k)
        order = list(STATUS_LABELS.values())
        title = "Projects grouped by status"

    lines = [f"**{title}{_scope_label(request)}:**"]
    for label in order:
        keys = groups.get(label)
        if not keys:
            continue
        names = ", ".join(short_name(PROJECTS[k]) for k in keys[:8])
        more = f", +{len(keys) - 8} more" if len(keys) > 8 else ""
        lines.append(f"\n**{label} ({len(keys)})** — {names}{more}")
    lines.append("\nAsk me to open any group, or name a project for details.")
    return "\n".join(lines), []


def answer_portfolio_query(
    text: str,
    previous_texts: Sequence[str] = (),
    subject_key: Optional[str] = None,
    default_overview: bool = False,
) -> Optional[Tuple[str, List[str], Dict[str, Any]]]:
    """Return (markdown text, project keys, request) or None."""
    request = parse_portfolio_query(text)
    if request is None:
        for previous in previous_texts:
            request = parse_followup(text, parse_portfolio_query(previous))
            if request:
                break
    if request is None:
        if not default_overview:
            return None
        request = {"kind": "stats"}

    kind = request["kind"]
    if kind == "rank":
        body, keys = _answer_rank(request, subject_key)
    elif kind == "filter":
        body, keys = _answer_filter(request)
    elif kind == "awards":
        body, keys = _answer_awards()
    elif kind == "flagship":
        body, keys = _answer_flagship()
    elif kind == "group":
        body, keys = _answer_group(request)
    else:
        body, keys = _answer_stats()
    return body, keys, request


# ── Scale summary used by the company "project size" answer ──────────────────


def scale_summary() -> Dict[str, Any]:
    built = [k for k in PROJECTS if FACTS[k]["status"] in REALIZED_STATUSES]
    return {
        "smallest_area": _sorted_by(built, "area", "min")[:3],
        "largest_area": _sorted_by(built, "area", "max")[:3],
        "smallest_cost": _sorted_by(list(PROJECTS), "cost_eur", "min")[:3],
        "largest_cost": _sorted_by(list(PROJECTS), "cost_eur", "max")[:3],
        "largest_design": _sorted_by(list(PROJECTS), "area", "max")[:2],
    }
