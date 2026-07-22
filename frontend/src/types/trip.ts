export type TripStatus = 'planificado' | 'en_curso' | 'completado' | 'cancelado'

export interface Trip {
  id: string
  company_id: string
  vehicle_id: string
  driver_id: string
  trailer_id: string | null
  client_id: string | null
  origin: string
  destination: string
  distance_km: number | null
  cargo_type: string
  is_round_trip: boolean
  status: TripStatus
  start_odometer_km: number | null
  end_odometer_km: number | null
  freight_cost: number | null
  advance_payment: number
  started_at: string | null
  ended_at: string | null
  custom_data?: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface TripExpense {
  id: string
  trip_id: string
  concept_id: string
  amount: number
  notes: string | null
  recorded_by: string | null
  created_at: string
}

export interface TripPayroll {
  id: string
  trip_id: string
  base_salary: number
  meal_allowance: number
  holiday_bonus: number
  return_bonus: number
  bonuses: number
  advance_payment: number
  total_to_pay: number
  created_at: string
  updated_at: string
}

export interface TripWithDetails extends Trip {
  expenses: TripExpense[]
  payroll: TripPayroll | null
}

export interface TripClosePreview {
  trip_days: number
  base_salary: number
  meal_allowance: number
  holiday_bonus: number
  holiday_count: number
  return_bonus: number
  bonuses: number
  advance_payment: number
  total_to_pay: number
  freight_cost: number | null
  missing_pay_rate: boolean
}
