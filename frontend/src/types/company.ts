export interface Company {
  id: string
  name: string
  tax_id: string
  plan: string
  is_active: boolean
  contact_person: string | null
  phone: string | null
  mobile_phone: string | null
  email: string | null
  address: string | null
  city: string | null
  state: string | null
  country: string | null
  logo_url: string | null
  created_at: string
  updated_at: string
}
