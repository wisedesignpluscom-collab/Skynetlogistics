import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { useProviders } from '../../features/providers/hooks'
import type { TireMovementBatchPayload } from '../../features/tires/api'
import type { Tire, TireMovementType, TireStatus, Warehouse } from '../../types/tire'

const VALID_MOVEMENTS_BY_STATUS: Record<TireStatus, TireMovementType[]> = {
  almacen: ['envio_reparacion', 'envio_reencauche'],
  instalado: ['desinstalacion', 'envio_reparacion', 'envio_reencauche'],
  reparacion: ['retorno_taller'],
}

const MOVEMENT_LABELS: Record<TireMovementType, string> = {
  instalacion: 'Instalar en vehículo',
  desinstalacion: 'Desinstalar a almacén',
  envio_reparacion: 'Enviar a reparación',
  envio_reencauche: 'Enviar a reencauche',
  retorno_taller: 'Retorno de taller a almacén',
}

function commonMovementTypes(tires: Tire[]): TireMovementType[] {
  if (tires.length === 0) return []
  const [first, ...rest] = tires.map((tire) => new Set(VALID_MOVEMENTS_BY_STATUS[tire.status]))
  return [...first].filter((type) => rest.every((set) => set.has(type)))
}

interface TireBatchMovementModalProps {
  tires: Tire[]
  warehouses: Warehouse[]
  onClose: () => void
  onSubmit: (payload: TireMovementBatchPayload) => Promise<void>
}

export function TireBatchMovementModal({ tires, warehouses, onClose, onSubmit }: TireBatchMovementModalProps) {
  const { providers } = useProviders()
  const options = commonMovementTypes(tires)
  const [movementType, setMovementType] = useState<TireMovementType | ''>(options[0] ?? '')
  const [warehouseId, setWarehouseId] = useState('')
  const [providerId, setProviderId] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!movementType) return
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        movement_type: movementType,
        items: tires.map((tire) => ({ tire_id: tire.id })),
        warehouse_id: movementType === 'desinstalacion' || movementType === 'retorno_taller' ? warehouseId : null,
        provider_id: movementType === 'envio_reparacion' || movementType === 'envio_reencauche' ? providerId || null : null,
        notes: notes || null,
      })
      onClose()
    } catch {
      setError('No se pudo aplicar el movimiento en lote')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={`Movimiento en lote (${tires.length} neumáticos)`} onClose={onClose}>
      {options.length === 0 ? (
        <p className="text-sm text-danger">
          Los neumáticos seleccionados no comparten un movimiento válido en común. Revisa la selección.
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <ul className="max-h-24 overflow-y-auto rounded-md border border-border p-2 text-xs text-text-muted">
            {tires.map((tire) => (
              <li key={tire.id}>{tire.unique_code}</li>
            ))}
          </ul>

          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor="batch_movement_type">
              Tipo de movimiento
            </label>
            <select
              id="batch_movement_type"
              value={movementType}
              onChange={(e) => setMovementType(e.target.value as TireMovementType)}
              className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
            >
              {options.map((type) => (
                <option key={type} value={type}>
                  {MOVEMENT_LABELS[type]}
                </option>
              ))}
            </select>
          </div>

          {(movementType === 'desinstalacion' || movementType === 'retorno_taller') && (
            <div className="flex flex-col gap-1">
              <label className="text-sm text-text-muted" htmlFor="batch_warehouse_id">
                Almacén destino
              </label>
              <select
                id="batch_warehouse_id"
                value={warehouseId}
                onChange={(e) => setWarehouseId(e.target.value)}
                required
                className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
              >
                <option value="">Seleccionar…</option>
                {warehouses.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {(movementType === 'envio_reparacion' || movementType === 'envio_reencauche') && (
            <div className="flex flex-col gap-1">
              <label className="text-sm text-text-muted" htmlFor="batch_provider_id">
                Proveedor (opcional)
              </label>
              <select
                id="batch_provider_id"
                value={providerId}
                onChange={(e) => setProviderId(e.target.value)}
                className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
              >
                <option value="">Sin especificar</option>
                {providers.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor="batch_notes">
              Motivo / notas
            </label>
            <textarea
              id="batch_notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              placeholder="Ej. reemplazo completo de eje 2"
              className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
            />
          </div>

          {error && <p className="text-sm text-danger">{error}</p>}
          <div className="mt-2 flex justify-end gap-3">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Aplicando…' : 'Aplicar a todos'}
            </Button>
          </div>
        </form>
      )}
    </Modal>
  )
}
