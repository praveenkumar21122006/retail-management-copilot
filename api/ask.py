import json
from http.server import BaseHTTPRequestHandler

from server import answer_question


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
            answer = answer_question(payload.get("question"))
        except (AttributeError, TypeError, ValueError, json.JSONDecodeError):
            self._send_json({"error": "Request body must be valid JSON."}, 400)
            return

        response = {"answer": answer} if answer else {
            "answer": None,
            "message": "I do not have enough data to answer that yet.",
        }
        self._send_json(response)

    def _send_json(self, payload, status=200):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)