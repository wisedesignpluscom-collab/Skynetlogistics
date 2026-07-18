import { Link } from 'react-router-dom'
import type { Driver } from '../../types/driver'
import type { DriverFatigueSummary } from '../../types/fatigue'
import { Badge } from '../ui/Badge'

interface DriverTableProps {
  drivers: Driver[]
  canWrite: boolean
  canDelete: boolean
  fatigueByDriver?: Record<string, DriverFatigueSummary>
  onEdit: (driver: Driver) => void
  onDeactivate: (driver: Driver) => void
}

const statusTone = {
  activo: 'gold',
  suspendido: 'muted',
  inactivo: 'danger',
} as const

const riskTone = {
  bajo: 'muted',
  medio: 'muted',
  alto: 'danger',
  critico: 'danger',
} as const

function isExpiringSoon(licenseExpiry: string): boolean {
  const daysLeft = (new Date(licenseExpiry).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  return daysLeft <= 30
}

export function DriverTable({
  drivers,
  canWrite,
  canDelete,
  fatigueByDriver = {},
  onEdit,
  onDeactivate,
}: DriverTableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface text-text-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Nombre</th>
            <th className="px-4 py-3 font-medium">Licencia</th>
            <th className="px-4 py-3 font-medium">Vence</th>
            <th className="px-4 py-3 font-medium">Teléfono</th>
            <th className="px-4 py-3 font-medium">Estado</th>
            <th className="px-4 py-3 font-medium">Fatiga</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {drivers.map((driver) => {
            const fatigue = fatigueByDriver[driver.id]
            return (
              <tr key={driver.id} className="bg-background/40">
                <td className="px-4 py-3">
                  <Link to={`/drivers/${driver.id}`} className="text-text hover:text-gold">
                    {driver.name}
                  </Link>
                </td>
                <td className="px-4 py-3 text-text-muted">{driver.license_number}</td>
                <td className="px-4 py-3">
                  <span className={isExpiringSoon(driver.license_expiry) ? 'text-danger' : 'text-text-muted'}>
                    {driver.license_expiry}
                  </span>
                </td>
                <td className="px-4 py-3 text-text-muted">{driver.phone ?? '—'}</td>
                <td className="px-4 py-3">
                  <Badge tone={statusTone[driver.status]}>{driver.status}</Badge>
                </td>
                <td className="px-4 py-3">
                  {fatigue?.risk_level ? (
                    <Badge tone={riskTone[fatigue.risk_level]}>{fatigue.risk_level}</Badge>
                  ) : (
                    <span className="text-text-muted">—</span>
                  )}
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex justify-end gap-3">
                    {canWrite && (
                      <button onClick={() => onEdit(driver)} className="text-text-muted hover:text-gold">
                        Editar
                      </button>
                    )}
                    {canDelete && driver.status !== 'inactivo' && (
                      <button
                        onClick={() => onDeactivate(driver)}
                        className="text-text-muted hover:text-danger"
                      >
                        Desactivar
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            )
          })}
          {drivers.length === 0 && (
            <tr>
              <td colSpan={7} className="px-4 py-8 text-center text-text-muted">
                No hay conductores para mostrar.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
