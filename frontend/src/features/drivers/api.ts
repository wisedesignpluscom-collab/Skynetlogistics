import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type { Driver, DriverStatus, PayPeriod } from '../../types/driver'

export interface DriverListParams {
  page?: number
  page_size?: number
  search?: string
  status_filter?: DriverStatus
}

export interface DriverPayload {
  name: string
  license_number: string
  license_expiry: string
  phone?: string | null
  birth_date?: string | null
  address?: string | null
  city?: string | null
  state?: string | null
  country?: string | null
  email?: string | null
  secondary_phone?: string | null
  notes?: string | null
  base_salary?: number | null
  pay_period?: PayPeriod | null
  hire_date?: string | null
  termination_date?: string | null
  custom_data?: Record<string, unknown>
}

export interface DriverUpdatePayload extends Partial<DriverPayload> {
  status?: DriverStatus
}

export async function listDrivers(params: DriverListParams = {}): Promise<Page<Driver>> {
  const { data } = await api.get<Page<Driver>>('/drivers', { params })
  return data
}

export async function getDriver(id: string): Promise<Driver> {
  const { data } = await api.get<Driver>(`/drivers/${id}`)
  return data
}

export async function createDriver(payload: DriverPayload): Promise<Driver> {
  const { data } = await api.post<Driver>('/drivers', payload)
  return data
}

export async function updateDriver(id: string, payload: DriverUpdatePayload): Promise<Driver> {
  const { data } = await api.patch<Driver>(`/drivers/${id}`, payload)
  return data
}

export async function deactivateDriver(id: string): Promise<void> {
  await api.delete(`/drivers/${id}`)
}
