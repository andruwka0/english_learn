"""ASGI entrypoint exposing the adaptive English level test application."""
from __future__ import annotations

from .api import create_app

app = create_app()


def main() -> None:
    from .server import main as server_main

    server_main()


if __name__ == "__main__":
    main()


__all__ = ["app", "main"]
