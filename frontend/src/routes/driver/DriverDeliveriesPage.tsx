import { useCallback, useEffect, useState } from 'react'
import { DriverPortalLayout } from '../../layouts/DriverPortalLayout'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { deliverDeliveryOrder, failDeliveryOrder, listMyDeliveryOrders } from '../../features/delivery/api'
import { DELIVERY_ORDER_STATUS_LABELS } from '../../types/delivery'
import type { DeliveryOrder, DeliveryOrderStatus } from '../../types/delivery'

const statusTone: Record<DeliveryOrderStatus, 'muted' | 'warning' | 'success' | 'danger'> = {
  pendiente: 'warning',
  asignado: 'warning',
  en_ruta: 'warning',
  entregado: 'success',
  fallido: 'danger',
}

export function DriverDeliveriesPage() {
  const [orders, setOrders] = useState<DeliveryOrder[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  const reload = useCallback(() => {
    setIsLoading(true)
    void listMyDeliveryOrders()
      .then(setOrders)
      .finally(() => setIsLoading(false))
  }, [])

  useEffect(reload, [reload])

  async function handleDeliver(order: DeliveryOrder) {
    setBusyId(order.id)
    try {
      await deliverDeliveryOrder(order.id)
      reload()
    } finally {
      setBusyId(null)
    }
  }

  async function handleFail(order: DeliveryOrder) {
    const reason = window.prompt('Motivo del fallo de entrega:')
    if (!reason) return
    setBusyId(order.id)
    try {
      await failDeliveryOrder(order.id, reason, true)
      reload()
    } finally {
      setBusyId(null)
    }
  }

  const pending = orders.filter((o) => o.status === 'asignado' || o.status === 'en_ruta')

  return (
    <DriverPortalLayout title="Mis entregas">
      {isLoading ? (
        <p className="text-sm text-text-muted">Cargando…</p>
      ) : orders.length === 0 ? (
        <p className="text-sm text-text-muted">No tienes entregas asignadas.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {orders.map((order) => {
            const actionable = order.status === 'asignado' || order.status === 'en_ruta'
            return (
              <div key={order.id} className="rounded-md border border-border bg-surface p-4">
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-sm text-text">{order.address}</p>
                  <Badge tone={statusTone[order.status]}>{DELIVERY_ORDER_STATUS_LABELS[order.status]}</Badge>
                </div>
                <p className="text-xs text-text-muted">
                  {order.items.length} línea(s) de mercancía
                  {order.notes ? ` · ${order.notes}` : ''}
                </p>
                {order.failure_reason && (
                  <p className="mt-1 text-xs text-danger">Fallo: {order.failure_reason}</p>
                )}
                {actionable && (
                  <div className="mt-3 flex gap-2">
                    <Button onClick={() => void handleDeliver(order)} disabled={busyId === order.id}>
                      Marcar entregado
                    </Button>
                    <Button variant="secondary" onClick={() => void handleFail(order)} disabled={busyId === order.id}>
                      Fallo
                    </Button>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
      {pending.length === 0 && orders.length > 0 && (
        <p className="mt-4 text-sm text-text-muted">No hay entregas pendientes de acción.</p>
      )}
    </DriverPortalLayout>
  )
}
