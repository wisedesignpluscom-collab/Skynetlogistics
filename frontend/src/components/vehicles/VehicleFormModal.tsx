import { useEffect, useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { CustomFieldsSection } from '../config/CustomFieldsSection'
import { useSystemFieldRules } from '../../features/config/useSystemFieldRules'
import { useDrivers } from '../../features/drivers/hooks'
import { useVehicleOwners } from '../../features/vehicleOwners/hooks'
import type { Vehicle, VehicleStatus, VehicleType } from '../../types/vehicle'
import type { VehiclePayload, VehicleUpdatePayload } from '../../features/vehicles/api'
import type { CustomData } from '../../types/customField'

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
  const { data: ownersPage } = useVehicleOwners({ page_size: 100 })
  const owners = (ownersPage?.items ?? []).filter((o) => o.is_active)

  const [plate, setPlate] = useState(initialVehicle?.plate ?? '')
  const [brand, setBrand] = useState(initialVehicle?.brand ?? '')
  const [model, setModel] = useState(initialVehicle?.model ?? '')
  const [year, setYear] = useState(initialVehicle?.year ?? new Date().getFullYear())
  const [vin, setVin] = useState(initialVehicle?.vin ?? '')
  const [type, setType] = useState<VehicleType>(initialVehicle?.type ?? 'camion')
  const [status, setStatus] = useState<VehicleStatus>(initialVehicle?.status ?? 'activo')
  const [odometer, setOdometer] = useState(initialVehicle?.current_odometer_km ?? 0)
  const [driverId, setDriverId] = useState(initialVehicle?.assigned_driver_id ?? '')
  const [ownerId, setOwnerId] = useState(initialVehicle?.owner_id ?? '')
  const [color, setColor] = useState(initialVehicle?.color ?? '')
  const [engineSerial, setEngineSerial] = useState(initialVehicle?.engine_serial ?? '')
  const [hasOdometer, setHasOdometer] = useState(initialVehicle?.has_odometer ?? true)
  const [odometerDigits, setOdometerDigits] = useState(initialVehicle?.odometer_digits?.toString() ?? '')
  const [cargoCapacity, setCargoCapacity] = useState(initialVehicle?.cargo_capacity_kg?.toString() ?? '')
  const [cargoCapacityM3, setCargoCapacityM3] = useState(initialVehicle?.cargo_capacity_m3?.toString() ?? '')
  const [contract, setContract] = useState(initialVehicle?.contract ?? '')
  const [customData, setCustomData] = useState<CustomData>(initialVehicle?.custom_data ?? {})
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const rules = useSystemFieldRules(
    'vehicle',
    { type, status, brand, model, year, cargo_capacity_kg: cargoCapacity, cargo_capacity_m3: cargoCapacityM3 },
    customData
  )

  // Autocompletar campos de sistema calculados por una regla de formulario.
  useEffect(() => {
    const setters: Record<string, (v: string) => void> = {
      brand: setBrand,
      model: setModel,
      year: (v) => setYear(Number(v)),
      cargo_capacity_kg: setCargoCapacity,
      cargo_capacity_m3: setCargoCapacityM3,
    }
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
      const common = {
        plate,
        brand,
        model,
        year,
        vin: vin || null,
        assigned_driver_id: driverId || null,
        owner_id: ownerId || null,
        color: color || null,
        engine_serial: engineSerial || null,
        has_odometer: hasOdometer,
        odometer_digits: odometerDigits ? Number(odometerDigits) : null,
        cargo_capacity_kg: cargoCapacity ? Number(cargoCapacity) : null,
        cargo_capacity_m3: cargoCapacityM3 ? Number(cargoCapacityM3) : null,
        contract: contract || null,
        custom_data: customData,
      }
      if (mode === 'create') {
        await onSubmit({ ...common, type })
      } else {
        await onSubmit({ ...common, status, current_odometer_km: odometer })
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
        <div className="grid grid-cols-2 gap-3">
          <Input id="plate" label="Placa" value={plate} onChange={(e) => setPlate(e.target.value)} required />
          <Input id="vin" label="VIN / Serial de carrocería" value={vin} onChange={(e) => setVin(e.target.value)} />
        </div>
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
        <div className="grid grid-cols-2 gap-3">
          {!rules.isHidden('year') && (
            <Input
              id="year"
              label={rules.isRequired('year') ? 'Año *' : 'Año'}
              type="number"
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              required
            />
          )}
          {!rules.isHidden('type') && (
            <div className="flex flex-col gap-1">
              <label className="text-sm text-text-muted" htmlFor="type">
                {rules.isRequired('type') ? 'Tipo *' : 'Tipo'}
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
          )}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Input id="color" label="Color" value={color} onChange={(e) => setColor(e.target.value)} />
          <Input
            id="engine_serial"
            label="Serial del motor"
            value={engineSerial}
            onChange={(e) => setEngineSerial(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          {!rules.isHidden('cargo_capacity_kg') && (
            <Input
              id="cargo_capacity"
              label={rules.isRequired('cargo_capacity_kg') ? 'Capacidad de carga (kg) *' : 'Capacidad de carga (kg)'}
              type="number"
              min={0}
              step="any"
              value={cargoCapacity}
              onChange={(e) => setCargoCapacity(e.target.value)}
              required={rules.isRequired('cargo_capacity_kg')}
            />
          )}
          {!rules.isHidden('cargo_capacity_m3') && (
            <Input
              id="cargo_capacity_m3"
              label={rules.isRequired('cargo_capacity_m3') ? 'Capacidad de carga (m³) *' : 'Capacidad de carga (m³)'}
              type="number"
              min={0}
              step="any"
              value={cargoCapacityM3}
              onChange={(e) => setCargoCapacityM3(e.target.value)}
              required={rules.isRequired('cargo_capacity_m3')}
            />
          )}
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Input id="contract" label="Contrato" value={contract} onChange={(e) => setContract(e.target.value)} />
        </div>

        <div className="grid grid-cols-2 gap-3 items-end">
          <label className="flex items-center gap-2 text-sm text-text-muted">
            <input
              type="checkbox"
              checked={hasOdometer}
              onChange={(e) => setHasOdometer(e.target.checked)}
              className="rounded border-border"
            />
            Posee odómetro
          </label>
          <Input
            id="odometer_digits"
            label="N° de dígitos del odómetro"
            type="number"
            min={1}
            value={odometerDigits}
            onChange={(e) => setOdometerDigits(e.target.value)}
            disabled={!hasOdometer}
          />
        </div>

        {mode === 'edit' && (
          <div className="grid grid-cols-2 gap-3">
            {!rules.isHidden('status') && (
              <div className="flex flex-col gap-1">
                <label className="text-sm text-text-muted" htmlFor="status">
                  {rules.isRequired('status') ? 'Estado *' : 'Estado'}
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
            )}
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

        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="owner">
            Propietario
          </label>
          <select
            id="owner"
            value={ownerId}
            onChange={(e) => setOwnerId(e.target.value)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            <option value="">Propio (sin especificar)</option>
            {owners.map((o) => (
              <option key={o.id} value={o.id}>
                {o.name}
              </option>
            ))}
          </select>
        </div>

        <CustomFieldsSection
          entityType="vehicle"
          value={customData}
          onChange={setCustomData}
          systemValues={{
            type,
            status,
            brand,
            model,
            year,
            cargo_capacity_kg: cargoCapacity,
            cargo_capacity_m3: cargoCapacityM3,
          }}
          rules={rules}
        />

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
