import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { DriverPortalLayout } from '../../layouts/DriverPortalLayout'
import { Badge } from '../../components/ui/Badge'
import { ChatThreadView } from '../../components/chat/ChatThreadView'
import { getIncidentReport } from '../../features/incidents/api'
import { getIncidentThread } from '../../features/chat/api'
import { INCIDENT_SEVERITY_LABELS, INCIDENT_STATUS_LABELS, INCIDENT_TYPE_LABELS } from '../../types/incident'
import type { IncidentReport } from '../../types/incident'

export function DriverIncidentDetailPage() {
  const { incidentId } = useParams<{ incidentId: string }>()
  const [incident, setIncident] = useState<IncidentReport | null>(null)
  const [threadId, setThreadId] = useState<string | null>(null)

  useEffect(() => {
    if (!incidentId) return
    void getIncidentReport(incidentId).then(setIncident)
    void getIncidentThread(incidentId).then((thread) => setThreadId(thread.id))
  }, [incidentId])

  if (!incident) {
    return (
      <DriverPortalLayout title="Reporte">
        <p className="text-sm text-text-muted">Cargando…</p>
      </DriverPortalLayout>
    )
  }

  return (
    <DriverPortalLayout title={INCIDENT_TYPE_LABELS[incident.type]}>
      <div className="flex h-[calc(100vh-8rem)] flex-col gap-4">
        <div className="rounded-md border border-border bg-surface p-4">
          <div className="mb-2 flex items-center gap-2">
            <Badge>{INCIDENT_SEVERITY_LABELS[incident.severity]}</Badge>
            <Badge tone="muted">{INCIDENT_STATUS_LABELS[incident.status]}</Badge>
          </div>
          <p className="text-sm text-text">{incident.description}</p>
          {incident.resolution_notes && (
            <p className="mt-2 text-sm text-text-muted">Resolución: {incident.resolution_notes}</p>
          )}
        </div>
        <div className="flex-1">
          {threadId && <ChatThreadView threadId={threadId} socketKind="driver" />}
        </div>
      </div>
    </DriverPortalLayout>
  )
}
