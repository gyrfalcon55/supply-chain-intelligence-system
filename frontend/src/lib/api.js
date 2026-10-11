const configuredBase = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').trim();
const API_BASE = configuredBase.replace(/\/$/, '');
export function apiUrl(path) {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE}${normalized}`;
}
export async function api(path, options = {}) {
  const response = await fetch(apiUrl(path), {
    ...options,
    headers: { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) },
  });
  const raw = await response.text();
  let data;
  try { data = raw ? JSON.parse(raw) : {}; } catch { data = { detail: raw }; }
  if (!response.ok) throw new Error(data.detail || data.message || raw || `Request failed (${response.status})`);
  return data;
}
export const post = (path, body) => api(path, { method: 'POST', ...(body === undefined ? {} : { body: JSON.stringify(body) }) });