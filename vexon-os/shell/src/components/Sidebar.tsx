import { useEffect, useState } from 'react'
import { History, Cpu, Database, ChevronLeft, ChevronRight } from 'lucide-react'
import { motion } from 'framer-motion'
import api from '../lib/api'
import { getToken } from '../lib/auth'
import { useStreamStore } from '../store/streamStore'

function formatTime(value: string | null) {
  if (!value) {
    return 'Just now'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return 'Recent'
  }

  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date)
}

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [activeTab, setActiveTab] = useState('sessions')
  const [isLoadingSessions, setIsLoadingSessions] = useState(false)
  const [sessionError, setSessionError] = useState<string | null>(null)
  const sessions = useStreamStore((state) => state.sessions)
  const activeSessionId = useStreamStore((state) => state.activeSessionId)
  const setSessions = useStreamStore((state) => state.setSessions)
  const setActiveSession = useStreamStore((state) => state.setActiveSession)

  useEffect(() => {
    let cancelled = false

    const loadSessions = async () => {
      setIsLoadingSessions(true)
      setSessionError(null)
      if (!getToken()) {
        if (!cancelled) {
          setSessions([])
          setIsLoadingSessions(false)
        }
        return
      }

      try {
        const { data } = await api.get('/sessions')
        if (cancelled) {
          return
        }
        const orderedSessions = Array.isArray(data) ? data : []
        if (orderedSessions.length > 0) {
          setSessions(orderedSessions)
          const hasActiveSession = orderedSessions.some((session: any) => session.session_id === activeSessionId)
          if (!hasActiveSession) {
            setActiveSession(orderedSessions[0].session_id)
          }
          return
        }

        const { data: session } = await api.post('/sessions', {
          title: 'New session',
        })
        if (!cancelled) {
          setSessions([session])
          setActiveSession(session.session_id)
        }
      } catch (error) {
        if (!cancelled) {
          setSessionError('Unable to load sessions.')
          setSessions([])
        }
      } finally {
        if (!cancelled) {
          setIsLoadingSessions(false)
        }
      }
    }

    void loadSessions()

    return () => {
      cancelled = true
    }
  }, [activeSessionId, setActiveSession, setSessions])

  const tabs = [
    { id: 'sessions', icon: History, label: 'Sessions' },
    { id: 'agents', icon: Cpu, label: 'Agents' },
    { id: 'memory', icon: Database, label: 'Memory' },
  ]

  return (
    <aside 
      className={`h-full border-r border-white/10 flex flex-col glass transition-all duration-300 z-10 ${isCollapsed ? 'w-16' : 'w-64'}`}
    >
      <div className="flex-1 flex flex-col">
        <nav className="p-3 space-y-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-colors relative group ${activeTab === tab.id ? 'bg-white/10 text-white' : 'text-white/50 hover:bg-white/5 hover:text-white'}`}
            >
              <tab.icon size={20} />
              {!isCollapsed && <span className="font-medium text-sm tracking-tight">{tab.label}</span>}
              {activeTab === tab.id && (
                <motion.div 
                  layoutId="activeTab"
                  className="absolute left-0 w-1 h-6 bg-white rounded-r-full"
                />
              )}
            </button>
          ))}
        </nav>

        <div className="flex-1 p-4 overflow-y-auto scrollbar-hide">
          {!isCollapsed && (
            <div className="space-y-4">
              <h3 className="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] px-2">Recent Sessions</h3>
              <div className="space-y-2">
                {isLoadingSessions && (
                  <div className="p-3 rounded-xl border border-white/5 bg-white/[0.02]">
                    <p className="text-xs font-medium text-white/60">Loading sessions...</p>
                  </div>
                )}
                {sessionError && (
                  <div className="p-3 rounded-xl border border-red-500/20 bg-red-500/5">
                    <p className="text-xs font-medium text-red-300">{sessionError}</p>
                  </div>
                )}
                {sessions.length === 0 && (
                  <div className="p-3 rounded-xl border border-white/5 bg-white/[0.02]">
                    <p className="text-xs font-medium text-white/60">
                      {getToken() ? 'No sessions yet.' : 'Sign in to load sessions.'}
                    </p>
                  </div>
                )}
                {sessions.map((session) => (
                  <button
                    key={session.session_id}
                    type="button"
                    onClick={() => setActiveSession(session.session_id)}
                    className={`w-full text-left p-3 rounded-xl border transition-all cursor-pointer bg-white/[0.02] group ${
                      activeSessionId === session.session_id
                        ? 'border-white/20 bg-white/[0.06]'
                        : 'border-white/5 hover:border-white/20'
                    }`}
                  >
                    <p className="text-xs font-medium truncate text-white/80 group-hover:text-white transition-colors">
                      {session.title || 'Untitled session'}
                    </p>
                    <p className="text-[10px] text-white/30 mt-1.5 font-medium uppercase tracking-wider">
                      {formatTime(session.last_active)}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <button 
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="p-4 border-t border-white/10 flex items-center justify-center text-white/20 hover:text-white transition-colors"
      >
        {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
      </button>
    </aside>
  )
}

export default Sidebar
