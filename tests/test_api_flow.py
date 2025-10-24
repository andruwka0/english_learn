from __future__ import annotations

import pathlib
import sqlite3
import sys
from uuid import UUID

# Ensure the repository root (which contains the ``app`` package) is on sys.path
for candidate in pathlib.Path(__file__).resolve().parents:
    if (candidate / "app").exists():
        sys.path.insert(0, str(candidate))
        break

from app.database import DB_PATH, reset_db
from app.item_bank import ITEMS
from app.service import AdaptiveTestService
from app.session_store import reset_store


def get_correct_answer(item_id: str) -> int | list[int]:
    for item in ITEMS:
        if item.id == item_id:
            if item.model.lower() == "gpcm":
                return list(item.correct_response())
            return item.correct_response()[0]
    raise ValueError(item_id)


def test_full_adaptive_flow() -> None:
    reset_store()
    reset_db()
    test_service = AdaptiveTestService()
    data = test_service.start_test(
        {"start_level": "easy", "first_name": "Ada", "last_name": "Lovelace"}
    )
    test_id = UUID(data["test_id"])

    answered = 0
    while True:
        try:
            item = test_service.get_next_item(test_id)
        except ValueError:
            break
        if item.get("pause"):
            resume = test_service.resume_section(test_id)
            assert "domain" in resume
            continue
        duplicate = test_service.get_next_item(test_id)
        if duplicate.get("pause"):
            test_service.resume_section(test_id)
            duplicate = test_service.get_next_item(test_id)
        assert duplicate["item_id"] == item["item_id"]
        answer_payload = {
            "item_id": item["item_id"],
            "response": {"answer": get_correct_answer(item["item_id"])},
        }
        answer_response = test_service.submit_answer(test_id, answer_payload)
        assert "theta" in answer_response
        answered += 1
        if answer_response["next_part"] is None:
            break

    assert answered > 0
    finish = test_service.finish_test(test_id)
    assert finish["completed"] is True
    report_data = test_service.get_report(test_id)
    assert "cefr" in report_data

    with sqlite3.connect(DB_PATH) as connection:
        row = connection.execute(
            "SELECT first_name, last_name, paused FROM tests WHERE id = ?",
            (str(test_id),),
        ).fetchone()
    assert row is not None
    assert row[0] == "Ada"
    assert row[1] == "Lovelace"
    assert row[2] == 0


def test_listening_play_limit() -> None:
    reset_store()
    reset_db()
    test_service = AdaptiveTestService()
    test_id = UUID(
        test_service.start_test(
            {"start_level": "middle", "first_name": "Test", "last_name": "User"}
        )["test_id"]
    )

    # Advance until we reach listening
    while True:
        item = test_service.get_next_item(test_id)
        if item.get("pause"):
            test_service.resume_section(test_id)
            continue
        if item["domain"] == "listening":
            item_id = item["item_id"]
            break
        payload = {
            "item_id": item["item_id"],
            "response": {"answer": get_correct_answer(item["item_id"])}
        }
        test_service.submit_answer(test_id, payload)

    assert test_service.record_play(test_id, {"item_id": item_id})["plays"] == 1
    assert test_service.record_play(test_id, {"item_id": item_id})["plays"] == 2
    try:
        test_service.record_play(test_id, {"item_id": item_id})
        raise AssertionError("Expected play limit error")
    except ValueError as exc:
        assert str(exc) == "Max plays reached"
