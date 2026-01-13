"""
app/dependencies/app_state.py

FastAPI dependencies for retrieving app-lifetime objects stored on app.state.

- Consider adding a request context dependency (trace_id/user/tenant).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, Request

from app.bootstrap import Runtime
from app.settings import Settings

type Graph = Any


def require_state_attr(request: Request, attr: str) -> Any:
    """
    Internal helper: fail fast with a clear message if lifespan didn't populate app.state.
    """
    if not hasattr(request.app.state, attr):
        raise RuntimeError(f"app.state.{attr} is missing. Did lifespan() run and initialize it?")
    return getattr(request.app.state, attr)


def get_app_settings(request: Request) -> Settings:
    """
    Return settings stored on app.state by lifespan().
    """
    return require_state_attr(request, "settings")


def get_runtime(request: Request) -> Runtime:
    """
    Return Runtime stored on app.state by lifespan().
    """
    return require_state_attr(request, "runtime")


def get_graph(request: Request) -> Graph:
    """
    Convenience accessor for the compiled LangGraph graph stored in Runtime.
    """
    runtime = get_runtime(request)
    graph = getattr(runtime, "graph", None)
    if graph is None:
        raise RuntimeError("runtime.graph is missing. Runtime may not be initialized correctly.")
    return graph


# ---- Annotated dependency aliases (import these in your routers)

SettingsDep = Annotated[Settings, Depends(get_app_settings)]
RuntimeDep = Annotated[Runtime, Depends(get_runtime)]
GraphDep = Annotated[Graph, Depends(get_graph)]
