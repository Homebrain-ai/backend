"""
app/workflow/nodes/router.py
"""

import logging
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.types import Command, interrupt

from app.schemas.routing import RouteDecision
from app.workflow.agents.homebrain.state import HomebrainState, HomebrainUpdate, Route
from app.workflow.utils.messages import last_human_text

log = logging.getLogger(__name__)


ROUTE_TO_NODE: dict[Route, str] = {
    "personal": "personal_agent",
    "projects": "projects_agent",
    "homelab": "homelab_agent",
    "general": "general_agent",
}

ROUTER_PROMPT = """\
You are a router for a personal assistant.

Choose exactly one route:
- personal: about Pukar (public/professional background)
- projects: about Pukar's software projects
- homelab: about Pukar's homelab/infra
- general: everything else

Set needs_human_review=true if the request asks for private identifiers
(address, phone, DOB, passwords, tokens) or asks for risky/real-world actions.

User message:
{user_message}
"""


def make_router_node(*, llm: BaseChatModel, min_confidence: float = 0.55, interrupt_on_ambiguity: bool = True):
    structured_router = llm.with_structured_output(RouteDecision)

    def router_node(state: HomebrainState) -> Command[str]:
        messages = state.get("messages", [])
        text = last_human_text(messages)

        if not text:
            update: HomebrainUpdate = {
                "route": "general",
                "route_confidence": 0.0,
                "route_reason": "empty_user_message",
                "needs_human_review": True,
            }
            return Command(update=update, goto=ROUTE_TO_NODE["general"])

        decision = classify(structured_router, text)

        if interrupt_on_ambiguity and decision.confidence < min_confidence:
            route = interrupt_for_route(text)
            decision = RouteDecision(
                route=route,
                confidence=0.99,
                reason="user_selected_route",
                needs_human_review=False,
            )

        goto = ROUTE_TO_NODE.get(decision.route, ROUTE_TO_NODE["general"])

        update: HomebrainUpdate = {
            "route": decision.route,
            "route_confidence": float(decision.confidence),
            "route_reason": decision.reason,
            "needs_human_review": bool(decision.needs_human_review),
        }

        return Command(update=update, goto=goto)

    return router_node


# -------------------------
# Helpers
# -------------------------
def classify(structured_router: Any, text: str) -> RouteDecision:
    try:
        decision: RouteDecision = structured_router.invoke(ROUTER_PROMPT.format(user_message=text))

        conf = float(decision.confidence)
        conf = 0.0 if conf < 0.0 else 1.0 if conf > 1.0 else conf

        route: Route = decision.route if decision.route in ROUTE_TO_NODE else "general"
        reason = decision.reason if route == decision.route else "invalid_route_from_model"

        return RouteDecision(
            route=route,
            confidence=conf if route == decision.route else 0.1,
            reason=reason,
            needs_human_review=bool(decision.needs_human_review),
        )
    except Exception:
        log.exception("router: classify failed; falling back to general")
        return RouteDecision(
            route="general",
            confidence=0.1,
            reason="classify_error",
            needs_human_review=False,
        )


def interrupt_for_route(original_text: str) -> Route:
    choice = interrupt(
        {
            "message": "Quick clarification so I route you correctly:",
            "options": ["personal", "projects", "homelab", "general"],
            "original_text": original_text,
        }
    )

    if choice in ("personal", "projects", "homelab", "general"):
        return choice

    return "general"
