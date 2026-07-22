import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type { Company } from '../../types/company'

export interface CompanyListParams {
  page?: number
  page_size?: number
  search?: string
}

export interface CompanyPayload {
  name: string
  tax_id: string
  plan?: string
  contact_person?: string | null
  phone?: string | null
  mobile_phone?: string | null
  email?: string | null
  address?: string | null
  city?: string | null
  state?: string | null
  country?: string | null
  logo_url?: string | null
}

export interface CompanyUpdatePayload extends Partial<CompanyPayload> {
  is_active?: boolean
}

export async function listCompanies(params: CompanyListParams = {}): Promise<Page<Company>> {
  const { data } = await api.get<Page<Company>>('/companies', { params })
  return data
}

export async function createCompany(payload: CompanyPayload): Promise<Company> {
  const { data } = await api.post<Company>('/companies', payload)
  return data
}

export async function updateCompany(id: string, payload: CompanyUpdatePayload): Promise<Company> {
  const { data } = await api.patch<Company>(`/companies/${id}`, payload)
  return data
}

export async function deactivateCompany(id: string): Promise<void> {
  await api.delete(`/companies/${id}`)
}
