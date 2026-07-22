export interface Client {
  id: string
  company_id: string
  name: string
  tax_id: string | null
  contact_person: string | null
  address: string | null
  phone: string | null
  email: string | null
  default_cargo_type: string | null
  is_active: boolean
  custom_data?: Record<string, unknown>
  created_at: string
  updated_at: string
}
