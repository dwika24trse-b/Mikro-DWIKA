from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/ping')
def ping():
    return jsonify({"status": "ok", "message": "Server is alive"})

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        "status": "success",
        "count": 1,
        "data": [
            {
                "id": 1,
                "temperature": 25.5,
                "ph": 7.2,
                "turbidity": 92.0,
                "water_level": 82.0,
                "created_at": "2026-07-06 12:00:00"
            }
        ]
    })

@app.route('/api/data', methods=['POST'])
def post_data():
    return jsonify({"status": "success"}), 201
