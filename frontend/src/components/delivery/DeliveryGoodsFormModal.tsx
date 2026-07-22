import { useEffect, useState } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { CustomFieldsSection } from '../config/CustomFieldsSection'
import { useSystemFieldRules } from '../../features/config/useSystemFieldRules'
import type { DeliveryGoodsCreatePayload } from '../../features/delivery/api'
import type { Warehouse } from '../../types/tire'
import type { CustomData } from '../../types/customField'

export function DeliveryGoodsFormModal({
  warehouses,
  onClose,
  onSubmit,
}: {
  warehouses: Warehouse[]
  onClose: () => void
  onSubmit: (values: DeliveryGoodsCreatePayload) => Promise<void>
}) {
  const [warehouseId, setWarehouseId] = useState(warehouses[0]?.id ?? '')
  const [sku, setSku] = useState('')
  const [name, setName] = useState('')
  const [unit, setUnit] = useState('unidad')
  const [minStock, setMinStock] = useState('0')
  const [unitCost, setUnitCost] = useState('0')
  const [weight, setWeight] = useState('0')
  const [volume, setVolume] = useState('0')
  const [customData, setCustomData] = useState<CustomData>({})
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const rules = useSystemFieldRules(
    'delivery_goods',
    { unit, min_stock: minStock, unit_cost: unitCost, weight_kg_per_unit: weight, volume_m3_per_unit: volume },
    customData
  )

  useEffect(() => {
    const setters: Record<string, (v: string) => void> = {
      min_stock: setMinStock,
      unit_cost: setUnitCost,
      weight_kg_per_unit: setWeight,
      volume_m3_per_unit: setVolume,
    }
    for (const [key, computedVal] of Object.entries(rules.computed)) {
      setters[key]?.(String(computedVal))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(rules.computed)])

  async function handleSubmit() {
    if (!warehouseId) {
      setError('Selecciona un almacén')
      return
    }
    if (!sku.trim() || !name.trim()) {
      setError('SKU y nombre son obligatorios')
      return
    }
    setIsSubmitting(true)
    setError(null)
    try {
      await onSubmit({
        warehouse_id: warehouseId,
        sku: sku.trim(),
        name: name.trim(),
        unit: unit.trim() || 'unidad',
        min_stock: Number(minStock) || 0,
        unit_cost: Number(unitCost) || 0,
        weight_kg_per_unit: Number(weight) || 0,
        volume_m3_per_unit: Number(volume) || 0,
        custom_data: customData,
      })
      onClose()
    } catch {
      setError('No se pudo crear la mercancía (¿SKU duplicado?)')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title="Nueva mercancía de reparto" onClose={onClose}>
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="warehouse">
            Almacén
          </label>
          <select
            id="warehouse"
            value={warehouseId}
            onChange={(e) => setWarehouseId(e.target.value)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            {warehouses.length === 0 && <option value="">Sin almacenes — crea uno primero</option>}
            {warehouses.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input id="sku" label="SKU" value={sku} onChange={(e) => setSku(e.target.value)} />
          {!rules.isHidden('unit') && (
            <Input
              id="unit"
              label={rules.isRequired('unit') ? 'Unidad *' : 'Unidad'}
              value={unit}
              onChange={(e) => setUnit(e.target.value)}
            />
          )}
        </div>
        <Input id="name" label="Nombre" value={name} onChange={(e) => setName(e.target.value)} />

        <div className="grid grid-cols-2 gap-4">
          {!rules.isHidden('min_stock') && (
            <Input
              id="min_stock"
              label={rules.isRequired('min_stock') ? 'Stock mínimo *' : 'Stock mínimo'}
              type="number"
              step="any"
              min={0}
              value={minStock}
              onChange={(e) => setMinStock(e.target.value)}
            />
          )}
          {!rules.isHidden('unit_cost') && (
            <Input
              id="unit_cost"
              label={rules.isRequired('unit_cost') ? 'Costo unitario *' : 'Costo unitario'}
              type="number"
              step="any"
              min={0}
              value={unitCost}
              onChange={(e) => setUnitCost(e.target.value)}
            />
          )}
        </div>
        <div className="grid grid-cols-2 gap-4">
          {!rules.isHidden('weight_kg_per_unit') && (
            <Input
              id="weight"
              label={rules.isRequired('weight_kg_per_unit') ? 'Peso por unidad (kg) *' : 'Peso por unidad (kg)'}
              type="number"
              step="any"
              min={0}
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
            />
          )}
          {!rules.isHidden('volume_m3_per_unit') && (
            <Input
              id="volume"
              label={rules.isRequired('volume_m3_per_unit') ? 'Volumen por unidad (m³) *' : 'Volumen por unidad (m³)'}
              type="number"
              step="any"
              min={0}
              value={volume}
              onChange={(e) => setVolume(e.target.value)}
            />
          )}
        </div>

        <CustomFieldsSection
          entityType="delivery_goods"
          value={customData}
          onChange={setCustomData}
          systemValues={{ unit, min_stock: minStock, unit_cost: unitCost, weight_kg_per_unit: weight, volume_m3_per_unit: volume }}
          rules={rules}
        />

        {error && <p className="text-sm text-danger">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose} disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button onClick={() => void handleSubmit()} disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Crear'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
