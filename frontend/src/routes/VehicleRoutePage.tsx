import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { RouteReplayMap } from '../components/gps/RouteReplayMap'
import { getPositionHistory } from '../features/gps/api'
import type { VehiclePosition } from '../types/gps'

function isoDaysAgo(days: number): string {
  const d = new Date()
  d.setDate(d.getDate() - days)
  return d.toISOString().slice(0, 16)
}

export function VehicleRoutePage() {
  const { vehicleId } = useParams<{ vehicleId: string }>()
  const [dateFrom, setDateFrom] = useState(isoDaysAgo(1))
  const [dateTo, setDateTo] = useState(new Date().toISOString().slice(0, 16))
  const [positions, setPositions] = useState<VehiclePosition[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  async function handleSearch() {
    if (!vehicleId) return
    setIsLoading(true)
    try {
      setPositions(
        await getPositionHistory(
          vehicleId,
          new Date(dateFrom).toISOString(),
          new Date(dateTo).toISOString(),
        ),
      )
      setHasSearched(true)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <DashboardLayout>
      <Link to={`/vehicles/${vehicleId}`} className="text-sm text-text-muted hover:text-gold">
        ← Volver al vehículo
      </Link>
      <h1 className="mt-4 mb-6 font-display text-2xl text-text">Replay de ruta</h1>

      <div className="mb-4 flex flex-wrap items-end gap-3">
        <Input
          id="date_from"
          label="Desde"
          type="datetime-local"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
        />
        <Input
          id="date_to"
          label="Hasta"
          type="datetime-local"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
        />
        <Button onClick={handleSearch} disabled={isLoading}>
          {isLoading ? 'Buscando…' : 'Buscar'}
        </Button>
      </div>

      {hasSearched && <RouteReplayMap positions={positions} />}
    </DashboardLayout>
  )
}
