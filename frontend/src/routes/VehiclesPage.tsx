import { useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { VehicleTable } from '../components/vehicles/VehicleTable'
import { VehicleFormModal } from '../components/vehicles/VehicleFormModal'
import { useVehicles } from '../features/vehicles/hooks'
import { createVehicle, deactivateVehicle, updateVehicle } from '../features/vehicles/api'
import { useAuth } from '../features/auth/AuthContext'
import type { Vehicle, VehicleStatus, VehicleType } from '../types/vehicle'
import type { VehiclePayload, VehicleUpdatePayload } from '../features/vehicles/api'

type ModalState = { mode: 'create' } | { mode: 'edit'; vehicle: Vehicle } | null

export function VehiclesPage() {
  const { hasPermission } = useAuth()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<VehicleStatus | ''>('')
  const [typeFilter, setTypeFilter] = useState<VehicleType | ''>('')
  const { data, isLoading, error, reload } = useVehicles({
    search: search || undefined,
    status_filter: statusFilter || undefined,
    type: typeFilter || undefined,
    page_size: 50,
  })
  const [modalState, setModalState] = useState<ModalState>(null)

  const canWrite = hasPermission('vehicles', 'write')
  const canDelete = hasPermission('vehicles', 'delete')

  async function handleDeactivate(vehicle: Vehicle) {
    if (!window.confirm(`¿Desactivar el vehículo ${vehicle.plate}?`)) return
    await deactivateVehicle(vehicle.id)
    await reload()
  }

  async function handleSubmit(values: VehiclePayload | VehicleUpdatePayload) {
    if (modalState?.mode === 'create') {
      await createVehicle(values as VehiclePayload)
    } else if (modalState?.mode === 'edit') {
      await updateVehicle(modalState.vehicle.id, values as VehicleUpdatePayload)
    }
    await reload()
  }

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Vehículos</h1>
        <div className="flex gap-3">
          <Link to="/vehicle-owners">
            <Button variant="secondary">Propietarios</Button>
          </Link>
          {canWrite && <Button onClick={() => setModalState({ mode: 'create' })}>Nuevo vehículo</Button>}
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        <Input
          placeholder="Buscar por placa o marca…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as VehicleStatus | '')}
          className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
        >
          <option value="">Todos los estados</option>
          <option value="activo">Activo</option>
          <option value="taller">Taller</option>
          <option value="inactivo">Inactivo</option>
        </select>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value as VehicleType | '')}
          className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
        >
          <option value="">Todos los tipos</option>
          <option value="camion">Camión</option>
          <option value="remolque">Remolque</option>
          <option value="cabezal">Cabezal</option>
        </select>
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}
      {error && <p className="text-danger">{error}</p>}
      {data && (
        <VehicleTable
          vehicles={data.items}
          canWrite={canWrite}
          canDelete={canDelete}
          onEdit={(vehicle) => setModalState({ mode: 'edit', vehicle })}
          onDeactivate={handleDeactivate}
        />
      )}

      {modalState && (
        <VehicleFormModal
          mode={modalState.mode}
          initialVehicle={modalState.mode === 'edit' ? modalState.vehicle : undefined}
          onClose={() => setModalState(null)}
          onSubmit={handleSubmit}
        />
      )}
    </DashboardLayout>
  )
}
