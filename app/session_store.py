"""In-memory storage for test sessions."""
from __future__ import annotations

from typing import Dict
from uuid import UUID, uuid4

from app.cat_engine import Session

LEVEL_PRIORS = {
    "easy": (-1.5, 1.0),
    "middle": (0.0, 1.0),
    "hard": (1.5, 1.0),
}


def create_session(start_level: str) -> Session:
    mu, sigma2 = LEVEL_PRIORS[start_level]
    session = Session(
        id=str(uuid4()),
        start_level=start_level,
        theta=mu,
        prior_mu=mu,
        prior_sigma=sigma2 ** 0.5,
        se=float("inf"),
    )
    _SESSIONS[UUID(session.id)] = session
    return session


def get_session(session_id: UUID) -> Session:
    if session_id not in _SESSIONS:
        raise KeyError("Session not found")
    return _SESSIONS[session_id]


def finish_session(session_id: UUID) -> None:
    session = get_session(session_id)
    session.finished = True


def reset_store() -> None:
    _SESSIONS.clear()


_SESSIONS: Dict[UUID, Session] = {}
