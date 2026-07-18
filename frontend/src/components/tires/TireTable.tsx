import { Link } from 'react-router-dom'
import { Badge } from '../ui/Badge'
import type { Tire } from '../../types/tire'

interface TireTableProps {
  tires: Tire[]
  selectedIds: Set<string>
  onToggleSelect: (tireId: string) => void
}

const statusTone = {
  instalado: 'gold',
  almacen: 'muted',
  reparacion: 'danger',
} as const

export function TireTable({ tires, selectedIds, onToggleSelect }: TireTableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface text-text-muted">
          <tr>
            <th className="px-4 py-3" />
            <th className="px-4 py-3 font-medium">Código</th>
            <th className="px-4 py-3 font-medium">Marca / Modelo</th>
            <th className="px-4 py-3 font-medium">Espesor</th>
            <th className="px-4 py-3 font-medium">Estado</th>
            <th className="px-4 py-3 font-medium">Posición</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {tires.map((tire) => (
            <tr key={tire.id} className="bg-background/40">
              <td className="px-4 py-3">
                <input
                  type="checkbox"
                  checked={selectedIds.has(tire.id)}
                  onChange={() => onToggleSelect(tire.id)}
                  className="accent-gold"
                />
              </td>
              <td className="px-4 py-3">
                <Link to={`/tires/${tire.id}`} className="text-gold hover:underline">
                  {tire.unique_code}
                </Link>
              </td>
              <td className="px-4 py-3 text-text-muted">
                {tire.brand} {tire.model}
              </td>
              <td className="px-4 py-3 text-text-muted">{tire.current_thickness_mm}mm</td>
              <td className="px-4 py-3">
                <Badge tone={statusTone[tire.status]}>{tire.status}</Badge>
              </td>
              <td className="px-4 py-3 text-text-muted">
                {tire.status === 'instalado'
                  ? `Eje ${tire.axle_number} · ${tire.axle_side} · ${tire.axle_dual_position}`
                  : '—'}
              </td>
            </tr>
          ))}
          {tires.length === 0 && (
            <tr>
              <td colSpan={6} className="px-4 py-8 text-center text-text-muted">
                No hay neumáticos para mostrar.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
