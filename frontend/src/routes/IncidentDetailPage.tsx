import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { ChatThreadView } from '../components/chat/ChatThreadView'
import { getIncidentReport, updateIncidentReportStatus } from '../features/incidents/api'
import { getIncidentThread } from '../features/chat/api'
import {
  INCIDENT_SEVERITY_LABELS,
  INCIDENT_STATUS_LABELS,
  INCIDENT_TYPE_LABELS,
} from '../types/incident'
import type { IncidentReport, IncidentStatus } from '../types/incident'

export function IncidentDetailPage() {
  const { incidentId } = useParams<{ incidentId: string }>()
  const [incident, setIncident] = useState<IncidentReport | null>(null)
  const [threadId, setThreadId] = useState<string | null>(null)
  const [status, setStatus] = useState<IncidentStatus>('reportado')
  const [notes, setNotes] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  function load() {
    if (!incidentId) return
    void getIncidentReport(incidentId).then((data) => {
      setIncident(data)
      setStatus(data.status)
      setNotes(data.resolution_notes ?? '')
    })
    void getIncidentThread(incidentId).then((thread) => setThreadId(thread.id))
  }

  useEffect(load, [incidentId])

  async function handleSave() {
    if (!incidentId) return
    setIsSaving(true)
    try {
      await updateIncidentReportStatus(incidentId, { status, resolution_notes: notes || null })
      load()
    } finally {
      setIsSaving(false)
    }
  }

  if (!incident) {
    return (
      <DashboardLayout>
        <p className="text-text-muted">Cargando…</p>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center gap-3">
        <h1 className="font-display text-2xl text-text">{INCIDENT_TYPE_LABELS[incident.type]}</h1>
        <Badge>{INCIDENT_SEVERITY_LABELS[incident.severity]}</Badge>
        <Badge tone="muted">{INCIDENT_STATUS_LABELS[incident.status]}</Badge>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="flex flex-col gap-4">
          <div className="rounded-md border border-border bg-surface p-4">
            <p className="text-sm text-text-muted">Descripción</p>
            <p className="mt-1 text-sm text-text">{incident.description}</p>
          </div>

          <div className="flex flex-col gap-3 rounded-md border border-border bg-surface p-4">
            <div className="flex flex-col gap-1">
              <label className="text-sm text-text-muted" htmlFor="status">
                Estado
              </label>
              <select
                id="status"
                value={status}
                onChange={(e) => setStatus(e.target.value as IncidentStatus)}
                className="rounded-md border border-border bg-background px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
              >
                {Object.entries(INCIDENT_STATUS_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm text-text-muted" htmlFor="notes">
                Notas de resolución
              </label>
              <textarea
                id="notes"
                rows={3}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="rounded-md border border-border bg-background px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
              />
            </div>
            <Button onClick={() => void handleSave()} disabled={isSaving}>
              {isSaving ? 'Guardando…' : 'Guardar'}
            </Button>
          </div>
        </div>

        <div className="h-[32rem]">
          {threadId && <ChatThreadView threadId={threadId} socketKind="company" />}
        </div>
      </div>
    </DashboardLayout>
  )
}
