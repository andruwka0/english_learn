"""Minimal ASGI application exposing the adaptive English level test API and UI."""
from __future__ import annotations

from typing import Iterable, Tuple

from .http_router import dispatch


class AdaptiveASGIApp:
    """Lightweight ASGI app that reuses the service layer via :mod:`http_router`."""

    async def __call__(self, scope, receive, send):  # type: ignore[override]
        if scope["type"] != "http":
            await send(
                {
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [(b"content-type", b"text/plain; charset=utf-8")],
                }
            )
            await send({"type": "http.response.body", "body": b"Not found"})
            return

        method = scope.get("method", "GET")
        path = scope.get("path", "/")
        body_chunks = []

        if method in {"POST", "PUT", "PATCH"}:
            while True:
                message = await receive()
                body_chunks.append(message.get("body", b""))
                if not message.get("more_body"):
                    break

        status, headers, body = dispatch(method, path, b"".join(body_chunks))
        if method == "HEAD":
            body = b""

        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": _encode_headers(headers.items()),
            }
        )
        await send({"type": "http.response.body", "body": body})


def _encode_headers(headers: Iterable[Tuple[str, str]]) -> Iterable[Tuple[bytes, bytes]]:
    for key, value in headers:
        yield key.encode("latin-1"), value.encode("latin-1")


def create_app() -> AdaptiveASGIApp:
    return AdaptiveASGIApp()


app = create_app()


__all__ = ["AdaptiveASGIApp", "app", "create_app"]
