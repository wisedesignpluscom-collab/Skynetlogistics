import { Link } from 'react-router-dom'
import type { Trip } from '../../types/trip'
import { Badge } from '../ui/Badge'

interface TripTableProps {
  trips: Trip[]
}

const statusTone = {
  planificado: 'muted',
  en_curso: 'gold',
  completado: 'gold',
  cancelado: 'danger',
} as const

export function TripTable({ trips }: TripTableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface text-text-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Ruta</th>
            <th className="px-4 py-3 font-medium">Carga</th>
            <th className="px-4 py-3 font-medium">Distancia</th>
            <th className="px-4 py-3 font-medium">Flete</th>
            <th className="px-4 py-3 font-medium">Estado</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {trips.map((trip) => (
            <tr key={trip.id} className="bg-background/40">
              <td className="px-4 py-3">
                <Link to={`/trips/${trip.id}`} className="text-gold hover:underline">
                  {trip.origin} → {trip.destination}
                </Link>
              </td>
              <td className="px-4 py-3 text-text-muted">{trip.cargo_type}</td>
              <td className="px-4 py-3 text-text-muted">
                {trip.distance_km !== null ? `${trip.distance_km} km` : '—'}
              </td>
              <td className="px-4 py-3 text-text-muted">
                {trip.freight_cost !== null ? `$${trip.freight_cost}` : '—'}
              </td>
              <td className="px-4 py-3">
                <Badge tone={statusTone[trip.status]}>{trip.status}</Badge>
              </td>
            </tr>
          ))}
          {trips.length === 0 && (
            <tr>
              <td colSpan={5} className="px-4 py-8 text-center text-text-muted">
                No hay viajes para mostrar.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
