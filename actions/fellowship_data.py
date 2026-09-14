"""
1PAX Graduate Fellowship 2026 — structured facts and a small topic router.

Source of truth: the live fellowship portal (1pax-fellowship-portal.vercel.app,
TalentPortal.tsx, fellowship-faq.ts, application-deadline.mjs). Older PDF/DOCX
drafts (August 14 deadline, age 25, LMIC-only eligibility) are superseded.
"""

from datetime import datetime, timezone
from typing import List, Optional

from .portfolio_insights import _has, _norm

APPLY_URL = "https://1pax-fellowship-portal.vercel.app"
CONTACT_EMAIL = "contact@1pax.com"

DEADLINE_UTC = datetime(2026, 9, 30, 21, 59, 59, tzinfo=timezone.utc)
DEADLINE_DISPLAY = "September 30, 2026 at 23:59 (Paris time)"
INTERVIEWS_UNTIL = "October 6, 2026"
RESULTS_DATE = "October 9, 2026"
START_DATE = "October 15, 2026"

JURY = [
    ("Cristiano Ceccato", "Director and Aviation Sector Leader, Zaha Hadid Architects (London)"),
    ("Michel Rojkind", "Founder, Rojkind Arquitectos"),
    ("J. Pablo Serrano Orozco", "Founding Partner, Serrano Monjaraz Arquitectos"),
    ("Marianela B. Castro de la Borda", "CEO, Director & Co-founder, FANCYSTUDIOLIMA"),
    ("Graciela Torre", "Founder & Director, TAW Architecture and TAW Lab"),
    ("Karel Van Oordt", "Senior Project Coordinator, Eurocities"),
    ("Jean-Charles Content", "Head of Architecture, Asia-Pacific, Artelia Airports"),
]


def applications_open(now: Optional[datetime] = None) -> bool:
    return (now or datetime.now(timezone.utc)) <= DEADLINE_UTC


def _deadline_line(now: Optional[datetime] = None) -> str:
    if applications_open(now):
        return (f"Applications are **open until {DEADLINE_DISPLAY}** — apply at "
                f"[{APPLY_URL}]({APPLY_URL}).")
    return (f"Applications for the 2026 cohort **closed on {DEADLINE_DISPLAY}**. Results are announced "
            f"on {RESULTS_DATE} and the fellowship starts on {START_DATE}. Keep an eye on 1pax.com for "
            "the next edition.")


def _overview(now):
    return [
        ("**1PAX Graduate Fellowship 2026** — a **paid, fully remote, six-month** fellowship for emerging "
         "architects who want international experience on real **aviation, transportation, and urban "
         "development** projects.\n\n"
         "• **Two fellows** are selected worldwide\n"
         f"• Starts **{START_DATE}**\n"
         "• Real project work with the 1PAX team **plus an independent research project**\n"
         "• An academic mentor and a professional mentor\n"
         "• A paid visit to one of our offices (flights and accommodation covered)"),
        _deadline_line(now),
        ("Ask me about **eligibility**, **pay**, the **research project**, the **jury**, **application "
         "documents**, or **key dates**."),
    ]


def _eligibility(now):
    return [
        ("**Who can apply to the 1PAX Graduate Fellowship:**\n\n"
         "• Recent **architecture graduates** or **final-year students**, from any university — public or private\n"
         "• **20 to 28 years old** at the start of the fellowship\n"
         "• Strong design potential and a strong portfolio\n"
         "• Professional proficiency in **English**\n"
         f"• Available from **{START_DATE}**\n"
         "• A genuine passion for the future of transportation and cities\n\n"
         "You can apply **from any country** — the fellowship is fully remote."),
        _deadline_line(now),
    ]


def _dates(now):
    return [
        ("**Fellowship timeline (2026 cohort):**\n\n"
         f"• **Application deadline:** {DEADLINE_DISPLAY}\n"
         f"• **Shortlist interviews:** until {INTERVIEWS_UNTIL} (about 10 candidates)\n"
         f"• **Results announced:** {RESULTS_DATE}, by email\n"
         f"• **Fellowship starts:** {START_DATE}, for six months"),
        _deadline_line(now),
    ]


def _pay(now):
    return [
        ("**Yes — the fellowship is paid.** The remuneration corresponds to the salary level of a "
         "young architect in France.\n\n"
         "The programme also includes a **paid visit to one of our offices** — flights and accommodation "
         "are covered."),
    ]


def _format(now):
    return [
        ("**Format:** six months, **fully remote**, working with the 1PAX team across countries and time "
         "zones.\n\n"
         "Fellows also get an **in-person visit of about two weeks to one of our international offices**, "
         "with flights and accommodation paid. Paris is the usual destination; a visit to our **Lima** or "
         "**Belgrade** office can be considered depending on each fellow's circumstances or visa timing."),
    ]


def _research(now):
    return [
        ("**The research project is an integral part of the fellowship.** Each fellow develops an individual "
         "research project alongside professional work:\n\n"
         "1. **Choose** a topic you are passionate about — architecture, aviation, transportation, urban "
         "development, sustainability, or another field connected to 1PAX's work\n"
         "2. **Develop** it with guidance from an experienced researcher\n"
         "3. **Share** your findings with the wider architecture and mobility community\n\n"
         "You have a lot of freedom to define your own question. The research can be carried out in another "
         "language, such as **French or Spanish**, but the final work must be translated into English."),
    ]


def _mentorship(now):
    return [
        ("**Mentorship:** each fellow has an **academic mentor** and a **professional mentor**, and works "
         "closely with the 1PAX team, receiving guidance and feedback throughout the six months.\n\n"
         "Fellows work on **real, ongoing international projects** in aviation, transportation, and urban "
         "development — not simulated academic exercises."),
    ]


def _jury(now):
    lines = ["**The fellows are selected by an international jury of seven professionals:**", ""]
    lines += [f"• **{name}** — {role}" for name, role in JURY]
    return ["\n".join(lines)]


def _selection(now):
    return [
        ("**How applications are evaluated:** portfolio, background, motivation, and potential — how you "
         "think, what you are curious about, and what you could bring. The jury looks for curious, proactive "
         "candidates with strong architectural thinking, initiative, adaptability, and the ability to work "
         "across cultures.\n\n"
         "**Process:** eligible applications are reviewed → about **10 candidates are shortlisted** and "
         f"interviewed by the jury (until {INTERVIEWS_UNTIL}) → **two fellows** are selected and everyone is "
         f"notified by email on **{RESULTS_DATE}**."),
    ]


def _apply(now):
    return [
        ("**How to apply:** submit the online application at "
         f"[{APPLY_URL}]({APPLY_URL}).\n\n"
         "**Documents:**\n"
         "• **CV** — academic background, experience, skills, and achievements\n"
         "• **Portfolio** — your strongest academic, professional, or personal work (PDF or link)\n"
         "• **Letter of motivation** — why the fellowship, what attracts you to mobility, what you hope to learn\n"
         "• **Recommendation letter** — one is required; a second one is strongly recommended\n\n"
         "Applications are complete only when all required documents are submitted."),
        _deadline_line(now),
    ]


def _visa(now):
    return [
        ("**Visas:** the fellowship itself is remote, so a visa is only relevant for the office visit. "
         "1PAX will do everything it can to support the visa process. Because requirements and processing "
         "times vary a lot between countries, the visit can be moved to our **Belgrade** or **Lima** office "
         "if one destination proves difficult."),
    ]


def _vs_internship(now):
    return [
        ("**Fellowship vs. internship:**\n\n"
         "• An **internship** is supervised, hands-on training usually focused on one role or project, and "
         "can be paid or unpaid.\n"
         "• The **1PAX Fellowship** combines international project work with an **independent research "
         "project**, mentorship, and greater professional autonomy — and it is **always paid**."),
    ]


def _after(now):
    return [
        ("The fellowship **does not guarantee employment**, but outstanding fellows may be considered for "
         "future opportunities at 1PAX based on performance and the studio's needs."),
    ]


def _contact(now):
    return [f"For fellowship questions not covered here, write to **{CONTACT_EMAIL}**."]


_TOPICS = [
    ("jury", _jury, ("jury", "juror", "jurors", "judges", "judge", "who selects", "who chooses",
                     "who decides", "selection committee", "committee")),
    ("eligibility", _eligibility, ("eligible", "eligibility", "who can apply", "age", "age limit",
                                   "years old", "how old", "qualify", "any country", "which countries",
                                   "what countries", "nationality", "apply from", "i am from", "i m from",
                                   "outside europe", "public university", "private university")),
    ("vs_internship", _vs_internship, ("difference", "different from an internship", "vs internship",
                                        "versus internship", "compared to an internship")),
    ("visa", _visa, ("visa", "visas", "immigration")),
    ("research", _research, ("research", "thesis", "topic", "topics", "study project")),
    ("pay", _pay, ("paid", "pay", "salary", "stipend", "compensation", "remuneration", "money",
                   "how much", "unpaid", "wage")),
    ("dates", _dates, ("deadline", "when", "dates", "date", "timeline", "close", "closes", "closing",
                       "results", "start", "starts", "begin", "begins", "still open", "open")),
    ("after", _after, ("after the fellowship", "job after", "hired after", "employment", "guarantee",
                       "full time job", "stay at 1pax")),
    ("apply", _apply, ("apply", "application", "documents", "cv", "resume", "portfolio",
                       "recommendation", "letter", "letters", "motivation", "submit", "materials",
                       "requirements to apply", "how to join")),
    ("eligibility", _eligibility, ("eligible", "eligibility", "who can", "age", "old", "years old",
                                   "requirements", "requirement", "qualify", "university", "graduate",
                                   "student", "students", "degree", "country", "countries", "english",
                                   "nationality", "can i")),
    ("selection", _selection, ("selection", "selected", "evaluate", "evaluated", "evaluation",
                               "interview", "interviews", "shortlist", "criteria", "chosen", "choose")),
    ("mentorship", _mentorship, ("mentor", "mentors", "mentorship", "work on", "projects", "tasks",
                                 "day to day", "what will i do")),
    ("format", _format, ("remote", "online", "visit", "travel", "office", "offices", "paris", "lima",
                         "belgrade", "where", "how long", "duration", "months", "location",
                         "in person", "relocate")),
    ("contact", _contact, ("contact", "email", "question")),
]

FELLOWSHIP_MARKERS = (
    "fellowship", "fellowships", "fellow", "fellows", "grad fellowship", "graduate fellowship",
    "graduate program", "graduate programme", "grad program", "research fellowship",
)


def looks_like_fellowship_question(text: str) -> bool:
    norm_text = _norm(text)
    if _has(norm_text, ("fellow architects", "fellow designers", "fellow employees")):
        return False
    return _has(norm_text, FELLOWSHIP_MARKERS)


def fellowship_topic(text: str) -> str:
    norm_text = _norm(text)
    # The programme name itself ("graduate fellowship") must not trigger the eligibility topic.
    for name in ("1pax graduate fellowship", "graduate fellowship", "grad fellowship", "graduate program",
                 "graduate programme", "grad program"):
        norm_text = f" {norm_text} ".replace(f" {name} ", " fellowship ").strip()
    if _has(norm_text, ("apply", "applying", "applicants")) and " from " in f" {norm_text} ":
        return "eligibility"  # "can I apply from Nigeria?"
    for topic, _, markers in _TOPICS:
        if _has(norm_text, markers):
            return topic
    return "overview"


def answer_fellowship(text: str, now: Optional[datetime] = None) -> List[str]:
    topic = fellowship_topic(text)
    for name, builder, _ in _TOPICS:
        if name == topic:
            return builder(now)
    return _overview(now)
