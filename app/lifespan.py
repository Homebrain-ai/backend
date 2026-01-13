"""
app/lifespan.py

Stores resources in app.state
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.bootstrap import Runtime, create_runtime
from app.db.core import Base, SQLengine
from app.settings import get_settings

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    app.state.settings = settings

    log.info("startup: starting", extra={"env": getattr(settings, "env", None)})

    runtime: Runtime | None = None
    try:
        log.info("startup: creating database tables")
        # Dev-only. In prod, use Alembic migrations (Gate behind a setting later).
        Base.metadata.create_all(bind=SQLengine)

        runtime = create_runtime(settings)
        app.state.runtime = runtime

        yield

    finally:
        if runtime is not None:
            try:
                runtime.close()
            except Exception:
                log.exception("shutdown: failed to close runtime")

        try:
            SQLengine.dispose()
        except Exception:
            log.exception("shutdown: failed to dispose SQL engine")
