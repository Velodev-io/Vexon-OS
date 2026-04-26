import { useEffect, useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import PrivateRoute from './components/PrivateRoute'
import { useWebSocket } from './hooks/useWebSocket'
import api from './lib/api'
import { getToken, logout, setUserId } from './lib/auth'
import Login from './pages/Login'
import Shell from './pages/Shell'
import { useStreamStore } from './store/streamStore'

function ShellApp() {
  const activeSessionId = useStreamStore((state) => state.activeSessionId)

  const { isConnected } = useWebSocket(activeSessionId || '')

  return (
    <div className="h-screen w-full flex flex-col bg-[#0a0a0a] text-white selection:bg-white/10">
      <Shell sessionId={activeSessionId || ''} isConnected={isConnected} />
    </div>
  )
}

function App() {
  const [authReady, setAuthReady] = useState(() => !getToken())

  useEffect(() => {
    const token = getToken()
    if (!token) {
      setAuthReady(true)
      return
    }

    let cancelled = false

    const bootstrapAuth = async () => {
      try {
        const { data } = await api.get('/auth/me')
        if (!cancelled) {
          setUserId(data?.sub ?? null)
        }
      } catch {
        if (!cancelled) {
          logout()
        }
      } finally {
        if (!cancelled) {
          setAuthReady(true)
        }
      }
    }

    void bootstrapAuth()

    return () => {
      cancelled = true
    }
  }, [])

  if (!authReady) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-[#0a0a0a] text-white">
        <div className="text-sm text-white/60">Restoring workspace...</div>
      </div>
    )
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<PrivateRoute />}>
        <Route path="/" element={<ShellApp />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

export default App
