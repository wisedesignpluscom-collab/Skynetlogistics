import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type { Alert, AlertStatus } from '../../types/alert'

export interface AlertListParams {
  page?: number
  page_size?: number
  status_filter?: AlertStatus
}

export async function listAlerts(params: AlertListParams = {}): Promise<Page<Alert>> {
  const { data } = await api.get<Page<Alert>>('/alerts', { params })
  return data
}

export async function getUnreadAlertCount(): Promise<number> {
  const { data } = await api.get<{ count: number }>('/alerts/unread-count')
  return data.count
}

export async function markAlertRead(id: string): Promise<Alert> {
  const { data } = await api.patch<Alert>(`/alerts/${id}/read`)
  return data
}

export async function markAllAlertsRead(): Promise<void> {
  await api.patch('/alerts/read-all')
}
