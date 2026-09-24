const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function apiRequest(path, options = {}) {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${API_URL}/api/v1${path}`, {
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  if (response.status === 204) return null
  const body = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(body.error?.message || `Request failed (${response.status})`)
  return body
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem('access_token'))
}
