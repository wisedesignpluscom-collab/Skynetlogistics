export interface VehicleOwner {
  id: string
  company_id: string
  name: string
  tax_id: string | null
  contact_person: string | null
  phone: string | null
  email: string | null
  notes: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}
