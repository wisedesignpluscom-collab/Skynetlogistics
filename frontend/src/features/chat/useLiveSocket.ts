import { useEffect, useRef } from 'react'
import { getAccessToken } from '../../lib/axios'

/**
 * Conexión WebSocket en vivo (dispatcher o conductor, ver app/api/v1/ws.py). El auth va por query
 * param porque el handshake de WebSocket del navegador no permite headers custom. Reconecta con un
 * backoff simple ante cierre inesperado; `onEvent` recibe el payload ya parseado.
 */
export function useLiveSocket(kind: 'company' | 'driver', onEvent: (payload: Record<string, unknown>) => void) {
  const onEventRef = useRef(onEvent)
  onEventRef.current = onEvent

  useEffect(() => {
    const token = getAccessToken()
    if (!token) return

    let socket: WebSocket | null = null
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null
    let closedByCleanup = false

    function connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      socket = new WebSocket(`${protocol}://${window.location.host}/api/v1/ws/${kind}?token=${token}`)

      socket.onmessage = (event) => {
        try {
          onEventRef.current(JSON.parse(event.data))
        } catch {
          // ignora mensajes no-JSON
        }
      }

      socket.onclose = () => {
        if (!closedByCleanup) {
          reconnectTimer = setTimeout(connect, 3000)
        }
      }
    }

    connect()

    return () => {
      closedByCleanup = true
      if (reconnectTimer) clearTimeout(reconnectTimer)
      socket?.close()
    }
  }, [kind])
}
