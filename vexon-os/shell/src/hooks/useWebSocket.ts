import { useEffect, useRef, useState } from 'react'
import { API_BASE_URL } from '../lib/api'
import { useStreamStore } from '../store/streamStore'
import { getToken } from '../lib/auth'

export const useWebSocket = (sessionId: string) => {
  const [isConnected, setIsConnected] = useState(false)
  const ws = useRef<WebSocket | null>(null)
  const addEvent = useStreamStore(state => state.addEvent)
  const token = getToken()

  useEffect(() => {
    if (!sessionId || !token) {
      setIsConnected(false)
      return
    }

    let cancelled = false
    let retryHandle: number | null = null
    let retryDelayMs = 1000

    const connect = async () => {
      const apiUrl = new URL(API_BASE_URL)
      const protocol = apiUrl.protocol === 'https:' ? 'wss:' : 'ws:'
      const url = `${protocol}//${apiUrl.host}/ws/${sessionId}?token=${encodeURIComponent(token)}`

      if (cancelled) {
        return
      }

      const socket = new WebSocket(url)
      ws.current = socket

      socket.onopen = () => {
        if (ws.current !== socket || cancelled) {
          socket.close()
          return
        }
        retryDelayMs = 1000
        setIsConnected(true)
      }

      socket.onmessage = (event) => {
        if (ws.current !== socket || cancelled) {
          return
        }
        try {
          const data = JSON.parse(event.data)
          if (data?.type === 'ping') {
            return
          }
          if (data?.session_id && data.session_id !== sessionId) {
            return
          }
          addEvent(data)
        } catch (e) {
          console.error('Failed to parse WS message', e)
        }
      }

      socket.onerror = () => {
        setIsConnected(false)
      }

      socket.onclose = () => {
        if (ws.current === socket) {
          ws.current = null
        }
        if (!cancelled) {
          setIsConnected(false)
          retryHandle = window.setTimeout(() => {
            void connect()
          }, retryDelayMs)
          retryDelayMs = Math.min(retryDelayMs * 2, 5000)
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
        ws.current = null
      }
    }
  }, [sessionId, addEvent, token])

  const sendMessage = (message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message))
    }
  }

  return { isConnected, sendMessage }
}
