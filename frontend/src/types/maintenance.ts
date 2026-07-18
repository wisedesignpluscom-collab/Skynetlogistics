export type MaintenanceType = 'preventivo' | 'correctivo'
export type ScheduledBy = 'tiempo' | 'km'
export type MaintenanceTaskStatus = 'pendiente' | 'en_proceso' | 'completada' | 'vencida' | 'cancelada'

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
