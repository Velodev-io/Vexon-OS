import React, { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useStreamStore } from '../store/streamStore'
import { Box, Sparkles, Terminal, Search, Globe, CheckCircle, Loader, ExternalLink } from 'lucide-react'

const AGENT_ICONS: Record<string, React.ReactNode> = {
  RESEARCHER: <Search size={18} className="text-blue-400/80" />,
  CODER: <Terminal size={18} className="text-green-400/80" />,
  AGENT: <Box size={18} className="text-white/50" />,
}

const AGENT_COLORS: Record<string, string> = {
  RESEARCHER: 'text-blue-400/60',
  CODER: 'text-green-400/60',
  AGENT: 'text-white/20',
}

const MainCanvas = () => {
  const activeAgents = useStreamStore(state => state.activeAgents)
  const events = useStreamStore(state => state.events)
  const agentIds = Object.keys(activeAgents)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events.length])

  if (agentIds.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="max-w-md w-full text-center space-y-8">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-20 h-20 bg-white/[0.03] rounded-3xl flex items-center justify-center mx-auto border border-white/10 glow"
          >
            <Sparkles className="text-white/50" size={36} />
          </motion.div>
          <div className="space-y-3">
            <h2 className="text-3xl font-semibold tracking-tight text-white/90">Vexon OS is online.</h2>
            <p className="text-sm text-white/40 leading-relaxed font-medium">
              Interact with the AI-Native kernel through natural language. 
              Spawn agents, execute code, and manage your neural memory.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-3 text-left">
            {[
              { label: 'Research', cmd: '/research', desc: 'Deep knowledge retrieval' },
              { label: 'Execute', cmd: '/code', desc: 'Run sandboxed tasks' },
              { label: 'Recall', cmd: '/memory', desc: 'Query personal context' },
              { label: 'Status', cmd: '/agents', desc: 'Monitor active kernels' }
            ].map(item => (
              <div key={item.cmd} className="p-4 rounded-2xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.05] hover:border-white/20 transition-all cursor-pointer group">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[11px] font-bold text-white/80">{item.label}</span>
                  <Terminal size={12} className="text-white/20 group-hover:text-white/40" />
                </div>
                <p className="text-[10px] text-white/30 font-medium">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-8 space-y-8 pb-40">
      <AnimatePresence initial={false}>
        {agentIds.map((agentId) => {
          const agent = activeAgents[agentId];
          const agentType = agent.agent_type || 'AGENT';
          const icon = AGENT_ICONS[agentType] || AGENT_ICONS['AGENT'];
          const colorClass = AGENT_COLORS[agentType] || AGENT_COLORS['AGENT'];

          return (
            <motion.div
              key={agentId}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-5 max-w-4xl mx-auto"
            >
              {/* Agent Icon */}
              <div className="w-10 h-10 rounded-2xl bg-white/[0.03] border border-white/10 flex items-center justify-center flex-shrink-0 glow">
                {icon}
              </div>

              <div className="flex-1 space-y-3 min-w-0">
                {/* Agent Header */}
                <div className="flex items-center gap-3 flex-wrap">
                  <span className={`text-[10px] font-black uppercase tracking-[0.2em] ${colorClass}`}>
                    {agentType}_KERNEL_{agentId.slice(0, 4)}
                  </span>
                  <span className="w-1 h-1 rounded-full bg-white/10" />
                  <div className="px-2 py-0.5 rounded-md bg-white/[0.05] border border-white/5">
                    <span className="text-[9px] font-bold text-white/40 uppercase tracking-widest">
                      {agent.status}
                    </span>
                  </div>
                </div>

                {/* Thinking state */}
                {agent.thinking_message && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-2 text-white/30 text-xs"
                  >
                    <Loader size={12} className="animate-spin" />
                    <span>{agent.thinking_message}</span>
                  </motion.div>
                )}

                {/* Tool Calls Trace - The "Neural Activity" of the kernel */}
                {agent.tool_calls && agent.tool_calls.map((tc: any, i: number) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="rounded-2xl border border-white/[0.08] bg-gradient-to-br from-white/[0.04] to-transparent p-5 backdrop-blur-md shadow-xl"
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${tc.status === 'running' ? 'bg-blue-500/20 text-blue-400' : 'bg-green-500/20 text-green-400'}`}>
                        {tc.tool === 'web_search' ? <Globe size={16} className={tc.status === 'running' ? 'animate-pulse' : ''} /> : <Terminal size={16} />}
                      </div>
                      <div className="flex flex-col">
                        <span className="text-[10px] font-black uppercase tracking-widest text-white/30">Action: {tc.tool}</span>
                        <span className="text-[13px] font-medium text-white/70">
                          {typeof tc.input === 'string' ? tc.input : tc.input?.query || 'Executing kernel command...'}
                        </span>
                      </div>
                      <div className="ml-auto">
                        {tc.status === 'running' ? (
                          <div className="flex items-center gap-2 px-2 py-1 rounded-full bg-white/[0.03] border border-white/10">
                            <Loader size={10} className="animate-spin text-white/40" />
                            <span className="text-[9px] font-bold text-white/30 uppercase tracking-tighter">Processing</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2 px-2 py-1 rounded-full bg-green-500/10 border border-green-500/20">
                            <CheckCircle size={10} className="text-green-400/80" />
                            <span className="text-[9px] font-bold text-green-400/60 uppercase tracking-tighter">Complete</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {tc.result && (
                      <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="pl-11"
                      >
                        <div className="p-3 rounded-xl bg-black/20 border border-white/5 text-[12px] text-white/50 leading-relaxed max-h-32 overflow-y-auto font-medium font-mono scrollbar-hide">
                          <span className="text-white/20 mr-2">OUTPUT_TRACE:</span>
                          {typeof tc.result === 'string' ? tc.result.slice(0, 500) : JSON.stringify(tc.result).slice(0, 500)}
                          {(typeof tc.result === 'string' ? tc.result : JSON.stringify(tc.result)).length > 500 && '...'}
                        </div>
                      </motion.div>
                    )}
                  </motion.div>
                ))}

                {/* Final Answer */}
                {agent.full_text && (
                  <div className="text-[15px] text-white/80 leading-relaxed font-medium selection:bg-white/20 whitespace-pre-wrap">
                    {agent.full_text}
                    {agent.status !== 'done' && agent.status !== 'error' && (
                      <span className="inline-block w-1 h-4 bg-white/50 ml-1 animate-pulse align-middle" />
                    )}
                  </div>
                )}

                {/* Pulse while waiting for first content */}
                {!agent.full_text && !agent.thinking_message && agent.status !== 'done' && (
                  <div className="flex gap-1 py-1">
                    {[0, 1, 2].map(i => (
                      <span
                        key={i}
                        className="w-1.5 h-1.5 rounded-full bg-white/20 animate-pulse"
                        style={{ animationDelay: `${i * 150}ms` }}
                      />
                    ))}
                  </div>
                )}

                {/* Sources — clickable links */}
                {agent.status === 'done' && agent.sources && agent.sources.length > 0 && (
                  <div className="pt-2 border-t border-white/[0.05]">
                    <p className="text-[10px] text-white/20 uppercase tracking-widest mb-2 font-bold">Sources</p>
                    <div className="flex flex-col gap-1">
                      {agent.sources.map((src: string, i: number) => (
                        <a
                          key={i}
                          href={src}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1.5 text-[11px] text-blue-400/60 hover:text-blue-400 transition-colors group"
                        >
                          <ExternalLink size={10} className="flex-shrink-0" />
                          <span className="truncate">{src}</span>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
      <div ref={bottomRef} />
    </div>
  )
}

export default MainCanvas
