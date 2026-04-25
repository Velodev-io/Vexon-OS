import { useEffect, useRef, useState } from 'react'
import { useStreamStore } from '../store/streamStore'
import { getToken } from '../lib/auth'

export const useWebSocket = (sessionId: string) => {
  const [isConnected, setIsConnected] = useState(false)
  const ws = useRef<WebSocket | null>(null)
  const addEvent = useStreamStore(state => state.addEvent)

  useEffect(() => {
    if (!sessionId) return

    let cancelled = false
    let retryHandle: number | null = null

    const connect = async () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const apiHost = window.location.hostname
      const token = getToken()
      const params = token ? `?token=${encodeURIComponent(token)}` : ''
      const url = `${protocol}//${apiHost}:8000/ws/${sessionId}${params}`

      if (cancelled) {
        return
      }
      
      console.log(`Connecting to WebSocket: ${url}`);
      ws.current = new WebSocket(url)

      ws.current.onopen = () => {
        setIsConnected(true)
        console.log('WS Connected')
      }

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          addEvent(data)
        } catch (e) {
          console.error('Failed to parse WS message', e)
        }
      }

      ws.current.onclose = () => {
        setIsConnected(false)
        console.log('WS Disconnected, retrying in 3s...')
        if (!cancelled) {
          retryHandle = window.setTimeout(() => {
            void connect()
          }, 3000)
        }
      }
    }

    void connect()

    return () => {
      cancelled = true
      if (retryHandle !== null) {
        window.clearTimeout(retryHandle)
      }
      if (ws.current) {
        ws.current.onclose = null
        ws.current.close()
      }
    }
  }, [sessionId, addEvent])

  const sendMessage = (message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message))
    }
  }

  return { isConnected, sendMessage }
}
