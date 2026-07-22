export interface DriverDocumentType {
  id: string
  company_id: string
  name: string
  alert_days_before: number
  created_at: string
  updated_at: string
}

export interface DriverDocument {
  id: string
  company_id: string
  driver_id: string
  document_type_id: string
  number: string | null
  expiry_date: string | null
  notes: string | null
  created_at: string
  updated_at: string
  document_type: DriverDocumentType
}
