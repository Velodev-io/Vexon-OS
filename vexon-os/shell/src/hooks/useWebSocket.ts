import { useEffect, useRef, useState } from 'react'
import { useStreamStore } from '../store/streamStore'

export const useWebSocket = (sessionId: string) => {
  const [isConnected, setIsConnected] = useState(false)
  const ws = useRef<WebSocket | null>(null)
  const addEvent = useStreamStore(state => state.addEvent)

  useEffect(() => {
    if (!sessionId) return

    const connect = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      // Use the current hostname (Mac Mini IP) but force port 8000 for the API
      const apiHost = window.location.hostname;
      const url = `${protocol}//${apiHost}:8000/ws/${sessionId}`
      
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
        setTimeout(connect, 3000)
      }
    }

    connect()

    return () => {
      if (ws.current) {
        // Remove the onclose handler so it doesn't trigger a retry
        ws.current.onclose = null;
        ws.current.close();
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
