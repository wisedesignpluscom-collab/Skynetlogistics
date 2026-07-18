import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { useDrivers } from '../../features/drivers/hooks'
import type { Vehicle, VehicleStatus, VehicleType } from '../../types/vehicle'
import type { VehiclePayload, VehicleUpdatePayload } from '../../features/vehicles/api'

const VEHICLE_TYPES: VehicleType[] = ['camion', 'remolque', 'cabezal']
const VEHICLE_STATUSES: VehicleStatus[] = ['activo', 'taller', 'inactivo']

interface VehicleFormModalProps {
  mode: 'create' | 'edit'
  initialVehicle?: Vehicle
  onClose: () => void
  onSubmit: (values: VehiclePayload | VehicleUpdatePayload) => Promise<void>
}

export function VehicleFormModal({ mode, initialVehicle, onClose, onSubmit }: VehicleFormModalProps) {
  const { data: driversPage } = useDrivers({ page_size: 100 })
  const [plate, setPlate] = useState(initialVehicle?.plate ?? '')
  const [brand, setBrand] = useState(initialVehicle?.brand ?? '')
  const [model, setModel] = useState(initialVehicle?.model ?? '')
  const [year, setYear] = useState(initialVehicle?.year ?? new Date().getFullYear())
  const [type, setType] = useState<VehicleType>(initialVehicle?.type ?? 'camion')
  const [status, setStatus] = useState<VehicleStatus>(initialVehicle?.status ?? 'activo')
  const [odometer, setOdometer] = useState(initialVehicle?.current_odometer_km ?? 0)
  const [driverId, setDriverId] = useState(initialVehicle?.assigned_driver_id ?? '')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      const assigned_driver_id = driverId || null
      if (mode === 'create') {
        await onSubmit({ plate, brand, model, year, type, assigned_driver_id })
      } else {
        await onSubmit({
          plate,
          brand,
          model,
          year,
          status,
          current_odometer_km: odometer,
          assigned_driver_id,
        })
      }
      onClose()
    } catch {
      setError('No se pudo guardar el vehículo')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={mode === 'create' ? 'Nuevo vehículo' : 'Editar vehículo'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex max-h-[70vh] flex-col gap-4 overflow-y-auto">
        <Input id="plate" label="Placa" value={plate} onChange={(e) => setPlate(e.target.value)} required />
        <div className="grid grid-cols-2 gap-3">
          <Input id="brand" label="Marca" value={brand} onChange={(e) => setBrand(e.target.value)} required />
          <Input id="model" label="Modelo" value={model} onChange={(e) => setModel(e.target.value)} required />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Input
            id="year"
            label="Año"
            type="number"
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            required
          />
          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor="type">
              Tipo
            </label>
            <select
              id="type"
              value={type}
              onChange={(e) => setType(e.target.value as VehicleType)}
              disabled={mode === 'edit'}
              className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold disabled:opacity-50"
            >
              {VEHICLE_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
        </div>

        {mode === 'edit' && (
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-1">
              <label className="text-sm text-text-muted" htmlFor="status">
                Estado
              </label>
              <select
                id="status"
                value={status}
                onChange={(e) => setStatus(e.target.value as VehicleStatus)}
                className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
              >
                {VEHICLE_STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            <Input
              label="Odómetro (km)"
              type="number"
              value={odometer}
              onChange={(e) => setOdometer(Number(e.target.value))}
              min={0}
            />
          </div>
        )}

        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="driver">
            Conductor asignado
          </label>
          <select
            id="driver"
            value={driverId}
            onChange={(e) => setDriverId(e.target.value)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            <option value="">Sin asignar</option>
            {driversPage?.items.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>

        {error && <p className="text-sm text-danger">{error}</p>}
        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Guardar'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
