import os
import sys

# Get the absolute path of the backend directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Add the backend directory to sys.path so 'app' and 'config' can be imported
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Now try importing
try:
    from app import create_app
    app = create_app(os.getenv("FLASK_ENV", "production"))
except ImportError:
    # Fallback for different Vercel structures
    try:
        from backend.app import create_app
        app = create_app(os.getenv("FLASK_ENV", "production"))
    except Exception as e:
        from flask import Flask
        app = Flask(__name__)
        @app.route('/api/health')
        def health_err():
            return f"Backend Configuration Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)
