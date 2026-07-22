export type VehicleType = 'camion' | 'remolque' | 'cabezal'
export type VehicleStatus = 'activo' | 'taller' | 'inactivo'

export interface Vehicle {
  id: string
  company_id: string
  plate: string
  brand: string
  model: string
  year: number
  vin: string | null
  type: VehicleType
  status: VehicleStatus
  current_odometer_km: number
  assigned_driver_id: string | null
  owner_id: string | null
  color: string | null
  engine_serial: string | null
  has_odometer: boolean
  odometer_digits: number | null
  cargo_capacity_kg: number | null
  cargo_capacity_m3: number | null
  custom_data?: Record<string, unknown>
  contract: string | null
  created_at: string
  updated_at: string
}
