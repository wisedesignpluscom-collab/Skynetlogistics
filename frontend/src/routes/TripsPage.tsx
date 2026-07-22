import { useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { TripTable } from '../components/trips/TripTable'
import { TripFormModal } from '../components/trips/TripFormModal'
import { useTrips } from '../features/trips/hooks'
import { createTrip } from '../features/trips/api'
import { useAuth } from '../features/auth/AuthContext'
import type { TripStatus } from '../types/trip'

export function TripsPage() {
  const { hasPermission } = useAuth()
  const [statusFilter, setStatusFilter] = useState<TripStatus | ''>('')
  const { data, isLoading, error, reload } = useTrips({
    status_filter: statusFilter || undefined,
    page_size: 50,
  })
  const [showCreateModal, setShowCreateModal] = useState(false)

  const canWrite = hasPermission('trips', 'write')

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Viajes</h1>
        <div className="flex gap-3">
          {hasPermission('trips', 'read') && (
            <Link to="/clients">
              <Button variant="secondary">Clientes</Button>
            </Link>
          )}
          {hasPermission('trip_settings', 'read') && (
            <Link to="/trip-settings">
              <Button variant="secondary">Tabulados</Button>
            </Link>
          )}
          {canWrite && (
            <Link to="/trips-vrp">
              <Button variant="secondary">Optimizar rutas (VRP)</Button>
            </Link>
          )}
          {canWrite && <Button onClick={() => setShowCreateModal(true)}>Nuevo viaje</Button>}
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as TripStatus | '')}
          className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
        >
          <option value="">Todos los estados</option>
          <option value="planificado">Planificado</option>
          <option value="en_curso">En curso</option>
          <option value="completado">Completado</option>
          <option value="cancelado">Cancelado</option>
        </select>
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}
      {error && <p className="text-danger">{error}</p>}
      {data && <TripTable trips={data.items} />}

      {showCreateModal && (
        <TripFormModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={async (values) => {
            await createTrip(values)
            await reload()
          }}
        />
      )}
    </DashboardLayout>
  )
}
