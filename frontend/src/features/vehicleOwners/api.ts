import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type { VehicleOwner } from '../../types/vehicle_owner'

export interface VehicleOwnerListParams {
  page?: number
  page_size?: number
  search?: string
}

export interface VehicleOwnerPayload {
  name: string
  tax_id?: string | null
  contact_person?: string | null
  phone?: string | null
  email?: string | null
  notes?: string | null
}

export interface VehicleOwnerUpdatePayload extends Partial<VehicleOwnerPayload> {
  is_active?: boolean
}

export async function listVehicleOwners(params: VehicleOwnerListParams = {}): Promise<Page<VehicleOwner>> {
  const { data } = await api.get<Page<VehicleOwner>>('/vehicle-owners', { params })
  return data
}

export async function createVehicleOwner(payload: VehicleOwnerPayload): Promise<VehicleOwner> {
  const { data } = await api.post<VehicleOwner>('/vehicle-owners', payload)
  return data
}

export async function updateVehicleOwner(
  id: string,
  payload: VehicleOwnerUpdatePayload,
): Promise<VehicleOwner> {
  const { data } = await api.patch<VehicleOwner>(`/vehicle-owners/${id}`, payload)
  return data
}

export async function deactivateVehicleOwner(id: string): Promise<void> {
  await api.delete(`/vehicle-owners/${id}`)
}
