import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { InventoryMovementModal } from '../components/inventory/InventoryMovementModal'
import { useInventoryItem } from '../features/inventory/hooks'
import { createInventoryMovement } from '../features/inventory/api'
import { useAuth } from '../features/auth/AuthContext'
import type { InventoryMovementType } from '../types/inventory'

const MOVEMENT_LABELS: Record<InventoryMovementType, string> = {
  entrada: 'Entrada',
  salida: 'Salida',
  ajuste: 'Ajuste',
}

export function InventoryItemDetailPage() {
  const { itemId } = useParams<{ itemId: string }>()
  const { hasPermission } = useAuth()
  const { item, isLoading, reload } = useInventoryItem(itemId)
  const [showMovementModal, setShowMovementModal] = useState(false)

  const canWrite = hasPermission('inventory', 'write')

  if (isLoading || !item) {
    return (
      <DashboardLayout>
        <p className="text-text-muted">Cargando…</p>
      </DashboardLayout>
    )
  }

  const isLow = item.quantity <= item.min_stock

  return (
    <DashboardLayout>
      <Link to="/inventory" className="text-sm text-text-muted hover:text-gold">
        ← Volver a inventario
      </Link>

      <div className="mt-4 mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl text-text">{item.name}</h1>
          <p className="text-text-muted">
            SKU {item.sku} · ${item.unit_cost} por {item.unit}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {isLow && <Badge tone="danger">stock bajo</Badge>}
          {canWrite && <Button onClick={() => setShowMovementModal(true)}>Registrar movimiento</Button>}
        </div>
      </div>

      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-border p-4">
          <p className="text-xs text-text-muted">Stock actual</p>
          <p className={`font-display text-xl ${isLow ? 'text-danger' : 'text-text'}`}>
            {item.quantity} {item.unit}
          </p>
        </div>
        <div className="rounded-lg border border-border p-4">
          <p className="text-xs text-text-muted">Stock mínimo</p>
          <p className="font-display text-xl text-text">
            {item.min_stock} {item.unit}
          </p>
        </div>
        <div className="rounded-lg border border-border p-4">
          <p className="text-xs text-text-muted">Movimientos registrados</p>
          <p className="font-display text-xl text-text">{item.movements.length}</p>
        </div>
      </div>

      <h2 className="mb-4 font-display text-lg text-text">Historial de movimientos</h2>
      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface text-text-muted">
            <tr>
              <th className="px-4 py-2 font-medium">Fecha</th>
              <th className="px-4 py-2 font-medium">Tipo</th>
              <th className="px-4 py-2 font-medium">Cantidad</th>
              <th className="px-4 py-2 font-medium">Documento</th>
              <th className="px-4 py-2 font-medium">Notas</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {item.movements.map((movement) => (
              <tr key={movement.id}>
                <td className="px-4 py-2 text-text-muted">{new Date(movement.created_at).toLocaleString()}</td>
                <td className="px-4 py-2 text-text">{MOVEMENT_LABELS[movement.movement_type]}</td>
                <td className="px-4 py-2 text-text-muted">
                  {movement.movement_type === 'salida' ? '-' : movement.movement_type === 'ajuste' && movement.quantity < 0 ? '' : '+'}
                  {movement.quantity} {item.unit}
                </td>
                <td className="px-4 py-2 text-text-muted">{movement.reference_doc ?? '—'}</td>
                <td className="px-4 py-2 text-text-muted">{movement.notes ?? '—'}</td>
              </tr>
            ))}
            {item.movements.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-text-muted">
                  Sin movimientos registrados todavía.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showMovementModal && (
        <InventoryMovementModal
          item={item}
          onClose={() => setShowMovementModal(false)}
          onSubmit={async (payload) => {
            await createInventoryMovement(payload)
            await reload()
          }}
        />
      )}
    </DashboardLayout>
  )
}
