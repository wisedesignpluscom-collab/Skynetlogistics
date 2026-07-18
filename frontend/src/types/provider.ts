export interface Provider {
  id: string
  company_id: string
  name: string
  type: string
  contact_info: Record<string, unknown>
  created_at: string
  updated_at: string
}
