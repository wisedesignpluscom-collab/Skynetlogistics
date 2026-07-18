import { useState, type FormEvent } from 'react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { useRateTables } from '../../features/tripSettings/hooks'
import { createRateTable, deleteRateTable } from '../../features/tripSettings/api'
import type { VehicleType } from '../../types/vehicle'

const VEHICLE_TYPES: VehicleType[] = ['camion', 'remolque', 'cabezal']

export function RateTableSection({ canWrite }: { canWrite: boolean }) {
  const { rateTables, isLoading, reload } = useRateTables()
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [vehicleType, setVehicleType] = useState<VehicleType>('camion')
  const [cargoType, setCargoType] = useState('')
  const [distanceKm, setDistanceKm] = useState('')
  const [freightAmount, setFreightAmount] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await createRateTable({
        origin,
        destination,
        vehicle_type: vehicleType,
        cargo_type: cargoType,
        distance_km: Number(distanceKm),
        freight_amount: Number(freightAmount),
      })
      setOrigin('')
      setDestination('')
      setCargoType('')
      setDistanceKm('')
      setFreightAmount('')
      await reload()
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm('¿Eliminar este tabulado?')) return
    await deleteRateTable(id)
    await reload()
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface text-text-muted">
            <tr>
              <th className="px-4 py-2 font-medium">Ruta</th>
              <th className="px-4 py-2 font-medium">Unidad</th>
              <th className="px-4 py-2 font-medium">Carga</th>
              <th className="px-4 py-2 font-medium">Distancia</th>
              <th className="px-4 py-2 font-medium">Flete</th>
              {canWrite && <th className="px-4 py-2" />}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {rateTables.map((rt) => (
              <tr key={rt.id}>
                <td className="px-4 py-2">
                  {rt.origin} → {rt.destination}
                </td>
                <td className="px-4 py-2 text-text-muted">{rt.vehicle_type}</td>
                <td className="px-4 py-2 text-text-muted">{rt.cargo_type}</td>
                <td className="px-4 py-2 text-text-muted">{rt.distance_km} km</td>
                <td className="px-4 py-2 text-text-muted">${rt.freight_amount}</td>
                {canWrite && (
                  <td className="px-4 py-2 text-right">
                    <button onClick={() => handleDelete(rt.id)} className="text-text-muted hover:text-danger">
                      Eliminar
                    </button>
                  </td>
                )}
              </tr>
            ))}
            {!isLoading && rateTables.length === 0 && (
              <tr>
                <td colSpan={canWrite ? 6 : 5} className="px-4 py-6 text-center text-text-muted">
                  No hay tabulados de flete configurados.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {canWrite && (
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3 rounded-lg border border-border p-4">
          <Input id="rt_origin" label="Origen" value={origin} onChange={(e) => setOrigin(e.target.value)} required />
          <Input
            id="rt_destination"
            label="Destino"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            required
          />
          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor="rt_vehicle_type">
              Tipo de unidad
            </label>
            <select
              id="rt_vehicle_type"
              value={vehicleType}
              onChange={(e) => setVehicleType(e.target.value as VehicleType)}
              className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
            >
              {VEHICLE_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
          <Input
            id="rt_cargo_type"
            label="Tipo de carga"
            value={cargoType}
            onChange={(e) => setCargoType(e.target.value)}
            required
          />
          <Input
            id="rt_distance"
            label="Distancia (km)"
            type="number"
            min={0}
            value={distanceKm}
            onChange={(e) => setDistanceKm(e.target.value)}
            required
          />
          <Input
            id="rt_freight"
            label="Flete ($)"
            type="number"
            min={0}
            step="0.01"
            value={freightAmount}
            onChange={(e) => setFreightAmount(e.target.value)}
            required
          />
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Agregar'}
          </Button>
        </form>
      )}
    </div>
  )
}
