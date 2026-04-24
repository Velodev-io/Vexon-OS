import React from 'react'
import Topbar from '../components/Topbar'
import Sidebar from '../components/Sidebar'
import MainCanvas from '../components/MainCanvas'
import IntentBar from '../components/IntentBar'

interface ShellProps {
  sessionId: string;
  isConnected: boolean;
}

const Shell: React.FC<ShellProps> = ({ sessionId, isConnected }) => {
  return (
    <div className="flex-1 flex flex-col overflow-hidden relative">
      <Topbar isConnected={isConnected} />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 relative flex flex-col min-w-0">
          <MainCanvas />
          <div className="absolute bottom-0 left-0 right-0 p-6 pointer-events-none">
            <IntentBar sessionId={sessionId} />
          </div>
        </main>
      </div>
    </div>
  )
}

export default Shell
