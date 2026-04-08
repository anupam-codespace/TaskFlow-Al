import os
import sys
from flask import Flask

# ── Baseline Setup ───────────────────────────────────────────────────────────
# We define 'app' immediately so Vercel always finds a valid export.
# If the real setup fails, this dummy app will at least provide an error message.
app = Flask(__name__)

@app.route('/api/health')
@app.route('/health')
def health_check():
    return {"status": "backend-base-running", "note": "Real app failed to load. Check logs."}, 200

# ── Real App Injection ───────────────────────────────────────────────────────
try:
    # Add the current directory to path to find 'app' and 'config'
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    if curr_dir not in sys.path:
        sys.path.insert(0, curr_dir)

    # Attempt to load the real application factory
    from app import create_app
    
    # Overwrite the 'app' variable with the real configurations
    real_app = create_app(os.getenv("FLASK_ENV", "production"))
    app = real_app

except Exception as e:
    # If the real app fails, we keep the dummy 'app' and log the error to it
    @app.route('/api/error')
    def startup_error():
        # This helps you see the actual traceback in the browser!
        import traceback
        return {
            "error": "Failed to initialize backend",
            "message": str(e),
            "traceback": traceback.format_exc()
        }, 500
    
    # Also log to console for Vercel logs
    print(f"CRITICAL: Backend startup failed: {e}")

if __name__ == "__main__":
    app.run(debug=True, port=8000)
