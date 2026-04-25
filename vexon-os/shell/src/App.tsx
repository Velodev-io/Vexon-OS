import { useEffect } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import PrivateRoute from './components/PrivateRoute'
import { useWebSocket } from './hooks/useWebSocket'
import Login from './pages/Login'
import Shell from './pages/Shell'
import { useStreamStore } from './store/streamStore'

function generateSessionId() {
  try {
    return crypto.randomUUID()
  } catch {
    return Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2)
  }
}

function ShellApp() {
  const activeSessionId = useStreamStore((state) => state.activeSessionId)
  const setActiveSession = useStreamStore((state) => state.setActiveSession)

  useEffect(() => {
    if (!activeSessionId) {
      setActiveSession(generateSessionId())
    }
  }, [activeSessionId, setActiveSession])

  const { isConnected } = useWebSocket(activeSessionId || '')

  return (
    <div className="h-screen w-full flex flex-col bg-[#0a0a0a] text-white selection:bg-white/10">
      <Shell sessionId={activeSessionId || ''} isConnected={isConnected} />
    </div>
  )
}

function App() {
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
