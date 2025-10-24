"""ASGI entrypoint exposing the FastAPI application for Uvicorn."""
from __future__ import annotations

from app.api import app

__all__ = ["app"]
