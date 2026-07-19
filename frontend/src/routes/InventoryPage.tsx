import { useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { InventoryTable } from '../components/inventory/InventoryTable'
import { InventoryItemFormModal } from '../components/inventory/InventoryItemFormModal'
import { useInventoryItems } from '../features/inventory/hooks'
import { useWarehouses } from '../features/tires/hooks'
import { createInventoryItem } from '../features/inventory/api'
import { useAuth } from '../features/auth/AuthContext'

export function InventoryPage() {
  const { hasPermission } = useAuth()
  const [search, setSearch] = useState('')
  const [lowStockOnly, setLowStockOnly] = useState(false)
  const { data, isLoading, error, reload } = useInventoryItems({
    search: search || undefined,
    low_stock: lowStockOnly || undefined,
    page_size: 50,
  })
  const { data: warehousesPage } = useWarehouses()
  const [showCreateModal, setShowCreateModal] = useState(false)

  const canWrite = hasPermission('inventory', 'write')

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Inventario</h1>
        <div className="flex gap-3">
          {hasPermission('tires', 'read') && (
            <Link to="/warehouses">
              <Button variant="secondary">Almacenes</Button>
            </Link>
          )}
          {canWrite && <Button onClick={() => setShowCreateModal(true)}>Nuevo ítem</Button>}
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
      {data && <InventoryTable items={data.items} />}

      {showCreateModal && (
        <InventoryItemFormModal
          warehouses={warehousesPage?.items ?? []}
          onClose={() => setShowCreateModal(false)}
          onSubmit={async (values) => {
            await createInventoryItem(values)
            await reload()
          }}
        />
      )}
    </DashboardLayout>
  )
}
