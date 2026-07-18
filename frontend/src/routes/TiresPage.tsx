import { useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { TireTable } from '../components/tires/TireTable'
import { TireFormModal } from '../components/tires/TireFormModal'
import { TireBatchMovementModal } from '../components/tires/TireBatchMovementModal'
import { useTires, useWarehouses } from '../features/tires/hooks'
import { createTire, createTireMovementBatch } from '../features/tires/api'
import { useAuth } from '../features/auth/AuthContext'
import type { TireStatus } from '../types/tire'

export function TiresPage() {
  const { hasPermission } = useAuth()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<TireStatus | ''>('')
  const [brandFilter, setBrandFilter] = useState('')
  const { data, isLoading, error, reload } = useTires({
    search: search || undefined,
    status_filter: statusFilter || undefined,
    brand: brandFilter || undefined,
    page_size: 50,
  })
  const { data: warehousesPage } = useWarehouses()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showBatchModal, setShowBatchModal] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  const canWrite = hasPermission('tires', 'write')

  function toggleSelect(tireId: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(tireId)) next.delete(tireId)
      else next.add(tireId)
      return next
    })
  }

  const selectedTires = data?.items.filter((tire) => selectedIds.has(tire.id)) ?? []

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Neumáticos</h1>
        <div className="flex gap-3">
          {hasPermission('tires', 'read') && (
            <>
              <Link to="/warehouses">
                <Button variant="secondary">Almacenes</Button>
              </Link>
              <Link to="/tire-performance">
                <Button variant="secondary">Rendimiento</Button>
              </Link>
              <Link to="/tire-settings">
                <Button variant="secondary">Umbral de disparidad</Button>
              </Link>
            </>
          )}
          {canWrite && <Button onClick={() => setShowCreateModal(true)}>Nuevo neumático</Button>}
        </div>
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <Input
          placeholder="Buscar por código o marca…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <Input
          placeholder="Filtrar por marca…"
          value={brandFilter}
          onChange={(e) => setBrandFilter(e.target.value)}
          className="max-w-xs"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as TireStatus | '')}
          className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
        >
          <option value="">Todos los estados</option>
          <option value="instalado">Instalado</option>
          <option value="almacen">Almacén</option>
          <option value="reparacion">Reparación</option>
        </select>
        {canWrite && selectedIds.size > 0 && (
          <Button variant="secondary" onClick={() => setShowBatchModal(true)}>
            Movimiento en lote ({selectedIds.size})
          </Button>
        )}
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}
      {error && <p className="text-danger">{error}</p>}
      {data && <TireTable tires={data.items} selectedIds={selectedIds} onToggleSelect={toggleSelect} />}

      {showCreateModal && (
        <TireFormModal
          warehouses={warehousesPage?.items ?? []}
          onClose={() => setShowCreateModal(false)}
          onSubmit={async (values) => {
            await createTire(values)
            await reload()
          }}
        />
      )}

      {showBatchModal && (
        <TireBatchMovementModal
          tires={selectedTires}
          warehouses={warehousesPage?.items ?? []}
          onClose={() => setShowBatchModal(false)}
          onSubmit={async (payload) => {
            await createTireMovementBatch(payload)
            setSelectedIds(new Set())
            await reload()
          }}
        />
      )}
    </DashboardLayout>
  )
}
