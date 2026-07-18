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
  created_at: string
  updated_at: string
}
