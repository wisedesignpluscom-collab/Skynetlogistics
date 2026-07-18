import { useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { DriverTable } from '../components/drivers/DriverTable'
import { DriverFormModal } from '../components/drivers/DriverFormModal'
import { useDrivers } from '../features/drivers/hooks'
import { createDriver, deactivateDriver, updateDriver } from '../features/drivers/api'
import { useFatigueSummary } from '../features/fatigue/hooks'
import { useAuth } from '../features/auth/AuthContext'
import type { Driver } from '../types/driver'
import type { DriverPayload, DriverUpdatePayload } from '../features/drivers/api'

type ModalState = { mode: 'create' } | { mode: 'edit'; driver: Driver } | null

export function DriversPage() {
  const { hasPermission } = useAuth()
  const [search, setSearch] = useState('')
  const { data, isLoading, error, reload } = useDrivers({ search: search || undefined, page_size: 50 })
  const { summaryByDriver } = useFatigueSummary()
  const [modalState, setModalState] = useState<ModalState>(null)

  const canWrite = hasPermission('drivers', 'write')
  const canDelete = hasPermission('drivers', 'delete')

  async function handleDeactivate(driver: Driver) {
    if (!window.confirm(`¿Desactivar a ${driver.name}?`)) return
    await deactivateDriver(driver.id)
    await reload()
  }

  async function handleSubmit(values: DriverPayload | DriverUpdatePayload) {
    if (modalState?.mode === 'create') {
      await createDriver(values as DriverPayload)
    } else if (modalState?.mode === 'edit') {
      await updateDriver(modalState.driver.id, values as DriverUpdatePayload)
    }
    await reload()
  }

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Conductores</h1>
        <div className="flex gap-3">
          {hasPermission('fatigue', 'read') && (
            <Link to="/fatigue-settings">
              <Button variant="secondary">Reglas de fatiga</Button>
            </Link>
          )}
          {canWrite && <Button onClick={() => setModalState({ mode: 'create' })}>Nuevo conductor</Button>}
        </div>
      </div>

      <div className="mb-4 max-w-xs">
        <Input
          placeholder="Buscar por nombre o licencia…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}
      {error && <p className="text-danger">{error}</p>}
      {data && (
        <DriverTable
          drivers={data.items}
          canWrite={canWrite}
          canDelete={canDelete}
          fatigueByDriver={summaryByDriver}
          onEdit={(driver) => setModalState({ mode: 'edit', driver })}
          onDeactivate={handleDeactivate}
        />
      )}

      {modalState && (
        <DriverFormModal
          mode={modalState.mode}
          initialDriver={modalState.mode === 'edit' ? modalState.driver : undefined}
          onClose={() => setModalState(null)}
          onSubmit={handleSubmit}
        />
      )}
    </DashboardLayout>
  )
}
