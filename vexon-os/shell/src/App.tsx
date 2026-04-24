import { useState } from 'react'
import { useWebSocket } from './hooks/useWebSocket'
import Shell from './pages/Shell'

function App() {
  const [sessionId] = useState(() => crypto.randomUUID())
  const { isConnected } = useWebSocket(sessionId)

  return (
    <div className="h-screen w-full flex flex-col bg-[#0a0a0a] text-white selection:bg-white/10">
      <Shell sessionId={sessionId} isConnected={isConnected} />
    </div>
  )
}

export default App
