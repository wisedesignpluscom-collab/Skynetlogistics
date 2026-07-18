import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type { UserWithRole } from '../../types/user'

export interface UserListParams {
  page?: number
  page_size?: number
  search?: string
  role_id?: string
  is_active?: boolean
}

export interface CreateUserPayload {
  name: string
  email: string
  password: string
  role_id: string
}

export interface UpdateUserPayload {
  name?: string
  role_id?: string
  is_active?: boolean
}

export async function listUsers(params: UserListParams = {}): Promise<Page<UserWithRole>> {
  const { data } = await api.get<Page<UserWithRole>>('/users', { params })
  return data
}

export async function createUser(payload: CreateUserPayload): Promise<UserWithRole> {
  const { data } = await api.post<UserWithRole>('/users', payload)
  return data
}

export async function updateUser(id: string, payload: UpdateUserPayload): Promise<UserWithRole> {
  const { data } = await api.patch<UserWithRole>(`/users/${id}`, payload)
  return data
}

export async function deactivateUser(id: string): Promise<void> {
  await api.delete(`/users/${id}`)
}
