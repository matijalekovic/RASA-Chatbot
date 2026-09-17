"""
1PAX Graduate Fellowship 2026 — structured facts and a small topic router.

Source of truth: the live fellowship portal https://1pax-fellowship-portal.vercel.app/
(code in ~/Documents/Internships/internship-portal: TalentPortal.tsx, fellowship-faq.ts,
application-deadline.mjs). Older PDF/DOCX drafts (August 14 deadline, age 25, LMIC-only
eligibility) are superseded. Every answer carries the portal link.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from .portfolio_insights import _has, _norm

APPLY_URL = "https://1pax-fellowship-portal.vercel.app/"
CONTACT_EMAIL = "contact@1pax.com"
PORTAL_LINK = f"[1pax-fellowship-portal.vercel.app]({APPLY_URL})"

DEADLINE_UTC = datetime(2026, 9, 30, 21, 59, 59, tzinfo=timezone.utc)
DEADLINE_DISPLAY = "September 30, 2026 at 23:59 (Paris time)"
INTERVIEWS_UNTIL = "October 6, 2026"
RESULTS_DATE = "October 9, 2026"
START_DATE = "October 15, 2026"

JURY = [
    ("Cristiano Ceccato", "Director and Aviation Sector Leader, Zaha Hadid Architects (London)",
     "leads ZHA's aviation sector; 25+ years directing major airport projects worldwide"),
    ("Michel Rojkind", "Founder, Rojkind Arquitectos (Mexico City)",
     "architect and urbanist; Honorary Fellow of the AIA (2025)"),
    ("J. Pablo Serrano Orozco", "Founding Partner, Serrano Monjaraz Arquitectos",
     "architect and educator, teaching at Universidad Iberoamericana since 1992"),
    ("Marianela B. Castro de la Borda", "CEO, Director & Co-founder, FANCYSTUDIOLIMA",
     "curator of the Peruvian Pavilion at the 16th Venice Architecture Biennale"),
    ("Graciela Torre", "Founder & Director, TAW Architecture and TAW Lab",
     "architect and urbanist working on mobility, innovation, care, and sustainability"),
    ("Karel Van Oordt", "Senior Project Coordinator, Eurocities",
     "urban development specialist with 12+ years in sustainable cities and infrastructure"),
    ("Jean-Charles Content", "Head of Architecture, Asia-Pacific, Artelia Airports",
     "nearly 18 years leading airport terminals and masterplans across Asia"),
]

FOCUS_TRACKS = [
    "Aviation and airport terminal design",
    "Transportation hubs and passenger flow",
    "Urban development and future cities",
    "Mobility infrastructure research",
    "BIM, digital workflows, and coordination",
    "Passenger experience and public-space design",
    "Visualization, storytelling, and portfolio communication",
]

PORTAL_BUTTON = {"title": "Open the fellowship portal", "url": APPLY_URL}


def applications_open(now: Optional[datetime] = None) -> bool:
    return (now or datetime.now(timezone.utc)) <= DEADLINE_UTC


def _link_line(now: Optional[datetime] = None) -> str:
    if applications_open(now):
        return (f"👉 **Apply or read the full details on the fellowship portal:** {PORTAL_LINK} — "
                f"applications close **{DEADLINE_DISPLAY}**.")
    return (f"👉 Applications for the 2026 cohort **closed on {DEADLINE_DISPLAY}** (results {RESULTS_DATE}, "
            f"start {START_DATE}). The programme details stay available at {PORTAL_LINK}; "
            "watch 1pax.com for the next edition.")


def _overview(now):
    return [
        ("**1PAX Graduate Fellowship 2026 — Design the Future of Mobility**\n\n"
         "A **paid, fully remote, six-month fellowship** for emerging architects to gain international "
         "experience, work on **real-world aviation, transportation, and urban development projects**, "
         "and develop their own **research project** at the intersection of architecture and mobility.\n\n"
         "**Why it exists — Talent is universal. Opportunity is not.** Exceptional designers can be found "
         "in every corner of the world, but access to international projects, mentorship, and professional "
         "networks is often limited by geography and circumstance. The fellowship was created to help "
         "bridge that gap."),
        ("**At a glance:**\n"
         "• **2 fellows** selected worldwide — applications open to every country and territory\n"
         f"• **6 months**, starting **{START_DATE}**\n"
         "• **Paid** — at the salary level of a young architect in France\n"
         "• **Fully remote**, plus a **fully paid visit to our Paris office** (flights + accommodation)\n"
         "• **Real project work** with the 1PAX team + an **independent research project** guided by an "
         "experienced researcher\n"
         "• **For:** recent architecture graduates or final-year students, **20–28 years old**\n\n"
         "**What you will gain:** international project experience, professional mentorship from architects, "
         "planners and mobility specialists, global collaboration across time zones, and career development — "
         "a stronger portfolio, technical skills, and global studio readiness."),
        _link_line(now),
        ("You can ask me about **eligibility**, **pay**, the **research project**, **application documents**, "
         "the **jury**, the **selection process**, or **key dates**."),
    ]


def _eligibility(now):
    return [
        ("**Who can apply to the 1PAX Graduate Fellowship:**\n\n"
         "• **Recent architecture graduates or final-year students** from any university — public or private\n"
         "• **20 to 28 years old** at the fellowship start\n"
         "• Strong design potential and a strong portfolio\n"
         "• Professional proficiency in **English**\n"
         f"• Available from **{START_DATE}**\n"
         "• A genuine passion for shaping the future of transportation and cities through thoughtful, "
         "human-centered design\n\n"
         "**Global eligibility:** applicants from **every country and territory** may apply. Citizenship or "
         "long-term residence is collected only as context — it doesn't exclude anyone.\n\n"
         "The jury looks for **potential as much as experience**: curiosity, initiative, communication, design "
         "passion, and the ability to work in an international remote team."),
        _link_line(now),
    ]


def _dates(now):
    return [
        ("**Fellowship timeline — 2026 cohort:**\n\n"
         f"1. **Application** — submit by **{DEADLINE_DISPLAY}**\n"
         f"2. **Interviews** — until **{INTERVIEWS_UNTIL}**, with about 10 shortlisted candidates\n"
         f"3. **Selection** — **{RESULTS_DATE}**: two fellows are selected and everyone is notified by email\n"
         f"4. **Fellowship begins** — **{START_DATE}**, for six months"),
        _link_line(now),
    ]


def _pay(now):
    return [
        ("**Yes — the fellowship is always paid.** The remuneration corresponds to the **salary level of a "
         "young architect in France**.\n\n"
         "The programme also includes a **fully paid visit to our Paris office** — flights and accommodation "
         "are covered — to meet and work with the team in person."),
        _link_line(now),
    ]


def _format(now):
    return [
        ("**How the fellowship works:** six months, **fully remote**, collaborating with 1PAX teams across "
         "countries and time zones.\n\n"
         "Fellows also have a **fully paid visit to our Paris office** (flights + accommodation) to meet and "
         "work with the team. Depending on a fellow's circumstances or visa timing, a visit to our **Lima** or "
         "**Belgrade** office can be considered instead.\n\n"
         "When you apply, you indicate your remote and travel availability (remote and able to travel for "
         "funded visits, remote with limited travel, or remote only)."),
        _link_line(now),
    ]


def _research(now):
    return [
        ("**The research project** is an integral part of the fellowship. Alongside real-world project work, "
         "each fellow develops an **independent research project** on a topic of their choice at the "
         "intersection of architecture and mobility, guided by an **experienced researcher** who helps shape "
         "the research question, methodology, and ideas.\n\n"
         "**Choose** — define a topic you are passionate about (architecture, aviation, transportation, urban "
         "development, sustainability, or another field connected to 1PAX's work)\n"
         "**Develop** — work with an experienced researcher to build your line of inquiry\n"
         "**Share** — present your findings and contribute to the wider conversation on architecture and mobility\n\n"
         "You have a lot of freedom. The research can be carried out in another language such as **French or "
         "Spanish**, but the final work must be translated into English."),
        _link_line(now),
    ]


def _work(now):
    return [
        ("**What fellows work on:** real, ongoing 1PAX projects in **aviation, transportation, and urban "
         "development** — not simulated academic exercises. You contribute to large-scale international work "
         "shaped by different cultural and urban contexts, collaborating with a multidisciplinary team.\n\n"
         "**Mentorship:** each fellow has an **academic mentor** and a **professional mentor**, and receives "
         "guidance and feedback from the 1PAX team throughout — covering design, digital workflows, and "
         "collaboration across cultures.\n\n"
         "**Focus areas you can choose when applying:**\n" + "\n".join(f"• {t}" for t in FOCUS_TRACKS)),
        _link_line(now),
    ]


def _jury(now):
    lines = ["**The fellows are selected by an international jury of seven architects and urbanists:**", ""]
    lines += [f"• **{name}** — {role}; {note}" for name, role, note in JURY]
    lines += ["", "The committee assesses each finalist's portfolio, motivation, and potential to contribute "
              "to the future of architecture."]
    return ["\n".join(lines), _link_line(now)]


def _selection(now):
    return [
        ("**How applications are evaluated:** a combination of **portfolio, background, motivation, and "
         "potential** — not only what you have done, but how you think, what you are curious about, and what "
         "you could bring. The jury looks for curious, proactive candidates with strong architectural thinking, "
         "initiative, adaptability, and the ability to work across cultures.\n\n"
         "**Process:**\n"
         "1. Eligible applications are reviewed after the deadline\n"
         f"2. About **10 candidates are shortlisted** and interviewed by the jury (until {INTERVIEWS_UNTIL})\n"
         f"3. **Two fellows** are selected — results by email on **{RESULTS_DATE}**\n"
         "4. Selected fellows receive next steps for the programme start"),
        _link_line(now),
    ]


def _apply(now):
    return [
        ("**How to apply:** complete the online application on the fellowship portal. It takes you through "
         "four parts:\n\n"
         "1. **CV / resume** (PDF or DOCX) — upload it first and the form pre-fills your profile, tools, and "
         "experience; you can edit everything before submitting\n"
         "2. **Candidate profile & fellowship fit** — contact details, country, university, graduation status, "
         "languages, your primary focus area, and remote/travel availability\n"
         "3. **Portfolio** — a portfolio link (best for large files) or a PDF/JPG/PNG upload\n"
         "4. **Recommendation & motivation** — **one recommendation letter is required**, a second is strongly "
         "recommended; plus a motivation letter or a written motivation statement\n\n"
         "**File limits:** up to 6 MB per file and about 10 MB in total — use a portfolio link for large work."),
        _link_line(now),
    ]


def _visa(now):
    return [
        ("**Visas:** the fellowship itself is remote, so a visa only matters for the office visit. 1PAX will do "
         "everything it can to support the visa process. Because requirements and processing times vary a lot "
         "between countries, the visit can be moved to our **Belgrade** or **Lima** office if Paris proves "
         "difficult."),
        _link_line(now),
    ]


def _vs_internship(now):
    return [
        ("**Fellowship vs. internship — more than an internship, a chance to develop your own ideas:**\n\n"
         "**Internship:** learning through professional experience · hands-on practical training · usually "
         "focused on one role or project · directly supervised · can be paid or unpaid\n\n"
         "**1PAX Fellowship:** learning through international project experience · an independent research "
         "project · mentorship and professional development · greater professional autonomy · **always paid**"),
        _link_line(now),
    ]


def _after(now):
    return [
        ("The fellowship **does not guarantee employment**, but outstanding fellows may be considered for "
         "future opportunities at 1PAX based on performance and business needs. Either way, you leave with "
         "international project experience, a research project, and a stronger portfolio."),
        _link_line(now),
    ]


def _status(now):
    return [
        ("I can't see submitted applications. If you already applied, **please don't submit again** — the "
         "portal sends a confirmation email after a successful submission. For questions about an application, "
         f"write to **{CONTACT_EMAIL}** using the same name and email you applied with.\n\n"
         f"Shortlisted candidates are contacted for interviews until {INTERVIEWS_UNTIL}, and all applicants hear "
         f"back by email on {RESULTS_DATE}."),
        _link_line(now),
    ]


def _contact(now):
    return [
        (f"For fellowship questions not covered here, write to **{CONTACT_EMAIL}**. The portal also has a "
         "full FAQ with 20 questions about the programme, the experience, the research project, and selection."),
        _link_line(now),
    ]


def _link(now):
    return [
        ("Here is the **1PAX Graduate Fellowship 2026** portal — programme details, the full FAQ, and the "
         f"online application: {PORTAL_LINK}"),
        _link_line(now),
    ]


# Order matters: specific topics first.
_TOPICS = [
    ("link", _link, ("link", "url", "website", "web page", "webpage")),
    ("status", _status, ("my application", "application status", "did you receive", "received my",
                         "already applied", "i applied", "submitted", "confirmation email", "hear back")),
    ("jury", _jury, ("jury", "juror", "jurors", "judges", "judge", "who selects", "who chooses",
                     "who decides", "selection committee", "committee")),
    ("vs_internship", _vs_internship, ("difference", "different from an internship", "vs internship",
                                        "versus internship", "compared to an internship", "is it an internship",
                                        "same as an internship")),
    ("eligibility", _eligibility, ("eligible", "eligibility", "who can apply", "age", "age limit",
                                   "years old", "how old", "too old", "too young", "qualify", "any country",
                                   "which countries", "what countries", "nationality", "apply from", "i am from",
                                   "i m from", "outside europe", "public university", "private university",
                                   "requirements", "requirement", "not an architect", "final year", "student",
                                   "students", "degree", "english", "who is it for", "for me")),
    ("visa", _visa, ("visa", "visas", "immigration")),
    ("research", _research, ("research", "thesis", "topic", "topics", "study project", "freedom")),
    ("pay", _pay, ("paid", "pay", "salary", "stipend", "compensation", "remuneration", "money",
                   "how much", "unpaid", "wage")),
    ("dates", _dates, ("deadline", "when", "dates", "date", "timeline", "close", "closes", "closing",
                       "results", "start", "starts", "begin", "begins", "still open", "open", "too late")),
    ("after", _after, ("after the fellowship", "job after", "hired after", "employment", "guarantee",
                       "full time job", "stay at 1pax", "afterwards")),
    ("apply", _apply, ("apply", "application", "documents", "cv", "resume", "portfolio",
                       "recommendation", "letter", "letters", "motivation", "submit", "materials",
                       "how to join", "form", "upload", "file size")),
    ("selection", _selection, ("selection", "selected", "evaluate", "evaluated", "evaluation",
                               "interview", "interviews", "shortlist", "criteria", "chosen", "choose",
                               "chances")),
    ("work", _work, ("mentor", "mentors", "mentorship", "work on", "projects", "tasks", "day to day",
                     "what will i do", "focus", "focus area", "tracks", "learn", "gain", "benefits",
                     "experience")),
    ("format", _format, ("remote", "online", "visit", "travel", "office", "offices", "paris", "lima",
                         "belgrade", "where", "how long", "duration", "months", "location",
                         "in person", "relocate", "time zone")),
    ("contact", _contact, ("contact", "email", "question", "faq")),
]

_FOLLOWUP_TOPICS = {name for name, _, _ in _TOPICS} - {"contact"}

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


def is_followup_topic(topic: str) -> bool:
    return topic in _FOLLOWUP_TOPICS


def answer_fellowship(text: str, now: Optional[datetime] = None) -> List[str]:
    topic = fellowship_topic(text)
    for name, builder, _ in _TOPICS:
        if name == topic:
            return builder(now)
    return _overview(now)


def fellowship_buttons() -> List[Dict[str, str]]:
    return [dict(PORTAL_BUTTON)]
