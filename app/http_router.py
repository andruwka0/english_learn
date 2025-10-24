"""HTTP routing helpers for the adaptive English level test service."""
from __future__ import annotations

import json
import mimetypes
from pathlib import Path
from typing import Dict, Tuple
from urllib.parse import urlparse
from uuid import UUID

from .service import AdaptiveTestService

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

_service = AdaptiveTestService()


def _json_response(payload: Dict[str, object], status: int = 200) -> Tuple[int, Dict[str, str], bytes]:
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Content-Length": str(len(body)),
    }
    return status, headers, body


def _json_error(message: str, status: int = 400) -> Tuple[int, Dict[str, str], bytes]:
    return _json_response({"detail": message}, status=status)


def _serve_static(path: str) -> Tuple[int, Dict[str, str], bytes]:
    if path in ("", "/"):
        file_path = TEMPLATE_DIR / "index.html"
    elif path.startswith("/static/"):
        candidate = (STATIC_DIR / path[len("/static/") :]).resolve()
        static_root = STATIC_DIR.resolve()
        if not str(candidate).startswith(str(static_root)):
            return _json_error("Not found", status=404)
        file_path = candidate
    else:
        return _json_error("Not found", status=404)

    if not file_path.exists() or not file_path.is_file():
        return _json_error("Not found", status=404)

    content = file_path.read_bytes()
    content_type, _ = mimetypes.guess_type(str(file_path))
    headers = {
        "Content-Type": (content_type or "application/octet-stream"),
        "Content-Length": str(len(content)),
    }
    return 200, headers, content


def _parse_json_body(body: bytes) -> Dict[str, object]:
    if not body:
        return {}
    try:
        return json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise ValueError("Invalid JSON body") from exc


def dispatch(method: str, raw_path: str, body: bytes) -> Tuple[int, Dict[str, str], bytes]:
    """Dispatch an HTTP request and return a status, headers, and body."""
    path = urlparse(raw_path).path

    if not path.startswith("/api/"):
        return _serve_static(path)

    parts = [part for part in path.strip("/").split("/") if part]
    if len(parts) < 2 or parts[0] != "api":
        return _json_error("Not found", status=404)

    if parts[1] == "test":
        if len(parts) == 3 and parts[2] == "start":
            if method != "POST":
                return _json_error("Method not allowed", status=405)
            try:
                payload = _parse_json_body(body)
                response = _service.start_test(payload)
                return _json_response(response)
            except ValueError as exc:
                return _json_error(str(exc))

        if len(parts) >= 4:
            test_id_str = parts[2]
            try:
                test_id = UUID(test_id_str)
            except ValueError:
                return _json_error("Invalid test id")

            action = parts[3]
            if action == "next" and len(parts) == 4:
                if method != "GET":
                    return _json_error("Method not allowed", status=405)
                try:
                    data = _service.get_next_item(test_id)
                    return _json_response(data)
                except ValueError as exc:
                    return _json_error(str(exc), status=404)

            if action == "answer" and len(parts) == 4:
                if method != "POST":
                    return _json_error("Method not allowed", status=405)
                try:
                    payload = _parse_json_body(body)
                    data = _service.submit_answer(test_id, payload)
                    return _json_response(data)
                except ValueError as exc:
                    return _json_error(str(exc))

            if action == "play" and len(parts) == 4:
                if method != "POST":
                    return _json_error("Method not allowed", status=405)
                try:
                    payload = _parse_json_body(body)
                    data = _service.record_play(test_id, payload)
                    return _json_response(data)
                except ValueError as exc:
                    return _json_error(str(exc))

            if action == "finish" and len(parts) == 4:
                if method != "POST":
                    return _json_error("Method not allowed", status=405)
                try:
                    payload = _parse_json_body(body)
                    if payload and not payload.get("confirm", True):
                        return _json_error("Finish confirmation required")
                    data = _service.finish_test(test_id)
                    return _json_response(data)
                except ValueError as exc:
                    return _json_error(str(exc))

    if parts[1] == "report" and len(parts) == 3:
        if method != "GET":
            return _json_error("Method not allowed", status=405)
        try:
            test_id = UUID(parts[2])
        except ValueError:
            return _json_error("Invalid test id")
        try:
            data = _service.get_report(test_id)
            return _json_response(data)
        except ValueError as exc:
            return _json_error(str(exc))

    return _json_error("Not found", status=404)


__all__ = ["dispatch"]
