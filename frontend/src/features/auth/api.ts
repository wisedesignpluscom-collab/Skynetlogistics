import { api } from '../../lib/axios'
import type { UserWithRole } from '../../types/user'
import type { Permissions } from '../../types/role'

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: UserWithRole
  driver_id: string | null
}

export interface MeResponse {
  user: UserWithRole
  permissions: Permissions
  driver_id: string | null
}

export async function loginRequest(email: string, password: string): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/auth/login', { email, password })
  return data
}

export async function meRequest(): Promise<MeResponse> {
  const { data } = await api.get<MeResponse>('/auth/me')
  return data
}

export async function logoutRequest(refreshToken: string): Promise<void> {
  await api.post('/auth/logout', { refresh_token: refreshToken })
}
