import type { Role } from './role'

export interface User {
  id: string
  company_id: string
  role_id: string
  name: string
  email: string
  is_active: boolean
  is_superadmin: boolean
  last_login_at: string | null
  created_at: string
  updated_at: string
}

export interface UserWithRole extends User {
  role: Role
}
