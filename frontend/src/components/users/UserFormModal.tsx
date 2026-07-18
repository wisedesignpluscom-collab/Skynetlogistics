import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import type { Role } from '../../types/role'
import type { UserWithRole } from '../../types/user'

export interface UserFormValues {
  name: string
  email?: string
  password?: string
  role_id: string
}

interface UserFormModalProps {
  mode: 'create' | 'edit'
  roles: Role[]
  initialUser?: UserWithRole
  onClose: () => void
  onSubmit: (values: UserFormValues) => Promise<void>
}

export function UserFormModal({ mode, roles, initialUser, onClose, onSubmit }: UserFormModalProps) {
  const [name, setName] = useState(initialUser?.name ?? '')
  const [email, setEmail] = useState(initialUser?.email ?? '')
  const [password, setPassword] = useState('')
  const [roleId, setRoleId] = useState(initialUser?.role_id ?? roles[0]?.id ?? '')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit(mode === 'create' ? { name, email, password, role_id: roleId } : { name, role_id: roleId })
      onClose()
    } catch {
      setError('No se pudo guardar el usuario')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={mode === 'create' ? 'Nuevo usuario' : 'Editar usuario'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input id="name" label="Nombre" value={name} onChange={(e) => setName(e.target.value)} required />
        {mode === 'create' && (
          <>
            <Input
              id="email"
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              id="password"
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              required
            />
          </>
        )}
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="role_id">
            Rol
          </label>
          <select
            id="role_id"
            value={roleId}
            onChange={(e) => setRoleId(e.target.value)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
            required
          >
            {roles.map((role) => (
              <option key={role.id} value={role.id}>
                {role.name}
              </option>
            ))}
          </select>
        </div>
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
