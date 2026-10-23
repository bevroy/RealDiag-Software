// Single place for calling the RealDiag API from the browser.
//
// The API (api.realdiag.com) is a different origin from the app
// (app.realdiag.com), so a plain fetch() does not send the HttpOnly login
// cookie and every signed-in route answers 401. apiFetch always sends
// credentials; use it for every API call instead of fetch().
//
// CommonJS so jest can load it without a Babel config (see __tests__).

const DEFAULT_API_BASE = 'https://api.realdiag.com'
const MUTATING_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

function getApiBase() {
  if (typeof window !== 'undefined') {
    const runtimeConfig = window.__RUNTIME_CONFIG || window.__RUNTIME_CONFIG__
    if (runtimeConfig && runtimeConfig.NEXT_PUBLIC_API_BASE) return runtimeConfig.NEXT_PUBLIC_API_BASE
  }
  return process.env.NEXT_PUBLIC_API_BASE || DEFAULT_API_BASE
}

// Paths ("/diagnostic/trees") are joined to the API base; absolute URLs are
// passed through so callers that already built a full URL keep working.
function apiUrl(path) {
  if (/^https?:\/\//i.test(path)) return path
  const base = getApiBase().replace(/\/+$/, '')
  return `${base}${path.startsWith('/') ? '' : '/'}${path}`
}

function readCsrfToken() {
  if (typeof document === 'undefined') return null
  const match = document.cookie.match(/csrf_token=([^;]+)/)
  return match ? match[1] : null
}

function apiFetch(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  const headers = { ...(options.headers || {}) }
  const hasContentType = Object.keys(headers).some((h) => h.toLowerCase() === 'content-type')
  if (typeof options.body === 'string' && !hasContentType) {
    headers['Content-Type'] = 'application/json'
  }
  if (MUTATING_METHODS.includes(method)) {
    const csrfToken = readCsrfToken()
    if (csrfToken) headers['X-CSRF-Token'] = csrfToken
  }
  return fetch(apiUrl(path), { ...options, method, headers, credentials: 'include' })
}

module.exports = { DEFAULT_API_BASE, getApiBase, apiUrl, apiFetch }
