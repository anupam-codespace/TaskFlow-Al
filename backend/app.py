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

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    try:
        # Fetch expenses, sorted by created_at or date descending
        response = supabase.table('expenses').select('*').order('date', desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.json
    if not data or not data.get('title') or not data.get('amount') or not data.get('category'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        new_expense = {
            'title': data['title'],
            'category': data['category'],
            'amount': float(data['amount'])
            # date is automatically set by Supabase default value if omitted, or we can let Postgres handle it
        }
        response = supabase.table('expenses').insert(new_expense).execute()
        # insert returns the inserted row in response.data
        if len(response.data) > 0:
            return jsonify(response.data[0]), 201
        else:
            return jsonify({'error': 'Failed to insert expense'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    try:
        # Check if exists (optional but good practice, though delete will just do nothing if not found)
        response = supabase.table('expenses').delete().eq('id', id).execute()
        return jsonify({'message': 'Expense deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
