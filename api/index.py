from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/api/health')
@app.route('/health')
def health():
    return jsonify({
        "status": "minimal-ok",
        "env": os.getenv("FLASK_ENV", "none"),
        "db": "present" if os.getenv("DATABASE_URL") else "absent"
    })

@app.route('/api/<path:path>')
@app.route('/<path:path>')
def catch_all(path):
    return jsonify({"error": "Minimal app running - main app failed to load", "path": path}), 500
