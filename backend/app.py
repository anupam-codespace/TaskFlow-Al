from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
# Enable CORS for React frontend (default vite port is 5173)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure SQLAlchemy (SQLite database)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'expenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'amount': self.amount,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S')
        }

with app.app_context():
    db.create_all()

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    try:
        expenses = Expense.query.order_by(Expense.date.desc()).all()
        return jsonify([expense.to_dict() for expense in expenses]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.json
    if not data or not data.get('title') or not data.get('amount') or not data.get('category'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        new_expense = Expense(
            title=data['title'],
            category=data['category'],
            amount=float(data['amount'])
        )
        db.session.add(new_expense)
        db.session.commit()
        return jsonify(new_expense.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    try:
        expense = Expense.query.get(id)
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'message': 'Expense deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
