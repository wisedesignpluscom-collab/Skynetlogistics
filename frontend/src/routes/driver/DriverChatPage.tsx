import { useEffect, useState } from 'react'
import { DriverPortalLayout } from '../../layouts/DriverPortalLayout'
import { ChatThreadView } from '../../components/chat/ChatThreadView'
import { getMyGeneralThread } from '../../features/chat/api'

export function DriverChatPage() {
  const [threadId, setThreadId] = useState<string | null>(null)

  useEffect(() => {
    void getMyGeneralThread().then((thread) => setThreadId(thread.id))
  }, [])

  return (
    <DriverPortalLayout title="Chat con despacho">
      <div className="h-[calc(100vh-8rem)]">
        {threadId ? (
          <ChatThreadView threadId={threadId} socketKind="driver" />
        ) : (
          <p className="text-sm text-text-muted">Cargando…</p>
        )}
      </div>
    </DriverPortalLayout>
  )
}
