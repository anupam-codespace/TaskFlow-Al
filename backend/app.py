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

@app.route('/api/initiatives', methods=['GET'])
def get_initiatives():
    try:
        require_db()
        # Fetch initiatives, sorted by created_at descending
        response = supabase.table('initiatives').select('*').order('created_at', desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/initiatives', methods=['POST'])
def add_initiative():
    data = request.json
    if not data or not data.get('title') or not data.get('owner') or not data.get('status') or not data.get('priority'):
        return jsonify({'error': 'Missing required fields (title, owner, status, priority)'}), 400
    
    try:
        require_db()
        new_initiative = {
            'title': data['title'],
            'owner': data['owner'],
            'status': data['status'],
            'priority': data['priority'],
            'notes': data.get('notes', '')
        }
        response = supabase.table('initiatives').insert(new_initiative).execute()
        if len(response.data) > 0:
            return jsonify(response.data[0]), 201
        else:
            return jsonify({'error': 'Failed to insert initiative status'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/initiatives/<int:id>', methods=['DELETE'])
def delete_initiative(id):
    try:
        require_db()
        response = supabase.table('initiatives').delete().eq('id', id).execute()
        return jsonify({'message': 'Initiative updated removed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
