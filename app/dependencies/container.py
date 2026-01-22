"""
app/dependencies/app_state.py

FastAPI dependencies for retrieving app-lifetime objects stored on app.state.

- Consider adding a request context dependency (trace_id/user/tenant).
"""

from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import Depends, Request

from app.runtime import Runtime
from app.settings import Settings

type Graph = Any


@dataclass(frozen=True, slots=True)
class AppState:
    settings: Settings
    runtime: Runtime

    @property
    def graph(self) -> Graph:
        graph = getattr(self.runtime, "graph", None)
        if graph is None:
            raise RuntimeError("state.runtime.graph is missing. Runtime may not be initialized correctly.")
        return graph


def get_state(request: Request) -> AppState:
    try:
        return request.app.state.container
    except AttributeError as e:
        raise RuntimeError("app.state.container is missing. Did lifespan() run and initialize it?") from e


def get_app_settings(request: Request) -> Settings:
    return get_state(request).settings


def get_runtime(request: Request) -> Runtime:
    return get_state(request).runtime


def get_graph(request: Request) -> Graph:
    return get_state(request).graph


SettingsDep = Annotated[Settings, Depends(get_app_settings)]
RuntimeDep = Annotated[Runtime, Depends(get_runtime)]
GraphDep = Annotated[Graph, Depends(get_graph)]
StateDep = Annotated[AppState, Depends(get_state)]
