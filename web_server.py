"""Local web frontend server for the Mini-C compiler."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src.minic.lexer import LexicalError
from src.minic.parser import ParseError
from src.minic.pipeline import format_stage_output, run_pipeline
from src.minic.semantic import SemanticError


ROOT = Path(__file__).parent.resolve()
WEB_DIR = ROOT / "web"
VALID_STAGES = {"output", "tokens", "ast", "symbols", "tac", "all"}


class MiniCRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_POST(self) -> None:
        if self.path != "/api/compile":
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")
            return

        try:
            payload = self._read_json()
            source = payload.get("source", "")
            stage = payload.get("stage", "all")
            if stage not in VALID_STAGES:
                raise ValueError(f"Unknown compiler stage: {stage}")

            result = run_pipeline(source)
            output = format_stage_output(result, stage)
            self._send_json({"ok": True, "output": output})
        except (LexicalError, ParseError, SemanticError, ValueError) as error:
            self._send_json({"ok": False, "output": str(error)}, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError:
            self._send_json({"ok": False, "output": "Invalid JSON request."}, status=HTTPStatus.BAD_REQUEST)

    def _read_json(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        return json.loads(raw_body.decode("utf-8"))

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Mini-C compiler web frontend")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), MiniCRequestHandler)
    print(f"Mini-C compiler frontend running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()

    return 0
#cd "Compiler-main"
#python minic.py examples/valid_program.mc --all 
# python web_server.py

if __name__ == "__main__":
    raise SystemExit(main())

