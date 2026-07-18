import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { useVehicles } from '../../features/vehicles/hooks'
import { useDrivers } from '../../features/drivers/hooks'
import { useDriverFatigueStatus } from '../../features/fatigue/hooks'
import type { TripPayload } from '../../features/trips/api'

const WARN_RISK_LEVELS = new Set(['alto', 'critico'])

interface TripFormModalProps {
  onClose: () => void
  onSubmit: (values: TripPayload) => Promise<void>
}

export function TripFormModal({ onClose, onSubmit }: TripFormModalProps) {
  const { data: vehiclesPage } = useVehicles({ page_size: 100, status_filter: 'activo' })
  const { data: driversPage } = useDrivers({ page_size: 100, status_filter: 'activo' })
  const vehicles = vehiclesPage?.items ?? []
  const trailers = vehicles.filter((v) => v.type === 'remolque')
  const tractors = vehicles.filter((v) => v.type !== 'remolque')

  const [vehicleId, setVehicleId] = useState('')
  const [driverId, setDriverId] = useState('')
  const [trailerId, setTrailerId] = useState('')
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [cargoType, setCargoType] = useState('')
  const [isRoundTrip, setIsRoundTrip] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { status: fatigueStatus } = useDriverFatigueStatus(driverId || null)
  const showFatigueWarning = !!fatigueStatus && WARN_RISK_LEVELS.has(fatigueStatus.risk_level)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        vehicle_id: vehicleId,
        driver_id: driverId,
        trailer_id: trailerId || null,
        origin,
        destination,
        cargo_type: cargoType,
        is_round_trip: isRoundTrip,
      })
      onClose()
    } catch {
      setError('No se pudo crear el viaje')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title="Nuevo viaje" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex max-h-[70vh] flex-col gap-4 overflow-y-auto">
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="vehicle">
            Vehículo
          </label>
          <select
            id="vehicle"
            value={vehicleId}
            onChange={(e) => setVehicleId(e.target.value)}
            required
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            <option value="">Selecciona un vehículo</option>
            {tractors.map((v) => (
              <option key={v.id} value={v.id}>
                {v.plate} — {v.brand} {v.model}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="driver">
            Conductor
          </label>
          <select
            id="driver"
            value={driverId}
            onChange={(e) => setDriverId(e.target.value)}
            required
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            <option value="">Selecciona un conductor</option>
            {driversPage?.items.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
          {showFatigueWarning && (
            <p className="mt-1 text-sm text-danger">
              ⚠ Este conductor tiene un riesgo de fatiga {fatigueStatus?.risk_level} (score{' '}
              {fatigueStatus?.risk_score}). Puedes continuar, pero considera asignar otro conductor.
            </p>
          )}
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="trailer">
            Remolque (opcional)
          </label>
          <select
            id="trailer"
            value={trailerId}
            onChange={(e) => setTrailerId(e.target.value)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            <option value="">Sin remolque</option>
            {trailers.map((t) => (
              <option key={t.id} value={t.id}>
                {t.plate}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Input id="origin" label="Origen" value={origin} onChange={(e) => setOrigin(e.target.value)} required />
          <Input
            id="destination"
            label="Destino"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            required
          />
        </div>

        <Input
          id="cargo_type"
          label="Tipo de carga"
          value={cargoType}
          onChange={(e) => setCargoType(e.target.value)}
          required
        />

        <label className="flex items-center gap-2 text-sm text-text-muted">
          <input
            type="checkbox"
            checked={isRoundTrip}
            onChange={(e) => setIsRoundTrip(e.target.checked)}
            className="rounded border-border"
          />
          Viaje de ida y vuelta
        </label>

        {error && <p className="text-sm text-danger">{error}</p>}
        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creando…' : 'Crear viaje'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
