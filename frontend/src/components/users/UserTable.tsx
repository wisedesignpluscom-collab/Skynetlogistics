import type { UserWithRole } from '../../types/user'
import { Badge } from '../ui/Badge'

interface UserTableProps {
  users: UserWithRole[]
  canWrite: boolean
  canDelete: boolean
  onEdit: (user: UserWithRole) => void
  onDeactivate: (user: UserWithRole) => void
}

export function UserTable({ users, canWrite, canDelete, onEdit, onDeactivate }: UserTableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface text-text-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Nombre</th>
            <th className="px-4 py-3 font-medium">Email</th>
            <th className="px-4 py-3 font-medium">Rol</th>
            <th className="px-4 py-3 font-medium">Estado</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {users.map((user) => (
            <tr key={user.id} className="bg-background/40">
              <td className="px-4 py-3">{user.name}</td>
              <td className="px-4 py-3 text-text-muted">{user.email}</td>
              <td className="px-4 py-3">
                <Badge tone="gold">{user.role.name}</Badge>
              </td>
              <td className="px-4 py-3">
                <Badge tone={user.is_active ? 'gold' : 'muted'}>
                  {user.is_active ? 'Activo' : 'Inactivo'}
                </Badge>
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex justify-end gap-3">
                  {canWrite && (
                    <button onClick={() => onEdit(user)} className="text-text-muted hover:text-gold">
                      Editar
                    </button>
                  )}
                  {canDelete && user.is_active && (
                    <button
                      onClick={() => onDeactivate(user)}
                      className="text-text-muted hover:text-danger"
                    >
                      Desactivar
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
          {users.length === 0 && (
            <tr>
              <td colSpan={5} className="px-4 py-8 text-center text-text-muted">
                No hay usuarios para mostrar.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
