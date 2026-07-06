from http.server import BaseHTTPRequestHandler
import json
import sqlite3
import os

DB_PATH = '/tmp/aquarium.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            ph REAL NOT NULL,
            turbidity REAL NOT NULL,
            water_level REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    row = conn.execute("SELECT COUNT(*) FROM sensor_data").fetchone()
    if row[0] == 0:
        import math, random
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        for i in range(30):
            ts = (now - timedelta(minutes=30 - i)).strftime('%Y-%m-%d %H:%M:%S')
            sv = (i % 60) / 60.0 * 2 * 3.14159
            t  = round(25.0 + 1.5 * math.sin(sv) + random.uniform(-0.15, 0.15), 2)
            p  = round(7.3  + 0.3 * math.cos(sv * 1.5) + random.uniform(-0.05, 0.05), 2)
            tb = round(max(0, min(100, 92.0 - 5.0 * abs(math.sin(sv / 2.0)) + random.uniform(-0.5, 0.5))), 2)
            wl = round(82.0 + 3.0 * math.sin(sv / 4.0) + random.uniform(-0.2, 0.2), 2)
            conn.execute(
                "INSERT INTO sensor_data (temperature, ph, turbidity, water_level, created_at) VALUES (?,?,?,?,?)",
                (t, p, tb, wl, ts)
            )
        conn.commit()
    conn.close()

CORS_HEADERS = [
    ('Access-Control-Allow-Origin', '*'),
    ('Access-Control-Allow-Headers', 'Content-Type'),
    ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
    ('Content-Type', 'application/json'),
]

class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress verbose access logs

    def send_json(self, code, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(code)
        for k, v in CORS_HEADERS:
            self.send_header(k, v)
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        for k, v in CORS_HEADERS:
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        try:
            init_db()
            limit = 100
            if 'limit=' in self.path:
                try:
                    limit = int(self.path.split('limit=')[1].split('&')[0])
                except Exception:
                    pass
            conn = get_db()
            rows = conn.execute(
                "SELECT id, temperature, ph, turbidity, water_level, created_at FROM sensor_data ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
            conn.close()
            result = [dict(r) for r in reversed(rows)]
            self.send_json(200, {"status": "success", "count": len(result), "data": result})
        except Exception as e:
            import traceback
            self.send_json(500, {"status": "error", "message": str(e), "traceback": traceback.format_exc()})

    def do_POST(self):
        try:
            init_db()
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            t  = data.get('temperature')
            p  = data.get('ph')
            tb = data.get('turbidity')
            wl = data.get('water_level')
            if None in [t, p, tb, wl]:
                self.send_json(400, {"status": "error", "message": "Missing fields"})
                return
            conn = get_db()
            conn.execute(
                "INSERT INTO sensor_data (temperature, ph, turbidity, water_level) VALUES (?,?,?,?)",
                (t, p, tb, wl)
            )
            conn.commit()
            conn.close()
            self.send_json(201, {"status": "success"})
        except Exception as e:
            import traceback
            self.send_json(500, {"status": "error", "message": str(e), "traceback": traceback.format_exc()})
