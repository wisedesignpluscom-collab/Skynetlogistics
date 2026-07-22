import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { DeliveryGoodsMovementModal } from '../components/delivery/DeliveryGoodsMovementModal'
import { useDeliveryGoodsDetail } from '../features/delivery/hooks'
import { createDeliveryGoodsMovement } from '../features/delivery/api'
import { useAuth } from '../features/auth/AuthContext'
import type { DeliveryGoodsMovementType } from '../types/delivery'

const MOVEMENT_LABELS: Record<DeliveryGoodsMovementType, string> = {
  entrada: 'Entrada',
  salida: 'Salida',
  ajuste: 'Ajuste',
}

export function DeliveryGoodsDetailPage() {
  const { goodsId } = useParams<{ goodsId: string }>()
  const { hasPermission } = useAuth()
  const { goods, isLoading, reload } = useDeliveryGoodsDetail(goodsId)
  const [showMovementModal, setShowMovementModal] = useState(false)

  const canWrite = hasPermission('delivery', 'write')

  if (isLoading || !goods) {
    return (
      <DashboardLayout>
        <p className="text-text-muted">Cargando…</p>
      </DashboardLayout>
    )
  }

  const isLow = goods.quantity <= goods.min_stock

  return (
    <DashboardLayout>
      <Link to="/delivery-goods" className="text-sm text-text-muted hover:text-gold">
        ← Volver a mercancía de reparto
      </Link>

      <div className="mt-4 mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl text-text">{goods.name}</h1>
          <p className="text-text-muted">
            SKU {goods.sku} · ${goods.unit_cost} por {goods.unit}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {isLow && <Badge tone="danger">stock bajo</Badge>}
          {canWrite && <Button onClick={() => setShowMovementModal(true)}>Registrar movimiento</Button>}
        </div>
      </div>

      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-lg border border-border p-4">
          <p className="text-xs text-text-muted">Stock actual</p>
          <p className={`font-display text-xl ${isLow ? 'text-danger' : 'text-text'}`}>
            {goods.quantity} {goods.unit}
          </p>
        </div>
        <div className="rounded-lg border border-border p-4">
          <p className="text-xs text-text-muted">Stock mínimo</p>
          <p className="font-display text-xl text-text">
            {goods.min_stock} {goods.unit}
          </p>
        </div>
        <div className="rounded-lg border border-border p-4">
          <p className="text-xs text-text-muted">Peso / unidad</p>
          <p className="font-display text-xl text-text">{goods.weight_kg_per_unit} kg</p>
        </div>
        <div className="rounded-lg border border-border p-4">
          <p className="text-xs text-text-muted">Volumen / unidad</p>
          <p className="font-display text-xl text-text">{goods.volume_m3_per_unit} m³</p>
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
              <th className="px-4 py-2 font-medium">Costo unit.</th>
              <th className="px-4 py-2 font-medium">Documento</th>
              <th className="px-4 py-2 font-medium">Notas</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {goods.movements.map((movement) => (
              <tr key={movement.id}>
                <td className="px-4 py-2 text-text-muted">{new Date(movement.created_at).toLocaleString()}</td>
                <td className="px-4 py-2 text-text">{MOVEMENT_LABELS[movement.movement_type]}</td>
                <td className="px-4 py-2 text-text-muted">
                  {movement.movement_type === 'salida' ? '-' : movement.movement_type === 'ajuste' && movement.quantity < 0 ? '' : '+'}
                  {movement.quantity} {goods.unit}
                </td>
                <td className="px-4 py-2 text-text-muted">{movement.unit_cost != null ? `$${movement.unit_cost}` : '—'}</td>
                <td className="px-4 py-2 text-text-muted">{movement.reference_doc ?? '—'}</td>
                <td className="px-4 py-2 text-text-muted">{movement.notes ?? '—'}</td>
              </tr>
            ))}
            {goods.movements.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-text-muted">
                  Sin movimientos registrados todavía.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showMovementModal && (
        <DeliveryGoodsMovementModal
          goods={goods}
          onClose={() => setShowMovementModal(false)}
          onSubmit={async (payload) => {
            await createDeliveryGoodsMovement(payload)
            await reload()
          }}
        />
      )}
    </DashboardLayout>
  )
}
