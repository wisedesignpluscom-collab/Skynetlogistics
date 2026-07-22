import type { VehicleOwner } from '../../types/vehicle_owner'
import { Badge } from '../ui/Badge'

interface VehicleOwnerTableProps {
  owners: VehicleOwner[]
  canWrite: boolean
  canDelete: boolean
  onEdit: (owner: VehicleOwner) => void
  onDeactivate: (owner: VehicleOwner) => void
}

export function VehicleOwnerTable({ owners, canWrite, canDelete, onEdit, onDeactivate }: VehicleOwnerTableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface text-text-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Nombre</th>
            <th className="px-4 py-3 font-medium">RIF / Tax ID</th>
            <th className="px-4 py-3 font-medium">Contacto</th>
            <th className="px-4 py-3 font-medium">Estado</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {owners.map((o) => (
            <tr key={o.id} className="bg-background/40">
              <td className="px-4 py-3">{o.name}</td>
              <td className="px-4 py-3 text-text-muted">{o.tax_id || '—'}</td>
              <td className="px-4 py-3 text-text-muted">
                {o.contact_person || '—'}
                {o.phone && <div className="text-xs">{o.phone}</div>}
              </td>
              <td className="px-4 py-3">
                <Badge tone={o.is_active ? 'gold' : 'muted'}>{o.is_active ? 'Activo' : 'Inactivo'}</Badge>
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex justify-end gap-3">
                  {canWrite && (
                    <button onClick={() => onEdit(o)} className="text-text-muted hover:text-gold">
                      Editar
                    </button>
                  )}
                  {canDelete && o.is_active && (
                    <button onClick={() => onDeactivate(o)} className="text-text-muted hover:text-danger">
                      Desactivar
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
          {owners.length === 0 && (
            <tr>
              <td colSpan={5} className="px-4 py-8 text-center text-text-muted">
                No hay propietarios para mostrar.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
