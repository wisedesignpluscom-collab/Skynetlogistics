import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Badge } from '../components/ui/Badge'
import { TripRouteMap } from '../components/routing/TripRouteMap'
import { useTripRoute } from '../features/routing/hooks'
import { computeTripRoute, recalculateTripRoute } from '../features/routing/api'
import { getTrip } from '../features/trips/api'
import { getLatestPosition } from '../features/gps/api'
import { useAuth } from '../features/auth/AuthContext'
import type { VehiclePosition } from '../types/gps'

const REASON_LABELS: Record<string, string> = {
  desvio: 'Desvío',
  manual: 'Manual',
  trafico: 'Tráfico',
}

export function TripRoutePage() {
  const { tripId } = useParams<{ tripId: string }>()
  const { hasPermission } = useAuth()
  const { plan, isLoading, reload } = useTripRoute(tripId)
  const [position, setPosition] = useState<VehiclePosition | null>(null)

  const [originLat, setOriginLat] = useState('')
  const [originLng, setOriginLng] = useState('')
  const [destLat, setDestLat] = useState('')
  const [destLng, setDestLng] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const canWrite = hasPermission('trips', 'write')

  const loadTripAndPosition = useCallback(async () => {
    if (!tripId) return
    const t = await getTrip(tripId)
    try {
      setPosition(await getLatestPosition(t.vehicle_id))
    } catch {
      setPosition(null)
    }
  }, [tripId])

  useEffect(() => {
    void loadTripAndPosition()
  }, [loadTripAndPosition])

  async function handleCompute(e: FormEvent) {
    e.preventDefault()
    if (!tripId) return
    setError(null)
    setIsSubmitting(true)
    try {
      await computeTripRoute(tripId, {
        origin_lat: Number(originLat),
        origin_lng: Number(originLng),
        destination_lat: Number(destLat),
        destination_lng: Number(destLng),
      })
      await reload()
    } catch {
      setError('No se pudo calcular la ruta')
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleRecalculate() {
    if (!tripId) return
    setIsSubmitting(true)
    try {
      await recalculateTripRoute(tripId)
      await reload()
    } finally {
      setIsSubmitting(false)
    }
  }

  const latestRecalc = plan?.recalculations[0]
  const hasDeviation = latestRecalc?.reason === 'desvio'

  return (
    <DashboardLayout>
      <Link to={`/trips/${tripId}`} className="text-sm text-text-muted hover:text-gold">
        ← Volver al viaje
      </Link>
      <h1 className="mt-4 mb-6 font-display text-2xl text-text">Ruta planeada</h1>

      {isLoading && <p className="text-text-muted">Cargando…</p>}

      {!isLoading && !plan && (
        <form onSubmit={handleCompute} className="mb-6 max-w-xl rounded-lg border border-border p-4">
          <p className="mb-4 text-sm text-text-muted">
            Este viaje aún no tiene ruta. Ingresa las coordenadas de origen y destino para calcularla.
          </p>
          <div className="grid grid-cols-2 gap-3">
            <Input id="origin_lat" label="Origen — latitud" type="number" step="any" value={originLat} onChange={(e) => setOriginLat(e.target.value)} required />
            <Input id="origin_lng" label="Origen — longitud" type="number" step="any" value={originLng} onChange={(e) => setOriginLng(e.target.value)} required />
            <Input id="dest_lat" label="Destino — latitud" type="number" step="any" value={destLat} onChange={(e) => setDestLat(e.target.value)} required />
            <Input id="dest_lng" label="Destino — longitud" type="number" step="any" value={destLng} onChange={(e) => setDestLng(e.target.value)} required />
          </div>
          {error && <p className="mt-3 text-sm text-danger">{error}</p>}
          {canWrite && (
            <div className="mt-4 flex justify-end">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Calculando…' : 'Calcular ruta'}
              </Button>
            </div>
          )}
        </form>
      )}

      {plan && (
        <>
          {hasDeviation && (
            <div className="mb-4 rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-danger">
              ⚠ Se detectó un desvío de ruta ({Math.round(latestRecalc!.deviation_m ?? 0)} m de la ruta
              planeada). La ruta fue recalculada automáticamente el{' '}
              {new Date(latestRecalc!.created_at).toLocaleString()}.
            </div>
          )}

          <div className="mb-4 flex flex-wrap items-center gap-4">
            <div className="rounded-lg border border-border px-4 py-2">
              <p className="text-xs text-text-muted">Distancia estimada</p>
              <p className="font-display text-lg text-text">{plan.calculated_distance_km} km</p>
            </div>
            <div className="rounded-lg border border-border px-4 py-2">
              <p className="text-xs text-text-muted">Duración estimada</p>
              <p className="font-display text-lg text-text">{plan.calculated_duration_min} min</p>
            </div>
            <div className="rounded-lg border border-border px-4 py-2">
              <p className="text-xs text-text-muted">Motor</p>
              <p className="font-display text-lg text-text">{plan.engine_used}</p>
            </div>
            {canWrite && (
              <Button variant="secondary" onClick={handleRecalculate} disabled={isSubmitting}>
                {isSubmitting ? 'Recalculando…' : 'Recalcular'}
              </Button>
            )}
          </div>

          <div className="mb-4 flex items-center gap-4 text-xs text-text-muted">
            <span className="flex items-center gap-1">
              <span className="inline-block h-1 w-6 rounded bg-gold" /> Ruta planeada
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block h-3 w-3 rounded-full bg-blue-500" /> Posición real del vehículo
            </span>
          </div>

          <TripRouteMap plan={plan} currentPosition={position} />

          {plan.recalculations.length > 0 && (
            <>
              <h2 className="mt-6 mb-3 font-display text-lg text-text">Historial de recálculos</h2>
              <div className="overflow-hidden rounded-lg border border-border">
                <table className="w-full text-left text-sm">
                  <thead className="bg-surface text-text-muted">
                    <tr>
                      <th className="px-4 py-2 font-medium">Fecha</th>
                      <th className="px-4 py-2 font-medium">Motivo</th>
                      <th className="px-4 py-2 font-medium">Desvío</th>
                      <th className="px-4 py-2 font-medium">Nueva distancia</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {plan.recalculations.map((r) => (
                      <tr key={r.id}>
                        <td className="px-4 py-2 text-text-muted">{new Date(r.created_at).toLocaleString()}</td>
                        <td className="px-4 py-2">
                          <Badge tone={r.reason === 'desvio' ? 'danger' : 'muted'}>
                            {REASON_LABELS[r.reason] ?? r.reason}
                          </Badge>
                        </td>
                        <td className="px-4 py-2 text-text-muted">
                          {r.deviation_m !== null ? `${Math.round(r.deviation_m)} m` : '—'}
                        </td>
                        <td className="px-4 py-2 text-text-muted">{r.new_distance_km} km</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </>
      )}
    </DashboardLayout>
  )
}
