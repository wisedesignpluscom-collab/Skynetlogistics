import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { FleetMap } from '../components/gps/FleetMap'
import { useFleetPositions } from '../features/gps/hooks'
import { useVehicles } from '../features/vehicles/hooks'
import { useAuth } from '../features/auth/AuthContext'
import type { Vehicle } from '../types/vehicle'

export function FleetMapPage() {
  const { hasPermission } = useAuth()
  const { positions, isLoading } = useFleetPositions()
  const { data: vehiclesPage } = useVehicles({ page_size: 200 })

  const vehiclesById = useMemo(() => {
    const map: Record<string, Vehicle> = {}
    for (const v of vehiclesPage?.items ?? []) {
      map[v.id] = v
    }
    return map
  }, [vehiclesPage])

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl text-text">Mapa en vivo de la flota</h1>
          <p className="text-text-muted">{positions.length} vehículo(s) con posición reciente</p>
        </div>
        {hasPermission('gps', 'read') && (
          <Link to="/gps-settings">
            <Button variant="secondary">Configuración GPS</Button>
          </Link>
        )}
      </div>

      {isLoading ? (
        <p className="text-text-muted">Cargando…</p>
      ) : (
        <FleetMap positions={positions} vehiclesById={vehiclesById} />
      )}
    </DashboardLayout>
  )
}
