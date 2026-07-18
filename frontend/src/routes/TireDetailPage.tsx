import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { TireMovementModal } from '../components/tires/TireMovementModal'
import { useTire, useWarehouses } from '../features/tires/hooks'
import { createTireMovement } from '../features/tires/api'
import { useAuth } from '../features/auth/AuthContext'
import type { TireMovementType } from '../types/tire'

const statusTone = {
  instalado: 'gold',
  almacen: 'muted',
  reparacion: 'danger',
} as const

const MOVEMENT_LABELS: Record<TireMovementType, string> = {
  instalacion: 'Instalación',
  desinstalacion: 'Desinstalación',
  envio_reparacion: 'Envío a reparación',
  envio_reencauche: 'Envío a reencauche',
  retorno_taller: 'Retorno de taller',
}

export function TireDetailPage() {
  const { tireId } = useParams<{ tireId: string }>()
  const { hasPermission } = useAuth()
  const { tire, isLoading, reload } = useTire(tireId)
  const { data: warehousesPage } = useWarehouses()
  const [showMovementModal, setShowMovementModal] = useState(false)

  const canWrite = hasPermission('tires', 'write')

  if (isLoading || !tire) {
    return (
      <DashboardLayout>
        <p className="text-text-muted">Cargando…</p>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <Link to="/tires" className="text-sm text-text-muted hover:text-gold">
        ← Volver a neumáticos
      </Link>

      <div className="mt-4 mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl text-text">{tire.unique_code}</h1>
          <p className="text-text-muted">
            {tire.brand} {tire.model} · {tire.current_thickness_mm}mm
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge tone={statusTone[tire.status]}>{tire.status}</Badge>
          {canWrite && <Button onClick={() => setShowMovementModal(true)}>Registrar movimiento</Button>}
        </div>
      </div>

      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-lg border border-border p-4">
          <p className="text-xs text-text-muted">Km período actual</p>
          <p className="font-display text-xl text-text">
            {tire.km_current_period !== null ? tire.km_current_period.toLocaleString() : '—'}
          </p>
        </div>
        <div className="rounded-lg border border-border p-4">
          <p className="text-xs text-text-muted">Km acumulados totales</p>
          <p className="font-display text-xl text-text">{tire.km_lifetime_total.toLocaleString()}</p>
        </div>
        <div className="rounded-lg border border-border p-4">
          <p className="text-xs text-text-muted">Posición actual</p>
          <p className="font-display text-xl text-text">
            {tire.status === 'instalado' ? `Eje ${tire.axle_number} · ${tire.axle_side}` : '—'}
          </p>
        </div>
        <div className="rounded-lg border border-border p-4">
          <p className="text-xs text-text-muted">Movimientos registrados</p>
          <p className="font-display text-xl text-text">{tire.movements.length}</p>
        </div>
      </div>

      <h2 className="mb-4 font-display text-lg text-text">Historial de movimientos</h2>
      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface text-text-muted">
            <tr>
              <th className="px-4 py-2 font-medium">Fecha</th>
              <th className="px-4 py-2 font-medium">Tipo</th>
              <th className="px-4 py-2 font-medium">Posición</th>
              <th className="px-4 py-2 font-medium">Km</th>
              <th className="px-4 py-2 font-medium">Espesor</th>
              <th className="px-4 py-2 font-medium">Notas</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {tire.movements.map((movement) => (
              <tr key={movement.id}>
                <td className="px-4 py-2 text-text-muted">{new Date(movement.created_at).toLocaleString()}</td>
                <td className="px-4 py-2 text-text">{MOVEMENT_LABELS[movement.movement_type]}</td>
                <td className="px-4 py-2 text-text-muted">
                  {movement.axle_number ? `Eje ${movement.axle_number} · ${movement.axle_side}` : '—'}
                </td>
                <td className="px-4 py-2 text-text-muted">
                  {movement.km_at_movement !== null ? movement.km_at_movement.toLocaleString() : '—'}
                </td>
                <td className="px-4 py-2 text-text-muted">
                  {movement.thickness_mm !== null ? `${movement.thickness_mm}mm` : '—'}
                </td>
                <td className="px-4 py-2 text-text-muted">{movement.notes ?? '—'}</td>
              </tr>
            ))}
            {tire.movements.length === 0 && (
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
        <TireMovementModal
          tire={tire}
          warehouses={warehousesPage?.items ?? []}
          onClose={() => setShowMovementModal(false)}
          onSubmit={async (payload) => {
            await createTireMovement(payload)
            await reload()
          }}
        />
      )}
    </DashboardLayout>
  )
}
