from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Enable CORS for React frontend (default vite port is 5173)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def require_db():
    if not supabase:
        raise ValueError("Supabase is not configured yet. Please set up the .env file with Supabase credentials.")

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    uid = data.get('id')
    try:
        require_db()
        response = supabase.table('users').select('*').eq('id', uid).execute()
        if len(response.data) > 0:
            return jsonify(response.data[0]), 200
        else:
            return jsonify({'error': 'User ID not found. Use MGR-01 or ENG-01'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects', methods=['GET'])
def get_projects():
    try:
        require_db()
        # Fetch projects
        response = supabase.table('projects').select('*').order('created_at', desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<int:project_id>/events', methods=['GET'])
def get_project_events(project_id):
    try:
        require_db()
        response = supabase.table('project_events').select('*').eq('project_id', project_id).order('created_at', desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    try:
        require_db()
        response = supabase.table('projects').insert(data).execute()
        return jsonify(response.data[0]), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
