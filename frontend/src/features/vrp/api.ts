import { api } from '../../lib/axios'
import type { Vehicle } from '../../types/vehicle'
import type { VrpRun, VrpStop } from '../../types/vrp'

export interface VrpOptimizePayload {
  // Modo manual (7B): stops. Modo desde pedidos (9C): order_ids. Exactamente uno.
  stops?: VrpStop[]
  order_ids?: string[]
  cargo_type: string
  vehicle_ids?: string[]
  enforce_capacity?: boolean
}

export async function getAvailableVehicles(): Promise<Vehicle[]> {
  const { data } = await api.get<Vehicle[]>('/vrp/available-vehicles')
  return data
}

export async function optimizeVrp(payload: VrpOptimizePayload): Promise<VrpRun> {
  const { data } = await api.post<VrpRun>('/vrp/optimize', payload)
  return data
}

export async function getVrpRun(runId: string): Promise<VrpRun> {
  const { data } = await api.get<VrpRun>(`/vrp/runs/${runId}`)
  return data
}

export async function confirmVrpRun(runId: string): Promise<VrpRun> {
  const { data } = await api.post<VrpRun>(`/vrp/runs/${runId}/confirm`)
  return data
}

export async function discardVrpRun(runId: string): Promise<VrpRun> {
  const { data } = await api.post<VrpRun>(`/vrp/runs/${runId}/discard`)
  return data
}
