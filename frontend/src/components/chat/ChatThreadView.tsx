import { useCallback, useEffect, useRef, useState } from 'react'
import { Button } from '../ui/Button'
import { listThreadMessages, sendThreadMessage } from '../../features/chat/api'
import { useLiveSocket } from '../../features/chat/useLiveSocket'
import type { ChatMessage } from '../../types/chat'

interface ChatThreadViewProps {
  threadId: string
  socketKind: 'company' | 'driver'
}

export function ChatThreadView({ threadId, socketKind }: ChatThreadViewProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [draft, setDraft] = useState('')
  const [isSending, setIsSending] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const reload = useCallback(() => {
    void listThreadMessages(threadId).then(setMessages)
  }, [threadId])

  useEffect(() => {
    reload()
  }, [reload])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useLiveSocket(socketKind, (payload) => {
    if (payload.event === 'chat_message' && payload.thread_id === threadId) {
      reload()
    }
  })

  async function handleSend() {
    if (!draft.trim()) return
    setIsSending(true)
    try {
      await sendThreadMessage(threadId, draft.trim())
      setDraft('')
      reload()
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="flex h-full flex-col gap-3">
      <div className="flex flex-1 flex-col gap-2 overflow-y-auto rounded-md border border-border bg-surface p-3">
        {messages.length === 0 && <p className="text-sm text-text-muted">Sin mensajes todavía.</p>}
        {messages.map((m) => (
          <div
            key={m.id}
            className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
              m.sender_type === 'conductor'
                ? 'self-start bg-surface-hover text-text'
                : 'self-end bg-gold/15 text-gold-soft'
            }`}
          >
            <p>{m.message}</p>
            <p className="mt-1 text-[10px] text-text-muted">
              {m.sender_type === 'conductor' ? 'Conductor' : 'Despachador'} ·{' '}
              {new Date(m.created_at).toLocaleString()}
            </p>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="flex gap-2">
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              void handleSend()
            }
          }}
          placeholder="Escribe un mensaje…"
          className="flex-1 rounded-md border border-border bg-surface px-3 py-2 text-text placeholder:text-text-muted/60 focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
        />
        <Button onClick={() => void handleSend()} disabled={isSending || !draft.trim()}>
          Enviar
        </Button>
      </div>
    </div>
  )
}
