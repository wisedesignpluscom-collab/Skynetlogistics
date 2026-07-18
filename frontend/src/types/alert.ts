export type AlertSeverity = 'baja' | 'media' | 'alta'
export type AlertStatus = 'no_leida' | 'leida'

export interface Alert {
  id: string
  company_id: string
  type: string
  entity_type: string
  entity_id: string
  message: string
  severity: AlertSeverity
  status: AlertStatus
  created_at: string
}
