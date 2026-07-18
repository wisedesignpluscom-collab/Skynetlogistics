export type Permissions = Record<string, string[]>

export interface Role {
  id: string
  company_id: string
  name: string
  permissions: Permissions
  is_system: boolean
  created_at: string
  updated_at: string
}
