import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { DeliveryOrderFormModal } from '../components/delivery/DeliveryOrderFormModal'
import { AssignOrderModal } from '../components/delivery/AssignOrderModal'
import {
  assignDeliveryOrder,
  createDeliveryOrder,
  listDeliveryGoods,
  listDeliveryOrders,
} from '../features/delivery/api'
import { useClients } from '../features/clients/hooks'
import { useAuth } from '../features/auth/AuthContext'
import { DELIVERY_ORDER_STATUS_LABELS } from '../types/delivery'
import type { DeliveryGoods, DeliveryOrder, DeliveryOrderStatus } from '../types/delivery'

const statusTone: Record<DeliveryOrderStatus, 'muted' | 'warning' | 'success' | 'danger'> = {
  pendiente: 'warning',
  asignado: 'muted',
  en_ruta: 'muted',
  entregado: 'success',
  fallido: 'danger',
}

export function DeliveryOrdersPage() {
  const { hasPermission } = useAuth()
  const [statusFilter, setStatusFilter] = useState<DeliveryOrderStatus | ''>('')
  const [orders, setOrders] = useState<DeliveryOrder[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [assignFor, setAssignFor] = useState<string | null>(null)
  const [goods, setGoods] = useState<DeliveryGoods[]>([])

  const { data: clientsPage } = useClients({ page_size: 100 })

  const canWrite = hasPermission('delivery', 'write')

  const reload = useCallback(async () => {
    setIsLoading(true)
    const page = await listDeliveryOrders({
      status_filter: statusFilter || undefined,
      page_size: 100,
    })
    setOrders(page.items)
    setIsLoading(false)
  }, [statusFilter])

  useEffect(() => {
    void reload()
  }, [reload])

  useEffect(() => {
    void listDeliveryGoods({ page_size: 200 }).then((p) => setGoods(p.items))
  }, [])

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Pedidos de reparto</h1>
        <div className="flex gap-3">
          <Link to="/delivery-goods">
            <Button variant="secondary">Catálogo de mercancía</Button>
          </Link>
          {canWrite && <Button onClick={() => setShowCreate(true)}>Nuevo pedido</Button>}
        </div>
      </div>

      <div className="mb-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as DeliveryOrderStatus | '')}
          className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
        >
          <option value="">Todos los estados</option>
          {Object.entries(DELIVERY_ORDER_STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <p className="text-text-muted">Cargando…</p>
      ) : orders.length === 0 ? (
        <p className="text-text-muted">No hay pedidos de reparto.</p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface text-text-muted">
              <tr>
                <th className="px-4 py-2 font-medium">Dirección</th>
                <th className="px-4 py-2 font-medium">Líneas</th>
                <th className="px-4 py-2 font-medium">Estado</th>
                <th className="px-4 py-2 font-medium">Creado</th>
                <th className="px-4 py-2 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {orders.map((order) => (
                <tr key={order.id} className="hover:bg-surface-hover">
                  <td className="px-4 py-2 text-text">{order.address}</td>
                  <td className="px-4 py-2 text-text-muted">{order.items.length}</td>
                  <td className="px-4 py-2">
                    <Badge tone={statusTone[order.status]}>{DELIVERY_ORDER_STATUS_LABELS[order.status]}</Badge>
                  </td>
                  <td className="px-4 py-2 text-text-muted">{new Date(order.created_at).toLocaleString()}</td>
                  <td className="px-4 py-2 text-right">
                    {canWrite && order.status === 'pendiente' && (
                      <button onClick={() => setAssignFor(order.id)} className="text-sm text-gold hover:underline">
                        Asignar a viaje
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showCreate && (
        <DeliveryOrderFormModal
          clients={clientsPage?.items ?? []}
          goods={goods}
          onClose={() => setShowCreate(false)}
          onSubmit={async (values) => {
            await createDeliveryOrder(values)
            await reload()
          }}
        />
      )}

      {assignFor && (
        <AssignOrderModal
          onClose={() => setAssignFor(null)}
          onAssign={async (tripId) => {
            await assignDeliveryOrder(assignFor, tripId)
            await reload()
          }}
        />
      )}
    </DashboardLayout>
  )
}
