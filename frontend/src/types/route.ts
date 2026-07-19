export type RecalculationReason = 'desvio' | 'manual' | 'trafico'

export interface RouteRecalculation {
  id: string
  route_plan_id: string
  reason: RecalculationReason
  deviation_m: number | null
  trigger_lat: number | null
  trigger_lng: number | null
  new_distance_km: number
  new_duration_min: number
  new_route_data: number[][]
  created_at: string
}

export interface RoutePlan {
  id: string
  company_id: string
  trip_id: string
  origin_lat: number
  origin_lng: number
  destination_lat: number
  destination_lng: number
  // GeoJSON LineString coords: [[lng, lat], ...]
  geometry: number[][]
  waypoints: unknown[]
  calculated_distance_km: number
  calculated_duration_min: number
  engine_used: string
  created_at: string
  updated_at: string
}

export interface RoutePlanDetail extends RoutePlan {
  recalculations: RouteRecalculation[]
}

export interface RouteSettings {
  id: string
  company_id: string
  deviation_threshold_m: number
  recalc_cooldown_min: number
  created_at: string
  updated_at: string
}
