"""
app/agents/homebrain/graph.py
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from app.workflow.agents.homebrain.state import HomebrainState
from app.workflow.nodes.finalize import finalize
from app.workflow.nodes.ingest import ingest
from app.workflow.nodes.router import make_router_node

# Import nodes: ingest, router, finalize
# Import agents + prompts: personal, projects, homelab, general


@dataclass(frozen=True)
class GraphConfig:
    min_confidence: float = 0.55
    interrupt_on_ambiguity: bool = True

    personal_tools: Sequence[Any] = field(default_factory=tuple)
    projects_tools: Sequence[Any] = field(default_factory=tuple)
    homelab_tools: Sequence[Any] = field(default_factory=tuple)
    general_tools: Sequence[Any] = field(default_factory=tuple)

    homelab_interrupt_on: Mapping[str, Any] = field(default_factory=dict)


def build_graph(*, llm: BaseChatModel, checkpointer: Any, cfg: GraphConfig | None = None):
    """
    Parent graph: ingest → router → specialist → finalize
    """
    if cfg is None:
        cfg = GraphConfig()

    router_node = make_router_node(
        llm=llm,
        min_confidence=cfg.min_confidence,
        interrupt_on_ambiguity=cfg.interrupt_on_ambiguity,
    )

    g = StateGraph(HomebrainState)

    router_retry = RetryPolicy(max_attempts=2, initial_interval=0.5)

    g.add_node("ingest", ingest)
    g.add_node("router", router_node, retry_policy=router_retry)
    g.add_node("finalize", finalize)

    g.add_edge(START, "ingest")
    g.add_edge("ingest", "router")

    g.add_edge("finalize", END)

    return g.compile(checkpointer=checkpointer)
