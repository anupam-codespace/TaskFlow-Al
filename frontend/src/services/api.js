/**
 * services/api.js — Centralised API client.
 *
 * All fetch calls go through this module. Benefits:
 * - One place to add auth headers in the future.
 * - Consistent error handling and JSON parsing.
 * - Easy to mock in tests.
 * - Changing the base URL is a 1-line change.
 */

const BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '/api' : 'http://127.0.0.1:5001/api');

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

/**
 * Core fetch wrapper. Throws ApiError on non-2xx responses.
 */
async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };

  let response;
  try {
    response = await fetch(url, config);
  } catch (networkError) {
    throw new ApiError('Network error — is the backend running?', 0);
  }

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      errorMessage = body.error || errorMessage;
    } catch {
      // body wasn't JSON — use default message
    }
    throw new ApiError(errorMessage, response.status);
  }

  // 204 No Content
  if (response.status === 204) return null;
  return response.json();
}

// ── Projects ──────────────────────────────────────────────────────────────────

export const projectsApi = {
  list: () => request('/projects'),
  get: (id) => request(`/projects/${id}`),
  create: (data) => request('/projects', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/projects/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (id) => request(`/projects/${id}`, { method: 'DELETE' }),
};

// ── Tasks ─────────────────────────────────────────────────────────────────────

export const tasksApi = {
  listForProject: (projectId) => request(`/tasks/project/${projectId}`),
  get: (id) => request(`/tasks/${id}`),
  create: (data) => request('/tasks', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (id) => request(`/tasks/${id}`, { method: 'DELETE' }),
};

// ── AI ────────────────────────────────────────────────────────────────────────

export const aiApi = {
  summarise: (taskId) => request(`/ai/summarise/${taskId}`, { method: 'POST' }),
  prioritise: (taskId) => request(`/ai/prioritise/${taskId}`, { method: 'POST' }),
  bulkSummarise: (projectId) => request(`/ai/bulk-summarise/${projectId}`, { method: 'POST' }),
};

// ── Health ────────────────────────────────────────────────────────────────────

export const healthApi = {
  check: () => request('/health'),
};

export { ApiError };
