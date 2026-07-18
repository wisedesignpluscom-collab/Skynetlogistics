import { useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { WarehouseFormModal } from '../components/tires/WarehouseFormModal'
import { useWarehouses } from '../features/tires/hooks'
import { createWarehouse, updateWarehouse } from '../features/tires/api'
import { useAuth } from '../features/auth/AuthContext'
import type { Warehouse } from '../types/tire'

type ModalState = { mode: 'create' } | { mode: 'edit'; warehouse: Warehouse } | null

export function WarehousesPage() {
  const { hasPermission } = useAuth()
  const { data, isLoading, reload } = useWarehouses()
  const [modalState, setModalState] = useState<ModalState>(null)
  const canWrite = hasPermission('tires', 'write')

  return (
    <DashboardLayout>
      <Link to="/tires" className="text-sm text-text-muted hover:text-gold">
        ← Volver a neumáticos
      </Link>

      <div className="mt-4 mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Almacenes</h1>
        {canWrite && <Button onClick={() => setModalState({ mode: 'create' })}>Nuevo almacén</Button>}
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}

      {data && (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface text-text-muted">
              <tr>
                <th className="px-4 py-3 font-medium">Nombre</th>
                <th className="px-4 py-3 font-medium">Ubicación</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.items.map((warehouse) => (
                <tr key={warehouse.id} className="bg-background/40">
                  <td className="px-4 py-3 text-text">{warehouse.name}</td>
                  <td className="px-4 py-3 text-text-muted">{warehouse.location ?? '—'}</td>
                  <td className="px-4 py-3 text-right">
                    {canWrite && (
                      <button
                        onClick={() => setModalState({ mode: 'edit', warehouse })}
                        className="text-text-muted hover:text-gold"
                      >
                        Editar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {data.items.length === 0 && (
                <tr>
                  <td colSpan={3} className="px-4 py-8 text-center text-text-muted">
                    No hay almacenes registrados.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {modalState && (
        <WarehouseFormModal
          initialWarehouse={modalState.mode === 'edit' ? modalState.warehouse : undefined}
          onClose={() => setModalState(null)}
          onSubmit={async (values) => {
            if (modalState.mode === 'create') {
              await createWarehouse(values)
            } else {
              await updateWarehouse(modalState.warehouse.id, values)
            }
            await reload()
          }}
        />
      )}
    </DashboardLayout>
  )
}
