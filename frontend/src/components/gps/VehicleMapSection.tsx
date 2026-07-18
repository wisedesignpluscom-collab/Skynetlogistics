import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { createVehicleMap, deleteVehicleMap, listVehicleMap } from '../../features/gps/api'
import { useVehicles } from '../../features/vehicles/hooks'
import type { GPSProviderVehicleMap } from '../../types/gps'

interface VehicleMapSectionProps {
  providerId: string
  canWrite: boolean
}

export function VehicleMapSection({ providerId, canWrite }: VehicleMapSectionProps) {
  const { data: vehiclesPage } = useVehicles({ page_size: 100, status_filter: 'activo' })
  const [mappings, setMappings] = useState<GPSProviderVehicleMap[]>([])
  const [vehicleId, setVehicleId] = useState('')
  const [externalDeviceId, setExternalDeviceId] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const reload = useCallback(async () => {
    setMappings(await listVehicleMap(providerId))
  }, [providerId])

  useEffect(() => {
    void reload()
  }, [reload])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await createVehicleMap(providerId, { vehicle_id: vehicleId, external_device_id: externalDeviceId })
      setVehicleId('')
      setExternalDeviceId('')
      await reload()
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleDelete(mappingId: string) {
    if (!window.confirm('¿Eliminar este mapeo?')) return
    await deleteVehicleMap(providerId, mappingId)
    await reload()
  }

  return (
    <div className="mt-4 flex flex-col gap-3 border-t border-border pt-4">
      <p className="text-sm text-text-muted">Mapeo de vehículos a device ID externo</p>
      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface text-text-muted">
            <tr>
              <th className="px-4 py-2 font-medium">Vehículo</th>
              <th className="px-4 py-2 font-medium">Device ID externo</th>
              {canWrite && <th className="px-4 py-2" />}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {mappings.map((m) => {
              const v = vehiclesPage?.items.find((veh) => veh.id === m.vehicle_id)
              return (
                <tr key={m.id}>
                  <td className="px-4 py-2">{v?.plate ?? m.vehicle_id}</td>
                  <td className="px-4 py-2 text-text-muted">{m.external_device_id}</td>
                  {canWrite && (
                    <td className="px-4 py-2 text-right">
                      <button onClick={() => handleDelete(m.id)} className="text-text-muted hover:text-danger">
                        Eliminar
                      </button>
                    </td>
                  )}
                </tr>
              )
            })}
            {mappings.length === 0 && (
              <tr>
                <td colSpan={canWrite ? 3 : 2} className="px-4 py-4 text-center text-text-muted">
                  Sin vehículos mapeados.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {canWrite && (
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3">
          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor={`vehicle-${providerId}`}>
              Vehículo
            </label>
            <select
              id={`vehicle-${providerId}`}
              value={vehicleId}
              onChange={(e) => setVehicleId(e.target.value)}
              required
              className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
            >
              <option value="">Selecciona…</option>
              {vehiclesPage?.items.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.plate}
                </option>
              ))}
            </select>
          </div>
          <Input
            id={`device-${providerId}`}
            label="Device ID externo"
            value={externalDeviceId}
            onChange={(e) => setExternalDeviceId(e.target.value)}
            required
          />
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Mapear'}
          </Button>
        </form>
      )}
    </div>
  )
}
