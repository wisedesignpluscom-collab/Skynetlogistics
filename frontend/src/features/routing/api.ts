import { api } from '../../lib/axios'
import type { RoutePlanDetail, RouteSettings } from '../../types/route'

export interface RouteComputePayload {
  origin_lat: number
  origin_lng: number
  destination_lat: number
  destination_lng: number
}

export async function getTripRoute(tripId: string): Promise<RoutePlanDetail | null> {
  try {
    const { data } = await api.get<RoutePlanDetail>(`/trips/${tripId}/route`)
    return data
  } catch (err: unknown) {
    // 404 = el viaje aún no tiene ruta planeada
    if (typeof err === 'object' && err !== null && 'response' in err) {
      const resp = (err as { response?: { status?: number } }).response
      if (resp?.status === 404) return null
    }
    throw err
  }
}

export async function computeTripRoute(tripId: string, payload: RouteComputePayload): Promise<RoutePlanDetail> {
  const { data } = await api.post<RoutePlanDetail>(`/trips/${tripId}/route`, payload)
  return data
}

export async function recalculateTripRoute(tripId: string): Promise<RoutePlanDetail> {
  const { data } = await api.post<RoutePlanDetail>(`/trips/${tripId}/route/recalculate`)
  return data
}

export async function getRouteSettings(): Promise<RouteSettings> {
  const { data } = await api.get<RouteSettings>('/route-settings')
  return data
}

export async function updateRouteSettings(payload: {
  deviation_threshold_m?: number
  recalc_cooldown_min?: number
}): Promise<RouteSettings> {
  const { data } = await api.patch<RouteSettings>('/route-settings', payload)
  return data
}
