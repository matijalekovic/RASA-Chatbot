#!/usr/bin/env python3
"""Pure-function checks for portfolio insights, company due-diligence answers, and the fellowship."""

from datetime import datetime, timezone
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from actions.actions import (  # noqa: E402
    ActionAnswerProjectQuery,
    ActionHandleOutOfScope,
    ActionListProjects,
)
from actions.company_actions import ActionAnswerCompanyQuery  # noqa: E402
from actions.company_inquiries import build_inquiry_answer, infer_inquiry_type  # noqa: E402
from actions.fellowship_data import answer_fellowship, fellowship_topic  # noqa: E402
from actions.portfolio_insights import (  # noqa: E402
    FACTS,
    answer_portfolio_query,
    parse_portfolio_query,
)
from actions.projects_data import PROJECTS  # noqa: E402


class _Tracker:
    def __init__(self, text, intent="", previous=(), slots=None):
        self.latest_message = {
            "text": text,
            "metadata": {"lang": "EN"},
            "intent": {"name": intent},
            "entities": [],
        }
        self.events = [{"event": "user", "text": t} for t in previous] + [{"event": "user", "text": text}]
        self._slots = slots or {}

    def get_latest_entity_values(self, entity_type):
        return iter(())

    def get_slot(self, name):
        return self._slots.get(name)


class _Dispatcher:
    def __init__(self):
        self.messages = []

    def utter_message(self, **kwargs):
        self.messages.append(kwargs)

    @property
    def text(self):
        return "\n".join(m.get("text", "") for m in self.messages)


def _run(action, text, intent="", previous=()):
    dispatcher = _Dispatcher()
    events = action().run(dispatcher, _Tracker(text, intent, previous), {})
    return dispatcher, events


def test_every_project_has_classified_status_and_procurement():
    for key in PROJECTS:
        assert FACTS[key]["status"] in {"built", "under_construction", "design", "study", "competition", "concession"}
        assert FACTS[key]["procurement"]


def test_biggest_project_answer_separates_built_from_competitions_and_budget():
    text, keys, request = answer_portfolio_query("What is the biggest project you did?")
    assert request["kind"] == "rank"
    assert "Sofia Airport" in text and "110,000 m²" in text
    assert "Lanzhou" in text and "Competition entry" in text
    assert "850 million €" in text  # Velana leads by budget
    assert keys[0] == "sofia_airport"


def test_smallest_and_followup_inherit_context():
    text, keys, _ = answer_portfolio_query("and the smallest?", ["what's your biggest project?"])
    assert "120 m²" in text and "Taxidrone Vertiport" in text


def test_metric_specific_rankings():
    assert "Velana" in answer_portfolio_query("what is your most expensive project?")[0].split("\n")[1]
    capacity = answer_portfolio_query("which airport project handles the most passengers?")[0]
    assert "passengers" in capacity
    first = answer_portfolio_query("what was 1PAX's first project?")[0]
    assert "2012" in first and "predate" in first


def test_filters_groups_stats_and_awards():
    built = answer_portfolio_query("which projects are built?")[0]
    assert "Built: 10 projects" in built
    assert parse_portfolio_query("what airport projects are under construction?")["status"] == "under_construction"
    assert "Over 100 million €" in answer_portfolio_query("group your projects by budget")[0]
    stats = answer_portfolio_query("how many countries have you worked in?")[0]
    assert "57 projects" in stats and "countries and territories" in stats
    awards = answer_portfolio_query("did you win any competitions?")[0]
    assert "1st Prize" in awards and "2nd Prize" in awards


def test_project_detail_questions_are_not_portfolio_queries():
    for text in ("how big is Sofia airport?", "tell me about Sofia airport", "is Sofia airport built?",
                 "show me all projects", "where are your offices?"):
        assert parse_portfolio_query(text) is None, text


def test_inquiry_detection():
    cases = {
        "what languages does your team speak?": "languages",
        "does having an office affect the way you do business with us?": "local_presence",
        "do you do engineering or only architecture?": "engineering",
        "who are your partners?": "partners",
        "have you worked with Arup?": "partners",
        "what else do you do apart from airports?": "beyond_airports",
        "do you design hospitals?": "beyond_airports",
        "do you only do large projects?": "project_size",
        "is there a minimum project size?": "project_size",
        "how do we start a project with you?": "engagement",
        "what stages do you cover?": "project_stages",
        "are you ISO certified?": "certifications",
        "what is your track record?": "track_record",
        "is the fellowship paid?": "fellowship",
        "do I need to speak French to work at 1PAX?": "",
        "which clients have you worked with?": "",
        "where are your offices?": "",
    }
    for text, expected in cases.items():
        assert infer_inquiry_type(text) == expected, (text, infer_inquiry_type(text))


def test_inquiry_answers_use_portfolio_data():
    assert "SETEC" in "\n".join(build_inquiry_answer("engineering", "do you do engineering?"))
    arup = "\n".join(build_inquiry_answer("partners", "have you worked with Arup?"))
    assert "Almaty" in arup
    size = "\n".join(build_inquiry_answer("project_size", "do you only do large projects?"))
    assert "no minimum project size" in size and "120 m²" in size
    hospital = "\n".join(build_inquiry_answer("beyond_airports", "do you design hospitals?"))
    assert "not part of 1PAX's current portfolio" in hospital
    metro = "\n".join(build_inquiry_answer("beyond_airports", "have you designed metro stations?"))
    assert "Belgrade Metro" in metro


def test_fellowship_topics_and_deadline():
    assert fellowship_topic("who is on the fellowship jury?") == "jury"
    assert fellowship_topic("can I apply for the fellowship from Nigeria?") == "eligibility"
    assert fellowship_topic("is the fellowship paid?") == "pay"
    before = "\n".join(answer_fellowship("when is the deadline", now=datetime(2026, 9, 14, tzinfo=timezone.utc)))
    after = "\n".join(answer_fellowship("when is the deadline", now=datetime(2026, 10, 2, tzinfo=timezone.utc)))
    assert "open until" in before and "closed" in after
    jury = "\n".join(answer_fellowship("who is on the jury"))
    assert "Cristiano Ceccato" in jury and "Jean-Charles Content" in jury


def test_actions_route_portfolio_and_inquiries():
    dispatcher, events = _run(ActionAnswerProjectQuery, "what is the biggest project you did?", "ask_project_area")
    assert "Largest built or under construction" in dispatcher.text
    assert any(e.get("name") == "project_name" and e.get("value") == "sofia_airport" for e in events)

    dispatcher, _ = _run(ActionListProjects, "what about the cheapest?", "ask_projects_list",
                         previous=["what is the most expensive project you did?"])
    assert "Lowest disclosed budgets" in dispatcher.text

    dispatcher, _ = _run(ActionAnswerCompanyQuery, "what languages does your team speak?", "ask_company_team")
    assert "13 languages" in dispatcher.text

    dispatcher, _ = _run(ActionAnswerCompanyQuery, "is the graduate fellowship paid?", "ask_company_compensation")
    assert "young architect in France" in dispatcher.text

    dispatcher, _ = _run(ActionHandleOutOfScope, "do you partner with engineering companies?", "nlu_fallback")
    assert "Engineering firms" in dispatcher.text or "engineering" in dispatcher.text.lower()

    dispatcher, _ = _run(ActionAnswerProjectQuery, "who are the partners?", "ask_project_partners")
    assert "partner network" in dispatcher.text


def test_live_probe_regressions():
    # "biggest project" must not be treated as a Sofia Airport alias.
    dispatcher, _ = _run(ActionListProjects, "what is the biggest project you did?", "ask_projects_ranking")
    assert "ranks **#" not in dispatcher.text
    # Offices intent must answer offices, not the Working & Living service.
    dispatcher, _ = _run(ActionAnswerCompanyQuery, "where do you have offices?", "ask_company_offices")
    assert "Paris" in dispatcher.text and "Working & Living" not in dispatcher.text
    # Portfolio + company inquiries misrouted by NLU to the services action.
    from actions.services_actions import ActionAnswerServicesQuery

    dispatcher, _ = _run(ActionAnswerServicesQuery, "do you have experience renovating live terminals?",
                         "ask_service_airports")
    assert "Refurbishment" in dispatcher.text
    dispatcher, _ = _run(ActionAnswerServicesQuery, "are you ISO certified?", "ask_service_bim")
    assert "ISO 19650" in dispatcher.text and "Revit modelling" not in dispatcher.text
    # Fellowship context carries into a short follow-up.
    dispatcher, _ = _run(ActionAnswerCompanyQuery, "who can apply?", "ask_company_candidate_profile",
                         previous=["tell me about the fellowship"])
    assert "20 to 28" in dispatcher.text


def test_story_suite_regressions_after_nlu_moves():
    from actions.services_actions import ActionAnswerServicesQuery
    from actions.team_actions import ActionAnswerTeamQuery

    # S02-04: NLU now says ask_about_team_member; must still list projects.
    dispatcher, _ = _run(ActionAnswerTeamQuery, "what projects have they done?", "ask_about_team_member")
    assert "Airports and Transportation" in dispatcher.text
    # S15-09: NLU now says ask_services_list; must answer the public-client segment.
    dispatcher, _ = _run(ActionAnswerServicesQuery, "what is 1PAX's experience with government clients?",
                         "ask_services_list")
    assert any(w in dispatcher.text.lower() for w in ("government", "public", "ministry"))


if __name__ == "__main__":
    test_every_project_has_classified_status_and_procurement()
    test_biggest_project_answer_separates_built_from_competitions_and_budget()
    test_smallest_and_followup_inherit_context()
    test_metric_specific_rankings()
    test_filters_groups_stats_and_awards()
    test_project_detail_questions_are_not_portfolio_queries()
    test_inquiry_detection()
    test_inquiry_answers_use_portfolio_data()
    test_fellowship_topics_and_deadline()
    test_actions_route_portfolio_and_inquiries()
    test_live_probe_regressions()
    test_story_suite_regressions_after_nlu_moves()
    print("Company inquiry unit checks passed.")
