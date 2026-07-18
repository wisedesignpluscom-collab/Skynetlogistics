import { useState } from 'react'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { UserTable } from '../components/users/UserTable'
import { UserFormModal, type UserFormValues } from '../components/users/UserFormModal'
import { useUsers } from '../features/users/hooks'
import { useRoles } from '../features/roles/hooks'
import { createUser, deactivateUser, updateUser } from '../features/users/api'
import { useAuth } from '../features/auth/AuthContext'
import type { UserWithRole } from '../types/user'

type ModalState = { mode: 'create' } | { mode: 'edit'; user: UserWithRole } | null

export function UsersPage() {
  const { hasPermission } = useAuth()
  const [search, setSearch] = useState('')
  const { data, isLoading, error, reload } = useUsers({ search: search || undefined, page_size: 50 })
  const { roles } = useRoles()
  const [modalState, setModalState] = useState<ModalState>(null)

  const canWrite = hasPermission('users', 'write')
  const canDelete = hasPermission('users', 'delete')

  async function handleDeactivate(user: UserWithRole) {
    if (!window.confirm(`¿Desactivar a ${user.name}?`)) return
    await deactivateUser(user.id)
    await reload()
  }

  async function handleSubmit(values: UserFormValues) {
    if (modalState?.mode === 'create') {
      await createUser({
        name: values.name,
        email: values.email ?? '',
        password: values.password ?? '',
        role_id: values.role_id,
      })
    } else if (modalState?.mode === 'edit') {
      await updateUser(modalState.user.id, { name: values.name, role_id: values.role_id })
    }
    await reload()
  }

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Usuarios</h1>
        {canWrite && <Button onClick={() => setModalState({ mode: 'create' })}>Nuevo usuario</Button>}
      </div>

      <div className="mb-4 max-w-xs">
        <Input
          placeholder="Buscar por nombre o email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}
      {error && <p className="text-danger">{error}</p>}
      {data && (
        <UserTable
          users={data.items}
          canWrite={canWrite}
          canDelete={canDelete}
          onEdit={(user) => setModalState({ mode: 'edit', user })}
          onDeactivate={handleDeactivate}
        />
      )}

      {modalState && (
        <UserFormModal
          mode={modalState.mode}
          roles={roles}
          initialUser={modalState.mode === 'edit' ? modalState.user : undefined}
          onClose={() => setModalState(null)}
          onSubmit={handleSubmit}
        />
      )}
    </DashboardLayout>
  )
}
