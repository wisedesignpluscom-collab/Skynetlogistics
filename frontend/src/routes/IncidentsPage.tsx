import { useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Badge } from '../components/ui/Badge'
import { useIncidentReports } from '../features/incidents/hooks'
import { useLiveSocket } from '../features/chat/useLiveSocket'
import {
  INCIDENT_SEVERITY_LABELS,
  INCIDENT_STATUS_LABELS,
  INCIDENT_TYPE_LABELS,
} from '../types/incident'
import type { IncidentSeverity, IncidentStatus } from '../types/incident'

const statusTone: Record<IncidentStatus, 'muted' | 'warning' | 'success'> = {
  reportado: 'warning',
  en_atencion: 'warning',
  resuelto: 'success',
}

const severityTone: Record<IncidentSeverity, 'muted' | 'warning' | 'danger'> = {
  baja: 'muted',
  media: 'muted',
  alta: 'warning',
  critica: 'danger',
}

export function IncidentsPage() {
  const [statusFilter, setStatusFilter] = useState<IncidentStatus | ''>('')
  const { items, total, isLoading, reload } = useIncidentReports({
    page_size: 50,
    status_filter: statusFilter || undefined,
  })

  useLiveSocket('company', (payload) => {
    if (payload.event === 'incident_report_created' || payload.event === 'incident_report_updated') {
      reload()
    }
  })

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Reportes de conductores</h1>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as IncidentStatus | '')}
          className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
        >
          <option value="">Todos los estados</option>
          {Object.entries(INCIDENT_STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <p className="text-text-muted">Cargando…</p>
      ) : total === 0 ? (
        <p className="text-text-muted">No hay reportes.</p>
      ) : (
        <div className="overflow-hidden rounded-md border border-border">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface text-text-muted">
              <tr>
                <th className="px-4 py-2">Tipo</th>
                <th className="px-4 py-2">Urgencia</th>
                <th className="px-4 py-2">Estado</th>
                <th className="px-4 py-2">Fecha</th>
              </tr>
            </thead>
            <tbody>
              {items.map((incident) => (
                <tr key={incident.id} className="border-t border-border hover:bg-surface-hover">
                  <td className="px-4 py-2">
                    <Link to={`/incidents/${incident.id}`} className="text-gold hover:underline">
                      {INCIDENT_TYPE_LABELS[incident.type]}
                    </Link>
                  </td>
                  <td className="px-4 py-2">
                    <Badge tone={severityTone[incident.severity]}>
                      {INCIDENT_SEVERITY_LABELS[incident.severity]}
                    </Badge>
                  </td>
                  <td className="px-4 py-2">
                    <Badge tone={statusTone[incident.status]}>{INCIDENT_STATUS_LABELS[incident.status]}</Badge>
                  </td>
                  <td className="px-4 py-2 text-text-muted">
                    {new Date(incident.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </DashboardLayout>
  )
}
