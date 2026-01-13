"""
app/main.py
"""

import logging

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.lifespan import lifespan

log = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Homebrain Backend",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    app.include_router(chat_router)
    return app


app = create_app()
