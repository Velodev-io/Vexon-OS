import axios from 'axios'

const defaultApiBase = `http://${window.location.hostname}:8000`
const apiBaseUrl = import.meta.env.VITE_API_URL ?? defaultApiBase

const TOKEN_KEY = 'vexon_token'
const USER_ID_KEY = 'vexon_user_id'

function decodePayload(token: string) {
  try {
    const [, payload] = token.split('.')
    if (!payload) {
      return null
    }

    const normalized = payload
      .replace(/-/g, '+')
      .replace(/_/g, '/')
      .padEnd(Math.ceil(payload.length / 4) * 4, '=')

    const decoded = window.atob(normalized)
    return JSON.parse(decoded)
  } catch {
    return null
  }
}

export async function login(password: string) {
  const response = await axios.post(`${apiBaseUrl}/auth/login`, { password })
  const { token, user_id: userId } = response.data
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_ID_KEY, userId)
  return response.data
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_ID_KEY)
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function getUserId() {
  return localStorage.getItem(USER_ID_KEY)
}

export function isLoggedIn() {
  const token = getToken()
  if (!token) {
    return false
  }

  const payload = decodePayload(token)
  if (!payload?.exp) {
    return false
  }

  return payload.exp * 1000 > Date.now()
}

// BYPASS AUTH - Mock login for testing
export async function loginBypass() {
  const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdXJ5YW5zaCIsImV4cCI6OTk5OTk5OTk5OX0.mock'
  const mockUserId = 'suryansh'
  localStorage.setItem(TOKEN_KEY, mockToken)
  localStorage.setItem(USER_ID_KEY, mockUserId)
  return { token: mockToken, user_id: mockUserId }
}
