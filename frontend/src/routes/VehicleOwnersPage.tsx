import { useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { VehicleOwnerTable } from '../components/vehicleOwners/VehicleOwnerTable'
import { VehicleOwnerFormModal } from '../components/vehicleOwners/VehicleOwnerFormModal'
import { useVehicleOwners } from '../features/vehicleOwners/hooks'
import { createVehicleOwner, deactivateVehicleOwner, updateVehicleOwner } from '../features/vehicleOwners/api'
import { useAuth } from '../features/auth/AuthContext'
import type { VehicleOwner } from '../types/vehicle_owner'
import type { VehicleOwnerPayload } from '../features/vehicleOwners/api'

type ModalState = { mode: 'create' } | { mode: 'edit'; owner: VehicleOwner } | null

export function VehicleOwnersPage() {
  const { hasPermission } = useAuth()
  const [search, setSearch] = useState('')
  const { data, isLoading, error, reload } = useVehicleOwners({ search: search || undefined, page_size: 50 })
  const [modalState, setModalState] = useState<ModalState>(null)

  const canWrite = hasPermission('vehicles', 'write')
  const canDelete = hasPermission('vehicles', 'delete')

  async function handleDeactivate(owner: VehicleOwner) {
    if (!window.confirm(`¿Desactivar al propietario ${owner.name}?`)) return
    await deactivateVehicleOwner(owner.id)
    await reload()
  }

  async function handleSubmit(values: VehicleOwnerPayload) {
    if (modalState?.mode === 'create') {
      await createVehicleOwner(values)
    } else if (modalState?.mode === 'edit') {
      await updateVehicleOwner(modalState.owner.id, values)
    }
    await reload()
  }

  return (
    <DashboardLayout>
      <Link to="/vehicles" className="text-sm text-text-muted hover:text-gold">
        ← Volver a vehículos
      </Link>

      <div className="mt-4 mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Propietarios</h1>
        {canWrite && <Button onClick={() => setModalState({ mode: 'create' })}>Nuevo propietario</Button>}
      </div>

      <div className="mb-4 max-w-xs">
        <Input placeholder="Buscar por nombre…" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}
      {error && <p className="text-danger">{error}</p>}
      {data && (
        <VehicleOwnerTable
          owners={data.items}
          canWrite={canWrite}
          canDelete={canDelete}
          onEdit={(owner) => setModalState({ mode: 'edit', owner })}
          onDeactivate={handleDeactivate}
        />
      )}

      {modalState && (
        <VehicleOwnerFormModal
          mode={modalState.mode}
          initialOwner={modalState.mode === 'edit' ? modalState.owner : undefined}
          onClose={() => setModalState(null)}
          onSubmit={handleSubmit}
        />
      )}
    </DashboardLayout>
  )
}
