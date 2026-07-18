import { useEffect, useState } from 'react'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { AlertList } from '../components/alerts/AlertList'
import { listAlerts, markAlertRead, markAllAlertsRead } from '../features/alerts/api'
import { useAuth } from '../features/auth/AuthContext'
import type { Alert } from '../types/alert'

export function AlertsPage() {
  const { hasPermission } = useAuth()
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const canWrite = hasPermission('alerts', 'write')

  async function reload() {
    setIsLoading(true)
    const page = await listAlerts({ page_size: 50 })
    setAlerts(page.items)
    setIsLoading(false)
  }

  useEffect(() => {
    void reload()
  }, [])

  async function handleMarkRead(alert: Alert) {
    await markAlertRead(alert.id)
    await reload()
  }

  async function handleMarkAllRead() {
    await markAllAlertsRead()
    await reload()
  }

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Alertas</h1>
        {canWrite && alerts.some((a) => a.status === 'no_leida') && (
          <Button variant="secondary" onClick={handleMarkAllRead}>
            Marcar todas como leídas
          </Button>
        )}
      </div>

      {isLoading ? <p className="text-text-muted">Cargando…</p> : <AlertList alerts={alerts} onMarkRead={handleMarkRead} />}
    </DashboardLayout>
  )
}
