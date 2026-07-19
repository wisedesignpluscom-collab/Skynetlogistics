import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { useVehicles } from '../../features/vehicles/hooks'
import type { InventoryMovementPayload } from '../../features/inventory/api'
import type { InventoryItem, InventoryMovementType } from '../../types/inventory'

const MOVEMENT_LABELS: Record<InventoryMovementType, string> = {
  entrada: 'Entrada (compra/reposición)',
  salida: 'Salida (consumo)',
  ajuste: 'Ajuste (corrección de conteo)',
}

interface InventoryMovementModalProps {
  item: InventoryItem
  onClose: () => void
  onSubmit: (payload: InventoryMovementPayload) => Promise<void>
}

export function InventoryMovementModal({ item, onClose, onSubmit }: InventoryMovementModalProps) {
  const { data: vehiclesPage } = useVehicles({ page_size: 100 })
  const [movementType, setMovementType] = useState<InventoryMovementType>('entrada')
  const [quantity, setQuantity] = useState('')
  const [vehicleId, setVehicleId] = useState('')
  const [unitCost, setUnitCost] = useState('')
  const [referenceDoc, setReferenceDoc] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      const numericQuantity = Number(quantity)
      await onSubmit({
        item_id: item.id,
        movement_type: movementType,
        quantity: movementType === 'ajuste' ? numericQuantity : Math.abs(numericQuantity),
        vehicle_id: movementType === 'salida' ? vehicleId || null : null,
        unit_cost: unitCost ? Number(unitCost) : null,
        reference_doc: referenceDoc || null,
        notes: notes || null,
      })
      onClose()
    } catch {
      setError('No se pudo registrar el movimiento (¿deja el stock negativo?)')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={`Movimiento — ${item.sku}`} onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="movement_type">
            Tipo de movimiento
          </label>
          <select
            id="movement_type"
            value={movementType}
            onChange={(e) => setMovementType(e.target.value as InventoryMovementType)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            {(Object.keys(MOVEMENT_LABELS) as InventoryMovementType[]).map((type) => (
              <option key={type} value={type}>
                {MOVEMENT_LABELS[type]}
              </option>
            ))}
          </select>
        </div>

        <Input
          id="quantity"
          label={movementType === 'ajuste' ? `Cantidad (± delta, stock actual: ${item.quantity})` : `Cantidad (stock actual: ${item.quantity})`}
          type="number"
          step="0.01"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          required
        />

        {movementType === 'salida' && (
          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor="vehicle_id">
              Vehículo (opcional)
            </label>
            <select
              id="vehicle_id"
              value={vehicleId}
              onChange={(e) => setVehicleId(e.target.value)}
              className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
            >
              <option value="">Sin especificar</option>
              {vehiclesPage?.items.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.plate}
                </option>
              ))}
            </select>
          </div>
        )}

        {movementType === 'entrada' && (
          <Input
            id="unit_cost"
            label="Costo unitario de esta entrada ($, opcional)"
            type="number"
            min={0}
            step="0.01"
            value={unitCost}
            onChange={(e) => setUnitCost(e.target.value)}
          />
        )}

        <Input
          id="reference_doc"
          label="Documento de referencia (opcional)"
          value={referenceDoc}
          onChange={(e) => setReferenceDoc(e.target.value)}
        />

        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="notes">
            Notas
          </label>
          <textarea
            id="notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={2}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          />
        </div>

        {error && <p className="text-sm text-danger">{error}</p>}
        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Confirmar'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
