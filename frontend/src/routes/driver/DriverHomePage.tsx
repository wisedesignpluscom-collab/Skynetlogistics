import { useState } from 'react'
import { Link } from 'react-router-dom'
import { DriverPortalLayout } from '../../layouts/DriverPortalLayout'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { IncidentReportFormModal } from '../../components/driver/IncidentReportFormModal'
import { useMyIncidentReports } from '../../features/incidents/hooks'
import { INCIDENT_STATUS_LABELS, INCIDENT_TYPE_LABELS } from '../../types/incident'
import type { IncidentStatus } from '../../types/incident'

const statusTone: Record<IncidentStatus, 'muted' | 'warning' | 'success'> = {
  reportado: 'warning',
  en_atencion: 'warning',
  resuelto: 'success',
}

export function DriverHomePage() {
  const { items, reload } = useMyIncidentReports()
  const [showForm, setShowForm] = useState(false)

  return (
    <DriverPortalLayout title="Mis reportes">
      <div className="flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-3">
          <Button onClick={() => setShowForm(true)}>Reportar incidencia</Button>
          <Link to="/driver/chat">
            <Button variant="secondary" className="w-full">
              Chat con despacho
            </Button>
          </Link>
          <Link to="/driver/deliveries" className="col-span-2">
            <Button variant="secondary" className="w-full">
              Mis entregas
            </Button>
          </Link>
        </div>

        <div className="flex flex-col gap-2">
          {items.length === 0 && (
            <p className="text-sm text-text-muted">Todavía no has enviado ningún reporte.</p>
          )}
          {items.map((incident) => (
            <Link
              key={incident.id}
              to={`/driver/incidents/${incident.id}`}
              className="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3 hover:bg-surface-hover"
            >
              <div>
                <p className="text-sm text-text">{INCIDENT_TYPE_LABELS[incident.type]}</p>
                <p className="text-xs text-text-muted">{new Date(incident.created_at).toLocaleString()}</p>
              </div>
              <Badge tone={statusTone[incident.status]}>{INCIDENT_STATUS_LABELS[incident.status]}</Badge>
            </Link>
          ))}
        </div>
      </div>

      {showForm && (
        <IncidentReportFormModal onClose={() => setShowForm(false)} onCreated={reload} />
      )}
    </DriverPortalLayout>
  )
}
