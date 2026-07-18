import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { VehicleAxleDiagram, type AxleSlot } from '../components/tires/VehicleAxleDiagram'
import { InstallTireModal } from '../components/tires/InstallTireModal'
import { TireMovementModal, type AxlePrefill } from '../components/tires/TireMovementModal'
import { getVehicle } from '../features/vehicles/api'
import { useVehicleTires, useWarehouses, useTireSettings } from '../features/tires/hooks'
import { createTireMovement } from '../features/tires/api'
import { useAuth } from '../features/auth/AuthContext'
import type { Vehicle } from '../types/vehicle'
import type { Tire } from '../types/tire'

export function VehicleTiresPage() {
  const { vehicleId } = useParams<{ vehicleId: string }>()
  const { hasPermission } = useAuth()
  const [vehicle, setVehicle] = useState<Vehicle | null>(null)
  const { tires, isLoading, reload } = useVehicleTires(vehicleId)
  const { data: warehousesPage } = useWarehouses()
  const { settings } = useTireSettings()
  const [installPrefill, setInstallPrefill] = useState<AxlePrefill | null>(null)
  const [movementTire, setMovementTire] = useState<Tire | null>(null)

  const canWrite = hasPermission('tires', 'write')

  const reloadVehicle = useCallback(async () => {
    if (!vehicleId) return
    setVehicle(await getVehicle(vehicleId))
  }, [vehicleId])

  useEffect(() => {
    void reloadVehicle()
  }, [reloadVehicle])

  function handleSlotClick(slot: AxleSlot) {
    if (!canWrite || !vehicleId) return
    if (slot.tire) {
      setMovementTire(slot.tire)
    } else {
      setInstallPrefill({
        vehicleId,
        axleNumber: slot.axleNumber,
        axleSide: slot.side,
        axleDualPosition: slot.dualPosition,
      })
    }
  }

  if (!vehicle || isLoading) {
    return (
      <DashboardLayout>
        <p className="text-text-muted">Cargando…</p>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <Link to={`/vehicles/${vehicle.id}`} className="text-sm text-text-muted hover:text-gold">
        ← Volver a {vehicle.plate}
      </Link>

      <div className="mt-4 mb-6">
        <h1 className="font-display text-2xl text-text">Neumáticos — {vehicle.plate}</h1>
        <p className="text-text-muted">
          {vehicle.brand} {vehicle.model} · {tires.length} neumáticos instalados
        </p>
      </div>

      <VehicleAxleDiagram
        vehicleType={vehicle.type}
        tires={tires}
        disparityThresholdMm={settings?.disparity_threshold_mm ?? 3}
        onSlotClick={handleSlotClick}
      />

      {installPrefill && (
        <InstallTireModal
          prefill={installPrefill}
          onClose={() => setInstallPrefill(null)}
          onSubmit={async (payload) => {
            await createTireMovement(payload)
            await reload()
          }}
        />
      )}

      {movementTire && (
        <TireMovementModal
          tire={movementTire}
          warehouses={warehousesPage?.items ?? []}
          onClose={() => setMovementTire(null)}
          onSubmit={async (payload) => {
            await createTireMovement(payload)
            await reload()
          }}
        />
      )}
    </DashboardLayout>
  )
}
