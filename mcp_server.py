#!/usr/bin/env python3
"""
1PAX chatbot QA MCP server.

This server intentionally has no third-party dependencies. It can run as a
stdio MCP server for local clients, or as a stateless HTTP JSON-RPC endpoint
for Railway deployments behind nginx.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable


SERVER_NAME = "1pax-chatbot-qa"
SERVER_VERSION = "0.1.0"
DEFAULT_PROTOCOL_VERSION = "2024-11-05"


class ToolError(Exception):
    """Raised when a tool receives invalid input or a backend call fails."""


class JsonRpcError(Exception):
    def __init__(self, code: int, message: str, data: Any | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


@dataclass(frozen=True)
class EndpointConfig:
    chatbot_base_url: str | None
    rasa_base_url: str
    translate_base_url: str
    request_timeout: float
    allow_base_url_override: bool
    http_bearer_token: str

    @classmethod
    def from_env(cls) -> "EndpointConfig":
        chatbot_base_url = _clean_base(os.environ.get("CHATBOT_BASE_URL"))
        rasa_base_url = _clean_base(
            os.environ.get("RASA_BASE_URL")
            or (chatbot_base_url if chatbot_base_url else "http://127.0.0.1:5005")
        )
        translate_base_url = _clean_base(
            os.environ.get("TRANSLATE_BASE_URL")
            or (chatbot_base_url if chatbot_base_url else "http://127.0.0.1:5056")
        )
        timeout_raw = os.environ.get("MCP_CHATBOT_TIMEOUT_SECONDS", "20")
        try:
            request_timeout = max(1.0, float(timeout_raw))
        except ValueError:
            request_timeout = 20.0

        return cls(
            chatbot_base_url=chatbot_base_url,
            rasa_base_url=rasa_base_url,
            translate_base_url=translate_base_url,
            request_timeout=request_timeout,
            allow_base_url_override=os.environ.get("MCP_ALLOW_BASE_URL_OVERRIDE") == "1",
            http_bearer_token=os.environ.get("MCP_BEARER_TOKEN", "").strip(),
        )


def _clean_base(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().rstrip("/")


def _join_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def _now_sender(prefix: str = "mcp_qa") -> str:
    return f"{prefix}_{int(time.time())}_{uuid.uuid4().hex[:8]}"


def _json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def _read_http_json(
    method: str,
    url: str,
    body: dict[str, Any] | None = None,
    timeout: float = 20.0,
) -> Any:
    encoded_body = None
    headers = {"Accept": "application/json"}
    if body is not None:
        encoded_body = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url,
        data=encoded_body,
        headers=headers,
        method=method.upper(),
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8")
            if not payload:
                return {}
            return json.loads(payload)
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(payload)
        except Exception:
            parsed = payload
        raise ToolError(f"{method.upper()} {url} failed with HTTP {exc.code}: {parsed}") from exc
    except urllib.error.URLError as exc:
        raise ToolError(f"{method.upper()} {url} failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise ToolError(f"{method.upper()} {url} timed out") from exc
    except json.JSONDecodeError as exc:
        raise ToolError(f"{method.upper()} {url} returned invalid JSON") from exc


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _lower_text(value: Any) -> str:
    return str(value or "").casefold()


def _contains_any(text: str, phrases: list[Any]) -> bool:
    lower = _lower_text(text)
    return any(_lower_text(phrase) in lower for phrase in phrases if str(phrase).strip())


def _contains_all(text: str, phrases: list[Any]) -> bool:
    lower = _lower_text(text)
    return all(_lower_text(phrase) in lower for phrase in phrases if str(phrase).strip())


def _summarize_tracker(tracker: dict[str, Any], include_events: bool, last_events: int) -> dict[str, Any]:
    events = tracker.get("events") or []
    summary = {
        "sender_id": tracker.get("sender_id"),
        "slots": tracker.get("slots") or {},
        "latest_message": tracker.get("latest_message") or {},
        "latest_action_name": tracker.get("latest_action_name"),
        "active_loop": tracker.get("active_loop"),
        "paused": tracker.get("paused"),
        "events_count": len(events),
    }
    if include_events:
        summary["events"] = events[-max(1, last_events):]
    return summary


class ChatbotQaTools:
    def __init__(self, config: EndpointConfig) -> None:
        self.config = config
        self.tools: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
            "chatbot_health": self.health,
            "chatbot_send_message": self.send_message,
            "chatbot_parse": self.parse,
            "chatbot_get_tracker": self.get_tracker,
            "chatbot_run_workflow": self.run_workflow,
            "chatbot_run_regression": self.run_regression,
        }

    def tool_specs(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "chatbot_health",
                "description": (
                    "Check the configured 1PAX chatbot deployment, including Rasa, "
                    "translation, and an optional parse probe."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "include_parse_check": {
                            "type": "boolean",
                            "description": "Also call /model/parse with a small hello probe.",
                            "default": True,
                        },
                        "base_url": {
                            "type": "string",
                            "description": (
                                "Optional one-off public chatbot URL. Disabled unless "
                                "MCP_ALLOW_BASE_URL_OVERRIDE=1."
                            ),
                        },
                    },
                    "additionalProperties": False,
                },
            },
            {
                "name": "chatbot_send_message",
                "description": (
                    "Send one message to the chatbot REST webhook and optionally include "
                    "NLU parse and tracker context."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "User message to send."},
                        "sender": {
                            "type": "string",
                            "description": "Conversation sender id. Omit for a unique QA sender.",
                        },
                        "source_lang": {
                            "type": "string",
                            "description": "Optional UI translation source language, e.g. SR, FR, ES.",
                        },
                        "translate_input": {
                            "type": "boolean",
                            "description": "Translate through /api/translate before sending to Rasa.",
                            "default": False,
                        },
                        "include_parse": {
                            "type": "boolean",
                            "description": "Include /model/parse for the message Rasa receives.",
                            "default": True,
                        },
                        "include_tracker": {
                            "type": "boolean",
                            "description": "Include a tracker summary after the message.",
                            "default": False,
                        },
                        "base_url": {"type": "string", "description": "Optional public chatbot URL override."},
                    },
                    "required": ["message"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "chatbot_parse",
                "description": "Call Rasa /model/parse and return intent, ranking, and entities.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to parse."},
                        "source_lang": {"type": "string", "description": "Optional source language."},
                        "translate_input": {
                            "type": "boolean",
                            "description": "Translate first through the UI translation proxy.",
                            "default": False,
                        },
                        "base_url": {"type": "string", "description": "Optional public chatbot URL override."},
                    },
                    "required": ["text"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "chatbot_get_tracker",
                "description": "Read a Rasa conversation tracker for a sender id.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sender": {"type": "string", "description": "Rasa sender id to inspect."},
                        "include_events": {
                            "type": "boolean",
                            "description": "Include recent event payloads.",
                            "default": False,
                        },
                        "last_events": {
                            "type": "integer",
                            "description": "How many recent events to include when include_events is true.",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 200,
                        },
                        "base_url": {"type": "string", "description": "Optional public chatbot URL override."},
                    },
                    "required": ["sender"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "chatbot_run_workflow",
                "description": (
                    "Run a multi-turn QA workflow against one sender and validate intents, "
                    "entities, slots, and response text."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sender": {
                            "type": "string",
                            "description": "Sender id. Omit for a unique QA sender.",
                        },
                        "steps": {
                            "type": "array",
                            "description": "Ordered messages and expectations.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string"},
                                    "expect_intent": {"type": "string"},
                                    "expect_response_contains_any": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "expect_response_contains_all": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "expect_response_not_contains": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "expect_entities": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "entity": {"type": "string"},
                                                "value": {"type": "string"},
                                            },
                                            "required": ["entity"],
                                            "additionalProperties": False,
                                        },
                                    },
                                    "expect_slots": {
                                        "type": "object",
                                        "additionalProperties": {"type": "string"},
                                    },
                                },
                                "required": ["message"],
                                "additionalProperties": False,
                            },
                        },
                        "source_lang": {"type": "string", "description": "Optional source language for all steps."},
                        "translate_input": {
                            "type": "boolean",
                            "description": "Translate each step through the UI translation proxy.",
                            "default": False,
                        },
                        "base_url": {"type": "string", "description": "Optional public chatbot URL override."},
                    },
                    "required": ["steps"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "chatbot_run_regression",
                "description": "Run a small built-in QA suite for smoke, context, team, or translation flows.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "suite": {
                            "type": "string",
                            "enum": ["smoke", "project_context", "team", "translation", "core"],
                            "default": "smoke",
                        },
                        "sender": {"type": "string", "description": "Optional sender id prefix."},
                        "base_url": {"type": "string", "description": "Optional public chatbot URL override."},
                    },
                    "additionalProperties": False,
                },
            },
        ]

    def config_snapshot(self) -> dict[str, Any]:
        return {
            "server": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "chatbot_base_url": self.config.chatbot_base_url,
            "rasa_base_url": self.config.rasa_base_url,
            "translate_base_url": self.config.translate_base_url,
            "request_timeout_seconds": self.config.request_timeout,
            "base_url_override_enabled": self.config.allow_base_url_override,
            "http_bearer_token_required": bool(self.config.http_bearer_token),
        }

    def public_mode(self, args: dict[str, Any]) -> bool:
        return bool(args.get("base_url") or self.config.chatbot_base_url)

    def base_url(self, args: dict[str, Any]) -> str | None:
        override = _clean_base(args.get("base_url"))
        if override:
            if not self.config.allow_base_url_override:
                raise ToolError(
                    "base_url overrides are disabled. Set MCP_ALLOW_BASE_URL_OVERRIDE=1 "
                    "only in trusted QA environments."
                )
            return override
        return self.config.chatbot_base_url

    def rasa_url(self, path: str, args: dict[str, Any]) -> str:
        public_base = self.base_url(args)
        if public_base:
            return _join_url(public_base, path)
        return _join_url(self.config.rasa_base_url, path)

    def translate_url(self, path: str, args: dict[str, Any]) -> str:
        public_base = self.base_url(args)
        if public_base:
            public_path = "api/translate/health" if path.strip("/") == "health" else "api/translate"
            return _join_url(public_base, public_path)
        return _join_url(self.config.translate_base_url, path)

    def maybe_translate(self, text: str, args: dict[str, Any]) -> dict[str, Any]:
        translate_input = bool(args.get("translate_input"))
        source_lang = str(args.get("source_lang") or "").strip()
        if not translate_input and not source_lang:
            return {"text": text, "used": False}

        payload = {"text": text, "source_lang": source_lang}
        translated = _read_http_json(
            "POST",
            self.translate_url("translate", args),
            payload,
            timeout=self.config.request_timeout,
        )
        translated_text = str(translated.get("text", text))
        return {
            "text": translated_text,
            "used": True,
            "source_lang": source_lang,
            "response": translated,
        }

    def health(self, args: dict[str, Any]) -> dict[str, Any]:
        include_parse_check = args.get("include_parse_check", True)
        checks: dict[str, Any] = {}

        checks["rasa_status"] = self._safe_check(
            lambda: _read_http_json(
                "GET",
                self.rasa_url("status", args),
                timeout=self.config.request_timeout,
            )
        )
        checks["translation_health"] = self._safe_check(
            lambda: _read_http_json(
                "GET",
                self.translate_url("health", args),
                timeout=self.config.request_timeout,
            )
        )
        if include_parse_check:
            checks["parse_probe"] = self._safe_check(
                lambda: _read_http_json(
                    "POST",
                    self.rasa_url("model/parse", args),
                    {"text": "hello"},
                    timeout=self.config.request_timeout,
                )
            )

        ok = all(item["ok"] for item in checks.values())
        return {"ok": ok, "checks": checks, "config": self.config_snapshot()}

    def send_message(self, args: dict[str, Any]) -> dict[str, Any]:
        message = str(args.get("message") or "").strip()
        if not message:
            raise ToolError("message is required")

        sender = str(args.get("sender") or "").strip() or _now_sender()
        translation = self.maybe_translate(message, args)
        sent_message = translation["text"]

        parse_result = None
        if args.get("include_parse", True):
            parse_result = _read_http_json(
                "POST",
                self.rasa_url("model/parse", args),
                {"text": sent_message},
                timeout=self.config.request_timeout,
            )

        responses = _read_http_json(
            "POST",
            self.rasa_url("webhooks/rest/webhook", args),
            {"sender": sender, "message": sent_message},
            timeout=self.config.request_timeout,
        )
        if not isinstance(responses, list):
            raise ToolError(f"Unexpected chat response shape: {responses!r}")

        response_texts = [str(item.get("text", "")) for item in responses if item.get("text")]
        result: dict[str, Any] = {
            "sender": sender,
            "original_message": message,
            "sent_message": sent_message,
            "translation": translation,
            "parse": _compact_parse(parse_result) if parse_result else None,
            "responses": responses,
            "response_text": " ".join(response_texts).strip(),
            "response_count": len(responses),
        }

        if args.get("include_tracker"):
            tracker = self._tracker(sender, args)
            result["tracker"] = _summarize_tracker(tracker, include_events=False, last_events=20)

        return result

    def parse(self, args: dict[str, Any]) -> dict[str, Any]:
        text = str(args.get("text") or "").strip()
        if not text:
            raise ToolError("text is required")

        translation = self.maybe_translate(text, args)
        parsed = _read_http_json(
            "POST",
            self.rasa_url("model/parse", args),
            {"text": translation["text"]},
            timeout=self.config.request_timeout,
        )
        return {
            "original_text": text,
            "parsed_text": translation["text"],
            "translation": translation,
            "parse": parsed,
            "compact": _compact_parse(parsed),
        }

    def get_tracker(self, args: dict[str, Any]) -> dict[str, Any]:
        sender = str(args.get("sender") or "").strip()
        if not sender:
            raise ToolError("sender is required")
        include_events = bool(args.get("include_events", False))
        last_events = int(args.get("last_events", 20))
        tracker = self._tracker(sender, args)
        return _summarize_tracker(tracker, include_events=include_events, last_events=last_events)

    def run_workflow(self, args: dict[str, Any]) -> dict[str, Any]:
        steps = args.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ToolError("steps must be a non-empty array")

        sender = str(args.get("sender") or "").strip() or _now_sender("mcp_workflow")
        shared_args = dict(args)
        shared_args["sender"] = sender

        results = []
        failures = []
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                raise ToolError(f"step {index} must be an object")
            message = str(step.get("message") or "").strip()
            if not message:
                raise ToolError(f"step {index} message is required")

            call_args = dict(shared_args)
            call_args["message"] = message
            call_args["include_parse"] = True
            call_args["include_tracker"] = bool(step.get("expect_slots"))
            sent = self.send_message(call_args)
            step_failures = _validate_step(step, sent)

            if step.get("expect_slots"):
                tracker = self._tracker(sender, args)
                tracker_summary = _summarize_tracker(tracker, include_events=False, last_events=20)
                sent["tracker"] = tracker_summary
                slot_failures = _validate_slots(step["expect_slots"], tracker_summary.get("slots") or {})
                step_failures.extend(slot_failures)

            step_result = {
                "index": index,
                "message": message,
                "passed": not step_failures,
                "failures": step_failures,
                "sent_message": sent["sent_message"],
                "intent": (sent.get("parse") or {}).get("intent"),
                "entities": (sent.get("parse") or {}).get("entities"),
                "response_text": sent.get("response_text"),
            }
            if "tracker" in sent:
                step_result["tracker"] = sent["tracker"]
            results.append(step_result)

            for failure in step_failures:
                failures.append({"step": index, "message": message, "failure": failure})

        return {
            "passed": not failures,
            "sender": sender,
            "failures": failures,
            "steps": results,
            "summary": {
                "total": len(steps),
                "passed": sum(1 for step in results if step["passed"]),
                "failed": sum(1 for step in results if not step["passed"]),
            },
        }

    def run_regression(self, args: dict[str, Any]) -> dict[str, Any]:
        suite = str(args.get("suite") or "smoke").strip()
        if suite not in REGRESSION_SUITES:
            raise ToolError(f"unknown suite {suite!r}; choose one of {sorted(REGRESSION_SUITES)}")

        sender_prefix = str(args.get("sender") or f"mcp_{suite}").strip()
        workflow_args = {
            "sender": _now_sender(sender_prefix),
            "steps": REGRESSION_SUITES[suite]["steps"],
        }
        if suite == "translation":
            workflow_args["source_lang"] = "SR"
            workflow_args["translate_input"] = True
        if args.get("base_url"):
            workflow_args["base_url"] = args["base_url"]

        result = self.run_workflow(workflow_args)
        result["suite"] = suite
        result["description"] = REGRESSION_SUITES[suite]["description"]
        return result

    def _tracker(self, sender: str, args: dict[str, Any]) -> dict[str, Any]:
        encoded_sender = urllib.parse.quote(sender, safe="")
        tracker = _read_http_json(
            "GET",
            self.rasa_url(f"conversations/{encoded_sender}/tracker", args),
            timeout=self.config.request_timeout,
        )
        if not isinstance(tracker, dict):
            raise ToolError(f"Unexpected tracker response shape: {tracker!r}")
        return tracker

    def _safe_check(self, fn: Callable[[], Any]) -> dict[str, Any]:
        try:
            return {"ok": True, "data": fn()}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}


def _compact_parse(parsed: dict[str, Any] | None) -> dict[str, Any] | None:
    if not parsed:
        return None
    intent = parsed.get("intent") or {}
    ranking = parsed.get("intent_ranking") or []
    entities = parsed.get("entities") or []
    return {
        "intent": {
            "name": intent.get("name"),
            "confidence": intent.get("confidence"),
        },
        "top_intents": [
            {"name": item.get("name"), "confidence": item.get("confidence")}
            for item in ranking[:5]
        ],
        "entities": entities,
    }


def _validate_step(step: dict[str, Any], sent: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    compact = sent.get("parse") or {}
    intent_name = ((compact.get("intent") or {}).get("name")) or ""
    response_text = sent.get("response_text") or ""
    entities = compact.get("entities") or []

    expected_intent = step.get("expect_intent")
    if expected_intent and intent_name != expected_intent:
        failures.append(f"intent {intent_name!r} did not match expected {expected_intent!r}")

    contains_any = _as_list(step.get("expect_response_contains_any"))
    if contains_any and not _contains_any(response_text, contains_any):
        failures.append(f"response did not contain any of {contains_any!r}")

    contains_all = _as_list(step.get("expect_response_contains_all"))
    if contains_all and not _contains_all(response_text, contains_all):
        failures.append(f"response did not contain all of {contains_all!r}")

    not_contains = _as_list(step.get("expect_response_not_contains"))
    blocked = [phrase for phrase in not_contains if _lower_text(phrase) in _lower_text(response_text)]
    if blocked:
        failures.append(f"response contained forbidden phrase(s): {blocked!r}")

    expected_entities = _as_list(step.get("expect_entities"))
    for expected in expected_entities:
        if not isinstance(expected, dict):
            failures.append(f"invalid expected entity spec {expected!r}")
            continue
        entity_name = expected.get("entity")
        expected_value = expected.get("value")
        matches = [entity for entity in entities if entity.get("entity") == entity_name]
        if expected_value:
            matches = [entity for entity in matches if str(entity.get("value")) == str(expected_value)]
        if not matches:
            failures.append(f"entity {expected!r} was not found in parse result")

    return failures


def _validate_slots(expected_slots: dict[str, Any], slots: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for key, expected_value in expected_slots.items():
        actual = slots.get(key)
        if str(actual) != str(expected_value):
            failures.append(f"slot {key!r} was {actual!r}, expected {expected_value!r}")
    return failures


REGRESSION_SUITES: dict[str, dict[str, Any]] = {
    "smoke": {
        "description": "Basic greeting, company overview, and project lookup.",
        "steps": [
            {
                "message": "Hello!",
                "expect_intent": "greet",
                "expect_response_contains_any": ["hello", "hi", "1PAX", "welcome"],
            },
            {
                "message": "What does 1PAX do?",
                "expect_response_contains_any": ["architecture", "airport", "design", "1PAX"],
            },
            {
                "message": "Tell me about Sofia Airport",
                "expect_response_contains_any": ["Sofia", "Terminal", "airport", "1PAX"],
            },
        ],
    },
    "project_context": {
        "description": "Multi-turn project slot continuity with follow-up questions.",
        "steps": [
            {
                "message": "Tell me about Bordeaux Airport",
                "expect_response_contains_any": ["Bordeaux", "airport"],
            },
            {
                "message": "How much did it cost?",
                "expect_response_contains_any": ["cost", "budget", "EUR", "million", "Not available"],
            },
            {
                "message": "Was it built?",
                "expect_response_contains_any": ["built", "status", "complete", "construction", "Not available"],
            },
        ],
    },
    "team": {
        "description": "Leadership and person entity lookup.",
        "steps": [
            {
                "message": "Who is the CEO of 1PAX?",
                "expect_response_contains_any": ["Mabel", "Miranda", "CEO"],
            },
            {
                "message": "Tell me about Mabel Miranda",
                "expect_response_contains_any": ["Mabel", "Miranda", "founder", "CEO"],
            },
        ],
    },
    "translation": {
        "description": "Serbian Latin input translated through the UI proxy before Rasa.",
        "steps": [
            {
                "message": "Koliki je budzet za aerodrom Sofija?",
                "expect_response_contains_any": ["Sofia", "budget", "cost", "EUR", "aerodrom"],
            }
        ],
    },
    "core": {
        "description": "Combined smoke, project context, and team QA.",
        "steps": [],
    },
}
REGRESSION_SUITES["core"]["steps"] = (
    REGRESSION_SUITES["smoke"]["steps"]
    + REGRESSION_SUITES["project_context"]["steps"]
    + REGRESSION_SUITES["team"]["steps"]
)


class McpServer:
    def __init__(self, tools: ChatbotQaTools) -> None:
        self.tools = tools

    def handle_payload(self, payload: Any) -> Any:
        if isinstance(payload, list):
            responses = []
            for request in payload:
                response = self.handle_request(request)
                if response is not None:
                    responses.append(response)
            return responses or None
        return self.handle_request(payload)

    def handle_request(self, request: Any) -> dict[str, Any] | None:
        if not isinstance(request, dict):
            return self.error_response(None, -32600, "Invalid Request")

        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params") or {}
        if not method:
            return self.error_response(request_id, -32600, "Missing method")

        try:
            result = self.dispatch(method, params)
        except JsonRpcError as exc:
            return self.error_response(request_id, exc.code, exc.message, exc.data)
        except ToolError as exc:
            return self.error_response(request_id, -32000, str(exc))
        except Exception as exc:
            return self.error_response(request_id, -32603, f"Internal error: {exc}")

        if request_id is None:
            return None
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def dispatch(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if method == "initialize":
            client_protocol = str(params.get("protocolVersion") or DEFAULT_PROTOCOL_VERSION)
            return {
                "protocolVersion": client_protocol,
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                },
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                "instructions": (
                    "Use the chatbot_* tools to probe the 1PAX Rasa chatbot, "
                    "validate conversations, inspect NLU parses, and check trackers."
                ),
            }
        if method == "ping":
            return {}
        if method == "notifications/initialized":
            return {}
        if method == "tools/list":
            return {"tools": self.tools.tool_specs()}
        if method == "tools/call":
            return self.call_tool(params)
        if method == "resources/list":
            return {"resources": self.resources()}
        if method == "resources/read":
            return self.read_resource(params)
        if method == "prompts/list":
            return {"prompts": []}

        raise JsonRpcError(-32601, f"Method not found: {method}")

    def call_tool(self, params: dict[str, Any]) -> dict[str, Any]:
        name = params.get("name")
        args = params.get("arguments") or {}
        if not isinstance(args, dict):
            raise JsonRpcError(-32602, "tools/call arguments must be an object")
        if name not in self.tools.tools:
            raise JsonRpcError(-32602, f"Unknown tool: {name}")

        try:
            data = self.tools.tools[name](args)
            return _tool_result(data, is_error=False)
        except ToolError as exc:
            return _tool_result({"error": str(exc)}, is_error=True)

    def resources(self) -> list[dict[str, Any]]:
        return [
            {
                "uri": "qa://1pax/config",
                "name": "1PAX QA MCP configuration",
                "description": "Current backend URLs and MCP server settings.",
                "mimeType": "application/json",
            },
            {
                "uri": "qa://1pax/suites",
                "name": "1PAX built-in QA suites",
                "description": "Small built-in regression suites available through chatbot_run_regression.",
                "mimeType": "application/json",
            },
            {
                "uri": "qa://1pax/guide",
                "name": "1PAX QA MCP guide",
                "description": "Short usage guide for manual and workflow QA.",
                "mimeType": "text/markdown",
            },
        ]

    def read_resource(self, params: dict[str, Any]) -> dict[str, Any]:
        uri = params.get("uri")
        if uri == "qa://1pax/config":
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": _json_dumps(self.tools.config_snapshot()),
                    }
                ]
            }
        if uri == "qa://1pax/suites":
            suites = {
                name: {
                    "description": suite["description"],
                    "steps": suite["steps"],
                }
                for name, suite in REGRESSION_SUITES.items()
            }
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": _json_dumps(suites),
                    }
                ]
            }
        if uri == "qa://1pax/guide":
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/markdown",
                        "text": MCP_GUIDE,
                    }
                ]
            }
        raise JsonRpcError(-32602, f"Unknown resource URI: {uri}")

    def error_response(
        self,
        request_id: Any,
        code: int,
        message: str,
        data: Any | None = None,
    ) -> dict[str, Any]:
        error: dict[str, Any] = {"code": code, "message": message}
        if data is not None:
            error["data"] = data
        return {"jsonrpc": "2.0", "id": request_id, "error": error}


def _tool_result(data: dict[str, Any], is_error: bool) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": _json_dumps(data)}],
        "isError": is_error,
    }


MCP_GUIDE = """# 1PAX QA MCP

Typical flow:

1. Run `chatbot_health` to confirm Rasa, translation, and parse endpoints.
2. Use `chatbot_send_message` for one-off manual probes.
3. Use `chatbot_parse` before adding synonyms or NLU examples.
4. Use `chatbot_run_workflow` for multi-turn slot/context checks.
5. Use `chatbot_get_tracker` when a follow-up behaves unexpectedly.

For deployed Railway QA, point the server at the public app with
`CHATBOT_BASE_URL=https://your-railway-app.up.railway.app`, or use the
HTTP MCP endpoint exposed by the container at `/mcp`.
"""


class McpHttpHandler(BaseHTTPRequestHandler):
    app: McpServer
    token: str = ""

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        if self.path.rstrip("/") == "/health":
            self._send_json(
                {
                    "status": "ok",
                    "server": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    "tools": sorted(self.app.tools.tools),
                }
            )
            return
        self._send_json(
            {
                "status": "ok",
                "message": "POST JSON-RPC MCP requests to /mcp.",
                "server": {"name": SERVER_NAME, "version": SERVER_VERSION},
            }
        )

    def do_POST(self) -> None:
        if self.path.rstrip("/") not in ("", "/mcp"):
            self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
            return
        if not self._authorized():
            self._send_json({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
            return

        length = int(self.headers.get("Content-Length", "0") or 0)
        try:
            payload = json.loads(self.rfile.read(length))
        except Exception:
            self._send_json(
                {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        response = self.app.handle_payload(payload)
        if response is None:
            self.send_response(HTTPStatus.ACCEPTED)
            self._send_cors_headers()
            self.end_headers()
            return
        self._send_json(response)

    def _authorized(self) -> bool:
        if not self.token:
            return True
        return self.headers.get("Authorization", "").strip() == f"Bearer {self.token}"

    def _send_json(self, data: Any, status: int = HTTPStatus.OK) -> None:
        encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, MCP-Protocol-Version")

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[mcp] {self.address_string()} - {fmt % args}", file=sys.stderr)


def run_stdio(app: McpServer) -> None:
    for raw_line in sys.stdin.buffer:
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except Exception:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }
        else:
            response = app.handle_payload(payload)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


def run_http(app: McpServer, host: str, port: int, token: str) -> None:
    McpHttpHandler.app = app
    McpHttpHandler.token = token
    server = ThreadingHTTPServer((host, port), McpHttpHandler)
    print(f"[mcp] Listening on http://{host}:{port}/mcp", file=sys.stderr)
    server.serve_forever()


def run_self_test(app: McpServer) -> None:
    init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": DEFAULT_PROTOCOL_VERSION},
    }
    tools = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    print(_json_dumps(app.handle_payload(init)))
    print(_json_dumps(app.handle_payload(tools)))


def main() -> int:
    parser = argparse.ArgumentParser(description="1PAX chatbot QA MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default=os.environ.get("MCP_TRANSPORT", "stdio"),
        help="MCP transport to run.",
    )
    parser.add_argument("--host", default=os.environ.get("MCP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MCP_PORT", "5057")))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    config = EndpointConfig.from_env()
    app = McpServer(ChatbotQaTools(config))

    if args.self_test:
        run_self_test(app)
        return 0
    if args.transport == "http":
        run_http(app, args.host, args.port, config.http_bearer_token)
    else:
        run_stdio(app)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
