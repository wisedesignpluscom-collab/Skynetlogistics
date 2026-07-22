export type DriverStatus = 'activo' | 'suspendido' | 'inactivo'
export type PayPeriod = 'semanal' | 'quincenal' | 'mensual'

export interface Driver {
  id: string
  company_id: string
  name: string
  license_number: string
  license_expiry: string
  phone: string | null
  status: DriverStatus
  birth_date: string | null
  address: string | null
  city: string | null
  state: string | null
  country: string | null
  email: string | null
  secondary_phone: string | null
  notes: string | null
  base_salary: number | null
  pay_period: PayPeriod | null
  hire_date: string | null
  termination_date: string | null
  custom_data?: Record<string, unknown>
  created_at: string
  updated_at: string
}
