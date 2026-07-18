import { Link } from 'react-router-dom'
import type { Vehicle } from '../../types/vehicle'
import { Badge } from '../ui/Badge'

interface VehicleTableProps {
  vehicles: Vehicle[]
  canWrite: boolean
  canDelete: boolean
  onEdit: (vehicle: Vehicle) => void
  onDeactivate: (vehicle: Vehicle) => void
}

const statusTone = {
  activo: 'gold',
  taller: 'muted',
  inactivo: 'danger',
} as const

const typeLabels: Record<string, string> = {
  camion: 'Camión',
  remolque: 'Remolque',
  cabezal: 'Cabezal',
}

export function VehicleTable({ vehicles, canWrite, canDelete, onEdit, onDeactivate }: VehicleTableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface text-text-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Placa</th>
            <th className="px-4 py-3 font-medium">Marca / Modelo</th>
            <th className="px-4 py-3 font-medium">Tipo</th>
            <th className="px-4 py-3 font-medium">Odómetro</th>
            <th className="px-4 py-3 font-medium">Estado</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {vehicles.map((vehicle) => (
            <tr key={vehicle.id} className="bg-background/40">
              <td className="px-4 py-3">
                <Link to={`/vehicles/${vehicle.id}`} className="text-gold hover:underline">
                  {vehicle.plate}
                </Link>
              </td>
              <td className="px-4 py-3 text-text-muted">
                {vehicle.brand} {vehicle.model} ({vehicle.year})
              </td>
              <td className="px-4 py-3">{typeLabels[vehicle.type] ?? vehicle.type}</td>
              <td className="px-4 py-3 text-text-muted">{vehicle.current_odometer_km.toLocaleString()} km</td>
              <td className="px-4 py-3">
                <Badge tone={statusTone[vehicle.status]}>{vehicle.status}</Badge>
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex justify-end gap-3">
                  {canWrite && (
                    <button onClick={() => onEdit(vehicle)} className="text-text-muted hover:text-gold">
                      Editar
                    </button>
                  )}
                  {canDelete && vehicle.status !== 'inactivo' && (
                    <button
                      onClick={() => onDeactivate(vehicle)}
                      className="text-text-muted hover:text-danger"
                    >
                      Desactivar
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
          {vehicles.length === 0 && (
            <tr>
              <td colSpan={6} className="px-4 py-8 text-center text-text-muted">
                No hay vehículos para mostrar.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
