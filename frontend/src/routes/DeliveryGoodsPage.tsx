import { useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Badge } from '../components/ui/Badge'
import { DeliveryGoodsFormModal } from '../components/delivery/DeliveryGoodsFormModal'
import { useDeliveryGoods } from '../features/delivery/hooks'
import { createDeliveryGoods } from '../features/delivery/api'
import { useWarehouses } from '../features/tires/hooks'
import { useAuth } from '../features/auth/AuthContext'

export function DeliveryGoodsPage() {
  const { hasPermission } = useAuth()
  const [search, setSearch] = useState('')
  const [lowStockOnly, setLowStockOnly] = useState(false)
  const { data, isLoading, error, reload } = useDeliveryGoods({
    search: search || undefined,
    low_stock: lowStockOnly || undefined,
    page_size: 50,
  })
  const { data: warehousesPage } = useWarehouses()
  const [showCreateModal, setShowCreateModal] = useState(false)

  const canWrite = hasPermission('delivery', 'write')

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Mercancía de reparto</h1>
        <div className="flex gap-3">
          {hasPermission('tires', 'read') && (
            <Link to="/warehouses">
              <Button variant="secondary">Almacenes</Button>
            </Link>
          )}
          {canWrite && <Button onClick={() => setShowCreateModal(true)}>Nueva mercancía</Button>}
        </div>
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <Input
          placeholder="Buscar por SKU o nombre…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <label className="flex items-center gap-2 text-sm text-text-muted">
          <input
            type="checkbox"
            checked={lowStockOnly}
            onChange={(e) => setLowStockOnly(e.target.checked)}
            className="rounded border-border"
          />
          Solo stock bajo
        </label>
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}
      {error && <p className="text-danger">{error}</p>}
      {data && (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface text-text-muted">
              <tr>
                <th className="px-4 py-2 font-medium">SKU</th>
                <th className="px-4 py-2 font-medium">Nombre</th>
                <th className="px-4 py-2 font-medium">Stock</th>
                <th className="px-4 py-2 font-medium">Peso/u</th>
                <th className="px-4 py-2 font-medium">Volumen/u</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.items.map((goods) => {
                const isLow = goods.quantity <= goods.min_stock
                return (
                  <tr key={goods.id} className="hover:bg-surface-hover">
                    <td className="px-4 py-2">
                      <Link to={`/delivery-goods/${goods.id}`} className="text-gold hover:underline">
                        {goods.sku}
                      </Link>
                    </td>
                    <td className="px-4 py-2 text-text">{goods.name}</td>
                    <td className="px-4 py-2">
                      <span className={isLow ? 'text-danger' : 'text-text-muted'}>
                        {goods.quantity} {goods.unit}
                      </span>{' '}
                      {isLow && <Badge tone="danger">stock bajo</Badge>}
                    </td>
                    <td className="px-4 py-2 text-text-muted">{goods.weight_kg_per_unit} kg</td>
                    <td className="px-4 py-2 text-text-muted">{goods.volume_m3_per_unit} m³</td>
                  </tr>
                )
              })}
              {data.items.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-text-muted">
                    No hay mercancía de reparto registrada.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {showCreateModal && (
        <DeliveryGoodsFormModal
          warehouses={warehousesPage?.items ?? []}
          onClose={() => setShowCreateModal(false)}
          onSubmit={async (values) => {
            await createDeliveryGoods(values)
            await reload()
          }}
        />
      )}
    </DashboardLayout>
  )
}
