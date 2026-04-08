"""
run.py — Application entry point.

Keeps the entry point minimal. All configuration is loaded via
the application factory in app/__init__.py.
"""

import os
import sys

# CRITICAL: Add the backend directory to sys.path before anything else!
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app import create_app
    app = create_app(os.getenv("FLASK_ENV", "production"))
except Exception as e:
    # Diagnostic fallback for Vercel crashes
    from flask import Flask
    app = Flask(__name__)
    @app.route('/api/health')
    def health_err():
        return f"Startup Error: {str(e)}", 500
    @app.route('/api/<path:path>')
    def catch_err(path):
        return f"Startup Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)

