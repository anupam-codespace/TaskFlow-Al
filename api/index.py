from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/api/health')
@app.route('/health')
def health():
    return jsonify({"status": "running", "diagnostic": "flask-minimal"})

@app.route('/api/<path:path>')
def catch_all(path):
    return jsonify({"error": "fallback", "path": path}), 200
