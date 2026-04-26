import axios from 'axios'

const defaultApiBase = `http://${window.location.hostname}:8000`
const apiBaseUrl = import.meta.env.VITE_API_URL ?? defaultApiBase

const TOKEN_KEY = 'vexon_token'
const USER_ID_KEY = 'vexon_user_id'

export async function login(password: string) {
  const response = await axios.post(`${apiBaseUrl}/auth/login`, { password })
  const { token, user_id: userId } = response.data
  localStorage.setItem(TOKEN_KEY, token)
  if (userId) {
    localStorage.setItem(USER_ID_KEY, userId)
  }
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

export function setUserId(userId: string | null) {
  if (!userId) {
    localStorage.removeItem(USER_ID_KEY)
    return
  }
  localStorage.setItem(USER_ID_KEY, userId)
}

export function isLoggedIn() {
  return Boolean(getToken())
}
