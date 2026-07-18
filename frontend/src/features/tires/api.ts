import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type {
  AxleDualPosition,
  AxleSide,
  Tire,
  TireDetail,
  TireMovement,
  TireMovementType,
  TirePerformanceRow,
  TireSettings,
  TireStatus,
  Warehouse,
} from '../../types/tire'

export interface TireListParams {
  page?: number
  page_size?: number
  status_filter?: TireStatus
  brand?: string
  model?: string
  search?: string
}

export interface TireCreatePayload {
  unique_code: string
  brand: string
  model: string
  current_thickness_mm: number
  warehouse_id?: string | null
}

export interface TireUpdatePayload {
  brand?: string
  model?: string
  current_thickness_mm?: number
}

export interface TireMovementPayload {
  tire_id: string
  movement_type: TireMovementType
  vehicle_id?: string | null
  axle_number?: number | null
  axle_side?: AxleSide | null
  axle_dual_position?: AxleDualPosition | null
  warehouse_id?: string | null
  provider_id?: string | null
  thickness_mm?: number | null
  notes?: string | null
}

export interface TireMovementBatchItemPayload {
  tire_id: string
  axle_number?: number | null
  axle_side?: AxleSide | null
  axle_dual_position?: AxleDualPosition | null
  thickness_mm?: number | null
}

export interface TireMovementBatchPayload {
  movement_type: TireMovementType
  items: TireMovementBatchItemPayload[]
  vehicle_id?: string | null
  warehouse_id?: string | null
  provider_id?: string | null
  notes?: string | null
}

export interface WarehousePayload {
  name: string
  location?: string | null
}

export async function listTires(params: TireListParams = {}): Promise<Page<Tire>> {
  const { data } = await api.get<Page<Tire>>('/tires', { params })
  return data
}

export async function getTire(id: string): Promise<TireDetail> {
  const { data } = await api.get<TireDetail>(`/tires/${id}`)
  return data
}

export async function createTire(payload: TireCreatePayload): Promise<Tire> {
  const { data } = await api.post<Tire>('/tires', payload)
  return data
}

export async function updateTire(id: string, payload: TireUpdatePayload): Promise<Tire> {
  const { data } = await api.patch<Tire>(`/tires/${id}`, payload)
  return data
}

export async function getTirePerformance(): Promise<TirePerformanceRow[]> {
  const { data } = await api.get<TirePerformanceRow[]>('/tires/analytics/performance')
  return data
}

export async function getVehicleTires(vehicleId: string): Promise<Tire[]> {
  const { data } = await api.get<Tire[]>(`/vehicles/${vehicleId}/tires`)
  return data
}

export async function createTireMovement(payload: TireMovementPayload): Promise<TireMovement> {
  const { data } = await api.post<TireMovement>('/tire-movements', payload)
  return data
}

export async function createTireMovementBatch(payload: TireMovementBatchPayload): Promise<TireMovement[]> {
  const { data } = await api.post<TireMovement[]>('/tire-movements/batch', payload)
  return data
}

export async function listTireMovements(params: { tire_id?: string; vehicle_id?: string }): Promise<TireMovement[]> {
  const { data } = await api.get<TireMovement[]>('/tire-movements', { params })
  return data
}

export async function listWarehouses(params: { page?: number; page_size?: number } = {}): Promise<Page<Warehouse>> {
  const { data } = await api.get<Page<Warehouse>>('/warehouses', { params })
  return data
}

export async function createWarehouse(payload: WarehousePayload): Promise<Warehouse> {
  const { data } = await api.post<Warehouse>('/warehouses', payload)
  return data
}

export async function updateWarehouse(id: string, payload: WarehousePayload): Promise<Warehouse> {
  const { data } = await api.patch<Warehouse>(`/warehouses/${id}`, payload)
  return data
}

export async function getTireSettings(): Promise<TireSettings> {
  const { data } = await api.get<TireSettings>('/tire-settings')
  return data
}

export async function updateTireSettings(disparityThresholdMm: number): Promise<TireSettings> {
  const { data } = await api.patch<TireSettings>('/tire-settings', {
    disparity_threshold_mm: disparityThresholdMm,
  })
  return data
}
