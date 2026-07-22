export type IncidentType =
  | 'accidente'
  | 'siniestro'
  | 'averia_mecanica'
  | 'falta_viaticos'
  | 'multa'
  | 'retraso_via'
  | 'pernocte'
  | 'mercancia_danada'
  | 'retencion_aduana'
  | 'emergencia_salud'
  | 'otro'

export type IncidentSeverity = 'baja' | 'media' | 'alta' | 'critica'
export type IncidentStatus = 'reportado' | 'en_atencion' | 'resuelto'

export const INCIDENT_TYPE_LABELS: Record<IncidentType, string> = {
  accidente: 'Accidente',
  siniestro: 'Siniestro',
  averia_mecanica: 'Avería mecánica',
  falta_viaticos: 'Falta de viáticos',
  multa: 'Multa',
  retraso_via: 'Retraso en vía',
  pernocte: 'Pernocte no planificado',
  mercancia_danada: 'Mercancía dañada',
  retencion_aduana: 'Retención en aduana/control',
  emergencia_salud: 'Emergencia de salud',
  otro: 'Otro',
}

export const INCIDENT_SEVERITY_LABELS: Record<IncidentSeverity, string> = {
  baja: 'Baja',
  media: 'Media',
  alta: 'Alta',
  critica: 'Crítica',
}

export const INCIDENT_STATUS_LABELS: Record<IncidentStatus, string> = {
  reportado: 'Reportado',
  en_atencion: 'En atención',
  resuelto: 'Resuelto',
}

export interface IncidentReport {
  id: string
  company_id: string
  driver_id: string
  vehicle_id: string | null
  trip_id: string | null
  type: IncidentType
  severity: IncidentSeverity
  status: IncidentStatus
  description: string
  lat: number | null
  lng: number | null
  resolved_at: string | null
  resolved_by: string | null
  resolution_notes: string | null
  created_at: string
  updated_at: string
}

export interface IncidentReportAttachment {
  id: string
  incident_report_id: string
  file_url: string
  uploaded_by: string | null
  created_at: string
}

export interface IncidentReportCreatePayload {
  vehicle_id?: string | null
  trip_id?: string | null
  type: IncidentType
  severity: IncidentSeverity
  description: string
  lat?: number | null
  lng?: number | null
}
