import { useEffect, useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { CustomFieldsSection } from '../config/CustomFieldsSection'
import { useSystemFieldRules } from '../../features/config/useSystemFieldRules'
import type { TireCreatePayload } from '../../features/tires/api'
import type { Warehouse } from '../../types/tire'
import type { CustomData } from '../../types/customField'

interface TireFormModalProps {
  warehouses: Warehouse[]
  onClose: () => void
  onSubmit: (values: TireCreatePayload) => Promise<void>
}

export function TireFormModal({ warehouses, onClose, onSubmit }: TireFormModalProps) {
  const [uniqueCode, setUniqueCode] = useState('')
  const [brand, setBrand] = useState('')
  const [model, setModel] = useState('')
  const [thickness, setThickness] = useState('')
  const [warehouseId, setWarehouseId] = useState('')
  const [customData, setCustomData] = useState<CustomData>({})
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const rules = useSystemFieldRules('tire', { brand, model, current_thickness_mm: thickness }, customData)

  useEffect(() => {
    const setters: Record<string, (v: string) => void> = { brand: setBrand, model: setModel, current_thickness_mm: setThickness }
    for (const [key, computedVal] of Object.entries(rules.computed)) {
      setters[key]?.(String(computedVal))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(rules.computed)])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        unique_code: uniqueCode,
        brand,
        model,
        current_thickness_mm: Number(thickness),
        warehouse_id: warehouseId || null,
        custom_data: customData,
      })
      onClose()
    } catch {
      setError('No se pudo crear el neumático (¿código ya existe?)')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title="Nuevo neumático" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          id="unique_code"
          label="Código único"
          value={uniqueCode}
          onChange={(e) => setUniqueCode(e.target.value)}
          required
        />
        <div className="grid grid-cols-2 gap-3">
          {!rules.isHidden('brand') && (
            <Input
              id="brand"
              label={rules.isRequired('brand') ? 'Marca *' : 'Marca'}
              value={brand}
              onChange={(e) => setBrand(e.target.value)}
              required
            />
          )}
          {!rules.isHidden('model') && (
            <Input
              id="model"
              label={rules.isRequired('model') ? 'Modelo *' : 'Modelo'}
              value={model}
              onChange={(e) => setModel(e.target.value)}
              required
            />
          )}
        </div>
        {!rules.isHidden('current_thickness_mm') && (
          <Input
            id="thickness"
            label={rules.isRequired('current_thickness_mm') ? 'Espesor inicial (mm) *' : 'Espesor inicial (mm)'}
            type="number"
            min={0}
            max={99.9}
            step="0.1"
            value={thickness}
            onChange={(e) => setThickness(e.target.value)}
            required
          />
        )}
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="warehouse_id">
            Almacén (opcional)
          </label>
          <select
            id="warehouse_id"
            value={warehouseId}
            onChange={(e) => setWarehouseId(e.target.value)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            <option value="">Sin asignar</option>
            {warehouses.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name}
              </option>
            ))}
          </select>
        </div>

        <CustomFieldsSection
          entityType="tire"
          value={customData}
          onChange={setCustomData}
          systemValues={{ brand, model, current_thickness_mm: thickness }}
          rules={rules}
        />

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
