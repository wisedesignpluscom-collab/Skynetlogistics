import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type { Client } from '../../types/client'

export interface ClientListParams {
  page?: number
  page_size?: number
  search?: string
}

export interface ClientPayload {
  name: string
  tax_id?: string | null
  contact_person?: string | null
  address?: string | null
  phone?: string | null
  email?: string | null
  default_cargo_type?: string | null
  custom_data?: Record<string, unknown>
}

export interface ClientUpdatePayload extends Partial<ClientPayload> {
  is_active?: boolean
}

export async function listClients(params: ClientListParams = {}): Promise<Page<Client>> {
  const { data } = await api.get<Page<Client>>('/clients', { params })
  return data
}

export async function createClient(payload: ClientPayload): Promise<Client> {
  const { data } = await api.post<Client>('/clients', payload)
  return data
}

export async function updateClient(id: string, payload: ClientUpdatePayload): Promise<Client> {
  const { data } = await api.patch<Client>(`/clients/${id}`, payload)
  return data
}

export async function deactivateClient(id: string): Promise<void> {
  await api.delete(`/clients/${id}`)
}
