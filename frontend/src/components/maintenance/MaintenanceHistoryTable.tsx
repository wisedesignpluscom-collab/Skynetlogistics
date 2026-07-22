import type { MaintenanceTaskWithRecords, TrafficLight } from '../../types/maintenance'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'

interface MaintenanceHistoryTableProps {
  tasks: MaintenanceTaskWithRecords[]
  canComplete: boolean
  onComplete: (task: MaintenanceTaskWithRecords) => void
}

const statusTone = {
  pendiente: 'muted',
  en_proceso: 'gold',
  completada: 'gold',
  vencida: 'danger',
  cancelada: 'muted',
} as const

const trafficLightTone: Record<TrafficLight, 'success' | 'warning' | 'danger'> = {
  verde: 'success',
  amarillo: 'warning',
  rojo: 'danger',
}

const trafficLightLabel: Record<TrafficLight, string> = {
  verde: 'Al día',
  amarillo: 'Por vencer',
  rojo: 'Vencida',
}

export function MaintenanceHistoryTable({ tasks, canComplete, onComplete }: MaintenanceHistoryTableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface text-text-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Tipo</th>
            <th className="px-4 py-3 font-medium">Vence</th>
            <th className="px-4 py-3 font-medium">Estado</th>
            <th className="px-4 py-3 font-medium">Semáforo</th>
            <th className="px-4 py-3 font-medium">Costo</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {tasks.map((task) => {
            const totalCost = task.records.reduce((sum, r) => sum + r.cost_labor + r.cost_parts, 0)
            return (
              <tr key={task.id} className="bg-background/40">
                <td className="px-4 py-3 capitalize">{task.type}</td>
                <td className="px-4 py-3 text-text-muted">
                  {task.scheduled_by === 'tiempo' ? task.due_date : `${task.due_km?.toLocaleString()} km`}
                </td>
                <td className="px-4 py-3">
                  <Badge tone={statusTone[task.status]}>{task.status}</Badge>
                </td>
                <td className="px-4 py-3">
                  {task.traffic_light ? (
                    <Badge tone={trafficLightTone[task.traffic_light]}>
                      {trafficLightLabel[task.traffic_light]}
                    </Badge>
                  ) : (
                    <span className="text-text-muted">—</span>
                  )}
                </td>
                <td className="px-4 py-3 text-text-muted">
                  {task.records.length > 0 ? `$${totalCost.toFixed(2)}` : '—'}
                </td>
                <td className="px-4 py-3 text-right">
                  {canComplete && (task.status === 'pendiente' || task.status === 'en_proceso') && (
                    <Button variant="secondary" onClick={() => onComplete(task)}>
                      Completar
                    </Button>
                  )}
                </td>
              </tr>
            )
          })}
          {tasks.length === 0 && (
            <tr>
              <td colSpan={6} className="px-4 py-8 text-center text-text-muted">
                Este vehículo no tiene historial de mantenimiento.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
