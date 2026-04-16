/**
 * api.js — Centralized API client for the portfolio frontend.
 * Handles auth headers, error responses, and base URL config.
 */

// ── Configuration ─────────────────────────────────────
const API_BASE = window.API_BASE_URL || 'http://localhost:5000/api';

// ── Token Management ──────────────────────────────────
const Auth = {
  getToken:    () => localStorage.getItem('portfolio_token'),
  setToken:    (t) => localStorage.setItem('portfolio_token', t),
  removeToken: () => localStorage.removeItem('portfolio_token'),
  isLoggedIn:  () => !!localStorage.getItem('portfolio_token'),
};

// ── Core API Fetch Wrapper ────────────────────────────
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const token = Auth.getToken();

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
    ...options,
  };

  // Remove Content-Type for FormData uploads
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  try {
    const res = await fetch(url, config);
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      // Handle 401 — token expired
      if (res.status === 401 && token) {
        Auth.removeToken();
        if (window.location.pathname.includes('/admin/dashboard')) {
          window.location.href = '/admin/login.html';
        }
      }
      throw new ApiError(data.error || 'Request failed', res.status, data);
    }

    return data;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    throw new ApiError('Network error — is the backend running?', 0);
  }
}

// ── Custom API Error Class ────────────────────────────
class ApiError extends Error {
  constructor(message, status, data = {}) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

// ── API Methods ───────────────────────────────────────
const API = {

  // ── Auth ─────────────────────────────────────────
  auth: {
    login: (email, password) =>
      apiFetch('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),

    me: () => apiFetch('/auth/me'),

    changePassword: (current_password, new_password) =>
      apiFetch('/auth/change-password', { method: 'POST', body: JSON.stringify({ current_password, new_password }) }),

    resetPassword: (email, recovery_pin, new_password) =>
      apiFetch('/auth/reset-password', { method: 'POST', body: JSON.stringify({ email, recovery_pin, new_password }) }),
  },

  // ── Projects ──────────────────────────────────────
  projects: {
    list: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return apiFetch(`/projects${qs ? '?' + qs : ''}`);
    },
    get: (id) => apiFetch(`/projects/${id}`),
    create: (data) => apiFetch('/projects', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiFetch(`/projects/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiFetch(`/projects/${id}`, { method: 'DELETE' }),
    categories: () => apiFetch('/projects/meta/categories'),
  },

  // ── Contact ───────────────────────────────────────
  contact: {
    submit: (data) => apiFetch('/contact', { method: 'POST', body: JSON.stringify(data) }),
    list: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return apiFetch(`/contact${qs ? '?' + qs : ''}`);
    },
    markRead: (id) => apiFetch(`/contact/${id}/read`, { method: 'PUT' }),
    delete: (id) => apiFetch(`/contact/${id}`, { method: 'DELETE' }),
  },

  // ── Analytics ─────────────────────────────────────
  analytics: {
    track: (data) => apiFetch('/analytics/track', { method: 'POST', body: JSON.stringify(data) }),
    summary: (days = 30) => apiFetch(`/analytics/summary?days=${days}`),
    pages: () => apiFetch('/analytics/pages'),
  },

  // ── Chatbot ───────────────────────────────────────
  chat: {
    send: (message, history = []) =>
      apiFetch('/chat', { method: 'POST', body: JSON.stringify({ message, history }) }),
  },

  // ── Resume ────────────────────────────────────────
  resume: {
    downloadUrl: () => `${API_BASE}/resume/download`,
  },

  // ── Skills ────────────────────────────────────────
  skills: {
    list: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return apiFetch(`/skills${qs ? '?' + qs : ''}`);
    },
    create: (data) => apiFetch('/skills', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiFetch(`/skills/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiFetch(`/skills/${id}`, { method: 'DELETE' }),
  },

  // ── Experience ────────────────────────────────────
  experience: {
    list: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return apiFetch(`/experience${qs ? '?' + qs : ''}`);
    },
    create: (data) => apiFetch('/experience', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiFetch(`/experience/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiFetch(`/experience/${id}`, { method: 'DELETE' }),
  },

  // ── Blog ─────────────────────────────────────────
  blog: {
    list: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return apiFetch(`/blog${qs ? '?' + qs : ''}`);
    },
    get: (slug) => apiFetch(`/blog/${slug}`),
    create: (data) => apiFetch('/blog', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiFetch(`/blog/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiFetch(`/blog/${id}`, { method: 'DELETE' }),
  },

  // ── Settings ──────────────────────────────────────
  settings: {
    getPublic: () => apiFetch('/settings/public'),
    list: () => apiFetch('/settings'),
    update: (key, value) => apiFetch(`/settings/${key}`, { method: 'PUT', body: JSON.stringify({ value }) }),
  },

};

// Export for use in other scripts
window.API = API;
window.Auth = Auth;
window.ApiError = ApiError;
