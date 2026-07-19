import { Link } from 'react-router-dom'
import { Badge } from '../ui/Badge'
import type { InventoryItem } from '../../types/inventory'

interface InventoryTableProps {
  items: InventoryItem[]
}

export function InventoryTable({ items }: InventoryTableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface text-text-muted">
          <tr>
            <th className="px-4 py-3 font-medium">SKU</th>
            <th className="px-4 py-3 font-medium">Nombre</th>
            <th className="px-4 py-3 font-medium">Stock</th>
            <th className="px-4 py-3 font-medium">Mínimo</th>
            <th className="px-4 py-3 font-medium">Costo unitario</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {items.map((item) => {
            const isLow = item.quantity <= item.min_stock
            return (
              <tr key={item.id} className="bg-background/40">
                <td className="px-4 py-3">
                  <Link to={`/inventory/${item.id}`} className="text-gold hover:underline">
                    {item.sku}
                  </Link>
                </td>
                <td className="px-4 py-3 text-text">{item.name}</td>
                <td className="px-4 py-3">
                  <span className={`mr-2 ${isLow ? 'text-danger' : 'text-text'}`}>
                    {item.quantity} {item.unit}
                  </span>
                  {isLow && <Badge tone="danger">bajo</Badge>}
                </td>
                <td className="px-4 py-3 text-text-muted">
                  {item.min_stock} {item.unit}
                </td>
                <td className="px-4 py-3 text-text-muted">${item.unit_cost}</td>
                <td className="px-4 py-3" />
              </tr>
            )
          })}
          {items.length === 0 && (
            <tr>
              <td colSpan={6} className="px-4 py-8 text-center text-text-muted">
                No hay ítems de inventario para mostrar.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
