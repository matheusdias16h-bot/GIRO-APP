import json
import os
import sqlite3
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("GIRO_DB_PATH", BASE_DIR / "giro_data.sqlite"))
INDEX_PATH = BASE_DIR / "index.html"
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

DEFAULT_SETTINGS = {
    "monthlyGoal": 10000,
    "initialCapital": 0,
    "facebookCity": "",
}


def db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state (
                key TEXT PRIMARY KEY,
                payload TEXT NOT NULL
            )
            """
        )


def get_state():
    with db_connection() as conn:
        products_row = conn.execute("SELECT payload FROM app_state WHERE key = 'products'").fetchone()
        settings_row = conn.execute("SELECT payload FROM app_state WHERE key = 'settings'").fetchone()
    products = json.loads(products_row["payload"]) if products_row else []
    settings = DEFAULT_SETTINGS.copy()
    if settings_row:
        settings.update(json.loads(settings_row["payload"]))
    updated_row = None
    with db_connection() as conn:
        updated_row = conn.execute("SELECT payload FROM app_state WHERE key = 'updated_at'").fetchone()
    return {
        "products": products,
        "settings": settings,
        "updatedAt": json.loads(updated_row["payload"]) if updated_row else None,
    }


def save_state(payload):
    products = payload.get("products", [])
    settings = DEFAULT_SETTINGS.copy()
    settings.update(payload.get("settings", {}))
    if not isinstance(products, list):
        raise ValueError("products precisa ser uma lista")
    with db_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO app_state (key, payload) VALUES ('products', ?)",
            (json.dumps(products, ensure_ascii=False),),
        )
        conn.execute(
            "INSERT OR REPLACE INTO app_state (key, payload) VALUES ('settings', ?)",
            (json.dumps(settings, ensure_ascii=False),),
        )
        updated_at = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT OR REPLACE INTO app_state (key, payload) VALUES ('updated_at', ?)",
            (json.dumps(updated_at),),
        )
    return {"products": products, "settings": settings, "updatedAt": updated_at}


class AppHandler(BaseHTTPRequestHandler):
    server_version = "GiroApp/1.0"

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/data":
            return self.send_json(HTTPStatus.OK, get_state())
        if parsed.path in {"/", "/index.html"} or "." not in Path(parsed.path).name:
            return self.serve_file(INDEX_PATH, "text/html; charset=utf-8")
        return self.send_error_json(HTTPStatus.NOT_FOUND, "Rota nao encontrada")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/data":
            return self.send_error_json(HTTPStatus.NOT_FOUND, "Rota nao encontrada")
        payload = self.read_json()
        if payload is None:
            return
        try:
            state = save_state(payload)
        except ValueError as exc:
            return self.send_error_json(HTTPStatus.BAD_REQUEST, str(exc))
        return self.send_json(HTTPStatus.OK, state)

    def serve_file(self, path, content_type):
        if not path.exists():
            return self.send_error_json(HTTPStatus.NOT_FOUND, "Arquivo nao encontrado")
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(content_length) if content_length else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error_json(HTTPStatus.BAD_REQUEST, "JSON invalido")
            return None

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, status, message):
        self.send_json(status, {"error": message})

    def log_message(self, format, *args):
        return


def run():
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), AppHandler)
    print(f"Giro App rodando em http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
