import { api } from '../../lib/axios'
import type {
  MaintenanceSettings,
  MaintenanceTask,
  MaintenanceTaskWithRecords,
  ScheduledBy,
  MaintenanceType,
} from '../../types/maintenance'

export interface MaintenanceTaskPayload {
  vehicle_id: string
  type: MaintenanceType
  scheduled_by: ScheduledBy
  due_date?: string | null
  due_km?: number | null
  responsible_id?: string | null
  description?: string | null
  custom_data?: Record<string, unknown>
}

export interface CompleteTaskPayload {
  cost_labor: number
  cost_parts: number
  provider_id?: string | null
  notes?: string | null
}

export async function getVehicleMaintenanceHistory(
  vehicleId: string,
): Promise<MaintenanceTaskWithRecords[]> {
  const { data } = await api.get<MaintenanceTaskWithRecords[]>(`/vehicles/${vehicleId}/maintenance`)
  return data
}

export async function createMaintenanceTask(payload: MaintenanceTaskPayload): Promise<MaintenanceTask> {
  const { data } = await api.post<MaintenanceTask>('/maintenance-tasks', payload)
  return data
}

export async function completeMaintenanceTask(
  taskId: string,
  payload: CompleteTaskPayload,
): Promise<MaintenanceTask> {
  const { data } = await api.post<MaintenanceTask>(`/maintenance-tasks/${taskId}/complete`, payload)
  return data
}

export interface MaintenanceSettingsPayload {
  warning_days_threshold?: number
  warning_km_threshold?: number
}

export async function getMaintenanceSettings(): Promise<MaintenanceSettings> {
  const { data } = await api.get<MaintenanceSettings>('/maintenance-settings')
  return data
}

export async function updateMaintenanceSettings(
  payload: MaintenanceSettingsPayload,
): Promise<MaintenanceSettings> {
  const { data } = await api.patch<MaintenanceSettings>('/maintenance-settings', payload)
  return data
}
