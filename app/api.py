"""FastAPI application exposing the adaptive English level test API and demo UI."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.service import AdaptiveTestService


app = FastAPI(title="Adaptive English Level Test")


service = AdaptiveTestService()


class StartPayload(BaseModel):
    start_level: str = Field(..., description="Initial difficulty: easy, middle, or hard")


class AnswerBody(BaseModel):
    answer: Union[int, List[int], None]


class AnswerPayload(BaseModel):
    item_id: str
    response: AnswerBody


class PlayPayload(BaseModel):
    item_id: str


class FinishPayload(BaseModel):
    confirm: bool = Field(default=True)


def _service_call(func, *args, **kwargs) -> Dict[str, Any]:
    try:
        return func(*args, **kwargs)
    except ValueError as exc:  # pragma: no cover - FastAPI error translation
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/test/start")
def start_test(payload: StartPayload) -> Dict[str, Any]:
    return _service_call(service.start_test, payload.dict())


@app.get("/api/test/{test_id}/next")
def get_next_item(test_id: UUID) -> Dict[str, Any]:
    return _service_call(service.get_next_item, test_id)


@app.post("/api/test/{test_id}/answer")
def submit_answer(test_id: UUID, payload: AnswerPayload) -> Dict[str, Any]:
    body = payload.dict()
    return _service_call(service.submit_answer, test_id, body)


@app.post("/api/test/{test_id}/play")
def record_play(test_id: UUID, payload: PlayPayload) -> Dict[str, Any]:
    return _service_call(service.record_play, test_id, payload.dict())


@app.post("/api/test/{test_id}/finish")
def finish_test(test_id: UUID, payload: Optional[FinishPayload] = None) -> Dict[str, Any]:
    if payload is not None and not payload.confirm:
        raise HTTPException(status_code=400, detail="Finish confirmation required")
    return _service_call(service.finish_test, test_id)


@app.get("/api/report/{test_id}")
def get_report(test_id: UUID) -> Dict[str, Any]:
    return _service_call(service.get_report, test_id)


# --- Frontend ----------------------------------------------------------------------------------


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def landing(request: Request) -> HTMLResponse:
    return TEMPLATES.TemplateResponse("index.html", {"request": request})


__all__ = ["app", "service"]
