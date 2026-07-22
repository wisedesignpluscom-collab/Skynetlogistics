import { useEffect, useState } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { listTrips } from '../../features/trips/api'
import type { Trip } from '../../types/trip'

export function AssignOrderModal({
  onClose,
  onAssign,
}: {
  onClose: () => void
  onAssign: (tripId: string) => Promise<void>
}) {
  const [trips, setTrips] = useState<Trip[]>([])
  const [tripId, setTripId] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    // Solo viajes que aún reparten (planificados o en curso).
    void Promise.all([
      listTrips({ status_filter: 'planificado', page_size: 50 }),
      listTrips({ status_filter: 'en_curso', page_size: 50 }),
    ]).then(([planned, ongoing]) => {
      const all = [...planned.items, ...ongoing.items]
      setTrips(all)
      setTripId(all[0]?.id ?? '')
    })
  }, [])

  async function handleAssign() {
    if (!tripId) return setError('Selecciona un viaje')
    setIsSubmitting(true)
    setError(null)
    try {
      await onAssign(tripId)
      onClose()
    } catch {
      setError('No se pudo asignar (¿stock insuficiente?)')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title="Asignar pedido a un viaje" onClose={onClose}>
      <div className="flex flex-col gap-4">
        <p className="text-sm text-text-muted">
          Al asignar, se descuenta la mercancía del stock (la carga sale a la calle).
        </p>
        <select
          value={tripId}
          onChange={(e) => setTripId(e.target.value)}
          className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
        >
          {trips.length === 0 && <option value="">No hay viajes disponibles</option>}
          {trips.map((t) => (
            <option key={t.id} value={t.id}>
              {t.origin} → {t.destination} ({t.status})
            </option>
          ))}
        </select>

        {error && <p className="text-sm text-danger">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose} disabled={isSubmitting}>Cancelar</Button>
          <Button onClick={() => void handleAssign()} disabled={isSubmitting || !tripId}>
            {isSubmitting ? 'Asignando…' : 'Asignar'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
