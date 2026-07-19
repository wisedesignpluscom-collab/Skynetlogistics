import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import type { InventoryItemCreatePayload } from '../../features/inventory/api'
import type { Warehouse } from '../../types/tire'

interface InventoryItemFormModalProps {
  warehouses: Warehouse[]
  onClose: () => void
  onSubmit: (values: InventoryItemCreatePayload) => Promise<void>
}

export function InventoryItemFormModal({ warehouses, onClose, onSubmit }: InventoryItemFormModalProps) {
  const [sku, setSku] = useState('')
  const [name, setName] = useState('')
  const [unit, setUnit] = useState('unidad')
  const [minStock, setMinStock] = useState('0')
  const [unitCost, setUnitCost] = useState('0')
  const [warehouseId, setWarehouseId] = useState(warehouses[0]?.id ?? '')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        warehouse_id: warehouseId,
        sku,
        name,
        unit,
        min_stock: Number(minStock),
        unit_cost: Number(unitCost),
      })
      onClose()
    } catch {
      setError('No se pudo crear el ítem (¿SKU ya existe?)')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title="Nuevo ítem de inventario" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="warehouse_id">
            Almacén
          </label>
          <select
            id="warehouse_id"
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
        <Input id="sku" label="SKU" value={sku} onChange={(e) => setSku(e.target.value)} required />
        <Input id="name" label="Nombre" value={name} onChange={(e) => setName(e.target.value)} required />
        <div className="grid grid-cols-3 gap-3">
          <Input id="unit" label="Unidad" value={unit} onChange={(e) => setUnit(e.target.value)} required />
          <Input
            id="min_stock"
            label="Stock mínimo"
            type="number"
            min={0}
            step="0.01"
            value={minStock}
            onChange={(e) => setMinStock(e.target.value)}
          />
          <Input
            id="unit_cost"
            label="Costo unitario ($)"
            type="number"
            min={0}
            step="0.01"
            value={unitCost}
            onChange={(e) => setUnitCost(e.target.value)}
          />
        </div>

        {error && <p className="text-sm text-danger">{error}</p>}
        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Crear'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
