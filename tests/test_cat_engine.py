from __future__ import annotations

from uuid import uuid4

import pathlib
import sys

for candidate in pathlib.Path(__file__).resolve().parents:
    if (candidate / "app").exists():
        sys.path.insert(0, str(candidate))
        break

from app.cat_engine import (
    Item,
    Response,
    Session,
    register_item_bank,
    update_theta_map,
)
from app.item_bank import ITEMS


def test_update_theta_map_improves_theta_for_correct_answer():
    original_theta = 0.0
    session = Session(
        id=str(uuid4()),
        start_level="middle",
        theta=original_theta,
        prior_mu=0.0,
        prior_sigma=1.0,
        se=1.0,
    )

    item = Item(
        id="diagnostic-3pl",
        domain="vocabulary",
        stem="Choose the synonym for 'rapid'.",
        options=["quick", "slow", "late", "calm"],
        correct_key=0,
        model="3PL",
        irt_a=1.2,
        irt_b=0.3,
        irt_c=0.2,
    )

    register_item_bank([item])

    try:
        theta, se = update_theta_map(session, item, 1.0)
    finally:
        register_item_bank(ITEMS)

    assert theta > original_theta
    assert se != float("inf")


def test_update_theta_map_uses_session_history_when_bank_changes():
    session = Session(
        id=str(uuid4()),
        start_level="middle",
        theta=0.2,
        prior_mu=0.0,
        prior_sigma=1.0,
        se=1.0,
    )

    prior_item = Item(
        id="history-item",
        domain="grammar",
        stem="Select the correct verb form.",
        options=["go", "goes", "gone", "going"],
        correct_key=1,
        model="2PL",
        irt_a=1.0,
        irt_b=-0.2,
    )
    session.item_history[prior_item.id] = prior_item
    session.responses.append(
        Response(
            item_id=prior_item.id,
            score=1.0,
            theta_before=0.0,
            theta_after=0.3,
            se_after=0.5,
        )
    )

    current_item = Item(
        id="current-item",
        domain="grammar",
        stem="Choose the correct auxiliary.",
        options=["do", "does", "did", "done"],
        correct_key=1,
        model="2PL",
        irt_a=1.1,
        irt_b=0.5,
    )

    register_item_bank([current_item])

    try:
        theta, se = update_theta_map(session, current_item, 0.0)
    finally:
        register_item_bank(ITEMS)

    assert theta is not None
    assert se != float("inf")
