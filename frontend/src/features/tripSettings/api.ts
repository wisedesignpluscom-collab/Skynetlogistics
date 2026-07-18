import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type {
  CompanyHoliday,
  DriverPayRate,
  ExpenseConcept,
  RateTable,
} from '../../types/tripSettings'
import type { VehicleType } from '../../types/vehicle'

// Tabulados de flete
export interface RateTablePayload {
  origin: string
  destination: string
  vehicle_type: VehicleType
  cargo_type: string
  distance_km: number
  freight_amount: number
}

export async function listRateTables(): Promise<Page<RateTable>> {
  const { data } = await api.get<Page<RateTable>>('/rate-tables', { params: { page_size: 100 } })
  return data
}

export async function createRateTable(payload: RateTablePayload): Promise<RateTable> {
  const { data } = await api.post<RateTable>('/rate-tables', payload)
  return data
}

export async function deleteRateTable(id: string): Promise<void> {
  await api.delete(`/rate-tables/${id}`)
}

// Tabulados de pago a conductores
export interface DriverPayRatePayload {
  vehicle_type: VehicleType
  daily_base_rate: number
  meal_allowance_per_day: number
  holiday_bonus_rate: number
  return_bonus_rate: number
}

export async function listDriverPayRates(): Promise<DriverPayRate[]> {
  const { data } = await api.get<DriverPayRate[]>('/driver-pay-rates')
  return data
}

export async function createDriverPayRate(payload: DriverPayRatePayload): Promise<DriverPayRate> {
  const { data } = await api.post<DriverPayRate>('/driver-pay-rates', payload)
  return data
}

export async function deleteDriverPayRate(id: string): Promise<void> {
  await api.delete(`/driver-pay-rates/${id}`)
}

// Feriados
export async function listHolidays(): Promise<CompanyHoliday[]> {
  const { data } = await api.get<CompanyHoliday[]>('/holidays')
  return data
}

export async function createHoliday(payload: { date: string; name: string }): Promise<CompanyHoliday> {
  const { data } = await api.post<CompanyHoliday>('/holidays', payload)
  return data
}

export async function deleteHoliday(id: string): Promise<void> {
  await api.delete(`/holidays/${id}`)
}

// Conceptos de gasto
export async function listExpenseConcepts(): Promise<Page<ExpenseConcept>> {
  const { data } = await api.get<Page<ExpenseConcept>>('/expense-concepts', { params: { page_size: 100 } })
  return data
}

export async function createExpenseConcept(payload: {
  name: string
  default_limit?: number | null
}): Promise<ExpenseConcept> {
  const { data } = await api.post<ExpenseConcept>('/expense-concepts', payload)
  return data
}

export async function deleteExpenseConcept(id: string): Promise<void> {
  await api.delete(`/expense-concepts/${id}`)
}
