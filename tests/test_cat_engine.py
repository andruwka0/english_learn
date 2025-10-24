from __future__ import annotations

from uuid import uuid4

from app.cat_engine import (
    Item,
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
