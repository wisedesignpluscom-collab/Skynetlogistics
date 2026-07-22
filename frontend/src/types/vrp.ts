export type VrpRunStatus = 'propuesto' | 'confirmado' | 'descartado'

export interface VrpStop {
  lat: number
  lng: number
  label: string
  order_id?: string | null
}

export interface VrpProposedVehicle {
  vehicle_id: string
  driver_id: string
  stops: VrpStop[]
  distance_km: number
  duration_min: number
  load_kg?: number | null
  load_m3?: number | null
  capacity_kg?: number | null
  capacity_m3?: number | null
}

export interface VrpRun {
  id: string
  company_id: string
  input_stops: VrpStop[]
  cargo_type: string
  vehicle_ids_considered: string[]
  proposed_assignment: VrpProposedVehicle[]
  status: VrpRunStatus
  result_trip_ids: string[]
  created_by: string
  created_at: string
}
