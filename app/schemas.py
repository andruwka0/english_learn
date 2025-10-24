"""Lightweight dataclass-based schemas used by the service layer."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from uuid import UUID

from app.cat_engine import CAT_PARTS, DOMAIN_TARGETS


def dataclass_from_dict(cls, data):
    field_names = {field.name for field in cls.__dataclass_fields__.values()}
    filtered = {key: data[key] for key in data if key in field_names}
    instance = cls(**filtered)
    if hasattr(instance, "__post_init__"):
        instance.__post_init__()
    return instance


@dataclass
class StartTestRequest:
    start_level: str
    first_name: str
    last_name: str

    def __post_init__(self) -> None:
        normalized = self.start_level.lower()
        if normalized not in {"easy", "middle", "hard"}:
            raise ValueError("start_level must be one of easy/middle/hard")
        self.start_level = normalized
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()
        if not self.first_name or not self.last_name:
            raise ValueError("first_name and last_name are required")

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "StartTestRequest":
        return dataclass_from_dict(cls, data)


@dataclass
class StartTestResponse:
    test_id: UUID
    theta: float
    se: float
    current_part: str
    paused: bool
    upcoming_part: Optional[str]

    def to_dict(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["test_id"] = str(self.test_id)
        return payload


DOMAIN_LENGTHS: Dict[str, int] = {part: DOMAIN_TARGETS.get(part, 0) for part in CAT_PARTS}


@dataclass
class ItemResponse:
    item_id: str
    stem: str
    options: List[str]
    domain: str
    model: str
    metadata: Optional[Dict[str, str]] = None
    max_plays: int = 0

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class AnswerRequest:
    item_id: str
    response: Dict[str, object]

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "AnswerRequest":
        return dataclass_from_dict(cls, data)


@dataclass
class AnswerResponse:
    theta: float
    se: float
    correct: bool
    score: float
    next_part: Optional[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class PauseResponse:
    pause: bool = field(default=True, init=False)
    domain: str = ""
    message: str = ""
    questions: int = 0

    def to_dict(self) -> Dict[str, object]:
        return {"pause": True, "domain": self.domain, "message": self.message, "questions": self.questions}


@dataclass
class ResumeResponse:
    domain: str

    def to_dict(self) -> Dict[str, object]:
        return {"domain": self.domain}


@dataclass
class PlayRequest:
    item_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "PlayRequest":
        return dataclass_from_dict(cls, data)


@dataclass
class PlayResponse:
    plays: int
    max_plays: int

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class FinishResponse:
    theta: float
    se: float
    t_score: float
    cefr: str
    completed: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(order=True)
class DomainBreakdown:
    sort_index: int = field(init=False, repr=False)
    domain: str
    average_score: float
    cefr: str

    def __post_init__(self) -> None:
        order = {name: index for index, name in enumerate(CAT_PARTS)}
        self.sort_index = order.get(self.domain, 99)

    def to_dict(self) -> Dict[str, object]:
        return {"domain": self.domain, "average_score": self.average_score, "cefr": self.cefr}


@dataclass
class ReportResponse:
    test_id: UUID
    theta: float
    se: float
    t_score: float
    cefr: str
    domains: List[DomainBreakdown]

    def to_dict(self) -> Dict[str, object]:
        sorted_domains = sorted(self.domains)
        return {
            "test_id": str(self.test_id),
            "theta": self.theta,
            "se": self.se,
            "t_score": self.t_score,
            "cefr": self.cefr,
            "domains": [domain.to_dict() for domain in sorted_domains],
        }
