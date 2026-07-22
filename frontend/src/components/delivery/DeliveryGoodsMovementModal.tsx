import { useState } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import type { DeliveryGoodsMovementPayload } from '../../features/delivery/api'
import type { DeliveryGoods, DeliveryGoodsMovementType } from '../../types/delivery'

export function DeliveryGoodsMovementModal({
  goods,
  onClose,
  onSubmit,
}: {
  goods: DeliveryGoods
  onClose: () => void
  onSubmit: (payload: DeliveryGoodsMovementPayload) => Promise<void>
}) {
  const [movementType, setMovementType] = useState<DeliveryGoodsMovementType>('entrada')
  const [quantity, setQuantity] = useState('1')
  const [unitCost, setUnitCost] = useState('')
  const [referenceDoc, setReferenceDoc] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit() {
    const qty = Number(quantity)
    if (!qty || (movementType !== 'ajuste' && qty <= 0)) {
      setError('Cantidad inválida')
      return
    }
    setIsSubmitting(true)
    setError(null)
    try {
      await onSubmit({
        goods_id: goods.id,
        movement_type: movementType,
        quantity: qty,
        unit_cost: unitCost ? Number(unitCost) : null,
        reference_doc: referenceDoc || null,
        notes: notes || null,
      })
      onClose()
    } catch {
      setError('No se pudo registrar el movimiento (¿stock insuficiente?)')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={`Movimiento — ${goods.name}`} onClose={onClose}>
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="movement_type">
            Tipo de movimiento
          </label>
          <select
            id="movement_type"
            value={movementType}
            onChange={(e) => setMovementType(e.target.value as DeliveryGoodsMovementType)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            <option value="entrada">Entrada</option>
            <option value="salida">Salida</option>
            <option value="ajuste">Ajuste (delta con signo)</option>
          </select>
        </div>

        <Input
          id="quantity"
          label={movementType === 'ajuste' ? 'Cantidad (puede ser negativa)' : 'Cantidad'}
          type="number"
          step="any"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />
        {movementType === 'entrada' && (
          <Input id="unit_cost" label="Costo unitario (opcional)" type="number" step="any" min={0} value={unitCost} onChange={(e) => setUnitCost(e.target.value)} />
        )}
        <Input id="reference_doc" label="Documento de referencia (opcional)" value={referenceDoc} onChange={(e) => setReferenceDoc(e.target.value)} />
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="notes">
            Notas (opcional)
          </label>
          <textarea
            id="notes"
            rows={2}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          />
        </div>

        {error && <p className="text-sm text-danger">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose} disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button onClick={() => void handleSubmit()} disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Registrar'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
