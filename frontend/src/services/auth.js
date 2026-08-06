// Simple auth helper — reads/writes localStorage
// All components use these functions instead of touching localStorage directly

export function getToken() {
  return localStorage.getItem('token')
}

export function getUser() {
  return JSON.parse(localStorage.getItem('user') || '{}')
}

export function saveAuth(token, user) {
  localStorage.setItem('token', token)
  localStorage.setItem('user', JSON.stringify(user))
}

export function clearAuth() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

export function isLoggedIn() {
  return !!localStorage.getItem('token')
}