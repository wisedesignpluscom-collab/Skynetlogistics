import type { Client } from '../../types/client'
import { Badge } from '../ui/Badge'

interface ClientTableProps {
  clients: Client[]
  canWrite: boolean
  canDelete: boolean
  onEdit: (client: Client) => void
  onDeactivate: (client: Client) => void
}

export function ClientTable({ clients, canWrite, canDelete, onEdit, onDeactivate }: ClientTableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface text-text-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Nombre</th>
            <th className="px-4 py-3 font-medium">RIF / Tax ID</th>
            <th className="px-4 py-3 font-medium">Contacto</th>
            <th className="px-4 py-3 font-medium">Carga predeterminada</th>
            <th className="px-4 py-3 font-medium">Estado</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {clients.map((c) => (
            <tr key={c.id} className="bg-background/40">
              <td className="px-4 py-3">{c.name}</td>
              <td className="px-4 py-3 text-text-muted">{c.tax_id || '—'}</td>
              <td className="px-4 py-3 text-text-muted">
                {c.contact_person || '—'}
                {c.phone && <div className="text-xs">{c.phone}</div>}
              </td>
              <td className="px-4 py-3 text-text-muted">{c.default_cargo_type || '—'}</td>
              <td className="px-4 py-3">
                <Badge tone={c.is_active ? 'gold' : 'muted'}>{c.is_active ? 'Activo' : 'Inactivo'}</Badge>
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex justify-end gap-3">
                  {canWrite && (
                    <button onClick={() => onEdit(c)} className="text-text-muted hover:text-gold">
                      Editar
                    </button>
                  )}
                  {canDelete && c.is_active && (
                    <button onClick={() => onDeactivate(c)} className="text-text-muted hover:text-danger">
                      Desactivar
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
          {clients.length === 0 && (
            <tr>
              <td colSpan={6} className="px-4 py-8 text-center text-text-muted">
                No hay clientes para mostrar.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
