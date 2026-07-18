import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { useTires } from '../../features/tires/hooks'
import type { TireMovementPayload } from '../../features/tires/api'
import type { AxlePrefill } from './TireMovementModal'

interface InstallTireModalProps {
  prefill: AxlePrefill
  onClose: () => void
  onSubmit: (payload: TireMovementPayload) => Promise<void>
}

export function InstallTireModal({ prefill, onClose, onSubmit }: InstallTireModalProps) {
  const { data } = useTires({ status_filter: 'almacen', page_size: 100 })
  const [tireId, setTireId] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        tire_id: tireId,
        movement_type: 'instalacion',
        vehicle_id: prefill.vehicleId,
        axle_number: prefill.axleNumber,
        axle_side: prefill.axleSide,
        axle_dual_position: prefill.axleDualPosition,
      })
      onClose()
    } catch {
      setError('No se pudo instalar el neumático en esa posición')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={`Instalar en eje ${prefill.axleNumber} · ${prefill.axleSide} · ${prefill.axleDualPosition}`} onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="tire_id">
            Neumático en almacén
          </label>
          <select
            id="tire_id"
            value={tireId}
            onChange={(e) => setTireId(e.target.value)}
            required
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            <option value="">Seleccionar…</option>
            {data?.items.map((tire) => (
              <option key={tire.id} value={tire.id}>
                {tire.unique_code} — {tire.brand} {tire.model} ({tire.current_thickness_mm}mm)
              </option>
            ))}
          </select>
          {data && data.items.length === 0 && (
            <p className="text-sm text-text-muted">No hay neumáticos disponibles en almacén.</p>
          )}
        </div>

        {error && <p className="text-sm text-danger">{error}</p>}
        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting || !tireId}>
            {isSubmitting ? 'Instalando…' : 'Instalar'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
