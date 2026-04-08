import os
import sys

# Ensure the backend directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Use port 5001 to avoid MacOS Control Center conflict.
    app.run(debug=True, port=5001)
