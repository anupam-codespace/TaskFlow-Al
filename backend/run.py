"""
run.py — Application entry point.

Keeps the entry point minimal. All configuration is loaded via
the application factory in app/__init__.py.
"""

import os
import sys

# Ensure the backend directory is in the path so 'app' and 'config' can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Vercel needs the 'app' variable to be the Flask instance
app = create_app(os.getenv("FLASK_ENV", "production"))

if __name__ == "__main__":
    app.run(debug=True, port=8000)

