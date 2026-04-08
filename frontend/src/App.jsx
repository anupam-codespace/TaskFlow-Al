import { useState, useEffect, useCallback } from 'react';
import './index.css';
import './App.css';
import { projectsApi, tasksApi, aiApi } from './services/api';
import { useToast } from './hooks/useToast';

// ── Constants ─────────────────────────────────────────────────────────────────

const STATUS_CONFIG = {
  todo: { label: 'To Do', color: 'var(--status-todo)', dot: '#5a5a7a' },
  in_progress: { label: 'In Progress', color: 'var(--status-inprogress)', dot: '#3b8df1' },
  done: { label: 'Done', color: 'var(--status-done)', dot: '#22c55e' },
  cancelled: { label: 'Cancelled', color: 'var(--status-cancelled)', dot: '#ef4444' },
};

const PRIORITY_CONFIG = {
  low: { label: 'Low', color: 'var(--priority-low)' },
  medium: { label: 'Medium', color: 'var(--priority-medium)' },
  high: { label: 'High', color: 'var(--priority-high)' },
  critical: { label: 'Critical', color: 'var(--priority-critical)' },
};

const PROJECT_COLORS = ['#6d6aff', '#22c55e', '#f59e0b', '#f97316', '#ec4899', '#06b6d4'];

// ── Small utility components ──────────────────────────────────────────────────

function ToastContainer({ toasts, onRemove }) {
  return (
    <div className="toast-container">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`toast toast-${t.type}`}
          onClick={() => onRemove(t.id)}
          style={{ cursor: 'pointer' }}
        >
          <span>{t.type === 'success' ? '✓' : t.type === 'error' ? '✗' : 'ℹ'}</span>
          {t.message}
        </div>
      ))}
    </div>
  );
}

function Badge({ type, value }) {
  return (
    <span className={`badge badge-${type}-${value}`}>
      {type === 'priority' ? PRIORITY_CONFIG[value]?.label : STATUS_CONFIG[value]?.label}
    </span>
  );
}

function StatusDot({ status, size = 10 }) {
  return (
    <div
      className="task-status-dot"
      style={{
        width: size,
        height: size,
        backgroundColor: STATUS_CONFIG[status]?.dot || '#5a5a7a',
      }}
    />
  );
}

// ── Modal ─────────────────────────────────────────────────────────────────────

function Modal({ title, onClose, children, footer }) {
  // Close on Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div className="modal-header">
          <h2 className="modal-title" id="modal-title">{title}</h2>
          <button className="modal-close" onClick={onClose} aria-label="Close modal">✕</button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  );
}

// ── Create Project Modal ──────────────────────────────────────────────────────

function CreateProjectModal({ onClose, onCreate }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) { setError('Project name is required.'); return; }
    setLoading(true);
    try {
      const project = await projectsApi.create({ name: name.trim(), description: description.trim() });
      onCreate(project);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title="New Project"
      onClose={onClose}
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button id="create-project-submit" className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? 'Creating…' : 'Create Project'}
          </button>
        </>
      }
    >
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label" htmlFor="project-name">Project Name *</label>
          <input
            id="project-name"
            className="form-input"
            type="text"
            placeholder="e.g. Mobile App Redesign"
            value={name}
            onChange={(e) => { setName(e.target.value); setError(''); }}
            autoFocus
          />
          {error && <span className="form-error">{error}</span>}
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="project-description">Description</label>
          <textarea
            id="project-description"
            className="form-textarea"
            placeholder="What is this project about?"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
      </form>
    </Modal>
  );
}

// ── Create Task Modal ─────────────────────────────────────────────────────────

function CreateTaskModal({ projectId, onClose, onCreate }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) { setError('Task title is required.'); return; }
    setLoading(true);
    try {
      const task = await tasksApi.create({
        project_id: projectId,
        title: title.trim(),
        description: description.trim(),
        priority,
        status: 'todo',
      });
      onCreate(task);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title="New Task"
      onClose={onClose}
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button id="create-task-submit" className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? 'Creating…' : 'Add Task'}
          </button>
        </>
      }
    >
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label" htmlFor="task-title">Title *</label>
          <input
            id="task-title"
            className="form-input"
            type="text"
            placeholder="e.g. Implement user authentication"
            value={title}
            onChange={(e) => { setTitle(e.target.value); setError(''); }}
            autoFocus
          />
          {error && <span className="form-error">{error}</span>}
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="task-description">Description</label>
          <textarea
            id="task-description"
            className="form-textarea"
            placeholder="What needs to be done? Adding detail helps the AI give better summaries."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="task-priority">Priority</label>
          <select
            id="task-priority"
            className="form-select"
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </form>
    </Modal>
  );
}

// ── Task Detail Panel ─────────────────────────────────────────────────────────

function TaskDetailModal({ task, onClose, onUpdate, onDelete }) {
  const [status, setStatus] = useState(task.status);
  const [priority, setPriority] = useState(task.priority);
  const [aiSummary, setAiSummary] = useState(task.ai_summary || '');
  const [aiPrioritySuggestion, setAiPrioritySuggestion] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await tasksApi.update(task.id, { status, priority });
      onUpdate(updated);
      onClose();
    } catch (err) {
      console.error('Failed to update task:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleAISummarise = async () => {
    setAiLoading(true);
    try {
      const result = await aiApi.summarise(task.id);
      setAiSummary(result.summary);
    } catch (err) {
      console.error('AI summarise failed:', err);
    } finally {
      setAiLoading(false);
    }
  };

  const handleAIPrioritise = async () => {
    setAiLoading(true);
    try {
      const result = await aiApi.prioritise(task.id);
      setAiPrioritySuggestion(result);
    } catch (err) {
      console.error('AI prioritise failed:', err);
    } finally {
      setAiLoading(false);
    }
  };

  const applyAISuggestion = () => {
    if (aiPrioritySuggestion) {
      setPriority(aiPrioritySuggestion.suggested_priority);
      setAiPrioritySuggestion(null);
    }
  };

  return (
    <Modal
      title={task.title}
      onClose={onClose}
      footer={
        <>
          <button
            id="delete-task-btn"
            className="btn btn-danger btn-sm"
            onClick={() => { onDelete(task.id); onClose(); }}
            style={{ marginRight: 'auto' }}
          >
            Delete
          </button>
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button id="save-task-btn" className="btn btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save Changes'}
          </button>
        </>
      }
    >
      {/* Description */}
      {task.description && (
        <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          {task.description}
        </p>
      )}

      {/* Status */}
      <div className="form-group">
        <label className="form-label" htmlFor="task-detail-status">Status</label>
        <select
          id="task-detail-status"
          className="form-select"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="done">Done</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {/* Priority */}
      <div className="form-group">
        <label className="form-label" htmlFor="task-detail-priority">Priority</label>
        <select
          id="task-detail-priority"
          className="form-select"
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      {/* AI Tools */}
      <div>
        <div style={{ display: 'flex', gap: 'var(--space-2)', marginBottom: 'var(--space-3)', flexWrap: 'wrap' }}>
          <button
            id="ai-summarise-btn"
            className="btn btn-ai btn-sm"
            onClick={handleAISummarise}
            disabled={aiLoading}
          >
            ✦ {aiSummary ? 'Regenerate Summary' : 'AI Summarise'}
          </button>
          <button
            id="ai-prioritise-btn"
            className="btn btn-ai btn-sm"
            onClick={handleAIPrioritise}
            disabled={aiLoading}
          >
            ✦ Suggest Priority
          </button>
        </div>

        {aiLoading && (
          <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center', fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
            <span style={{ animation: 'pulse-glow 1s infinite' }}>●</span> AI is thinking…
          </div>
        )}

        {aiSummary && !aiLoading && (
          <div className="ai-panel">
            <div className="ai-panel-header">
              <span className="ai-icon">✦</span>
              <span className="ai-label">AI Summary</span>
            </div>
            <p className="ai-summary-text">{aiSummary}</p>
          </div>
        )}

        {aiPrioritySuggestion && !aiLoading && (
          <div className="ai-panel" style={{ marginTop: 'var(--space-2)' }}>
            <div className="ai-panel-header">
              <span className="ai-icon">✦</span>
              <span className="ai-label">Priority Suggestion</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginTop: 'var(--space-2)' }}>
              <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
                AI suggests:
              </span>
              <span className="ai-suggestion-badge">
                {PRIORITY_CONFIG[aiPrioritySuggestion.suggested_priority]?.label}
              </span>
              {aiPrioritySuggestion.should_update && (
                <button className="btn btn-secondary btn-sm" onClick={applyAISuggestion}>
                  Apply
                </button>
              )}
              {!aiPrioritySuggestion.should_update && (
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
                  Already set correctly ✓
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}

// ── Task Card ─────────────────────────────────────────────────────────────────

function TaskCard({ task, onClick }) {
  return (
    <div
      className="task-card"
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      <StatusDot status={task.status} />
      <div className="task-card-body">
        <div className="task-card-title">{task.title}</div>
        {task.ai_summary && (
          <div className="task-card-summary">✦ {task.ai_summary}</div>
        )}
        <div className="task-card-meta">
          <Badge type="priority" value={task.priority} />
          <Badge type="status" value={task.status} />
        </div>
      </div>
    </div>
  );
}

// ── Task Board ────────────────────────────────────────────────────────────────

function TaskBoard({ project, tasks, onTaskUpdate, onTaskDelete, onAddTask, onBulkSummarise }) {
  const [selectedTask, setSelectedTask] = useState(null);

  const groupedTasks = {
    in_progress: tasks.filter(t => t.status === 'in_progress'),
    todo: tasks.filter(t => t.status === 'todo'),
    done: tasks.filter(t => t.status === 'done'),
    cancelled: tasks.filter(t => t.status === 'cancelled'),
  };

  const stats = {
    total: tasks.length,
    done: tasks.filter(t => t.status === 'done').length,
    in_progress: tasks.filter(t => t.status === 'in_progress').length,
    completion_pct: tasks.length ? Math.round((tasks.filter(t => t.status === 'done').length / tasks.length) * 100) : 0,
  };

  return (
    <div className="task-board">
      <div className="board-header">
        <div className="board-title-area">
          <h1 className="board-title">{project.name}</h1>
          <p className="board-subtitle">{project.description || 'No description'}</p>
        </div>
        <div className="board-header-actions">
          <button
            id="bulk-summarise-btn"
            className="btn btn-ai btn-sm"
            onClick={onBulkSummarise}
            title="Generate AI summaries for all unsummarised tasks"
          >
            ✦ Summarise All
          </button>
          <button id="add-task-btn" className="btn btn-primary btn-sm" onClick={onAddTask}>
            + Add Task
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-bar">
        <div className="stat-card">
          <div className="stat-label">Total Tasks</div>
          <div className="stat-value">{stats.total}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">In Progress</div>
          <div className="stat-value inprogress-color">{stats.in_progress}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Completed</div>
          <div className="stat-value done-color">{stats.done}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Completion</div>
          <div className="stat-value pct-color">{stats.completion_pct}%</div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="progress-bar-wrap">
        <div className="progress-bar-fill" style={{ width: `${stats.completion_pct}%` }} />
      </div>

      {/* Task groups */}
      {tasks.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <div className="empty-state-title">No tasks yet</div>
          <div className="empty-state-desc">Add your first task to get started</div>
          <button className="btn btn-primary" onClick={onAddTask}>+ Add Task</button>
        </div>
      ) : (
        ['in_progress', 'todo', 'done', 'cancelled'].map(status => {
          const group = groupedTasks[status];
          if (status === 'cancelled' && group.length === 0) return null;
          return (
            <div key={status} className="task-group">
              <div className="task-group-header">
                <StatusDot status={status} />
                <span
                  className="task-group-label"
                  style={{ color: STATUS_CONFIG[status]?.color }}
                >
                  {STATUS_CONFIG[status]?.label}
                </span>
                <span className="task-group-count">{group.length}</span>
              </div>
              {group.length === 0 ? (
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', paddingLeft: '20px', paddingBottom: '8px' }}>
                  No tasks here
                </div>
              ) : (
                group.map(task => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onClick={() => setSelectedTask(task)}
                  />
                ))
              )}
            </div>
          );
        })
      )}

      {/* Task detail modal */}
      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
          onUpdate={(updated) => {
            onTaskUpdate(updated);
            setSelectedTask(null);
          }}
          onDelete={(id) => {
            onTaskDelete(id);
            setSelectedTask(null);
          }}
        />
      )}
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────────────────────────

export default function App() {
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [loadingTasks, setLoadingTasks] = useState(false);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [showCreateTask, setShowCreateTask] = useState(false);
  const [backendError, setBackendError] = useState(false);
  const { toasts, addToast, removeToast } = useToast();

  const selectedProject = projects.find(p => p.id === selectedProjectId);

  // ── Load projects ──────────────────────────────────────────────────────────
  const loadProjects = useCallback(async () => {
    setLoadingProjects(true);
    try {
      const data = await projectsApi.list();
      setProjects(data);
      setBackendError(false);
    } catch (err) {
      console.error('Failed to load projects:', err);
      setBackendError(true);
      addToast('Cannot connect to backend. Is Flask running on port 5001?', 'error');
    } finally {
      setLoadingProjects(false);
    }
  }, []);

  useEffect(() => { loadProjects(); }, [loadProjects]);

  // ── Load tasks when project changes ───────────────────────────────────────
  useEffect(() => {
    if (!selectedProjectId) { setTasks([]); return; }
    const load = async () => {
      setLoadingTasks(true);
      try {
        const data = await tasksApi.listForProject(selectedProjectId);
        setTasks(data);
      } catch (err) {
        console.error('Failed to load tasks:', err);
        addToast('Failed to load tasks.', 'error');
      } finally {
        setLoadingTasks(false);
      }
    };
    load();
  }, [selectedProjectId]);

  // ── Handlers ───────────────────────────────────────────────────────────────
  const handleProjectCreated = (project) => {
    setProjects(prev => [project, ...prev]);
    setSelectedProjectId(project.id);
    addToast(`Project "${project.name}" created.`, 'success');
  };

  const handleTaskCreated = (task) => {
    setTasks(prev => [task, ...prev]);
    addToast('Task added.', 'success');
  };

  const handleTaskUpdated = (updated) => {
    setTasks(prev => prev.map(t => t.id === updated.id ? updated : t));
    addToast('Task updated.', 'success');
  };

  const handleTaskDeleted = async (taskId) => {
    try {
      await tasksApi.delete(taskId);
      setTasks(prev => prev.filter(t => t.id !== taskId));
      addToast('Task deleted.', 'info');
    } catch (err) {
      addToast('Failed to delete task.', 'error');
    }
  };

  const handleBulkSummarise = async () => {
    if (!selectedProjectId) return;
    addToast('Generating AI summaries…', 'info');
    try {
      const result = await aiApi.bulkSummarise(selectedProjectId);
      // Reload tasks to show new summaries
      const data = await tasksApi.listForProject(selectedProjectId);
      setTasks(data);
      addToast(`Summarised ${result.processed} task${result.processed !== 1 ? 's' : ''}.`, 'success');
    } catch (err) {
      addToast('Bulk summarisation failed.', 'error');
    }
  };

  // ── Project colour ─────────────────────────────────────────────────────────
  const getProjectColor = (idx) => PROJECT_COLORS[idx % PROJECT_COLORS.length];

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="app-layout">
      {/* Topbar */}
      <header className="topbar">
        <div className="topbar-brand">
          <div className="topbar-logo" aria-hidden="true">T</div>
          <span className="topbar-name">TaskFlow</span>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginLeft: '4px' }}>
            AI-Powered
          </span>
        </div>
        <div className="topbar-actions">
          {backendError && (
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--status-cancelled)', padding: '4px 8px', background: 'rgba(239,68,68,0.1)', borderRadius: '4px', border: '1px solid rgba(239,68,68,0.2)' }}>
              ● Backend offline
            </span>
          )}
          <a
            href="http://127.0.0.1:5001/api/health"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-ghost btn-sm"
            title="Check API health"
          >
            API ↗
          </a>
        </div>
      </header>

      {/* Body */}
      <div className="main-content">
        {/* Sidebar */}
        <nav className="sidebar" aria-label="Projects">
          <div className="sidebar-section-title">Projects</div>
          <button
            id="new-project-btn"
            className="sidebar-add-btn"
            onClick={() => setShowCreateProject(true)}
          >
            <span>+</span> New Project
          </button>
          {loadingProjects ? (
            Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="project-item">
                <div className="skeleton" style={{ width: 8, height: 8, borderRadius: '50%' }} />
                <div className="skeleton" style={{ flex: 1, height: 12 }} />
              </div>
            ))
          ) : projects.length === 0 ? (
            <div style={{ padding: 'var(--space-4)', fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
              No projects yet. Create one!
            </div>
          ) : (
            projects.map((p, idx) => (
              <div
                key={p.id}
                id={`project-item-${p.id}`}
                className={`project-item ${selectedProjectId === p.id ? 'active' : ''}`}
                onClick={() => setSelectedProjectId(p.id)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && setSelectedProjectId(p.id)}
              >
                <div
                  className="project-dot"
                  style={{ backgroundColor: getProjectColor(idx) }}
                />
                <span className="project-item-name">{p.name}</span>
                <span className="project-item-count">{p.task_count ?? ''}</span>
              </div>
            ))
          )}
        </nav>

        {/* Main area */}
        <main style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          {!selectedProject ? (
            <div className="no-project-state animate-fade-in">
              <div className="no-project-glyph">🗂️</div>
              <h2 style={{ fontSize: 'var(--text-xl)', color: 'var(--text-secondary)' }}>
                Select a project
              </h2>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>
                Choose a project from the sidebar or create a new one to get started.
              </p>
              <button className="btn btn-primary" onClick={() => setShowCreateProject(true)}>
                + New Project
              </button>
            </div>
          ) : loadingTasks ? (
            <div className="task-board animate-fade-in">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="task-card" style={{ cursor: 'default' }}>
                  <div className="skeleton" style={{ width: 10, height: 10, borderRadius: '50%', marginTop: 4 }} />
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div className="skeleton" style={{ height: 14, width: '70%' }} />
                    <div className="skeleton" style={{ height: 12, width: '40%' }} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <TaskBoard
              project={selectedProject}
              tasks={tasks}
              onTaskUpdate={handleTaskUpdated}
              onTaskDelete={handleTaskDeleted}
              onAddTask={() => setShowCreateTask(true)}
              onBulkSummarise={handleBulkSummarise}
            />
          )}
        </main>
      </div>

      {/* Modals */}
      {showCreateProject && (
        <CreateProjectModal
          onClose={() => setShowCreateProject(false)}
          onCreate={handleProjectCreated}
        />
      )}

      {showCreateTask && selectedProject && (
        <CreateTaskModal
          projectId={selectedProject.id}
          onClose={() => setShowCreateTask(false)}
          onCreate={handleTaskCreated}
        />
      )}

      {/* Toast notifications */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}
