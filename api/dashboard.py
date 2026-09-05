import json
from http.server import BaseHTTPRequestHandler

from server import DASHBOARD


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        payload = json.dumps(DASHBOARD, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
