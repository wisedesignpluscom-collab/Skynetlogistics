import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Badge } from '../components/ui/Badge'
import { VrpProposalMap } from '../components/vrp/VrpProposalMap'
import { useAvailableVehicles } from '../features/vrp/hooks'
import { confirmVrpRun, discardVrpRun, optimizeVrp } from '../features/vrp/api'
import { listDeliveryOrders } from '../features/delivery/api'
import { getLatestPosition } from '../features/gps/api'
import type { VrpRun, VrpStop } from '../types/vrp'
import type { DeliveryOrder } from '../types/delivery'

type OptimizeMode = 'manual' | 'orders'

const STATUS_LABELS: Record<VrpRun['status'], { label: string; tone: 'gold' | 'success' | 'muted' }> = {
  propuesto: { label: 'Propuesto', tone: 'gold' },
  confirmado: { label: 'Confirmado', tone: 'success' },
  descartado: { label: 'Descartado', tone: 'muted' },
}

export function VrpOptimizationPage() {
  const { vehicles, isLoading: vehiclesLoading } = useAvailableVehicles()
  const [selectedVehicleIds, setSelectedVehicleIds] = useState<string[]>([])
  const [stops, setStops] = useState<VrpStop[]>([])
  const [cargoType, setCargoType] = useState('')
  const [stopLat, setStopLat] = useState('')
  const [stopLng, setStopLng] = useState('')
  const [stopLabel, setStopLabel] = useState('')

  const [mode, setMode] = useState<OptimizeMode>('manual')
  const [pendingOrders, setPendingOrders] = useState<DeliveryOrder[]>([])
  const [selectedOrderIds, setSelectedOrderIds] = useState<string[]>([])
  const [enforceCapacity, setEnforceCapacity] = useState(true)

  useEffect(() => {
    if (mode !== 'orders') return
    void listDeliveryOrders({ status_filter: 'pendiente', page_size: 100 }).then((p) =>
      setPendingOrders(p.items)
    )
  }, [mode])

  function toggleOrder(id: string) {
    setSelectedOrderIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))
  }

  const [run, setRun] = useState<VrpRun | null>(null)
  const [vehicleStarts, setVehicleStarts] = useState<Record<string, { lat: number; lng: number }>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setSelectedVehicleIds(vehicles.map((v) => v.id))
  }, [vehicles])

  const vehicleLabelById: Record<string, string> = Object.fromEntries(
    vehicles.map((v) => [v.id, `${v.plate} (${v.brand} ${v.model})`])
  )

  function toggleVehicle(id: string) {
    setSelectedVehicleIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))
  }

  function handleAddStop(e: FormEvent) {
    e.preventDefault()
    if (!stopLat || !stopLng || !stopLabel) return
    setStops((prev) => [...prev, { lat: Number(stopLat), lng: Number(stopLng), label: stopLabel }])
    setStopLat('')
    setStopLng('')
    setStopLabel('')
  }

  function removeStop(index: number) {
    setStops((prev) => prev.filter((_, i) => i !== index))
  }

  async function handleOptimize(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      const allSelected = selectedVehicleIds.length === vehicles.length
      const proposal = await optimizeVrp({
        stops: mode === 'manual' ? stops : undefined,
        order_ids: mode === 'orders' ? selectedOrderIds : undefined,
        enforce_capacity: mode === 'orders' ? enforceCapacity : undefined,
        cargo_type: cargoType,
        vehicle_ids: allSelected ? undefined : selectedVehicleIds,
      })
      setRun(proposal)

      const starts: Record<string, { lat: number; lng: number }> = {}
      await Promise.all(
        proposal.proposed_assignment.map(async (a) => {
          const position = await getLatestPosition(a.vehicle_id)
          if (position) starts[a.vehicle_id] = { lat: position.lat, lng: position.lng }
        })
      )
      setVehicleStarts(starts)
    } catch (err: unknown) {
      const detail =
        typeof err === 'object' && err !== null && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined
      setError(detail ?? 'No se pudo optimizar — revisa las paradas y los vehículos seleccionados')
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleConfirm() {
    if (!run) return
    setIsSubmitting(true)
    try {
      setRun(await confirmVrpRun(run.id))
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleDiscard() {
    if (!run) return
    setIsSubmitting(true)
    try {
      setRun(await discardVrpRun(run.id))
    } finally {
      setIsSubmitting(false)
    }
  }

  function handleReset() {
    setRun(null)
    setVehicleStarts({})
    setStops([])
    setCargoType('')
    setSelectedOrderIds([])
  }

  const statusInfo = run ? STATUS_LABELS[run.status] : null

  return (
    <DashboardLayout>
      <Link to="/trips" className="text-sm text-text-muted hover:text-gold">
        ← Volver a viajes
      </Link>
      <h1 className="mt-4 mb-2 font-display text-2xl text-text">Optimizar rutas (VRP)</h1>
      <p className="mb-6 text-sm text-text-muted">
        Reparte un conjunto de paradas entre los vehículos disponibles y ordena la visita de cada
        uno para minimizar la distancia total recorrida.
      </p>

      {!run && (
        <form onSubmit={handleOptimize} className="max-w-3xl space-y-6">
          <div className="inline-flex rounded-lg border border-border bg-surface p-1">
            <button
              type="button"
              onClick={() => setMode('manual')}
              className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
                mode === 'manual' ? 'bg-gold text-white' : 'text-text-muted hover:text-text'
              }`}
            >
              Captura manual
            </button>
            <button
              type="button"
              onClick={() => setMode('orders')}
              className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
                mode === 'orders' ? 'bg-gold text-white' : 'text-text-muted hover:text-text'
              }`}
            >
              Desde pedidos pendientes
            </button>
          </div>

          {mode === 'orders' && (
            <div>
              <h2 className="mb-3 font-display text-lg text-text">Pedidos pendientes</h2>
              {pendingOrders.length === 0 ? (
                <p className="text-text-muted">
                  No hay pedidos de reparto pendientes.{' '}
                  <Link to="/delivery-orders" className="text-gold hover:underline">
                    Crear pedidos
                  </Link>
                </p>
              ) : (
                <ul className="divide-y divide-border rounded-lg border border-border">
                  {pendingOrders.map((o) => (
                    <li key={o.id} className="flex items-center gap-3 px-4 py-2 text-sm">
                      <input
                        type="checkbox"
                        checked={selectedOrderIds.includes(o.id)}
                        onChange={() => toggleOrder(o.id)}
                      />
                      <span className="text-text">{o.address}</span>
                      <span className="text-text-muted">· {o.items.length} línea(s)</span>
                    </li>
                  ))}
                </ul>
              )}
              <label className="mt-3 flex items-center gap-2 text-sm text-text-muted">
                <input
                  type="checkbox"
                  checked={enforceCapacity}
                  onChange={(e) => setEnforceCapacity(e.target.checked)}
                />
                Respetar la capacidad de carga (peso/volumen) de cada vehículo
              </label>
            </div>
          )}

          {mode === 'manual' && (
          <div>
            <h2 className="mb-3 font-display text-lg text-text">Paradas</h2>
            <div className="mb-3 flex flex-wrap items-end gap-3">
              <Input
                id="stop_label"
                label="Etiqueta / dirección"
                value={stopLabel}
                onChange={(e) => setStopLabel(e.target.value)}
                placeholder="Cliente / dirección"
              />
              <Input
                id="stop_lat"
                label="Latitud"
                type="number"
                step="any"
                value={stopLat}
                onChange={(e) => setStopLat(e.target.value)}
              />
              <Input
                id="stop_lng"
                label="Longitud"
                type="number"
                step="any"
                value={stopLng}
                onChange={(e) => setStopLng(e.target.value)}
              />
              <Button type="button" variant="secondary" onClick={handleAddStop}>
                Agregar parada
              </Button>
            </div>
            {stops.length > 0 && (
              <ul className="divide-y divide-border rounded-lg border border-border">
                {stops.map((s, i) => (
                  <li key={i} className="flex items-center justify-between px-4 py-2 text-sm">
                    <span className="text-text">
                      {s.label}{' '}
                      <span className="text-text-muted">
                        ({s.lat}, {s.lng})
                      </span>
                    </span>
                    <button
                      type="button"
                      onClick={() => removeStop(i)}
                      className="text-text-muted hover:text-danger"
                    >
                      Quitar
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
          )}

          <div>
            <h2 className="mb-3 font-display text-lg text-text">Tipo de carga</h2>
            <Input
              id="cargo_type"
              value={cargoType}
              onChange={(e) => setCargoType(e.target.value)}
              placeholder="general, refrigerada, etc."
              required
            />
          </div>

          <div>
            <h2 className="mb-3 font-display text-lg text-text">Vehículos candidatos</h2>
            {vehiclesLoading && <p className="text-text-muted">Cargando vehículos…</p>}
            {!vehiclesLoading && vehicles.length === 0 && (
              <p className="text-text-muted">
                No hay vehículos disponibles (activos, con conductor asignado, sin viaje en curso y
                con posición GPS conocida).
              </p>
            )}
            {vehicles.length > 0 && (
              <ul className="divide-y divide-border rounded-lg border border-border">
                {vehicles.map((v) => (
                  <li key={v.id} className="flex items-center gap-3 px-4 py-2 text-sm">
                    <input
                      type="checkbox"
                      checked={selectedVehicleIds.includes(v.id)}
                      onChange={() => toggleVehicle(v.id)}
                    />
                    <span className="text-text">
                      {v.plate} — {v.brand} {v.model}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {error && <p className="text-sm text-danger">{error}</p>}

          <div className="flex justify-end">
            <Button
              type="submit"
              disabled={
                isSubmitting ||
                selectedVehicleIds.length === 0 ||
                (mode === 'manual' ? stops.length === 0 : selectedOrderIds.length === 0)
              }
            >
              {isSubmitting ? 'Optimizando…' : 'Optimizar'}
            </Button>
          </div>
        </form>
      )}

      {run && (
        <div>
          <div className="mb-4 flex flex-wrap items-center gap-3">
            {statusInfo && <Badge tone={statusInfo.tone}>{statusInfo.label}</Badge>}
            <span className="text-sm text-text-muted">
              {run.proposed_assignment.length} vehículo(s) · {run.input_stops.length} parada(s)
            </span>
          </div>

          <VrpProposalMap
            proposal={run.proposed_assignment}
            vehicleStarts={vehicleStarts}
            vehicleLabels={vehicleLabelById}
          />

          <div className="mt-4 overflow-hidden rounded-lg border border-border">
            <table className="w-full text-left text-sm">
              <thead className="bg-surface text-text-muted">
                <tr>
                  <th className="px-4 py-2 font-medium">Vehículo</th>
                  <th className="px-4 py-2 font-medium">Paradas (orden)</th>
                  <th className="px-4 py-2 font-medium">Carga</th>
                  <th className="px-4 py-2 font-medium">Distancia est.</th>
                  <th className="px-4 py-2 font-medium">Duración est.</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {run.proposed_assignment.map((a) => (
                  <tr key={a.vehicle_id}>
                    <td className="px-4 py-2 text-text">
                      {vehicleLabelById[a.vehicle_id] ?? a.vehicle_id}
                    </td>
                    <td className="px-4 py-2 text-text-muted">
                      {a.stops.map((s) => s.label).join(' → ')}
                    </td>
                    <td className="px-4 py-2 text-text-muted">
                      {a.load_kg != null ? (
                        <span>
                          {a.load_kg} / {a.capacity_kg != null ? `${a.capacity_kg} kg` : '∞'}
                          {a.load_m3 != null && a.load_m3 > 0 && (
                            <span className="block text-xs">
                              {a.load_m3} / {a.capacity_m3 != null ? `${a.capacity_m3} m³` : '∞'}
                            </span>
                          )}
                        </span>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td className="px-4 py-2 text-text-muted">{a.distance_km} km</td>
                    <td className="px-4 py-2 text-text-muted">{a.duration_min} min</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {run.status === 'propuesto' && (
            <div className="mt-4 flex justify-end gap-3">
              <Button variant="secondary" onClick={handleDiscard} disabled={isSubmitting}>
                Descartar
              </Button>
              <Button onClick={handleConfirm} disabled={isSubmitting}>
                {isSubmitting ? 'Confirmando…' : 'Confirmar y crear viajes'}
              </Button>
            </div>
          )}

          {run.status === 'confirmado' && (
            <div className="mt-4">
              <p className="mb-3 text-sm text-text-muted">Viajes creados:</p>
              <div className="flex flex-wrap gap-2">
                {run.result_trip_ids.map((id) => (
                  <Link key={id} to={`/trips/${id}`}>
                    <Button variant="secondary">Ver viaje →</Button>
                  </Link>
                ))}
              </div>
              <Button className="mt-4" variant="secondary" onClick={handleReset}>
                Nueva optimización
              </Button>
            </div>
          )}

          {run.status === 'descartado' && (
            <div className="mt-4">
              <Button variant="secondary" onClick={handleReset}>
                Nueva optimización
              </Button>
            </div>
          )}
        </div>
      )}
    </DashboardLayout>
  )
}
