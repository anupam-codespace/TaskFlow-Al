import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [initiatives, setInitiatives] = useState([]);
  const [title, setTitle] = useState('');
  const [owner, setOwner] = useState('');
  const [status, setStatus] = useState('On Track');
  const [priority, setPriority] = useState('Medium');
  const [notes, setNotes] = useState('');
  
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState(null);

  const API_URL = 'http://127.0.0.1:5000/api/initiatives';

  useEffect(() => {
    fetchInitiatives();
  }, []);

  const fetchInitiatives = async () => {
    try {
      const response = await fetch(API_URL);
      const data = await response.json();
      if (Array.isArray(data)) {
        setInitiatives(data);
        setApiError(null);
      } else {
        console.error('API Error:', data.error);
        setApiError(data.error);
        setInitiatives([]);
      }
    } catch (error) {
      console.error('Fetch error:', error);
      setApiError('Unable to reach the Clarity server. Ensure backend is running.');
      setInitiatives([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title || !owner) return;

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, owner, status, priority, notes }),
      });

      if (response.ok) {
        setTitle('');
        setNotes('');
        // Keep owner, status, priority as defaults for rapid entry
        fetchInitiatives();
      } else {
        const err = await response.json();
        setApiError(err.error);
      }
    } catch (error) {
      console.error('Submit error:', error);
    }
  };

  const handleDelete = async (id) => {
    try {
      const response = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
      if (response.ok) {
        setInitiatives(initiatives.filter(init => init.id !== id));
      }
    } catch (error) {
      console.error('Delete error:', error);
    }
  };

  const getStatusClass = (stat) => {
    switch (stat) {
      case 'On Track': return 'status-on-track';
      case 'At Risk': return 'status-at-risk';
      case 'Blocked': return 'status-blocked';
      default: return '';
    }
  };

  const getPriorityColor = (pri) => {
    switch (pri) {
      case 'High': return 'var(--priority-high)';
      case 'Medium': return 'var(--priority-medium)';
      case 'Low': return 'var(--priority-low)';
      default: return '#71717A';
    }
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="dashboard-container animate-slide-up">
      <header className="dashboard-header">
        <h1>Clarity Pulse</h1>
        <p>Enterprise Initiative Tracking & Real-Time Alignment</p>
      </header>

      {apiError && (
        <div className="error-state glass-panel">
          <h4>Database Connection Warning</h4>
          <p>{apiError}</p>
        </div>
      )}

      <main className="main-content">
        {/* Left Sidebar Form */}
        <aside className="glass-panel pulse-form">
          <h2>Post Update</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-field">
              <label>Initiative Title</label>
              <input
                type="text"
                className="input-control"
                placeholder="e.g. Q3 Migration Project"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>

            <div className="form-field">
              <label>Project Owner</label>
              <input
                type="text"
                className="input-control"
                placeholder="Name or Team"
                value={owner}
                onChange={(e) => setOwner(e.target.value)}
                required
              />
            </div>

            <div className="form-field">
              <label>Current Status</label>
              <select 
                className="input-control"
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              >
                <option value="On Track">🟢 On Track</option>
                <option value="At Risk">🟡 At Risk</option>
                <option value="Blocked">🔴 Blocked</option>
              </select>
            </div>

            <div className="form-field">
              <label>Priority Layer</label>
              <select 
                className="input-control"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
              >
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>

            <div className="form-field">
              <label>Latest Notes</label>
              <textarea
                className="input-control"
                placeholder="Briefly summarize progress or blockers..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>

            <button type="submit" className="btn-submit">
              Broadcast Update
            </button>
          </form>
        </aside>

        {/* Right Feed Panel */}
        <section className="feed-container">
          <div className="feed-header">
            <h2>Live Pulse Feed</h2>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              {initiatives.length} Active
            </span>
          </div>

          <div className="initiatives-feed">
            {loading ? (
              <div className="empty-state">Syncing data...</div>
            ) : initiatives.length === 0 && !apiError ? (
              <div className="empty-state">
                No active initiatives found. Post an update to begin tracking.
              </div>
            ) : (
              initiatives.map((init, index) => (
                <article 
                  key={init.id} 
                  className="glass-panel initiative-card animate-slide-up"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <div className="card-top">
                    <div className="title-row">
                      <h3>{init.title}</h3>
                      <p>Owned by <strong>{init.owner}</strong></p>
                    </div>
                    <span className={`status-badge ${getStatusClass(init.status)}`}>
                      {init.status}
                    </span>
                  </div>

                  {init.notes && (
                    <div className="card-notes">
                      {init.notes}
                    </div>
                  )}

                  <div className="card-bottom">
                    <div className="priority-badge">
                      <span className="priority-dot" style={{ backgroundColor: getPriorityColor(init.priority) }}></span>
                      {init.priority} Priority
                    </div>
                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                      <span>{formatDate(init.created_at)}</span>
                      <button className="btn-delete" onClick={() => handleDelete(init.id)}>Remove</button>
                    </div>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
