export type MaintenanceType = 'preventivo' | 'correctivo'
export type ScheduledBy = 'tiempo' | 'km'
export type MaintenanceTaskStatus = 'pendiente' | 'en_proceso' | 'completada' | 'vencida' | 'cancelada'
export type TrafficLight = 'verde' | 'amarillo' | 'rojo'

export interface MaintenanceTask {
  id: string
  company_id: string
  vehicle_id: string
  type: MaintenanceType
  scheduled_by: ScheduledBy
  due_date: string | null
  due_km: number | null
  status: MaintenanceTaskStatus
  responsible_id: string | null
  description: string | null
  custom_data?: Record<string, unknown>
  created_at: string
  updated_at: string
  traffic_light: TrafficLight | null
}

export interface MaintenanceSettings {
  id: string
  company_id: string
  warning_days_threshold: number
  warning_km_threshold: number
  created_at: string
  updated_at: string
}

export interface MaintenanceRecord {
  id: string
  task_id: string
  cost_labor: number
  cost_parts: number
  provider_id: string | null
  completed_at: string
  notes: string | null
  created_at: string
}

export interface MaintenanceTaskWithRecords extends MaintenanceTask {
  records: MaintenanceRecord[]
}
