#!/usr/bin/env python3
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
PORT = int(os.environ.get("PORT", "3000"))

DASHBOARD = {
    "syncedAt": "Today at 08:42",
    "stores": 3,
    "products": 642,
    "metrics": {"sales": "$48,290", "salesChange": "8.4%", "units": "2,847", "unitsChange": "4.1%", "stockValue": "$31,640", "stockChange": "0.6%", "attention": 8, "urgent": 3},
    "attention": [
        {"product": "Matcha Starter Kit", "type": "Likely stock-out", "store": "High Street", "summary": "4 units left · 9 sold in last 7 days", "evidence": [["Runs out in", "2 days"], ["7-day velocity", "1.3/day"], ["Reorder point", "6 units"]], "action": "Reorder", "question": "What should I reorder first?", "tone": "urgent"},
        {"product": "Linen Market Tote", "type": "Not moving", "store": "Riverside", "summary": "38 units on hand · 2 sold in last 30 days", "evidence": [["Cover", "570 days"], ["Last sale", "14 days ago"], ["Stock value", "$1,140"]], "action": "Review stock", "question": "What is overstocked?", "tone": "warning"},
        {"product": "Cloudberry Candle · 220g", "type": "Sales spike", "store": "All stores", "summary": "31 sold this week · up from 18 last week", "evidence": [["Week over week", "+72%"], ["Highest store", "Riverside"], ["Units left", "24"]], "action": "Investigate", "question": "What changed in sales this week?", "tone": "trend"},
        {"product": "Salted Caramel Biscuit", "type": "Sales drop", "store": "Station kiosk", "summary": "6 sold this week · down from 15 last week", "evidence": [["Week over week", "−60%"], ["On hand", "42 units"], ["Price changed", "No"]], "action": "Investigate", "question": "What sales dropped this week?", "tone": "drop"},
    ],
    "pulse": [{"store": "High Street", "status": "Healthy", "rate": 78, "tone": "good"}, {"store": "Riverside", "status": "Watch", "rate": 61, "tone": "watch"}, {"store": "Station kiosk", "status": "Healthy", "rate": 86, "tone": "good"}],
}

ANSWERS = [
    {"matches": ["run", "stock-out", "reorder"], "title": "Matcha Starter Kit is closest to a stock-out.", "body": "At the current sales pace, High Street has about <span class=\"answer-number\">2 days</span> of cover left. A reorder now protects the weekend demand window.", "rows": [["On hand", "4 units"], ["7-day sales", "9 units"], ["Daily velocity", "1.3 units"], ["Reorder point", "6 units"]], "recommendation": "Order 12 units from your usual supplier. This covers 9 days of demand plus a 3-unit buffer.", "assumption": "Assumption: next 7 days follow the last 7 days; no incoming stock included."},
    {"matches": ["overstock", "not moving", "excess"], "title": "Linen Market Tote has the most excess stock.", "body": "Riverside holds <span class=\"answer-number\">38 units</span>, but only 2 sold in the last 30 days. That is roughly <span class=\"answer-number\">570 days of cover</span>.", "rows": [["On hand", "38 units"], ["30-day sales", "2 units"], ["Stock value", "$1,140"], ["Last sale", "14 days ago"]], "recommendation": "Move 12 units to High Street and test a 15% markdown on the remaining Riverside stock.", "assumption": "Cover uses the last 30 days of sales and assumes no change in demand."},
    {"matches": ["matcha", "product", "month"], "title": "Matcha Starter Kit is up 18% this month.", "body": "It sold <span class=\"answer-number\">42 units</span> for <span class=\"answer-number\">$1,680</span> across all stores, compared with 36 units in August.", "rows": [["This month", "42 units"], ["Last month", "36 units"], ["Revenue", "$1,680"], ["Best store", "High Street · 21 units"]], "recommendation": "Keep the product in the front display at High Street and replenish before the weekend.", "assumption": "Based on recorded sales through 05 Sep 2026; returns and transfers excluded."},
    {"matches": ["drop", "down"], "title": "Salted Caramel Biscuit is down 60%.", "body": "Station kiosk sold <span class=\"answer-number\">6 units</span> this week versus 15 last week. There was no price change, with 42 units still on hand.", "rows": [["This week", "6 units"], ["Last week", "15 units"], ["Change", "−9 units"], ["On hand", "42 units"]], "recommendation": "Check kiosk placement and expiry dates today before discounting. The data does not identify a cause.", "assumption": "Price history and stock counts are available; customer traffic data is not."},
    {"matches": ["spike", "changed", "sales"], "title": "Cloudberry Candle is the standout spike.", "body": "It sold <span class=\"answer-number\">31 units</span> this week versus 18 last week, a <span class=\"answer-number\">72% increase</span>. Riverside contributed 19 units.", "rows": [["This week", "31 units"], ["Last week", "18 units"], ["Change", "+13 units"], ["Remaining stock", "24 units"]], "recommendation": "Check the Riverside display and place a small replenishment order before the current 24 units are gone.", "assumption": "Weeks are Monday-Sunday; current week is partial through Saturday morning."},
]


def answer_for(question):
    text = str(question or "").lower()
    return next((answer for answer in ANSWERS if any(term in text for term in answer["matches"])), None)


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/api/dashboard":
            self.send_json(200, DASHBOARD)
            return
        requested = urlparse(self.path).path
        file_path = (ROOT / ("index.html" if requested == "/" else requested.lstrip("/"))).resolve()
        if ROOT not in file_path.parents and file_path != ROOT or not file_path.is_file():
            self.send_error(404, "Not found")
            return
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/api/ask":
            self.send_error(404, "Not found")
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
            answer = answer_for(payload.get("question"))
            self.send_json(200, {"answer": answer} if answer else {"answer": None, "message": "I do not have enough data to answer that yet."})
        except (ValueError, json.JSONDecodeError, AttributeError):
            self.send_json(400, {"error": "Request body must be valid JSON."})

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}")


if __name__ == "__main__":
    print(f"Ledger & Loom running at http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
