import React, { useState } from 'react'
import { Send, Mic, Paperclip, Terminal as TerminalIcon } from 'lucide-react'

const IntentBar = ({ sessionId }: { sessionId: string }) => {
  const [value, setValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!value.trim() || isLoading) return

    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:8000/intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: value,
          session_id: sessionId,
          user_id: 'default-user'
        })
      })
      if (response.ok) {
        setValue('')
      }
    } catch (error) {
      console.error('Failed to submit intent', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form 
      onSubmit={handleSubmit}
      className="max-w-4xl mx-auto w-full glass rounded-[24px] border border-white/10 glow p-2 flex items-center gap-2 pointer-events-auto shadow-2xl shadow-black"
    >
      <div className="flex items-center gap-1 ml-2">
        <button type="button" className="p-2.5 text-white/20 hover:text-white transition-all hover:bg-white/5 rounded-xl">
          <Paperclip size={20} />
        </button>
        <button type="button" className="p-2.5 text-white/20 hover:text-white transition-all hover:bg-white/5 rounded-xl">
          <Mic size={20} />
        </button>
      </div>

      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="How can Vexon help you today?"
        className="flex-1 bg-transparent border-none outline-none text-[15px] py-4 px-3 text-white placeholder:text-white/20 font-medium"
      />

      <div className="flex items-center gap-3 mr-1">
        {value.startsWith('/') && (
          <div className="hidden sm:flex items-center gap-2 px-3 py-2 bg-white/[0.03] rounded-xl border border-white/10">
            <TerminalIcon size={14} className="text-white/40" />
            <span className="text-[10px] font-black text-white/30 uppercase tracking-[0.15em]">Kernel Command</span>
          </div>
        )}
        <button 
          disabled={!value.trim() || isLoading}
          className="bg-white text-black h-11 w-11 flex items-center justify-center rounded-[18px] disabled:opacity-20 disabled:grayscale transition-all hover:scale-105 active:scale-95 shadow-lg shadow-white/10"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin" />
          ) : (
            <Send size={20} fill="black" />
          )}
        </button>
      </div>
    </form>
  )
}

export default IntentBar
