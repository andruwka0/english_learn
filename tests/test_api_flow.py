from __future__ import annotations

import pathlib
import sys
from uuid import UUID

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from app.item_bank import ITEMS
from app.main import AdaptiveTestService
from app.session_store import reset_store


def get_correct_answer(item_id: str) -> int | list[int]:
    for item in ITEMS:
        if item.id == item_id:
            if item.model.lower() == "gpcm":
                return list(item.correct_response())
            return item.correct_response()[0]
    raise ValueError(item_id)


def test_full_adaptive_flow():
    reset_store()
    test_service = AdaptiveTestService()
    data = test_service.start_test({"start_level": "easy"})
    test_id = UUID(data["test_id"])

    for _ in range(len(ITEMS)):
        item = test_service.get_next_item(test_id)
        duplicate = test_service.get_next_item(test_id)
        assert duplicate["item_id"] == item["item_id"]
        answer_payload = {"item_id": item["item_id"], "response": {"answer": get_correct_answer(item["item_id"])}}
        answer_response = test_service.submit_answer(test_id, answer_payload)
        assert "theta" in answer_response

    finish = test_service.finish_test(test_id)
    assert finish["completed"] is True
    report_data = test_service.get_report(test_id)
    assert "cefr" in report_data


def test_listening_play_limit():
    reset_store()
    test_service = AdaptiveTestService()
    test_id = UUID(test_service.start_test({"start_level": "middle"})["test_id"])

    # Advance until we reach listening
    while True:
        item = test_service.get_next_item(test_id)
        if item["domain"] == "listening":
            item_id = item["item_id"]
            break
        test_service.submit_answer(test_id, {"item_id": item["item_id"], "response": {"answer": get_correct_answer(item["item_id"])}})

    assert test_service.record_play(test_id, {"item_id": item_id})["plays"] == 1
    assert test_service.record_play(test_id, {"item_id": item_id})["plays"] == 2
    try:
        test_service.record_play(test_id, {"item_id": item_id})
        raise AssertionError("Expected play limit error")
    except ValueError as exc:
        assert str(exc) == "Max plays reached"
