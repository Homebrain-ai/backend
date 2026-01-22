"""
app/workflow/nodes/ingest.py
"""

import logging

from app.workflow.agents.homebrain.state import HomebrainState, HomebrainUpdate
from app.workflow.utils.messages import last_human_text

log = logging.getLogger(__name__)


def ingest(state: HomebrainState) -> HomebrainUpdate:
    messages = state.get("messages", [])
    last_user_txt = last_human_text(messages)

    update: HomebrainUpdate = {
        "error": None,
        "retrieved_context": "",
        "tool_results": {},
        "route_reason": "",
        "route_confidence": 0.0,
        "needs_human_review": False,
    }

    if not last_user_txt:
        log.warning("ingest: empty last user message", extra={"messages_count": len(messages)})
        update["error"] = "Empty user message"
        update["needs_human_review"] = True

    return update
