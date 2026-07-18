import type { Alert } from '../../types/alert'
import { Badge } from '../ui/Badge'

interface AlertListProps {
  alerts: Alert[]
  onMarkRead: (alert: Alert) => void
}

const severityTone = {
  alta: 'danger',
  media: 'gold',
  baja: 'muted',
} as const

export function AlertList({ alerts, onMarkRead }: AlertListProps) {
  if (alerts.length === 0) {
    return <p className="text-text-muted">No hay alertas para mostrar.</p>
  }

  return (
    <ul className="flex flex-col gap-2">
      {alerts.map((alert) => (
        <li
          key={alert.id}
          className={`flex items-center justify-between rounded-lg border border-border px-4 py-3 ${
            alert.status === 'no_leida' ? 'bg-surface' : 'bg-background/40 opacity-60'
          }`}
        >
          <div className="flex items-center gap-3">
            <Badge tone={severityTone[alert.severity]}>{alert.severity}</Badge>
            <span className="text-sm text-text">{alert.message}</span>
          </div>
          {alert.status === 'no_leida' && (
            <button onClick={() => onMarkRead(alert)} className="text-sm text-text-muted hover:text-gold">
              Marcar leída
            </button>
          )}
        </li>
      ))}
    </ul>
  )
}
