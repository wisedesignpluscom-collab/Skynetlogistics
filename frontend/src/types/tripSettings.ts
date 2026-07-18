import type { VehicleType } from './vehicle'

export interface RateTable {
  id: string
  company_id: string
  origin: string
  destination: string
  vehicle_type: VehicleType
  cargo_type: string
  distance_km: number
  freight_amount: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface DriverPayRate {
  id: string
  company_id: string
  vehicle_type: VehicleType
  daily_base_rate: number
  meal_allowance_per_day: number
  holiday_bonus_rate: number
  return_bonus_rate: number
  created_at: string
  updated_at: string
}

export interface CompanyHoliday {
  id: string
  company_id: string
  date: string
  name: string
}

export interface ExpenseConcept {
  id: string
  company_id: string
  name: string
  default_limit: number | null
  is_active: boolean
  created_at: string
  updated_at: string
}
