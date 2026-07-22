import { useState } from 'react'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { ClientTable } from '../components/clients/ClientTable'
import { ClientFormModal } from '../components/clients/ClientFormModal'
import { useClients } from '../features/clients/hooks'
import { createClient, deactivateClient, updateClient } from '../features/clients/api'
import { useAuth } from '../features/auth/AuthContext'
import type { Client } from '../types/client'
import type { ClientPayload } from '../features/clients/api'

type ModalState = { mode: 'create' } | { mode: 'edit'; client: Client } | null

export function ClientsPage() {
  const { hasPermission } = useAuth()
  const [search, setSearch] = useState('')
  const { data, isLoading, error, reload } = useClients({ search: search || undefined, page_size: 50 })
  const [modalState, setModalState] = useState<ModalState>(null)

  const canWrite = hasPermission('trips', 'write')
  const canDelete = hasPermission('trips', 'delete')

  async function handleDeactivate(c: Client) {
    if (!window.confirm(`¿Desactivar al cliente ${c.name}?`)) return
    await deactivateClient(c.id)
    await reload()
  }

  async function handleSubmit(values: ClientPayload) {
    if (modalState?.mode === 'create') {
      await createClient(values)
    } else if (modalState?.mode === 'edit') {
      await updateClient(modalState.client.id, values)
    }
    await reload()
  }

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Clientes</h1>
        {canWrite && <Button onClick={() => setModalState({ mode: 'create' })}>Nuevo cliente</Button>}
      </div>

      <div className="mb-4 max-w-xs">
        <Input placeholder="Buscar por nombre…" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}
      {error && <p className="text-danger">{error}</p>}
      {data && (
        <ClientTable
          clients={data.items}
          canWrite={canWrite}
          canDelete={canDelete}
          onEdit={(c) => setModalState({ mode: 'edit', client: c })}
          onDeactivate={handleDeactivate}
        />
      )}

      {modalState && (
        <ClientFormModal
          mode={modalState.mode}
          initialClient={modalState.mode === 'edit' ? modalState.client : undefined}
          onClose={() => setModalState(null)}
          onSubmit={handleSubmit}
        />
      )}
    </DashboardLayout>
  )
}
