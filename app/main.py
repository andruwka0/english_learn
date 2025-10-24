"""Service layer implementing the Adaptive English Level Test logic."""
from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID

from app import schemas
from app.cat_engine import (
    CAT_PARTS,
    Response as ResponseRecord,
    Session,
    Item,
    register_item_bank,
    select_next_item,
    score_response,
    update_theta_map,
    it_lookup,
)
from app.item_bank import ITEMS
from app.session_store import create_session, get_session

register_item_bank(ITEMS)


class AdaptiveTestService:
    """Implements the business rules for the adaptive test."""

    def __init__(self) -> None:
        self._items = ITEMS

    def _get_session(self, test_id: UUID) -> Session:
        try:
            return get_session(test_id)
        except KeyError as exc:  # pragma: no cover - safety net
            raise ValueError("Test session not found") from exc

    def start_test(self, payload: Dict[str, object]) -> Dict[str, object]:
        request = schemas.StartTestRequest.from_dict(payload)
        session = create_session(request.start_level)
        response = schemas.StartTestResponse(
            test_id=UUID(session.id),
            theta=session.theta,
            se=session.se,
            current_part=session.current_domain(),
        )
        return response.to_dict()

    def _ensure_next_item(self, session: Session) -> Item:
        if session.finished:
            raise ValueError("Test already finished")
        item = select_next_item(session, self._items)
        if item is None:
            if session.pending_item_id is not None:
                session.pending_item_id = None
                return self._ensure_next_item(session)
            session.finished = True
            raise ValueError("No more items available")
        return item

    def get_next_item(self, test_id: UUID) -> Dict[str, object]:
        session = self._get_session(test_id)
        item = self._ensure_next_item(session)
        response = schemas.ItemResponse(
            item_id=item.id,
            stem=item.stem,
            options=item.options,
            domain=item.domain,
            model=item.model,
            metadata=item.metadata,
            max_plays=item.max_plays,
        )
        return response.to_dict()

    def submit_answer(self, test_id: UUID, payload: Dict[str, object]) -> Dict[str, object]:
        session = self._get_session(test_id)
        if session.finished:
            raise ValueError("Test already finished")
        request = schemas.AnswerRequest.from_dict(payload)
        item = session.item_history.get(request.item_id)
        if item is None:
            item = it_lookup.get(request.item_id)
        if item is None:
            raise ValueError("Item not found")
        session.item_history[item.id] = item
        score = score_response(item, request.response)
        theta_before = session.theta
        theta_after, se = update_theta_map(session, item, score)
        session.theta = theta_after
        session.se = se
        session.responses.append(
            ResponseRecord(
                item_id=item.id,
                score=score,
                theta_before=theta_before,
                theta_after=theta_after,
                se_after=se,
                raw_response=request.response,
            )
        )
        session.record_domain_progress(item.domain)
        session.pending_item_id = None
        next_part: Optional[str] = None
        if len(session.responses) >= 40 or session.se <= 0.32:
            session.finished = True
        else:
            next_part = session.current_domain()
        response = schemas.AnswerResponse(
            theta=session.theta,
            se=session.se,
            correct=score > 0.0,
            score=score,
            next_part=next_part,
        )
        return response.to_dict()

    def record_play(self, test_id: UUID, payload: Dict[str, object]) -> Dict[str, object]:
        session = self._get_session(test_id)
        request = schemas.PlayRequest.from_dict(payload)
        item = session.item_history.get(request.item_id)
        if item is None:
            item = it_lookup.get(request.item_id)
        if item is None:
            raise ValueError("Item not found")
        if item.domain != "listening":
            raise ValueError("Play tracking applies to listening items only")
        current = session.plays.get(item.id, 0)
        if current >= item.max_plays:
            raise ValueError("Max plays reached")
        current += 1
        session.plays[item.id] = current
        response = schemas.PlayResponse(plays=current, max_plays=item.max_plays)
        return response.to_dict()

    def finish_test(self, test_id: UUID) -> Dict[str, object]:
        session = self._get_session(test_id)
        session.finished = True
        session.pending_item_id = None
        t_score = 50 + 10 * session.theta
        response = schemas.FinishResponse(
            theta=session.theta,
            se=session.se,
            t_score=t_score,
            cefr=self._cefr_level(session.theta),
            completed=True,
        )
        return response.to_dict()

    def get_report(self, test_id: UUID) -> Dict[str, object]:
        session = self._get_session(test_id)
        if not session.finished:
            raise ValueError("Test not finished")
        breakdown = self._summarize_domains(session)
        response = schemas.ReportResponse(
            test_id=test_id,
            theta=session.theta,
            se=session.se,
            t_score=50 + 10 * session.theta,
            cefr=self._cefr_level(session.theta),
            domains=breakdown,
        )
        return response.to_dict()

    @staticmethod
    def _cefr_level(theta: float) -> str:
        if theta < -2.0:
            return "A1"
        if theta < -1.0:
            return "A2"
        if theta < 0.0:
            return "B1"
        if theta < 1.0:
            return "B2"
        if theta < 2.0:
            return "C1"
        return "C2"

    def _summarize_domains(self, session: Session) -> List[schemas.DomainBreakdown]:
        summary: Dict[str, List[float]] = {domain: [] for domain in CAT_PARTS}
        for resp in session.responses:
            item = session.item_history.get(resp.item_id)
            if item is None:
                item = it_lookup.get(resp.item_id)
            if item is None:
                continue
            summary[item.domain].append(resp.score)
        breakdown = []
        for domain, scores in summary.items():
            if not scores:
                continue
            average = sum(scores) / len(scores)
            theta_domain = session.theta + (average - 0.5)
            breakdown.append(
                schemas.DomainBreakdown(
                    domain=domain,
                    average_score=average,
                    cefr=self._cefr_level(theta_domain),
                )
            )
        return breakdown


service = AdaptiveTestService()
