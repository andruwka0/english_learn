"""Core CAT engine utilities implementing IRT calculations and adaptive item selection."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence
import math


CAT_PARTS = ["vocabulary", "grammar", "listening", "english_in_use"]


@dataclass
class Item:
    """Representation of a single test item from the bank."""

    id: str
    domain: str
    stem: str
    options: List[str]
    correct_key: Sequence[int] | int
    model: str
    irt_a: float
    irt_b: float
    irt_c: float = 0.0
    max_plays: int = 0
    metadata: Dict[str, str] | None = None
    step_difficulties: Optional[List[float]] = None

    def correct_response(self) -> Sequence[int]:
        if isinstance(self.correct_key, Sequence) and not isinstance(self.correct_key, (str, bytes)):
            return tuple(int(v) for v in self.correct_key)
        return (int(self.correct_key),)


@dataclass
class Response:
    item_id: str
    score: float
    theta_before: float
    theta_after: float
    se_after: float
    raw_response: Dict[str, object] | None = None


@dataclass
class Session:
    id: str
    start_level: str
    theta: float
    prior_mu: float
    prior_sigma: float
    se: float
    part_index: int = 0
    finished: bool = False
    responses: List[Response] = field(default_factory=list)
    plays: Dict[str, int] = field(default_factory=dict)
    seen_items: set[str] = field(default_factory=set)
    pending_item_id: Optional[str] = None

    def current_domain(self) -> str:
        return CAT_PARTS[self.part_index]

    def advance_part(self) -> None:
        if self.part_index < len(CAT_PARTS) - 1:
            self.part_index += 1
            self.pending_item_id = None
        else:
            self.finished = True
            self.pending_item_id = None


def logistic_2pl(theta: float, a: float, b: float) -> float:
    """Probability of success for the 2PL model."""
    exponent = -a * (theta - b)
    if exponent > 30:  # prevent overflow
        return 0.0
    if exponent < -30:
        return 1.0
    return 1.0 / (1.0 + math.exp(exponent))


def logistic_3pl(theta: float, a: float, b: float, c: float) -> float:
    base = logistic_2pl(theta, a, b)
    return c + (1.0 - c) * base


def gpcm_probabilities(item: Item, theta: float) -> List[float]:
    if not item.step_difficulties:
        steps = [item.irt_b + (idx - 0.5) * 0.2 for idx in range(len(item.correct_response()))]
    else:
        steps = list(item.step_difficulties)
    eta = [0.0]
    cumulative = 0.0
    for step in steps:
        cumulative += item.irt_a * (theta - step)
        eta.append(cumulative)
    exps = [math.exp(value) for value in eta]
    denom = sum(exps)
    if denom == 0:
        return [1.0 / len(exps)] * len(exps)
    return [value / denom for value in exps]


def fisher_information(item: Item, theta: float) -> float:
    if item.model.lower() == "3pl":
        p = logistic_3pl(theta, item.irt_a, item.irt_b, item.irt_c)
        q = 1.0 - p
        numerator = (p - item.irt_c) ** 2
        denom = (1.0 - item.irt_c) ** 2
        return (item.irt_a ** 2) * (numerator / denom) * (q / p)
    if item.model.lower() == "2pl":
        p = logistic_2pl(theta, item.irt_a, item.irt_b)
        q = 1.0 - p
        return (item.irt_a ** 2) * p * q
    if item.model.lower() == "gpcm":
        # approximate using variance of score categories
        probs = gpcm_probabilities(item, theta)
        mean = sum(score * prob for score, prob in enumerate(probs))
        variance = sum(((score - mean) ** 2) * prob for score, prob in enumerate(probs))
        return item.irt_a ** 2 * variance
    raise ValueError(f"Unsupported model: {item.model}")


def log_likelihood_derivatives(
    theta: float,
    responses: Iterable[tuple[Item, float]],
) -> tuple[float, float]:
    first = 0.0
    second = 0.0
    for item, score in responses:
        model = item.model.lower()
        if model in {"2pl", "3pl"}:
            p = logistic_3pl(theta, item.irt_a, item.irt_b, item.irt_c) if model == "3pl" else logistic_2pl(theta, item.irt_a, item.irt_b)
            q = 1.0 - p
            d1 = item.irt_a * (score - p) / (p * (1.0 - item.irt_c)) if model == "3pl" else item.irt_a * (score - p)
            d2 = - (item.irt_a ** 2) * (q * (1.0 - 2 * p))
        elif model == "gpcm":
            probs = gpcm_probabilities(item, theta)
            expected = sum(idx * prob for idx, prob in enumerate(probs))
            variance = sum(((idx - expected) ** 2) * prob for idx, prob in enumerate(probs))
            d1 = item.irt_a * (score - expected)
            d2 = - (item.irt_a ** 2) * variance
        else:
            raise ValueError(f"Unsupported model: {item.model}")
        first += d1
        second += d2
    return first, second


def update_theta_map(
    session: Session,
    item: Item,
    score: float,
    max_iter: int = 25,
    tolerance: float = 1e-4,
) -> tuple[float, float]:
    theta = session.theta
    responses = [(it, resp.score) for resp in session.responses for it in [it_lookup[resp.item_id]]] + [(item, score)]
    for _ in range(max_iter):
        ll1, ll2 = log_likelihood_derivatives(theta, responses)
        prior1 = (session.prior_mu - theta) / (session.prior_sigma ** 2)
        prior2 = -1.0 / (session.prior_sigma ** 2)
        numerator = ll1 + prior1
        denominator = ll2 + prior2
        if abs(denominator) < 1e-6:
            break
        theta_new = theta - numerator / denominator
        if abs(theta_new - theta) < tolerance:
            theta = theta_new
            break
        theta = theta_new
    info = sum(fisher_information(it, theta) for it, _ in responses)
    if info <= 0:
        se = float("inf")
    else:
        se = 1.0 / math.sqrt(info)
    return theta, se


it_lookup: Dict[str, Item] = {}


def register_item_bank(items: Iterable[Item]) -> None:
    it_lookup.clear()
    for item in items:
        it_lookup[item.id] = item


def select_next_item(session: Session, candidate_items: Iterable[Item]) -> Optional[Item]:
    if session.pending_item_id:
        return it_lookup.get(session.pending_item_id)
    domain_items = [item for item in candidate_items if item.domain == session.current_domain() and item.id not in session.seen_items]
    if not domain_items:
        # advance to next part if possible
        session.advance_part()
        if session.finished:
            return None
        return select_next_item(session, candidate_items)
    best_item = max(domain_items, key=lambda item: fisher_information(item, session.theta))
    session.seen_items.add(best_item.id)
    session.pending_item_id = best_item.id
    return best_item


def score_response(item: Item, response: Dict[str, object]) -> float:
    model = item.model.lower()
    if model in {"2pl", "3pl"}:
        answer = int(response.get("answer"))
        return 1.0 if answer in item.correct_response() else 0.0
    if model == "gpcm":
        raw = response.get("answer")
        if not isinstance(raw, list):
            raw = [raw]
        correct_set = set(item.correct_response())
        awarded = 0
        seen: set[int] = set()
        for value in raw:
            if value is None:
                continue
            idx = int(value)
            if idx in correct_set and idx not in seen:
                awarded += 1
                seen.add(idx)
        return float(awarded)
    raise ValueError(f"Unsupported model: {item.model}")
