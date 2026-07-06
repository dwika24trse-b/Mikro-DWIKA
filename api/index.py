import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='../public', static_url_path='')

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

SQLITE_DB_PATH = '/tmp/aquarium.db'

def get_db():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_table():
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
            t = round(25.0 + 1.5 * math.sin(sv) + random.uniform(-0.15, 0.15), 2)
            p = round(7.3 + 0.3 * math.cos(sv * 1.5) + random.uniform(-0.05, 0.05), 2)
            tb = round(92.0 - 5.0 * abs(math.sin(sv / 2.0)) + random.uniform(-0.5, 0.5), 2)
            wl = round(82.0 + 3.0 * math.sin(sv / 4.0) + random.uniform(-0.2, 0.2), 2)
            conn.execute(
                "INSERT INTO sensor_data (temperature, ph, turbidity, water_level, created_at) VALUES (?,?,?,?,?)",
                (t, p, tb, wl, ts)
            )
        conn.commit()
    conn.close()

_db_ready = False

@app.before_request
def setup():
    global _db_ready
    if not _db_ready:
        ensure_table()
        _db_ready = True

@app.route('/')
def index():
    return send_from_directory('../public', 'index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    limit = request.args.get('limit', 100, type=int)
    conn = get_db()
    rows = conn.execute(
        "SELECT id, temperature, ph, turbidity, water_level, created_at FROM sensor_data ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    result = [dict(r) for r in reversed(rows)]
    return jsonify({"status": "success", "count": len(result), "data": result})

@app.route('/api/data', methods=['POST'])
def post_data():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    t = data.get('temperature')
    p = data.get('ph')
    tb = data.get('turbidity')
    wl = data.get('water_level')
    if None in [t, p, tb, wl]:
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    conn = get_db()
    conn.execute(
        "INSERT INTO sensor_data (temperature, ph, turbidity, water_level) VALUES (?,?,?,?)",
        (t, p, tb, wl)
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201
