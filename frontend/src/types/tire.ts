export type TireStatus = 'instalado' | 'almacen' | 'reparacion'
export type AxleSide = 'izquierdo' | 'derecho' | 'unico'
export type AxleDualPosition = 'unico' | 'interior' | 'exterior'
export type TireMovementType =
  | 'instalacion'
  | 'desinstalacion'
  | 'envio_reparacion'
  | 'envio_reencauche'
  | 'retorno_taller'

export interface Warehouse {
  id: string
  company_id: string
  name: string
  location: string | null
  created_at: string
  updated_at: string
}

export interface Tire {
  id: string
  company_id: string
  unique_code: string
  brand: string
  model: string
  current_thickness_mm: number
  status: TireStatus
  vehicle_id: string | null
  axle_number: number | null
  axle_side: AxleSide | null
  axle_dual_position: AxleDualPosition | null
  warehouse_id: string | null
  created_at: string
  updated_at: string
}

export interface TireMovement {
  id: string
  tire_id: string
  movement_type: TireMovementType
  vehicle_id: string | null
  axle_number: number | null
  axle_side: AxleSide | null
  axle_dual_position: AxleDualPosition | null
  warehouse_id: string | null
  provider_id: string | null
  km_at_movement: number | null
  thickness_mm: number | null
  notes: string | null
  recorded_by: string | null
  created_at: string
}

export interface TireDetail extends Tire {
  movements: TireMovement[]
  km_current_period: number | null
  km_lifetime_total: number
}

export interface TireSettings {
  id: string
  company_id: string
  disparity_threshold_mm: number
  created_at: string
  updated_at: string
}

export interface TirePerformanceRow {
  brand: string
  model: string
  end_reason: TireMovementType
  sample_count: number
  avg_km: number
}
