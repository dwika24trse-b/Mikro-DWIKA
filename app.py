import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

# Database Configuration
DB_HOST = os.environ.get('DB_HOST', '')
DB_USER = os.environ.get('DB_USER', '')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', '')

use_mysql = all([DB_HOST, DB_USER, DB_NAME])
SQLITE_DB_PATH = 'aquarium.db'

def get_db_connection():
    """Establish database connection. Connects to MySQL if configured, otherwise falls back to SQLite."""
    if use_mysql:
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            if conn.is_connected():
                return conn, "mysql"
        except Error as e:
            print(f"Error connecting to MySQL: {e}. Falling back to SQLite...")
    
    # SQLite fallback
    conn = sqlite3.connect(SQLITE_DB_PATH)
    # Return database rows as dictionaries for easier JSON conversion
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"

def init_db():
    """Initialize database tables for MySQL or SQLite."""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    if db_type == "mysql":
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                temperature FLOAT NOT NULL,
                ph FLOAT NOT NULL,
                turbidity FLOAT NOT NULL,
                water_level FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Initialized MySQL database successfully.")
    else:
        cursor.execute("""
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
        print(f"Initialized SQLite database at '{SQLITE_DB_PATH}' successfully.")
        
    cursor.close()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    """Serve the main frontend dashboard."""
    return send_from_directory('public', 'index.html')

@app.route('/api/data', methods=['POST'])
def add_sensor_data():
    """
    API endpoint for ESP32 / Arduino / Raspberry Pi to send sensor data.
    Expects JSON: { "temperature": 25.5, "ph": 7.2, "turbidity": 92.5, "water_level": 80.0 }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON format"}), 400
        
    # Extract values
    temperature = data.get('temperature')
    ph = data.get('ph')
    turbidity = data.get('turbidity')
    water_level = data.get('water_level')
    
    # Validation
    if None in [temperature, ph, turbidity, water_level]:
        return jsonify({"status": "error", "message": "Missing required fields (temperature, ph, turbidity, water_level)"}), 400
        
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        if db_type == "mysql":
            query = """
                INSERT INTO sensor_data (temperature, ph, turbidity, water_level)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (temperature, ph, turbidity, water_level))
            conn.commit()
        else:
            query = """
                INSERT INTO sensor_data (temperature, ph, turbidity, water_level)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, (temperature, ph, turbidity, water_level))
            conn.commit()
            
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "Data saved successfully"}), 201
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/data', methods=['GET'])
def get_sensor_data():
    """
    API endpoint to retrieve historical sensor data.
    Query parameter: 'limit' (default 100)
    """
    limit = request.args.get('limit', 100, type=int)
    
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        if db_type == "mysql":
            query = "SELECT id, temperature, ph, turbidity, water_level, created_at FROM sensor_data ORDER BY id DESC LIMIT %s"
            # Setting dictionary=True to return dicts in mysql connector
            mysql_cursor = conn.cursor(dictionary=True)
            mysql_cursor.execute(query, (limit,))
            rows = mysql_cursor.fetchall()
            mysql_cursor.close()
        else:
            query = "SELECT id, temperature, ph, turbidity, water_level, created_at FROM sensor_data ORDER BY id DESC LIMIT ?"
            cursor.execute(query, (limit,))
            rows = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            
        conn.close()
        
        # Reverse rows to return data in chronological order for charting
        rows.reverse()
        
        return jsonify({
            "status": "success",
            "db_type": db_type,
            "count": len(rows),
            "data": rows
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Determine port
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Smart Aquarium server on port {port}...")
    print(f"Backend mode: {'MySQL' if use_mysql else 'SQLiteFallback'}")
    app.run(host='0.0.0.0', port=port, debug=True)
