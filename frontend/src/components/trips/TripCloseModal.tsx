import { useEffect, useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { getTripClosePreview } from '../../features/trips/api'
import type { Trip, TripClosePreview } from '../../types/trip'
import type { TripClosePayload } from '../../features/trips/api'

interface TripCloseModalProps {
  trip: Trip
  onClose: () => void
  onSubmit: (values: TripClosePayload) => Promise<void>
}

export function TripCloseModal({ trip, onClose, onSubmit }: TripCloseModalProps) {
  const [preview, setPreview] = useState<TripClosePreview | null>(null)
  const [endOdometerKm, setEndOdometerKm] = useState('')
  const [freightCost, setFreightCost] = useState(trip.freight_cost?.toString() ?? '')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    void getTripClosePreview(trip.id).then(setPreview)
  }, [trip.id])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        end_odometer_km: Number(endOdometerKm),
        freight_cost: freightCost ? Number(freightCost) : null,
      })
      onClose()
    } catch {
      setError('No se pudo cerrar el viaje')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title="Cerrar viaje" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {preview?.missing_pay_rate && (
          <p className="rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
            No hay tabulado de pago configurado para este tipo de vehículo. Configúralo antes de cerrar.
          </p>
        )}

        {preview && (
          <div className="rounded-md border border-border bg-surface p-4 text-sm">
            <p className="mb-2 font-display text-text">Resumen de pago (proyectado)</p>
            <dl className="grid grid-cols-2 gap-y-1 text-text-muted">
              <dt>Días de viaje</dt>
              <dd className="text-right text-text">{preview.trip_days}</dd>
              <dt>Salario base</dt>
              <dd className="text-right text-text">${preview.base_salary.toFixed(2)}</dd>
              <dt>Bono de alimentación</dt>
              <dd className="text-right text-text">${preview.meal_allowance.toFixed(2)}</dd>
              <dt>Bono de feriados ({preview.holiday_count})</dt>
              <dd className="text-right text-text">${preview.holiday_bonus.toFixed(2)}</dd>
              <dt>Bono de retorno</dt>
              <dd className="text-right text-text">${preview.return_bonus.toFixed(2)}</dd>
              <dt>Anticipo</dt>
              <dd className="text-right text-text">-${preview.advance_payment.toFixed(2)}</dd>
              <dt className="font-medium text-text">Total a pagar</dt>
              <dd className="text-right font-medium text-gold">${preview.total_to_pay.toFixed(2)}</dd>
            </dl>
          </div>
        )}

        <Input
          id="end_odometer_km"
          label="Odómetro final (km)"
          type="number"
          min={trip.start_odometer_km ?? 0}
          value={endOdometerKm}
          onChange={(e) => setEndOdometerKm(e.target.value)}
          required
        />
        <Input
          id="freight_cost"
          label="Flete (confirmar o ajustar)"
          type="number"
          min={0}
          step="0.01"
          value={freightCost}
          onChange={(e) => setFreightCost(e.target.value)}
        />

        {error && <p className="text-sm text-danger">{error}</p>}
        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting || preview?.missing_pay_rate}>
            {isSubmitting ? 'Cerrando…' : 'Confirmar cierre'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
