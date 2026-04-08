import os
import sys

# Standard Vercel Python entry point
try:
    from app import create_app
    app = create_app(os.getenv("FLASK_ENV", "production"))
except Exception as e:
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
