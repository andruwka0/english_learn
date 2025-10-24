"""Standard library HTTP server for the adaptive English level test UI and API."""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Tuple
from urllib.parse import urlsplit

from .http_router import dispatch


class AdaptiveHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802 - HTTP verb method name
        self._handle_request()

    def do_POST(self) -> None:  # noqa: N802 - HTTP verb method name
        self._handle_request()

    def do_HEAD(self) -> None:  # noqa: N802 - HTTP verb method name
        self._handle_request(send_body=False)

    def _handle_request(self, send_body: bool = True) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length > 0 else b""
        status, headers, content = dispatch(self.command, urlsplit(self.path).path, body)
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        if "Content-Length" not in headers:
            self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        if send_body and content:
            self.wfile.write(content)

    def log_message(self, format: str, *args) -> None:  # pragma: no cover - diagnostic output
        print(f"[HTTP] {self.log_date_time_string()} - {format % args}")


def run(host: str = "127.0.0.1", port: int = 8000) -> Tuple[str, int]:
    """Start the development server and return the host/port in use."""
    server = ThreadingHTTPServer((host, port), AdaptiveHTTPRequestHandler)
    address = server.server_address
    print(f"Serving adaptive test UI on http://{address[0]}:{address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - manual shutdown
        print("\nStopping server…")
    finally:
        server.server_close()
    return address


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the adaptive English level test server")
    parser.add_argument("--host", default="127.0.0.1", help="Hostname to bind (default: 127.0.0.1)")
    parser.add_argument("--port", default=8000, type=int, help="Port to bind (default: 8000)")
    args = parser.parse_args()
    run(args.host, args.port)


if __name__ == "__main__":
    main()
