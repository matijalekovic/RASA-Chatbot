"""
Client / contractor due-diligence answers about 1PAX as a company.

Covers questions a prospective client, contractor, or partner asks while
investigating the studio: languages, offices vs. local presence, engineering
scope, partner ecosystem, building types beyond airports, project size limits,
how to engage, project stages, certifications, track record, and the Graduate
Fellowship. Answers are built from PROJECTS / TEAM data where possible so they
stay consistent with the portfolio.
"""

from datetime import datetime
from typing import Dict, List, Optional, Sequence, Tuple

from .fellowship_data import answer_fellowship, looks_like_fellowship_question
from .portfolio_insights import (
    FACTS,
    _has,
    _norm,
    answer_portfolio_query,
    portfolio_stats,
    scale_summary,
    short_name,
)
from .projects_data import CATEGORIES, PROJECTS

INQUIRY_TYPES = (
    "fellowship",
    "languages",
    "local_presence",
    "engineering",
    "partners",
    "beyond_airports",
    "project_size",
    "engagement",
    "project_stages",
    "certifications",
    "track_record",
    "awards",
)

OFFICE_COUNTRIES = {"France", "Serbia", "China", "Spain", "Peru"}

# ── Partner ecosystem (derived from project architect / partners fields) ─────

PARTNER_GROUPS: Dict[str, Dict[str, Tuple[str, ...]]] = {
    "engineering": {
        "SETEC": ("setec",),
        "EGIS": ("egis",),
        "Ingerop": ("ingerop",),
        "SYSTRA": ("systra",),
        "Arup": ("arup",),
        "Surbana Jurong": ("surbana jurong",),
        "Arcadis": ("arcadis",),
        "KAIRN Ingénierie": ("kairn",),
        "Atelier des Fluides": ("atelier des fluides",),
    },
    "architects": {
        "IPA EOOD (Sofia)": ("ipa eood",),
        "Energoprojekt (Belgrade)": ("energoprojekt",),
        "ENIA and BM (Guadeloupe)": ("enia",),
        "ECADI and AVIC (China)": ("ecadi", "avic"),
        "Calvo Tran Van": ("calvo tran van",),
        "Colorado Architecture": ("colorado architecture",),
        "Ferrier and West 8": ("ferrier", "west8"),
    },
    "contractors": {
        "SBG-CHEC": ("sbg chec",),
        "Coveris": ("coveris",),
        "BRIAND (design-and-build)": ("briand",),
    },
    "operators": {
        "VINCI Airports": ("vinci airports",),
        "Groupe ADP": ("groupe adp",),
        "Skyports": ("skyports",),
        "Eiffage Concession": ("eiffage",),
        "Lagardère Travel Retail": ("lagardere",),
    },
    "specialists": {
        "Saguez & Partners and NRV": ("saguez",),
        "TG Concept": ("tg concept",),
        "Altavia Travel Retail": ("altavia",),
        "Copilot": ("copilot",),
    },
    "reviews": {
        "Foster + Partners": ("foster partners",),
    },
}

_PARTNER_GROUP_TITLES = {
    "engineering": "Engineering firms",
    "architects": "Co-architects and local design partners",
    "contractors": "Contractors",
    "operators": "Airport operators, concessionaires and developers (bid and design partners)",
    "specialists": "Design, retail and specialist consultants",
    "reviews": "Architects whose terminals 1PAX reviewed or supported",
}


def _project_blob(project: Dict) -> str:
    fields = ("architect", "partners", "client", "tender_result", "scope")
    return _norm(" ".join(str(project.get(f, "")) for f in fields))


def partner_projects(aliases: Sequence[str]) -> List[str]:
    return [key for key, project in PROJECTS.items() if _has(_project_blob(project), aliases)]


def _partner_line(name: str, aliases: Sequence[str], limit: int = 3) -> Optional[str]:
    keys = partner_projects(aliases)
    if not keys:
        return None
    names = ", ".join(short_name(PROJECTS[k]) for k in keys[:limit])
    more = f" +{len(keys) - limit} more" if len(keys) > limit else ""
    return f"• **{name}** — {names}{more}"


def find_partner_in_text(text: str) -> Optional[Tuple[str, str, Tuple[str, ...]]]:
    norm_text = _norm(text)
    for group, partners in PARTNER_GROUPS.items():
        for name, aliases in partners.items():
            if _has(norm_text, aliases):
                return group, name, aliases
    return None


# ── Detection ────────────────────────────────────────────────────────────────

_ENGINEERING_CUES = (
    "engineering firm", "engineering company", "engineering companies", "do you do engineering",
    "do you provide engineering", "do you offer engineering", "engineering services",
    "structural engineering", "structural design", "mep", "mep design", "civil engineering",
    "are you engineers", "architects or engineers", "architecture or engineering",
    "engineering design", "who does the engineering", "who does engineering", "engineering side",
    "engineer of record", "stamp", "in house engineers", "in house engineering", "only architecture",
    "just architecture", "architecture only", "only architects", "do you have engineers",
)
_PARTNER_CUES = (
    "your partners", "1pax partners", "partner firms", "partner companies", "who do you partner",
    "who do you work with", "do you partner", "partnered with", "partner with engineering",
    "collaborate with other", "work with other architects", "work with other firms",
    "local architect", "local architects", "local partner", "local partners", "architect of record",
    "design and build", "work with contractors", "contractors do you work", "consortium", "consortia",
    "subconsultant", "sub consultant", "engineering partners", "your engineering partners",
    "network of partners", "partner network", "who are your collaborators", "your collaborators",
    "joint bid", "team up", "teaming", "work with a contractor", "general contractor",
)
_LANGUAGE_CUES = (
    "languages", "language does your team", "language do you work", "working language",
    "speak french", "speak spanish", "speak chinese", "speak mandarin", "speak serbian",
    "speak english", "speak portuguese", "speak german", "speak arabic", "multilingual",
    "what language", "which language", "communicate in",
)
_APPLICANT_LANGUAGE_CUES = ("do i need", "requirement", "requirements", "required", "must i",
                            "to work at", "to apply", "should i speak")
_LOCAL_PRESENCE_CUES = (
    "local office", "office in my country", "office in our country", "office in your country",
    "office near us", "without an office", "without a local office", "don t have an office",
    "dont have an office", "no office in", "need an office", "having an office", "have an office affect",
    "affect the way", "affect how you work", "affect working with", "matter that you don t have",
    "work remotely with", "time zone", "time zones", "work in countries where", "site visits",
    "visit our site", "come to our site", "be on site", "local presence", "presence in my country",
    "presence in our country", "how do you work with international clients", "far away",
    "different country", "another country", "remote collaboration", "work from abroad",
)
_PROJECT_SIZE_CUES = (
    "only large", "only big", "only do large", "only do big", "small projects", "smaller projects",
    "small project", "smaller project", "minimum project size", "minimum size", "minimum budget",
    "minimum fee", "too small", "project size requirement", "size requirement", "size requirements",
    "requirements for project size", "requirements for the size", "do you take small", "small jobs",
    "small commissions", "scale of projects", "what size projects", "what size of projects",
    "how small", "large projects only", "big projects only", "only work on big", "only work on large",
    "minimum scale", "size limit", "project size", "size of projects you take", "large scale only",
    "experience with large projects", "handle large projects", "handle big projects",
    "would you take", "would you accept", "you would take on", "would you consider", "modest budget",
    "mega projects", "only interested in big",
)
_BEYOND_AIRPORT_CUES = (
    "apart from airports", "besides airports", "other than airports", "beyond airports",
    "except airports", "not just airports", "only airports", "only do airports", "only design airports",
    "only terminals", "apart from terminals", "besides terminals", "what else do you do",
    "what else do you design", "what else have you designed", "other types of projects",
    "other building types", "other types of buildings", "non airport", "non aviation",
    "outside aviation", "other sectors", "apart from architecture", "besides architecture",
    "other than architecture", "what else apart", "anything other than airports", "besides aviation",
)
_BUILDING_TYPE_VERBS = ("do you design", "have you designed", "experience with", "experience in",
                        "do you do", "can you design", "have you done", "do you work on",
                        "worked on", "ever designed", "can 1pax design", "does 1pax design")
_ENGAGEMENT_CUES = (
    "hire you", "hire 1pax", "engage you", "engage 1pax", "appoint you", "appoint 1pax",
    "start a project with", "starting a project with", "begin a project with", "work together",
    "request a proposal", "get a proposal", "get a quote", "ask for a quote", "request a quote",
    "how do we start", "how do i start", "next steps to work", "what do you need from us",
    "what information do you need", "what should we send", "prepare before", "how long does it take to design",
    "design timeline", "how quickly can you start", "how soon can you start", "when can you start",
    "do we need a tender", "run a tender", "direct appointment", "directly appoint", "directly hire",
    "work with you", "working with you", "work with 1pax", "working with 1pax", "become your client",
    "commission you", "commission 1pax", "how does the process work", "onboarding",
)
_STAGES_CUES = (
    "what stages", "which stages", "project stages", "design stages", "riba", "phases do you cover",
    "which phases", "what phases", "from concept", "concept to construction", "tender documents",
    "tender documentation", "construction documents", "during construction", "stay involved",
    "full service", "end to end", "scope of services", "what part of the project", "which part of the project",
    "feasibility to", "do you do feasibility", "do you do concept design", "detailed design",
    "design development", "schematic design", "construction drawings", "work in phases",
)
_CERTIFICATION_CUES = (
    "certifications", "certified", "iso 9001", "iso 19650", "iso", "accreditation", "accredited",
    "insurance", "insured", "professional indemnity", "licensed", "registered architects",
    "un global compact", "quality management", "company certification",
)
_TRACK_RECORD_CUES = (
    "track record", "how experienced", "years of experience", "how long have you been",
    "how long has 1pax been", "since when", "how established", "how many employees",
    "how many people work", "company size", "how big is your company", "how big is 1pax",
    "how large is your firm", "how big is your firm", "how big is the studio", "size of your company",
    "how old is 1pax", "how old is the company", "reliable", "credentials", "references",
    "proven experience", "credibility",
)


def infer_inquiry_type(text: str) -> str:
    """Conservative raw-text detector for fallback paths."""
    norm_text = _norm(text)
    if not norm_text:
        return ""
    if looks_like_fellowship_question(text):
        return "fellowship"
    if _has(norm_text, _PARTNER_CUES) or (
        find_partner_in_text(text)
        and _has(norm_text, ("worked with", "work with", "partner", "collaborate", "know"))
    ):
        return "partners"
    if _has(norm_text, _ENGINEERING_CUES):
        return "engineering"
    if _has(norm_text, _LANGUAGE_CUES) and not _has(norm_text, _APPLICANT_LANGUAGE_CUES):
        return "languages"
    if _has(norm_text, _LOCAL_PRESENCE_CUES):
        return "local_presence"
    if _has(norm_text, _PROJECT_SIZE_CUES):
        return "project_size"
    if _has(norm_text, _BEYOND_AIRPORT_CUES) or (
        _building_type(norm_text) and _has(norm_text, _BUILDING_TYPE_VERBS)
    ):
        return "beyond_airports"
    if _has(norm_text, _STAGES_CUES):
        return "project_stages"
    if _has(norm_text, _CERTIFICATION_CUES) and not _has(norm_text, ("5 star", "five star", "breeam", "hqe", "leed")):
        return "certifications"
    if _has(norm_text, _ENGAGEMENT_CUES):
        return "engagement"
    if _has(norm_text, _TRACK_RECORD_CUES):
        return "track_record"
    return ""


# ── Building types ───────────────────────────────────────────────────────────

_PORTFOLIO_TYPES: List[Tuple[str, Tuple[str, ...], Tuple[str, ...]]] = [
    ("Air traffic control towers", ("control tower", "control towers", "atc tower", "atct"),
     ("riga_control_tower", "chateauroux_atct_mro")),
    ("Airport fire stations", ("fire station", "fire stations"),
     ("belgrade_fire_station", "le_bourget_fire_station")),
    ("Hangars and industrial buildings", ("hangar", "hangars", "industrial", "baggage building",
                                          "logistics building"),
     ("air_guyane_hangar", "cdg_baggage_building")),
    ("Metro stations and rail depots", ("metro", "subway", "rail", "railway", "train station",
                                        "depot", "transit station"),
     ("belgrade_metro_line1", "lima_metro_line1_stations", "pachacamac_metro_station", "doha_metro_depot")),
    ("Vertiports and heliports", ("vertiport", "vertiports", "heliport", "heliports", "evtol", "drone port"),
     ("cergy_vertiport", "singapore_vertiport", "paris_heliport")),
    ("Offices and headquarters", ("office building", "office buildings", "offices", "headquarters", "hq",
                                  "workplace", "corporate"),
     ("belgrade_admin_building", "qatar_railways_hq", "cayenne_airport_offices")),
    ("Embassies and diplomatic buildings", ("embassy", "embassies", "diplomatic", "consulate", "delegation"),
     ("tokyo_eu_delegation", "french_embassy_bangkok")),
    ("Retail, food halls and commercial areas", ("retail", "shops", "food hall", "food court", "restaurant",
                                                 "restaurants", "commercial areas", "duty free"),
     ("jorge_chavez_food_hall", "lima_peru_plaza_food_court", "lyon_retail_shell", "nantes_commercial_zone",
      "montijo_airport_commercial", "marseille_commercial_assistance")),
    ("Wayfinding and signage systems", ("wayfinding", "signage"),
     ("belgrade_wayfinding", "santiago_wayfinding")),
    ("Bank branch networks", ("bank", "banks", "bank branch", "branches", "atm"),
     ("aik_bank_design",)),
    ("Masterplans", ("masterplan", "master plan", "masterplanning", "urban planning"),
     ("cayenne_airport_masterplan", "cabo_verde_airports", "lanzhou_airport", "almaty_airport")),
]

_SERVICE_ONLY_TYPES: List[Tuple[str, Tuple[str, ...]]] = [
    ("residential and mixed-use buildings", ("housing", "residential", "apartments", "apartment", "homes",
                                             "mixed use", "mixed-use")),
    ("hotels and resorts", ("hotel", "hotels", "resort", "resorts", "hospitality")),
    ("shopping centres", ("shopping centre", "shopping center", "shopping mall", "mall", "malls")),
    ("public spaces and urban regeneration", ("public space", "public spaces", "plaza", "park", "parks",
                                              "urban regeneration")),
]

_NOT_IN_PORTFOLIO_TYPES: List[Tuple[str, Tuple[str, ...]]] = [
    ("hospitals and healthcare buildings", ("hospital", "hospitals", "clinic", "clinics", "healthcare")),
    ("schools and universities", ("school", "schools", "university", "universities", "campus", "education")),
    ("stadiums and sports venues", ("stadium", "stadiums", "arena", "arenas", "sports")),
    ("museums and cultural buildings", ("museum", "museums", "theatre", "theater", "cultural center",
                                        "cultural centre", "library")),
    ("factories, warehouses and data centres", ("factory", "factories", "warehouse", "warehouses",
                                                "data center", "data centre", "data centers")),
    ("ports and cruise terminals", ("port", "seaport", "cruise terminal", "ferry terminal", "marina")),
    ("private houses and villas", ("house", "villa", "villas", "private home", "single family")),
    ("bridges and civil structures", ("bridge", "bridges", "tunnel", "tunnels", "dam")),
]


def _building_type(norm_text: str) -> Optional[Tuple[str, str, Tuple[str, ...]]]:
    for label, aliases, keys in _PORTFOLIO_TYPES:
        if _has(norm_text, aliases):
            return "portfolio", label, keys
    for label, aliases in _SERVICE_ONLY_TYPES:
        if _has(norm_text, aliases):
            return "service_only", label, ()
    for label, aliases in _NOT_IN_PORTFOLIO_TYPES:
        if _has(norm_text, aliases):
            return "not_in_portfolio", label, ()
    return None


# ── Answer builders ──────────────────────────────────────────────────────────


def _languages(text: str) -> List[str]:
    return [
        ("**Our team collectively speaks 13 languages.**\n\n"
         "With offices in **Paris, Belgrade, Shanghai, Barcelona, and Lima**, the studio works every day "
         "across French-, Serbian-, Chinese- and Spanish-speaking contexts, and **English** is the shared "
         "working language of our international team. That lets us hold workshops, review documents, and "
         "coordinate with local authorities and partners in the client's language on many projects."),
        ("If you need a specific language for meetings or deliverables, mention it when you contact "
         "**contact@1pax.com** or schedule a meeting, and the studio will route you to the right office "
         "or team members.\n\n"
         "And for this chat: you can write to me in your own language — I'll reply in it."),
    ]


def _local_presence(text: str) -> List[str]:
    stats = portfolio_stats()
    countries = stats["countries"]
    abroad = [c for c in countries if c not in OFFICE_COUNTRIES]
    parts = [
        ("**Not having a 1PAX office in your country doesn't change how we work with you.**\n\n"
         f"Our portfolio spans **{len(countries)} countries and territories**, and most of that work — "
         f"including {', '.join(abroad[:8])} — was delivered **without a local 1PAX office**.\n\n"
         "**How we make distance a non-issue:**\n"
         "• **Five offices across time zones** (Paris, Belgrade, Shanghai, Barcelona, Lima) give near "
         "24/7 working hours and fast responses\n"
         "• **BIM-based, cloud-coordinated delivery** — the new Velana terminal in the Maldives was "
         "developed entirely in BIM\n"
         "• **Local partners** where local registration, codes, or site presence matter — e.g. IPA EOOD "
         "in Sofia or Energoprojekt in Belgrade\n"
         "• **Team members who speak 13 languages** between them\n"
         "• On-site presence (workshops, site visits, authority meetings) is planned with you according "
         "to the project stage"),
    ]
    try:
        from .company_actions import _OFFICE_PROFILES, _find_office_target

        target = _find_office_target(text)
    except Exception:  # pragma: no cover - defensive
        target = None
    if target:
        office_key, place = target
        office = _OFFICE_PROFILES[office_key]
        parts.append(
            f"For **{place}**, the closest office is **{office['city']}, {office['country']}**, which "
            f"supports {office['role']}."
        )
    parts.append("Want to discuss a project in your region? I can help you schedule a meeting with the team.")
    return parts


def _engineering(text: str) -> List[str]:
    lines = [
        _partner_line(name, aliases)
        for name, aliases in PARTNER_GROUPS["engineering"].items()
    ]
    lines = [line for line in lines if line]
    return [
        ("**1PAX is an architecture and design practice — we don't sell engineering design services.**\n\n"
         "We lead the **architecture, interiors, planning and passenger-experience design**, and we work "
         "hand in hand with **specialist engineering firms** for structural, MEP, civil, and systems "
         "engineering. Our team includes people with engineering backgrounds who coordinate those "
         "disciplines, so the client gets one integrated design.\n\n"
         "**What 1PAX handles:** architectural design and envelope, functional programming, passenger-flow "
         "and capacity studies, airport/landside masterplanning, interior and wayfinding design, fire-safety "
         "strategy review, and **BIM coordination and clash detection across all disciplines**."),
        ("**Engineering firms we have worked alongside:**\n\n" + "\n".join(lines)),
        ("**Typical set-ups:** 1PAX with an engineering partner in one design team, 1PAX inside a "
         "multidisciplinary consortium (e.g. the Châteauroux control tower, led by Calvo Tran Van with "
         "SETEC for engineering), or a design-and-build team with a contractor (e.g. BRIAND at Paris-CDG). "
         "If you already have engineers appointed, we coordinate with them.\n\n"
         "Tell us about your project and we can propose the right team configuration."),
    ]


def _partners(text: str) -> List[str]:
    found = find_partner_in_text(text)
    if found:
        group, name, aliases = found
        keys = partner_projects(aliases)
        project_lines = "\n".join(
            f"• **{short_name(PROJECTS[k])}** ({PROJECTS[k]['location']}, {PROJECTS[k]['year']})"
            for k in keys
        )
        return [
            f"**Yes — 1PAX has worked with {name}** ({_PARTNER_GROUP_TITLES[group].lower()}) on "
            f"{len(keys)} project{'s' if len(keys) != 1 else ''}:\n\n{project_lines}",
            "Name one of these projects to see the scope and 1PAX's role.",
        ]

    norm_text = _norm(text)
    if _has(norm_text, ("contractor", "contractors", "design and build", "general contractor", "builder")):
        return [
            ("**Working with contractors:** 1PAX regularly designs within contractor-led and design-and-build "
             "set-ups — for example with **BRIAND** on the Paris-CDG baggage building competition, alongside "
             "**SBG-CHEC** on the Velana terminal in the Maldives, and **Coveris** on the Bordeaux-Mérignac "
             "façade.\n\n"
             "We also prepare **contractor-ready BIM deliverables**, construction phasing studies for live "
             "airports, and tender documentation (e.g. Marseille Provence catering facilities).\n\n"
             "If you are a contractor preparing a bid and need an architecture partner, share the tender "
             "details at **contact@1pax.com** or schedule a meeting."),
        ]
    if _has(norm_text, ("local architect", "local architects", "architect of record", "local partner",
                        "local partners", "licensed locally", "local firm")):
        return [
            ("**Local partners:** where local registration, permitting, or code expertise is needed, 1PAX "
             "teams up with local architects and engineers — for example **IPA EOOD** on Sofia Airport, "
             "**Energoprojekt** on Belgrade Airport, **ENIA** and **BM** on Pointe-à-Pitre, and **ECADI** "
             "and **AVIC** on the Chinese airport competitions. 1PAX leads the design vision while the local "
             "partner can act as architect of record."),
        ]

    sections = ["**1PAX works with a wide partner network across every project type:**"]
    for group, partners in PARTNER_GROUPS.items():
        lines = [line for line in (_partner_line(n, a, limit=2) for n, a in partners.items()) if line]
        if lines:
            sections.append(f"**{_PARTNER_GROUP_TITLES[group]}:**\n" + "\n".join(lines))
    sections.append(
        "**Ways we collaborate:** joint design teams with engineering firms, co-design with local "
        "architects, consortium and design-and-build bids with contractors, concession bid support for "
        "airport operators, and independent reviews of other architects' designs.\n\n"
        "Interested in partnering? Share the opportunity at **contact@1pax.com** or schedule a meeting."
    )
    return ["\n\n".join(sections[:4]), "\n\n".join(sections[4:])]


def _beyond_airports(text: str) -> List[str]:
    norm_text = _norm(text)
    building = _building_type(norm_text)
    if building and not _has(norm_text, _BEYOND_AIRPORT_CUES):
        kind, label, keys = building
        if kind == "portfolio":
            project_lines = "\n".join(
                f"• **{short_name(PROJECTS[k])}** ({PROJECTS[k]['location']}) — {PROJECTS[k]['status']}"
                for k in keys
            )
            return [f"**Yes — {label.lower()} are part of the 1PAX portfolio:**\n\n{project_lines}",
                    "Name one to hear about the design and 1PAX's role."]
        if kind == "service_only":
            return [
                (f"**{label.capitalize()}** are part of 1PAX's **Working & Living** service line — alongside "
                 "offices, embassies, shopping centres, resorts, and airport-city developments. The current "
                 "public portfolio doesn't yet include a completed project of this exact type, so share "
                 "your brief at **contact@1pax.com** and the team will tell you how they would approach it."),
            ]
        return [
            (f"**{label.capitalize()}** are not part of 1PAX's current portfolio. The studio's core "
             "expertise is complex, high-footfall public buildings where user experience matters most — "
             "airports, transport hubs, control towers, offices, embassies, and commercial interiors.\n\n"
             "If your project shares those challenges, describe it at **contact@1pax.com** or schedule a "
             "meeting and the team will tell you honestly whether it's a fit."),
        ]

    counts = {cat: len(keys) for cat, keys in CATEGORIES.items()}
    lines = []
    for label, _, keys in _PORTFOLIO_TYPES:
        names = ", ".join(short_name(PROJECTS[k]) for k in keys[:3])
        lines.append(f"• **{label}** — {names}")
    return [
        ("**Airports are our core, but far from all we do.** Of our "
         f"{sum(counts.values())} projects, {counts.get('Airports and Transportation', 0)} are airports and "
         f"terminals; the rest span:\n\n" + "\n".join(lines)),
        ("**Beyond buildings:**\n"
         "• **Innovation & patents** — the PAX all-in-one passenger cart, the Ecoport modular vertiport, "
         "and Skylo aerial-logistics research\n"
         "• **BIM project management** — Revit modelling, digital twins, clash detection\n"
         "• **Consultancy** — feasibility studies, operational diagnostics, value engineering and "
         "fire-safety reviews\n"
         "• **Working & Living design** — mixed-use, hotels, resorts, and airport-city developments\n\n"
         "Ask about any of these, or name a building type to check our experience."),
    ]


def _fmt_keys(keys: Sequence[str], field: str) -> str:
    out = []
    for key in keys:
        project = PROJECTS[key]
        value = project.get(field, "")
        if field == "area" and FACTS[key]["area"]:
            value = f"{int(FACTS[key]['area']):,} m²"
        out.append(f"{short_name(project)} ({value})")
    return ", ".join(out)


def _project_size(text: str) -> List[str]:
    scale = scale_summary()
    return [
        ("**No — 1PAX has no minimum project size.** We are known for large, complex infrastructure, but "
         "we take on projects of every scale when the challenge and the user experience matter.\n\n"
         f"• **Smallest built work:** {_fmt_keys(scale['smallest_area'], 'area')}\n"
         f"• **Smallest budgets:** {_fmt_keys(scale['smallest_cost'], 'cost')}\n"
         f"• **Largest built / in construction:** {_fmt_keys(scale['largest_area'], 'area')}\n"
         f"• **Largest budgets:** {_fmt_keys(scale['largest_cost'], 'cost')}\n"
         f"• **Largest designs (competitions):** {_fmt_keys(scale['largest_design'], 'area')}"),
        ("**Scope can be just as focused:** a 900 m² departure-lounge extension, a historic façade "
         "replacement, a retail 'ready-made shop' concept, a wayfinding system, a value-engineering review, "
         "or a feasibility study — up to entire terminals and airport masterplans.\n\n"
         "What matters more than size is fit: mobility, public, and high-footfall buildings where design "
         "quality and passenger experience make the difference. Share your brief and the team will scope it."),
    ]


def _engagement(text: str) -> List[str]:
    norm_text = _norm(text)
    stats = portfolio_stats()
    proc = stats["procurement"]
    if _has(norm_text, ("tender", "direct appointment", "directly appoint", "directly hire", "competition")):
        return [
            ("**Both routes work.** Of our 57 projects, **{direct} were direct commissions**, "
             "**{comp} came through design competitions** (including {won} wins and {prize} podium prizes), "
             "and **{conc} were winning concession bids** prepared with airport operators.\n\n"
             "We can be appointed directly, respond to your tender or competition, or join a consortium or "
             "design-and-build team.").format(
                direct=proc.get("direct", 0),
                comp=proc.get("competition_won", 0) + proc.get("prize", 0) + proc.get("competition_entry", 0),
                won=proc.get("competition_won", 0),
                prize=proc.get("prize", 0),
                conc=proc.get("concession_won", 0),
            ),
        ]
    if _has(norm_text, ("how long", "timeline", "how quickly", "how soon", "when can you start", "how fast")):
        return [
            ("**Timelines depend on scope and stage.** From the portfolio: the Cergy-Pontoise vertiport was "
             "designed and delivered in 2022; the Pointe-à-Pitre T2 lounge extension ran 2023–2025; Nice "
             "airport's gate expansion ran 2017–2020; the new Velana terminal ran 2016–2025.\n\n"
             "Studies and competition entries are typically delivered within months. Share your programme "
             "and target dates and the team will confirm availability and a realistic schedule."),
        ]
    return [
        ("**How to start a project with 1PAX:**\n\n"
         "1. **Share the context** — email **contact@1pax.com**, use the 1pax.com contact form, or schedule "
         "a meeting right here\n"
         "2. **Intro conversation** with the team about your goals, site, constraints, and timing\n"
         "3. **Tailored proposal** covering scope, deliverables, team, schedule, and fees\n"
         "4. **Kick-off** with a dedicated project lead and team"),
        ("**Helpful to prepare:** project type and location, current stage (idea, feasibility, design, "
         "construction), size or capacity targets, budget range, procurement route, timeline, and any "
         "existing brief or drawings. Fees depend on scope, stage, and location, so they're set in the "
         "proposal. For confidential material, ask for an NDA first."),
    ]


def _project_stages(text: str) -> List[str]:
    return [
        ("**1PAX works across the whole design life-cycle — from strategy to construction support:**\n\n"
         "• **Strategy & feasibility** — capacity and feasibility studies, operational diagnostics "
         "(Jaipur, Ahmedabad, Cusco)\n"
         "• **Masterplanning** — airport and landside masterplans (Cayenne, Cabo Verde, Belgrade landside)\n"
         "• **Bids & competitions** — concession bid support and design competitions (VINCI bids in Cabo "
         "Verde and Annecy; Fuzhou, Singapore)\n"
         "• **Concept & design development** — architecture, interiors, and passenger experience\n"
         "• **Technical design & tender documentation** — BIM models, coordination, and tender packages "
         "(Velana fully in BIM; Marseille tender documentation)\n"
         "• **Construction phase** — design follow-up on projects in construction, construction phasing for "
         "live airports, and design reviews (Sofia, Belgrade, Pointe-à-Pitre)\n"
         "• **Independent reviews** — value engineering (Kigali) and fire-safety compliance reviews (Tocumen)"),
        ("In RIBA terms, that covers **Stages 0–4** as core services, with construction-stage support "
         "depending on the contract. Standalone resident site supervision isn't a published standard service, "
         "so confirm that scope with **contact@1pax.com**.\n\n"
         "You can hire 1PAX for a single stage or the full journey."),
    ]


def _certifications(text: str) -> List[str]:
    return [
        ("**Standards, certifications and commitments:**\n\n"
         "• **ISO 19650** — our BIM Manager is ISO 19650-accredited, and BIM delivery follows the standard\n"
         "• **Sustainability certification** — the Annecy terminal achieved **HQE** certification; the Paris "
         "heliport targets **HQE and BREEAM**; our goal is **BREEAM certification for 100% of projects by 2028**\n"
         "• **UN Global Compact** — 1PAX aligns with its 10 principles and has applied to join\n"
         "• **Registered patents** — 4 registered patents in aviation design (PAX cart, Ecoport)\n"
         "• **Ethics & governance** — an Ethics and Sustainability Committee, anti-corruption protocols, and "
         "a Supplier Code of Conduct"),
        ("For company documents such as **professional indemnity insurance**, registrations, or quality "
         "certificates required for a tender, contact **contact@1pax.com** — the team will provide what your "
         "procurement process needs."),
    ]


def _track_record(text: str) -> List[str]:
    stats = portfolio_stats()
    status = stats["status"]
    years = datetime.now().year - 2016
    try:
        from .team_data import PERSONS

        team = sum(1 for p in PERSONS.values() if p.get("group") != "Collaborators")
        collaborators = len(PERSONS) - team
        team_line = (f"• **{team} team members** on the website roster, plus {collaborators} close collaborators\n")
    except Exception:  # pragma: no cover
        team_line = ""
    return [
        ("**1PAX at a glance:**\n\n"
         f"• **Founded in 2016** by Mabel Miranda — about {years} years of practice\n"
         f"• **{stats['total']} projects** in **{len(stats['countries'])} countries and territories**\n"
         f"• **{status.get('built', 0)} built** and **{status.get('under_construction', 0)} under construction**, "
         "including the 102,000 m² Velana terminal (850 million €) and Sofia's 110,000 m² Terminal 3 programme\n"
         "• **Competition wins and prizes** in Guadeloupe, France, Peru, China, Singapore, and Latvia\n"
         f"{team_line}"
         "• **5 offices** — Paris, Belgrade, Shanghai, Barcelona, Lima — and **13 languages**\n"
         "• **Long-term clients** such as VINCI Airports, Groupe ADP, and SOF Connect"),
        ("Ask me for the biggest projects, the built ones, our competition results, or our clients — or "
         "schedule a meeting to request references."),
    ]


_BUILDERS = {
    "languages": _languages,
    "local_presence": _local_presence,
    "engineering": _engineering,
    "partners": _partners,
    "beyond_airports": _beyond_airports,
    "project_size": _project_size,
    "engagement": _engagement,
    "project_stages": _project_stages,
    "certifications": _certifications,
    "track_record": _track_record,
}


def build_inquiry_answer(info_type: str, text: str) -> Optional[List[str]]:
    if info_type == "fellowship":
        return answer_fellowship(text)
    if info_type == "awards":
        result = answer_portfolio_query("which competitions did you win and what awards")
        return [result[0]] if result else None
    builder = _BUILDERS.get(info_type)
    return builder(text) if builder else None
