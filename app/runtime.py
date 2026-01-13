"""
app/bootstrap.py

Builds AI runtime once per process.
"""

import logging
from dataclasses import dataclass
from typing import Any

from app.llms.gemini import build_gemini_llm
from app.persistence import CheckpointerResource, create_checkpointer_resource
from app.settings import Settings
from app.workflow.agents.homebrain.graph import GraphConfig, build_graph

log = logging.getLogger(__name__)

type Graph = Any
type LLM = Any


@dataclass
class Runtime:
    settings: Settings
    llm: LLM
    checkpointer_resource: CheckpointerResource
    graph: Graph

    def close(self) -> None:
        self.checkpointer_resource.close()


def create_runtime(settings: Settings) -> Runtime:
    llm = build_gemini_llm(settings)

    checkpointer_resource = create_checkpointer_resource(settings)

    try:
        checkpointer = checkpointer_resource.checkpointer

        cfg = GraphConfig()

        graph = build_graph(llm=llm, checkpointer=checkpointer, cfg=cfg)
        if graph is None:
            raise RuntimeError("create_runtime: build_graph returned None")

        log.info("runtime: ready")
        return Runtime(settings=settings, llm=llm, checkpointer_resource=checkpointer_resource, graph=graph)
    except Exception:
        log.exception("runtime: initialization failed")
        if checkpointer_resource is not None:
            try:
                checkpointer_resource.close()
            except Exception:
                log.exception("runtime: failed to close checkpointer resource after init failure")
        raise
