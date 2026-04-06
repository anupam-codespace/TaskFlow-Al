import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [expenses, setExpenses] = useState([]);
  const [title, setTitle] = useState('');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('General');
  const [loading, setLoading] = useState(true);

  // Consider fetching API URL from environment, using localhost for dev
  const API_URL = 'http://127.0.0.1:5000/api/expenses';

  useEffect(() => {
    fetchExpenses();
  }, []);

  const fetchExpenses = async () => {
    try {
      const response = await fetch(API_URL);
      const data = await response.json();
      setExpenses(data);
    } catch (error) {
      console.error('Error fetching expenses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title || !amount) return;

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          amount: parseFloat(amount),
          category
        }),
      });

      if (response.ok) {
        setTitle('');
        setAmount('');
        setCategory('General');
        fetchExpenses();
      }
    } catch (error) {
      console.error('Error adding expense:', error);
    }
  };

  const handleDelete = async (id) => {
    try {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setExpenses(expenses.filter(expense => expense.id !== id));
      }
    } catch (error) {
      console.error('Error deleting expense:', error);
    }
  };

  const totalExpenses = expenses.reduce((sum, item) => sum + item.amount, 0);

  return (
    <div className="app-container">
      <header className="header animate-fade-in">
        <h1>NexusFi Tracker</h1>
        <p>Premium Expense Management</p>
      </header>

      <main className="dashboard">
        <section className="glass card animate-fade-in" style={{ animationDelay: '0.1s' }}>
          <h2>Add Expense</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Title</label>
              <input
                type="text"
                className="form-input"
                placeholder="E.g., Groceries"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            
            <div className="form-group">
              <label>Amount ($)</label>
              <input
                type="number"
                className="form-input"
                placeholder="0.00"
                step="0.01"
                min="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Category</label>
              <select 
                className="form-input"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                <option value="General">General</option>
                <option value="Food & Dining">Food & Dining</option>
                <option value="Transportation">Transportation</option>
                <option value="Entertainment">Entertainment</option>
                <option value="Shopping">Shopping</option>
                <option value="Bills & Utilities">Bills & Utilities</option>
              </select>
            </div>

            <button type="submit" className="btn-primary">
              Add Expense
            </button>
          </form>
        </section>

        <section className="glass card animate-fade-in" style={{ animationDelay: '0.2s' }}>
          <h2>Overview</h2>
          
          <div className="stats-container">
            <div className="stat-box">
              <p>Total Expenses</p>
              <h3>${totalExpenses.toFixed(2)}</h3>
            </div>
            <div className="stat-box">
              <p>Transactions</p>
              <h3 style={{ color: '#a5b4fc' }}>{expenses.length}</h3>
            </div>
          </div>

          <div className="expense-list">
            {loading ? (
              <div className="empty-state">Loading expenses...</div>
            ) : expenses.length === 0 ? (
              <div className="empty-state">
                <p>No expenses found. Start tracking today!</p>
              </div>
            ) : (
              expenses.map((expense) => (
                <div key={expense.id} className="expense-item">
                  <div className="expense-info">
                    <h4>{expense.title}</h4>
                    <div className="expense-meta">
                      <span className="category-badge">{expense.category}</span>
                      <span>{expense.date.split(' ')[0]}</span>
                    </div>
                  </div>
                  <div className="expense-actions">
                    <span className="expense-amount">${expense.amount.toFixed(2)}</span>
                    <button 
                      className="btn-danger"
                      onClick={() => handleDelete(expense.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
