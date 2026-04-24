import { Wifi, WifiOff } from 'lucide-react'
import { useStreamStore } from '../store/streamStore'

const Topbar = ({ isConnected }: { isConnected: boolean }) => {
  const activeAgents = useStreamStore(state => state.activeAgents)
  const activeCount = Object.values(activeAgents).filter(a => !['done', 'error'].includes(a.status)).length

  return (
    <header className="h-14 border-b border-white/10 flex items-center justify-between px-6 glass z-20">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center">
          <span className="text-black font-bold text-xl leading-none">V</span>
        </div>
        <h1 className="font-semibold text-lg tracking-tight">Vexon OS</h1>
      </div>
      
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-[11px] font-medium text-white/50 bg-white/5 px-3 py-1.5 rounded-full border border-white/5">
          <div className={`w-1.5 h-1.5 rounded-full ${activeCount > 0 ? 'bg-green-500 animate-pulse' : 'bg-white/20'}`} />
          <span className="uppercase tracking-wider">{activeCount} Kernel{activeCount !== 1 ? 's' : ''} Running</span>
        </div>
        
        <div className="flex items-center gap-2">
          {isConnected ? (
            <div className="flex items-center gap-2 text-[11px] font-medium text-green-400 uppercase tracking-wider">
              <Wifi size={14} />
              <span>Kernel Connected</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-[11px] font-medium text-red-400 uppercase tracking-wider">
              <WifiOff size={14} />
              <span>Kernel Link Lost</span>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export default Topbar
