import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type { Vehicle, VehicleStatus, VehicleType } from '../../types/vehicle'

export interface VehicleListParams {
  page?: number
  page_size?: number
  search?: string
  status_filter?: VehicleStatus
  type?: VehicleType
}

export interface VehiclePayload {
  plate: string
  brand: string
  model: string
  year: number
  vin?: string | null
  type: VehicleType
  assigned_driver_id?: string | null
  owner_id?: string | null
  color?: string | null
  engine_serial?: string | null
  has_odometer?: boolean
  odometer_digits?: number | null
  cargo_capacity_kg?: number | null
  cargo_capacity_m3?: number | null
  contract?: string | null
}

export interface VehicleUpdatePayload extends Partial<Omit<VehiclePayload, 'type'>> {
  status?: VehicleStatus
  current_odometer_km?: number
}

export async function listVehicles(params: VehicleListParams = {}): Promise<Page<Vehicle>> {
  const { data } = await api.get<Page<Vehicle>>('/vehicles', { params })
  return data
}

export async function getVehicle(id: string): Promise<Vehicle> {
  const { data } = await api.get<Vehicle>(`/vehicles/${id}`)
  return data
}

export async function createVehicle(payload: VehiclePayload): Promise<Vehicle> {
  const { data } = await api.post<Vehicle>('/vehicles', payload)
  return data
}

export async function updateVehicle(id: string, payload: VehicleUpdatePayload): Promise<Vehicle> {
  const { data } = await api.patch<Vehicle>(`/vehicles/${id}`, payload)
  return data
}

export async function deactivateVehicle(id: string): Promise<void> {
  await api.delete(`/vehicles/${id}`)
}
