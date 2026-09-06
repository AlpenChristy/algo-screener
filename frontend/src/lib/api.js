/**
 * API helper — centralises the base URL so the frontend works
 * both locally (proxied via Vite) and in production on Cloudflare Pages.
 *
 * Local dev:   VITE_API_BASE_URL is not set → falls back to '' → Vite proxy
 *              handles /api/* → http://localhost:8000
 * Production:  VITE_API_BASE_URL = https://algo-screener-backend.onrender.com
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

/**
 * Build a full HTTP URL for an API path.
 * @param {string} path  e.g. '/api/universes'
 * @returns {string}
 */
export function apiUrl(path) {
  return `${BASE_URL}${path}`;
}

/**
 * Build a WebSocket URL for an API path.
 * Automatically switches ws:// ↔ wss:// based on the base URL protocol.
 * @param {string} path  e.g. '/ws/screener'
 * @returns {string}
 */
export function wsUrl(path) {
  if (BASE_URL) {
    // Convert https → wss, http → ws
    const wsBase = BASE_URL.replace(/^https/, 'wss').replace(/^http/, 'ws');
    return `${wsBase}${path}`;
  }
  // Local dev: derive from current page origin
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${window.location.host}${path}`;
}

/**
 * Convenience wrapper around fetch() that prepends the base URL.
 * @param {string} path
 * @param {RequestInit} [options]
 * @returns {Promise<Response>}
 */
export function apiFetch(path, options = {}) {
  return fetch(apiUrl(path), options);
}
