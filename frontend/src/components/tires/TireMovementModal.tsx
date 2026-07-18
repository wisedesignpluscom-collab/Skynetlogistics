import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { useVehicles } from '../../features/vehicles/hooks'
import { useProviders } from '../../features/providers/hooks'
import type { TireMovementPayload } from '../../features/tires/api'
import type { AxleDualPosition, AxleSide, Tire, TireMovementType, TireStatus, Warehouse } from '../../types/tire'

const AXLE_SIDES: AxleSide[] = ['izquierdo', 'derecho', 'unico']
const AXLE_DUAL_POSITIONS: AxleDualPosition[] = ['unico', 'interior', 'exterior']

const VALID_MOVEMENTS_BY_STATUS: Record<TireStatus, TireMovementType[]> = {
  almacen: ['instalacion', 'envio_reparacion', 'envio_reencauche'],
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

export interface AxlePrefill {
  vehicleId: string
  axleNumber: number
  axleSide: AxleSide
  axleDualPosition: AxleDualPosition
}

interface TireMovementModalProps {
  tire: Tire
  warehouses: Warehouse[]
  prefill?: AxlePrefill
  onClose: () => void
  onSubmit: (payload: TireMovementPayload) => Promise<void>
}

export function TireMovementModal({ tire, warehouses, prefill, onClose, onSubmit }: TireMovementModalProps) {
  const options = VALID_MOVEMENTS_BY_STATUS[tire.status]
  const { data: vehiclesPage } = useVehicles({ page_size: 100 })
  const { providers } = useProviders()

  const [movementType, setMovementType] = useState<TireMovementType>(prefill ? 'instalacion' : options[0])
  const [vehicleId, setVehicleId] = useState(prefill?.vehicleId ?? '')
  const [axleNumber, setAxleNumber] = useState(prefill?.axleNumber ?? 1)
  const [axleSide, setAxleSide] = useState<AxleSide>(prefill?.axleSide ?? 'izquierdo')
  const [axleDualPosition, setAxleDualPosition] = useState<AxleDualPosition>(prefill?.axleDualPosition ?? 'unico')
  const [warehouseId, setWarehouseId] = useState('')
  const [providerId, setProviderId] = useState('')
  const [thicknessMm, setThicknessMm] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      const payload: TireMovementPayload = {
        tire_id: tire.id,
        movement_type: movementType,
        thickness_mm: thicknessMm ? Number(thicknessMm) : null,
        notes: notes || null,
      }
      if (movementType === 'instalacion') {
        payload.vehicle_id = vehicleId
        payload.axle_number = axleNumber
        payload.axle_side = axleSide
        payload.axle_dual_position = axleDualPosition
      }
      if (movementType === 'desinstalacion' || movementType === 'retorno_taller') {
        payload.warehouse_id = warehouseId
      }
      if (movementType === 'envio_reparacion' || movementType === 'envio_reencauche') {
        payload.provider_id = providerId || null
      }
      await onSubmit(payload)
      onClose()
    } catch {
      setError('No se pudo registrar el movimiento')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={`Movimiento — ${tire.unique_code}`} onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="movement_type">
            Tipo de movimiento
          </label>
          <select
            id="movement_type"
            value={movementType}
            onChange={(e) => setMovementType(e.target.value as TireMovementType)}
            disabled={!!prefill || options.length === 1}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold disabled:opacity-50"
          >
            {options.map((type) => (
              <option key={type} value={type}>
                {MOVEMENT_LABELS[type]}
              </option>
            ))}
          </select>
        </div>

        {movementType === 'instalacion' && (
          <>
            <div className="flex flex-col gap-1">
              <label className="text-sm text-text-muted" htmlFor="vehicle_id">
                Vehículo
              </label>
              <select
                id="vehicle_id"
                value={vehicleId}
                onChange={(e) => setVehicleId(e.target.value)}
                disabled={!!prefill}
                required
                className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold disabled:opacity-50"
              >
                <option value="">Seleccionar…</option>
                {vehiclesPage?.items.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.plate}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <Input
                id="axle_number"
                label="Eje"
                type="number"
                min={1}
                max={10}
                value={axleNumber}
                onChange={(e) => setAxleNumber(Number(e.target.value))}
                disabled={!!prefill}
                required
              />
              <div className="flex flex-col gap-1">
                <label className="text-sm text-text-muted" htmlFor="axle_side">
                  Lado
                </label>
                <select
                  id="axle_side"
                  value={axleSide}
                  onChange={(e) => setAxleSide(e.target.value as AxleSide)}
                  disabled={!!prefill}
                  className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold disabled:opacity-50"
                >
                  {AXLE_SIDES.map((side) => (
                    <option key={side} value={side}>
                      {side}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-sm text-text-muted" htmlFor="axle_dual_position">
                  Rodado
                </label>
                <select
                  id="axle_dual_position"
                  value={axleDualPosition}
                  onChange={(e) => setAxleDualPosition(e.target.value as AxleDualPosition)}
                  disabled={!!prefill}
                  className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold disabled:opacity-50"
                >
                  {AXLE_DUAL_POSITIONS.map((pos) => (
                    <option key={pos} value={pos}>
                      {pos}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </>
        )}

        {(movementType === 'desinstalacion' || movementType === 'retorno_taller') && (
          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor="warehouse_id">
              Almacén destino
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
        )}

        {(movementType === 'envio_reparacion' || movementType === 'envio_reencauche') && (
          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor="provider_id">
              Proveedor (opcional)
            </label>
            <select
              id="provider_id"
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

        <Input
          id="thickness_mm"
          label="Espesor medido en este movimiento (mm, opcional)"
          type="number"
          min={0}
          max={99.9}
          step="0.1"
          value={thicknessMm}
          onChange={(e) => setThicknessMm(e.target.value)}
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
